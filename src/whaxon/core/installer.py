"""Explicitly approved, allowlisted Python-package installation transactions.

This module is intentionally narrow: no shell, no OS package manager, no
privilege escalation, and no manifest-supplied executable or argument strings.
"""
from __future__ import annotations

import importlib
import importlib.metadata
import json
import os
import re
import subprocess
import sys
import uuid
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from whaxon.core.dependencies import _version_tuple, load_dependency_manifest
from whaxon.core.remediation import build_remediation_plan

INSTALL_TIMEOUT_SECONDS = 900
_SECRET_PATTERNS = (
    re.compile(r"(?i)(token|password|secret|api[_-]?key)(\s*[:=]\s*)[^\s,;]+"),
    re.compile(r"(?i)bearer\s+[A-Za-z0-9._~+/=-]+"),
)


def _redact(value: str, limit: int = 12000) -> str:
    clean = value[:limit]
    for pattern in _SECRET_PATTERNS:
        clean = pattern.sub(r"\1\2[REDACTED]", clean)
    return clean


def _audit_path() -> Path:
    return Path.home() / ".whaxon" / "audit" / "dependency-install.jsonl"


def _append_audit(record: dict[str, Any]) -> None:
    path = _audit_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def apply_approved_dependency_plan(
    dependency_id: str,
    approved_plan_id: str,
    *,
    data_dir: Path | None = None,
) -> dict[str, Any]:
    """Install exactly one manifest-declared Python package after plan-ID approval."""
    plan = build_remediation_plan(dependency_ids=[dependency_id], data_dir=data_dir)
    if plan["unknown_dependency_ids"]:
        raise ValueError(f"Unknown dependency: {dependency_id}")
    if plan["plan_id"] != approved_plan_id:
        raise ValueError("Approval does not match the current remediation plan; regenerate and review it.")
    actions = [action for action in plan["actions"] if action["dependency_id"] == dependency_id]
    if len(actions) != 1:
        raise ValueError("Dependency does not require an automated installation.")
    options = actions[0]["options"]
    if len(options) != 1 or options[0]["kind"] != "python-package":
        raise ValueError("No supported automated installation is available for this dependency.")
    if sys.prefix == getattr(sys, "base_prefix", sys.prefix):
        raise ValueError(
            "Automatic Python-package installation requires an active virtual environment. "
            "Create and activate a venv, then run doctor and review a fresh plan."
        )

    manifest = load_dependency_manifest()
    entry = next((item for item in manifest["dependencies"] if item["id"] == dependency_id), None)
    if not entry or entry.get("kind") != "python-package":
        raise ValueError("Dependency is not an allowlisted Python package.")
    requirement = f"{entry['id']}>={entry['minimum_version']}"
    argv = [
        sys.executable, "-m", "pip", "install", "--disable-pip-version-check",
        "--no-input", "--quiet", "--progress-bar", "off",
        "--only-binary=:all:", "--index-url",
        "https://pypi.org/simple", requirement,
    ]
    operation_id = str(uuid.uuid4())
    started = datetime.now(UTC).isoformat()
    base = {
        "schema_version": 1,
        "operation_id": operation_id,
        "dependency_id": dependency_id,
        "plan_id": approved_plan_id,
        "manifest_schema_version": manifest["schema_version"],
        "started_at": started,
        "interpreter": sys.executable,
        "command": argv,
        "privilege_escalation": False,
        "shell": False,
    }
    _append_audit({**base, "status": "STARTED"})
    try:
        completed = subprocess.run(
            argv, shell=False, check=False, capture_output=True, text=True,
            timeout=INSTALL_TIMEOUT_SECONDS,
        )
        exit_code = completed.returncode
        output = _redact((completed.stdout or "") + "\n" + (completed.stderr or ""))
        if exit_code != 0:
            result = {**base, "status": "INSTALL_FAILED", "exit_code": exit_code,
                      "output": output, "recovery": "No automatic rollback was attempted. Re-run whaxon doctor; if the environment is inconsistent, recreate the virtual environment and reinstall from the approved lock/profile.", "finished_at": datetime.now(UTC).isoformat()}
            _append_audit(result)
            return result
    except subprocess.TimeoutExpired as exc:
        result = {**base, "status": "TIMED_OUT", "exit_code": None,
                  "output": _redact(str(exc)), "recovery": "The pip process was terminated after timeout. Re-run whaxon doctor; recreate the virtual environment if package state is uncertain.", "finished_at": datetime.now(timezone.utc).isoformat()}
        _append_audit(result)
        return result
    except KeyboardInterrupt:
        result = {**base, "status": "INTERRUPTED", "exit_code": None,
                  "output": "Installation interrupted by user.",
                  "recovery": "The package manager may have partially changed the virtual environment. Re-run whaxon doctor and recreate the venv if state is inconsistent.",
                  "finished_at": datetime.now(timezone.utc).isoformat()}
        _append_audit(result)
        raise

    try:
        version = importlib.metadata.version(entry["id"])
        importlib.import_module(entry.get("import_name", entry["id"]))
        verified = _version_tuple(version) >= _version_tuple(entry["minimum_version"])
        verification_reason = (
            "Installed distribution meets the minimum version and import check succeeded."
            if verified else "Installed version is below the declared minimum."
        )
    except Exception as exc:
        version = None
        verified = False
        verification_reason = f"Post-install verification failed ({type(exc).__name__})."
    result = {
        **base,
        "status": "VERIFIED" if verified else "VERIFICATION_FAILED",
        "exit_code": 0,
        "installed_version": version,
        "verification": verification_reason,
        "output": output,
        "finished_at": datetime.now(timezone.utc).isoformat(),
    }
    _append_audit(result)
    return result
