"""Authorization regression coverage for low-impact network effects."""
from __future__ import annotations

import time

import pytest

from whaxon.core import Core
from whaxon.core.capabilities import CapabilityManifest
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


class _ProviderBindings:
    def __init__(self, manifest: CapabilityManifest) -> None:
        self.manifest = manifest

    def manifest_for(self, capability_id: str) -> CapabilityManifest:
        assert capability_id == self.manifest.capability_id
        return self.manifest

    def plan_binding_valid(self, _task: WorkflowTask, _metadata: dict) -> bool:
        return True


def _authorize_test_plan(
    tmp_path,
    monkeypatch,
    *,
    impact: str,
    permissions: tuple[str, ...],
    side_effects: tuple[str, ...],
) -> tuple[Core, WorkflowTask]:
    core = Core(tmp_path)
    core.create_mission("approval-mission", "Exercise exact V2 plan authorization")
    manifest = CapabilityManifest(
        capability_id="fixture.network_effect",
        provider_id="fixture.authorization",
        provider_version="1.0.0",
        transports=("local_process",),
        target_types=("hostname",),
        permissions=permissions,
        side_effects=side_effects,
        impact=impact,
    )
    task = WorkflowTask(
        id="task-1",
        capability_id=manifest.capability_id,
        target="example.test",
        permissions=permissions,
        impact=impact,
    )
    core.save_workflow_plan("approval-plan", WorkflowPlan("approval-mission", (task,)))
    core.providers = _ProviderBindings(manifest)
    monkeypatch.setattr(core, "authorize_workflow_task", lambda _task: True)
    return core, task


@pytest.mark.parametrize(
    ("permissions", "side_effects"),
    [
        (("network.scan",), ()),
        ((), ("network_traffic",)),
    ],
)
def test_low_impact_network_effect_requires_exact_plan_approval(
    tmp_path, monkeypatch, permissions, side_effects,
):
    core, task = _authorize_test_plan(
        tmp_path,
        monkeypatch,
        impact="low",
        permissions=permissions,
        side_effects=side_effects,
    )

    assert core.authorize_workflow_task_for_plan("approval-plan", task) is False
    assert core.grant_workflow_approval(
        "approval-plan", task.id, "approval-exact", "operator",
        expires_at=time.time() + 3600,
    )
    assert core.authorize_workflow_task_for_plan("approval-plan", task) is True


def test_non_network_read_only_plan_remains_auto_authorized(tmp_path, monkeypatch):
    core, task = _authorize_test_plan(
        tmp_path,
        monkeypatch,
        impact="read_only",
        permissions=(),
        side_effects=(),
    )

    assert core.authorize_workflow_task_for_plan("approval-plan", task) is True


def test_approval_queue_includes_low_impact_network_candidates_only(tmp_path):
    core = Core(tmp_path)
    core.create_mission("queue-mission", "Exercise the backend approval candidate service")

    cases = (
        ("permission-task", "fixture.network_permission", ("network.scan",), (), "low"),
        ("effect-task", "fixture.network_effect", (), ("network_traffic",), "low"),
        ("read-only-task", "fixture.read_only", (), (), "read_only"),
    )
    for task_id, capability_id, permissions, side_effects, impact in cases:
        manifest = CapabilityManifest(
            capability_id=capability_id,
            provider_id="fixture.approval-queue",
            provider_version="1.0.0",
            transports=("local_process",),
            target_types=("hostname",),
            permissions=permissions,
            side_effects=side_effects,
            impact=impact,
        )
        core.capabilities.register(manifest)
        task = WorkflowTask(
            id=task_id,
            capability_id=capability_id,
            target="example.test",
            permissions=permissions,
            impact=impact,
        )
        plan = WorkflowPlan(
            "queue-mission",
            (task,),
            metadata={
                "provider_bindings": {
                    task_id: {
                        "provider_id": manifest.provider_id,
                        "manifest_fingerprint": manifest.fingerprint,
                    },
                },
            },
        )
        core.save_workflow_plan(f"plan-{task_id}", plan)

    candidates = core.workflow_approval_queue(limit=2)
    candidate_ids = {item["task_key"] for item in candidates}

    assert candidate_ids == {"permission-task", "effect-task"}
    assert len(core.workflow_approval_queue(limit=1)) == 1
    assert all("permissions_json" not in item and "plan_json" not in item for item in candidates)



@pytest.mark.parametrize(
    ("scope_mode", "expected_method"),
    [
        ("network", "check_for_execution"),
        ("dns_query", "check_for_dns_query"),
        ("pinned_network", "check_for_pinned_execution"),
        ("unknown", None),
    ],
)
def test_core_scope_preflight_uses_manifest_scope_mode(
    tmp_path, scope_mode, expected_method,
):
    from types import SimpleNamespace

    core = Core(tmp_path)
    calls = []

    class _Scope:
        def load(self):
            return None

        def check_for_execution(self, target):
            calls.append(("check_for_execution", target))
            return SimpleNamespace(allowed=True)

        def check_for_dns_query(self, target):
            calls.append(("check_for_dns_query", target))
            return SimpleNamespace(allowed=True)

        def check_for_pinned_execution(self, target):
            calls.append(("check_for_pinned_execution", target))
            return SimpleNamespace(allowed=True)

    core.scope = _Scope()
    manifest = CapabilityManifest(
        capability_id="fixture.scope_mode",
        provider_id="fixture.scope_mode",
        provider_version="1.0.0",
        transports=("local_process",),
        target_types=("hostname",),
        permissions=("network.scan",),
        impact="moderate",
        scope_mode=scope_mode if scope_mode != "unknown" else "network",
    )
    if scope_mode == "unknown":
        # Simulate malformed persisted/provider metadata reaching the policy
        # boundary; normal manifest construction rejects this mode earlier.
        manifest = SimpleNamespace(
            capability_id=manifest.capability_id,
            impact=manifest.impact,
            permissions=manifest.permissions,
            scope_mode="unknown",
        )

    class _Bindings:
        def resolve_task(self, _task, *, require_installed):
            assert require_installed is True
            return SimpleNamespace(manifest=manifest)

    core.providers = _Bindings()
    task = WorkflowTask(
        id="scope-mode-task",
        capability_id="fixture.scope_mode",
        target="example.test",
        permissions=("network.scan",),
        impact="moderate",
    )

    assert core.authorize_workflow_task(task) is (expected_method is not None)
    if expected_method is None:
        assert calls == []
    else:
        assert calls == [(expected_method, "example.test")]


@pytest.mark.parametrize("scope_mode", ["dns_query", "pinned_network"])
def test_core_dns_and_pinned_preflights_do_not_resolve_hostname(
    tmp_path, monkeypatch, scope_mode,
):
    import json
    import socket

    from whaxon.core.scope import ScopeManager

    data_dir = tmp_path / "core-data"
    data_dir.mkdir()
    core = Core(data_dir)
    scope_path = tmp_path / "scope.json"
    scope_path.write_text(json.dumps({
        "engagement": "scope-mode-test",
        "enabled": True,
        "in_scope": ["*.acme.test", "10.0.0.0/8"],
        "out_of_scope": [],
    }))
    core.scope = ScopeManager(scope_path)

    def unexpected_resolution(*_args, **_kwargs):
        pytest.fail("Core preflight must not resolve the target hostname")

    monkeypatch.setattr(socket, "getaddrinfo", unexpected_resolution)

    manifest = CapabilityManifest(
        capability_id="fixture.scope_mode",
        provider_id="fixture.scope_mode",
        provider_version="1.0.0",
        transports=("local_process",),
        target_types=("hostname",),
        permissions=("network.scan",),
        impact="moderate",
        scope_mode=scope_mode,
    )

    from types import SimpleNamespace

    class _Bindings:
        def resolve_task(self, _task, *, require_installed):
            assert require_installed is True
            return SimpleNamespace(manifest=manifest)

    core.providers = _Bindings()
    task = WorkflowTask(
        id="scope-mode-no-dns",
        capability_id="fixture.scope_mode",
        target="service.acme.test",
        permissions=("network.scan",),
        impact="moderate",
    )

    assert core.authorize_workflow_task(task) is True
