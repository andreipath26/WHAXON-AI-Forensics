"""Read-only dependency detection and capability readiness for WHAXON.

This first implementation deliberately diagnoses only. It never installs,
changes PATH, elevates privileges, or executes commands from manifests.
"""
from __future__ import annotations

import importlib.metadata
import importlib.util
import json
import os
import platform
import shutil
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Any

SCHEMA_VERSION = 1


def load_dependency_manifest() -> dict[str, Any]:
    """Load and minimally validate the packaged dependency manifest."""
    path = Path(__file__).resolve().parents[1] / "data" / "dependencies.json"
    raw = json.loads(path.read_text(encoding="utf-8"))
    if raw.get("schema_version") != SCHEMA_VERSION or not isinstance(raw.get("dependencies"), list):
        raise ValueError("unsupported or malformed dependency manifest")
    seen: set[str] = set()
    for entry in raw["dependencies"]:
        if not isinstance(entry, dict) or not entry.get("id") or entry["id"] in seen:
            raise ValueError("dependency manifest contains an invalid or duplicate id")
        seen.add(entry["id"])
        if entry.get("kind") == "python-package" and not entry.get("minimum_version"):
            raise ValueError(f"dependency {entry['id']} has no minimum_version")
    return raw


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
                    capabilities: tuple[str, ...]) -> DependencyResult:
    try:
        version = importlib.metadata.version(dist)
    except importlib.metadata.PackageNotFoundError:
        return DependencyResult(
            dist, dist, "python-package", required, "MISSING",
            required_version=f">={minimum}", capabilities=capabilities,
            reason="Python distribution is not installed in the active interpreter.",
            remediation=f"Install the documented WHAXON extra or package containing {dist}.",
        )
    except Exception as exc:  # metadata providers can fail in broken environments
        return DependencyResult(
            dist, dist, "python-package", required, "BROKEN",
            required_version=f">={minimum}", capabilities=capabilities,
            reason=f"Package metadata could not be read ({type(exc).__name__}).",
        )
    if _version_tuple(version) < _version_tuple(minimum):
        status = "INCOMPATIBLE"
        reason = f"Installed version {version} is below required {minimum}."
    else:
        try:
            if importlib.util.find_spec(import_name) is None:
                raise ModuleNotFoundError(import_name)
        except Exception as exc:
            status = "BROKEN"
            reason = f"Package metadata exists but import failed ({type(exc).__name__})."
        else:
            status = "READY"
            reason = "Minimum version is satisfied and package import succeeded."
    return DependencyResult(
        dist, dist, "python-package", required, status, version,
        required_version=f">={minimum}", capabilities=capabilities,
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
                               include_optional: bool = True,
                               include_external: bool = True) -> dict[str, Any]:
    """Return a deterministic, read-only report; no install or network actions."""
    results: list[DependencyResult] = []
    py_status = "READY"
    py_reason = "Python runtime satisfies the declared minimum."
    results.append(DependencyResult(
        "python", "Python", "runtime", True, py_status, platform.python_version(),
        sys.executable, ">=3.11", ("core", "cli", "web", "tui", "gui"), py_reason,
        "Install Python 3.11 or newer and run WHAXON with that interpreter."
        if py_status != "READY" else "",
    ))
    try:
        manifest = load_dependency_manifest()
        for entry in manifest["dependencies"]:
            if entry.get("kind") != "python-package":
                continue
            if not include_optional and not entry.get("required", False):
                continue
            capabilities = tuple(entry.get("capabilities") or ["core"])
            results.append(_package_result(
                entry["id"], entry.get("import_name", entry["id"]), entry["minimum_version"],
                required=bool(entry.get("required")), capabilities=capabilities,
            ))
    except (OSError, ValueError, TypeError, KeyError) as exc:
        results.append(DependencyResult(
            "dependency-manifest", "Dependency manifest", "resource", True, "BROKEN",
            reason=f"Dependency manifest unavailable or invalid ({type(exc).__name__}).",
            remediation="Restore a valid packaged dependencies.json manifest.",
        ))

    catalog_path = (Path(data_dir) / "tools.json") if data_dir else (
        Path(__file__).resolve().parents[1] / "data" / "tools.json"
    )
    if include_external and not catalog_path.is_file():
        packaged_catalog = Path(__file__).resolve().parents[1] / "data" / "tools.json"
        if packaged_catalog.is_file():
            catalog_path = packaged_catalog
    if include_external and catalog_path.is_file():
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
                    "DETECTED" if path else "MISSING",
                    detected_path=path,
                    capabilities=(f"tool:{tool_id}",),
                    reason=("Executable resolved on PATH; version and smoke test are not yet verified." if path else
                            f"Executable '{binary}' was not found on PATH."),
                    remediation=("" if path else
                                 "Use the platform's trusted package source or the official project instructions; "
                                 "WHAXON has not attempted an installation."),
                ))
        except (OSError, ValueError, TypeError) as exc:
            results.append(DependencyResult(
                "tool-catalog", "Tool catalog", "resource", True, "BROKEN",
                reason=f"Could not read tool catalog ({type(exc).__name__}).",
            ))
    elif include_external:
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
            "detected_unverified": sum(r.status == "DETECTED" for r in results),
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
