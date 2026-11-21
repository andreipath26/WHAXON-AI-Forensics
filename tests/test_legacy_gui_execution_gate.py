"""The dormant Qt compatibility module cannot dispatch by default."""
from __future__ import annotations

import ast
import asyncio
from pathlib import Path

from whaxon.interfaces.legacy_execution import legacy_gui_execution_enabled


def test_legacy_gui_execution_is_retired_even_with_stale_environment_flag(monkeypatch):
    for value in ("1", "true", "YES", " true "):
        monkeypatch.setenv("WHAXON_LEGACY_GUI_EXECUTION_ENABLED", value)
        assert legacy_gui_execution_enabled() is False

    for value in ("", "false", "on"):
        monkeypatch.setenv("WHAXON_LEGACY_GUI_EXECUTION_ENABLED", value)
        assert legacy_gui_execution_enabled() is False


def test_legacy_qt_dispatch_checks_gate_before_toolrunner_call():
    source = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "whaxon"
        / "interfaces"
        / "gui"
        / "main_window.py"
    )
    module = ast.parse(source.read_text(encoding="utf-8"))
    run_tool = next(
        node for node in ast.walk(module)
        if isinstance(node, ast.AsyncFunctionDef) and node.name == "_run_tool"
    )
    calls = [
        node for node in ast.walk(run_tool)
        if isinstance(node, ast.Call)
    ]
    gate_lines = [
        node.lineno for node in calls
        if isinstance(node.func, ast.Name)
        and node.func.id == "legacy_gui_execution_enabled"
    ]
    dispatch_lines = [
        node.lineno for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "run_tool"
    ]
    assert gate_lines and dispatch_lines
    assert min(gate_lines) < min(dispatch_lines)


def test_legacy_qt_run_action_blocks_before_queuing_task():
    source = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "whaxon"
        / "interfaces"
        / "gui"
        / "main_window.py"
    )
    module = ast.parse(source.read_text(encoding="utf-8"))
    run_selected = next(
        node for node in ast.walk(module)
        if isinstance(node, ast.FunctionDef) and node.name == "_run_selected"
    )
    calls = [node for node in ast.walk(run_selected) if isinstance(node, ast.Call)]
    gate_lines = [
        node.lineno for node in calls
        if isinstance(node.func, ast.Name)
        and node.func.id == "legacy_gui_execution_enabled"
    ]
    task_lines = [
        node.lineno for node in calls
        if isinstance(node.func, ast.Attribute)
        and node.func.attr == "create_task"
    ]
    assert gate_lines and task_lines
    assert min(gate_lines) < min(task_lines)


def _cancel_harness_type():
    source = (
        Path(__file__).resolve().parents[1]
        / "src"
        / "whaxon"
        / "interfaces"
        / "gui"
        / "main_window.py"
    )
    module = ast.parse(source.read_text(encoding="utf-8"))
    main_window = next(
        node for node in ast.walk(module)
        if isinstance(node, ast.ClassDef) and node.name == "MainWindow"
    )
    method_names = {"_allow_direct_cancel", "_cancel_job", "_cancel_job_async"}
    methods = [
        node for node in main_window.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))
        and node.name in method_names
    ]
    assert {node.name for node in methods} == method_names
    harness = ast.ClassDef(
        name="CancelHarness", bases=[], keywords=[], body=methods, decorator_list=[],
    )
    executable = ast.fix_missing_locations(
        ast.Module(body=[harness], type_ignores=[]),
    )
    namespace = {"asyncio": asyncio}
    exec(compile(executable, str(source), "exec"), namespace)
    return namespace["CancelHarness"]


def _cancel_window_harness(is_v2_job, cancelled, statuses):
    from types import SimpleNamespace

    window = _cancel_harness_type()()

    async def raw_cancel(job_id):
        cancelled.append(job_id)

    window.core = SimpleNamespace(
        store=SimpleNamespace(is_engine_v2_execution_job=is_v2_job),
        runner=SimpleNamespace(cancel=raw_cancel),
    )
    window.current_job_id = "provider-job"
    window.statusBar = lambda: SimpleNamespace(showMessage=statuses.append)
    return window


def test_qt_cancel_button_fails_closed_for_v2_and_ownership_errors(monkeypatch):
    def ownership_error(_job_id):
        raise RuntimeError("store unavailable")

    for ownership, expected in (
        (lambda _job_id: True, "Engine V2 work"),
        (ownership_error, "ownership could not be checked"),
    ):
        cancelled = []
        statuses = []
        scheduled = []
        window = _cancel_window_harness(ownership, cancelled, statuses)
        monkeypatch.setattr(
            asyncio, "create_task",
            lambda coroutine: scheduled.append(coroutine),
        )

        window._cancel_job()

        assert scheduled == []
        assert cancelled == []
        assert expected in statuses[-1]


def test_qt_cancel_async_dispatch_rechecks_v2_ownership(monkeypatch):
    ownership = iter((False, True))
    cancelled = []
    statuses = []
    scheduled = []
    window = _cancel_window_harness(
        lambda _job_id: next(ownership), cancelled, statuses,
    )
    monkeypatch.setattr(
        asyncio, "create_task",
        lambda coroutine: scheduled.append(coroutine),
    )

    window._cancel_job()
    assert len(scheduled) == 1
    asyncio.run(scheduled.pop())

    assert cancelled == []
    assert "Engine V2 work" in statuses[-1]



def test_qt_cancel_dispatch_still_allows_legacy_job(monkeypatch):
    cancelled = []
    statuses = []
    scheduled = []
    window = _cancel_window_harness(
        lambda _job_id: False, cancelled, statuses,
    )
    monkeypatch.setattr(
        asyncio, "create_task",
        lambda coroutine: scheduled.append(coroutine),
    )

    window._cancel_job()
    assert len(scheduled) == 1
    asyncio.run(scheduled.pop())

    assert cancelled == ["provider-job"]
