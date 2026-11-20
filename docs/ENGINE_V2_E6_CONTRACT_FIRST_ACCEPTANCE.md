# Engine V2 E6 — contract-first integration and UI readiness boundary

**Status:** E6 implementation in progress; **NOT engineering-accepted, NOT UI-ready, NOT release-ready**.
**Branch:** `engine-v2/e6-contract-first-integration` (one E6 branch, one phase PR, no partial merge).
**Base:** E5 squash merge `80c3ca566ecdaef1181209fab90fc23184796251`.
**Governing documents:** master roadmap P4/P5 and §38 G01–G10; `ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md`; `ENGINEERING_EXECUTION_MODEL.md`; `UI_CONTROL_INVENTORY.md`.

## Binding boundary: supplied UI is NOT yet ready

Do not redesign, edit, restyle, silently complete, or declare accepted the supplied UI. Keep `web ui files and rendering/` and existing `ui_v2_*.html` source intact. A rendered route, a source script reference, a successful HTTP 200 or a passing API test **does not** certify the UI's visual fidelity, accessibility, control behavior or release readiness. UI completion remains an explicit external dependency. Preserve distinct supplied reference variants, and do not build a substitute interface.

## Parallel workstreams and contracts

| Stream | E6 deliverable independent of unfinished design | Pass condition | State |
|---|---|---|---|
| C1: service truth | Stable read-only API semantics for mission, plan, progress, readiness, findings/evidence, queue summary and reconnect snapshots; reject unknown IDs; do not claim liveness or execution | Exact-SHA tests for truthful unsupported/queued/cancelled/error states without external effects | IN PROGRESS |
| C2: authorization and actions | Cross-client mutation inventory and explicit scope/plan/approval/CSRF/expiry barriers; no UI-only authorization | Negative assertions and no-bypass evidence across API/CLI; no live scanner | OPEN |
| C3: durable client lifecycle | Persist request identity, reconnect URL, cancellation and uncertainty; no per-browser runner | Independent-server restart and API/CLI parity tests; preserve E5 worker fencing | EXISTING E5 CONTRACT, E6 PARITY OPEN |
| C4: evidence and reporting | Verified result versus observed raw output; deterministic report provenance, audit and missing-data disclosure | Seeded controlled workflow with negative/inconclusive cases, repeatable exports | OPEN |
| C5: supplied UI binding | Control-to-service matrix for each actually-visible control, including loading/error/blocked/reconnect/no-data states | Only after final supplied design is ready, visual/accessibility/user acceptance | BLOCKED ON UI |
| C6: release operations | Clean installs, headless/desktop/browser parity, offline and deployment/resource behavior | Supported exact-head CI plus independent G01–G10 acceptance | OPEN |

## Source-backed integration inventory (not acceptance)

- V2 mission and plan APIs: `GET/POST /api/v2/missions`, `GET /api/v2/missions/<id>/plans`, `POST /api/v2/workflows`, `GET /api/v2/workflows/<id>`.
- V2 durable submission: `POST /api/v2/workflows/<id>/run` returns a durable **accepted request** (202), never a guarantee of execution.
- V2 reconnect: `GET /api/v2/workflow-runs/<id>`, `GET /api/v2/workflow-runs/<id>/snapshot`, `GET /api/v2/workflow-runs/summary`, `GET /api/v2/workflows/<id>/progress`.
- V2 control: `POST /api/v2/workflow-runs/<id>/cancel`, plan cancel, approval/revoke, limits, deadlines, rate limits. Each action needs separate authority and negative-test evidence.
- V2 evidence and readiness: `GET /api/v2/workflows/<id>/readiness`, `/audit`, `/evidence`, `/reconciliation`, `/events`, `/attempts`. These surfaces do not themselves demonstrate truthful complete reports.
- 22 supplied production template files with the existing static inventory of 793 controls. The inventory marks static unresolved and script-reference-only controls; no runtime acceptance implied.

## Initial E6 preflight checks

`tests/test_engine_v2_e6_contract_preflight.py` checks that a distinct web instance can inspect a durable queued request without executing it, that status, snapshot and queue views never present a queued request as completed or a live worker as verified, and that unknown requests are rejected. Uses an inert unsupported fixture address in the reserved TEST-NET-1 range and `WHAXON_V2_EXTERNAL_WORKER=1`. **No new UI**, no scanner, no external target or new runtime authority.

## E6 acceptance blockers

1. Finish supported API/CLI/desktop parity and test all exposed mutation authority boundaries; reconcile E4/P2 legacy direct-execution exceptions.
2. Finish deterministic findings, verification, evidence, coverage and reports in one controlled end-to-end solo workflow.
3. When design is declared ready, reconcile every visible control against a real endpoint, permissions, states and error behavior without altering the supplied design.
4. Verify pixel/responsive fidelity, focus/keyboard/assistive-tech behavior, external assets and environment parity against approved design evidence.
5. Execute, evidence and sign off G01–G10; preserve production external audit-anchor and live authorized lab requirements.

**Gate rule:** E6 stays OPEN until applicable supported engineering checks and documented phase decision succeed; production/full V2 deployment acceptance remains separately OPEN even after engineering freeze. No percentage based solely on pages, test count or source presence.
