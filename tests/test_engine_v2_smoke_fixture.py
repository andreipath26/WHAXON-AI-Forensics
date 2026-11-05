"""The SQLmap loopback oracle must distinguish multi-condition probes."""
from __future__ import annotations

import runpy
from pathlib import Path

_SMOKE = runpy.run_path(str(Path(__file__).with_name("smoke_external_tools.py")))
_ORACLE = _SMOKE["_sqlmap_boolean_oracle"]


def test_boolean_oracle_accepts_multiple_true_conjuncts():
    assert _ORACLE("1 AND 123=123 AND 456=456") == b"Product: fixture-item\n"


def test_boolean_oracle_rejects_false_later_conjunct():
    assert _ORACLE("1 AND 123=123 AND 456=457") == b"No products found\n"


def test_boolean_oracle_leaves_non_boolean_lookup_stable():
    assert _ORACLE("1") == b"Product: fixture-item\n"


def test_boolean_oracle_handles_whitespace_around_comparisons():
    assert _ORACLE("1 AND 123 = 123 AND 456 = 457") == b"No products found\n"
