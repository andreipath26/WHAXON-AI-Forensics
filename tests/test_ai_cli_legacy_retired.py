"""Legacy AI CLI entry points fail closed before touching state or providers."""
from __future__ import annotations

import pytest

from whaxon.interfaces.cli import ai_cmd


@pytest.mark.parametrize("args", [
    ["--legacy", "scan 127.0.0.1"],
    ["--legacy", "--auto", "scan 127.0.0.1"],
    ["--resume", "ai-old", "--answer", "yes"],
])
def test_legacy_ai_dispatch_and_resume_are_retired_before_state_access(
    args, tmp_path, monkeypatch, capsys,
):
    def forbidden(*_args, **_kwargs):
        raise AssertionError("retired AI command must stop before accessing state")

    monkeypatch.setattr(ai_cmd, "Core", forbidden)
    monkeypatch.setattr(ai_cmd, "build_executor", forbidden)
    monkeypatch.setenv("WHAXON_AI_AUTO_ALLOW", "true")

    with pytest.raises(SystemExit) as exc:
        ai_cmd.main([*args, "--data", str(tmp_path)])

    assert exc.value.code == 2
    assert "legacy autonomous AI execution and resume are retired" in capsys.readouterr().err
    assert list(tmp_path.iterdir()) == []
