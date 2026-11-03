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
        from .workflow_requests import WorkflowRunQueue
        self.workflow_requests = WorkflowRunQueue(self.store)
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
        from .providers import (
            BoundProviderRouter,
            CatalogAdapterProvider,
            SemanticOperationProvider,
        )
        self.capabilities = CapabilityRegistry(self.store)
        catalog_provider = CatalogAdapterProvider(
            catalog=self.catalog,
            runner=self.runner,
            store=self.store,
            registry=self.capabilities,
            suppress_legacy_followup=self.automator.suppress_legacy_followup,
        )
        self.providers = BoundProviderRouter((
            catalog_provider,
            SemanticOperationProvider(catalog_provider, self.capabilities),
        ))

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

    def deliver_workflow_outbox_events(
        self, plan_id: str, consumer_id: str, publish, *, limit: int = 100,
    ):
        """At-least-once event delivery with post-publish durable acknowledgement."""
        from .outbox import WorkflowEventOutbox

        return WorkflowEventOutbox(self.store).deliver(
            plan_id, consumer_id, publish, limit=limit,
        )

    def workflow_event_inbox(self, plan_id: str, consumer_id: str, *, limit: int = 100):
        return self.store.list_unacknowledged_workflow_events(
            plan_id, consumer_id, limit=limit,
        )

    def acknowledge_workflow_event(self, plan_id: str, consumer_id: str, event_id: int):
        return self.store.acknowledge_workflow_events(plan_id, consumer_id, event_id)

    def workflow_events(self, plan_id: str, *, after_id: int = 0, limit: int = 100):
        return self.store.list_workflow_events(plan_id, after_id, limit)

    def configure_mission_cost_limit(self, mission_id: str, *, max_cost_microusd: int):
        return self.store.set_mission_cost_limit(
            mission_id, max_cost_microusd=max_cost_microusd,
        )

    def record_workflow_attempt_cost(
        self, attempt_id: str, *, cost_microusd: int, source: str,
    ):
        return self.store.record_workflow_attempt_cost(
            attempt_id, cost_microusd=cost_microusd, source=source,
        )

    def mission_cost_summary(self, mission_id: str):
        return self.store.get_mission_cost_summary(mission_id)

    def configure_mission_rate_limit(self, mission_id: str, *, min_spacing_s: float):
        return self.store.set_mission_rate_limit(
            mission_id, min_spacing_s=min_spacing_s,
        )

    def mission_rate_limit(self, mission_id: str):
        return self.store.get_mission_rate_limit(mission_id)

    def configure_mission_deadline(self, mission_id: str, *, deadline_at: float):
        return self.store.set_mission_deadline(mission_id, deadline_at=deadline_at)

    def mission_deadline(self, mission_id: str):
        """Read the authoritative persisted mission cutoff for every interface."""
        return self.store.get_mission_deadline(mission_id)

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

    def workflow_evidence(self, plan_id: str, *, limit: int = 100):
        """Return real, cross-checked workflow-to-tool evidence for reporting."""
        return self.store.get_workflow_evidence(plan_id, limit=limit)

    def workflow_resource_summary(self, plan_id: str):
        return self.store.get_workflow_resource_summary(plan_id)

    def workflow_audit_integrity(self, plan_id: str):
        return self.store.get_workflow_audit_integrity(plan_id)

    def workflow_audit_snapshot(self, plan_id: str):
        """Read-only lifecycle digest; external anchoring is operator-owned."""
        return self.store.get_workflow_audit_snapshot(plan_id)

    def verify_workflow_audit_snapshot(self, plan_id: str, expected_digest: str):
        """Compare current lifecycle state against an externally retained digest."""
        return self.store.verify_workflow_audit_snapshot(plan_id, expected_digest)

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
        """Stop future task claims and close queued (not running) run intents."""
        cancelled = self.store.request_workflow_cancellation(plan_id)
        self.workflow_requests.cancel_queued(plan_id)
        return cancelled

    def save_workflow_plan(self, plan_id: str, plan):
        """Validate and persist a versioned mission DAG."""
        return self.store.save_workflow_plan(plan_id, plan)

    def workflow_plan_details(self, plan_id: str):
        """Return the same persisted plan/task snapshot to CLI and API."""
        plan = self.store.get_workflow_plan(plan_id)
        if plan is None:
            raise ValueError(f"unknown workflow plan: {plan_id}")
        return {
            "plan": plan["plan"],
            "tasks": self.store.list_workflow_tasks(plan_id),
        }

    def enqueue_workflow_run(self, plan_id: str, *, max_tasks: int = 100,
                             max_attempts: int = 2, max_concurrency: int = 4):
        """Persist an execution request before acknowledging any client."""
        return self.workflow_requests.enqueue(plan_id, limits={
            "max_tasks": max_tasks, "max_attempts": max_attempts,
            "max_concurrency": max_concurrency,
        })

    def workflow_run_queue_summary(self):
        """Shared read-only queue diagnostics for API, CLI and headless."""
        return self.workflow_requests.summary()

    def workflow_run_request(self, request_id: str):
        return self.workflow_requests.get(request_id)

    def cancel_workflow_run_request(self, request_id: str):
        """Request cancellation through the existing durable plan stop barrier.

        A running external effect is not asserted to have stopped. Unknown
        requests never cancel an unrelated plan.
        """
        row = self.workflow_run_request(request_id)
        if row is None:
            raise ValueError("unknown workflow run request")
        cancelled = self.cancel_workflow_plan(row["plan_id"])
        return {
            "run_request_id": request_id,
            "plan_id": row["plan_id"],
            "cancellation_requested": True,
            "tasks_cancelled": cancelled,
            "external_effects_stopped": False,
            "request": self.workflow_run_request(request_id),
        }

    def workflow_run_snapshot(self, request_id: str):
        """Reconnect-safe persisted run and task progress, without lease secrets.

        The request and task views are individually persisted snapshots, not
        a claim that external effects completed or that a worker is alive.
        """
        row = self.workflow_run_request(request_id)
        if row is None:
            return None
        return {
            "schema_version": "whaxon.workflow-run-snapshot.v1",
            "request": row,
            "progress": self.workflow_progress(row["plan_id"]),
            "worker_liveness_verified": False,
            "automatic_uncertain_replay": False,
        }

    async def drain_workflow_run_requests(self, *, max_runs: int = 20,
                                          initialized: bool = False,
                                          stop_event=None) -> int:
        """Claim persistent V2 run requests; never replay uncertain executions.

        A CLI, headless daemon or web service can call this after restart.
        The scheduler continues to own task leases, policy and evidence.
        """
        import asyncio
        import uuid

        if type(max_runs) is not int or not 1 <= max_runs <= 100:
            raise ValueError("max_runs must be between 1 and 100")
        if stop_event is not None and not callable(getattr(stop_event, "is_set", None)):
            raise TypeError("stop_event must expose is_set()")
        if not initialized:
            await self.initialize(drain=False)
        # Reconcile the full bounded backlog before claiming fresh work.
        # Each pass holds a short transaction (at most 128 lost leases).
        # A single pass would leave older lost leases indefinitely if the
        # service exits after draining all newly queued work.
        while self.workflow_requests.reconcile_stale():
            if stop_event is not None and stop_event.is_set():
                return 0
        owner = "workflow-run-worker-" + uuid.uuid4().hex
        processed = 0
        for _ in range(max_runs):
            # Stop admits no additional request after a graceful shutdown
            # signal, even inside a multi-request batch. An already claimed
            # external effect is allowed to finish or become uncertain.
            if stop_event is not None and stop_event.is_set():
                break
            request = self.workflow_requests.claim(owner)
            if request is None:
                break
            token = request["lease_token"]
            request_id = request["id"]
            async def heartbeat(active_id=request_id, active_token=token):
                while True:
                    await asyncio.sleep(5)
                    if not self.workflow_requests.heartbeat(active_id, active_token):
                        return

            pulse = asyncio.create_task(heartbeat())
            status = "uncertain"
            error = ""
            try:
                result = await self.run_workflow_plan(
                    request["plan_id"], worker_id=owner, **request["limits"],
                )
                status = "completed" if result["complete"] else "incomplete"
            except Exception as exc:
                # Dispatch may have produced an external effect before failure.
                # Never automatically retry this request.
                error = f"worker error after claim: {type(exc).__name__}"
            finally:
                pulse.cancel()
                try:
                    await pulse
                except asyncio.CancelledError:
                    pass
                self.workflow_requests.finish(
                    request_id, token, status=status, error=error,
                )
            processed += 1
        return processed

    async def serve_workflow_run_requests(
        self, stop_event, *, poll_interval_s: float = 1.0,
        max_runs_per_batch: int = 20,
    ) -> int:
        """Continuously service durable V2 intents until graceful stop.

        stop_event is a threading.Event, so foreground services can handle
        SIGTERM/SIGINT without assuming they own the asyncio event loop.
        A stop signal prevents new claims within the current batch, without
        falsely claiming that an in-flight external operation stopped.
        """
        import asyncio
        import math

        if isinstance(poll_interval_s, bool) or not isinstance(
            poll_interval_s, (int, float)
        ) or not math.isfinite(poll_interval_s) or not 0.05 <= poll_interval_s <= 3600:
            raise ValueError("poll interval must be finite and in [0.05, 3600]")
        if type(max_runs_per_batch) is not int or not 1 <= max_runs_per_batch <= 100:
            raise ValueError("max_runs_per_batch must be in range 1..100")
        if not callable(getattr(stop_event, "is_set", None)):
            raise TypeError("stop_event must expose is_set()")
        await self.initialize(drain=False)
        total = 0
        while not stop_event.is_set():
            total += await self.drain_workflow_run_requests(
                max_runs=max_runs_per_batch, initialized=True,
                stop_event=stop_event,
            )
            # Poll deadlines use a monotonic clock: repeated fractional
            # subtraction can drift under scheduler pauses and postpone new
            # durable requests. A stop signal remains responsive.
            deadline = asyncio.get_running_loop().time() + float(poll_interval_s)
            while not stop_event.is_set():
                remaining = deadline - asyncio.get_running_loop().time()
                if remaining <= 0:
                    break
                await asyncio.sleep(min(remaining, 0.25))
        return total

    def propose_workflow_followups(self, source_plan_id: str, *, max_tasks: int = 16):
        """Compile reviewable follow-ups from sealed, persisted evidence."""
        from .followups import EvidenceFollowupPlanner

        return EvidenceFollowupPlanner(
            store=self.store, providers=self.providers, scope=self.scope,
        ).propose(source_plan_id, max_tasks=max_tasks)

    def capability_portfolio_audit(self):
        """Expose catalog/adapter gaps without registering execution routes."""
        return self.providers.portfolio_audit()

    def capability_inventory(self):
        """Return truthful live provider readiness without changing manifests."""
        return self.providers.inventory()

    def authorize_workflow_task(self, task) -> bool:
        """Fail-closed default policy for scoped, read-only catalog scans."""
        from .capabilities import CapabilityUnavailable

        try:
            from .capabilities import CapabilityRequirements
            from .providers import _target_type

            bound = getattr(self, "providers", None)
            if bound is not None:
                # The production policy and execution must bind the same
                # in-process adapter manifest, not a persisted-only claim.
                manifest = bound.resolve_task(
                    task, require_installed=True,
                ).manifest
            else:
                # Small policy-only tests instantiate Core without providers.
                candidates = self.capabilities.list(task.capability_id)
                target_type = _target_type(task.target) if any(
                    item.target_types for item in candidates
                ) else ""
                manifest = self.capabilities.resolve(
                    task.capability_id,
                    CapabilityRequirements(
                        target_type=target_type,
                        required_permissions=tuple(task.permissions),
                        transport="local_process",
                        allowed_versions=("catalog-v1",) if task.capability_id.startswith("tool.") else (),
                    ),
                ).manifest
        except (CapabilityUnavailable, ValueError, TypeError, RuntimeError):
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
        # The network-execution gate is stricter than a UI scope preview:
        # DNS-rebinding-prone hostnames must not be authorized under CIDR scope.
        try:
            # Scope may be revoked by another CLI/server process. Refresh the
            # persisted policy at each decision; malformed updates fail closed.
            reload_scope = getattr(self.scope, "load", None)
            if callable(reload_scope):
                reload_scope()
            execution_check = getattr(self.scope, "check_for_execution", None)
            if not callable(execution_check):
                execution_check = self.scope.check
            return execution_check(task.target).allowed is True
        except Exception:
            return False

    def authorize_workflow_task_for_plan(self, plan_id: str, task) -> bool:
        """Enforce exact consent for moderate-impact tasks in persisted plans.

        An approval is never a substitute for scope/provider policy. Revocation,
        expiry, changed task bindings and missing approval all fail closed.
        """
        from .workflow import WorkflowPlan, WorkflowTask

        # Never authorize an unpersisted or modified task using approval/scope
        # from a different plan. This applies to low-impact nodes too.
        if not isinstance(task, WorkflowTask):
            return False
        try:
            row = self.store.get_workflow_plan(plan_id)
            if row is None or row["status"] == "cancel_requested":
                return False
            plan = WorkflowPlan.from_dict(row["plan"])
            if plan.digest != row["digest"] or plan.mission_id != row["mission_id"]:
                return False
            if not any(candidate == task for candidate in plan.tasks):
                return False
            self.store.verify_workflow_plan_integrity(plan_id)
            provider = getattr(self, "providers", None)
            check_binding = getattr(provider, "plan_binding_valid", None)
            if callable(check_binding) and check_binding(task, plan.metadata) is not True:
                return False
            if not self.authorize_workflow_task(task):
                return False
            if task.impact in ("moderate", "high", "critical"):
                return self.store.has_valid_workflow_approval(plan_id, task.id) is True
            return True
        except (ValueError, TypeError, RuntimeError, KeyError):
            return False

    def workflow_scheduler(
        self, *, plan_id: str | None = None, authorize=None, dispatch=None,
        worker_id: str = "workflow-worker",
    ):
        """Default to plan-bound authorization, never unbound scope approval.

        Custom callbacks are explicit injection hooks for controlled callers;
        production callers should use run_workflow_plan instead.
        """
        from .scheduler import WorkflowScheduler

        if authorize is None:
            if not plan_id:
                raise ValueError("plan_id required for default workflow authorization")

            def authorize(task):
                return self.authorize_workflow_task_for_plan(plan_id, task)

        return WorkflowScheduler(
            self.store, authorize=authorize,
            dispatch=dispatch if dispatch is not None else self.providers.dispatch,
            worker_id=worker_id,
        )

    async def run_workflow_plan(
        self, plan_id: str, *, authorize=None, dispatch=None,
        worker_id: str = "workflow-worker", max_tasks: int = 100, max_attempts: int = 2,
        max_concurrency: int = 4,
    ):
        """Run a persisted plan; all authorization and dispatch stay injected."""
        discover_followups = authorize is None and dispatch is None
        if authorize is None:
            def authorize(task):
                return self.authorize_workflow_task_for_plan(plan_id, task)
        scheduler = self.workflow_scheduler(
            plan_id=plan_id, authorize=authorize, dispatch=dispatch, worker_id=worker_id,
        )
        result = await scheduler.run(
            plan_id, max_tasks=max_tasks, max_attempts=max_attempts,
            max_concurrency=max_concurrency,
        )
        # E4 only proposes and persists a NEW plan from sealed evidence. It
        # cannot approve or execute it. Existing E3 scheduling stays unchanged.
        if (
            discover_followups
            and result.get("complete")
            and any(item["status"] == "succeeded" for item in result["tasks"])
        ):
            try:
                proposal = self.propose_workflow_followups(plan_id)
                if proposal.plan is not None:
                    self.save_workflow_plan(proposal.plan_id, proposal.plan)
                result["followup"] = proposal.to_dict()
            except Exception as exc:
                # Follow-up discovery is a secondary, review-only activity.
                # A planner failure cannot reclassify a completed source
                # workflow as an uncertain external execution.
                result["followup_error"] = type(exc).__name__
        return result

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
