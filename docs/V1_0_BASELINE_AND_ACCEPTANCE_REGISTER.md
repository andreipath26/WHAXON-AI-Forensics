# WHAXON v1.0 Baseline and Acceptance Register

**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Baseline branch:** `main`  
**Baseline commit inspected:** `4019b65511897f61cfce2f547d8beb9cd1da0e7b`  
**Baseline date:** 2026-11-02  
**Authority:** `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md`, especially §§0, 38, 44, 47, 48 and the Engine V2 crosswalk.  
**Status:** Phase 0 in progress; this register records repository evidence, not release acceptance.

## 1. Release identity and repository state

| Item | Observed state |
|---|---|
| Default branch | `main` |
| Inspected HEAD | `4019b655` — `fix(engine-v2): complete E1 security and recovery hardening` |
| Package version | `0.11.16` in `pyproject.toml` |
| Package development classifier | Beta |
| v1.0.0 release | Not published; GitHub releases endpoint returned no releases |
| Open pull requests | 0 at inspection |
| Open issues | 0 at inspection |
| Branch references | 56 total, including `main` |
| Historical PR records | 86 returned by the repository PR listing |
| UI v2 production templates/routes | 22 |
| UI v2 browser test modules | 23 |
| Python test files under `tests/` | 152 |
| Packaged tool catalog entries | 24 |

A roadmap document revision of 1.0.0 is not the package release version. The package remains 0.11.16 and its classifier remains Beta.

## 2. Current CI evidence

Latest run inspected: [CI #41472444936](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/41472444936), for the exact baseline commit `4019b655`.

At the time of inspection, the workflow was still in progress. Completed jobs included successful Ubuntu setup, Windows setup, headless Linux server smoke and curated apt installation smoke. Python 3.11 failed; Python 3.12 and 3.13, Homebrew and macOS setup were still running.

### Confirmed Python 3.11 failure

Job: `125369807312`.

- Ruff passed.
- Mypy passed.
- Pytest reached 100% progress but failed during collection.
- Reported summary: 1,370 passed, 14 skipped, 4 collection errors.
- All four collection errors originate from `tests/test_smb_pivot.py:226`: `Route(..., session_host="10.0.0.5")` raises `TypeError: Route.__init__() got an unexpected keyword argument 'session_host'`.
- Distribution build, metadata validation and wheel smoke were skipped because pytest failed.

Source mismatch confirmed:
- `src/whaxon/core/routes.py` defines `Route` with only `target_host`, `target_port`, `local_port` and `via_session`.
- The latest `src/whaxon/core/runner.py` pivot authorization path reads `route.session_host` and requires the live session identity to match the persisted session.
- The new test fixtures also pass `session_host` to `Route`.

**Disposition:** release blocker. The route contract and resolver must carry trustworthy live session identity, or the runner must obtain it through an explicit supported contract. Do not weaken the new session-identity check to make the tests pass. Add tests for route resolution, persisted/live identity match and mismatch, missing identity, closed/missing session and invalid ports.

The previous run on parent commit `10be95a` failed at system dependency installation before pytest. That is a different failure and must not be confused with this current test-collection failure.

Historical CI run #41313223574 passed on its own older commit; it does not certify this baseline.

## 3. What is present in the repository

### 3.1 Existing product foundations

The current source tree and operator documentation show substantial existing implementation:

- Python package and CLI, shared runner, catalog, adapter registry and SQLite-backed job/finding/session persistence.
- Command-backed and session-backed tool integrations.
- Scope include/exclude rules and fail-closed handling in selected execution paths.
- Reconnaissance pipeline, normalized findings and correlation.
- Deterministic request-context, blind/time-based and observation validation for supported cases.
- Retest command/core paths and finding/report interfaces.
- Evidence storage and HTML, PDF, Markdown and JSON report paths.
- Optional AI providers and operator-governed proposal/approval boundaries.
- Dependency diagnostics and allowlisted, approval-gated installation workflows.
- New UI v2 with production templates and browser tests.
- Engine V2 contracts, persistence, scheduler/recovery foundations and initial read-only scanner-provider bridge.

These are source-presence findings. They do not prove every tool, transport, page, platform or workflow has passed end-to-end acceptance.

### 3.2 Tool inventory

The packaged catalog at `src/whaxon/data/tools.json` contains 24 entries:

`nmap`, `nikto`, `gobuster`, `echo`, `sqlmap`, `whois`, `dig`, `nuclei`, `commix`, `ffuf`, `wpscan`, `impacket`, `theharvester`, `dnsrecon`, `msf_sysinfo`, `msf_getuid`, `msf_hashdump`, `ssh_cmd`, `smb_shares`, `smb_ls`, `netexec`, `arjun`, `wmi_exec`, `hydra`.

The catalog is not a readiness or authorization guarantee. Runtime availability must be checked through the live API/doctor workflow. Adapter registration, executable availability, successful execution, output parsing and validated capability must be tracked as separate states.

### 3.3 New UI

The 22 current UI v2 templates/routes are:

`dashboard`, `scope`, `run`, `findings`, `report`, `reports`, `history`, `diagnostics`, `evidence`, `ai`, `retest`, `chains`, `adapters`, `settings`, `audit`, `monitoring`, `bas`, `bug-bounty`, `compliance`, `ptaas`, `threat-intel`, `approvals`.

The UI interaction audit identifies these still-open acceptance gaps:

1. Visual regression against supplied PNG references.
2. Explicit CLI/web service-parity audit and tests.
3. Accessibility acceptance, including keyboard/focus and manual review.
4. A complete inventory of every visible control, marking each real, disabled or hidden.
5. Deployment decision and tests for external Tailwind/font CDN dependencies.
6. Exact-candidate browser/E2E acceptance.

Reference-only and simulated controls must remain hidden or disabled until real backend behavior and authorization exist. No redesign, substitute screens or mock-success flows are permitted.

### 3.4 Installation and headless operation

Implemented foundations include dependency manifests, readiness diagnostics, profiles, remediation planning, explicit approval and allowlisted installation operations. CI currently has successful Linux headless and Windows setup smoke jobs on the baseline run; macOS setup and Homebrew smoke were still running when inspected.

Still requiring acceptance: clean-machine installation, upgrade, offline behavior, interruption/recovery, partial failure, supported native operating systems, secrets and permissions, persistent service state, backup/restore and advertised service modes. Do not claim native Windows external-tool installation or universal offline readiness without evidence.

## 4. Engine V2 implementation crosswalk

The dated Engine V2 crosswalk on main records:

| Area | Repository evidence/status | Acceptance still required |
|---|---|---|
| E1 security/correctness | Worker leases, owner/token/heartbeat, stale recovery, session identity checks, TLS transport guard, pivot validation and immediate pre-process scope recheck are implemented in source | Current Python 3.11 collection failure; route/session identity contract; DNS, redirect, pivot, child-process and worker-race regression; full cross-version CI |
| E2 contracts/persistence | Versioned WorkflowTask/WorkflowPlan, plan digests, exact ApprovalBinding, durable mission/plan/task/attempt storage and versioned manifests | Integrated lifecycle and crash/restart evidence across real workflows |
| E3 scheduler/recovery | Atomic dependency claims, bounded retries, fail-closed authorization, task deadlines, stale-attempt fencing and uncertain-outcome handling | Mission-wide budgets, concurrency/resource ceilings, durable cancellation, audit/outbox guarantees and reconciliation for uncertain external side effects |
| E4 providers | Initial read-only scanner provider bridge through catalog, capability registry and existing ToolRunner | Full portfolio reconciliation, truthful readiness/capability extraction, remaining adapter contracts and separately gated session/API transports |
| Shared Core / E5 | Core mission/plan/scheduler services and a headless Linux smoke are present | Shared CLI/API/web lifecycle, durable progress/coverage/evidence/verification, restart recovery and parity |
| E6 UI | Supplied UI route/template integration exists | All-control, visual, accessibility, parity and exact-candidate acceptance |
| Later autonomy/multi-target | Foundations or roadmap designs exist | Not a v1.0 prerequisite; gated behind earlier phases |

The roadmap and crosswalk explicitly say implementation records do not equal release acceptance. E1 is not accepted merely because the latest commit title says it completes E1.

## 5. Branch and pull-request reconciliation

There were 56 branch references including main and no open pull requests at inspection. The repository PR listing returned 86 historical PR records. The canonical UI integration and follow-up work—PRs #37, #41, #42 and #43–#73—was recorded as merged. Dependency readiness PR #79, bug-bounty ingestion PR #78, first-run installation PR #86, Findings PR #85, Run PR #84 and Scope PR #83 were also recorded as merged.

Important cautions:

- Many historical branch tips compare as diverged/ahead of current main because the work was merged through squash or merge commits and the branches were retained.
- A compare result showing commits ahead is not sufficient evidence that the changes are absent from main.
- Old branches must not be merged or cherry-picked blindly.
- The historical full-wiring PR #16 was closed unmerged as a draft; PRs #33–#36 were superseded by later integration.
- Some branch references are entirely behind main and contain no commits ahead. They are stale candidates for eventual cleanup, not implementation work.
- The branch `ui/dashboard-wiring-2026-10-28` has a large divergent history and should be treated as historical; its merged PR #42 is the integration record. Do not reintroduce its whole branch tip.

**Disposition:** no PR merge is waiting. Branch cleanup is not a release task and should occur only after the unique-work check is documented. Preserve all branch content until this check is complete.

## 6. v1.0 blockers and dependency order

### Blockers to close

1. **Current E1 CI failure:** reconcile `Route` and live pivot session identity; restore collection and add meaningful authorization tests without weakening security.
2. **E1 security acceptance:** DNS and redirect behavior, child/follow-up jobs, pivot transitions, scope changes, worker ownership, cancellation and race conditions.
3. **Trust Layer/evidence chain:** verified/candidate/inconclusive state transitions; no LLM/UI promotion; evidence provenance and integrity across success, denial, cancellation, timeout, crash, audit-write failure and recovery.
4. **Shared execution services:** common CLI/API/web contracts; durable jobs independent of browser lifetime; bounded workers, deadlines, cancellation, idempotency, recovery and observable follow-up execution.
5. **Dependency readiness/headless:** clean supported install, explicit consent, independent verification, offline/partial-failure/restart acceptance and honest platform support.
6. **New UI:** page-by-page real backend wiring and exact supplied design preservation; all visible controls accounted for; visual/accessibility/parity tests.
7. **Tool portfolio:** reconcile catalog/adapters/providers with the roadmap's candidate inventory; do not equate catalog presence with verified support.
8. **Reporting and retest:** reproduction evidence, honest coverage/non-testing disclosure, persisted retest transitions and supported report formats.
9. **Release acceptance:** full tests/static checks/package build/install/upgrade, cross-version/platform checks and controlled end-to-end workflows on the exact release candidate.

### Explicitly deferred beyond solo v1.0

- §42 multi-target/CIDR campaigns and bounded per-target parallelism.
- §43 competitive parity and expanded benchmarking.
- Enterprise/team/multi-tenant capabilities and high availability.
- Broader autonomous bug-bounty campaigns and unrestricted autonomy.
- Long-term research and platform expansion.

Do not begin §42/§43 before the supplied UI gate and solo v1.0 acceptance. Do not expose unsupported controls to make a page look complete.

## 7. Phase 0 work remaining

This register is an initial evidence-backed baseline, not the completed Stage 0 exit gate. The following work remains:

1. Finish the full capability matrix for every CLI command, API route, worker, transport, adapter, tool, UI control and advertised deployment mode. Route/template counts alone are not enough.
2. Trace the critical workflow from scope and authorization through plan, scheduler, adapter, evidence, validation, retest and report, recording source paths and persisted records at each boundary.
3. Reconcile all historical branch refs against merged PR contents and current main file contents. Do not delete branches in this phase.
4. Refresh the exact CI matrix after run #41472444936 completes and record every failure by job, step and root cause.
5. Build the dependency graph and workstream register required by `docs/ENGINEERING_EXECUTION_MODEL.md`, with isolated file ownership and acceptance tests.
6. Update the state/crosswalk documentation only when current code and exact test evidence support the change.

**Phase 0 exit gate:** one current, evidence-backed capability inventory, critical workflow map, dependency graph, workstream ownership and acceptance plan exist; exact main CI status and known blockers are recorded. No feature expansion is part of Phase 0.

## 8. Immediate next implementation dependency

The first Stage 1 issue exposed by this baseline is the pivot route contract:

- `src/whaxon/core/routes.py` currently defines no `session_host` field.
- `src/whaxon/core/runner.py` now requires the live route's session host to compare it with the persisted session host.
- `tests/test_smb_pivot.py` constructs routes with `session_host`, causing Python 3.11 test collection to fail.

The fix must make the route resolver carry the actual live session identity from the port-forward/session source and validate it against the persisted session. It must not add a fabricated default host or bypass the identity comparison.

---
This register is a baseline snapshot, not a claim that v1.0 or Phase 0 is complete. Recheck main and CI before using it as a later release-candidate record.
