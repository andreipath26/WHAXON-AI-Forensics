"""Continuous Engine V2 workflow-request worker regression coverage."""
from __future__ import annotations

import asyncio
import threading
from concurrent.futures import ThreadPoolExecutor

import pytest

from whaxon.core import Core
from whaxon.core.workflow import WorkflowPlan, WorkflowTask
from whaxon.interfaces.cli.workflow_cmd import _parser


def _core(tmp_path):
    core = Core(tmp_path)
    core.create_mission("m", "worker lifecycle")
    core.save_workflow_plan(
        "p", WorkflowPlan("m", (
            WorkflowTask("scan", "unsupported.fixture", "192.0.2.10"),
        )),
    )
    return core


def test_headless_worker_polls_for_later_arrivals(tmp_path):
    worker = _core(tmp_path)
    submitter = Core(tmp_path)
    stop = threading.Event()

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(lambda: asyncio.run(
            worker.serve_workflow_run_requests(
                stop, poll_interval_s=0.05, max_runs_per_batch=1,
            ),
        ))
        # The service starts without work; a distinct Core can later enqueue.
        request = submitter.enqueue_workflow_run("p")
        import time

        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            if submitter.workflow_run_request(request["id"])["status"] == "completed":
                break
            time.sleep(0.025)
        stop.set()
        processed = future.result(timeout=10)

    assert processed == 1
    assert submitter.workflow_run_request(request["id"])["status"] == "completed"
    assert submitter.workflow_progress("p")["counts"]["blocked"] == 1


def test_headless_worker_stops_before_claiming_when_signalled(tmp_path):
    core = _core(tmp_path)
    request = core.enqueue_workflow_run("p")
    stop = threading.Event()
    stop.set()
    with ThreadPoolExecutor(max_workers=1) as pool:
        assert pool.submit(lambda: asyncio.run(
            core.serve_workflow_run_requests(stop, poll_interval_s=0.05),
        )).result(timeout=5) == 0
    assert core.workflow_run_request(request["id"])["status"] == "queued"


@pytest.mark.parametrize("interval", [0, -1, float("nan"), float("inf"), True, 3601])
def test_headless_worker_rejects_invalid_poll_interval(tmp_path, interval):
    core = _core(tmp_path)
    with ThreadPoolExecutor(max_workers=1) as pool:
        with pytest.raises(ValueError, match="poll interval"):
            pool.submit(lambda: asyncio.run(
                core.serve_workflow_run_requests(
                    threading.Event(), poll_interval_s=interval,
                ),
            )).result(timeout=5)


def test_headless_worker_cli_argument_contract():
    opts = _parser().parse_args([
        "plan", "serve-requests", "--poll-interval", "0.5",
        "--max-runs-per-batch", "3",
    ])
    assert opts.command == "plan"
    assert opts.plan_command == "serve-requests"
    assert opts.poll_interval == 0.5
    assert opts.max_runs_per_batch == 3
