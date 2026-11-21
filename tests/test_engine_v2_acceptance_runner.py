from __future__ import annotations

import hashlib
import json
import subprocess
import sys
import tarfile
from pathlib import Path

import pytest

from scripts.engine_v2_acceptance import (
    _artifact_check,
    _source_revision,
    run_engine_v2_acceptance,
)


def _repo(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    root.mkdir()
    (root / "pyproject.toml").write_text("[project]\nname='fixture'\n")
    return root


def test_revision_requires_a_hex_sha_and_never_guesses_git_state(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WHAXON_SOURCE_REVISION", raising=False)
    monkeypatch.delenv("GITHUB_SHA", raising=False)
    assert _source_revision(None) == "unknown"
    assert _source_revision("ABCDEF1") == "abcdef1"
    with pytest.raises(ValueError, match="hexadecimal"):
        _source_revision("branch-name")


def test_runner_records_all_results_and_never_self_approves_deployment(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    calls = 0

    def fake_runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        nonlocal calls
        calls += 1
        kwargs["stdout"].write(f"ran {command[0]}\n".encode())  # type: ignore[union-attr]
        return subprocess.CompletedProcess(command, 1 if calls == 1 else 0)

    output = tmp_path / "evidence"
    report = run_engine_v2_acceptance(
        root, output, source_revision="abcdef1",
        checks=[
            {"id": "one", "title": "first", "command": [sys.executable, "-c", "pass"], "timeout_seconds": 4},
            {"id": "two", "title": "second", "command": [sys.executable, "-c", "pass"], "timeout_seconds": 4},
        ],
        runner=fake_runner,
    )
    assert calls == 2
    assert [check["status"] for check in report["checks"]] == ["failed", "passed"]
    assert report["internal_status"] == "failed"
    assert report["deployment_decision"] == "HOLD"
    assert all(gate["status"] == "pending" for gate in report["external_gates"])
    for check in report["checks"]:
        log_path = output / check["log"]
        assert hashlib.sha256(log_path.read_bytes()).hexdigest() == check["log_sha256"]
    digest, filename = (output / "report.sha256").read_text().split()
    assert filename == "report.json"
    assert hashlib.sha256((output / filename).read_bytes()).hexdigest() == digest
    assert json.loads((output / "report.json").read_text())["deployment_decision"] == "HOLD"


def test_runner_refuses_to_overwrite_an_existing_evidence_bundle(tmp_path: Path) -> None:
    root = _repo(tmp_path)
    output = tmp_path / "evidence"
    output.mkdir()
    with pytest.raises(FileExistsError):
        run_engine_v2_acceptance(root, output, checks=[])


def test_sdist_check_requires_manifests_and_at_least_one_payload(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    dist = bundle / "dist"
    dist.mkdir(parents=True)
    archive_path = dist / "whaxon-fixture.tar.gz"
    source = tmp_path / "whaxon-0.0.0"
    data = source / "src" / "whaxon" / "data"
    (data / "payloads").mkdir(parents=True)
    (data / "dependencies.json").write_text("{}")
    (data / "tools.json").write_text("{}")
    (data / "payloads" / "fixture.txt").write_text("fixture")
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(source, arcname=source.name)
    status, reason, code = _artifact_check(
        {"kind": "sdist_runtime_data"}, repo_root=tmp_path, bundle=bundle,
    )
    assert (status, reason, code) == ("passed", None, 0)

    (data / "tools.json").unlink()
    with tarfile.open(archive_path, "w:gz") as archive:
        archive.add(source, arcname=source.name)
    status, reason, code = _artifact_check(
        {"kind": "sdist_runtime_data"}, repo_root=tmp_path, bundle=bundle,
    )
    assert status == "failed"
    assert "tools.json" in (reason or "")
    assert code == 1


def test_clean_wheel_smoke_runs_install_cli_doctor_and_packaged_data(tmp_path: Path) -> None:
    bundle = tmp_path / "bundle"
    dist = bundle / "dist"
    dist.mkdir(parents=True)
    (bundle / "logs").mkdir()
    wheel = dist / "whaxon_fixture.whl"
    wheel.write_bytes(b"fixture")
    commands: list[list[str]] = []

    def fake_runner(command: list[str], **kwargs: object) -> subprocess.CompletedProcess[str]:
        commands.append(command)
        kwargs["stdout"].write(b"ok\n")  # type: ignore[union-attr]
        return subprocess.CompletedProcess(command, 0)

    status, reason, code = _artifact_check(
        {"id": "clean_wheel_smoke", "kind": "clean_wheel_smoke", "timeout_seconds": 30},
        repo_root=tmp_path, bundle=bundle, runner=fake_runner,
    )
    assert (status, reason, code) == ("passed", None, 0)
    assert len(commands) == 4
    assert commands[0][1:3] == ["-m", "pip"]
    assert commands[1][-1] == "--help"
    assert commands[2][-2:] == ["doctor", "--json"]
    assert "importlib.resources" in commands[3][-1]
