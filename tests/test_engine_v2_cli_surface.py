"""Keep the top-level CLI help aligned with dispatched command modes."""
from __future__ import annotations

import ast
import re
from pathlib import Path

from whaxon import cli


def test_every_dispatched_top_level_mode_is_listed_in_help(monkeypatch, capsys):
    source = Path(cli.__file__).read_text(encoding="utf-8")
    tree = ast.parse(source)
    modes: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Compare) or not isinstance(node.left, ast.Name):
            continue
        if node.left.id != "mode":
            continue
        for comparator in node.comparators:
            try:
                values = ast.literal_eval(comparator)
            except (ValueError, TypeError):
                continue
            if isinstance(values, str):
                values = (values,)
            if isinstance(values, tuple):
                modes.update(
                    value for value in values
                    if isinstance(value, str) and not value.startswith("-")
                )

    monkeypatch.setattr("sys.argv", ["whaxon", "--help"])
    cli.main()
    help_text = capsys.readouterr().out
    listed = set(re.search(r"Usage: whaxon \[([^]]+)\]", help_text).group(1).split("|"))

    assert modes <= listed, f"dispatched modes missing from --help: {modes - listed}"
