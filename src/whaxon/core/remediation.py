"""Deterministic, read-only remediation planning for dependency diagnostics."""
from __future__ import annotations

import json
import platform
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

from whaxon.core.dependencies import collect_dependency_report, load_dependency_manifest

PLAN_SCHEMA_VERSION = 1


def _python_package_option(entry: dict[str, Any]) -> dict[str, Any]:
    requirement = f"{entry['id']}>={entry['minimum_version']}"
    description = f"Install or upgrade {entry['id']} in the active interpreter."
    argv = [sys.executable, "-m", "pip", "install", requirement]
    return {
        "id": f"pip:{entry['id']}",
        "kind": "python-package",
        "title": description,
        "command": argv,
        "display_command": (subprocess.list2cmdline(argv) if platform.system() == "Windows" else shlex.join(argv)),
        "requires_network": True,
        "requires_privilege": False,
        "system_wide": False,
        "automated_execution_supported": False,
        "approval_required": True,
        "warning": "Preview only. This plan does not execute pip or resolve/install packages.",
    }


def build_remediation_plan(*, dependency_ids: list[str] | None = None,
                           data_dir: Path | None = None) -> dict[str, Any]:
    """Build a deterministic plan from the packaged manifest and current read-only state."""
    manifest = load_dependency_manifest()
    report = collect_dependency_report(data_dir=data_dir)
    entries = {entry["id"]: entry for entry in manifest["dependencies"]}
    observed = {entry["id"]: entry for entry in report["dependencies"]}
    selected = set(dependency_ids or observed)
    unknown = sorted(selected - set(observed))
    actions: list[dict[str, Any]] = []
    for dep_id in sorted(selected & set(observed)):
        result = observed[dep_id]
        if result["status"] in {"READY", "DETECTED"}:
            continue
        manifest_entry = entries.get(dep_id)
        if manifest_entry and manifest_entry.get("kind") == "python-package":
            actions.append({
                "dependency_id": dep_id,
                "current_status": result["status"],
                "options": [_python_package_option(manifest_entry)],
            })
        elif dep_id == "python":
            actions.append({
                "dependency_id": dep_id,
                "current_status": result["status"],
                "options": [{
                    "id": "manual:python-runtime",
                    "kind": "manual",
                    "title": "Install a supported Python 3.11+ runtime using the official distribution for this operating system.",
                    "command": None,
                    "display_command": None,
                    "requires_network": None,
                    "requires_privilege": "depends-on-install-method",
                    "system_wide": "depends-on-install-method",
                    "automated_execution_supported": False,
                    "approval_required": False,
                    "warning": "WHAXON cannot safely choose a Python installer for this host yet.",
                }],
            })
        else:
            actions.append({
                "dependency_id": dep_id,
                "current_status": result["status"],
                "options": [{
                    "id": f"manual:{dep_id}",
                    "kind": "manual",
                    "title": result.get("remediation") or "Consult the official project installation instructions.",
                    "command": None,
                    "display_command": None,
                    "requires_network": None,
                    "requires_privilege": "unknown",
                    "system_wide": "unknown",
                    "automated_execution_supported": False,
                    "approval_required": False,
                    "warning": "No trusted platform-specific installer is configured for this dependency.",
                }],
            })
    return {
        "schema_version": PLAN_SCHEMA_VERSION,
        "plan_id": "plan-" + __import__("hashlib").sha256(
            json.dumps({"selected": sorted(selected), "environment": report["environment"],
                        "manifest_schema": manifest["schema_version"]},
                       sort_keys=True, separators=(",", ":")).encode()
        ).hexdigest()[:16],
        "platform": {
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "overall_status": report["overall_status"],
        "actions": actions,
        "unknown_dependency_ids": unknown,
        "safety": {
            "read_only": True,
            "commands_executed": False,
            "network_accessed": False,
            "installation_attempted": False,
            "privilege_escalation_attempted": False,
            "approval_granted": False,
        },
        "notice": "A plan is not authorization. No command in this document has been executed.",
    }
