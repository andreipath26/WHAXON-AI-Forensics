from __future__ import annotations

import json
import tomllib
import subprocess

from whaxon.core.dependencies import collect_dependency_report


def test_dependency_report_is_read_only_and_versioned():
    report = collect_dependency_report(include_optional=False)
    assert report["schema_version"] == 1
    assert report["environment"]["python_executable"]
    assert report["dependencies"]
    assert report["safety"] == {
        "read_only": True,
        "installation_attempted": False,
        "network_accessed": False,
        "privilege_escalation_attempted": False,
    }


def test_dependency_report_json_serializable():
    report = collect_dependency_report(include_optional=True)
    encoded = json.dumps(report)
    assert '"dependencies"' in encoded


def test_packaged_catalog_is_used_when_user_data_is_not_initialized(tmp_path):
    report = collect_dependency_report(data_dir=tmp_path, include_optional=False)
    assert any(d["id"] == "nmap" for d in report["dependencies"])


def test_optional_dependencies_do_not_block_core(tmp_path):
    report = collect_dependency_report(data_dir=tmp_path, include_optional=True)
    if report["summary"]["required_blockers"] == 0:
        assert report["overall_status"] in {"READY", "DEGRADED"}


def test_manifest_has_unique_ids_and_profiles():
    from whaxon.core.dependencies import load_dependency_manifest

    manifest = load_dependency_manifest()
    ids = [entry["id"] for entry in manifest["dependencies"]]
    assert len(ids) == len(set(ids))
    assert "core" in manifest["profiles"]


def test_external_version_probe_is_opt_in_and_bounded(tmp_path, monkeypatch):
    import whaxon.core.dependencies as dependencies

    (tmp_path / "tools.json").write_text(json.dumps({
        "tools": [{"id": "nmap", "name": "Nmap", "binary": "nmap", "transport": "cli"}]
    }))
    calls = []

    def fake_run(argv, **kwargs):
        calls.append((argv, kwargs))
        return subprocess.CompletedProcess(
            argv, 0, stdout="Nmap version 7.95 ( https://nmap.org )", stderr=""
        )

    monkeypatch.setattr(dependencies.shutil, "which", lambda _binary: "/usr/bin/nmap")
    monkeypatch.setattr(dependencies.subprocess, "run", fake_run)

    detected = dependencies.collect_dependency_report(
        data_dir=tmp_path, include_optional=False, verify_external=False
    )
    assert next(d for d in detected["dependencies"] if d["id"] == "nmap")["status"] == "DETECTED"
    assert calls == []

    verified = dependencies.collect_dependency_report(
        data_dir=tmp_path, include_optional=False, verify_external=True
    )
    nmap = next(d for d in verified["dependencies"] if d["id"] == "nmap")
    assert nmap["status"] == "READY"
    assert nmap["detected_version"] == "7.95"
    assert calls[0][1]["shell"] is False
    assert calls[0][1]["timeout"] == 8


def test_external_version_probe_failure_is_not_ready(tmp_path, monkeypatch):
    import whaxon.core.dependencies as dependencies

    (tmp_path / "tools.json").write_text(json.dumps({
        "tools": [{"id": "nmap", "name": "Nmap", "binary": "nmap", "transport": "cli"}]
    }))
    monkeypatch.setattr(dependencies.shutil, "which", lambda _binary: "/usr/bin/nmap")
    monkeypatch.setattr(
        dependencies.subprocess,
        "run",
        lambda argv, **kwargs: subprocess.CompletedProcess(argv, 1, stdout="", stderr="bad"),
    )
    report = dependencies.collect_dependency_report(
        data_dir=tmp_path, include_optional=False, verify_external=True
    )
    nmap = next(d for d in report["dependencies"] if d["id"] == "nmap")
    assert nmap["status"] == "BROKEN"


def test_unsupported_python_runtime_blocks_core(monkeypatch):
    import whaxon.core.dependencies as dependencies

    monkeypatch.setattr(dependencies.platform, "python_version", lambda: "3.10.14")
    report = dependencies.collect_dependency_report(
        include_optional=False,
        include_external=False,
    )
    runtime = next(item for item in report["dependencies"] if item["id"] == "python")
    assert runtime["status"] == "INCOMPATIBLE"
    assert report["overall_status"] == "BLOCKED"


def test_invalid_manifest_disables_external_version_probes(tmp_path, monkeypatch):
    import whaxon.core.dependencies as dependencies

    (tmp_path / "tools.json").write_text(json.dumps({
        "tools": [{"id": "nmap", "name": "Nmap", "binary": "nmap", "transport": "cli"}]
    }))
    monkeypatch.setattr(dependencies, "load_dependency_manifest", lambda: (_ for _ in ()).throw(ValueError("invalid")))
    monkeypatch.setattr(dependencies.shutil, "which", lambda _binary: "/usr/bin/nmap")
    monkeypatch.setattr(
        dependencies.subprocess,
        "run",
        lambda *_args, **_kwargs: (_ for _ in ()).throw(AssertionError("probe must not run")),
    )
    report = dependencies.collect_dependency_report(
        data_dir=tmp_path, include_optional=False, verify_external=True
    )
    assert next(item for item in report["dependencies"] if item["id"] == "dependency-manifest")["status"] == "BROKEN"
    assert next(item for item in report["dependencies"] if item["id"] == "nmap")["status"] == "DETECTED"


def test_malformed_tool_catalog_is_reported_as_broken(tmp_path):
    (tmp_path / "tools.json").write_text("[]")
    report = collect_dependency_report(
        data_dir=tmp_path, include_optional=False, verify_external=False
    )
    catalog = next(item for item in report["dependencies"] if item["id"] == "tool-catalog")
    assert catalog["status"] == "BROKEN"


def test_manifest_covers_all_declared_runtime_dependencies():
    from pathlib import Path

    manifest = load_dependency_manifest()
    project = tomllib.loads(
        (Path(__file__).parents[1] / "pyproject.toml").read_text(encoding="utf-8")
    )["project"]
    declared = {
        requirement.split(">=", 1)[0].split("[", 1)[0].lower().replace("_", "-")
        for requirement in project.get("dependencies", [])
    }
    for extra, requirements in project.get("optional-dependencies", {}).items():
        if extra == "dev":
            continue
        declared.update(
            requirement.split(">=", 1)[0].split("[", 1)[0].lower().replace("_", "-")
            for requirement in requirements
        )
    manifest_ids = {
        item["id"].lower().replace("_", "-")
        for item in manifest["dependencies"]
        if item["kind"] == "python-package"
    }
    assert declared <= manifest_ids
