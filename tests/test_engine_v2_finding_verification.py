"""Scheduler ownership and sealed evidence for bounded V2 finding verification."""
from __future__ import annotations

import asyncio
import hashlib
import json
import threading
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from whaxon.core import Core
from whaxon.core.findings import Finding
from whaxon.core.providers import FindingVerificationProvider
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


class _SQLiFixture(BaseHTTPRequestHandler):
    requests = 0
    paths = []
    vulnerable = True
    reflect_xss = True
    send_cookie = False
    secure_cookie = False
    send_csp = False
    after_response = None
    scope_path = None
    revoke_after = None

    def do_GET(self):
        type(self).requests += 1
        type(self).paths.append(self.path)
        if (
            type(self).scope_path is not None
            and type(self).revoke_after == type(self).requests
        ):
            type(self).scope_path.write_text(json.dumps({
                "engagement": "revoked-fixture-scope",
                "enabled": True,
                "in_scope": [],
                "out_of_scope": [],
                "notes": "revoked during controlled test",
            }), encoding="utf-8")
        query = parse_qs(urlsplit(self.path).query)
        value = query.get("id", [""])[0]
        xss_value = query.get("q", [""])[0]
        body = (
            xss_value.encode() if type(self).reflect_xss and "whaxon_xss_" in xss_value
            else b"You have an error in your SQL syntax"
            if "'" in value and type(self).vulnerable else b"Product found"
        )
        self.send_response(200)
        if type(self).send_csp:
            self.send_header("Content-Security-Policy", "default-src 'self'")
        if type(self).send_cookie:
            cookie_flags = "; HttpOnly; Secure" if type(self).secure_cookie else ""
            self.send_header("Set-Cookie", f"session=fixture; Path=/{cookie_flags}")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        callback = type(self).after_response
        if callback is not None:
            callback()
        self.wfile.write(body)

    def log_message(self, *_args):
        pass


def _bound_plan(core, *, plan_id, capability_id, target, inputs):
    core.create_mission(plan_id, "Exercise the bounded verifier on the controlled fixture")
    task = WorkflowTask(
        id="verification", capability_id=capability_id, target=target,
        inputs=inputs, permissions=("network.verify",), impact="moderate",
        timeout_s=75,
    )
    manifest = core.providers.manifest_for(capability_id)
    plan = WorkflowPlan(
        mission_id=plan_id, tasks=(task,),
        metadata={"provider_bindings": {task.id: {
            "provider_id": manifest.provider_id,
            "manifest_fingerprint": manifest.fingerprint,
        }}},
    )
    core.save_workflow_plan(plan_id, plan)
    core.grant_workflow_approval(
        plan_id, task.id, f"approval-{plan_id}", "ci-operator",
        expires_at=time.time() + 120,
    )
    return task


async def _seed_sealed_source(
    core, *, plan_id, target, request_context=None, finding_data=None, kind="sqli",
):
    """Persist a test-only SQLmap result through the real scheduler seal path."""
    from whaxon.core.workflow import WorkflowPlan

    core.create_mission(plan_id, "Seed a sealed in-process scanner fixture")
    tool_id = (
        "nuclei" if kind == "xss"
        else "nmap" if kind in {"http_header_missing", "cookie_insecure"}
        else "sqlmap"
    )
    task = WorkflowTask(
        id="scan", capability_id=f"tool.{tool_id}", target=target,
        permissions=("network.scan",), impact="moderate",
    )
    core.save_workflow_plan(plan_id, WorkflowPlan(mission_id=plan_id, tasks=(task,)))
    source_job = hashlib.sha256(plan_id.encode("utf-8")).hexdigest()[:12]

    async def fake_scan(_task):
        core.store.create(source_job)
        core.store.set_started(source_job, tool_id, target)
        core.store.mark_engine_v2_execution_job(source_job)
        data = finding_data or (
            {"header": "Content-Security-Policy", "url": target}
            if kind == "http_header_missing"
            else {"cookie": "session", "missing": "httponly", "url": target}
            if kind == "cookie_insecure"
            else {"parameter": "q" if kind == "xss" else "id"}
        )
        core.store.append_finding(source_job, Finding(
            kind=kind, severity="high", source=tool_id,
            data=data, raw_line="controlled fixture finding",
            request_context=(request_context if request_context is not None else {
                "method": "GET", "url": target, "parameter": "id",
            }),
        ), 0)
        core.store.set_finished(source_job, 0, 0.01)
        return {
            "job_id": source_job, "tool_id": tool_id, "target": target,
            "exit_code": 0,
        }

    scheduler = core.workflow_scheduler(
        plan_id=plan_id, authorize=lambda _task: True, dispatch=fake_scan,
    )
    result = await scheduler.run(plan_id, max_tasks=1, max_concurrency=1)
    assert result["tasks"] == [{"id": "scan", "status": "succeeded"}]
    assert core.workflow_evidence(plan_id)["all_evidence_integrity_verified"] is True
    return source_job


def test_v2_verify_and_retest_are_scheduler_owned_and_sealed(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.vulnerable = True
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)

            source_job = await _seed_sealed_source(
                core, plan_id="source-plan", target=target,
            )

            _bound_plan(
                core, plan_id="verification-plan",
                capability_id=FindingVerificationProvider.VERIFY,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            verified = await core.run_workflow_plan(
                "verification-plan", max_tasks=1, max_concurrency=1,
            )
            assert verified["tasks"] == [{"id": "verification", "status": "succeeded"}]
            verify_evidence = core.workflow_evidence("verification-plan")
            assert verify_evidence["all_evidence_recorded"] is True
            assert verify_evidence["all_evidence_integrity_verified"] is True, verify_evidence
            verify_attempt = verify_evidence["attempts"][0]
            assert verify_attempt["findings"][0]["verification_status"] == "verified"
            assert verify_attempt["findings"][0]["verification_reason"].startswith(
                "SQL error signature"
            )

            _bound_plan(
                core, plan_id="retest-plan",
                capability_id=FindingVerificationProvider.RETEST,
                target=target,
                inputs={"source_job_id": verify_attempt["job_id"], "finding_seq": 0},
            )
            retested = await core.run_workflow_plan(
                "retest-plan", max_tasks=1, max_concurrency=1,
            )
            assert retested["tasks"] == [{"id": "verification", "status": "succeeded"}]
            retest_evidence = core.workflow_evidence("retest-plan")
            assert retest_evidence["all_evidence_integrity_verified"] is True
            finding = retest_evidence["attempts"][0]["findings"][0]
            assert finding["verification_status"] == "still_vulnerable"
            assert _SQLiFixture.requests == 12

            _SQLiFixture.vulnerable = False
            _bound_plan(
                core, plan_id="inconclusive-retest-plan",
                capability_id=FindingVerificationProvider.RETEST,
                target=target,
                inputs={"source_job_id": verify_attempt["job_id"], "finding_seq": 0},
            )
            inconclusive = await core.run_workflow_plan(
                "inconclusive-retest-plan", max_tasks=1, max_concurrency=1,
            )
            assert inconclusive["tasks"] == [{"id": "verification", "status": "succeeded"}]
            result = core.workflow_evidence("inconclusive-retest-plan")["attempts"][0]["findings"][0]
            assert result["verification_status"] == "inconclusive"
            assert "inconclusive" in result["verification_reason"]
            assert _SQLiFixture.requests == 18

        asyncio.run(exercise())
    finally:
        server.shutdown()
        server.server_close()


def test_verifier_effect_is_correlated_before_evidence_persistence(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.vulnerable = True
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            source_job = await _seed_sealed_source(
                core, plan_id="crash-source-plan", target=target,
            )
            _bound_plan(
                core, plan_id="crash-verification-plan",
                capability_id=FindingVerificationProvider.VERIFY,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            original_append_finding = core.store.append_finding

            def fail_evidence_write(job_id, finding, seq):
                job = core.store.get(job_id)
                if job and job.get("tool") == "verify_sqli":
                    raise RuntimeError("simulated crash after probe")
                return original_append_finding(job_id, finding, seq)

            core.store.append_finding = fail_evidence_write
            result = await core.run_workflow_plan(
                "crash-verification-plan", max_tasks=1, max_concurrency=1,
            )
            assert result["tasks"] == [
                {"id": "verification", "status": "uncertain"},
            ]
            reconciliation = core.workflow_dispatch_reconciliation(
                "crash-verification-plan",
            )
            assert len(reconciliation) == 1
            attempt = reconciliation[0]
            assert attempt["provider_execution_id"] == attempt["attempt_id"]
            assert attempt["provider_job_identity_mismatch"] is False
            assert attempt["provider_job"]["job_id"] == attempt["attempt_id"]
            assert attempt["provider_job"]["status"] == "failed"
            assert attempt["provider_job"]["tool"] == "verify_sqli"
            assert _SQLiFixture.requests == 6

        asyncio.run(exercise())
    finally:
        server.shutdown()
        server.server_close()


def test_v2_reflected_xss_verify_and_retest_are_scheduler_owned(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.reflect_xss = True
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            source_job = await _seed_sealed_source(
                core, plan_id="xss-source-plan", target=target, kind="xss",
                request_context={"method": "GET", "url": target, "parameter": "q"},
            )
            _bound_plan(
                core, plan_id="xss-verification-plan",
                capability_id=FindingVerificationProvider.VERIFY_XSS,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            verified = await core.run_workflow_plan(
                "xss-verification-plan", max_tasks=1, max_concurrency=1,
            )
            assert verified["tasks"] == [{"id": "verification", "status": "succeeded"}]
            evidence = core.workflow_evidence("xss-verification-plan")
            assert evidence["all_evidence_integrity_verified"] is True, evidence
            attempt = evidence["attempts"][0]
            assert attempt["findings"][0]["verification_status"] == "verified"
            verified_job = attempt["job_id"]

            _SQLiFixture.reflect_xss = False
            _bound_plan(
                core, plan_id="xss-retest-plan",
                capability_id=FindingVerificationProvider.RETEST_XSS,
                target=target,
                inputs={"source_job_id": verified_job, "finding_seq": 0},
            )
            retested = await core.run_workflow_plan(
                "xss-retest-plan", max_tasks=1, max_concurrency=1,
            )
            assert retested["tasks"] == [{"id": "verification", "status": "succeeded"}]
            retest_evidence = core.workflow_evidence("xss-retest-plan")
            assert retest_evidence["all_evidence_integrity_verified"] is True
            assert retest_evidence["attempts"][0]["findings"][0]["verification_status"] == "inconclusive"

        asyncio.run(exercise())
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        thread.join(timeout=5)



def test_v2_verification_cancellation_drains_validator_and_fails_evidence(
    tmp_path, monkeypatch,
):
    from whaxon.core.validator import Validator

    started = threading.Event()
    release = threading.Event()
    followup_authorizations = []

    def blocked_validation(self, _finding, *, target_url):
        started.set()
        assert release.wait(timeout=5), "test did not release the in-flight validation"
        allowed = self.authorize_request(target_url)
        followup_authorizations.append(allowed)
        return "verified", "controlled test response"

    monkeypatch.setattr(Validator, "validate", blocked_validation)
    _SQLiFixture.requests = 0
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            source_job = await _seed_sealed_source(
                core, plan_id="cancel-drain-source-plan", target=target,
            )
            _bound_plan(
                core, plan_id="cancel-drain-plan",
                capability_id=FindingVerificationProvider.VERIFY,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )

            run = asyncio.create_task(core.run_workflow_plan(
                "cancel-drain-plan", max_tasks=1, max_concurrency=1,
            ))
            assert await asyncio.to_thread(started.wait, 5), "validator did not start"
            run.cancel()
            # Let scheduler cancellation reach the provider before allowing the
            # simulated in-flight request to complete and consider another.
            await asyncio.sleep(0.01)
            release.set()
            try:
                await run
            except asyncio.CancelledError:
                pass
            else:
                raise AssertionError("scheduler cancellation did not propagate")

            reconciliation = core.workflow_dispatch_reconciliation("cancel-drain-plan")
            assert len(reconciliation) == 1
            attempt = reconciliation[0]
            assert attempt["status"] == "uncertain"
            assert attempt["provider_job"]["status"] == "failed"
            assert followup_authorizations == [False]

        asyncio.run(exercise())
    finally:
        release.set()
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_v2_http_header_observation_verification_is_scheduler_owned(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            source_job = await _seed_sealed_source(
                core, plan_id="header-source-plan", target=target,
                kind="http_header_missing",
            )
            _bound_plan(
                core, plan_id="header-verification-plan",
                capability_id=FindingVerificationProvider.VERIFY_HTTP_OBSERVATION,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            result = await core.run_workflow_plan(
                "header-verification-plan", max_tasks=1, max_concurrency=1,
            )
            assert result["tasks"] == [{"id": "verification", "status": "succeeded"}]
            evidence = core.workflow_evidence("header-verification-plan")
            assert evidence["all_evidence_integrity_verified"] is True
            finding = evidence["attempts"][0]["findings"][0]
            assert finding["kind"] == "http_header_missing"
            assert finding["verification_status"] == "verified"
            assert "still lacks Content-Security-Policy" in finding["verification_reason"]
            assert _SQLiFixture.requests == 1

        asyncio.run(exercise())
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        thread.join(timeout=5)


def test_v2_cookie_observation_verification_is_scheduler_owned(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.send_cookie = True
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            source_job = await _seed_sealed_source(
                core, plan_id="cookie-source-plan", target=target,
                kind="cookie_insecure",
            )
            _bound_plan(
                core, plan_id="cookie-verification-plan",
                capability_id=FindingVerificationProvider.VERIFY_HTTP_OBSERVATION,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            result = await core.run_workflow_plan(
                "cookie-verification-plan", max_tasks=1, max_concurrency=1,
            )
            assert result["tasks"] == [{"id": "verification", "status": "succeeded"}]
            evidence = core.workflow_evidence("cookie-verification-plan")
            assert evidence["all_evidence_integrity_verified"] is True
            finding = evidence["attempts"][0]["findings"][0]
            assert finding["kind"] == "cookie_insecure"
            assert finding["verification_status"] == "verified"
            assert "still lacks httponly" in finding["verification_reason"]
            assert _SQLiFixture.requests == 1

        asyncio.run(exercise())
    finally:
        _SQLiFixture.send_cookie = False
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        thread.join(timeout=5)


def test_v2_http_observation_retest_reports_fixed_only_on_positive_correction(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.send_cookie = False
    _SQLiFixture.secure_cookie = False
    _SQLiFixture.send_csp = False
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/settings"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            for kind in ("http_header_missing", "cookie_insecure"):
                if kind == "cookie_insecure":
                    _SQLiFixture.send_cookie = True
                    _SQLiFixture.secure_cookie = False
                source_job = await _seed_sealed_source(
                    core, plan_id=f"{kind}-source-plan", target=target, kind=kind,
                )
                _bound_plan(
                    core, plan_id=f"{kind}-verify-plan",
                    capability_id=FindingVerificationProvider.VERIFY_HTTP_OBSERVATION,
                    target=target,
                    inputs={"source_job_id": source_job, "finding_seq": 0},
                )
                verified = await core.run_workflow_plan(
                    f"{kind}-verify-plan", max_tasks=1, max_concurrency=1,
                )
                assert verified["tasks"] == [{"id": "verification", "status": "succeeded"}]
                verified_evidence = core.workflow_evidence(f"{kind}-verify-plan")
                verified_finding = verified_evidence["attempts"][0]["findings"][0]
                assert verified_finding["verification_status"] == "verified"
                verified_job = verified_evidence["attempts"][0]["job_id"]

                if kind == "http_header_missing":
                    _SQLiFixture.send_csp = True
                else:
                    _SQLiFixture.send_cookie = True
                    _SQLiFixture.secure_cookie = True
                _bound_plan(
                    core, plan_id=f"{kind}-retest-plan",
                    capability_id=FindingVerificationProvider.RETEST_HTTP_OBSERVATION,
                    target=target,
                    inputs={"source_job_id": verified_job, "finding_seq": 0},
                )
                retested = await core.run_workflow_plan(
                    f"{kind}-retest-plan", max_tasks=1, max_concurrency=1,
                )
                assert retested["tasks"] == [{"id": "verification", "status": "succeeded"}]
                retest_finding = core.workflow_evidence(
                    f"{kind}-retest-plan",
                )["attempts"][0]["findings"][0]
                assert retest_finding["verification_status"] == "fixed", (kind, retest_finding)
                assert "now includes" in retest_finding["verification_reason"]

                if kind == "cookie_insecure":
                    _SQLiFixture.send_cookie = False
                    _bound_plan(
                        core, plan_id="cookie-absent-retest-plan",
                        capability_id=FindingVerificationProvider.RETEST_HTTP_OBSERVATION,
                        target=target,
                        inputs={"source_job_id": verified_job, "finding_seq": 0},
                    )
                    absent = await core.run_workflow_plan(
                        "cookie-absent-retest-plan", max_tasks=1, max_concurrency=1,
                    )
                    assert absent["tasks"] == [{"id": "verification", "status": "succeeded"}]
                    absent_finding = core.workflow_evidence(
                        "cookie-absent-retest-plan",
                    )["attempts"][0]["findings"][0]
                    assert absent_finding["verification_status"] == "inconclusive"

        asyncio.run(exercise())
    finally:
        _SQLiFixture.send_cookie = False
        _SQLiFixture.secure_cookie = False
        _SQLiFixture.send_csp = False
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        thread.join(timeout=5)


def test_v2_observation_verifier_strips_evidence_query_before_request(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.paths = []
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            source_job = await _seed_sealed_source(
                core, plan_id="changed-query-source-plan", target=target,
                kind="http_header_missing",
                finding_data={
                    "header": "Content-Security-Policy",
                    "url": f"http://127.0.0.1:{server.server_port}/search?id=2",
                },
            )
            _bound_plan(
                core, plan_id="changed-query-verification-plan",
                capability_id=FindingVerificationProvider.VERIFY_HTTP_OBSERVATION,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            result = await core.run_workflow_plan(
                "changed-query-verification-plan", max_tasks=1, max_concurrency=1,
            )
            assert result["tasks"] == [{"id": "verification", "status": "succeeded"}]
            evidence = core.workflow_evidence("changed-query-verification-plan")
            finding = evidence["attempts"][0]["findings"][0]
            assert finding["verification_status"] == "verified"
            assert _SQLiFixture.requests == 1
            assert _SQLiFixture.paths == ["/search"]

        asyncio.run(exercise())
    finally:
        server.shutdown()
        thread.join(timeout=2)
        server.server_close()
        thread.join(timeout=5)


def test_v2_retest_requires_a_prior_v2_verified_finding(tmp_path):
    async def exercise():
        core = Core(tmp_path / "data")
        await core.initialize(drain=False)
        target = "http://127.0.0.1:8000/search?id=1"
        source_job = await _seed_sealed_source(
            core, plan_id="source-plan", target=target,
        )
        _bound_plan(
            core, plan_id="retest-unverified-plan",
            capability_id=FindingVerificationProvider.RETEST,
            target=target,
            inputs={"source_job_id": source_job, "finding_seq": 0},
        )
        result = await core.run_workflow_plan(
            "retest-unverified-plan", max_tasks=1, max_concurrency=1,
        )
        assert result["tasks"] == [{"id": "verification", "status": "blocked"}]
        assert core.workflow_evidence("retest-unverified-plan")["all_evidence_recorded"] is False

        observation_source = await _seed_sealed_source(
            core, plan_id="observation-unverified-source-plan",
            target=target, kind="http_header_missing",
        )
        _bound_plan(
            core, plan_id="observation-unverified-retest-plan",
            capability_id=FindingVerificationProvider.RETEST_HTTP_OBSERVATION,
            target=target,
            inputs={"source_job_id": observation_source, "finding_seq": 0},
        )
        observation_retest = await core.run_workflow_plan(
            "observation-unverified-retest-plan", max_tasks=1, max_concurrency=1,
        )
        assert observation_retest["tasks"] == [
            {"id": "verification", "status": "blocked"},
        ]

    asyncio.run(exercise())


def test_v2_verify_rejects_mutated_source_after_evidence_seal(tmp_path):
    async def exercise():
        core = Core(tmp_path / "data")
        await core.initialize(drain=False)
        target = "http://127.0.0.1:8000/search?id=1"
        source_job = await _seed_sealed_source(
            core, plan_id="source-plan", target=target,
        )
        assert core.store.has_valid_workflow_evidence_seal(source_job) is True
        core.store.update_verification(
            source_job, 0, "verified", by="operator", reason="post-seal mutation",
        )
        assert core.store.has_valid_workflow_evidence_seal(source_job) is False
        _bound_plan(
            core, plan_id="mutated-source-verification-plan",
            capability_id=FindingVerificationProvider.VERIFY,
            target=target,
            inputs={"source_job_id": source_job, "finding_seq": 0},
        )
        result = await core.run_workflow_plan(
            "mutated-source-verification-plan", max_tasks=1, max_concurrency=1,
        )
        assert result["tasks"] == [{"id": "verification", "status": "blocked"}]
        assert core.workflow_evidence(
            "mutated-source-verification-plan",
        )["all_evidence_recorded"] is False

    asyncio.run(exercise())


def test_v2_verification_rejects_hostname_targets_before_dispatch(tmp_path):
    async def exercise():
        core = Core(tmp_path / "data")
        await core.initialize(drain=False)
        target = "http://localhost:8000/search?id=1"
        source_job = await _seed_sealed_source(
            core, plan_id="source-plan", target=target,
        )
        task = _bound_plan(
            core, plan_id="hostname-verification-plan",
            capability_id=FindingVerificationProvider.VERIFY,
            target=target,
            inputs={"source_job_id": source_job, "finding_seq": 0},
        )
        try:
            core.providers.resolve_task(task)
        except ValueError as exc:
            assert "IP literal" in str(exc)
        else:
            raise AssertionError("hostname verification target must be rejected")

    asyncio.run(exercise())


def test_v2_verifier_readiness_and_inventory_are_documented(tmp_path):
    async def exercise():
        core = Core(tmp_path / "data")
        await core.initialize(drain=False)
        rows = [
            row for row in core.providers.inventory()
            if row.get("provider_id") == FindingVerificationProvider.PROVIDER_ID
        ]
        assert {row["capability_id"] for row in rows} == {
            FindingVerificationProvider.VERIFY,
            FindingVerificationProvider.RETEST,
            FindingVerificationProvider.VERIFY_XSS,
            FindingVerificationProvider.RETEST_XSS,
            FindingVerificationProvider.VERIFY_HTTP_OBSERVATION,
            FindingVerificationProvider.RETEST_HTTP_OBSERVATION,
        }
        assert all(
            row["provider_version"] == FindingVerificationProvider.PROVIDER_VERSION
            and row["readiness"] == "registered"
            and row["smoke_tested"] is False
            and row["lab_validated"] is False
            and row["end_to_end_verified"] is False
            for row in rows
        )
        inventory = (
            Path(__file__).resolve().parents[1]
            / "docs"
            / "ENGINE_V2_LEGACY_EXECUTION_INVENTORY.md"
        ).read_text(encoding="utf-8")
        section = inventory[
            inventory.index("The separately bound HTTP verifier"):
            inventory.index("The built-in adapter registry")
        ]
        assert all(capability in section for capability in (
            FindingVerificationProvider.VERIFY,
            FindingVerificationProvider.RETEST,
            FindingVerificationProvider.VERIFY_XSS,
            FindingVerificationProvider.RETEST_XSS,
            FindingVerificationProvider.VERIFY_HTTP_OBSERVATION,
            FindingVerificationProvider.RETEST_HTTP_OBSERVATION,
        ))

    asyncio.run(exercise())


def test_v2_verification_authorizes_contextless_and_rejects_changed_path(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.vulnerable = True
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            source_job = await _seed_sealed_source(
                core, plan_id="contextless-source-plan", target=target,
                request_context={},
            )
            _bound_plan(
                core, plan_id="contextless-verification-plan",
                capability_id=FindingVerificationProvider.VERIFY,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            verified = await core.run_workflow_plan(
                "contextless-verification-plan", max_tasks=1, max_concurrency=1,
            )
            assert verified["tasks"] == [{"id": "verification", "status": "succeeded"}]
            evidence = core.workflow_evidence("contextless-verification-plan")
            assert evidence["all_evidence_integrity_verified"] is True
            assert evidence["attempts"][0]["findings"][0]["verification_status"] == "verified"
            assert _SQLiFixture.requests == 6

            other_path_source = await _seed_sealed_source(
                core, plan_id="changed-path-source-plan", target=target,
                request_context={
                    "method": "GET", "url": target.replace("/search", "/other"),
                    "parameter": "id",
                },
            )
            _bound_plan(
                core, plan_id="changed-path-verification-plan",
                capability_id=FindingVerificationProvider.VERIFY,
                target=target,
                inputs={"source_job_id": other_path_source, "finding_seq": 0},
            )
            result = await core.run_workflow_plan(
                "changed-path-verification-plan", max_tasks=1, max_concurrency=1,
            )
            assert result["tasks"] == [{"id": "verification", "status": "succeeded"}]
            changed = core.workflow_evidence("changed-path-verification-plan")
            assert changed["all_evidence_integrity_verified"] is True
            finding = changed["attempts"][0]["findings"][0]
            assert finding["verification_status"] == "candidate"
            assert "scope authorization denied" in finding["verification_reason"]
            assert _SQLiFixture.requests == 6

        asyncio.run(exercise())
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_v2_validation_rechecks_scope_before_each_probe(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.vulnerable = True
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            _SQLiFixture.scope_path = tmp_path / "data" / "scope.json"
            _SQLiFixture.revoke_after = 3
            scope_decisions = []
            original_check = core.scope.check_for_execution

            def track_scope_check(url):
                result = original_check(url)
                scope_decisions.append((url, result.allowed, tuple(core.scope._in)))
                return result

            core.scope.check_for_execution = track_scope_check
            provider = core.providers._routes[FindingVerificationProvider.VERIFY]
            assert provider.scope is core.scope
            assert core.scope.path == _SQLiFixture.scope_path
            source_job = await _seed_sealed_source(
                core, plan_id="source-plan", target=target,
            )
            _bound_plan(
                core, plan_id="scope-revocation-plan",
                capability_id=FindingVerificationProvider.VERIFY,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            result = await core.run_workflow_plan(
                "scope-revocation-plan", max_tasks=1, max_concurrency=1,
            )
            assert result["tasks"] == [{"id": "verification", "status": "succeeded"}]
            evidence = core.workflow_evidence("scope-revocation-plan")
            assert evidence["all_evidence_integrity_verified"] is True
            finding = evidence["attempts"][0]["findings"][0]
            assert finding["verification_status"] == "candidate", (
                _SQLiFixture.requests, str(core.scope.path),
                len(scope_decisions), scope_decisions[-1:] if scope_decisions else [],
            )
            assert "scope authorization denied" in finding["verification_reason"]
            assert _SQLiFixture.requests == 3

        asyncio.run(exercise())
    finally:
        _SQLiFixture.scope_path = None
        _SQLiFixture.revoke_after = None
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_v2_verification_rechecks_exact_approval_before_each_request(
    tmp_path, monkeypatch,
):
    _SQLiFixture.requests = 0
    _SQLiFixture.vulnerable = True
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            source_job = await _seed_sealed_source(
                core, plan_id="approval-source-plan", target=target,
            )
            _bound_plan(
                core, plan_id="approval-revocation-plan",
                capability_id=FindingVerificationProvider.VERIFY,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            approval_checks = []

            def approval_is_current(plan_id, task_key):
                approval_checks.append((plan_id, task_key))
                # Scheduler dispatch checks are allowed; revoke before the
                # verifier's second HTTP request.
                return len(approval_checks) < 4

            monkeypatch.setattr(
                core.store, "has_valid_workflow_approval", approval_is_current,
            )
            result = await core.run_workflow_plan(
                "approval-revocation-plan", max_tasks=1, max_concurrency=1,
            )
            assert result["tasks"] == [{"id": "verification", "status": "succeeded"}]
            evidence = core.workflow_evidence("approval-revocation-plan")
            finding = evidence["attempts"][0]["findings"][0]
            assert finding["verification_status"] == "candidate"
            assert "scope authorization denied" in finding["verification_reason"]
            assert len(approval_checks) == 4
            assert all(item == ("approval-revocation-plan", "verification")
                       for item in approval_checks)
            assert _SQLiFixture.requests == 1

        asyncio.run(exercise())
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)


def test_v2_verification_cancellation_blocks_the_next_probe(tmp_path):
    _SQLiFixture.requests = 0
    _SQLiFixture.vulnerable = True
    _SQLiFixture.scope_path = None
    _SQLiFixture.revoke_after = None
    _SQLiFixture.after_response = None
    server = HTTPServer(("127.0.0.1", 0), _SQLiFixture)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    target = f"http://127.0.0.1:{server.server_port}/search?id=1"
    try:
        async def exercise():
            core = Core(tmp_path / "data")
            await core.initialize(drain=False)
            source_job = await _seed_sealed_source(
                core, plan_id="cancel-source-plan", target=target,
            )
            _bound_plan(
                core, plan_id="cancel-in-flight-plan",
                capability_id=FindingVerificationProvider.VERIFY,
                target=target,
                inputs={"source_job_id": source_job, "finding_seq": 0},
            )
            _SQLiFixture.after_response = lambda: core.store.request_workflow_cancellation(
                "cancel-in-flight-plan",
            )

            result = await core.run_workflow_plan(
                "cancel-in-flight-plan", max_tasks=1, max_concurrency=1,
            )

            assert _SQLiFixture.requests == 1
            assert core.store.get_workflow_progress(
                "cancel-in-flight-plan",
            )["cancellation_requested"] is True
            assert result["tasks"][0]["status"] in {"uncertain", "cancelled"}

        asyncio.run(exercise())
    finally:
        _SQLiFixture.after_response = None
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
