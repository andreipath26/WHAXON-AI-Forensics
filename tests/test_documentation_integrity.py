"""Prevent obsolete source/test references in canonical Engine V2 ledgers."""
from __future__ import annotations

import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LEDGERS = (
    ROOT / "docs/ENGINE_V2_ROADMAP_REQUIREMENTS.csv",
    ROOT / "docs/ENGINE_V2_AUDIT_CHECKPOINTS_2026-11-03.csv",
)
PATH = re.compile(r"(?:docs|src|tests|scripts)/[A-Za-z0-9_./-]+\.(?:md|csv|py)")


def test_acceptance_ledgers_reference_existing_repository_files():
    missing = []
    for ledger in LEDGERS:
        with ledger.open(newline="", encoding="utf-8") as handle:
            for row in csv.DictReader(handle):
                key = row.get("requirement_id") or row.get("checkpoint_id")
                for field in ("implementation_candidate", "test_candidate",
                              "source_paths", "related_test_definition"):
                    for path in PATH.findall(row.get(field, "") or ""):
                        if not (ROOT / path).is_file():
                            missing.append(f"{ledger.name}:{key}:{field}:{path}")
    assert not missing, "Stale file references in acceptance ledgers:\n" + "\n".join(missing)


def test_roadmap_ledger_has_75_unique_entries():
    with LEDGERS[0].open(newline="", encoding="utf-8") as handle:
        entries = list(csv.DictReader(handle))
    ids = [row["requirement_id"] for row in entries]
    assert len(ids) == len(set(ids)) == 75
    assert all(row["acceptance"] in {"ACCEPTED", "NOT_ACCEPTED"} for row in entries)
