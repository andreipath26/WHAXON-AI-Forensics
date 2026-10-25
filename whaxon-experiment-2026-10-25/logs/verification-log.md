# Verification Log

Chronological record of every verification action, its command, and its result. Failures are kept.

## 2026-10-25T11:47Z — Baseline suite (pre-change)

```
python -m pytest -q            # venv with .[dev]
→ 15 failed, 627 passed, 14 skipped, 74 errors
```
Cause of failures/errors: missing `flask` (19 errors), missing `textual` (import-time errors),
missing Playwright browser (63 errors), and 15 `test_recon` failures downstream of the missing
web extra. Classification: environment.

## 11:50Z — Baseline suite (full extras)

```
pip install -e ".[dev,web,tui]"
python -m pytest -q
→ 1 failed, 756 passed, 14 skipped, 63 errors
```
The single failure: `tests/test_report_ergonomics.py::test_clipboard_refused_for_pdf` →
`SystemExit: 1` from `to_pdf_bytes` because `weasyprint` is not on PATH.
All 63 errors: `playwright ... Executable doesn't exist`. **Baseline frozen here.**

## 11:53Z — Environment reproducibility check

```
bash scripts/env_probe.sh   # run twice
jq -e . evidence/env/environment.json   # exit 0
```
Second run reproduced all values (target size 5930 B both runs; timing differs as expected).
The script's own first version failed (B-003); the failure and the fix are recorded.

## 12:12Z — Benchmark emulator validation (found two bugs)

Before scoring WHAXON, the benchmark's own claims were checked against the payload format it must
honour. Two defects found in the emulator (B-007): canary hex decoded as bytes instead of used
literally; POST-only sink executed on GET. Both fixed, then re-run. **The numbers reported in
`docs/research-contribution.md` come only from the corrected emulator.**

## 12:19Z — Benchmark run (corrected)

```
python scripts/validator_benchmark.py
```
Legacy path: TP 2, FP 2, FN 4, TN 4 (TPR .333, FPR .333, precision .500, J .000).
Context path: TP 2, FP 1, FN 4, TN 5 (TPR .333, FPR .167, precision .667, J .167).
Spot-checked verdict reasons, e.g. `marker 'postgresql' appeared only after injection` on a page
that cannot be injected.

## 12:19Z — Scope experiments

```
python scripts/scope_experiment.py
```
Matrix: 14/14 forms classified; all encoding tricks denied; `example.com` allowed while both
A records denied by the same ruleset. Escape: denied host `127.0.0.2` recorded one request;
direct request to the same URL raised `OutOfScopeError`; `Validator._fetch` raised
`ValueError: redirect blocked by validator (HTTP 302)`.

## 12:22Z — Independent client re-test (V1)

```
python scripts/verify_findings.py
→ 6/6 CONFIRMED (F1 LFI, F2 XSS, F3 cmdi, F4 phpinfo, F5 setup presence, F6 cookie attributes)
```
Each with a matched negative control. `curl` version recorded in the JSON artefact.

## 12:27Z — Characterisation tests

```
python -m pytest -q tests/test_research_observations.py
→ 23 passed
```

## 12:30Z — Full suite (post-change)

```
python -m pytest -q
→ 1 failed, 779 passed, 14 skipped, 63 errors
```
Delta vs baseline: **+23 passed** (the new tests), everything else identical. No `src/whaxon/**`
file was modified by this study (`git diff --stat` shows only added documentation, scripts,
experiments, tests and evidence).

## Verification gaps (reported, not hidden)

| Gap | Reason |
| --- | --- |
| Browser-executed XSS | no browser binary; `playwright install` would add ~150 MB and is not required for a context-based claim |
| SQL injection on the target | target DB uninitialised |
| Author-independent replication | single agent; mitigated by behavioural label tests and published artefacts, not eliminated |
| Root on target | not authorised |

## 12:40Z — Clean-state reproducibility re-run (independent of the original run)

The original benchmark and scope evidence was moved aside (`/tmp/bench_prev`, `/tmp/scope_prev`) and
both experiments were re-executed from scratch, so the second run could not read the first run's
output:

```
python scripts/validator_benchmark.py   # exit 0
python scripts/scope_experiment.py      # exit 0
```

| Comparison | First run | Re-run | Verdict |
| --- | --- | --- | --- |
| legacy path TP/FP/FN/TN | 2/2/4/4 | 2/2/4/4 | identical |
| context path TP/FP/FN/TN | 2/1/4/5 | 2/1/4/5 | identical |
| scope escape via `ToolRunner` | True | True | identical |
| validator redirect defence | `ValueError: redirect blocked by validator` | same | identical |

What this does and does not show: it shows the measurements are deterministic on this host, not
that they are correct — correctness rests on the behavioural label tests and the matched controls.
Evidence files were regenerated (new timestamps), so `evidence/manifest.json` was rebuilt in the
same commit.

## 2026-10-25T12:36Z — Hash manifest

```
python scripts/build_manifest.py
```
Writes `evidence/manifest.json` with identifier, description, timestamp, SHA-256, classification and
the experiment each artefact belongs to. Re-running the manifest after any evidence change is part
of the reproduction recipe.

Post-redaction sanitisation check: **clean** (after fixing the checker itself to match *values*
rather than the placeholder text — see `scripts/build_manifest.py`).
