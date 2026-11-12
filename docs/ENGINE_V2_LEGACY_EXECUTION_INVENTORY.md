Warning: truncated output (original token count: 16865)
Total output lines: 613

# Engine V2 legacy execution inventory

This inventory records Python callsites that invoke `run_tool` or
`run_in_session` directly. It is guarded by
`tests/test_engine_v2_legacy_callsite_inventory.py`: adding, removing, or moving
a callsite requires reviewing its execution path and updating the classification.

| Source | Caller | Classification | Notes |
| --- | --- | --- | --- |
| `interfaces/web/server.py` | `_run_job_blocking` | Legacy | `/api/run`; scope checked, but no persisted V2 request or task lease. |
| `core/ai_bridge.py` | `_run_tool`, `build_executor._run_in_session` | Legacy | Used only by legacy `/api/ai/run` and explicit `whaxon ai --legacy` execution/resume; approvals remain in legacy `ai_runs`. The separate `propose_v2_workflow_plan` path creates reviewable plan tasks and does not dispatch. |
| `ai/executor.py`, `ai/providers/*` | Executor/provider actions | Legacy | Indirect callbacks still dispatch through `ToolRunner`. |
| `interfaces/cli/run_cmd.py` | default proposal path / `main._go` | Mixed; default V2 plan-only | `whaxon run <tool> <target>` saves a provider-pinned review plan after scope/readiness checks; it does not approve or execute. `--v2-plan` executes only a previously persisted and approved plan. Direct ToolRunner and session transports require explicit `--legacy`; there is no V2-to-legacy fallback. |
| `core/worker.py` | `drain_async` | Legacy | Drains Automator follow-up jobs outside workflow-plan authorization. |
| `interfaces/gui/main_window.py` | `_run_tool` | Legacy; dormant module | The shipped `whaxon-gui` entry point is `interfaces.gui.app:main` and embeds `/ui-v2`; repository search found no import of this older widget. The module remains packaged until documented downstream-import and clean-wheel checks permit removal. It is not the active desktop dispatch path. |
| `interfaces/tui/screens/main.py` | catalog Run handoff / workflow screen | Engine V2 workflow client | Catalog Run opens V2 authoring with tool and target prefilled. The workflow screen proposes fixed-tool and sealed-evidence plans, reviews task bindings, records per-task approval, submits durable requests, reconnects and requests cancellation through shared Core services. No direct ToolRunner call remains in the TUI. |
| `core/providers.py` | `dispatch` | Engine V2 | Canonical provider dispatch after workflow authorization and scheduler checks. |

The legacy routes already apply scope checks and tool validation. Their remaining
gap is lifecycle and policy parity: workflow-bound authorization, durable request
identity, task leases, plan-bound approval, cancellation, reconnect, and recovery.
This inventory is evidence of caller coverage, not a claim that those controls
are absent from every legacy path or that a migration is safe.

The workflow CLI also provides `plan propose-tool` for supported catalog tools.
It creates a fixed-argument, provider-pinned review proposal only after current
scope and provider readiness checks. Saving remains explicit; approval and
execution are separate commands. The default `whaxon run <tool> <target>` now
uses this proposal path and persists the plan; unsupported/session transports
remain available through explicit `--legacy` dispatch only.

`plan propose-verification` similarly prepares V2 verify/retest plans for
supported SQLi and reflected-XSS findings. The selected verifier rechecks the
source job's V2 execution marker, evidence seal, exact finding sequence, target,
and prior verification state for retests. This is a separate route for eligible
V2 evidence. Legacy CLI/API validator entry points now refuse V2-owned evidence
before sending a request or mutating its finding; legacy job behavior remains.
This does not add unsupported validator kinds or finish full validator client
parity.

The V2 Run builder admits the fixed-input, moderate-impact
`dns.recon.passive` provider when it is installed and selected. Its plan is
provider-pinned and remains unapproved and undispatched until the operator
reviews, approves, and submits it. Target preview uses the DNS-query scope
policy and accepts hostnames only; generic target checks retain the stricter
execution policy. The CLI also provides
`whaxon workflow plan propose-dns-recon --mission-id M --id P --target HOST`
with optional `--save`. The recon providers expose fixed-plan proposals for
headers, robots and `security.txt`; `propose-headers-recon` and
`propose-security-txt-recon` create pinned, unapproved plans for one fixed HTTPS
request each. Proposal creation never dispatches network work.

Additional execution actions need their own semantic inventory. CLI passive
recon and legacy-job CLI/API validate/retest callers still use dedicated legacy
services rather than `ToolRunner`. A separate V2 provider now covers
only sealed-finding SQLi verification/retest under a plan-bound contract; this
does not migrate those legacy callers or cover the other validator kinds.

## Dedicated network-service entry points

These paths can perform network work without calling `ToolRunner`. The
callsite guard pins their current production entry points separately from the
runner inventory.

| Source | Caller | Service path | Scope/consent boundary | Persistence and V2 status |
| --- | --- | --- | --- | --- |
| `interfaces/cli/recon_cmd.py` | `main` | `core.recon.run` → `ReconRunner.run` → registered DNS/TLS/HTTP checks | CLI checks scope before execution; `ReconRunner.run` checks scope again. No plan-bound approval or V2 task authorization. | `JobStarted`/`JobFindings` enter the legacy event bus and its store subscribers. Direct service execution; no V2 workflow request, lease, attempt or cancellation record. |
| `interfaces/cli/validate_cmd.py` | `main` | `Validator.validate` | V2-owned evidence is refused before target replay; legacy jobs still require target and active scope. | Legacy job updates remain in `JobStore`; V2 verification uses the plan-bound provider path. |
| `interfaces/cli/retest_cmd.py` | `main` | `Validator.revalidate` → `Validator.validate` | V2-owned evidence is refused before replay; legacy findings still require prior verification and current scope. | Legacy job updates remain in `JobStore`; V2 retest uses the plan-bound provider path. |
| `interfaces/web/server.py` | `create_app.api_validate` | `Validator.validate` | V2-owned jobs receive HTTP 409 before replay; legacy jobs still pass `_validation_scope_error` before the probe. | Legacy job updates remain in `JobStore`; V2 verification uses the plan-bound provider path. |
| `interfaces/web/server.py` | `create_app.api_retest` | `Validator.revalidate` → `Validator.validate` | V2-owned jobs receive HTTP 409 before replay; legacy findings still require prior verification and current scope. | Legacy job updates remain in `JobStore`; V2 retest uses the plan-bound provider path. |
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
| CLI workflow | `whaxon run`, default `whaxon ai`, `recon --engine v2 --plan-id`, and `whaxon workflow` use shared `Core` workflow/proposal/approval/provider services; `--v2-plan` executes an approved saved plan | `whaxon run --legacy`, `whaxon ai --legacy`, default `recon`, `validate`, and `retest` retain legacy execution; `whaxon msf` only inspects status/sessions/modules | Default AI goals save a scope-checked proposal and print separate review, approval and submission commands. AI `--resume` requires `--legacy`; `--approvals` is read-only. Recon defaults to the direct `ReconRunner` path; its V2 workflow path is opt-in through `--engine v2 --plan-id`. V2 plans, approvals, requests, tasks, events and evidence use `JobStore`/`WorkflowRunQueue`; see `test_run_cmd.py`, `test_recon_v2_cli.py`, `test_workflow_cli.py`, `test_workflow.py`, `test_workflow_run_requests.py`, and `test_providers.py`. |
| HTTP API and web clients | `/api/v2/ai/proposals`, `/api/v2/workflow-proposals`, workflow lifecycle APIs and V2 AI, Findings, BAS, Retest and Approvals clients use shared Core services | `/api/run`, `/api/ai/run`, `/api/ai/runs/<id>/answer`, `/api/msf/run`, `/api/msf/sessions/<id>/exec`, `POST /api/msf/sessions/<id>/portfwd`, `/api/validate`, `/api/retest` remain separate legacy paths for older clients; legacy AI and MSF execution routes require explicit environment opt-in | V2 AI/Findings/BAS/Retest/Approvals clients do not call legacy executor, answer, validation or retest mutations. Their legacy history is read-only; proposals and approvals remain separate from submission. MSF module launch, session commands, and port-forward creation are default-denied behind `WHAXON_LEGACY_MSF_EXECUTION_ENABLED=true`; port-forward deletion remains available for cleanup, separately from V2 lab plan approval. Other legacy APIs remain outside V2 request/task ownership. |
| Headless service | `whaxon serve` plus `whaxon workflow plan serve-requests` | Legacy worker/Automator follow-ups remain separate | V2 worker claims durable requests; see `test_workflow_continuous_worker.py`, E5 systemd and Docker tests. |
| Native desktop and terminal | `whaxon-gui` embeds `/ui-v2`; TUI workflow screen and catalog Run-to-plan handoff use shared V2 workflow services | The unreferenced older `interfaces/gui/main_window.py` retains direct `Core.runner` calls; no TUI catalog legacy action remains | Desktop destination/root-route behavior is covered by `test_gui_entrypoint.py`; see also `test_tui_main.py`. Clean-wheel desktop launch and broader UI acceptance remain open. |

### Consequential HTTP route ownership

`test_api_route_methods_and_handlers_are_explicit` pins the method, path and
handler binding for all Flask `/api/*` routes, including read/status/export
routes. The matrix below summarizes consequential ownership and authorization
boundaries; it does not claim to guard UI controls.

A static decorator census currently finds 104 `/api/*` method/path bindings,
22 distinct `/ui-v2/*` page handlers with 23 route aliases, and five other
health/root/settings/favicon routes in `interfaces/web/server.py`. The matrix below covers consequential
execution, authorization-state, cancellation and provisioning routes. This census makes every method/path/handle…6865 tokens truncated…from sdist; this is a checkout/source deployment path. |
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
worker; `whaxon run <tool> <target>` creates a saved plan but does not execute;
explicit `whaxon run --legacy`, `ai`, `recon`, `validate`, and `retest` remain
outside V2 task/request ownership. Recon defaults to its direct legacy runner; its V2 path
requires `--engine v2 --plan-id ID`. `workflow plan run` is not a legacy runner
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
retest in bulk. The Run and AI Gate pages now hand off to persisted V2 plans;
the legacy HTTP routes remain for older clients, CLI AI still uses separate
legacy run records, and recon retains its dedicated service. Each migration
needs an explicit capability mapping and parity before retiring the legacy
caller. UI-10 and broader E6 acceptance remain open.

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

The AI Gate page now uses the V2 proposal endpoint and hands saved plans to the
Run page. Default `whaxon ai "<goal>"` now creates and saves a scope-checked V2
proposal, then prints separate review, approval and submission commands. It
does not grant approval or submit a run. The old autonomous executor and
`--resume` path require explicit `--legacy`; `/api/ai/run` remains a legacy API
for existing clients. V2 AI action generation is still bounded to one
moderate-impact catalog action with an exact target and no dynamic arguments;
multi-step autonomous planning remains outside this migration slice.

The V2 Approvals page now reads `GET /api/v2/approval-queue` and grants
plan/task-bound, expiring consent through
`POST /api/v2/workflows/<plan_id>/approvals`. It never resumes a legacy AI
run: `/api/ai/pending` is displayed read-only, and
`POST /api/ai/runs/<id>/answer` remains available only for older clients.
Granting consent does not submit the separate V2 run request; blocked tasks
remain blocked and must be replanned.

The V2 Findings, BAS and Retest pages no longer call the legacy validation or
retest mutation routes. They hand off candidate findings for V2 verification
plans and verified findings for V2 retest plans. The server requires sealed V2
evidence and current scope before saving either plan. Legacy validation and
retest APIs remain available for compatibility clients; saved plans still
require review, approval, and separate run submission.

## Cancellation ownership boundary — 2026-11-11

`GET /api/jobs/active` now marks each row with its durable Engine V2 ownership.
V2 UI emergency-halt controls must cancel legacy rows through
`POST /api/jobs/<job_id>/cancel` and V2 runs through
`POST /api/v2/workflow-runs/<request_id>/cancel`. The legacy job-cancel route
rejects a marked V2 execution job with HTTP 409, so a client cannot bypass the
workflow plan's persisted stop barrier. Durable cancellation records a request
to stop; it does not prove that an already-dispatched external effect stopped.
The V2 request and its task outcomes may require reconciliation. This boundary
covers cancellation ownership; it does not migrate the remaining legacy
execution routes listed above.

## Recon capability parity ledger — 2026-11-12

`whaxon recon` defaults to the legacy execution boundary: it runs named protocol
checks directly in `ReconRunner`, gates the target with `ScopeManager`, then
publishes legacy `JobStarted`/`JobFindings` events. The `--engine v2 --plan-id`
route accepts only one matching fixed task and dispatches it through an approved
workflow plan. V2 providers are migrated individually; wrapping `ReconRunner.run()`
as a single V2 provider would preserve internal threads and legacy event writes
outside scheduler attempt ownership.

| Legacy check | Current behavior / output contract | V2 capability overlap | Parity |
| --- | --- | --- | --- |
| `dns` | Queries A, AAAA, MX, NS, TXT and SOA through dnspython; emits `dns_record` findings and per-query errors. | `dns.records.query` (`dig`) and `dns.records.enumerate` (`dnsrecon`) are admitted fixed-argv catalog providers. Dedicated `dns.recon.passive` provider implemented with fixed inputs and a supervised child process. | Catalog tools remain partial. The dedicated provider preserves the query/finding contract in source, but is not yet test-qualified or wired into the legacy CLI; no recon parity is claimed. |
| `ssl` | Connects to port 443, checks certificate validity, SANs and expiry; emits certificate/error findings. | No equivalent fixed V2 certificate-inspection provider. | Absent. |
| `headers` | Fetches the target (HTTPS first, HTTP fallback) and reports configured security headers missing from the response. | Dedicated `web.recon.headers` provider makes one root-path HTTPS GET, checks pinned scope inside a supervised child, reads only bounded response headers, and persists attempt-linked evidence. | Bounded HTTPS header observations are implemented and covered by focused tests; HTTP fallback and complete legacy parity/release qualification remain open. |
| `tech` | Detects server/framework markers from HTTP headers and emits technology/port findings. | `web.server.audit` may expose server banners among broader findings. | Not equivalent; no fixed technology-detection contract. |
| `robots` | Fetches at most 64 KiB from `robots.txt` and `sitemap.xml` without following redirects; emits disallowed paths, sitemap references and up to 100 sitemap URLs. | Dedicated `web.recon.robots` V2 provider makes only two fixed HTTPS GETs, checks pinned scope inside a supervised child, bounds parsing/output, and persists attempt-linked evidence. | Bounded provider is implemented and covered by source/tests; full legacy parity/release qualification remains open. |
| `security_txt` | Fetches `/.well-known/security.txt`, parses recognized RFC 9116 fields, and emits field observations or an informational missing/no-recognized-fields finding; it does not validate `Expires`. | Dedicated `web.recon.security_txt` V2 provider makes one fixed HTTPS GET, checks pinned scope inside a supervised child, bounds headers/body/output, and persists attempt-linked evidence. | Bounded provider is implemented and covered by focused tests; full legacy parity/release qualification remains open. |
| `cookies` | Fetches the target and audits `Set-Cookie` flags (`Secure`, `HttpOnly`, `SameSite`). | `web.server.audit` may report some cookie issues. | Not equivalent; no stable cookie-only output contract. |
| `redirects` | Manually follows at most 10 hops, records HTTPS-to-HTTP and cross-origin hops, and stops before contacting a new cross-origin destination. | Generic web providers may encounter redirects but do not expose this exact bounded chain contract. | Not equivalent. |
| `waf` | Fingerprints known WAF/CDN signatures from response headers and cookies. | No equivalent fixed V2 provider. | Absent. |
| `dns_full` | Checks CAA, DMARC and SPF posture and emits dedicated policy findings. | Dedicated `dns.recon.full` V2 provider makes only fixed CAA(host), TXT(_dmarc.host), and TXT(host) queries with DNS-query scope checks and bounded child execution. | Bounded provider is implemented and covered by focused tests; complete legacy parity/release qualification remains open. |

The legacy HTTP helpers use short per-request socket timeouts, and the DNS
resolver has a timeout setting. However, `ReconRunner` waits for its
`ThreadPoolExecutor` context to close; a scheduler timeout cannot guarantee
that a stuck Python thread has stopped. A V2 implementation therefore needs
hard-bounded execution ownership (for example, a supervised worker process)
before it can claim durable cancellation. The implemented headers, robots, security.txt, and dns_full providers select fixed inputs, recheck scope in supervised workers, and record results in attempt-linked evidence. Their broader release qualification remains open; absent checks still require separate migrations. The two DNS catalog capabilities are partial overlap, not recon parity. The first
`dns.recon.passive` implementation requires an explicit hostname scope rule
when IP/CIDR rules are configured; Core preflight avoids uncancellable DNS
resolution, then the provider repeats the full scope decision in its supervised
child before querying. Static syntax checks passed; tests were not run, so
runtime readiness, cancellation and evidence-seal behavior remain unqualified.
