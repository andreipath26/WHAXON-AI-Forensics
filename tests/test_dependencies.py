from __future__ import annotations

import json

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
