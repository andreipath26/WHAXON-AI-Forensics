"""E3 catalog-provider crash recovery through the real dig adapter path.

The fake executable records one invocation and returns fixed DNS output. The
test uses the normal Core provider, ToolRunner, parser, SQLite persistence and
recovery path without contacting an external DNS server.
"""
from __future__ import annotations

import asyncio
import os
from pathlib import Path
import subprocess
import sys
import time

import pytest

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


_CATALOG_WORKER = """
import asyncio
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path.cwd() / "src"))
from whaxon.core import Core

data_dir = Path(sys.argv[1])
sealed_marker = Path(sys.argv[2])

async def main():
    core = Core(data_dir)
    await core.initialize(drain=False)
    seal_result = core.store.seal_engine_v2_provider_result

    def seal_then_pause(job_id):
        if not seal_result(job_id):
            raise RuntimeError("provider result did not seal")
        pending_marker = sealed_marker.with_name(sealed_marker.name + ".tmp")
        pending_marker.write_text(job_id, encoding="utf-8")
        pending_marker.replace(sealed_marker)
        while True:
            time.sleep(0.05)

    core.store.seal_engine_v2_provider_result = seal_then_pause
    await core.run_workflow_plan(
        "dig-recovery-plan",
        authorize=lambda _task: True,
        max_tasks=1,
        max_attempts=1,
        max_concurrency=1,
    )

asyncio.run(main())
"""


def _write_fake_dig(directory: Path) -> None:
    directory.mkdir()
    executable = directory / "dig"
    executable.write_text(
        "#!/bin/sh\n"
        "printf 'invoked\\n' >> \"$DIG_INVOCATIONS\"\n"
        "printf '203.0.113.10\\n'\n",
        encoding="utf-8",
    )
    executable.chmod(0o755)


def test_catalog_dig_crash_after_seal_recovers_without_replay(
    tmp_path, monkeypatch,
):
    fake_bin = tmp_path / "bin"
    _write_fake_dig(fake_bin)
    invocations = tmp_path / "dig-invocations"
    monkeypatch.setenv(
        "PATH", str(fake_bin) + os.pathsep + os.environ.get("PATH", ""),
    )
    monkeypatch.setenv("DIG_INVOCATIONS", str(invocations))
    (tmp_path / "scope.json").write_text(
        '{"engagement":"fixture","enabled":true,'
        '"in_scope":["recovery.fixture"],"out_of_scope":[],"notes":"test"}',
        encoding="utf-8",
    )

    core = Core(tmp_path)
    core.create_mission("dig-recovery", "recover one local fake DNS observation")
    manifest = core.providers.manifest_for("tool.dig")
    plan = WorkflowPlan(
        "dig-recovery",
        (WorkflowTask(
            "lookup",
            "tool.dig",
            "recovery.fixture",
            permissions=manifest.permissions,
            impact=manifest.impact,
            timeout_s=10.0,
        ),),
        metadata={"provider_bindings": {"lookup": {
            "provider_id": manifest.provider_id,
            "provider_version": manifest.provider_version,
            "manifest_fingerprint": manifest.fingerprint,
        }}},
    )
    core.save_workflow_plan("dig-recovery-plan", plan)

    sealed_marker = tmp_path / "provider-result-sealed"
    process = subprocess.Popen(
        [
            sys.executable, "-c", _CATALOG_WORKER,
            str(tmp_path), str(sealed_marker),
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
        text=True,
        env=os.environ.copy(),
    )
    try:
        deadline = time.monotonic() + 20
        while (
            not sealed_marker.exists()
            and process.poll() is None
            and time.monotonic() < deadline
        ):
            time.sleep(0.02)
        assert sealed_marker.exists(), (
            "catalog provider did not persist and seal its result before timeout"
        )
        attempt_id = sealed_marker.read_text(encoding="utf-8")
        assert len(attempt_id) == 32
        assert invocations.read_text(encoding="utf-8").splitlines() == ["invoked"]
    finally:
        if process.poll() is None:
            process.kill()
        _, stderr = process.communicate(timeout=10)
    assert process.returncode is not None, stderr

    restarted = Core(tmp_path)
    attempts = restarted.store.list_workflow_attempts("dig-recovery-plan")
    assert len(attempts) == 1
    assert attempts[0]["id"] == attempt_id
    conn = restarted.store._conn()
    try:
        conn.execute(
            "UPDATE task_attempts SET heartbeat_at=? WHERE id=?",
            (time.time() - 3600, attempt_id),
        )
    finally:
        conn.close()

    asyncio.run(restarted.initialize(drain=False))
    assert restarted.store.get_workflow_attempt_status(attempt_id) == "uncertain"

    recovered = restarted.recover_workflow_attempt_from_provider_job(
        "dig-recovery-plan", attempt_id,
    )
    assert recovered["task_status"] == "succeeded"
    assert recovered["provider_execution_id"] == attempt_id
    assert recovered["automatic_replay"] is False

    evidence = restarted.workflow_evidence("dig-recovery-plan")
    recovered_attempt = evidence["attempts"][0]
    assert recovered_attempt["integrity_status"] == "verified"
    assert any(
        finding["kind"] == "a_record"
        and finding["data"] == {"ip": "203.0.113.10"}
        for finding in recovered_attempt["findings"]
    )

    with pytest.raises(ValueError, match="only uncertain"):
        restarted.recover_workflow_attempt_from_provider_job(
            "dig-recovery-plan", attempt_id,
        )

    dispatched = []

    async def forbidden_replay(task):
        dispatched.append(task.id)
        raise AssertionError("recovered provider effects must never replay")

    result = asyncio.run(restarted.run_workflow_plan(
        "dig-recovery-plan",
        authorize=lambda _task: True,
        dispatch=forbidden_replay,
        max_tasks=1,
        max_attempts=1,
        max_concurrency=1,
    ))
    assert result["attempts"] == 0
    assert dispatched == []
    assert invocations.read_text(encoding="utf-8").splitlines() == ["invoked"]
