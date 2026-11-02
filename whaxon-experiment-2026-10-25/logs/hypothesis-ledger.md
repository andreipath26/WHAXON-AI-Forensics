# Hypothesis Ledger

Lifecycle record. Every hypothesis is kept, including rejected ones; nothing is deleted because a
later result superseded it. Status values: proposed, testing, supported, partially supported,
rejected, blocked, unresolved.

| ID | Hypothesis (short) | Proposed | Test | Status | Evidence | Note |
| --- | --- | --- | --- | --- | --- | --- |
| H0 | Security tools (nmap/ffuf/…) are preinstalled in the runner | 11:38Z | environment sweep | **rejected** | `logs/tool-inventory.md` | zero of nine present |
| H0b | `apt install` can add them | 11:44Z | `sudo -n true` | **rejected** | `evidence/env/environment.json` | no caps, `no_new_privileges` |
| H1a | The validator follows redirects off-scope | 11:45Z | code read + `_fetch` probe | **rejected** | both paths install `NoRedirect`; `ValueError: redirect blocked` | narrowed to H1b/H1c |
| H1b | Scope authorises a name without binding its resolved address | 11:52Z | E10 DNS probe | **supported** | `evidence/scope/decision-matrix.json` | name allowed, both A records denied |
| H1c | A permitted target's redirect moves tool traffic to a denied host | 12:10Z | E11 two-address test | **supported** | `evidence/scope/redirect-escape.json` | denied host's log records the hit |
| H1d | Scope is bypassable via alternative IP encodings (decimal/hex/IPv4-mapped/userinfo) | 11:52Z | E10 matrix | **rejected** | 14-form matrix | string layer is sound; not claimed anywhere |
| H2 | ffuf adapter invents `status: 200` when output has none | 11:45Z | E9 synthetic | **supported** | `adapters/ffuf.py` + `fidelity.json` | severity ladder follows the invented value |
| H2b | The repository's shipped artefact contains the same invention | 11:45Z | E9 artefact parse | **supported** | 12/12 ffuf findings status 200, size null | 9/12 disagree with gobuster |
| H2c | Deduplication hides cross-tool contradiction | 12:16Z | E9 unique_findings analysis | **supported** | `merged_unique_finding_sources` | keeps first-ingested tool's data |
| H3a | `verified` can be produced without exploitability (marker) | 12:10Z | E8 `marker_decoy` | **supported** | both paths | reason names the marker word |
| H3b | `verified` can be produced without exploitability (timing) | 12:10Z | E8 `timing_decoy` | **supported** (legacy path only) | legacy `verified`, context `candidate` | README already admits the risk; now quantified |
| H3c | Genuinely exploitable cases are labelled `refuted` | 12:10Z | E8 `sqli_union` | **supported** | `results.json` | over-claimed negative |
| H3d | Replayed payload selection is defective (index 0 is documentation) | 12:14Z | `PayloadLoader` inspection | **supported** | sqli `` `+HERP ``; lfi/cmdi `<?php` | 4 of 6 kinds inspected |
| H3e | Some exploitable classes can never be verified (LFI, POST-only) | 12:10Z | code + benchmark | **supported** | `REPLAYABLE`, method allowlist | structural, not a bug per se |
| H4 | Live command injection yields `www-data`, not root | 12:03Z | E6 + V1 | **supported** | `uid=33(www-data)` twice | root not attempted |
| H4b | `www-data` → root on the target | — | — | **not attempted** | `docs/privilege-boundary-assessment.md` §5 | outside authorised ceiling |
| H5 | Deployment serves DVWA modules unauthenticated | 11:57Z | E5 + V1 | **supported** | 6/6 re-confirmed with cookieless curl | root cause undiagnosed |
| H6 | Target DVWA database is uninitialised | 11:52Z | login redirect + fatal error | **supported** | `Table 'dvwa.users' doesn't exist` | blocks stateful tests |
| H7 | WHAXON would mark a real DVWA SQLi `verified` | 11:52Z | E8 proxy case | **unresolved / contradicted on benchmark** | `sqli_low` → `candidate` | live test blocked by H6 |
| H8 | Resolver-pinned scope + no-timing-verified would improve soundness | 12:30Z | natural experiment between the two existing paths | **unresolved (observational only)** | FPR 0.167 vs 0.333 | not an intervention trial |
| H9 | My benchmark emulator is correct | 12:12Z | cross-check against canary format | **rejected twice, then fixed** | `logs/errors-and-blockers.md` B-007 | two emulator bugs found and corrected before reporting |

## Ledger notes

- H1a and H1d are the two hypotheses whose rejection most improved the study: both would have been
  easy "findings" to publish and both are false.
- H7 is deliberately left unresolved rather than inferred from the benchmark: the benchmark
  reproduces DVWA's *error text*, not DVWA's *query construction*.
- H9 exists because the study's own instrument was wrong twice; recording it prevents the
  benchmark's numbers from being treated as oracle output.
