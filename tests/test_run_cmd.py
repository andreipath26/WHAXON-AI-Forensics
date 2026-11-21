"""Tests for whaxon.interfaces.cli.run_cmd.

Runs the CLI entry point directly against a temp data dir. Uses the
`echo` catalog tool as the "real run" case. The packaged catalog
provides it and produces predictable output.
"""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from whaxon.interfaces.cli import run_cmd


def _seed_data_dir(tmp_path: Path) -> Path:
    """Copy the packaged tools.json into tmp_path so the catalog has tools."""
    repo_data = Path(__file__).resolve().parents[1] / "src" / "whaxon" / "data"
    if (repo_data / "tools.json").exists():
        shutil.copy(repo_data / "tools.json", tmp_path / "tools.json")
    return tmp_path


# ---------------------------------------------------------------- validation

def test_no_args_prints_usage(capsys):
    run_cmd.main([])
    out = capsys.readouterr().out
    assert "Usage: whaxon run" in out


def test_help_prints_usage(capsys):
    run_cmd.main(["--help"])
    out = capsys.readouterr().out
    assert "Usage: whaxon run" in out


def test_missing_target_exits_usage(tmp_path, capsys):
    _seed_data_dir(tmp_path)
    with pytest.raises(SystemExit) as ei:
        run_cmd.main(["echo", "--data", str(tmp_path)])
    assert ei.value.code == run_cmd.EXIT_USAGE


def test_unknown_tool_exits_3(tmp_path, capsys):
    _seed_data_dir(tmp_path)
    with pytest.raises(SystemExit) as ei:
        run_cmd.main(["definitely-not-a-tool", "127.0.0.1",
                      "--data", str(tmp_path)])
    assert ei.value.code == run_cmd.EXIT_UNKNOWN_TOOL
    err = capsys.readouterr().err
    assert "unknown tool" in err
    assert "available:" in err


def test_unknown_flag_exits_usage(tmp_path, capsys):
    _seed_data_dir(tmp_path)
    with pytest.raises(SystemExit) as ei:
        run_cmd.main(["echo", "127.0.0.1", "--bogus-flag",
                      "--data", str(tmp_path)])
    assert ei.value.code == run_cmd.EXIT_USAGE


def test_bad_timeout_value_exits_usage(tmp_path, capsys):
    _seed_data_dir(tmp_path)
    with pytest.raises(SystemExit) as ei:
        run_cmd.main(["echo", "127.0.0.1", "--timeout", "not-a-number",
                      "--data", str(tmp_path)])
    assert ei.value.code == run_cmd.EXIT_USAGE


# ---------------------------------------------------------------- retired direct dispatch

@pytest.mark.parametrize("legacy_args", [
    ["--legacy"],
    ["--legacy", "--quiet", "--json"],
    ["--legacy", "--extra", "-sV"],
])
def test_legacy_run_is_retired_without_creating_core_or_job(
    tmp_path, monkeypatch, capsys, legacy_args,
):
    def forbidden_core(*args, **kwargs):
        raise AssertionError("retired legacy path must stop before Core creation")

    monkeypatch.setattr(run_cmd, "Core", forbidden_core)
    with pytest.raises(SystemExit) as exc:
        run_cmd.main(["echo", "127.0.0.1", *legacy_args, "--data", str(tmp_path)])

    assert exc.value.code == run_cmd.EXIT_USAGE
    assert "legacy direct tool execution is retired" in capsys.readouterr().err
