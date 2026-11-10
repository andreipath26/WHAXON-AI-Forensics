Warning: truncated output (original token count: 13944)
Total output lines: 523

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
| `interfaces/cli/run_cmd.py` | `main._go` | Legacy | Default direct tool/session execution remains legacy. An explicit `--v2-plan` bridge executes only a previously persisted and approved plan through the shared workflow service; it does not silently fall back. |
| `core/worker.py` | `drain_async` | Legacy | Drains Automator follow-up jobs outside workflow-plan authorization. |
| `interfaces/gui/main_window.py`, `interfaces/tui/screens/main.py` | `_run_tool` | Legacy | Desktop and terminal clients still use direct dispatch. |
| `core/providers.py` | `dispatch` | Engine V2 | Canonical provider dispatch after workflow authorization and scheduler checks. |

The legacy routes already apply scope checks and tool validation. Their remaining
gap is lifecycle and policy parity: workflow-bound authorization, durable request
identity, task leases, plan-bound approval, cancellation, reconnect, and recovery.
This inventory is evidence of caller coverage, not a claim that those controls
are absent from every legacy path or that a migration is safe.

The workflow CLI also provides `plan propose-tool` for supported catalog tools.
It creates a fixed-argument, provider-pinned review proposal only after current
scope and provider readiness checks. Saving remains explicit; approval and
execution are separate commands. It does not cut over the default legacy
`whaxon run <tool> <target>` path or cover unsupported/session transports.

`plan propose-verification` similarly prepares V2 verify/retest plans for
supported SQLi and reflected-XSS findings. The selected verifier rechecks the
source job's V2 execution marker, evidence seal, exact finding sequence, target,
and prior verification state for retests. This is a separate route for eligible
V2 evidence; it does not migrate the legacy CLI/API validator dispatch or add
unsupported validator kinds.

Additional execution actions need their own semantic inventory. CLI passive
recon and the existing CLI/API validate/retest callers still use dedicated
legacy services rather than `ToolRunner`. A separate V2 provider now covers
only sealed-finding SQLi verification/retest under a plan-bound contract; this
does not migrate those legacy callers or cover the other validator kinds.

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

The legacy CLI/API validator paths remain separate from the bounded V2 provider.
For SQLi, the current replay uses three baseline and three injected samples
and verifies only when a specific SQL parser error appears consistently after
the quote probe. Missing proof, network failure and timing-only signals remain
`candidate`; legacy retest reports those as `inconclusive`. The SQLi path has
no `refuted` result, so it cannot currently establish `fixed`. Existing
validator tests use synthetic HTTP fixtures; they do not replace a seeded-lab
validation run for the scheduler-owned provider.

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

The separately bound HTTP verifier adds four V2-only operations outside the
local-process catalog table:

| Capability | Provider | Target and permission | Supported contract | Readiness |
| --- | --- | --- | --- | --- |
| `tool.verify_sqli` | `whaxon.verifier.http` (`v2-sqli-xss-verifier.1`) | IP-literal HTTP(S) URL; `network.verify`; moderate impact | A successful same-target Engine V2 SQLi finding with an intact workflow evidence seal; separate exact-plan approval; fixed quote probe; scope reload before each request; redirects and changed paths blocked; result stored as a separate sealed job. | Registered; smoke, lab and end-to-end flags remain false. |
| `tool.retest_sqli` | `whaxon.verifier.http` (`v2-sqli-xss-verifier.1`) | IP-literal HTTP(S) URL; `network.verify`; moderate impact | Requires a prior V2 `verified` result from `tool.verify_sqli`; reports `still_vulnerable` or `inconclusive`, never `fixed` when proof is absent; separate exact-plan approval and sealed result job. | Registered; smoke, lab and end-to-end flags remain false. |
| `tool.verify_xss` | `whaxon.verifier.http` (`v2-sqli-xss-verifier.1`) | IP-literal HTTP(S) URL; `network.verify`; moderate impact | A successful same-target Engine V2 reflected-XSS finding with an intact workflow evidence seal; separate exact-plan approval; unique non-destructive SVG console probe; scope reload before each request; redirects and changed paths blocked; result stored as a separate sealed job. | Registered; smoke, lab and end-to-end flags remain false. |
| `tool.retest_xss` | `whaxon.verifier.http` (`v2-sqli-xss-verifier.1`) | IP-literal HTTP(S) URL; `network.verify`; moderate impact | Requires a prior V2 `verified` result from `tool.verify_xss`; reports `still_vulnerable` or `inconclusive`, never `fixed` when proof is absent; separate exact-plan approval and sealed result job. | Registered; smoke, lab and end-to-end flags remain false. |

These operations require separate plans because their source job and finding
sequence must already exist when each task is authorized. The provider supports
SQLi and reflected-XSS validation only; timing and observation validators are
not registered. IP literals avoid DNS rebinding in the current urllib transport;
hostname verification remains unsupported until the transport pins the
validated destination address.

The built-in adapter registry also reports four adapter-only IDs—`burp`,
`hashcat`, `msf`, and `whatweb`—without packaged catalog entries. The prior
V2 allowlist declared `whatweb` even though no catalog item could bind it. The
allowlist and semantic alias map now exclude that stale declaration; the
catalog/transport guard will fail if the shipped catalog or admitted set drifts
without explicit G01 review. `echo` and `ssh_cmd` are catalog entries without a
registered adapter. Portfolio classification for non-admitted tools does not
replace this separate adapter-presence fact.

### Read-only live snapshot

The earlier local portfolio audit reported 24 catalog entries and 26 discovered
adapters: 12 bound, five not admitted, seven unsupported transports, and four
adapter-only. That snapshot preceded the two verifier operations. The current
Core inventory includes 12 compatibility capabilities, 12 semantic aliases,
and the two registered verifier operations; the verifier's smoke, lab and
end-to-end flags remain false. The earlier snapshot found **zero executable
providers**, with all 12 admitted binaries absent from that environment. These
are environment-specific readiness observations, not claims about a deployment
host. The audit command is read-only and explicitly does not enable execution.
A same-session executable preflight also found no Docker CLI
and none of the 12 admitted binaries (`arjun`, `dig`, `dnsrecon`, `ffuf`,
`gobuster`, `nikto`, `nmap`, `nuclei`, `sqlmap`, `theharvester`, `whois`,
`wpscan`) on this workspace host. No scanner, container or network operation
was attempted. This host therefore cannot supply the required controlled-lab
execution evidence; deployment-host readiness remains unverified.

### Client and service boundary summary

| Client surface | V2 path | Existing legacy path | Durable owner / relevant evidence |
| --- | --- | --- | --- |
| CLI workflow | `whaxon workflow` → shared `Core` workflow/approval/provider services | `whaxon run`, `ai`, `recon`, `validate`, and `retest` retain direct legacy execution; `whaxon msf` only inspects status/sessions/modules | V2 plans, approvals, requests, tasks, events and evidence use `JobStore`/`WorkflowRunQueue`; see `test_workflow_cli.py`, `test_workflow.py`, `test_workflow_run_requests.py`, and `test_providers.py`. |
| HTTP API | `/api/v2/capabilities`, `/api/v2/ai/proposals`, `/providers`, `/workflows`, `/workflow-runs` and related lifecycle routes call shared Core services | `/api/run`, `/api/ai/run`, `/api/msf/run`, `/api/validate`, `/api/retest` remain separate legacy paths | V2 route evidence: `test_server_workflow_v2.py`; legacy paths retain legacy job/AI state and are not all V2 request/task-owned. |
| Headless service | `whaxon serve` plus `whaxon workflow plan serve-requests` | Legacy worker/Automator follow-ups remain separate | V2 worker claims durable …5944 tokens truncated…opped or recovered. | `test_server_workflow_v2.py`, `test_workflow_run_requests.py`, `test_workflow.py` |
| Legacy AI answer | `POST /api/ai/runs/<run_id>/answer` writes the operator response to legacy AI-run state and may resume the legacy executor. | Not a V2 plan/task approval. The route ignores a client-supplied user identity and records its local actor behavior. | `test_server_ai.py::test_ai_run_answer_records_operator_response` |
| Legacy evidence mutation | `POST`/`DELETE /api/jobs/<job_id>/evidence[/<seq>]` writes/removes files and JobStore evidence rows. | Legacy job evidence, not V2 attempt-sealed evidence. | `test_server.py`, `test_server_ai.py` evidence note/delete cases |
| Bounty program import | `POST /api/bounty/import` fetches or parses source and returns a disabled review-required draft. | Ingestion only; draft is not persisted as authorization and does not activate testing. | `test_web_bounty_ingest.py`, `test_bounty_ingest.py` |
| Burp report import | `POST /api/import/burp` parses uploaded XML, creates a legacy job and persists imported findings. | User-supplied evidence import; no target dispatch and no V2 attempt/evidence seal. | `test_server.py::test_burp_import_route_persists_imported_findings`, plus invalid-upload cases |
| Dependency checks and local config | `POST /api/dependencies/verify`, `/snapshots`, `/plan` run bounded local checks, save a local snapshot, or create a remediation preview; `POST /api/settings` persists application settings. | Not target assessment or V2 capability execution. Settings are configuration state, not target authorization. | `test_dependencies.py`, `test_dependency_installer.py`, `test_server.py` settings/dependency cases |

The V2 and legacy mutations above have different actor, persistence and
evidence contracts. V2 approval and attempt-reconciliation routes derive their
audit actor from the local peer identity or the username on a Basic-auth request
that has passed the shared request gate; legacy `actor` body fields are ignored
for compatibility. A remote username identifies the configured authenticated
account, not a distinct role or independent approver. Attempt-cost `source`
remains caller-supplied metadata and is not provider-origin proof. The route map
is source/test traceability; unresolved trust and authorization acceptance
remains open under the relevant later gates and must not be inferred from route
registration alone.

### Deployment entry points and readiness semantics

| Entry point or report | Current source behavior | G01 limit |
| --- | --- | --- |
| `whaxon web` | `server.main` starts Flask's development server. | Development path; not the production serving mode. |
| `whaxon serve` | `interfaces/web/serve.py` starts Waitress in foreground; `--daemon` uses `os.fork` double-fork. | Daemon mode is Unix-specific in source; do not infer native Windows support from OS documentation. |
| systemd | `whaxon.service` uses Gunicorn with `create_app_factory()`; paired worker unit runs durable request polling. | Unit contract and CI are not a successful supported-host install or live worker verification. |
| `docker-compose.e5.yml` | Repository-source web and dedicated worker share `/data`; host-published port `5001` is bound to `127.0.0.1` (the app listens on `0.0.0.0` inside the container). | Distinct from root `docker-compose.yml`, which is the vulnerable lab target. Docker assets are excluded from sdist; this is a checkout/source deployment path. |
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

| Workflow command group | Ownership and effect | Existing CLI/domain evidence |
| --- | --- | --- |
| `capabilities`, `providers`, `portfolio-audit` | Read-only registry, live provider and catalog/adapter portfolio views. | `test_workflow_cli.py`, `test_providers.py` |
| `mission create/list/plans`, `cost`, `cost-limit`, `rate`, `rate-limit`, `deadline`, `limits`, `budget` | Shared Core mission state and policy limits; no target dispatch. | `test_workflow_cli.py`, mission enforcement cases in `test_workflow.py` |
| `plan save`, `followups`, `show` | Validate/persist a plan, propose followups, or inspect state; no provider dispatch. `followups --save` only persists a new unapproved plan. | CLI coverage in `test_workflow_cli.py`; `test_engine_v2_followups.py`; core plan tests in `test_workflow.py`. |
| `plan approval list/grant/revoke`, `record-cost`, `cancel`, `reconcile`, `rate-limit`, `deadline`, `limits` | Consent, accounting and lifecycle control-plane mutations. Approval actor identity supplied as CLI text is not authenticated identity. | Approval, cancel, recovery and limit tests in `test_workflow_cli.py` and `test_workflow.py`. |
| `plan readiness`, `evidence`, `report`, `resources`, `audit`, `audit-snapshot`, `audit-verify`, `attempts`, `progress`, `events`, `event-inbox`, `event-ack`, `reconciliation-report` | Persisted diagnostics and evidence views; `report` renders only attempts linked to its named plan and marks failed, incomplete or unsealed evidence partial. It does not collect arbitrary job IDs or call the legacy engagement report. `event-ack` advances a consumer cursor but does not dispatch. | `test_workflow_report.py`, `test_workflow_cli.py`, `test_engine_v2_e3_audit_cli.py`, `test_workflow.py`. |
| `plan submit-run`, `serve-requests`, `drain-requests`, `queue-summary`, `run-request`, `run-snapshot`, `cancel-request` | Durable request queue and supervised worker lifecycle; submit returns queued state and does not assert completion. | `test_workflow_run_requests.py`, `test_workflow_continuous_worker.py`, `test_workflow_cli.py`. |
| `plan run` | Synchronous V2 Core workflow execution through policy, provider binding, scheduler and task attempts; does not create a durable run-request record/worker lease. | `test_workflow_cli.py::test_workflow_cli_runs_headless_without_draining_legacy_jobs`, `test_providers.py`, `test_workflow.py`. |

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
| Supported initial access | `lab.initial_access.samba_usermap` is a registered critical-impact provider restricted to the checked-in Metasploitable2 target `172.28.0.10`, fixed module `exploit/multi/samba/usermap_script`, fixed payload `cmd/unix/reverse_netcat`, and callback `172.28.0.11:4444`. It accepts no dynamic task inputs; requires `WHAXON_ENABLE_V2_LAB_INITIAL_ACCESS=1`, a scope reload/check, and exact plan-bound critical approval. It creates local evidence before dispatch, records the remote MSF job ID, accepts only a newly created matching session and stops that session if local evidence persistence fails. Normal success leaves the session open for operator follow-up; the G01 CI harness closes its session in `finally`. | **Implemented, not accepted.** Fake-client contract tests cover fixed options, opt-in, target, scope reload, RPC binding, non-reuse of pre-existing sessions, and evidence-failure cleanup. The isolated `docker-compose.g01-lab.yml` pins the target image and Rapid7 Metasploit Framework 6.5.4 image, places the RPC runner at `.11` with MSF RPC bound to loopback, and places the seeded boolean SQLi fixture in the `.10` target's network namespace, so recon, enumeration, initial access, verification and retest share the same IP. The mission aggregate now normalizes and requires one target identity across all stage plans. CI checks and retains the mission JSON plus a SHA-256 sidecar. Rapid7 source review checked the selected module, payload, session metadata/stop RPC and daemon flags. Exact-head CI #2157 exposed Compose credential ordering, SQLmap final confirmation and report typing issues; those are fixed. Actual image startup, callback/RPC connectivity, module compatibility and the complete chain remain unverified until the latest exact-head CI passes. Do not claim lab success before then. |
| Independent verification | `tool.verify_sqli`/`tool.retest_sqli` and `tool.verify_xss`/`tool.retest_xss` run bounded SQLi or reflected-XSS probes as approved V2 scheduler tasks, require a successful same-target V2 finding of the matching kind with a valid evidence seal, and write separate sealed result jobs. Every HTTP request rechecks scope and exact URL path; only IP-literal targets are accepted to avoid DNS rebinding. | **Partial.** Timing/observation paths are not covered; each operation requires a separate plan and neither verifier family has been independently lab-validated. G03 remains open. |
| Evidence, report, retest | `Core.workflow_report` and `whaxon workflow plan report --id PLAN` render only persisted evidence linked to one named plan, excluding unsealed findings and marking failed, incomplete or truncated attempts partial. Scheduler-owned SQLi/XSS verification and retests each produce sealed jobs. | Component paths are implemented, but no accepted end-to-end chain/report/retest proof exists; legacy export/report parity also remains open under G04/G05. |

`Core.workflow_mission_report` and `whaxon workflow mission report --id MISSION`
aggregate only plan IDs persisted under that mission (or an explicitly
selected subset of those plans). Required order is scope → recon → enumeration
→ initial access → verification → report → retest. Scope is rechecked against
each immutable plan's exact task authorization and readiness; stage plans must
have complete reports with recorded, integrity-verified attempts. The aggregate
itself supplies the report stage after sealed verification evidence, so no
synthetic report plan or arbitrary job ID is accepted. A partial/missing stage,
failed authorization/readiness check, truncated report, or unsealed attempt
keeps the result partial. This is chain-report evidence only, not G01 acceptance
or production deployment approval. See `tests/test_workflow_mission_report.py`.

Existing tests establish component and client behavior; none is the required
controlled full solo-chain run with retained, independently verified proof.
The opt-in provider is limited to the repository's exact lab target and plan
approval; its presence does not establish working target compatibility or
authorize any other target. G01 remains open until its topology, execution,
evidence retention and complete chain satisfy controlled-lab acceptance.

This matrix is not G01 closeout. It records source mappings and a local
readiness snapshot; the required controlled full solo chain has not been
executed. The initial-access provider is not accepted based on fake-client
tests; the `.11` callback and loopback MSF RPC endpoint must be reachable in
the deployed lab topology, and the fixed Samba module must open a matching
session on the actual `.10` image. Catalog/admission/transport changes are guarded by
`test_catalog_transports_and_v2_admission_are_explicit` in addition to the
runner and service callsite guards.

## Migration constraint

Do not redirect `/api/run`, `/api/ai/run`, CLI tool/session execution, recon, or
retest in bulk. The Run page consumes the current web route, AI uses a separate
operator-answer record, and the CLI exposes capability-specific options. Each
migration needs an explicit capability mapping and parity tests before retiring
the legacy caller. E6 remains frozen until the operator declares the UI ready.

## AI-to-V2 proposal boundary

`whaxon workflow plan ai-propose` and `POST /api/v2/ai/proposals` convert one
legacy AI `Action` into a reviewable, single-task V2 plan. They reject
out-of-scope targets before invoking the provider and expose only installed
and selected moderate-impact catalog providers, and pin the current manifest
fingerprint. The proposal requires the AI target to exactly match the
operator-supplied target and rejects session actions or dynamic arguments.
`--save` or API `save: true` persists the immutable plan; neither grants
approval, submits a run request, or dispatches work. Operators use the existing
plan approval and run-request commands separately.

This adds the V2 proposal API but does not migrate `whaxon ai`, `/api/ai/run`,
or the legacy Executor loop. Those callers still dispatch through the legacy AI
bridge and remain in the inventory above until their lifecycle and client
parity work is completed.
