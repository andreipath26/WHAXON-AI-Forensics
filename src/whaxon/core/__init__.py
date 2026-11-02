"""WHAXON core — headless, UI-agnostic."""
from __future__ import annotations

import asyncio
from pathlib import Path

from .catalog import ToolCatalog
from .events import (
    CoverageSkipped,
    EventBus,
    JobFailed,
    JobFindings,
    JobFinished,
    JobOutput,
    JobStarted,
)
from .msf import MSFClient
from .msf_tracker import MSFTracker
from .runner import ToolRunner
from .scope import ScopeManager
from .store import JobStore


class Core:
    """Single entry point for every interface. Holds no UI state."""

    def __init__(self, data_dir: Path) -> None:
        self.data_dir = Path(data_dir)
        self.bus = EventBus()
        self.catalog = ToolCatalog(self.bus, self.data_dir / "tools.json")
        self.scope = ScopeManager(self.data_dir / "scope.json")
        from .settings import Settings
        self.settings = Settings(self.data_dir / "settings.json")
        # Phase E.2: a resolver that queries live portfwd state on demand.
        # Returns None on any MSF failure, so the runner behaves normally
        # when Metasploit is not running.
        from .routes import live_resolver
        _route_resolver = live_resolver()
        # Local vulnerability database (CVSS / EPSS / CISA KEV). Used by the
        # severity resolver to set finding severity from CVSS when a CVE is
        # present. See docs/report-redesign.md section 1e.
        from .vulndb import VulnDB
        self.vulndb = VulnDB(self.data_dir / "vulndb.db")
        self.runner = ToolRunner(self.bus, self.catalog, self.scope,
                                 route_resolver=_route_resolver,
                                 vulndb=self.vulndb)
        # SQLite-backed persistence for all UIs
        state_path = self.data_dir / "whaxon.db"
        self.store = JobStore(state_path)
        self.runner.bind_session_lookup(self.store.get_session)
        # Subscribe the persister FIRST so every other JobFindings consumer
        # (correlator, suggester, automator) sees findings already in the store.
        self._wire_store()
        # Cross-finding correlation (deterministic, no AI).
        from .correlator import Correlator
        self.correlator = Correlator(self.bus, self.store)
        self.correlator.attach()

        # Attach next-step suggestions from adapters to findings.
        from .suggester import Suggester
        def _adapter_lookup(tool_id):
            try:
                from ..adapters import get_adapter
                return get_adapter(tool_id)
            except Exception:
                return None
        self.suggester = Suggester(self.bus, self.store, _adapter_lookup)
        self.suggester.attach()

        # Deterministic auto-chain rules (nmap -> nikto per web port).
        from .automation import Automator
        self.automator = Automator(self.bus, self.store, self.runner)
        self.automator.attach()
        # Recon: passive checks that flow through the same event pipeline.
        from . import recon_checks as _rc
        from .recon import ReconRunner
        self.recon = ReconRunner(
            scope=self.scope,
            bus=self.bus,
            resolver=self.runner._resolve_findings,
        )
        self.recon.register("dns", _rc.check_dns)
        self.recon.register("ssl", _rc.check_ssl)
        self.recon.register("headers", _rc.check_headers)
        self.recon.register("tech", _rc.check_tech)
        self.recon.register("robots", _rc.check_robots)
        self.recon.register("security_txt", _rc.check_security_txt)
        self.recon.register("cookies", _rc.check_cookies)
        self.recon.register("redirects", _rc.check_redirects)
        self.recon.register("waf", _rc.check_waf)
        self.recon.register("dns_full", _rc.check_dns_full)
        # Metasploit RPC + session tracker
        self.msf = MSFClient()
        self.msf_tracker = MSFTracker(self.bus, self.store, self.msf)
        # A PyPI installation must work from an arbitrary working directory.
        # Seed the user data directory from the packaged catalog on first run;
        # never overwrite an operator's existing tools.json.
        if not self.catalog.path.exists():
            packaged_catalog = Path(__file__).parent.parent / "data" / "tools.json"
            if packaged_catalog.is_file():
                self.data_dir.mkdir(parents=True, exist_ok=True)
                try:
                    self.catalog.path.write_text(
                        packaged_catalog.read_text(encoding="utf-8"),
                        encoding="utf-8",
                    )
                except OSError as exc:
                    raise RuntimeError(
                        f"cannot initialize tool catalog at {self.catalog.path}: {exc}"
                    ) from exc

        # Scope enforcement
        if self.catalog.path.exists():
            self.catalog.load()

        # Engine v2 uses the same catalog, runner, adapter parser and event store
        # as the existing interfaces. The provider bridge is intentionally
        # limited to read-only scanners until dedicated approval models exist.
        from .capabilities import CapabilityRegistry
        from .providers import CatalogAdapterProvider
        self.capabilities = CapabilityRegistry(self.store)
        self.providers = CatalogAdapterProvider(
            catalog=self.catalog,
            runner=self.runner,
            store=self.store,
            registry=self.capabilities,
        )

    def _wire_store(self) -> None:
        """Subscribe the store to every job event so history persists."""
        def _on_started(e):
            self.store.create(e.job_id)
            self.store.set_started(e.job_id, e.tool_id, e.target, lease_token=e.lease_token)
        def _on_output(e):
            if self.store.owns_lease(e.job_id, e.lease_token):
                self.store.append_line(e.job_id, e.stream, e.line)
        def _on_finished(e):
            self.store.set_finished(e.job_id, e.exit_code, e.duration_s, lease_token=e.lease_token)
        def _on_failed(e):
            self.store.set_failed(e.job_id, e.error, lease_token=e.lease_token)
        def _on_findings(e):
            if not self.store.owns_lease(e.job_id, e.lease_token):
                return
            for i, f in enumerate(e.findings):
                self.store.append_finding(e.job_id, f, i)
        self.bus.subscribe(JobStarted, _on_started)
        self.bus.subscribe(JobOutput, _on_output)
        self.bus.subscribe(JobFinished, _on_finished)
        self.bus.subscribe(JobFailed, _on_failed)
        self.bus.subscribe(JobFindings, _on_findings)
        def _on_coverage(e):
            self.store.record_coverage(e.job_id, e.tool_id, e.target, e.kind, e.detail, getattr(e, "phase", ""))
        self.bus.subscribe(CoverageSkipped, _on_coverage)

    def create_mission(self, mission_id: str, objective: str, metadata=None):
        """Create a durable Engine v2 mission through the shared Core service."""
        return self.store.create_mission(mission_id, objective, metadata)

    def grant_workflow_approval(
        self, plan_id: str, task_key: str, approval_id: str, actor: str,
        *, expires_at: float, policy_version: str = "policy.v1",
    ):
        return self.store.grant_workflow_approval(
            plan_id, task_key, approval_id, actor,
            expires_at=expires_at, policy_version=policy_version,
        )

    def revoke_workflow_approval(self, plan_id: str, approval_id: str, *, actor: str):
        return self.store.revoke_workflow_approval(plan_id, approval_id, actor=actor)

    def workflow_approvals(self, plan_id: str):
        return self.store.list_workflow_approvals(plan_id)

    def configure_workflow_rate_limit(self, plan_id: str, *, min_spacing_s: float):
        return self.store.set_workflow_rate_limit(plan_id, min_spacing_s=min_spacing_s)

    def configure_workflow_deadline(self, plan_id: str, *, deadline_at: float):
        return self.store.set_workflow_deadline(plan_id, deadline_at=deadline_at)

    def configure_workflow_limits(
        self, plan_id: str, *, max_total_attempts: int, max_concurrency: int,
    ):
        return self.store.set_workflow_limits(
            plan_id, max_total_attempts=max_total_attempts,
            max_concurrency=max_concurrency,
        )

    def reconcile_workflow_plan(self, plan_id: str, *, stale_after_s: float = 60.0):
        """Reconcile expired worker leases without repeating external effects."""
        return self.store.reconcile_workflow_plan(plan_id, stale_after_s=stale_after_s)

    def workflow_event_cursor(self, plan_id: str, consumer_id: str):
        return self.store.get_workflow_event_cursor(plan_id, consumer_id)

    def workflow_event_inbox(self, plan_id: str, consumer_id: str, *, limit: int = 100):
        return self.store.list_unacknowledged_workflow_events(
            plan_id, consumer_id, limit=limit,
        )

    def acknowledge_workflow_event(self, plan_id: str, consumer_id: str, event_id: int):
        return self.store.acknowledge_workflow_events(plan_id, consumer_id, event_id)

    def workflow_events(self, plan_id: str, *, after_id: int = 0, limit: int = 100):
        return self.store.list_workflow_events(plan_id, after_id, limit)

    def configure_mission_deadline(self, mission_id: str, *, deadline_at: float):
        return self.store.set_mission_deadline(mission_id, deadline_at=deadline_at)

    def mission_execution_limits(self, mission_id: str):
        return self.store.get_mission_execution_limits(mission_id)

    def configure_mission_execution_limits(
        self, mission_id: str, *, max_total_attempts: int, max_concurrency: int,
    ):
        return self.store.set_mission_execution_limits(
            mission_id, max_total_attempts=max_total_attempts,
            max_concurrency=max_concurrency,
        )

    def missions(self, *, limit: int = 100, after_created: float = 0.0):
        return self.store.list_missions(limit=limit, after_created=after_created)

    def mission_workflow_plans(self, mission_id: str):
        return self.store.list_workflow_mission_plans(mission_id)

    def workflow_dispatch_reconciliation(self, plan_id: str):
        return self.store.get_workflow_dispatch_reconciliation(plan_id)

    def workflow_readiness(self, plan_id: str):
        return self.store.get_workflow_readiness(plan_id)

    def workflow_resource_summary(self, plan_id: str):
        return self.store.get_workflow_resource_summary(plan_id)

    def workflow_audit_integrity(self, plan_id: str):
        return self.store.get_workflow_audit_integrity(plan_id)

    def workflow_attempts(
        self, plan_id: str, *, after_started: float = 0.0, limit: int = 100,
    ):
        """Expose read-only attempt diagnostics through the shared Core service."""
        return self.store.list_workflow_attempts(
            plan_id, after_started=after_started, limit=limit,
        )

    def workflow_progress(self, plan_id: str):
        """Expose durable task/attempt progress to CLI, API and headless clients."""
        return self.store.get_workflow_progress(plan_id)

    def cancel_workflow_plan(self, plan_id: str) -> int:
        """Durably halt future claims; in-flight provider effects remain uncertain."""
        return self.store.request_workflow_cancellation(plan_id)

    def save_workflow_plan(self, plan_id: str, plan):
        """Validate and persist a versioned mission DAG."""
        return self.store.save_workflow_plan(plan_id, plan)

    def authorize_workflow_task(self, task) -> bool:
        """Fail-closed default policy for scoped, read-only catalog scans."""
        from .capabilities import CapabilityUnavailable

        try:
            manifest = self.capabilities.resolve(task.capability_id).manifest
        except (CapabilityUnavailable, ValueError):
            return False
        impact_rank = {
            "read_only": 0, "low": 1, "moderate": 2, "high": 3, "critical": 4,
        }
        if task.impact not in impact_rank or manifest.impact not in impact_rank:
            return False
        if task.impact != manifest.impact or set(task.permissions) != set(manifest.permissions):
            return False
        if impact_rank[task.impact] > impact_rank["moderate"]:
            return False
        try:
            return bool(self.scope.check(task.target).allowed)
        except Exception:
            return False

    def authorize_workflow_task_for_plan(self, plan_id: str, task) -> bool:
        """Enforce exact consent for moderate-impact tasks in persisted plans.

        An approval is never a substitute for scope/provider policy. Revocation,
        expiry, changed task bindings and missing approval all fail closed.
        """
        if not self.authorize_workflow_task(task):
            return False
        if task.impact in ("moderate", "high", "critical"):
            try:
                return bool(self.store.has_valid_workflow_approval(plan_id, task.id))
            except (ValueError, TypeError, RuntimeError):
                return False
        return True

    def workflow_scheduler(
        self, *, authorize=None, dispatch=None, worker_id: str = "workflow-worker",
    ):
        """Build a scheduler with fail-closed scope policy and real catalog providers."""
        from .scheduler import WorkflowScheduler
        return WorkflowScheduler(
            self.store, authorize=authorize or self.authorize_workflow_task,
            dispatch=dispatch or self.providers.dispatch, worker_id=worker_id,
        )

    async def run_workflow_plan(
        self, plan_id: str, *, authorize=None, dispatch=None,
        worker_id: str = "workflow-worker", max_tasks: int = 100, max_attempts: int = 2,
        max_concurrency: int = 4,
    ):
        """Run a persisted plan; all authorization and dispatch stay injected."""
        if authorize is None:
            def authorize(task):
                return self.authorize_workflow_task_for_plan(plan_id, task)
        scheduler = self.workflow_scheduler(
            authorize=authorize, dispatch=dispatch, worker_id=worker_id,
        )
        return await scheduler.run(
            plan_id, max_tasks=max_tasks, max_attempts=max_attempts,
            max_concurrency=max_concurrency,
        )

    async def initialize(self, drain: bool = True) -> None:
        """Called once by any interface. Awaitable inside a splash screen.

        drain=True (default): long-lived hosts. Drains queued jobs after
        reconciling stale rows. drain=False: one-shot CLI commands, which
        must not silently execute jobs a previous process queued.
        """
        self.bus.bind_loop(asyncio.get_running_loop())
        if self.catalog.path.exists():
            self.catalog.load()
        # Recover from a prior process that died mid-job, then run any
        # jobs a previous process queued (the durable auto-chain).
        try:
            self.store.reconcile_stale()
        except Exception:
            pass
        try:
            # Do not steal a live worker's attempt when another CLI/daemon
            # process starts. Workflow workers renew this lease while executing.
            self.store.reconcile_workflow_attempts(stale_after_s=60.0)
        except Exception:
            # Startup remains available, but an unreconciled workflow task
            # cannot be reclaimed by the scheduler; operators can inspect it.
            pass
        if drain:
            try:
                from .worker import drain_async
                await drain_async(self.store, self.runner)
            except Exception:
                pass
