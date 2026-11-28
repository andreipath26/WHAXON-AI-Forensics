# Engine V2 deployment readiness audit — 2026-11-28

## Decision

**HOLD — NOT READY TO DEPLOY.** The code candidate is `9b4b2417fa37557e7d726905dec39d93716234d8`. Exact main CI [run #46157672540](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/46157672540) passed **21/21 jobs**, and README freeze [run #46157672587](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/46157672587) passed. This is strong internal engineering evidence, not release qualification.

No real target was tested. No independent security/evidence reviewer, manual UI acceptance, production operator-host exercise, or operator deployment authorization is recorded. No V2 release tag or PyPI publication exists. Keep the release held.

## G01–G10 disposition

| Gate | Evidence now in the repository | Remaining work | State |
|---|---|---|---|
| G01 — inventory and end-to-end workflow | P0 inventory reconciles 33 CLI mode rows, 115 API method/path/handler bindings, 24 catalog IDs, adapter dispositions and direct effect callsites. The controlled G01 lab passed on exact CI; provider loopback smoke artifacts were retained. | Complete release-candidate end-to-end acceptance across the declared supported paths and host. Static census and a bounded lab chain do not prove all paths or external-target behavior. | OPEN |
| G02 — authorization and execution | PR #274 rejects credential/malformed URLs and covers dispatch-time revocation. PR #281 covers cross-origin verifier redirects, cancellation before dispatch, and fail-closed dispatch audit insertion. PR #283 adds context sanitization, full origin matching, and proxy isolation. | Cover all original/redirect/DNS-resolved/secondary request paths, pivots, sessions and worker/cancellation races; prove external-tool egress restrictions and independent deterministic permission enforcement. | OPEN |
| G03 — independent verification | PR #283 adds malformed-context, same-origin, proxy and stale-proof regressions; source seals are preserved and verifier evidence is separately persisted. Existing outcome logic keeps failures/conclusive proof conservative. | Complete supported verification/retest matrix and independent target-side acceptance. Connection failure, timeouts and timing signals remain non-proof; broad verification behavior has not been qualified. | OPEN |
| G04 — evidence and coverage | Persisted digest-bound evidence and coverage projections exist; PR #281 tests failed, unsupported, inaccessible and unrequested outcomes as distinct. Dispatch-intent audit failure is tested fail-closed. | Establish independent custody/trust anchor; test audit-write failure/recovery across refusal, cancellation, timeout, interruption and recovery; prove report completeness/redaction. | OPEN |
| G05 — lifecycle and external effects | PR #276 retires legacy human resolution with HTTP 409. PR #280 prevents the TUI process from draining its own provider work. PR #278's loopback run records real scanner hashes, versions, evidence and uncertain Gobuster restart/no-replay behavior. Outbox delivery remains at-least-once. | Full API/CLI/web/TUI/headless create/approve/observe/cancel/recover parity; provider-by-provider effect recovery and operator reconciliation across processes/hosts. No exactly-once external-effect claim. | OPEN |
| G06 — UI | Route and static control inventories plus automated suites exist. | Full approved visual design, every live control wired to shared services, responsive and keyboard behavior, accessibility and manual acceptance remain incomplete. | BLOCKED |
| G07 — installation and deployment | PR #275 adds clean partial/offline wheel installation evidence. PR #279 keeps production's global cap at 200/min and scopes the high test cap to a loopback auth-disabled fixture. CI covers selected Ubuntu, macOS, Windows setup and Linux systemd/Docker smoke combinations. | Finish optional extras, no-admin/venv, PATH and version conflicts, asset failures, WSL, secrets/TLS/reverse proxy, permissions, storage/resource bounds, backup/restore and operator-host recovery. Do not generalize CI runner coverage to all release hosts. | OPEN |
| G08 — release CI | Current exact main CI is green 21/21, with exact-head PR suites green for the merged batches. | Produce the final release candidate after all gates close and run its complete supported OS/browser/deployment matrix with retained artifacts. | OPEN |
| G09 — release identity | Current project has no V2 release tag/publication. | Select and approve version; build and verify reproducible wheel/sdist/artifact hashes and release workflow. Publish only after qualification. | OPEN |
| G10 — sign-off | Current ledger and this audit record the candidate and decision. | Independent reviewers must accept evidence; the operator must authorize deployment of the exact candidate. | OPEN |

## Merged engineering batches and exact-head checks

Every listed batch below passed its exact-head checks before merge. These checks verify the stated code and test scope; they do not close unrelated ledger obligations.

| PR | Scope | Exact-head checks |
|---|---|---:|
| [#273](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/273) | Public README overhaul | 22/22 |
| [#274](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/274) | URL credential/port rejection; dispatch authorization race | 23/23 |
| [#275](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/275) | P3 install matrix and partial/offline wheel smoke | 23/23 |
| [#276](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/276) | Legacy resolution 409; legacy CLI fail-before-Core | 22/22 |
| [#277](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/277) | P0 capability/caller inventory | 22/22 |
| [#278](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/278) | Provider status separation and bounded loopback smoke | 23/23 |
| [#279](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/279) | Test-only rate limit override; production/route limits preserved | 23/23 |
| [#280](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/280) | TUI workflow submissions remain durable and worker-owned | 23/23 |
| [#281](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/281) | Dispatch/evidence/coverage regressions and egress limitation record | 23/23 |
| [#282](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/282) | P0 inventory and CI evidence reconciliation | 23/23 |
| [#283](https://github.com/andreipath26/WHAXON-AI-Forensics/pull/283) | Request-context/origin/proxy validator hardening | 23/23 |

Current-main exact CI: [#46157672540](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/46157672540), 21/21 jobs. README freeze: [#46157672587](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/46157672587), passed.

## Provider evidence artifact and limits

On exact source head `9f26e848642518b95138305a0ab43cedca23e1c4`, provider CI run [#46144343464](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/46144343464) passed 23/23 checks and retained [provider artifact #15263048381](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/46144343464/artifacts/15263048381), SHA-256 `55827c0e93470b030de59cd5d5468564bbdcd6833d884c9d48d9644dd6d85261`.

The Linux apt lane runs real Nmap, Gobuster, ffuf and SQLmap through approved V2 plans in a network namespace containing only loopback. Gobuster's fixture-observed effect, cancellation, restart uncertainty and no-replay were recorded. Gobuster and ffuf persisted zero normalized findings in the directory smoke. The macOS Homebrew lane runs the loopback-configured smoke but does not use the Linux network namespace; no general scanner egress claim follows from it. Nuclei's template smoke is not full provider qualification. All 12 admitted providers remain `not_qualified` because this artifact does not establish resource bounds, full output correctness, all modes, version pinning before install, production egress, broad effect recovery or end-to-end acceptance.

## Required path to change HOLD

1. Close every implementation and evidence item in the current G01–G10 ledger; keep G06 blocked until the full UI acceptance criteria pass.
2. Obtain independent security/evidence review and authorized operator sign-off for the exact candidate. No external target should be touched before explicit scope authorization.
3. Complete production-like installation, upgrade, backup/restore, multi-worker and recovery exercises on the declared support matrix.
4. Build the release candidate, record its exact SHA and reproducible artifacts/checksums, run all required exact-candidate CI, and only then reconsider PyPI publication and deployment.
5. Update the ledger and G10 decision with reviewer identities, accepted evidence links, limitations and the final disposition. Until those steps pass, **HOLD remains binding**.
