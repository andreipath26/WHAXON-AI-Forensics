"""E8 — measure WHAXON's replay validator against labeled ground truth.

Two questions
-------------
Q1 (soundness): when the validator says `verified`, is the case actually
    exploitable, and when it says `refuted`, is the case actually safe?
Q2 (completeness): which confirmed-exploitable cases can the validator never
    verify because no replay path exists for them?

Method
------
* Start the labeled local benchmark (`experiments/benchmark/server.py`).
* For each case, construct the `Finding` a scanner would have produced and call
  WHAXON's **own** `Validator` in-process — no reimplementation.
* Run it twice where possible: the legacy query-parameter path
  (`data.parameter`) and the hardened context path (`data._request_context`,
  the "C-03" path), so the two code paths can be compared on identical input.
* Score `verified` as a positive prediction against ground truth, then compute
  TP/FP/FN/TN, TPR, FPR, precision and Youden's J = TPR - FPR.

Outputs
-------
evidence/benchmark/results.json                 every verdict with its reason
evidence/benchmark/confusion.json               metrics per path
evidence/benchmark/access-log.jsonl             what the validator really contacted
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from whaxon.core.findings import Finding                     # noqa: E402
from whaxon.core.validator import Validator                   # noqa: E402
from experiments.benchmark.server import CASES, serve         # noqa: E402

PAYLOADS = ROOT / "src" / "whaxon" / "data" / "payloads"
OUT = ROOT / "evidence" / "benchmark"


def metrics(rows: list[dict]) -> dict:
    tp = sum(1 for r in rows if r["truth"] and r["predicted_positive"])
    fp = sum(1 for r in rows if not r["truth"] and r["predicted_positive"])
    fn = sum(1 for r in rows if r["truth"] and not r["predicted_positive"])
    tn = sum(1 for r in rows if not r["truth"] and not r["predicted_positive"])
    tpr = tp / (tp + fn) if (tp + fn) else None
    fpr = fp / (fp + tn) if (fp + tn) else None
    precision = tp / (tp + fp) if (tp + fp) else None
    youden = (tpr - fpr) if (tpr is not None and fpr is not None) else None
    return {"tp": tp, "fp": fp, "fn": fn, "tn": tn,
            "tpr_recall": tpr, "fpr": fpr, "precision": precision, "youden_j": youden,
            "n": len(rows)}


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "access-log.jsonl").unlink(missing_ok=True)
    srv = serve(0)
    port = srv.server_address[1]
    base = f"http://127.0.0.1:{port}"
    print(f"benchmark server on {base}\n")

    validator = Validator(PAYLOADS, timing_threshold=3.0)
    results = []
    for case, spec in CASES.items():
        url = f"{base}/{case}"
        kind, param = spec["kind"], spec["param"]

        # --- path A: legacy query-parameter replay -------------------------
        f_legacy = Finding(kind=kind, severity="info", source="benchmark",
                           data={"parameter": param}, raw_line=case)
        status_a, reason_a = validator.validate(f_legacy, target_url=url)

        # --- path B: hardened request-context replay ------------------------
        ctx = {"method": spec["method"], "url": f"{url}?{param}=1",
               "parameter": param, "headers": {"User-Agent": "whaxon-bench/1"}}
        if spec["method"] == "POST":
            ctx["body"] = f"{param}=1"
        f_ctx = Finding(kind=kind, severity="info", source="benchmark",
                        data={"parameter": param, "_request_context": ctx}, raw_line=case)
        status_b, reason_b = validator.validate(f_ctx, target_url=url)

        results.append({
            "case": case, "kind": kind, "method": spec["method"], "url": url,
            "ground_truth_vulnerable": spec["vulnerable"], "note": spec["note"],
            "cwe": spec["cwe"],
            "legacy_path": {"status": status_a, "reason": reason_a,
                            "predicted_positive": status_a == "verified"},
            "context_path": {"status": status_b, "reason": reason_b,
                             "predicted_positive": status_b == "verified"},
        })
        print(f"{case:20s} truth={str(spec['vulnerable']):5s} "
              f"legacy={status_a:9s} ctx={status_b:9s}")

    legacy_rows = [{"truth": r["ground_truth_vulnerable"],
                    **r["legacy_path"]} for r in results]
    ctx_rows = [{"truth": r["ground_truth_vulnerable"],
                 **r["context_path"]} for r in results]

    summary = {
        "experiment": "E8-validator-benchmark",
        "validator_module": "whaxon.core.validator",
        "timing_threshold_s": validator.timing_threshold,
        "legacy_query_param_path": metrics(legacy_rows),
        "context_replay_path": metrics(ctx_rows),
        "cases": len(results),
        "notes": [
            "predicted_positive = validator reported 'verified'",
            "ground truth asserted independently in tests/test_benchmark_labels.py",
            "a 'refuted' verdict on a truly vulnerable case is a completeness failure, "
            "counted here as a false negative",
        ],
    }
    (OUT / "results.json").write_text(json.dumps(
        {"experiment": summary["experiment"], "base": base, "results": results},
        indent=2), encoding="utf-8")
    (OUT / "confusion.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print("\n" + json.dumps({k: v for k, v in summary.items() if k != "notes"}, indent=2))
    srv.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
