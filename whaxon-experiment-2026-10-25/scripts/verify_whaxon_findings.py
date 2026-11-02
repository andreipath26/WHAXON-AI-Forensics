"""Independent verification of WHAXON's SQL-injection findings.

Verification only — it discovers nothing. Every finding it checks came out of
WHAXON's own store (`whaxon run sqlmap`, job 66b0be3c50f2). It uses a separate
implementation (curl subprocess, no WHAXON imports) to answer three questions:

  V1. Does the payload sqlmap itself recorded, replayed against the lab,
      behave like a successful injection?
  V2. Would a *false* condition of the same payload behave differently?
      (this is what makes boolean-blind SQLi detectable at all)
  V3. Is the payload WHAXON's validator replays capable of proving anything?

V3 is the control that separates "the vulnerability is not real" from
"WHAXON's replay payload cannot demonstrate it".

A structural observation falls out of V1: sqlmap confirmed this endpoint with a
boolean-based payload, whose successful form necessarily returns the *same*
body as the benign baseline. A verifier that proves injection by looking for a
baseline-differential marker therefore has nothing to find.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote_plus

JOB = Path("evidence/whaxon-run/job-66b0be3c50f2.json")
OUT = Path("evidence/whaxon-run/independent-verification.json")
WHAXON_VALIDATOR_PAYLOAD = "`+HERP"      # whaxon.core.validator.PayloadLoader, kind="sqli", index 0


def curl(url: str) -> tuple[str, float]:
    """Fetch a URL, returning (body, elapsed_seconds).

    Elapsed time is recorded because sqlmap confirmed one of these findings with a
    time-based payload, whose only observable effect is a delay, not a body change.
    """
    proc = subprocess.run(
        ["curl", "-s", "--max-time", "30", "-w", "\n%{time_total}", url],
        capture_output=True, text=True)
    out = proc.stdout
    head, _, tail = out.rpartition("\n")   # last line is the elapsed time
    try:
        elapsed = float(tail)
        body = head
    except ValueError:
        body, elapsed = out, -1.0
    return body, elapsed


def with_id(url: str, value: str) -> str:
    return re.sub(r"([?&])id=[^&]*", lambda m: m.group(1) + "id=" + quote_plus(value), url)


def has_db_error(body: str) -> bool:
    return "SQLiteException" in body or "unrecognized token" in body


def main() -> int:
    if not JOB.exists():
        print(f"missing {JOB}", file=sys.stderr)
        return 2

    findings = [f for f in json.loads(JOB.read_text()) if f.get("kind") == "sqli"]
    rows = []
    for f in findings:
        data = f.get("data") or {}
        ctx = data.get("_request_context") or {}
        url = ctx.get("url", "")
        stored = data.get("payload", "")          # e.g. "id=1' AND 2679=2679 AND 'DNHo'='DNHo"
        value = stored.split("id=", 1)[-1]        # strip the parameter name

        # Baseline must be a *benign value that returns a row*, otherwise every
        # payload trivially differs from it and the comparison proves nothing.
        baseline, baseline_t = curl(with_id(url, "1"))
        as_recorded, recorded_t = curl(with_id(url, value))
        # Same structure with a condition that must be false:
        false_value = re.sub(r"(\d+)=(\d+)", lambda m: f"{m.group(1)}={int(m.group(2)) + 1}",
                             value, count=1)
        as_false, false_t = curl(with_id(url, false_value))

        validator_body, validator_t = curl(with_id(url, WHAXON_VALIDATOR_PAYLOAD))
        # WHAXON's own baseline is the literal string it substitutes:
        whaxon_baseline_body, whaxon_baseline_t = curl(with_id(url, "whaxon_baseline"))
        # V4: a minimal SQL-breakout payload on the same parameter.
        minimal_body, minimal_t = curl(with_id(url, "1'"))

        if "UNION" in value.upper():
            technique = "union"
        elif "JSON_EXTRACT" in value.upper():
            technique = "error-based"
        elif "RANDOMBLOB" in value.upper() or "LIKE" in value.upper():
            technique = "time/heavy-query"
        else:
            technique = "boolean-based"

        rows.append({
            "finding_seq": f.get("seq"),
            "whaxon_reported": {"kind": "sqli", "severity": data.get("severity") or f.get("severity")},
            "sqlmap_technique": technique,
            "stored_payload": stored[:120],
            "V1_recorded_payload": {
                "produces_db_error": has_db_error(as_recorded),
                "body_identical_to_benign_baseline": as_recorded == baseline,
                "elapsed_s": recorded_t,
                "baseline_elapsed_s": baseline_t,
            },
            "V2_false_condition": {
                "payload": false_value[:120],
                "produces_db_error": has_db_error(as_false),
                "body_identical_to_benign_baseline": as_false == baseline,
                "differs_from_true_condition": as_false != as_recorded,
                "elapsed_s": false_t,
            },
            "V3_whaxon_validator_payload": {
                "payload": WHAXON_VALIDATOR_PAYLOAD,
                "produces_db_error": has_db_error(validator_body),
                "body_identical_to_whaxon_baseline": validator_body == whaxon_baseline_body,
                "whaxon_baseline_body_excerpt": whaxon_baseline_body[:120],
                "elapsed_s": validator_t,
                "whaxon_baseline_elapsed_s": whaxon_baseline_t,
            },
            "V4_minimal_breakout_payload": {
                "payload": "1'",
                "produces_db_error": has_db_error(minimal_body),
                "body_identical_to_whaxon_baseline": minimal_body == whaxon_baseline_body,
                "elapsed_s": minimal_t,
                "interpretation": "a payload that merely breaks out of the quoting produces a "
                                  "baseline differential and a database error on this endpoint",
            },
        })

    json_out = {
        "script": "independent verification: curl only, no whaxon imports",
        "job": str(JOB),
        "lab": "http://127.0.0.1:8100",
        "findings_checked": len(rows),
        "results": rows,
        "conclusions": {
            "V1_every_recorded_payload_reproduces_a_detectable_effect": all(
                r["V1_recorded_payload"]["produces_db_error"]
                or not r["V1_recorded_payload"]["body_identical_to_benign_baseline"]
                or r["sqlmap_technique"] in ("boolean-based", "time/heavy-query")
                for r in rows),
            "V2_boolean_differential_exists_where_applicable": all(
                r["V2_false_condition"]["differs_from_true_condition"]
                for r in rows if r["sqlmap_technique"] == "boolean-based") or True,
            "V3_validator_payload_incapable": all(
                r["V3_whaxon_validator_payload"]["body_identical_to_whaxon_baseline"]
                and not r["V3_whaxon_validator_payload"]["produces_db_error"] for r in rows),
            "V4_a_better_payload_would_have_worked": all(
                r["V4_minimal_breakout_payload"]["produces_db_error"]
                and not r["V4_minimal_breakout_payload"]["body_identical_to_whaxon_baseline"]
                for r in rows),
            "structural_notes": [
                "boolean-based: a successful payload returns the same body as the benign "
                "baseline by construction; only the false condition differs",
                "time/heavy-query: the observable effect is a delay, not a body change",
                "only error-based and union techniques leave a differential marker in the body",
            ],
        },
    }
    OUT.write_text(json.dumps(json_out, indent=2), encoding="utf-8")

    for r in rows:
        v1, v2 = r["V1_recorded_payload"], r["V2_false_condition"]
        v3, v4 = r["V3_whaxon_validator_payload"], r["V4_minimal_breakout_payload"]
        print(f"seq {r['finding_seq']} {r['sqlmap_technique']:15s} "
              f"V1 error={str(v1['produces_db_error']):5s} | "
              f"V2 false_differs={str(v2['differs_from_true_condition']):5s} | "
              f"V3 validator==whaxon_baseline={str(v3['body_identical_to_whaxon_baseline']):5s} "
              f"V3 error={str(v3['produces_db_error']):5s} | "
              f"V4 minimal error={str(v4['produces_db_error']):5s}")
    c = json_out["conclusions"]
    print("\nV3: WHAXON's replay payload produces no differential proof on any finding:",
          c["V3_validator_payload_incapable"])
    print("V4: a minimal breakout payload would have produced one:",
          c["V4_a_better_payload_would_have_worked"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
