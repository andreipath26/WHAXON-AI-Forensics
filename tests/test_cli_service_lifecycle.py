"""Mocked coverage for the local whaxon up/down service commands."""
from __future__ import annotations

from contextlib import nullcontext
from types import SimpleNamespace

import pytest

from whaxon.interfaces.cli import down_cmd, up_cmd


def _data_dir(tmp_path):
    data = tmp_path / "data"
    data.mkdir()
    (data / "whaxon.env").write_text("", encoding="utf-8")
    return data


def test_up_foreground_delegates_to_web_service_without_host_effects(
    tmp_path, monkeypatch,
):
    data = _data_dir(tmp_path)
    calls = []
    from whaxon.interfaces.web import serve

    monkeypatch.setattr(serve, "main", lambda args: calls.append(args))
    monkeypatch.setattr(
        up_cmd.subprocess,
        "run",
        lambda *a, **kw: pytest.fail("unexpected subprocess"),
    )
    monkeypatch.setattr(
        up_cmd.subprocess,
        "Popen",
        lambda *a, **kw: pytest.fail("unexpected process"),
    )

    up_cmd.main(["--no-docker", "--no-msfrpcd", "--foreground", "--data", str(data)])

    assert calls == [[]]


def test_up_daemon_uses_local_service_command_and_waits_for_loopback(
    tmp_path, monkeypatch,
):
    data = _data_dir(tmp_path)
    commands = []
    sockets = []

    def run(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0, stdout="", stderr="")

    def connect(address, timeout):
        sockets.append((address, timeout))
        return nullcontext()

    import shutil

    monkeypatch.setattr(shutil, "which", lambda _name: "/opt/whaxon/bin/whaxon")
    monkeypatch.setattr(up_cmd.subprocess, "run", run)
    monkeypatch.setattr(up_cmd.socket, "create_connection", connect)

    up_cmd.main(["--no-docker", "--no-msfrpcd", "--data", str(data)])

    assert commands == [[
        "/opt/whaxon/bin/whaxon",
        "serve",
        "--daemon",
        "--log",
        str(data / "whaxon.log"),
    ]]
    assert sockets and all(address[0] == "127.0.0.1" for address, _ in sockets)


def test_up_starts_msfrpcd_only_after_loopback_probe_fails(
    tmp_path, monkeypatch,
):
    data = _data_dir(tmp_path)
    monkeypatch.setenv("WHAXON_MSF_USER", "test-user")
    monkeypatch.setenv("WHAXON_MSF_PASS", "test-password")
    monkeypatch.setenv("WHAXON_MSF_SSL", "true")
    probes = iter([False, True])
    started = []
    from whaxon.interfaces.web import serve

    monkeypatch.setattr(up_cmd, "_wait_tcp", lambda *a, **kw: next(probes))
    monkeypatch.setattr(
        up_cmd.subprocess,
        "Popen",
        lambda command, **kw: started.append(command),
    )
    monkeypatch.setattr(serve, "main", lambda _args: None)

    up_cmd.main(["--no-docker", "--foreground", "--data", str(data)])

    assert started == [[
        "sudo", "msfrpcd", "-P", "test-password", "-U", "test-user",
        "-a", "127.0.0.1", "-p", "55553", "-S",
    ]]


def test_down_keep_flags_only_stop_whaxon_processes(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    data = tmp_path / "data"
    data.mkdir()
    (data / "whaxon.pid").write_text("12345\n", encoding="utf-8")
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(down_cmd.subprocess, "run", run)

    down_cmd.main(["--keep-docker", "--keep-msfrpcd"])

    assert commands == [["kill", "12345"], ["pkill", "-f", "whaxon serve"]]


def test_down_default_stops_only_named_local_services(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    commands = []

    def run(command, **kwargs):
        commands.append(command)
        return SimpleNamespace(returncode=0)

    monkeypatch.setattr(down_cmd.subprocess, "run", run)

    down_cmd.main([])

    assert commands == [
        ["pkill", "-f", "whaxon serve"],
        ["pgrep", "-f", "msfrpcd"],
        ["sudo", "pkill", "-f", "msfrpcd"],
        ["docker", "rm", "-f", "msf-target"],
        ["docker", "network", "rm", "whaxon-lab"],
    ]
