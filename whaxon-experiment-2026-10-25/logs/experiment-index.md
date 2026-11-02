# Experiment Index

Every experiment with its question, runner, artefacts, and reproducibility class.
`loopback` = needs no target; `live` = contacts `pentest-ground.com:4280`.

| ID | Question | Runner | Artefacts | Class | Hypotheses |
| --- | --- | --- | --- | --- | --- |
| E0 | What is the runner capable of? | `scripts/env_probe.sh` | `evidence/env/environment.json`, `probe.log`, `target_root.headers`, `target_root.html` | loopback + 3 benign GETs | H0, H0b |
| E1 | Which scope forms are allowed, and is DNS consulted? | `scripts/scope_experiment.py` (matrix part) | `evidence/scope/decision-matrix.json` | loopback | H1b, H1d |
| E2 | Do adapters record only observed fields? | `scripts/adapter_fidelity.py` (synthetic + artefact parts) | `evidence/adapters/fidelity.json` | loopback | H2, H2b, H2c |
| E3 | Is replay verification sound and complete? | `scripts/validator_benchmark.py` + `experiments/benchmark/server.py` | `evidence/benchmark/results.json`, `confusion.json`, `access-log.jsonl` | loopback | H3a–H3e |
| E4 | What is exposed before authentication? | `scripts/live_probe.py` | `evidence/live/routes.json`, `request-log.jsonl`, route bodies | live (18 GETs) | H5, H6 |
| E5 | Are LFI/XSS/command-injection real, with controls? | `scripts/exploit_confirm.py` | `evidence/live/confirm.json`, `*.body` | live (8 requests) | H4, H5 |
| E6 | Does adapter output match live truth for the same paths? | `scripts/adapter_fidelity.py` (live part) | `evidence/adapters/fidelity.json` (`live_status_measurement`, adjudication) | live (14 GETs) | H2b |
| E7 | Does an in-scope redirect reach an out-of-scope host? | `scripts/scope_experiment.py` (escape part) | `evidence/scope/redirect-escape.json` | loopback | H1c |
| V1 | Do the live findings survive a different HTTP client? | `scripts/verify_findings.py` | `evidence/verification/verification.json` + `*.body` | live (8 requests, curl) | all live |
| V2 | Do the instrument claims survive targeted tests? | `pytest tests/test_research_observations.py` | 23 passing tests | loopback | H2, H3, H4, H1b, H1c, H1d |
| V3 | Is the repository's suite still green? | `pytest -q` | 779 passed, 1 env failure, 63 env errors | loopback | regression guard |

## Artefact → claim map

| Artefact | Supports |
| --- | --- |
| `evidence/env/environment.json` | every statement in `docs/environment-report.md` |
| `evidence/scope/decision-matrix.json` | H1b (name-not-address), H1d (string layer sound) |
| `evidence/scope/redirect-escape.json` | H1c; the negative control (`direct_out_of_scope_run`) and the validator defence |
| `evidence/adapters/fidelity.json` | H2, H2b, H2c; live truth table for 12 paths |
| `evidence/benchmark/results.json` | per-case verdicts and reasons (quotable lines such as `marker 'postgresql' appeared only after injection`) |
| `evidence/benchmark/confusion.json` | R1 metrics |
| `evidence/benchmark/access-log.jsonl` | proof the validator actually contacted the cases it scored |
| `evidence/live/routes.json` | F1–F8 surface map, including the `Username: Unknown` observation |
| `evidence/live/request-log.jsonl` | full request accounting, sanitised cookies |
| `evidence/live/confirm.json` | F1–F3 verdicts with matched controls |
| `evidence/verification/verification.json` | independent re-confirmation of F1–F6 |

## Experiments designed but not run

| ID | Why not |
| --- | --- |
| E8-live | SQLi/statefulness blocked by B-006 |
| E9-orchestration | nmap/nikto/ffuf absent (B-001, B-002) |
| E12-browser | no Chromium/Playwright browser |
| E13-privesc | not authorised (scope §4) |
