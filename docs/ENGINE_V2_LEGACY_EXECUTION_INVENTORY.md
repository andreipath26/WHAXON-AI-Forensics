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
| `interfaces/web/server.py`, `adapters/msf.py` | `create_app.msf_run._do_run` → `MSFAdapter.run_module` | `MSFClient.execute` (module and optional auto-chain post modules) | The MSF route validates module/target inputs and checks target scope before enqueueing its worker. This direct adapter path is not a `ToolRunner` dispatch. The optional post-module auto-chain is not plan-bound V2 dispatch. | Persists job output/findings through `JobStore`; no V2 workflow task, lease, attempt or cancellation record. Keep separate from catalog tools routed through `ToolRunner`. |
| `interfaces/web/server.py` | `create_app.msf_session_exec` | `MSFClient.session_exec` | `_msf_session_scope_error` resolves the session host and checks current scope before sending the supplied session command. | Returns output directly; no V2 task/attempt record or durable workflow evidence link. |
| `core/runner.py` | `run_in_session` → `_run_msf_session` | `MSFClient.session_exec` | Runner requires a persisted open session, authorizes its stored host, re-reads the live RPC session and authorizes its host, rejects host identity drift, and enforces a required session type when available before dispatch. | Emits legacy job events and stores capped output; this session-scoped execution path is not scheduler-owned V2 workflow dispatch. |

`Validator.revalidate` calling `self.validate` is an internal service delegation,
not a second external dispatch. The dedicated tests currently include
`test_recon.py`, `test_validate_cmd.py`, `test_validator_retest.py`,
`test_validator_security_regressions.py`, and `test_web_trust_layer.py`. UI tests exercise client requests but are not the route-level security evidence cited here.
These prove selected service and route behavior; they do not establish
cross-client V2 parity, durable workflow ownership, operator consent, or
deployment acceptance. Keep the service paths classified as legacy until a
separate capability mapping and migration with rollback evidence is accepted.

## Adapter subprocess ownership

`HashcatAdapter.run_module` and `ImpacketAdapter.run_module` contain direct
subprocess hooks, but repository callsite search found no callers for either
hook. The only direct `adapter.run_module(...)` invocation is in the MSF route,
which resolves the MSF adapter. Do not treat the Hashcat/Impacket hooks as
reachable execution paths until a caller is added and its authorization owner
is reviewed. Current Impacket catalog and SMB/WMI session execution goes through
`ToolRunner`, which applies target/scope checks before dispatch.

## Packaged catalog and Engine V2 admission

The packaged catalog contains 24 tool IDs across five declared transports:
17 `cli`, three `msf_session`, two `smb`, one `ssh`, and one `wmi`. The V2
catalog bridge admits 12 of the CLI entries. For each admitted entry it creates
both a `tool.<id>` compatibility capability and one stable semantic operation
alias. These aliases share the same local-process provider, fixed catalog argv,
`network.scan` permission, moderate impact, network-traffic/service-log side
effects, scope and approval checks, and ToolRunner dispatch. Dynamic task
arguments are unsupported; a successful tool exit is not independent
verification.

| Catalog IDs | V2 status | Transport and reason |
| --- | --- | --- |
| `arjun`, `dig`, `dnsrecon`, `ffuf`, `gobuster`, `nikto`, `nmap`, `nuclei`, `sqlmap`, `theharvester`, `whois`, `wpscan` | Admitted | `cli` → `local_process`, provider-bound; target-type allowlist applies. |
| `commix`, `echo`, `hydra`, `impacket`, `netexec` | Not admitted | `cli`; no Engine V2 provider admission. Some have legacy adapters. |
| `msf_getuid`, `msf_hashdump`, `msf_sysinfo` | Unsupported in V2 | `msf_session`; requires a separately accepted session provider. |
| `smb_ls`, `smb_shares` | Unsupported in V2 | `smb`; requires a separately accepted session provider. |
| `ssh_cmd` | Unsupported in V2 | `ssh`; no registered adapter in the inspected runtime. |
| `wmi_exec` | Unsupported in V2 | `wmi`; requires a separately accepted session provider. |

Exact V2 operation aliases and declared target types:

| Tool | Compatibility capability | Semantic capability | Target types |
| --- | --- | --- | --- |
| `arjun` | `tool.arjun` | `web.parameters.discover` | URL |
| `dig` | `tool.dig` | `dns.records.query` | Hostname |
| `dnsrecon` | `tool.dnsrecon` | `dns.records.enumerate` | Hostname |
| `ffuf` | `tool.ffuf` | `web.paths.fuzz` | URL |
| `gobuster` | `tool.gobuster` | `web.directories.enumerate` | Hostname, IP |
| `nikto` | `tool.nikto` | `web.server.audit` | Hostname, IP, URL |
| `nmap` | `tool.nmap` | `network.services.discover` | Hostname, IP |
| `nuclei` | `tool.nuclei` | `web.templates.assess` | URL |
| `sqlmap` | `tool.sqlmap` | `web.sql_injection.assess` | URL |
| `theharvester` | `tool.theharvester` | `osint.domain.contacts.search` | Hostname |
| `whois` | `tool.whois` | `domain.registration.lookup` | Hostname, IP |
| `wpscan` | `tool.wpscan` | `web.wordpress.audit` | URL |

The built-in adapter registry also reports four adapter-only IDs—`burp`,
`hashcat`, `msf`, and `whatweb`—without packaged catalog entries. The prior
V2 allowlist declared `whatweb` even though no catalog item could bind it. The
allowlist and semantic alias map now exclude that stale declaration; the
catalog/transport guard will fail if the shipped catalog or admitted set drifts
without explicit G01 review. `echo` and `ssh_cmd` are catalog entries without a
registered adapter. Portfolio classification for non-admitted tools does not
replace this separate adapter-presence fact.

### Read-only live snapshot

On the local audit environment, `whaxon workflow portfolio-audit` reported 24
catalog entries and 26 discovered adapters: 12 bound, five not admitted, seven
unsupported transports, and four adapter-only. The provider inventory showed
24 registered rows (12 compatibility + 12 semantic aliases), 12 unsupported
catalog rows, **zero executable providers**, and no smoke-tested, lab-validated,
or end-to-end-verified providers; all 12 admitted binaries were absent from that
environment. This is an environment-specific readiness observation, not a claim
about a deployment host. The audit command is read-only and explicitly does not
enable execution. A same-session executable preflight also found no Docker CLI
and none of the 12 admitted binaries (`arjun`, `dig`, `dnsrecon`, `ffuf`,
`gobuster`, `nikto`, `nmap`, `nuclei`, `sqlmap`, `theharvester`, `whois`,
`wpscan`) on this workspace host. No scanner, container or network operation
was attempted. This host therefore cannot supply the required controlled-lab
execution evidence; deployment-host readiness remains unverified.

### Client and service boundary summary

| Client surface | V2 path | Existing legacy path | Durable owner / relevant evidence |
| --- | --- | --- | --- |
| CLI workflow | `whaxon workflow` → shared `Core` workflow/approval/provider services | `whaxon run`, `ai`, `recon`, `validate`, and `retest` retain direct legacy execution; `whaxon msf` only inspects status/sessions/modules | V2 plans, approvals, requests, tasks, events and evidence use `JobStore`/`WorkflowRunQueue`; see `test_workflow_cli.py`, `test_workflow.py`, `test_workflow_run_requests.py`, and `test_providers.py`. |
| HTTP API | `/api/v2/capabilities`, `/providers`, `/workflows`, `/workflow-runs` and related lifecycle routes call shared Core services | `/api/run`, `/api/ai/run`, `/api/msf/run`, `/api/validate`, `/api/retest` remain separate legacy paths | V2 route evidence: `test_server_workflow_v2.py`; legacy paths retain legacy job/AI state and are not all V2 request/task-owned. |
| Headless service | `whaxon serve` plus `whaxon workflow plan serve-requests` | Legacy worker/Automator follow-ups remain separate | V2 worker claims durable requests; see `test_workflow_continuous_worker.py`, E5 systemd and Docker tests. |
| Native desktop and terminal | None of their direct execution actions are V2 workflow dispatches | GUI/TUI call `Core.runner` directly | Legacy `JobStore`/event path; see `test_gui_entrypoint.py`, `test_tui_main.py`, and runner tests. |

### Consequential HTTP route ownership

`test_api_route_methods_and_handlers_are_explicit` pins the method, path and
handler binding for all Flask `/api/*` routes, including read/status/export
routes. The matrix below summarizes consequential ownership and authorization
boundaries; it does not claim to guard UI controls.

A static decorator census currently finds 104 `/api/*` method/path bindings and
22 `/ui-v2/*` page routes in `interfaces/web/server.py` (five other routes are
health/root/settings/favicon pages). The matrix below covers consequential
execution, authorization-state, cancellation and provisioning routes. Read,
status and export routes are pinned for drift, but their complete source,
persistence, access-control and test-semantic crosswalk remains open under G01.
The UI page/control inventory is frozen and is not being edited here.

| Route group | Paths and owner | Authorization/effect boundary | V2 ownership and evidence |
| --- | --- | --- | --- |
| V2 capability and lifecycle | `GET /api/v2/capabilities`, `/providers`, `/providers/portfolio-audit`; `POST /api/v2/workflows`; `POST /api/v2/workflows/<plan_id>/run`; `POST /api/v2/workflow-runs/<request_id>/cancel` | Core capability registry, workflow contracts, approvals and durable request queue. A run submission is persisted work, not a success result. | Shared Core path; see `test_server_workflow_v2.py`, `test_workflow_run_requests.py`, and `test_workflow.py`. |
| Legacy tool and AI dispatch | `POST /api/run` → `_run_job_blocking`; `POST /api/ai/run` → legacy AI executor/bridge | Scope and input checks apply at the route, with legacy job or AI-run state. They do not create V2 plan-bound task attempts. | Legacy path; see `test_server.py`, `test_server_ai.py`, runner and AI bridge tests. |
| Legacy Metasploit | `POST /api/msf/run`; `POST /api/msf/sessions/<session_id>/exec` | Module path validates inputs and scope before worker dispatch. Session command checks live session scope before RPC. | Legacy job/session paths; no V2 task/attempt lifecycle. |
| Metasploit pivot forwarding | `GET`, `POST`, and `DELETE /api/msf/sessions/<session_id>/portfwd` | Every operation checks the session host against current scope. Creation separately checks the destination and writes a pivot edge; removal calls the legacy forward manager. | Network/pivot side effects remain outside V2 task ownership. See `test_server_portfwd.py` and scope-denial cases in `test_server.py`. |
| Verification and human resolution | `POST /api/validate/<job_id>/<seq>`; `POST /api/retest/<job_id>/<seq>`; `POST /api/approvals/<job_id>/<seq>/resolve` | Validate/retest recheck current target scope; retest requires existing verified status. The resolve route writes verified/refuted state using a caller-supplied display label; it is not a plan-bound V2 approval. | Validator routes are legacy and not scheduler-owned. Route trust-boundary evidence includes `test_web_trust_layer.py`, `test_validator_retest.py`, and `test_server.py`. |
| Scope policy | `GET`, `POST /api/scope`; `POST /api/scope/check`; `POST /api/scope/override` | Scope POST persists rules and requires explicit confirmation to disable enforcement. Scope check evaluates a target. Override only writes a legacy audit-style record; it does not authorize dispatch. | Scope configuration feeds shared Core checks, but the legacy override record is not a V2 approval. See `test_web_scope.py`, `test_scope_failclosed.py`, and `test_server.py`. |
| Legacy job cancellation | `POST /api/jobs/<job_id>/cancel` | Calls `_cancel_job_blocking` for a legacy job process/event state. | Separate from durable V2 run-request and plan cancellation endpoints. Route-level lifecycle parity remains open under G05. |
| Dependency provisioning | `POST /api/dependencies/install`, `/install-batch`; `POST /api/dependencies/install/<operation_id>/cancel` | Runs only from a current approved install plan and uses separate OS/package-manager authority; this is system provisioning, not target assessment. | Outside workflow task dispatch. See `test_dependencies.py`, `test_dependency_installer.py`, and dependency server tests. |

The legacy `/api/tools` catalog and `/api/v2/capabilities` registry are different
advertisements: catalog presence is not V2 admission, and provider installation
does not prove smoke, lab, end-to-end or authorization acceptance.

### Deployment entry points and readiness semantics

| Entry point or report | Current source behavior | G01 limit |
| --- | --- | --- |
| `whaxon web` | `server.main` starts Flask's development server. | Development path; not the production serving mode. |
| `whaxon serve` | `interfaces/web/serve.py` starts Waitress in foreground; `--daemon` uses `os.fork` double-fork. | Daemon mode is Unix-specific in source; do not infer native Windows support from OS documentation. |
| systemd | `whaxon.service` uses Gunicorn with `create_app_factory()`; paired worker unit runs durable request polling. | Unit contract and CI are not a successful supported-host install or live worker verification. |
| `docker-compose.e5.yml` | Repository-source web and dedicated worker share `/data`; web binds to loopback. | Distinct from root `docker-compose.yml`, which is the vulnerable lab target. Docker assets are excluded from sdist; this is a checkout/source deployment path. |
| Wheel/package | `pyproject.toml` exposes `whaxon`, `whaxon-tui`, and `whaxon-gui` and packages systemd units. | Installed TUI/GUI data directory behavior has not been reconciled with `WHAXON_DATA`; GUI startup also launches `whaxon serve --daemon`. Installed-wheel GUI/TUI acceptance remains unverified. |
| `/api/health` | `core_ready` means SQLite responds and the data directory is writable; Metasploit is reported as optional degraded state. | Does not prove worker liveness, scanner readiness, workflow readiness, or assessment success. |
| `whaxon workflow providers`, `/api/v2/providers` | `executable=true` means local manifest/catalog binding plus installed binary. `smoke_tested`, `lab_validated`, and `end_to_end_verified` remain separate fields and currently false. | “Executable” does not mean authorized, smoke-tested, lab-validated, end-to-end verified, or production-ready. |
| `whaxon doctor` | `overall_status=READY` means required dependency checks are ready. | Does not establish service, worker, workflow or deployment acceptance. |

Top-level CLI modes from `src/whaxon/cli.py` are `setup`, `doctor`, `init`,
`up`, `down`, `serve`, `web`, `tui`, `gui`, `msf`, `bounty`, `scope`,
`install`, `suggest`, `burp-import`, `evidence`, `report`, `jobs`, `ai`,
`cve`, `vulndb`, `lookup`, `validate`, `retest`, `coverage`, `recon`,
`findings`, `run`, `workflow`, and `state`. Only `workflow` enters Engine V2
capability and plan services. Of the assessment commands, `run`, `ai`, `recon`,
`validate`, and `retest` still use legacy execution/service ownership; `msf`
is an inspection CLI, while module/session execution remains on web/runner
legacy routes. Environment/bootstrap commands and read/report commands do not
become V2 assessment dispatch merely because they share the `whaxon` binary.

Installed terminal and desktop paths need a separate packaging check: `WhaxonApp`
and `EmbeddedServer` derive their data directory from the checkout-relative
package path rather than `WHAXON_DATA`; GUI starts `serve --daemon`. Their source
checkout behavior therefore does not establish installed-wheel data-path or
daemon support.

All `whaxon workflow` verbs call shared `Core` capability, policy, store,
scheduler or queue methods; only `plan run` and the durable request worker
dispatch providers. The remaining verbs are read or control-plane operations.
CLI `plan approval grant --actor` accepts a caller-supplied actor label, so that
label is not authenticated-principal evidence.

The CLI split also distinguishes three V2 execution modes: `workflow plan run`
uses the V2 scheduler/policy/provider path synchronously; `workflow plan
submit-run` plus `serve-requests` uses the durable request queue and supervised
worker; legacy `whaxon run`, `ai`, `recon`, `validate`, and `retest` remain
outside V2 task/request ownership. `workflow plan run` is not a legacy runner
dispatch, although it bypasses the durable run-request queue. The top-level
help omission for `recon` was corrected and is guarded by
`test_engine_v2_cli_surface.py`.

### G01 controlled solo-chain crosswalk

The release chain is scope → recon → enumeration → supported initial access →
independent verification → evidence/report → retest. Current source maps as
follows; the gaps below prevent a G01 pass.

| Stage | Current V2 path/evidence | G01 result |
| --- | --- | --- |
| Scope and bounded plan | Mission, typed plan/task, scope authorization, exact approval, limits and scheduler path in `Core`; see `test_workflow.py`, `test_providers.py`, and `test_engine_v2_e1_boundary.py`. | Implemented components; full cross-client and controlled-target acceptance is open under G02/G05. |
| Recon and enumeration | Admitted local-process providers listed above; fixed catalog argv goes through `ToolRunner`. | Provider contracts exist, but this local environment has no installed V2 binaries and none is smoke/lab/E2E verified. |
| Supported initial access | No initial-access provider is admitted to the V2 capability registry. `commix`, `impacket`, and MSF/session actions remain excluded or on legacy paths. | **Missing from V2.** The full release chain cannot currently exercise this stage through V2. |
| Independent verification | `Validator` supports legacy CLI/API validation and retest paths; they are outside the V2 scheduler and task/attempt ownership. | **Not integrated into V2 chain.** G03 acceptance remains open. |
| Evidence, report, retest | V2 exposes workflow evidence, audit and readiness; legacy validators and report/export paths still use job/finding state. | **No accepted end-to-end workflow report/retest proof.** G04/G05 acceptance remains open. |

Existing tests establish component and client behavior; none is the required
controlled full solo-chain run with retained, independently verified proof.
This assessment does not authorize adding or exercising high-impact initial
access against any target. The missing stage must be resolved through the
reviewed capability, consent, evidence and rollback contracts before G01 can
close.

This matrix is not G01 closeout. It records source mappings and a local
readiness snapshot; the required controlled full solo chain has not been
executed. Catalog/admission/transport changes are guarded by
`test_catalog_transports_and_v2_admission_are_explicit` in addition to the
runner and service callsite guards.

## Migration constraint

Do not redirect `/api/run`, `/api/ai/run`, CLI tool/session execution, recon, or
retest in bulk. The Run page consumes the current web route, AI uses a separate
operator-answer record, and the CLI exposes capability-specific options. Each
migration needs an explicit capability mapping and parity tests before retiring
the legacy caller. E6 remains frozen until the operator declares the UI ready.
