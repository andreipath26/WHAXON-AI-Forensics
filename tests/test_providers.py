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
