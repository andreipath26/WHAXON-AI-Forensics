# Engine V2 — Roadmap requirement evidence matrix

**Source of truth:** [master roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md) and [architecture crosswalk](ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md).  
**Audited baseline:** `c75c03888e35f6147cfae3547f286202bb09fd6e` (main, 2026-11-03).  
**Detailed ledger:** [ENGINE_V2_ROADMAP_REQUIREMENTS.csv](ENGINE_V2_ROADMAP_REQUIREMENTS.csv).

## Coverage and limitations

| Scope | Requirement entries mapped |
|---|---:|
| P0–P4 | 34 |
| P5–P8 | 21 |
| Engine gates E0–E9 | 10 |
| Solo-release gates G01–G10 | 10 |
| **Total** | **75** |

- 42 entries link candidate implementation/doc artifacts; 68 entries link candidate test artifacts. All referenced file paths were checked against the repository tree, and all 29 explicit test-function references were checked against actual definitions; none was missing.
- The entries correspond to the roadmap's P0–P8 bulleted/numbered/table requirements (plus P5/P7 narrative paragraphs), E0–E9 gates, and G01–G10 release gates. A compound paragraph/bullet may contain multiple acceptance obligations; **this is a source-level index, not an atomic criterion tally**. Future acceptance work must split compound requirements rather than declare them complete as a group.
- `CANDIDATE_MAPPING` means a relevant code or test artifact exists; **it does not mean that test proves the full requirement**. A row without a direct test link has an explicit evidence gap; a row with related tests can still have uncovered clauses.
- `NOT_ACCEPTED` is conservative: no row is counted as a completed acceptance criterion until exact assertion/expected result and a candidate-SHA execution result are recorded.
- All nine post-merge CI check-runs on `c75c03888e35f6147cfae3547f286202bb09fd6e` passed, including Python 3.11/3.12/3.13. This is **overall CI evidence**, not a requirement-level sign-off.

## Verified from source

- **E0:** Architecture crosswalk and dated baseline inventory are present. Historical inventory is not evidence of current implementation state.
- **E1:** Fail-closed scope, Nikto regression, replay/retest and approval tests exist. [E1 acceptance](ENGINE_V2_E1_ACCEPTANCE.md) explicitly remains **OPEN**.
- **E2:** `src/whaxon/core/workflow.py` has typed workflow tasks/plans, digest and approval binding; `src/whaxon/core/capabilities.py` has manifests, requirements and deterministic resolution, with persistence and compatibility tests.
- **E3:** `src/whaxon/core/scheduler.py` implements scheduler execution/heartbeat and retries; workflow/worker tests cover durable leases, deadlines, mission limits, cancellation and uncertain attempts. Wider crash/audit/outbox acceptance remains open.
- **E4:** `src/whaxon/core/providers.py` implements the local catalog-adapter provider bridge with pinned version and readiness; remote/session/browser/cloud transport acceptance is not established.
- **E5–E6:** CLI/API, Core, headless and V2 route tests exist; full shared-lifecycle, per-control UI and release-gate acceptance remain open.
- **E7–E9:** Deferred expansion has partial supporting components, not accepted complete phases.

## Acceptance accounting rule

Do **not** use arbitrary percentages. For every atomic requirement, record a durable: (1) source symbol and path, (2) exact test function and assertion, (3) running environment and commit SHA, (4) result, (5) reviewer/acceptance decision, and (6) limitations. Count `accepted / applicable atomic requirements` only after that evidence exists; explicitly exclude roadmap-deferred features from a solo-v1.0 percentage. Do not substitute a generic passing suite or a file's existence for a requirement's acceptance test.

**Current defensible acceptance percentage: not measured.** The ledger is an auditable inventory and gap register, not a release certification.
