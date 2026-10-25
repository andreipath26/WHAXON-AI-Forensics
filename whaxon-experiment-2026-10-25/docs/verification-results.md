# Verification Results

Verification here means: re-establish each claim with a method that shares as little as possible
with the method that produced it, and check that the claim survives. Where it does not, the claim is
downgraded in `docs/findings.md`.

## 1. Baseline: the repository's own test suite

| Run | Command | Result | Interpretation |
| --- | --- | --- | --- |
| Baseline before any change | `pytest -q` in a fresh venv with `.[dev]` | **15 failed, 627 passed, 74 errors** | failures were missing optional deps (`flask`, `textual`) and a missing Playwright browser |
| After installing `.[dev,web,tui]` | same | **1 failed, 756 passed, 63 errors** | 1 failure = `weasyprint` absent (PDF export); 63 errors = Playwright browser absent |
| Final, after adding this study's tests | same | **1 failed, 779 passed, 63 errors, 14 skipped** | +23 new tests pass; no regression introduced (no `src/` file was modified) |

Classification of the residual failure:
`tests/test_report_ergonomics.py::test_clipboard_refused_for_pdf` → `SystemExit: 1` because
`to_pdf_bytes` requires `weasyprint` on PATH. This is an environment dependency (a system library
requiring root to install), not a defect introduced or hidden by this study.

The 63 errors are all `playwright._impl._errors.Error: Executable doesn't exist` — no browser binary
in the image. They are reported, not skipped silently.

## 2. Independent re-test of the live findings (V1)

`scripts/verify_findings.py` re-tests F1–F6 with `curl` in a separate process: no shared session,
no shared encoding code, literal URL strings, grep over raw bytes.

| Finding | Positive re-established | Negative control clean | Verdict |
| --- | --- | --- | --- |
| F1 LFI | 18 `/etc/passwd` lines | intended include returns no passwd lines | CONFIRMED |
| F2 reflected XSS | `<svg/onload=...>` bytes present, not escaped | inert marker reflected, payload absent | CONFIRMED |
| F3 command injection | `uid=33(www-data)` | benign IP → no `uid`, ping replies present | CONFIRMED |
| F4 phpinfo | PHP version, `DOCUMENT_ROOT`, `display_errors=On` | `/about.php` has no phpinfo markers | CONFIRMED |
| F5 setup exposure | reset control present, DB host disclosed | (presence-only finding; effect not tested) | CONFIRMED (presence) |
| F6 cookie attributes | no `HttpOnly`/`Secure`/`SameSite` | value never recorded | CONFIRMED |

**Common-mode errors that remain.** Both clients use the same OS resolver and the same TLS
termination; a DNS or certificate fault would affect both equally. The TLS chain was inspected
independently with `openssl s_client` (Let's Encrypt `YE2`, CN matches, valid dates), and every
request used certificate verification **on** — failures would have raised.

**What this is not.** This is *method* independence, not *author* independence: one agent designed
both checks. The mitigating controls are (a) matched negatives for every positive, (b) tests that
re-derive the labels from behaviour rather than trusting a case name, and (c) raw artefacts
published for third-party re-checking.

## 3. Verifying the instrument claims (E8–E11)

| Claim | Method | Independent check | Result |
| --- | --- | --- | --- |
| H2 adapter fabricates `status: 200` | read `adapters/ffuf.py`; parse synthetic input | the same fabricated value appears in the repository's own recorded artefact, and is contradicted by a different adapter on the same path | holds |
| H2 severity follows the fabricated status | map `STATUS_KNOWLEDGE` | gobuster grades the same 403 paths `info`; ffuf grades them `low` | holds |
| H3 false `verified` from a marker word | run `Validator.validate` on a decoy | the verdict string itself names the marker: `marker 'postgresql' appeared only after injection` | holds |
| H3 false `verified` from timing | run on a sleeping decoy | the hardened path returns `candidate` for the same server, proving the signal is not sufficient | holds |
| H3 `refuted` on a real injection | run on `sqli_union` | ground truth asserted separately by `tests/test_research_observations.py` (UNION returns rows) | holds |
| H1 redirect escape | two loopback servers, `ToolRunner` | the denied host's own access log records the hit; direct request to the same URL raises `OutOfScopeError` | holds |
| H1 validator does *not* follow redirects | `Validator._fetch` against the redirector | `ValueError: redirect blocked by validator (HTTP 302)` | holds (hypothesis narrowed) |

### Negative results that shaped the conclusions

1. **"Scope can be bypassed with IP encodings"** — **rejected**. Decimal, hex, IPv4-mapped IPv6,
   userinfo and fragment forms are all denied. The write-up does not claim this.
2. **"The validator follows redirects off-scope"** — **rejected**. Both replay paths install
   `NoRedirect`. The escape is limited to tool execution and the operator's own sub-requests.
3. **"The target is a stock DVWA with a login gate"** — **rejected**. Modules execute for anonymous
   clients; `Username: Unknown` appears on every page footer.
4. **"The target's SQLi is exploitable"** — **not demonstrated**, and not claimed. The schema is
   absent; the query never runs.

## 4. Reproducing this study from a clean state

```bash
python3 -m venv .venv && . .venv/bin/activate
pip install -e ".[dev,web,tui]"
pytest -q                                   # expect 779 passed, 1 weasyprint failure, 63 browser errors

bash scripts/env_probe.sh                   # environment evidence
python scripts/validator_benchmark.py       # E8, ~40 s, loopback only
python scripts/scope_experiment.py          # E10/E11, loopback only
python scripts/adapter_fidelity.py          # E9 (live part contacts the target: 14 GETs)
python scripts/live_probe.py                # E5 (18 GETs)
python scripts/exploit_confirm.py           # E6/E7 (8 requests incl. `id`)
python scripts/verify_findings.py           # V1 (8 requests, curl)
python scripts/build_manifest.py            # hashes for evidence/manifest.json
```

Loopback-only experiments (E8, E10/E11) run without contacting the target and reproduce every
quantitative claim in `docs/findings.md` about the instrument. Only the live scripts touch
`pentest-ground.com`.

## 5. Checks that could not be run

| Check | Blocker |
| --- | --- |
| Browser-executed XSS proof (DOM) | no Playwright browser binary; `playwright install` needs network + ~150 MB and was not required for the context-based claim |
| SQL injection reproduction | target database uninitialised (H6) |
| PDF report fidelity | `weasyprint` absent |
| End-to-end scanner orchestration | `nmap`/`nikto`/`ffuf` absent, installation impossible |
