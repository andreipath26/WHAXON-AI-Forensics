"""Core initialization never auto-dispatches legacy JobStore rows.

A long-lived process uses the durable Engine V2 request worker. Pending legacy
rows remain visible for explicit inspection and cannot start because an old
environment opt-in is present.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from whaxon.core import Core


def _core(tmp_path: Path) -> Core:
    data = tmp_path / "data"
    data.mkdir()
    (data / "tools.json").write_text(
        '{"tools":[{"id":"echo","name":"Echo","category":"test",'
        '"binary":"/bin/echo","args":"{target}"}]}'
    )
    return Core(data_dir=data)


def test_initialize_drain_false_leaves_job_pending(tmp_path: Path) -> None:
    core = _core(tmp_path)
    core.store.create_pending("j1", "echo", "127.0.0.1")
    asyncio.run(core.initialize(drain=False))
    assert core.store.list_pending() == [
        {"id": "j1", "tool": "echo", "target": "127.0.0.1"}
    ]


def test_one_shot_initialize_never_drains_even_with_legacy_opt_in(
    tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.setenv("WHAXON_LEGACY_QUEUE_DRAIN_ENABLED", "true")
    core = _core(tmp_path)
    core.store.create_pending("j1", "echo", "127.0.0.1")
    asyncio.run(core.initialize(drain=False))
    assert core.store.list_pending() == [
        {"id": "j1", "tool": "echo", "target": "127.0.0.1"}
    ]


def test_initialize_drain_true_leaves_legacy_job_pending_by_default(
    tmp_path: Path, monkeypatch,
) -> None:
    monkeypatch.delenv("WHAXON_LEGACY_QUEUE_DRAIN_ENABLED", raising=False)
    core = _core(tmp_path)
    core.store.create_pending("j1", "echo", "127.0.0.1")
    asyncio.run(core.initialize(drain=True))
    assert core.store.list_pending() == [
        {"id": "j1", "tool": "echo", "target": "127.0.0.1"}
    ]


def test_initialize_drain_true_ignores_stale_legacy_opt_in(
    tmp_path: Path, monkeypatch,
) -> None:
    from whaxon.core import worker

    monkeypatch.setenv("WHAXON_LEGACY_QUEUE_DRAIN_ENABLED", "true")
    core = _core(tmp_path)
    core.store.create_pending("j1", "echo", "127.0.0.1")
    calls = []

    async def forbidden_drain(*args, **kwargs):
        calls.append((args, kwargs))

    monkeypatch.setattr(worker, "drain_async", forbidden_drain)
    asyncio.run(core.initialize(drain=True))

    assert calls == []
    assert core.store.list_pending() == [
        {"id": "j1", "tool": "echo", "target": "127.0.0.1"}
    ]


def test_initialize_fails_closed_when_v2_recovery_fails(tmp_path: Path, monkeypatch):
    monkeypatch.delenv("WHAXON_LEGACY_QUEUE_DRAIN_ENABLED", raising=False)
    core = _core(tmp_path)

    def fail_recovery(*args, **kwargs):
        raise OSError("private recovery details")

    monkeypatch.setattr(core.store, "reconcile_workflow_attempts", fail_recovery)
    try:
        asyncio.run(core.initialize(drain=False))
    except RuntimeError as exc:
        assert str(exc) == "workflow recovery failed; execution is not ready"
        assert isinstance(exc.__cause__, OSError)
    else:
        raise AssertionError("initialize must fail closed when workflow recovery fails")
