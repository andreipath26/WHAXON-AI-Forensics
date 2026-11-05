# Engine V2 legacy execution inventory

This inventory records Python callsites that invoke `run_tool` or
`run_in_session` directly. It is guarded by
`tests/test_engine_v2_legacy_callsite_inventory.py`: adding, removing, or moving
a callsite requires reviewing its execution path and updating the classification.

| Source | Caller | Classification | Notes |
| --- | --- | --- | --- |
| `interfaces/web/server.py` | `_run_job_blocking` | Legacy | `/api/run`; scope checked, but no persisted V2 request or task lease. |
| `core/ai_bridge.py` | `_run_tool`, `build_executor._run_in_session` | Legacy | Used by web and CLI AI execution; approvals remain in legacy `ai_runs`. |
| `ai/executor.py`, `ai/providers/*` | Executor/provider actions | Legacy | Indirect callbacks still dispatch through `ToolRunner`. |
| `interfaces/cli/run_cmd.py` | `main._go` | Legacy | Direct tool/session execution; legacy override semantics remain. |
| `core/worker.py` | `drain_async` | Legacy | Drains Automator follow-up jobs outside workflow-plan authorization. |
| `interfaces/gui/main_window.py`, `interfaces/tui/screens/main.py` | `_run_tool` | Legacy | Desktop and terminal clients still use direct dispatch. |
| `core/providers.py` | `dispatch` | Engine V2 | Canonical provider dispatch after workflow authorization and scheduler checks. |

The legacy routes already apply scope checks and tool validation. Their remaining
gap is lifecycle and policy parity: workflow-bound authorization, durable request
identity, task leases, plan-bound approval, cancellation, reconnect, and recovery.
This inventory is evidence of caller coverage, not a claim that those controls
are absent from every legacy path or that a migration is safe.

Additional execution actions need their own semantic inventory. In particular,
CLI passive recon and verified-finding retests call their dedicated recon and
validator services rather than `ToolRunner`; they should only be mapped to V2
capabilities after their permission and evidence contracts are reviewed.

## Dedicated network-service entry points

These paths can perform network work without calling `ToolRunner`. The
callsite guard pins their current production entry points separately from the
runner inventory.

| Source | Caller | Service path | Scope/consent boundary | Persistence and V2 status |
| --- | --- | --- | --- | --- |
| `interfaces/cli/recon_cmd.py` | `main` | `core.recon.run` → `ReconRunner.run` → registered DNS/TLS/HTTP checks | CLI checks scope before execution; `ReconRunner.run` checks scope again. No plan-bound approval or V2 task authorization. | `JobStarted`/`JobFindings` enter the legacy event bus and its store subscribers. Direct service execution; no V2 workflow request, lease, attempt or cancellation record. |
| `interfaces/cli/validate_cmd.py` | `main` | `Validator.validate` | CLI resolves the stored finding target, requires it, then checks active scope before calling the validator. The validator itself does not enforce scope. | Writes verification state to the legacy job store and records proof for verified outcomes. Direct HTTP probes; no V2 task/attempt record. |
| `interfaces/cli/retest_cmd.py` | `main` | `Validator.revalidate` → `Validator.validate` | Requires a previously verified finding and rechecks target scope before calling the validator. The validator itself does not enforce scope. | Updates legacy finding verification state. Direct HTTP probes; no V2 task/attempt record. |
| `interfaces/web/server.py` | `create_app.api_validate` | `Validator.validate` | `_validation_scope_error` checks target presence and current scope before the probe. The validator itself does not enforce scope. | Updates legacy verification state and proof through `JobStore`; not dispatched as a V2 workflow task. |
| `interfaces/web/server.py` | `create_app.api_retest` | `Validator.revalidate` → `Validator.validate` | Requires `verification_status == "verified"`; `_validation_scope_error` checks target presence and current scope before the probe. | Updates legacy verification state through `JobStore`; not dispatched as a V2 workflow task. |

`Validator.revalidate` calling `self.validate` is an internal service delegation,
not a second external dispatch. The dedicated tests currently include
`test_recon.py`, `test_validate_cmd.py`, `test_validator_retest.py`,
`test_validator_security_regressions.py`, and `test_web_trust_layer.py`. UI tests exercise client requests but are not the route-level security evidence cited here.
These prove selected service and route behavior; they do not establish
cross-client V2 parity, durable workflow ownership, operator consent, or
deployment acceptance. Keep the service paths classified as legacy until a
separate capability mapping and migration with rollback evidence is accepted.

## Migration constraint

Do not redirect `/api/run`, `/api/ai/run`, CLI tool/session execution, recon, or
retest in bulk. The Run page consumes the current web route, AI uses a separate
operator-answer record, and the CLI exposes capability-specific options. Each
migration needs an explicit capability mapping and parity tests before retiring
the legacy caller. E6 remains frozen until the operator declares the UI ready.
