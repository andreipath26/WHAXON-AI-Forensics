# E6 service-to-UI handoff matrix — backend evidence only

**Date:** 2026-11-05. **Status:** candidate contract inventory, NOT UI acceptance.
**UI owner dependency:** final supplied UI design **not ready**. This matrix is an integration handoff specification, *not* an instruction to change templates. Zero redesign; preserve supplied references and existing templates. Never mark a static control accepted because its route exists.

## Existing APIs and consumer contracts

| Consumer concern | Current V2 service path | Evidence location | Required semantics for future UI | Open validation |
|---|---|---|---|---|
| Mission list/create | `GET/POST /api/v2/missions` | `tests/test_server_workflow_v2.py` | No phantom missions, error on invalid input, authentication and scope | Complete real-client behavior |
| Plans and detailed task state | `GET /api/v2/missions/<mission_id>/plans`, `GET /api/v2/workflows/<plan_id>` | `tests/test_server_workflow_v2.py` | Persisted identifiers, 404 on unknown, distinguish blocked from succeeded | Full visual mapping |
| Durable start | `POST /api/v2/workflows/<plan_id>/run` | `tests/test_workflow_run_requests.py` | HTTP 202 means accepted/queued only; reconnect URL, no automatic success | Human consent and actual tool lab |
| Run status and snapshot | `GET /api/v2/workflow-runs/<id>`, `/<id>/snapshot` | `tests/test_engine_v2_e6_contract_preflight.py`, `tests/test_engine_v2_e6_client_parity.py` | Persisted request, no private lease token, no assumed worker liveness, uncertain state visible | Browser lifecycle |
| Queue summary | `GET /api/v2/workflow-runs/summary` | `tests/test_workflow_run_requests.py` | Read-only counts, not worker liveness proof | Empty/error/offline behavior |
| Cancel intent | `POST /api/v2/workflow-runs/<id>/cancel`, `POST /api/v2/workflows/<plan_id>/cancel` | `tests/test_engine_v2_e6_client_parity.py`, `tests/test_server_workflow_v2.py` | Request-level stop barrier; never imply external effect already stopped | Browser confirmation/reconciliation |
| Workflow progress/events | `GET /api/v2/workflows/<id>/progress`, `/events`, `/attempts` | `tests/test_server_workflow_v2.py` | Distinguish queued, blocked, failed, uncertain and actual verified evidence | Event polling/reconnect proof |
| Approval and revoke | `GET/POST /api/v2/workflows/<id>/approvals`, `POST /api/v2/workflows/<id>/approvals/<approval_id>/revoke` | `tests/test_server_workflow_v2.py` | No implicit approval; server enforces exact scope/actor/expiry and change of plan | Cross-client adversarial approval lab |
| Budget/deadline/rate | `/api/v2/workflows/<id>/limits`, `/deadline`, `/rate-limit` and mission-level bounds | `tests/test_server_workflow_v2.py` | Tightening and fail-closed invalid settings, one server-side authority | Negative/migration matrix |
| Evidence and audit | `GET /api/v2/workflows/<id>/evidence`, `/audit`, `/reconciliation` | `tests/test_server_workflow_v2.py` | Report raw/observed versus independently verified; disclose broken seals and uncertainty | Final report reproducibility and external witness |
| Readiness | `GET /api/v2/workflows/<id>/readiness` | `tests/test_engine_v2_e6_client_parity.py` | Never infer success from queue completion or HTTP 200 | Full solo lab acceptance |

## Explicitly unresolved legacy paths

Existing legacy `/api/run`, `/api/ai/run`, Metasploit and CLI direct execution remain separate from V2 queue authority. The E5 freeze did **not** migrate them. E6 must consume the P2/E4 caller migration/no-bypass results rather than add another UI-side execution path. Do not delete compatibility code before migration and rollback checks.

## Future visual-control acceptance protocol (not yet executable)

When the new design is formally ready, map each visible control to an approved reference variant, exact endpoint and input, backend authorization, response schema, loading/error/blocked/empty/offline/reconnect/cancel states and specific test. Preserve all existing design inputs. Test keyboard focus/semantic labels, responsive behavior and assistive technologies; compare approved screenshots and external-asset behavior across supported environments. Count accepted controls only after test evidence at an exact commit, not static source references.

### Review boundaries

1. E6 backend test additions can run while UI is incomplete. **No claimed UI progress** results from their success.
2. API/CLI parity is narrower than UI or full product parity.
3. E6 and G01–G10 release gates remain open; no real scanner, live unauthorized target or production trust anchor was exercised.
4. Keep the existing one-E6-branch/one-PR model; document regressions and exact-head CI before any freeze.
