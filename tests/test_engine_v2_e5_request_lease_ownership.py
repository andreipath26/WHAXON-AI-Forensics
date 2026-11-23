"""Durable run-request lease loss must stop its active scheduler immediately.

These fixtures never invoke an external provider or target; they exercise the
shared Core queue-to-scheduler authority boundary with a suspended DAG.
"""
import asyncio

import pytest

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask


@pytest.mark.parametrize("heartbeat_fails_with_exception", (False, True))
def test_lost_run_request_lease_cancels_active_workflow_and_never_succeeds(
    tmp_path, monkeypatch, heartbeat_fails_with_exception,
):
    core = Core(tmp_path)
    core.create_mission("mission", "controlled local lease-loss fixture")
    core.save_workflow_plan("plan", WorkflowPlan("mission", (
        WorkflowTask("one", "fixture", "192.0.2.10"),
    )))
    request = core.enqueue_workflow_run("plan")
    started = asyncio.Event()
    stopped = asyncio.Event()

    async def hung_workflow(*_args, **_kwargs):
        started.set()
        try:
            await asyncio.Event().wait()
        finally:
            stopped.set()

    monkeypatch.setattr(core, "run_workflow_plan", hung_workflow)

    def lost_heartbeat(*_args):
        if heartbeat_fails_with_exception:
            raise OSError("simulated loss of durable heartbeat storage")
        return False

    monkeypatch.setattr(core.workflow_requests, "heartbeat", lost_heartbeat)

    async def scenario():
        drained = await asyncio.wait_for(
            core.drain_workflow_run_requests(initialized=True, max_runs=1),
            timeout=9,
        )
        assert drained == 1
        assert started.is_set()
        assert stopped.is_set()

    asyncio.run(scenario())
    record = core.workflow_run_request(request["id"])
    assert record["status"] == "uncertain"
    assert "lease lost" in record["error"]
    assert core.workflow_requests.claim("other-worker") is None
