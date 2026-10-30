"""Read-only dependency detection and capability readiness for WHAXON.

This first implementation deliberately diagnoses only. It never installs,
changes PATH, elevates privileges, or executes commands from manifests.
"""
from __future__ import annotations

import importlib.metadata
import json
import os
import platform
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1
CORE_PACKAGES = (
    ("platformdirs", "platformdirs", "4.0"),
    ("dnspython", "dns", "2.6"),
    ("defusedxml", "defusedxml", "0.7.1"),
)
OPTIONAL_EXTRAS = {
    "tui": (("textual", "textual", "0.80"), ("rich", "rich", "13")),
    "gui": (("PySide6", "PySide6", "6.7"), ("qasync", "qasync", "0.27")),
    "web": (("flask", "flask", "3.0"),),
    "metasploit": (("pymetasploit3", "pymetasploit3", "2.0"),),
}


@dataclass(frozen=True)
class DependencyResult:
    id: str
    name: str
    kind: str
    required: bool
    status: str
    detected_version: str | None = None
    detected_path: str | None = None
    required_version: str | None = None
    capabilities: tuple[str, ...] = ()
    reason: str = ""
    remediation: str = ""


def _version_tuple(value: str) -> tuple[int, ...]:
    parts: list[int] = []
    for part in value.split("."):
        digits = "".join(ch for ch in part if ch.isdigit())
        if not digits:
            break
        parts.append(int(digits))
    return tuple(parts)


def _package_result(dist: str, import_name: str, minimum: str, *, required: bool,
                    capability: str) -> DependencyResult:
    try:
        version = importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        return DependencyResult(
            dist, dist, "python-package", required, "MISSING",
            required_version=f">={minimum}", capabilities=(capability,),
            reason="Python distribution is not installed in the active interpreter.",
            remediation=f"Install the documented WHAXON extra or package containing {dist}.",
        )
    except Exception as exc:  # metadata providers can fail in broken environments
        return DependencyResult(
            dist, dist, "python-package", required, "BROKEN",
            required_version=f">={minimum}", capabilities=(capability,),
            reason=f"Package metadata could not be read ({type(exc).__name__}).",
        )
    status = "READY" if _version_tuple(version) >= _version_tuple(minimum) else "INCOMPATIBLE"
    reason = "Installed version satisfies the minimum." if status == "READY" else (
        f"Installed version {version} is below required {minimum}."
    )
    return DependencyResult(
        dist, dist, "python-package", required, status, version,
        required_version=f">={minimum}", capabilities=(capability,),
        reason=reason,
        remediation="" if status == "READY" else f"Upgrade {dist} in the active environment.",
    )


def _environment() -> dict[str, Any]:
    return {
        "os": platform.system(),
        "os_release": platform.release(),
        "platform": platform.platform(),
        "architecture": platform.machine(),
        "python": platform.python_version(),
        "python_implementation": platform.python_implementation(),
        "python_executable": sys.executable,
        "virtual_environment": bool(sys.prefix != getattr(sys, "base_prefix", sys.prefix)),
        "cwd": str(Path.cwd()),
        "path_entries": len(os.environ.get("PATH", "").split(os.pathsep)),
    }


def collect_dependency_report(*, data_dir: Path | None = None,
                               include_optional: bool = True) -> dict[str, Any]:
    """Return a deterministic, read-only report; no install or network actions."""
    results: list[DependencyResult] = []
    if sys.version_info < (3, 11):
        py_status = "INCOMPATIBLE"
        py_reason = "WHAXON requires Python 3.11 or newer."
    else:
        py_status = "READY"
        py_reason = "Python runtime satisfies the declared minimum."
    results.append(DependencyResult(
        "python", "Python", "runtime", True, py_status, platform.python_version(),
        sys.executable, ">=3.11", ("core", "cli", "web", "tui", "gui"), py_reason,
        "Install Python 3.11 or newer and run WHAXON with that interpreter."
        if py_status != "READY" else "",
    ))
    for dist, import_name, minimum in CORE_PACKAGES:
        results.append(_package_result(
            dist, import_name, minimum, required=True, capability="core",
        ))
    if include_optional:
        for extra, packages in OPTIONAL_EXTRAS.items():
            for dist, import_name, minimum in packages:
                results.append(_package_result(
                    dist, import_name, minimum, required=False, capability=extra,
                ))

    catalog_path = (Path(data_dir) / "tools.json") if data_dir else (
        Path(__file__).resolve().parents[1] / "data" / "tools.json"
    )
    if catalog_path.is_file():
        try:
            raw = json.loads(catalog_path.read_text(encoding="utf-8"))
            for tool in raw.get("tools", []):
                binary = str(tool.get("binary") or "")
                transport = str(tool.get("transport") or "cli")
                if not binary or transport != "cli":
                    continue
                path = shutil.which(binary)
                tool_id = str(tool.get("id") or binary)
                results.append(DependencyResult(
                    tool_id, str(tool.get("name") or tool_id), "external-tool", False,
                    "READY" if path else "MISSING",
                    detected_path=path,
                    capabilities=(f"tool:{tool_id}",),
                    reason=("Executable resolved on PATH." if path else
                            f"Executable '{binary}' was not found on PATH."),
                    remediation=(" " if path else
                                 "Use the platform's trusted package source or the official project instructions; "
                                 "WHAXON has not attempted an installation."),
                ))
        except (OSError, ValueError, TypeError) as exc:
            results.append(DependencyResult(
                "tool-catalog", "Tool catalog", "resource", True, "BROKEN",
                reason=f"Could not read tool catalog ({type(exc).__name__}).",
            ))
    else:
        results.append(DependencyResult(
            "tool-catalog", "Tool catalog", "resource", True, "MISSING",
            reason=f"Tool catalog not found at {catalog_path}.",
            remediation="Restore the packaged tools.json resource or initialize the WHAXON data directory.",
        ))

    required_bad = [r for r in results if r.required and r.status != "READY"]
    optional_bad = [r for r in results if not r.required and r.status != "READY"]
    overall = "BLOCKED" if required_bad else ("DEGRADED" if optional_bad else "READY")
    return {
        "schema_version": SCHEMA_VERSION,
        "environment": _environment(),
        "overall_status": overall,
        "summary": {
            "total": len(results),
            "ready": sum(r.status == "READY" for r in results),
            "missing": sum(r.status == "MISSING" for r in results),
            "incompatible": sum(r.status == "INCOMPATIBLE" for r in results),
            "broken": sum(r.status == "BROKEN" for r in results),
            "required_blockers": len(required_bad),
            "optional_degraded": len(optional_bad),
        },
        "dependencies": [asdict(r) for r in results],
        "safety": {
            "read_only": True,
            "installation_attempted": False,
            "network_accessed": False,
            "privilege_escalation_attempted": False,
        },
    }
