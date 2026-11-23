from __future__ import annotations

from whaxon.core import workflow_proposals
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


class _Store:
    def get_mission(self, mission_id):
        return {"id": mission_id}


class _Core:
    store = _Store()


def _proposal(mission_id, check):
    task = WorkflowTask(
        id="task-1", capability_id=f"recon.{check}", target="example.test",
        inputs={}, permissions=("network.scan",), impact="moderate",
        timeout_s=30, idempotency_key=f"{check}-key",
    )
    plan = WorkflowPlan(
        mission_id=mission_id,
        tasks=(task,),
        metadata={"provider_bindings": {"task-1": {
            "provider_id": f"provider.{check}",
            "provider_version": "1",
            "manifest_fingerprint": "a" * 64,
        }}},
    )
    return {"status": "proposed", "plan": plan.to_dict()}


def test_default_recon_proposal_combines_ready_providers_and_lists_omissions(monkeypatch):
    builders = (
        "propose_passive_dns_plan",
        "propose_dns_full_posture_plan",
        "propose_tls_certificate_plan",
        "propose_passive_https_recon_plan",
        "propose_passive_redirect_observation_plan",
        "propose_passive_robots_recon_plan",
        "propose_passive_security_txt_recon_plan",
    )
    for name in builders:
        check = {
            "propose_passive_dns_plan": "dns",
            "propose_dns_full_posture_plan": "dns_full",
            "propose_tls_certificate_plan": "ssl",
            "propose_passive_https_recon_plan": "https",
            "propose_passive_redirect_observation_plan": "redirects",
            "propose_passive_robots_recon_plan": "robots",
            "propose_passive_security_txt_recon_plan": "security_txt",
        }[name]
        monkeypatch.setattr(
            workflow_proposals, name,
            lambda _core, *, mission_id, plan_id, target, check=check:
                _proposal(mission_id, check),
        )

    result = workflow_proposals.propose_passive_recon_plan(
        _Core(), mission_id="mission-1", plan_id="recon-1", target="example.test",
    )

    assert result["status"] == "proposed"
    assert result["execution_submitted"] is False
    assert result["approval_granted"] is False
    assert result["included_checks"] == [
        "dns", "dns_full", "ssl", "https", "headers", "redirects", "robots",
        "security_txt", "tech", "cookies", "waf",
    ]
    assert [task["id"] for task in result["plan"]["tasks"]] == [
        "task-dns", "task-dns_full", "task-ssl", "task-https",
        "task-redirects", "task-robots", "task-security_txt",
    ]
    assert set(result["plan"]["metadata"]["provider_bindings"]) == {
        task["id"] for task in result["plan"]["tasks"]
    }
    assert {
        binding["provider_version"]
        for binding in result["plan"]["metadata"]["provider_bindings"].values()
    } == {"1"}
    assert result["omitted_checks"] == []
    assert list(result["plan"]["metadata"]["omitted_checks"]) == result["omitted_checks"]
    assert result["plan"]["metadata"]["coverage_contract"] == {
        "schema_version": 1,
        "checklist": list(workflow_proposals.PASSIVE_RECON_CHECKS),
        "requested": list(workflow_proposals.PASSIVE_RECON_CHECKS),
        "included": result["included_checks"],
        "dispositions": [],
    }
    assert result["plan"]["metadata"]["provider_outputs"]["task-https"] == (
        "http_header_missing", "tech_detected", "open_port", "cookie_insecure", "waf_detected",
    )


def test_default_recon_plan_persists_provider_unavailable_disposition(monkeypatch):
    builders = {
        "propose_passive_dns_plan": "dns",
        "propose_dns_full_posture_plan": "dns_full",
        "propose_tls_certificate_plan": "ssl",
        "propose_passive_https_recon_plan": "https",
        "propose_passive_headers_recon_plan": "headers",
        "propose_passive_redirect_observation_plan": "redirects",
        "propose_passive_robots_recon_plan": "robots",
        "propose_passive_security_txt_recon_plan": "security_txt",
    }
    for name, check in builders.items():
        proposal = (
            {"status": "blocked", "reason": "provider is not ready"}
            if check == "dns" else _proposal("mission-1", check)
        )
        monkeypatch.setattr(
            workflow_proposals, name,
            lambda _core, *, mission_id, plan_id, target, proposal=proposal: proposal,
        )

    result = workflow_proposals.propose_passive_recon_plan(
        _Core(), mission_id="mission-1", plan_id="recon-1", target="example.test",
    )

    unavailable = [
        item for item in result["plan"]["metadata"]["omitted_checks"]
        if item["check"] == "dns"
    ]
    assert unavailable == [{
        "check": "dns", "reason": "provider is not ready",
        "disposition": "provider_unavailable",
    }]
    assert result["plan"]["metadata"]["coverage_contract"]["dispositions"] == [{
        "check_id": "dns", "disposition": "provider_unavailable",
    }]


def test_explicit_unknown_check_blocks_entire_proposal():
    result = workflow_proposals.propose_passive_recon_plan(
        _Core(), mission_id="mission-1", plan_id="recon-1",
        target="example.test", checks=["dns", "not-a-check"],
    )

    assert result["status"] == "blocked"
    assert "not-a-check" in result["reason"]
    assert result["execution_submitted"] is False


def test_explicit_bundled_http_checks_use_one_https_task(monkeypatch):
    calls = []

    def propose_https(_core, *, mission_id, plan_id, target):
        calls.append((plan_id, target))
        return _proposal(mission_id, "https")

    monkeypatch.setattr(workflow_proposals, "propose_passive_https_recon_plan", propose_https)
    result = workflow_proposals.propose_passive_recon_plan(
        _Core(), mission_id="mission-1", plan_id="recon-1", target="example.test",
        checks=["headers", "tech", "cookies", "waf"],
    )

    assert result["status"] == "proposed"
    assert result["included_checks"] == ["headers", "tech", "cookies", "waf"]
    assert len(result["plan"]["tasks"]) == 1
    assert result["plan"]["tasks"][0]["id"] == "task-https"
    assert result["plan"]["metadata"]["provider_outputs"]["task-https"] == (
        "http_header_missing", "tech_detected", "open_port", "cookie_insecure", "waf_detected",
    )
    assert calls == [("recon-1-https", "example.test")]


def test_unavailable_https_bundle_is_reported_for_every_requested_alias(monkeypatch):
    builders = {
        "propose_passive_dns_plan": "dns",
        "propose_dns_full_posture_plan": "dns_full",
        "propose_tls_certificate_plan": "ssl",
        "propose_passive_https_recon_plan": "https",
        "propose_passive_redirect_observation_plan": "redirects",
        "propose_passive_robots_recon_plan": "robots",
        "propose_passive_security_txt_recon_plan": "security_txt",
    }
    for name, check in builders.items():
        proposal = (
            {"status": "blocked", "reason": "HTTPS provider is not ready"}
            if check == "https" else _proposal("mission-1", check)
        )
        monkeypatch.setattr(
            workflow_proposals, name,
            lambda _core, *, mission_id, plan_id, target, proposal=proposal: proposal,
        )

    default = workflow_proposals.propose_passive_recon_plan(
        _Core(), mission_id="mission-1", plan_id="recon-1", target="example.test",
    )
    unavailable = [
        item for item in default["omitted_checks"]
        if item["check"] in {"https", "headers", "tech", "cookies", "waf"}
    ]
    assert [item["check"] for item in unavailable] == [
        "https", "headers", "tech", "cookies", "waf",
    ]
    assert {item["disposition"] for item in unavailable} == {"provider_unavailable"}

    explicit = workflow_proposals.propose_passive_recon_plan(
        _Core(), mission_id="mission-1", plan_id="recon-2", target="example.test",
        checks=["cookies"],
    )
    assert explicit["status"] == "blocked"
    assert "cookies check is unavailable" in explicit["reason"]
    assert "plan" not in explicit


def test_explicit_unavailable_check_does_not_create_partial_plan(monkeypatch):
    monkeypatch.setattr(
        workflow_proposals, "propose_passive_dns_plan",
        lambda *_args, **_kwargs: {"status": "blocked", "reason": "provider is not ready"},
    )

    result = workflow_proposals.propose_passive_recon_plan(
        _Core(), mission_id="mission-1", plan_id="recon-1",
        target="example.test", checks=["dns"],
    )

    assert result["status"] == "blocked"
    assert "provider is not ready" in result["reason"]
    assert "plan" not in result
