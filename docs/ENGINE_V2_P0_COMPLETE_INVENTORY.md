# Engine V2 P0 — Current capability, caller, and deployment inventory

**Review date:** 2026-11-28  
**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Second-pass branch base:** `8e938fe65790af3954c5613e05904a00e42268a8`  
**Latest main observed during review:** `e90c11fd24d489815840dc28a00db14bd04aaec5`  
**Evidence cutoff:** 2026-11-28 11:44 UTC. Main includes merged PR #274 and PR #279; open PR #278 is tracked separately below. This branch is documentation-only and based on the earlier main SHA shown above.  
**Disposition:** P0 inventory is documented, but evidence gaps remain; this is not runtime qualification, approval to execute against a target, or a release decision. Repository release status remains **HOLD**.

## 1. Evidence method and limits

The inventory was built from the current GitHub source tree, including the top-level CLI dispatcher, CLI mode CSV, provider bridge and manifests, route and callsite inventory guards, workflow and run-queue services, adapter registry, deployment files, and the cited tests. This pass did not execute code, install a package, invoke a scanner, connect to a target, or read a deployment host. Local binary availability recorded in the older execution-path inventory is environment-specific and is not evidence for a release host.

A source declaration, catalog entry, adapter registration, importable module, route, test name, or provider manifest does not alone prove that a path is installed, executable, secure, lab-validated, or ready to deploy. Readiness levels are distinct: **registered → installed → smoke-tested → lab-validated → end-to-end verified**. Authorization is a separate dispatch-time decision.

## 2. Product and support boundary

| Surface | Current disposition | Authorization and state owner | Evidence and limit |
|---|---|---|---|
| Engine V2 plan workflow | Supported implementation surface: mission/plan authoring, validation, approval grants, run requests, task attempts, status, audit, evidence, reconciliation and reports are owned by shared Core/workflow services. | Scope policy plus exact persisted-plan/task approval; Core and workflow SQLite stores. A proposal or accepted queue request is not execution success. | `core/workflow.py`, `core/workflow_proposals.py`, `core/workflow_requests.py`, `core/providers.py`; `test_workflow.py`, `test_server_workflow_v2.py`, `test_workflow_run_requests.py`. Full client parity and deployment acceptance remain open. |
| Local-process catalog | Bounded V2 surface of 12 fixed-argument tool providers, detailed in §3. | Scope checked and reloaded at dispatch, deterministic capability/provider binding, exact-plan approval and bounded ToolRunner process execution; persisted V2 attempts/evidence. No dynamic argv or automatic legacy fallback. | `core/providers.py`, `core/provider_execution.py`, catalog bridge/provider tests and legacy inventory guard. A catalog/provider selection is not proof the binary exists or has passed a controlled lab. |
| Fixed recon providers | Bounded, independently implemented observations in §4. | Fixed provider input and destination constraints, DNS/network scope mode, supervised execution where implemented, approval and workflow persistence. | `core/*_v2.py`; focused provider tests and recon plan proposal tests. Legacy recon parity and release qualification remain open; redirect provider is first-hop only. |
| Verification and retest | Six separately planned V2 operations in §5. | Requires same-mission/same-target supported V2 evidence, intact seal and separate plan approval; fixed bounded requests. | `core/providers.py`, `core/validator.py`, `test_engine_v2_finding_verification.py`, `test_validator_security_regressions.py`, `test_validator_retest.py`. Provider smoke/lab/end-to-end release flags remain false in the reconciled source inventory. |
| Legacy V1 execution | Compatibility only; excluded from the V2 attempt/authorization guarantees unless individually migrated and qualified. | Explicit legacy selection and named feature gates where applicable; legacy stores and event paths remain separate. | `docs/ENGINE_V2_LEGACY_EXECUTION_INVENTORY.md`, `tests/test_engine_v2_legacy_callsite_inventory.py`, `tests/test_legacy_gui_execution_gate.py`. |
| Catalog-only / adapter-only / import-only | Not V2 executable unless a bound V2 provider and readiness state explicitly say so. | No V2 approval may be inferred from adapter registration or import. | See §3 and `docs/ENGINE_V2_LEGACY_EXECUTION_INVENTORY.md`. |
| Session transports | Explicitly excluded from the V2 release surface: Metasploit, SMB, SSH, and WMI session execution. | Legacy-only and separately gated; no V2 plan/attempt evidence. Metasploit module dispatch is disabled by the current server helper (returns false); legacy inventories that describe it as enabled behind a flag are stale and must not be used as current behavior. | `core/runner.py`, `interfaces/web/server.py`, `interfaces/cli/msf_cmd.py`, `test_engine_v2_legacy_callsite_inventory.py`, `test_server_msf.py`. |
| Research / information integrations | CVE, vulnerability database, bounty import, Burp import, model/provider catalogs and suggestions are informational, planning, or import surfaces unless explicitly routed to an admitted provider. They do not establish target observations or execution authorization. | Local cache, legacy records, or proposal stores according to the individual command. | `interfaces/cli/*_cmd.py`, `test_bounty_cmd.py`, `test_burp`/finding tests, `test_cve_cmd.py`, `test_vulndb_cmd.py`. |

## 3. Catalog and adapter reconciliation

The packaged catalog contains 24 IDs: 17 declared `cli` entries, three `msf_session`, two `smb`, one `ssh`, and one `wmi`. Only the 12 rows below are admitted through the Engine V2 catalog bridge. Each has a compatibility ID `tool.<id>` and the stable semantic operation listed below; both resolve to the same fixed local-process provider. The aliases do not add execution permission.

| Catalog tool | Semantic capability | Target types | V2 status / constraints |
|---|---|---|---|
| `arjun` | `web.parameters.discover` | URL | Admitted fixed argv; moderate network impact; scope/approval required. |
| `dig` | `dns.records.query` | Hostname | Admitted fixed argv; DNS-query scope and approval required. |
| `dnsrecon` | `dns.records.enumerate` | Hostname | Admitted fixed argv; DNS/network scope and approval required. |
| `ffuf` | `web.paths.fuzz` | URL | Admitted fixed argv; network impact and exact approval required. |
| `gobuster` | `web.directories.enumerate` | Hostname, IP | Admitted fixed argv; network impact and exact approval required. |
| `nikto` | `web.server.audit` | Hostname, IP, URL | Admitted fixed argv; network impact and exact approval required. |
| `nmap` | `network.services.discover` | Hostname, IP | Admitted fixed argv; network impact and exact approval required. |
| `nuclei` | `web.templates.assess` | URL | Admitted fixed argv; network impact and exact approval required. |
| `sqlmap` | `web.sql_injection.assess` | URL | Admitted fixed argv; potentially consequential network requests; separate approval required. |
| `theharvester` | `osint.domain.contacts.search` | Hostname | Admitted fixed argv; outbound OSINT provider behavior still requires qualification. |
| `whois` | `domain.registration.lookup` | Hostname, IP | Admitted fixed argv; external lookup behavior still requires qualification. |
| `wpscan` | `web.wordpress.audit` | URL | Admitted fixed argv; network impact and exact approval required. |

Declared target support is a manifest constraint, not a claim that all target forms or behavior have passed a lab test. Any successful process exit is an observation, not independent finding verification. Provider qualification and real external-effect recovery remain assigned to P2-B.

The non-admitted catalog entries are explicitly dispositioned as follows:

| IDs | Classification / disposition |
|---|---|
| `commix` | CLI catalog/legacy adapter may exist; excluded from V2 solo release and cannot be dispatched through V2 plans. |
| `echo` | Test-only fixture; not an assessment capability. |
| `hydra` | Legacy/catalog and adapter presence does not admit credential attacks to V2; excluded from V2 solo release. |
| `impacket`, `netexec` | Legacy/catalog/adapter surface; excluded from V2. No broad protocol toolbox is represented as an admitted capability. |
| `msf_getuid`, `msf_hashdump`, `msf_sysinfo` | Catalog-only session tools; unsupported as V2 transports. |
| `smb_ls`, `smb_shares`, `ssh_cmd`, `wmi_exec` | Catalog-only/session transport entries; unsupported as V2 transports. |

The adapter registry also discovers built-in parsers and Python entry points; parsing support can exist without a V2 provider. The repository has adapters for Burp/HTTP archive inputs, Hashcat, Impacket, Metasploit, session protocols, and some catalog tools. These are not promoted to V2 execution by parser availability. The inventory guard in `tests/test_engine_v2_legacy_callsite_inventory.py` protects direct runner calls, external effect sinks, catalog transport mapping, V2 admission, and semantic aliases. `tests/test_adapters_*.py`, `test_plugin_discovery.py`, and individual adapter tests protect bounded parsing/registration behavior only.

## 4. Fixed recon and observation paths

| Capability family | Current bounded V2 implementation | Known limit / readiness boundary |
|---|---|---|
| DNS passive/full posture | `dns.recon.passive`, `dns.recon.full`; separately `dig`/`dnsrecon` catalog operations | DNS query scope applies; catalog overlap is partial, not legacy `ReconRunner` parity. |
| TLS certificate | `tls.certificate.inspect` via `core/tls_cert_v2.py` | Fixed port 443, pinned scope addresses and supervised child; legacy output parity and end-to-end qualification remain open. |
| HTTP passive profile | `web.recon.passive`, with bundled header, technology, cookie and WAF observations from one fixed HTTPS request | Fixed signature set; no independent request per bundled check; no HTTP fallback; legacy parity remains open. |
| Header-only | `web.recon.headers` | Bounded HTTPS header observations; no full legacy HTTP fallback. |
| Robots / sitemap | `web.recon.robots` | Fixed HTTPS GETs, bounded body and output, no redirect following; legacy parity remains open. |
| Security.txt | `web.recon.security_txt` | Fixed HTTPS GET and bounded parser; not a general web fetcher. |
| Redirect observation | `web.recon.redirect_observe` | One root GET, records sanitized first Location and never follows it; not multi-hop redirect parity. |

Recon CLI default mode creates a reviewable plan from ready fixed providers and reports omitted checks; it does not approve or execute. An explicit V2 plan submission still needs approval and the supervised workflow worker. Legacy recon requires explicit `--legacy` plus its legacy feature flag; it remains outside V2 lifecycle/evidence guarantees. Tests: `test_recon_v2_cli.py`, `test_engine_v2_recon_plan_proposal.py`, `test_dns_full_v2.py`, `test_tls_cert_v2.py`, `test_headers_v2.py`, `test_http_recon_v2.py`, `test_robots_recon_v2.py`, `test_security_txt_recon_v2.py`, `test_redirect_recon_v2.py`.

## 5. Verification operations

| Operation | Admission requirement | Outcome boundary |
|---|---|---|
| `tool.verify_sqli` / `tool.retest_sqli` | Same-target, sealed V2 SQLi source evidence; retest requires a prior verified result. | Fixed quote probe; blocked redirects/path changes; lack of proof is inconclusive, never fixed. |
| `tool.verify_xss` / `tool.retest_xss` | Same-target, sealed V2 reflected-XSS source evidence; retest requires a prior verified result. | Fixed unique non-destructive probe; lack of proof is inconclusive, never fixed. |
| `tool.verify_http_observation` / `tool.retest_http_observation` | Supported sealed HTTP observation and prior verified result for retest. | Bounded same-target checks; unsupported evidence remains unsupported/inconclusive. |

These are provider registrations and bounded contracts; the current provider inventory still marks provider smoke, lab and end-to-end acceptance false. Do not convert a registration or passing unit test into a deployment-ready claim. Security and outcome-state qualification are tracked in P1.

## 6. Clients, routes, and workflow ownership

| Client / command surface | Current owner and behavior | Persistence / guard evidence |
|---|---|---|
| CLI default / TUI | Defaults to TUI; workflow screen is a V2 client, catalog Run hands off to reviewable plan authoring. | Starts read-only; supported actions use shared workflow stores; `test_tui_workflows.py`, `test_engine_v2_cli_mode_inventory.py`. |
| CLI `run`, `ai`, `recon`, `workflow`, `validate`, `retest` | V2 defaults author plans; run submission requires a separately approved persisted plan. Legacy direct execution/resume is explicit and separate. | Workflow state persists in shared Core stores; CLI mode inventory CSV + AST guard and command-specific bridge tests. |
| CLI supporting commands | `setup`, `doctor`, `init`, `up/down`, `scope`, `install`, `msf`, bounty/import, evidence/report/jobs/findings/coverage/suggest, CVE/vulndb/lookup, state and help modes. Their CSV rows classify them as setup/read-only/legacy/import/report services, not V2 execution. | Per-mode persistence, limit and tests are recorded in `docs/ENGINE_V2_G01_CLI_MODE_INVENTORY.csv`; `test_engine_v2_cli_mode_inventory.py` compares dispatcher literals, source files, regression-guard references and inventory rows. |
| V2 HTTP API and browser UI | API workflow methods use shared Core services. `/ui-v2` is the supported desktop web client; 22 page handlers/23 aliases are inventoried. The static control inventory is 808 controls across 22 templates, but controls and pages are not thereby accepted. | Workflow state is durable; route contract tests include `test_server_workflow_v2.py`, `test_workflow_run_requests.py`, route method/handler guard and per-page `test_web_ui_v2_*.py`. Full per-control wiring/parity remains open. |
| Retired HTTP compatibility routes | `POST /api/run`, `/api/ai/run`, `/api/ai/runs/<id>/answer`, `/api/validate/<job>/<seq>`, and `/api/retest/<job>/<seq>` return HTTP 410 with no dispatch/resume/mutation. Legacy human-resolution rejects V2-owned finding mutation with HTTP 409. | `test_server.py`, `test_server_ai.py`, `test_validator_retest.py`, `test_engine_v2_legacy_verification_store.py`. |
| Desktop entry | Shipped `whaxon-gui` embeds `/ui-v2`. Older `interfaces/gui/main_window.py` remains in package but is dormant and direct execution is default-denied behind an explicit gate. | `test_gui_entrypoint.py`, `test_legacy_gui_execution_gate.py`; clean-install launch acceptance remains open. |
| Headless worker | `whaxon workflow plan serve-requests` is the supervised durable V2 request worker; `drain-requests` is the bounded operator drain. | Request, claim, lease, heartbeat and uncertain-result state persist; lease fencing and no-blind-replay tests include `test_workflow_continuous_worker.py`, `test_engine_v2_e5_request_lease_ownership.py`, `test_engine_v2_e3_recovery_boundaries.py`. |
| Legacy worker / Automator | Separate legacy queue and fixed follow-up behavior; does not gain V2 plan authorization or evidence by being present. Long-running legacy drain is gated. | Legacy JobStore state; `test_autochain_durable.py`, `test_initialize_drain.py`; migration/parity is open in P2-A. |

The route count is reconciled against `test_engine_v2_legacy_callsite_inventory.py`: its `EXPECTED_API_ROUTE_HANDLERS` mapping and the documented exact method/path/handler table both contain 115 `/api/*` method/path bindings at this source baseline. The older inventory's prose counts of 104 and 105 were stale summary values; they are corrected to 115 on this branch. The route census proves static route registration only, not authorization or behavior.

## 7. Transports, external effects, and deployment modes

- **V2 transport:** local process for the admitted catalog; bounded supervised local providers for fixed network observations/verification. Only the pinned provider bound to the reviewed task may dispatch.
- **Not V2 transports:** Metasploit session, SMB, SSH, WMI; catalog entries remain unsupported for V2. The `echo` command is test-only.
- **AI model providers:** local Ollama plus remote OpenAI, Anthropic, and Google backends exist for proposal/advisory or legacy AI paths. AI output is not an authorization, policy, or provider selection authority. The HTTP route for AI execution is retired; advisory communication/inference is distinct from scanner dispatch. No inference backend is required for deterministic V2 execution.
- **External tools and effects:** ToolRunner subprocesses; fixed recon sockets/HTTP/DNS providers; verification HTTP; legacy Metasploit RPC/session, legacy recon, dependency installers, reporting lookups, and information caches. Static sink inventory names exact callsites; dynamic effects are outside a static census and need runtime/effect qualification.
- **Network egress:** fixed V2 providers constrain destinations/inputs and scope-check; generic legacy tools or optional external model endpoints do not inherit those guarantees. Deployment egress firewalling and external-tool secondary-request behavior remain unqualified.
- **Deployment forms:** foreground web/CLI; systemd web + separate workflow worker; Docker Compose web + worker with shared state; desktop GUI embedding web UI; CLI/TUI client. Readiness health checks local writable Core state/SQLite and optional Metasploit status; they do not prove worker liveness, provider installation, authorization, safe egress, backup integrity, or deployment acceptance. Docker/systemd source tests are not host install evidence.

Evidence files/tests: `docs/ENGINE_V2_E5_SERVICE_READINESS.md`, `docs/ENGINE_V2_E5_CALLER_INVENTORY_AND_ROLLBACK.md`, `tests/test_engine_v2_e5_core_readiness.py`, `test_engine_v2_e5_docker_compose.py`, `test_engine_v2_e5_systemd_deployment.py`, `test_engine_v2_e5_backup_restore.py`. See P3 for package, host, and headless operational qualification.

## 8. Ownership and open boundaries

| Work area | Operational owner | Source / evidence boundary |
|---|---|---|
| Mission, task, approval, scheduler, persistence | Core/workflow maintainers | `core/workflow*.py`, workflow request/store services; API and CLI are clients. |
| Provider manifests, binding, external-effect recovery | Provider maintainers | `core/capabilities.py`, `core/providers.py`, per-provider implementations and E4/E5 tests. Provider-specific qualification stays open. |
| Scope, trust, verification, evidence | Security/trust maintainers and independent deployment reviewer | Scope/policy, verifier and audit/evidence services; automated tests do not replace the independent deployment trust anchor. |
| CLI, API, UI, GUI, TUI | Client maintainers | Client surfaces may author/approve/observe through Core services but must not own hidden dispatch. UI per-control acceptance remains open. |
| Packaging, worker services, deployment configuration | Release/operator owner | Setup, systemd, Docker, backup/restore and exact-head CI; no production deployment decision exists in this inventory. |
| Legacy compatibility and retirement | Core + affected client owner | Every remaining direct dispatch sink remains explicitly legacy or excluded until migrated, retired, or approved as out of V2 scope with rollback evidence. |

The functional owner roles below are assigned for inventory and close-out accountability; they are verifiable against the named source trees and evidence files but are not GitHub team identities. `.github/CODEOWNERS` currently names `@andreipath26` only for README and its freeze workflow, so it does not enforce these subsystem roles. Record a named reviewer/operator for each applicable G01–G10 gate before external qualification.

## 9. CI baseline and capability/readiness evidence snapshot

Evidence was refreshed from GitHub Actions on 2026-11-28 at approximately 11:44 UTC. A green PR-head workflow is evidence for that exact source head and its named matrix only; the merged main commit e90c11f... has no combined status contexts returned by the GitHub status endpoint in this snapshot. Do not promote a successful PR job or a catalog row into a global deployment claim.

| Change / exact source head | PR state | CI run outcome | What the matrix actually exercised |
|---|---|---|---|
| P0 inventory PR #277 / 0c74831152f8dec3a6045ef1838d1cd25ea6260a | Merged | CI #46137652419: 20/20 jobs succeeded; README freeze #46137652401 succeeded. | Python 3.11–3.13 test jobs, Linux/macOS/Windows setup smoke, G01 controlled-lab chain, E1 regressions, systemd, Docker web/worker, headless Linux, package upgrade and install jobs. |
| P1 authorization PR #274 / ba4a75c1c9017c7f686b52341bee4b45b54d3bd3 | Merged as 8e938fe65790af3954c5613e05904a00e42268a8 | CI #46140276808: 21/21 jobs succeeded; README freeze #46140276802 succeeded. | Full Python 3.11–3.13 test jobs, scope/dispatch-boundary regressions, G01 lab, apt/Homebrew/setup smokes, Windows setup, systemd, Docker, headless, SearchSploit, upgrade matrix and clean/offline install. This is exact PR-head evidence; no separate combined status contexts were returned for the merged main SHA. |
| PR #279 rate-limit test isolation / 244602008be4e46d67a3e0a04038d71ed51307ff | Merged into current main | CI #46140812530: 21/21 jobs succeeded; README freeze #46140812589 succeeded. | Python 3.11–3.13 tests (including the server rate-limit regression), G01, E1, systemd, Docker, headless, install and upgrade matrix. |
| PR #278 provider qualification, earlier head 22fbff4c25842a018b3c4ab599a91ffd8ded1ab9 | Superseded; PR remains open | CI #46140843666: cancelled, with 14 successful, 2 failed, and 5 cancelled jobs; README freeze passed. | Apt provider smoke failed at Gobuster version query (No help topic for 'version'). Homebrew smoke failed during real Gobuster cancellation/restart setup because an immutable workflow plan ID was reused. Its expected smoke artifact was not uploaded. This run is failed/incomplete evidence, not provider qualification. |
| PR #278 current head b30715c9289220e49fce238c77953d5339649b42 | Open | CI run #46141251306 had 5 succeeded, 6 in progress, 10 queued at cutoff; README freeze #46141251300 succeeded. Workflow-level API status still reported queued. | The revised provider smoke and remaining CI jobs had no final outcome at cutoff. Do not assume the earlier failures are fixed or that the revised run passed. |
| Current main e90c11fd24d489815840dc28a00db14bd04aaec5 | Current branch | Combined status returned no contexts; commit-workflow lookup returned no PR-triggered run. | Main contains the merged #274 and #279 source. PR-head runs above are the available evidence; a final release candidate still needs exact-head verification. |

### Compact capability and readiness matrix

The following states are intentionally separate: registered is code/catalog admission; installed requires a specific runtime host; smoke-tested, lab-validated, and end-to-end verified require retained evidence for their named scope. Unknown means no current evidence, while not qualified is a release disposition. CI unit/parser tests do not prove a scanner binary is installed or that its external effect is safe.

| Capability family | Registered/admitted | Test evidence on exact reviewed PR heads | Installed at deployment target | Smoke | Lab | End-to-end / deployment |
|---|---|---|---|---|---|---|
| 12 fixed local catalog providers (next table) | Registered in the current provider bridge; only 12 of 24 catalog IDs are admitted. | CI #46140276808 passed the three Python test jobs and provider/unit suites. #278 attempted real loopback smoke for Nmap, Gobuster, ffuf and SQLmap, but the first run failed/cancelled and the revised run is pending. | Unknown | No completed provider-qualification run at cutoff; prior attempt failed and produced no artifact. | A G01 controlled chain passed, but it is not individual qualification of all 12. | Not qualified as a complete portfolio; external-provider behavior and deployment-host readiness unknown. |
| Six verifier operations | Registered as fixed HTTP verification/retest operations. | Verification, validator and trust boundary tests were included in the successful Python CI matrix for #274. | N/A (built-in code; host network/runtime configuration unknown) | Unexecuted as a provider smoke | Unexecuted as a verifier-specific lab | Source inventory still records smoke/lab/end-to-end flags false; deployment qualification unknown. |
| Fixed recon providers (DNS, TLS, HTTP passive, headers, robots, security.txt, redirect) | Registered as bounded V2 providers/proposals where listed in §4. | Focused source tests were included in the successful Python CI matrix for #274; no fresh manual test was run in this pass. | N/A for built-in code; DNS/network conditions at deployment unknown. | No separate real-host smoke recorded | No provider-specific lab record identified | Legacy parity and end-to-end deployment qualification remain open. |
| Workflow lifecycle, API/CLI clients, queue worker | Implemented shared service/client paths; exact route and command inventories below. | #274 and #279 CI matrices passed their named tests; see exact runs above. | Package/worker installation on a future deployment is unknown | CI host smoke exists for the named jobs only. | The G01 chain passed in the named PR runs only. | Full UI/client parity, operator approval and release candidate acceptance remain open. |

### Fixed catalog provider inventory and per-provider evidence

The current catalog has 24 IDs (17 CLI, 3 Metasploit-session, 2 SMB, 1 SSH, 1 WMI). The static bridge admits only the 12 listed here. Test files below establish parser, binding, or bounded regression behavior; they do not establish provider readiness. The deployment-target installed version is unknown, and no row is marked qualified by the source or CI results cited here.

| Provider | Test evidence source | Evidence class / unexecuted fields |
|---|---|---|
| arjun | tests/test_providers.py | Binding only; no dedicated parser test identified. Installed/smoke/lab/E2E: unknown or unexecuted. |
| dig | tests/test_adapters_whois_dig_whatweb.py; tests/test_engine_v2_e3_catalog_provider_crash.py | Parser and fake-dig crash/recovery regression; not a real dig qualification. |
| dnsrecon | tests/test_adapters_theharvester_dnsrecon.py | Parser contract; real executable and effect behavior unknown. |
| ffuf | tests/test_adapters_gobuster_ffuf_nuclei_wpscan.py | Parser/contract suite included in CI; #278 real loopback attempt not finalized. |
| gobuster | tests/test_adapters_gobuster_ffuf_nuclei_wpscan.py | Parser/contract suite included in CI; #278 version/cancellation checks failed on earlier head. |
| nikto | tests/test_adapters_parse.py; tests/test_e1_nikto_regressions.py | Parser and bounded regressions; real provider qualification unknown. |
| nmap | tests/test_adapters_parse.py | Parser suite included in CI; #278 loopback attempt not finalized. |
| nuclei | tests/test_adapters_gobuster_ffuf_nuclei_wpscan.py | Parser contract; no completed provider-specific smoke record identified. |
| sqlmap | tests/test_adapters_parse.py; tests/test_engine_v2_g01_lab_compose.py | Parser plus bounded G01 lab chain; not full portfolio or production qualification. |
| theharvester | tests/test_adapters_theharvester_dnsrecon.py | Parser contract; outbound behavior and provider readiness unknown. |
| whois | tests/test_adapters_whois_dig_whatweb.py | Parser contract; external lookup behavior and provider readiness unknown. |
| wpscan | tests/test_adapters_gobuster_ffuf_nuclei_wpscan.py | Parser contract; no completed provider-specific smoke record identified. |

### Reconciled census counts at current main observation

- CLI: the G01 CLI mode inventory CSV has 33 mode rows (including default/help aliases); its AST test compares them with the dispatcher. Rows state owner, classification, persistence, boundary and regression guard.
- HTTP API: EXPECTED_API_ROUTE_HANDLERS and its exact documented table both contain 115 /api/* method/path/handler bindings. The guard compares exact mapping, not a hand-entered total.
- UI: 22 distinct UI page handlers / 23 GET aliases in the canonical crosswalk; 808 static control records are a source inventory only and are not accepted as wired controls.
- Catalog: 24 IDs with the transport split above; 12 admitted local-process providers, 5 excluded CLI entries and 7 unsupported session transports.
- Adapter modules: registry.py attempts to autoload 22 built-in module names; dynamic third-party entry points and import failures affect runtime registration. The old snapshot of “26 discovered adapters” is point-in-time only and must not be presented as a current runtime count. Four adapter-only IDs are recorded as burp, hashcat, msf, and whatweb; echo and ssh_cmd are catalog entries without registered adapters in the reconciled inventory. Runtime registration count on the deployment target is unknown.
- Dispatch and side-effect guard: the AST inventory pins 10 direct ToolRunner caller tuples, 7 direct service-call tuples, and 60 process/network effect sink tuples; these are code locations, not proof that all are reachable, authorized, or supported.
- #278 qualification branch: its new readiness fields and tool loopback qualification are pending review/CI; do not backport its claims to current main until merged and evidence artifacts are verified.

## 10. P0 exit assessment and handoff

- **Inventory completeness:** source-backed top-level CLI modes (including side-effect category, persistence and regression guard) are enumerated by the existing CSV and AST test; legacy runner/network sinks and catalog/admission dispositions are enumerated by the legacy inventory and callsite test; API method/path/handler bindings and UI page/control counts are separately guarded. The second-pass census and exact CI snapshot are in §9.
- **Capability truthfulness:** catalog, adapter, import, session, AI, recon and verifier registration are separated from actual V2 admission and deployment readiness.
- **Dependencies:** supported provider names and target constraints are recorded; installed/readiness, live egress, and exact deployment-host versions are not verified here.
- **Work ownership:** functional owner roles are explicitly mapped in §8; CODEOWNERS does not enforce those roles, and named reviewers/operators remain unresolved for final gate sign-off.
- **P0 status: OPEN — inventory documented; exit is not signed off.** The exact CLI/API/catalog census is reconciled and merged PR evidence is recorded, but unresolved rows remain: (1) 12-provider installed/readiness on the deployment target is unknown; (2) provider smoke/lab/end-to-end qualification is incomplete, with #278 CI still pending at its revised head; (3) current main `e90c11f...` has no separate combined status contexts returned; and (4) named gate reviewers/operators are not attached to role owners. G01 remains **OPEN** for complete controlled workflow acceptance and client parity; G02–G10 are not closed by these CI runs. Overall status remains **HOLD**.

### Canonical detail sources

- `docs/ENGINE_V2_G01_CLI_MODE_INVENTORY.csv` — every top-level mode, engine owner, action boundary, persistence, and regression file.
- `docs/ENGINE_V2_LEGACY_EXECUTION_INVENTORY.md` — direct caller/sink inventory, catalog and adapter disposition, route methods/handlers, API semantics, recon parity, and rollback details.
- `docs/ENGINE_V2_E6_DEPLOYMENT_GATE_LEDGER.md` and `docs/ENGINE_V2_G10_RELEASE_DECISION.md` — release gates and HOLD decision.
- `docs/V2_UI_MANDATORY_CROSSWALK.md` — 22 UI pages, design/control evidence and acceptance boundary.
- `tests/test_engine_v2_cli_mode_inventory.py`, `tests/test_engine_v2_legacy_callsite_inventory.py`, `tests/test_v2_ui_mandatory_crosswalk.py` — inventory consistency guards.
