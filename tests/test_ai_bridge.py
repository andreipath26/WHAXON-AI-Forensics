"""Integration tests for the core<->ai bridge."""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from whaxon.ai import ExecutorLimits, NullProvider
from whaxon.ai.actions import Action
from whaxon.ai.provider import Provider
from whaxon.core import Core
from whaxon.core.ai_bridge import build_executor


@pytest.fixture
def core(tmp_path: Path) -> Core:
    data = tmp_path / "data"
    data.mkdir()
    (data / "tools.json").write_text(
        "{\"tools\":[{\"id\":\"echo\",\"name\":\"Echo\","
        "\"category\":\"test\",\"binary\":\"/bin/echo\","
        "\"args\":\"{target}\"}]}"
    )
    return Core(data_dir=data)


def test_bridge_runs_null_provider_end_to_end(core: Core) -> None:
    ex = build_executor(core, provider=NullProvider())
    history = asyncio.run(ex.run("anything", job_id_prefix="aitest"))
    assert len(history) == 1
    assert history[0].action.kind == "stop"
    assert history[0].ok is True


def test_bridge_rejects_out_of_scope_before_runner(core: Core) -> None:
    calls: list[tuple] = []

    async def spy(*a, **kw):
        calls.append((a, kw))
        return "never"

    core.runner.run_tool = spy  # type: ignore[assignment]

    class OneShot(Provider):
        name = "one-shot"
        def plan_step(self, goal, history, catalog, scope_summary, step, max_steps, phase="recon", prior_runs=None):
            if step == 1:
                return Action.run_tool("echo", "8.8.8.8", rationale="t",
                                       confidence=0.9, ai_source="one-shot")
            return Action.stop("done", ai_source="one-shot")

    ex = build_executor(core, provider=OneShot(),
                        limits=ExecutorLimits(max_steps=3))
    history = asyncio.run(ex.run("scan something"))
    assert history[0].ok is False
    assert "out of scope" in history[0].error
    assert calls == []


def test_bridge_rejects_unknown_tool_before_runner(core: Core) -> None:
    calls: list[tuple] = []

    async def spy(*a, **kw):
        calls.append((a, kw))
        return "never"

    core.runner.run_tool = spy  # type: ignore[assignment]

    class OneShot(Provider):
        name = "one-shot"
        def plan_step(self, goal, history, catalog, scope_summary, step, max_steps, phase="recon", prior_runs=None):
            if step == 1:
                return Action.run_tool("ghost", "127.0.0.1", rationale="t",
                                       confidence=0.9, ai_source="one-shot")
            return Action.stop("done", ai_source="one-shot")

    ex = build_executor(core, provider=OneShot(),
                        limits=ExecutorLimits(max_steps=3))
    history = asyncio.run(ex.run("scan something"))
    assert history[0].ok is False
    assert "not in catalog" in history[0].error
    assert calls == []

def test_bridge_honours_rules_env(monkeypatch) -> None:
    from whaxon.ai.providers.rules import RulesProvider
    from whaxon.core.ai_bridge import build_executor
    monkeypatch.setenv("WHAXON_AI_ENABLED", "true")
    monkeypatch.setenv("WHAXON_AI_PROVIDER", "rules")
    import tempfile
    from pathlib import Path as _P
    with tempfile.TemporaryDirectory() as td:
        d = _P(td) / "data"
        d.mkdir()
        (d / "tools.json").write_text("{\"tools\":[]}")
        core = Core(data_dir=d)
        ex = build_executor(core)
        assert isinstance(ex.agent.provider, RulesProvider)
        assert ex.agent.provider.name == "rules"


def test_bridge_unknown_provider_falls_back(monkeypatch) -> None:
    from whaxon.ai.provider import NullProvider
    from whaxon.core.ai_bridge import build_executor
    monkeypatch.setenv("WHAXON_AI_ENABLED", "true")
    monkeypatch.setenv("WHAXON_AI_PROVIDER", "gpt-9000")
    import tempfile
    from pathlib import Path as _P
    with tempfile.TemporaryDirectory() as td:
        d = _P(td) / "data"
        d.mkdir()
        (d / "tools.json").write_text("{\"tools\":[]}")
        core = Core(data_dir=d)
        ex = build_executor(core)
        assert isinstance(ex.agent.provider, NullProvider)


def test_ai_plan_persists_a_typed_inference_trace(core: Core, monkeypatch) -> None:
    from types import SimpleNamespace

    from whaxon.ai import Action as ProposedAction
    from whaxon.ai import Provider as BaseProvider
    from whaxon.core.ai_bridge import propose_v2_workflow_plan
    from whaxon.core.capabilities import CapabilityManifest
    from whaxon.core.providers import SEMANTIC_OPERATION_IDS

    capability_id = SEMANTIC_OPERATION_IDS.get("nmap", "tool.nmap")

    class OneShot(BaseProvider):
        name = "trace-fixture"

        def plan_step(self, *args, **kwargs):
            return ProposedAction.run_tool(
                "nmap", "192.0.2.10", rationale="Inventory the authorized lab.",
                confidence=0.8, ai_source="trace-fixture",
            )

    class OneShotAgent:
        def __init__(self, provider):
            self.provider = provider

        def audit(self, _goal):
            return {"feasible": True}

        def next_action(self, **kwargs):
            return self.provider.plan_step(**kwargs)

    manifest = CapabilityManifest(
        capability_id, "trace-fixture", "1", ("local_process",),
        impact="moderate", input_schema={
            "type": "object", "properties": {}, "required": [],
            "additionalProperties": False,
        },
    )

    class Providers:
        def manifest_for(self, _capability_id):
            return manifest

        def resolve_task(self, _task, *, require_installed=False):
            assert require_installed is True
            return SimpleNamespace(manifest=manifest)

    core.create_mission("trace-mission", "authorized lab")
    core.scope.check = lambda _target: SimpleNamespace(allowed=True, reason="")
    core.providers = Providers()
    core.capability_inventory = lambda: [{
        "capability_id": capability_id, "provider_id": manifest.provider_id,
        "selected_for_execution": True, "installed": True, "executable": True,
    }]
    core.catalog.list = lambda: [SimpleNamespace(
        id="nmap", name="Nmap", category="network",
    )]
    monkeypatch.setattr("whaxon.ai.Agent", OneShotAgent)

    result = propose_v2_workflow_plan(
        core, mission_id="trace-mission", plan_id="trace-plan",
        goal="Inventory my authorized lab", target="192.0.2.10",
        provider=OneShot(),
    )
    assert result["status"] == "proposed", result
    trace = result["proposal_trace"]
    assert trace["schema_version"] == "whaxon.ai-proposal.v1"
    assert trace["inference"]["rationale"] == "Inventory the authorized lab."
    assert trace["source_record_refs"] == []
    assert trace["observations"] == []
    assert trace["uncertainty"] == [
        "No persisted observation was supplied to this proposal."
    ]
    import json
    saved_trace = json.loads(json.dumps(result["plan"]["metadata"]["ai_proposal"]))
    assert saved_trace == trace
    assert result["approval_granted"] is False
    assert result["execution_submitted"] is False
