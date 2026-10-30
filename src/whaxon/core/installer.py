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
import time
import uuid
from collections.abc import Callable
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from whaxon.core.dependencies import _version_tuple, load_dependency_manifest
from whaxon.core.remediation import build_python_package_argv, build_remediation_plan

INSTALL_TIMEOUT_SECONDS = 900
_SECRET_PATTERNS = (
    re.compile(r"(?i)(token|password|secret|api[_-]?key)(\s*[:=]\s*)[^\s,;]+"),
    re.compile(r"(?i)(bearer\s+)[A-Za-z0-9._~+/=-]+"),
)


def _redact(value: str, limit: int = 12000) -> str:
    clean = value[:limit]
    clean = _SECRET_PATTERNS[0].sub(r"\1\2[REDACTED]", clean)
    clean = _SECRET_PATTERNS[1].sub(r"\1[REDACTED]", clean)
    return clean


def _audit_path() -> Path:
    return Path.home() / ".whaxon" / "audit" / "dependency-install.jsonl"


def _append_audit(record: dict[str, Any]) -> None:
    path = _audit_path()
    path.parent.mkdir(mode=0o700, parents=True, exist_ok=True)
    descriptor = os.open(path, os.O_APPEND | os.O_CREAT | os.O_WRONLY, 0o600)
    with os.fdopen(descriptor, "a", encoding="utf-8") as stream:
        stream.write(json.dumps(record, sort_keys=True) + "\n")


def _finish_audit(result: dict[str, Any]) -> dict[str, Any]:
    """Never misreport an executed install if its final audit write fails."""
    try:
        _append_audit(result)
    except OSError as exc:
        return {
            **result,
            "original_status": result["status"],
            "status": "AUDIT_FAILED",
            "audit_error": type(exc).__name__,
            "recovery": (
                "The operation ran but its final audit record could not be written. "
                "Run whaxon doctor to establish current state and inspect the local audit directory."
            ),
        }
    return result


def apply_approved_dependency_plan(
    dependency_id: str,
    approved_plan_id: str,
    *,
    data_dir: Path | None = None,
    progress_callback: Callable[[str, str], None] | None = None,
    cancel_requested: Callable[[], bool] | None = None,
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
    policy = manifest.get("policy", {})
    if (
        policy.get("automatic_installation_enabled") is not True
        or "python-package" not in policy.get("automatic_installation_kinds", [])
    ):
        raise ValueError("automatic Python-package installation is disabled by the dependency policy")
    entry = next((item for item in manifest["dependencies"] if item["id"] == dependency_id), None)
    if not entry or entry.get("kind") != "python-package":
        raise ValueError("Dependency is not an allowlisted Python package.")
    argv = build_python_package_argv(entry)
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
    if cancel_requested and cancel_requested():
        result = {
            **base,
            "status": "CANCELLED",
            "exit_code": None,
            "output": "Installation was cancelled before the package manager started.",
            "recovery": "No package-manager command was started. Re-run doctor and create a new plan if needed.",
            "finished_at": datetime.now(UTC).isoformat(),
        }
        return _finish_audit(result)
    if progress_callback:
        progress_callback("INSTALLING", "Installing the approved Python package.")
    process = None
    try:
        process = subprocess.Popen(
            argv,
            shell=False,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        started_monotonic = time.monotonic()
        last_progress = started_monotonic
        while True:
            if cancel_requested and cancel_requested() and process.poll() is None:
                if process.poll() is None:
                    process.terminate()
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                result = {
                    **base,
                    "status": "CANCELLED",
                    "exit_code": process.returncode,
                    "output": _redact((stdout or "") + "\n" + (stderr or "")),
                    "recovery": "The package operation was terminated; package state may be partial. Re-run whaxon doctor and recreate the virtual environment if inconsistent.",
                    "finished_at": datetime.now(UTC).isoformat(),
                }
                result = _finish_audit(result)
                return result
            elapsed = time.monotonic() - started_monotonic
            if progress_callback and elapsed - last_progress >= 5:
                progress_callback("INSTALLING", f"Package manager running for {int(elapsed)} seconds.")
                last_progress = elapsed
            if elapsed >= INSTALL_TIMEOUT_SECONDS and process.poll() is None:
                process.terminate()
                try:
                    stdout, stderr = process.communicate(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    stdout, stderr = process.communicate()
                result = {
                    **base,
                    "status": "TIMED_OUT",
                    "exit_code": process.returncode,
                    "output": _redact((stdout or "") + "\n" + (stderr or "")),
                    "recovery": "The package manager was terminated after timeout. Re-run whaxon doctor; recreate the virtual environment if package state is uncertain.",
                    "finished_at": datetime.now(UTC).isoformat(),
                }
                result = _finish_audit(result)
                return result
            try:
                stdout, stderr = process.communicate(timeout=0.25)
                break
            except subprocess.TimeoutExpired:
                continue
        exit_code = process.returncode
        output = _redact((stdout or "") + "\n" + (stderr or ""))
        if exit_code != 0:
            result = {**base, "status": "INSTALL_FAILED", "exit_code": exit_code,
                      "output": output, "recovery": "No automatic rollback was attempted. Re-run whaxon doctor; if the environment is inconsistent, recreate the virtual environment and reinstall from the approved lock/profile.", "finished_at": datetime.now(UTC).isoformat()}
            result = _finish_audit(result)
            return result
    except OSError as exc:
        result = {**base, "status": "INSTALL_FAILED", "exit_code": None,
                  "output": _redact(str(exc)), "recovery": "The package manager could not be started. No successful installation is confirmed.", "finished_at": datetime.now(UTC).isoformat()}
        result = _finish_audit(result)
        return result
    except KeyboardInterrupt:
        if process is not None and process.poll() is None:
            process.terminate()
            try:
                process.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.communicate()
        result = {**base, "status": "INTERRUPTED", "exit_code": None,
                  "output": "Installation interrupted by user.",
                  "recovery": "The package manager may have partially changed the virtual environment. Re-run whaxon doctor and recreate the venv if state is inconsistent.",
                  "finished_at": datetime.now(UTC).isoformat()}
        _finish_audit(result)
        raise

    if progress_callback:
        progress_callback("VERIFYING", "Checking installed package version and import availability.")
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
        "finished_at": datetime.now(UTC).isoformat(),
    }
    result = _finish_audit(result)
    if progress_callback:
        progress_callback(result["status"], result.get("verification", result.get("recovery", "Installation finished.")))
    return result
