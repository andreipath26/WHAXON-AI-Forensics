#!/usr/bin/env python3
"""Run local Engine V2 release checks and write a reviewable evidence bundle.

This runner does not use Git, contact external targets, publish artifacts, or
claim deployment readiness. Supply the source revision explicitly (or set
GITHUB_SHA/WHAXON_SOURCE_REVISION); exact remote CI, approved lab, external
audit-anchor, manual UI, and operator-acceptance gates remain separate.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import shlex
import shutil
import subprocess
import sys
import tarfile
import time
import venv
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

_EXTERNAL_GATES = (
    ("exact_head_ci_matrix", "pending", "GitHub CI for this exact source revision, including Python 3.11-3.13 and platform jobs"),
    ("authorized_provider_effect_lab", "pending", "Operator-approved controlled target lab with retained effect and recovery evidence"),
    ("independent_audit_anchor", "pending", "Independent protected retention and verification of the lifecycle digest"),
    ("manual_ui_accessibility_review", "pending", "Manual review of supplied UI workflows, keyboard/screen-reader behavior, and approved visual references"),
    ("production_service_recovery", "pending", "Operator-reviewed production-like install, upgrade, rollback, multi-worker, and backup/restore evidence"),
    ("independent_engineering_acceptance", "pending", "Named reviewer signs the exact candidate SHA, residuals, and rollback decision"),
    ("release_artifact_publication", "pending", "Verified release identity and package artifacts after all implementation and qualification gates pass"),
)


def _utc_now() -> str:
    return datetime.now(UTC).isoformat(timespec="seconds").replace("+00:00", "Z")


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _write_json_atomic(path: Path, value: dict[str, Any]) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(
        json.dumps(value, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    temporary.replace(path)


def _source_revision(explicit: str | None) -> str:
    value = explicit or os.environ.get("WHAXON_SOURCE_REVISION") or os.environ.get("GITHUB_SHA")
    if value is None:
        return "unknown"
    value = value.strip()
    if value != "unknown" and (
        not 7 <= len(value) <= 64
        or any(char not in "0123456789abcdefABCDEF" for char in value)
    ):
        raise ValueError("source revision must be a 7-64 digit hexadecimal SHA or 'unknown'")
    return value.lower()


def _default_output_root(repo_root: Path, revision: str) -> Path:
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    label = revision[:12] if revision != "unknown" else "unidentified"
    return repo_root / "artifacts" / "engine-v2-acceptance" / f"{stamp}-{label}"


def _distribution_artifacts(dist_dir: Path) -> list[dict[str, Any]]:
    """Identify exact package outputs so the evidence report binds their bytes."""
    paths = sorted(dist_dir.glob("*.whl")) + sorted(dist_dir.glob("*.tar.gz"))
    return [
        {"filename": path.name, "size_bytes": path.stat().st_size, "sha256": _sha256(path)}
        for path in paths if path.is_file()
    ]


def _checks(bundle: Path) -> list[dict[str, Any]]:
    dist_dir = bundle / "dist"
    python = sys.executable
    return [
        {
            "id": "ai_boundary",
            "title": "AI/core import boundary",
            "command": [python, "-m", "pytest", "tests/test_ai_boundary.py", "-q", "-ra"],
            "timeout_seconds": 600,
        },
        {
            "id": "ruff",
            "title": "Ruff source, tests, and scripts",
            "command": ["ruff", "check", "src", "tests", "scripts"],
            "timeout_seconds": 600,
        },
        {
            "id": "mypy",
            "title": "Mypy source tree",
            "command": ["mypy", "src"],
            "timeout_seconds": 1200,
        },
        {
            "id": "full_test_suite",
            "title": "Full repository test suite",
            "command": [python, "-m", "pytest", "tests/", "-q", "-ra"],
            "timeout_seconds": 7200,
        },
        {
            "id": "build_distributions",
            "title": "Build wheel and source distribution",
            "command": [python, "-m", "build", "--wheel", "--sdist", "--outdir", str(dist_dir)],
            "timeout_seconds": 1800,
        },
        {
            "id": "distribution_metadata",
            "title": "Validate built distribution metadata",
            "command": ["twine", "check", str(dist_dir / "*")],
            "timeout_seconds": 600,
            "expand_glob": True,
        },
        {
            "id": "sdist_runtime_data",
            "title": "Source archive contains required runtime catalogs and payloads",
            "kind": "sdist_runtime_data",
            "timeout_seconds": 60,
        },
        {
            "id": "clean_wheel_smoke",
            "title": "Install wheel in a fresh environment and smoke-test CLI/data",
            "kind": "clean_wheel_smoke",
            "timeout_seconds": 1800,
        },
    ]


def _artifact_check(
    check: dict[str, Any], *, repo_root: Path, bundle: Path,
    runner=subprocess.run,
) -> tuple[str, str | None, int | None]:
    """Perform package checks whose logic is clearer than a shell pipeline."""
    dist_dir = bundle / "dist"
    if check["kind"] == "sdist_runtime_data":
        archives = sorted(dist_dir.glob("*.tar.gz"))
        if not archives:
            return "blocked", "distribution build produced no source archive", None
        required = ("dependencies.json", "tools.json")
        try:
            with tarfile.open(archives[0], "r:gz") as archive:
                names = archive.getnames()
                missing = [
                    name for name in required
                    if not any(path.endswith(f"/whaxon/data/{name}") for path in names)
                ]
                payloads = [
                    path for path in names
                    if "/whaxon/data/payloads/" in path and not path.endswith("/")
                ]
            if missing or not payloads:
                return "failed", f"missing runtime data: {missing}; payload_count={len(payloads)}", 1
        except (OSError, tarfile.TarError) as exc:
            return "failed", f"could not inspect source archive: {type(exc).__name__}", 1
        return "passed", None, 0

    wheels = sorted(dist_dir.glob("*.whl"))
    if not wheels:
        return "blocked", "distribution build produced no wheel", None
    smoke_env = bundle / "wheel-smoke-venv"
    try:
        venv.EnvBuilder(with_pip=True).create(smoke_env)
    except OSError as exc:
        return "blocked", f"could not create wheel smoke environment: {type(exc).__name__}", None
    bin_dir = "Scripts" if os.name == "nt" else "bin"
    python = smoke_env / bin_dir / ("python.exe" if os.name == "nt" else "python")
    cli = smoke_env / bin_dir / ("whaxon.exe" if os.name == "nt" else "whaxon")
    log_path = bundle / "logs" / f"{check['id']}.log"
    commands = [
        [str(python), "-m", "pip", "install", str(wheels[0])],
        [str(cli), "--help"],
        [str(cli), "doctor", "--json"],
        [str(python), "-c", (
            "from importlib.resources import files; "
            "d=files('whaxon').joinpath('data'); "
            "assert d.joinpath('tools.json').is_file(); "
            "assert d.joinpath('dependencies.json').is_file(); "
            "p=d.joinpath('payloads'); "
            "assert p.is_dir() and any(p.iterdir())"
        )],
    ]
    try:
        with log_path.open("ab") as log:
            for command in commands:
                log.write(("\\n$ " + shlex.join(command) + "\\n").encode())
                log.flush()
                result = runner(
                    command, cwd=repo_root, stdout=log, stderr=subprocess.STDOUT,
                    timeout=check["timeout_seconds"], check=False,
                    env={**os.environ, "PYTHONUNBUFFERED": "1"},
                )
                if result.returncode:
                    return "failed", f"wheel smoke command exited with status {result.returncode}", result.returncode
    except subprocess.TimeoutExpired:
        return "failed", f"wheel smoke exceeded {check['timeout_seconds']} seconds", None
    except OSError as exc:
        return "blocked", f"could not run wheel smoke: {type(exc).__name__}", None
    return "passed", None, 0


def _run_check(
    check: dict[str, Any], *, repo_root: Path, bundle: Path,
    runner=subprocess.run,
) -> dict[str, Any]:
    log_path = bundle / "logs" / f"{check['id']}.log"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    if check.get("kind"):
        started = time.monotonic()
        try:
            status, reason, return_code = _artifact_check(
                check, repo_root=repo_root, bundle=bundle, runner=runner,
            )
        except Exception as exc:
            status, return_code = "blocked", None
            reason = f"artifact-check harness raised {type(exc).__name__}"
        with log_path.open("a", encoding="utf-8") as log:
            log.write(f"status={status}\n")
            if reason:
                log.write(f"reason={reason}\n")
        return {
            "id": check["id"], "title": check["title"], "status": status,
            "command": ["<built-in artifact validation>"], "return_code": return_code,
            "duration_seconds": round(time.monotonic() - started, 3),
            "timeout_seconds": check["timeout_seconds"], "reason": reason,
            "log": str(log_path.relative_to(bundle)),
            "log_sha256": _sha256(log_path),
        }
    command = list(check["command"])
    if check.get("expand_glob"):
        dist_dir = Path(command[-1]).parent
        artifacts = sorted(dist_dir.glob("*.whl")) + sorted(dist_dir.glob("*.tar.gz"))
        command = command[:-1] + [str(item) for item in artifacts]
        if not artifacts:
            return {
                "id": check["id"], "title": check["title"], "status": "blocked",
                "command": command, "duration_seconds": 0.0,
                "reason": "distribution build produced no wheel or source archive",
                "log": str(log_path.relative_to(bundle)),
            }
    if any(shutil.which(token) is None for token in (command[0],) if not Path(token).is_absolute()):
        reason = f"required executable is unavailable: {command[0]}"
        log_path.write_text(reason + "\n", encoding="utf-8")
        return {
            "id": check["id"], "title": check["title"], "status": "blocked",
            "command": command, "duration_seconds": 0.0, "reason": reason,
            "log": str(log_path.relative_to(bundle)), "log_sha256": _sha256(log_path),
        }
    started = time.monotonic()
    status = "passed"
    reason = None
    return_code = None
    try:
        with log_path.open("wb") as log:
            completed = runner(
                command, cwd=repo_root, stdout=log, stderr=subprocess.STDOUT,
                timeout=check["timeout_seconds"], check=False,
                env={**os.environ, "PYTHONUNBUFFERED": "1"},
            )
        return_code = completed.returncode
        if return_code != 0:
            status = "failed"
            reason = f"command exited with status {return_code}"
    except subprocess.TimeoutExpired:
        status = "failed"
        reason = f"command exceeded {check['timeout_seconds']} seconds"
        with log_path.open("ab") as log:
            log.write(("\nACCEPTANCE RUNNER: " + reason + "\n").encode())
    except OSError as exc:
        status = "blocked"
        reason = f"could not execute command: {type(exc).__name__}"
        log_path.write_text(reason + "\n", encoding="utf-8")
    return {
        "id": check["id"], "title": check["title"], "status": status,
        "command": command, "return_code": return_code,
        "duration_seconds": round(time.monotonic() - started, 3),
        "timeout_seconds": check["timeout_seconds"], "reason": reason,
        "log": str(log_path.relative_to(bundle)), "log_sha256": _sha256(log_path),
    }


def run_engine_v2_acceptance(
    repo_root: Path, output_dir: Path, *, source_revision: str = "unknown",
    checks: list[dict[str, Any]] | None = None, runner=subprocess.run,
) -> dict[str, Any]:
    """Run every local gate, checkpoint each result, and preserve its log."""
    repo_root = repo_root.resolve()
    output_dir = output_dir.resolve()
    if not (repo_root / "pyproject.toml").is_file():
        raise ValueError("repo_root must be the WHAXON repository root")
    output_dir.parent.mkdir(parents=True, exist_ok=True)
    output_dir.mkdir(exist_ok=False)
    (output_dir / "logs").mkdir()
    report_path = output_dir / "report.json"
    selected = checks if checks is not None else _checks(output_dir)
    report: dict[str, Any] = {
        "schema_version": "whaxon.engine-v2-acceptance.v1",
        "started_at": _utc_now(), "finished_at": None,
        "source_revision": source_revision,
        "repository": "andreipath26/WHAXON-AI-Forensics",
        "environment": {
            "python_version": platform.python_version(),
            "python_implementation": platform.python_implementation(),
            "platform": platform.platform(), "machine": platform.machine(),
        },
        "checks": [],
        "distribution_artifacts": [],
        "external_gates": [
            {"id": gate_id, "status": status, "required_evidence": description}
            for gate_id, status, description in _EXTERNAL_GATES
        ],
        "internal_status": "running",
        "deployment_decision": "HOLD",
        "limitations": [
            "This local run is not GitHub exact-head CI and covers only the current Python/platform.",
            "This runner does not contact target systems or perform an authorized scanner lab.",
            "Local SHA-256 values detect later file changes only when the digest is retained independently.",
            "A passed internal test/build run does not close any pending external or operator gate.",
        ],
    }
    _write_json_atomic(report_path, report)
    for definition in selected:
        print(f"[engine-v2-acceptance] {definition['id']}: {definition['title']}", flush=True)
        result = _run_check(definition, repo_root=repo_root, bundle=output_dir, runner=runner)
        report["checks"].append(result)
        _write_json_atomic(report_path, report)
        print(f"[engine-v2-acceptance] {result['id']}: {result['status']}", flush=True)
    failed = [item for item in report["checks"] if item["status"] == "failed"]
    blocked = [item for item in report["checks"] if item["status"] == "blocked"]
    report["distribution_artifacts"] = _distribution_artifacts(output_dir / "dist")
    report["internal_status"] = "failed" if failed else "blocked" if blocked else "passed"
    report["finished_at"] = _utc_now()
    report["deployment_decision"] = "HOLD"
    _write_json_atomic(report_path, report)
    report_digest = _sha256(report_path)
    (output_dir / "report.sha256").write_text(
        f"{report_digest}  report.json\n", encoding="ascii",
    )
    print(f"[engine-v2-acceptance] report: {report_path}", flush=True)
    print(f"[engine-v2-acceptance] decision: HOLD ({report['internal_status']})", flush=True)
    return report


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run local Engine V2 release checks and write an evidence bundle."
    )
    parser.add_argument(
        "--repo-root", type=Path,
        default=Path(__file__).resolve().parents[1],
        help="WHAXON repository root (defaults to this script's parent repository)",
    )
    parser.add_argument(
        "--output-dir", type=Path,
        help="new directory for report and full command logs (never overwritten)",
    )
    parser.add_argument(
        "--source-revision",
        help="source SHA supplied by the caller or CI; no Git command is run",
    )
    options = parser.parse_args(argv)
    revision = _source_revision(options.source_revision)
    repo_root = options.repo_root.resolve()
    output_dir = options.output_dir or _default_output_root(repo_root, revision)
    report = run_engine_v2_acceptance(
        repo_root, output_dir, source_revision=revision,
    )
    return 0 if report["internal_status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
