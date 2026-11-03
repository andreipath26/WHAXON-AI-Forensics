from types import SimpleNamespace

import pytest

from whaxon.core.capabilities import CapabilityRegistry
from whaxon.core.providers import CatalogAdapterProvider
from whaxon.core.workflow import WorkflowTask


class _Catalog:
    def __init__(self, tools):
        self.tools = {tool.id: tool for tool in tools}

    def list(self):
        return list(self.tools.values())

    def get(self, tool_id):
        return self.tools.get(tool_id)


class _Runner:
    def __init__(self):
        self.calls = []

    async def run_tool(self, **kwargs):
        self.calls.append(kwargs)
        return kwargs["job_id"]


class _Store:
    def get(self, job_id):
        return {
            "id": job_id, "status": "finished", "exit_code": 0,
            "duration_s": 0.25, "error": None,
        }

    def get_findings(self, job_id):
        return [{"kind": "open_port", "data": {"port": 443}}]


def _tool(tool_id="nmap", *, available=True, category="recon"):
    return SimpleNamespace(id=tool_id, available=available, category=category)


def test_catalog_adapter_provider_executes_through_core_runner(monkeypatch):
    import whaxon.adapters

    monkeypatch.setattr(whaxon.adapters, "get_adapter", lambda tool_id: object())
    catalog = _Catalog([_tool()])
    runner = _Runner()
    provider = CatalogAdapterProvider(
        catalog=catalog, runner=runner, store=_Store(),
        registry=CapabilityRegistry(),
    )

    import asyncio
    result = asyncio.run(provider.dispatch(
        WorkflowTask("scan", "tool.nmap", "192.0.2.10"),
    ))

    assert result["tool_id"] == "nmap"
    assert result["findings"][0]["data"]["port"] == 443
    assert runner.calls[0]["tool_id"] == "nmap"
    assert runner.calls[0]["target"] == "192.0.2.10"
    assert runner.calls[0]["phase"] == "workflow"


def test_catalog_adapter_provider_rejects_dynamic_cli_arguments(monkeypatch):
    import whaxon.adapters

    monkeypatch.setattr(whaxon.adapters, "get_adapter", lambda tool_id: object())
    provider = CatalogAdapterProvider(
        catalog=_Catalog([_tool()]), runner=_Runner(), store=_Store(),
        registry=CapabilityRegistry(),
    )
    with pytest.raises(ValueError, match="no dynamic inputs"):
        import asyncio
        asyncio.run(provider.dispatch(
            WorkflowTask("scan", "tool.nmap", "192.0.2.10", inputs={"extra_args": "-p-"}),
        ))


def test_catalog_adapter_provider_refuses_missing_binary(monkeypatch):
    import whaxon.adapters

    monkeypatch.setattr(whaxon.adapters, "get_adapter", lambda tool_id: object())
    provider = CatalogAdapterProvider(
        catalog=_Catalog([_tool(available=False)]), runner=_Runner(), store=_Store(),
        registry=CapabilityRegistry(),
    )
    with pytest.raises(RuntimeError, match="not installed"):
        import asyncio
        asyncio.run(provider.dispatch(
            WorkflowTask("scan", "tool.nmap", "192.0.2.10"),
        ))


def test_provider_does_not_register_exploit_or_credential_tools(monkeypatch):
    import whaxon.adapters

    monkeypatch.setattr(whaxon.adapters, "get_adapter", lambda tool_id: object())
    registry = CapabilityRegistry()
    CatalogAdapterProvider(
        catalog=_Catalog([_tool("hydra"), _tool("commix"), _tool("nmap")]),
        runner=_Runner(), store=_Store(), registry=registry,
    )
    assert [item.capability_id for item in registry.list()] == ["tool.nmap"]


def test_core_default_workflow_policy_requires_scope_permission_and_matching_impact():
    from types import SimpleNamespace

    from whaxon.core import Core
    from whaxon.core.capabilities import CapabilityManifest, CapabilityRegistry

    core = Core.__new__(Core)
    core.capabilities = CapabilityRegistry()
    core.capabilities.register(CapabilityManifest(
        capability_id="tool.nmap",
        provider_id="whaxon.adapter.nmap",
        provider_version="catalog-v1",
        transports=("local_process",),
        permissions=("network.scan",),
        impact="moderate",
    ))
    core.scope = SimpleNamespace(
        check=lambda target: SimpleNamespace(allowed=target == "192.0.2.10"),
    )
    allowed = WorkflowTask(
        "scan", "tool.nmap", "192.0.2.10",
        permissions=("network.scan",), impact="moderate",
    )
    assert core.authorize_workflow_task(allowed) is True
    assert core.authorize_workflow_task(WorkflowTask(
        "scan", "tool.nmap", "192.0.2.10", impact="moderate",
    )) is False
    assert core.authorize_workflow_task(WorkflowTask(
        "scan", "tool.nmap", "192.0.2.10",
        permissions=("network.scan",), impact="low",
    )) is False
    assert core.authorize_workflow_task(WorkflowTask(
        "scan", "tool.nmap", "198.51.100.20",
        permissions=("network.scan",), impact="moderate",
    )) is False


def test_core_plan_bound_policy_requires_exact_unrevoked_approval(tmp_path):
    import time
    from types import SimpleNamespace

    from whaxon.core import Core
    from whaxon.core.capabilities import CapabilityManifest, CapabilityRegistry
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    core = Core.__new__(Core)
    core.store = JobStore(tmp_path / "policy-approval.db")
    core.capabilities = CapabilityRegistry()
    core.capabilities.register(CapabilityManifest(
        capability_id="tool.nmap",
        provider_id="whaxon.adapter.nmap",
        provider_version="catalog-v1",
        transports=("local_process",),
        permissions=("network.scan",),
        impact="moderate",
    ))
    core.scope = SimpleNamespace(
        check=lambda target: SimpleNamespace(allowed=target == "192.0.2.10"),
    )
    task = WorkflowTask(
        "scan", "tool.nmap", "192.0.2.10",
        permissions=("network.scan",), impact="moderate",
    )
    plan = WorkflowPlan("mission", (task,))
    core.store.create_mission("mission", "controlled lab")
    core.store.save_workflow_plan("p", plan)
    assert core.authorize_workflow_task_for_plan("p", task) is False
    core.store.grant_workflow_approval(
        "p", "scan", "approval", "operator", expires_at=time.time() + 300,
    )
    assert core.authorize_workflow_task_for_plan("p", task) is True
    assert core.authorize_workflow_task_for_plan("p", WorkflowTask(
        "scan", "tool.nmap", "198.51.100.20",
        permissions=("network.scan",), impact="moderate",
    )) is False
    core.store.revoke_workflow_approval("p", "approval", actor="operator")
    assert core.authorize_workflow_task_for_plan("p", task) is False


def test_engine_v2_scope_execution_gate_rejects_dns_rebinding_preview():
    from types import SimpleNamespace

    from whaxon.core import Core
    from whaxon.core.capabilities import CapabilityManifest, CapabilityRegistry

    core = Core.__new__(Core)
    core.capabilities = CapabilityRegistry()
    core.capabilities.register(CapabilityManifest(
        capability_id="tool.nmap", provider_id="whaxon.adapter.nmap",
        provider_version="catalog-v1", transports=("local_process",),
        permissions=("network.scan",), impact="moderate",
    ))
    core.scope = SimpleNamespace(
        check=lambda target: SimpleNamespace(allowed=True),
        check_for_execution=lambda target: SimpleNamespace(allowed=False),
    )
    task = WorkflowTask(
        "scan", "tool.nmap", "lab.example",
        permissions=("network.scan",), impact="moderate",
    )
    assert core.authorize_workflow_task(task) is False


def test_engine_v2_scope_requires_literal_true_not_truthy_authorization():
    from types import SimpleNamespace

    from whaxon.core import Core
    from whaxon.core.capabilities import CapabilityManifest, CapabilityRegistry

    core = Core.__new__(Core)
    core.capabilities = CapabilityRegistry()
    core.capabilities.register(CapabilityManifest(
        capability_id="tool.nmap", provider_id="whaxon.adapter.nmap",
        provider_version="catalog-v1", transports=("local_process",),
        permissions=("network.scan",), impact="moderate",
    ))
    core.scope = SimpleNamespace(check=lambda target: SimpleNamespace(allowed="yes"))
    task = WorkflowTask(
        "scan", "tool.nmap", "192.0.2.10",
        permissions=("network.scan",), impact="moderate",
    )
    assert core.authorize_workflow_task(task) is False


def test_engine_v2_plan_authorization_rejects_modified_low_impact_nodes(tmp_path):
    from types import SimpleNamespace

    from whaxon.core import Core
    from whaxon.core.capabilities import CapabilityManifest, CapabilityRegistry
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    core = Core.__new__(Core)
    core.store = JobStore(tmp_path / "plan-auth-identity.db")
    core.capabilities = CapabilityRegistry()
    core.capabilities.register(CapabilityManifest(
        capability_id="tool.fixture", provider_id="whaxon.adapter.fixture",
        provider_version="catalog-v1", transports=("local_process",),
        permissions=(), impact="low",
    ))
    core.scope = SimpleNamespace(check=lambda target: SimpleNamespace(allowed=True))
    original = WorkflowTask("scan", "tool.fixture", "192.0.2.10", impact="low")
    core.store.create_mission("m", "controlled lab")
    core.store.save_workflow_plan("p", WorkflowPlan("m", (original,)))
    assert core.authorize_workflow_task_for_plan("p", original) is True
    assert core.authorize_workflow_task_for_plan(
        "p", WorkflowTask("scan", "tool.fixture", "192.0.2.11", impact="low"),
    ) is False
    assert core.authorize_workflow_task_for_plan("missing", original) is False
    core.store.request_workflow_cancellation("p")
    assert core.authorize_workflow_task_for_plan("p", original) is False


def test_engine_v2_plan_authorization_rejects_tampered_sqlite_plan(tmp_path):
    from types import SimpleNamespace

    from whaxon.core import Core
    from whaxon.core.capabilities import CapabilityManifest, CapabilityRegistry
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    core = Core.__new__(Core)
    core.store = JobStore(tmp_path / "tampered-auth.db")
    core.capabilities = CapabilityRegistry()
    core.capabilities.register(CapabilityManifest(
        capability_id="tool.fixture", provider_id="whaxon.adapter.fixture",
        provider_version="catalog-v1", transports=("local_process",),
        permissions=(), impact="low",
    ))
    core.scope = SimpleNamespace(check=lambda target: SimpleNamespace(allowed=True))
    task = WorkflowTask("scan", "tool.fixture", "192.0.2.10", impact="low")
    core.store.create_mission("m", "controlled lab")
    core.store.save_workflow_plan("p", WorkflowPlan("m", (task,)))
    conn = core.store._conn()
    try:
        conn.execute(
            "UPDATE workflow_tasks SET target=? WHERE plan_id=?",
            ("192.0.2.200", "p"),
        )
    finally:
        conn.close()
    assert core.authorize_workflow_task_for_plan("p", task) is False


def test_engine_v2_scheduler_requires_plan_bound_policy_by_default(tmp_path):
    from whaxon.core import Core
    from whaxon.core.store import JobStore

    core = Core.__new__(Core)
    core.store = JobStore(tmp_path / "scheduler-approval-default.db")
    with pytest.raises(ValueError, match="plan_id required"):
        core.workflow_scheduler()


def test_engine_v2_scheduler_uses_plan_bound_approval_instead_of_scope_only(tmp_path):
    import asyncio
    from types import SimpleNamespace

    from whaxon.core import Core
    from whaxon.core.capabilities import CapabilityManifest, CapabilityRegistry
    from whaxon.core.store import JobStore
    from whaxon.core.workflow import WorkflowPlan, WorkflowTask

    core = Core.__new__(Core)
    core.store = JobStore(tmp_path / "scheduler-plan-approval.db")
    core.capabilities = CapabilityRegistry()
    core.capabilities.register(CapabilityManifest(
        capability_id="tool.fixture", provider_id="whaxon.adapter.fixture",
        provider_version="catalog-v1", transports=("local_process",),
        permissions=("network.scan",), impact="moderate",
    ))
    core.scope = SimpleNamespace(check=lambda target: SimpleNamespace(allowed=True))
    core.store.create_mission("m", "controlled lab")
    task = WorkflowTask(
        "scan", "tool.fixture", "192.0.2.10",
        permissions=("network.scan",), impact="moderate",
    )
    core.store.save_workflow_plan("p", WorkflowPlan("m", (task,)))
    dispatched = []
    scheduler = core.workflow_scheduler(
        plan_id="p", dispatch=lambda task: dispatched.append(task.id),
    )
    result = asyncio.run(scheduler.run("p"))
    assert dispatched == []
    assert result["tasks"] == [{"id": "scan", "status": "blocked"}]


def test_engine_v2_scope_revocation_from_another_process_takes_effect(tmp_path):
    import json

    from whaxon.core import Core
    from whaxon.core.capabilities import CapabilityManifest, CapabilityRegistry
    from whaxon.core.scope import ScopeManager

    scope_path = tmp_path / "scope.json"
    scope_path.write_text(json.dumps({
        "enabled": True, "engagement": "test",
        "in_scope": ["lab.example"], "out_of_scope": [],
    }), encoding="utf-8")
    core = Core.__new__(Core)
    core.capabilities = CapabilityRegistry()
    core.capabilities.register(CapabilityManifest(
        capability_id="tool.fixture", provider_id="whaxon.adapter.fixture",
        provider_version="catalog-v1", transports=("local_process",),
        permissions=(), impact="low",
    ))
    core.scope = ScopeManager(scope_path)
    task = WorkflowTask("scan", "tool.fixture", "lab.example", impact="low")
    assert core.authorize_workflow_task(task) is True
    scope_path.write_text(json.dumps({
        "enabled": True, "engagement": "test",
        "in_scope": ["lab.example"], "out_of_scope": ["lab.example"],
    }), encoding="utf-8")
    assert core.authorize_workflow_task(task) is False
    scope_path.write_text("{invalid", encoding="utf-8")
    assert core.authorize_workflow_task(task) is False


@pytest.mark.parametrize("target, expected", [
    ("192.0.2.10", "ip"),
    ("2001:db8::1", "ip"),
    ("lab.example", "hostname"),
    ("https://lab.example/path", "url"),
])
def test_catalog_target_type_classification_is_pure(target, expected):
    from whaxon.core.providers import _target_type
    assert _target_type(target) == expected


@pytest.mark.parametrize("target", [
    "", " lab.example", "lab.example/path", "user@lab.example",
    "https://user:secret@lab.example/", "https://lab.example/#fragment",
    "ftp://lab.example/", "lab.example?query=1",
])
def test_catalog_target_type_rejects_ambiguous_or_credential_targets(target):
    from whaxon.core.providers import _target_type
    with pytest.raises(ValueError):
        _target_type(target)


def test_catalog_provider_rejects_unbound_registry_provider_without_dispatch(monkeypatch):
    import asyncio

    import whaxon.adapters
    from whaxon.core.capabilities import CapabilityManifest

    monkeypatch.setattr(whaxon.adapters, "get_adapter", lambda tool_id: object())
    registry = CapabilityRegistry()
    runner = _Runner()
    provider = CatalogAdapterProvider(
        catalog=_Catalog([_tool()]), runner=runner, store=_Store(), registry=registry,
    )
    # Higher-readiness third-party provider cannot be used as a catalog adapter.
    registry.register(CapabilityManifest(
        capability_id="tool.nmap", provider_id="other.provider",
        provider_version="1", transports=("local_process",),
        target_types=("ip",), readiness="end_to_end_verified",
    ))
    result = asyncio.run(provider.dispatch(WorkflowTask("scan", "tool.nmap", "192.0.2.10")))
    assert result["tool_id"] == "nmap"
    assert len(runner.calls) == 1


def test_catalog_provider_rejects_unsupported_target_type_before_dispatch(monkeypatch):
    import whaxon.adapters
    from whaxon.core.capabilities import CapabilityUnavailable

    monkeypatch.setattr(whaxon.adapters, "get_adapter", lambda tool_id: object())
    registry = CapabilityRegistry()
    runner = _Runner()
    CatalogAdapterProvider(
        catalog=_Catalog([_tool()]), runner=runner, store=_Store(), registry=registry,
    )
    # Explicit resolver contract: a provider limited to hostnames must not
    # match a URL task, even when the capability identifier is identical.
    with pytest.raises(CapabilityUnavailable):
        registry.resolve("tool.nmap", __import__(
            "whaxon.core.capabilities", fromlist=["CapabilityRequirements"]
        ).CapabilityRequirements(target_type="unsupported-target"))
    assert runner.calls == []


def test_catalog_dispatch_rejects_undeclared_task_permissions(monkeypatch):
    import asyncio

    import whaxon.adapters
    from whaxon.core.capabilities import CapabilityUnavailable

    monkeypatch.setattr(whaxon.adapters, "get_adapter", lambda tool_id: object())
    runner = _Runner()
    provider = CatalogAdapterProvider(
        catalog=_Catalog([_tool()]), runner=runner, store=_Store(),
        registry=CapabilityRegistry(),
    )
    with pytest.raises(CapabilityUnavailable, match="permissions"):
        asyncio.run(provider.dispatch(WorkflowTask(
            "scan", "tool.nmap", "192.0.2.10",
            permissions=("credentials.read",), impact="moderate",
        )))
    assert runner.calls == []


def test_catalog_dispatch_rejects_mutated_registry_manifest_before_runner(monkeypatch):
    import asyncio

    import whaxon.adapters
    from whaxon.core.capabilities import CapabilityManifest, CapabilityUnavailable

    monkeypatch.setattr(whaxon.adapters, "get_adapter", lambda tool_id: object())
    registry = CapabilityRegistry()
    runner = _Runner()
    provider = CatalogAdapterProvider(
        catalog=_Catalog([_tool()]), runner=runner, store=_Store(), registry=registry,
    )
    registry.register(CapabilityManifest(
        capability_id="tool.nmap", provider_id="whaxon.adapter.nmap",
        provider_version="catalog-v2", transports=("local_process",),
        target_types=("hostname", "ip", "url"), permissions=("network.scan",),
        impact="moderate", readiness="end_to_end_verified",
    ))
    with pytest.raises(CapabilityUnavailable):
        asyncio.run(provider.dispatch(WorkflowTask("scan", "tool.nmap", "192.0.2.10")))
    assert runner.calls == []


def test_catalog_dispatch_rejects_job_identity_mismatch(monkeypatch):
    import asyncio

    import whaxon.adapters

    monkeypatch.setattr(whaxon.adapters, "get_adapter", lambda tool_id: object())

    class WrongJobStore(_Store):
        def get(self, job_id):
            return {**super().get(job_id), "tool": "nikto", "target": "192.0.2.99"}

    provider = CatalogAdapterProvider(
        catalog=_Catalog([_tool()]), runner=_Runner(),
        store=WrongJobStore(), registry=CapabilityRegistry(),
    )
    with pytest.raises(RuntimeError, match="identity"):
        asyncio.run(provider.dispatch(WorkflowTask("scan", "tool.nmap", "192.0.2.10")))


def test_core_authorization_rejects_provider_without_local_transport():
    from types import SimpleNamespace

    from whaxon.core import Core
    from whaxon.core.capabilities import CapabilityManifest

    core = Core.__new__(Core)
    core.capabilities = CapabilityRegistry()
    core.capabilities.register(CapabilityManifest(
        capability_id="tool.fixture", provider_id="remote.fixture",
        provider_version="1", transports=("remote_agent",),
        target_types=("ip",), impact="low",
    ))
    core.scope = SimpleNamespace(check=lambda target: SimpleNamespace(allowed=True))
    assert core.authorize_workflow_task(
        WorkflowTask("scan", "tool.fixture", "192.0.2.10", impact="low"),
    ) is False
