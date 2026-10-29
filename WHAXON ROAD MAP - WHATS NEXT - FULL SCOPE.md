# WHAXON — CONSOLIDATED SCOPE (MERGED)

**Version:** v1.0.0
**Status:** Living document. Source of truth for project scope.

**Status legend:**
- **DONE** — implemented and shipped
- **QUEUED** — in scope, not yet built
- **URGENT** — do before other queued work
- **OUT** — explicitly excluded, never built

## Repository reality check — 2026-10-25 (reconciled against source tree)

This section supersedes stale progress estimates and any older status statements below where they conflict. It is a repository inspection, not a claim that every capability has passed end-to-end acceptance testing.

**Inspected repository:** `andreipath26/WHAXON-AI-Forensics`, `main` at `21db85a83fa2a8d643570434ec8ad1b75a903cfa` (merge of UI asset upload PR #9). The separate `WHAXON` repository is not the source of truth for this review. The experimental folder `whaxon-experiment-2026-10-25/` is intentionally excluded from this roadmap reconciliation and must remain untouched.

### Framework work present in the repository

| Area | Evidence in this repository | Roadmap status after reconciliation |
|---|---|---|
| Request-context validation | `core/validator.py`, adapter request-context support, `tests/test_request_context.py`, `tests/test_validator_request_context_contract.py` | Implemented; retain regression coverage. Do not describe as future work. |
| Blind/time-based validation | `tests/test_validator_blind.py`; validator uses multiple baseline/injected samples and median comparison | Implemented, but timing evidence has inherent false-positive/target-variance risk; keep as a qualified evidence type, not a universal guarantee. |
| Observation probes | `tests/test_validator_observation.py` and observation-validation code/tests | Present in code and tests; verify supported observation types and end-to-end CLI/web behavior before claiming full acceptance. |
| Retest lifecycle | `interfaces/cli/retest_cmd.py`, `tests/test_validator_retest.py`, `tests/test_web_findings.py` | CLI/core and web route paths exist. Full finding-state lifecycle, scheduling, and client-facing workflow remain distinct from a working retest command. |
| Scope and execution hardening | `tests/test_scope_failclosed.py`, `tests/test_runner.py`, `tests/test_executor_target_lock.py`, `tests/test_web_auth_fail_closed.py`; current changelog documents guarded web execution, cancellation, and listener credential checks | Implemented controls are present; still require release-level regression and deployment checks. DNS preflight is not connection-time DNS pinning; external egress restrictions remain required for beta deployments. |
| Passive reconnaissance | `core/recon.py`, `core/recon_checks.py`, `interfaces/cli/recon_cmd.py`, `tests/test_recon.py` | Phase 1 and passive Phase 2 are implemented in the repository. Third-party data providers and active checks remain future work. |
| Reporting and severity | `core/report.py`, `core/report.html`, `core/report_charts.py`, report and business-impact tests; standalone HTML/PDF/Markdown/JSON paths | Report generation, severity enrichment, deduplication, and business-impact work are present. Coverage disclosure and reproducible proof artifacts must be separately acceptance-tested against the v1.0 definition. |
| CLI, web, TUI, GUI | `interfaces/cli/`, `interfaces/web/`, `interfaces/tui/`, `interfaces/gui/`; web, TUI, server, and route tests | Multiple interfaces exist. Their existence does not prove feature parity or a completed redesign. |
| Quality and packaging | `pyproject.toml` declares package version `1.0.0`; CI/release workflows exist; changelog describes clean-wheel smoke tests and metadata checks | Release metadata/workflow work is present. Do not infer that a public v1.0 release, tag, publication, or green current CI run exists without checking those live states. |

### UI architecture decision — new default UI; legacy UIs retained as references

The checked-in design package under `web ui files and rendering/` (32 HTML screens, 32 PNG renderings, and `obsidian_kinetic/DESIGN.md`) defines the **new default WHAXON web UI**. This is a new UI implementation, not a refresh or continuation of the previous UI. The old web UI, its templates, CSS/JS, prior mockups, and prior screenshots are **deprecated reference material only**: preserve them unchanged for historical comparison, but do not use them as the design source, do not merge their visual language into the new UI, and do not treat their completion status as completion of the new UI.

The new UI must become the default interface launched by WHAXON. Build/integrate it as the active frontend and connect it to the existing framework/services and safe backend routes. Use the checked-in screen HTML and PNG renderings as the source of truth for visual fidelity. The new UI is not complete just because the design assets are present: each screen intended for production must be mapped to a route/workflow, controls must be wired to real supported behavior, and browser/interaction/visual regression checks must pass. If a control has no safe implemented backend, hide or disable it in the live UI without deleting the supplied reference screen or redesigning it.

The existing `docs/WEB_UI_INTERACTION_AUDIT.md` describes the deprecated UI, not the new default UI. Preserve it as a historical audit; create a separate interaction/acceptance audit for the new UI rather than rewriting history. The old Flask templates and assets remain untouched unless a later, explicitly scoped migration step requires changing how the app selects its default entry point. Do not delete or overwrite deprecated UI files.

### Corrected v1.0 interpretation

The framework has advanced substantially beyond the older `docs/STATE.md` snapshot (last updated 2026-10-21, version 0.11.12, 797 tests). The state file is historical until refreshed. The current roadmap must not treat the old ~71-hour / 8–10-session estimate as remaining work: key framework units in §34.2 are already represented in source/tests. The remaining path is primarily **evidence-led integration and release acceptance**: map the actual implemented framework to the v1.0 stopping condition, integrate the supplied UI without redesigning it, wire or hide unsupported controls in the live interface while preserving source assets, run browser/CLI end-to-end checks, resolve release blockers, then verify the actual release artifacts and CI state.

**Status vocabulary for this reconciliation:** “Implemented in source” means code/tests exist; “verified” means the relevant automated or end-to-end check was actually observed passing; “released” means a release artifact/tag/publication was independently confirmed. These statuses are not interchangeable.

---

---

## TABLE OF CONTENTS

1. Vision phases
2. Migration plans
3. Current capabilities
4. Deferred small items
5. Deferred medium items
6. Deferred large items
7. Full tool adoption
8. Cloud scope
9. Distro portability
10. AI modes backlog
11. Full time scale
12. Suggested sequencing
13. Out of scope (never built)
14. Failure modes still guarded
15. Companion files
16. MCP / competitor reference
17. Team-ready capabilities
18. Company-grade platform
19. New default UI integration and acceptance (URGENT; legacy UI deprecated)
20. Market coverage (20.1 URGENT)
21. Report and UI quality issues
22. Session log
23. Agentic pentesting blind spots
24. External feature list triage
25. Report redesign track
26. Bug-bounty add-on
32. Solo-first v1.0 — The Validated Pentest
33. The Trust Layer & Competitive Moat
34. The Solo v1.0 & Competitive Launch Plan
35. Portfolio R&D Pipeline
36. Web-Check-Style Recon Stage
37. Post-v1.0 Strategic Pivots
38. v1.0 Release Blockers and acceptance checklist
39. Tooling portfolio review and integration gates

---

# 1. VISION DOC PHASES — 9 of 9 DONE

| Phase | Status |
|---|---|
| A — Complete the toolbox | ~~DONE~~ |
| A.5 — CVE/exploit lookup | ~~DONE~~ |
| B — Single-step loop MVP | ~~DONE~~ |
| C — Agent architecture design | ~~DONE~~ |
| D — Phase awareness | ~~DONE~~ |
| E — Session-based execution | ~~DONE~~ |
| F — Human-in-the-loop protocol | ~~DONE~~ |
| G — Scope expansion policy | ~~DONE~~ |
| H — Autonomous loop | ~~DONE~~ |

---

# 2. MIGRATION PLANS — 21 of 21 DONE

**Agent-architecture (session 19) — 7 of 7 DONE**
~~ask_human pause/resume · ai_runs.phase column · phase through providers · CLI wiring · phase transitions · WHAXON_AI_SCOPE_EXPANSION · whaxon ai --resume~~

**Session-execution (session 31) — 7 of 7 DONE**
~~catalog schema · Action.session_id · runner.run_in_session() · SessionAdapter · executor session branch · planner integration · report integration~~

**Autonomous-loop (session 51) — 7 of 7 DONE**
~~ai_runs.consecutive_failures · set_ai_run_consecutive_failures · Executor.run(resume_state=...) · ai/objectives.py · ai/auto_answers.py · CLI --auto wiring · --resume inherits mode~~

---

# 3. CURRENT CAPABILITIES (v1.0.0)

| Area | Detail |
|---|---|
| Tools in catalog | ~~21~~ **25** (+ commix, + recon) |
| Adapters registered | ~~24~~ **26** |
| Transports | 4 (MSF, SSH, SMB live-verified; WMI untested) |
| AI providers | 6 (null, rules, ollama, openai, anthropic, google) |
| AI modes | 3 (interactive, --auto, --resume) |
| Correlation rules firing | 8 |
| Interfaces | CLI (22 subcommands), TUI, Web, GUI |
| Tests passing | ~~540~~ **779+** (1 failure due to missing weasyprint, 63 errors due to missing Playwright) |

**Catalog:** nmap, nikto, sqlmap, whatweb, wpscan, ffuf, gobuster, hashcat, theharvester, dnsrecon, whois, dig, impacket, metasploit, netexec, arjun, nuclei, burp, commix, msf_sysinfo, msf_getuid, msf_hashdump, ssh_cmd, smb_shares, smb_ls, wmi_exec

---

# 4. DEFERRED SMALL ITEMS

| Item | Est | Rationale |
|---|---|---|
| ~~ai_source="auto" for auto-answered steps~~ | ~~1h~~ — **DONE** (session 67) | ~~Currently records as "human". Reports misattribute. Foundational for §10 items 1–3.~~ |
| ~~smb_ls generalization~~ | ~~1h~~ — **DONE** (session 67) | ~~Catalog entry hardcodes "use whaxon".~~ |
| ~~Cross-run summary → rules provider~~ | ~~1.5h~~ — **DONE** (session 67) | ~~prior_runs.py fed to LLMProvider but not RulesProvider.~~ |
| ~~Per-owner run visibility in web UI~~ | ~~2h~~ — **DONE** (session 67) | ~~Approval queue has owner; UI doesn't filter.~~ |

**Subtotal: ~~5.5h~~ 0h / 0 sessions.**

---

# 5. DEFERRED MEDIUM ITEMS (QUEUED)

| Item | Est | Rationale |
|---|---|---|
| Web route pause into approval queue | 3h | _ai_run_blocking doesn't wire ask_human callback. |
| MSF structured error channel | 3h | SSH and SMB return [error]; MSF raises. |
| LLM rate limiting with retry/backoff | 3h | Blocks reliable long --auto runs. |
| Long-running session tools | 3h | portfwd times out after 15s. |
| Concurrent runs isolation | 3h | Lock prevents same-run resume only. |

**Subtotal: 15h / ~6 sessions.**

**Blocked:**
| Item | Est | Blocker |
|---|---|---|
| WMI live verification | 2h | No Windows target on this host. |

---

# 6. DEFERRED LARGE ITEMS (QUEUED)

| Item | Est | Rationale |
|---|---|---|
| Full pivot-through-tool wiring | 6–8h | Route resolver exists; HTTP-tool integration missing. |
| Structured objective grammar | 6h | Current design uses heuristics. |
| Cost budget enforcement | 6h | Columns exist; enforcement point needs design. |
| Full streaming session output | 8h | Adapter contract change. |
| Multi-target engagements (fan-out) | 12–16h | New abstraction. |

**Subtotal: ~40h / ~13–16 sessions.**

---

# 7. FULL TOOL ADOPTION (QUEUED)

## Adapter harness contract — CLI-Anything methodology (reference)

**Source:** github.com/HKUDS/CLI-Anything (SOP: `HARNESS.md`, ~600 lines; seven phases; no code generator — the SOP is the deliverable).

**What it is:** a formal contract for turning any software into a CLI an agent can drive. Six properties: State, Commands, Inspection, Rendering, Verification, Discovery.

**Why it maps to WHAXON:** the adapter layer today is a stateless parser. CLI-Anything's contract is stronger:

| WHAXON today | Contract equivalent |
|---|---|
| `tools.json` argument templates | generated command groups per tool |
| adapter `parse()` returning findings | `--json` structured output + inspection commands |
| stateless one-shot run | dual mode: REPL session + one-shot subcommand |
| exit code 0 accepted | independent output verification required |
| no discovery contract | `SKILL.md` for agent discovery |

**The four actions, in order:**

1. **Read `HARNESS.md`** and reference it in `docs/adapters.md`. The contract is the SOP; adopt it as the adapter design standard. ~2h.
2. **Dual-mode CLI.** Every adapter gains a one-shot path (`whaxon run <tool> --json`) and, where the tool supports it, a session path. Existing adapters retrofitted as they are touched. ~2h per adapter.
3. **`--json` as a hard requirement with test coverage.** Every catalog tool returns structured output; the test suite asserts it. Already implicit; make it explicit.
4. **Evaluate CLI-Anything for Burp Suite.** Burp is WHAXON's one GUI-only integration (currently XML import only). A generated harness would let WHAXON *drive* Burp, not just ingest its exports. Separate unit, ~4–6h.

**Explicit caution:** do not run the CLI-Anything generator against nmap/ffuf/nuclei. Those are CLI-native; the generator is for GUI software. The value for WHAXON is the **methodology**, not the generator. The generator's real WHAXON use case is Burp, and possibly other GUI-only security tools if any enter the catalog.

**Dependency:** none — applies to the adapter layer as it is touched. Retrofitting all 25 adapters is not a prerequisite; adopt the contract for new adapters and retrofit on touch.

**Effort:** ~2h to read and document; ~2h per adapter retrofit; Burp harness separate.

**Decision:** All tools from the master list, Tiers 1–3, are confirmed adoption targets.
**Current catalog:** ~~20~~ 25 → **Target:** 120. **New tools:** ~~100~~ 95, ~171h, ~60–70 sessions.

## Tier 1 — Direct fit (44 tools, ~66h)

- **Recon (10):** subfinder, httpx, enum4linux, dnsx, katana, waybackurls, amass, fierce, crtsh, assetfinder
- **Vulnerability (7):** testssl, dalfox, wapiti, commix, smuggler, sslscan, sslyze
- **Web (8):** wafw00f, wfuzz, xsstrike, skipfish, joomscan, droopescan, drupwn, cmseek
- **Cloud/K8s (7):** prowler, trivy, checkov, kube-hunter, kubeaudit, kube-bench, scoutsuite
- **Code security (2):** semgrep, gitleaks
- **Password (3):** medusa, ncrack, patator

## Tier 2 — Fits, lower priority (42 tools, ~63h)

- **Recon (15):** sublist3r, knockpy, shuffledns, uncover, gowitness, alterx, cero, spiderfoot, recon-ng, ghost-eye, sn1per, red-hawk, infoga, **knockmail**, dmitry, gau
  *(Note: knockmail added per tools-to-add.TXT — replaces a duplicate slot; list count stays 42 once the duplicate is resolved. If knockmail is a 16th entry, bump total to 43.)*
- **Enumeration (6):** smbmap, smtp-user-enum, snmp-check, dnsgen, domlink, extracthosts
- **AD/Kerberos (13):** certipy, kerbrute, bloodhound-python, gofenrir, autobloody, adaclscanner, grouper2, asreproast, domainpasswordspray, adrecon, roadrecon, powerview, rubeus
- **Web (1):** sqlninja
- **TLS (1):** a2sv
- **Password (6):** hydra, john, ssh-auditor, crunch, wgen, ophcrack

## Tier 3 — Session-scoped (14 tools, ~42h)

Windows-native, run inside an established session (Phase E). Different integration model.
mimikatz, safetykatz, seatbelt, sharpdpapi, sharpup, powersploit, powerupsql, nishang, invoke-aclpwn, privexchange, zbang, covenant, empire, responder

## Infrastructure implied

- Cloud transport — prowler/trivy/checkov/scoutsuite/kube-* don't fit MSF/SSH/SMB/WMI
- Code security adapter pattern — SARIF-shaped output, new `code_finding` kind
- Session-scoped tool contract for Tier 3
- Wordlist dependencies — WHAXON_WORDLIST_DIR becomes important
- Cloud scope enforcement — data/scope.json needs cloud: section

## Note on vision doc §11

"~18 adapters" was a floor for the initial catalog, not a ceiling. This file records the choice to grow to 120.

### Addendum — tool candidate memo (external), reviewed session 58

A separate memo proposed adding gobuster, enum4linux, masscan, hydra, john, dnsrecon, amass and "confirming" ffuf, whatweb, netexec, gobuster.

Reconciliation against §3 (Current capabilities) and the state snapshot (whaxon_state.md §8):

- **Already wired (adapter registered, `register=True`):** gobuster, ffuf, whatweb, netexec, dnsrecon.
- **Genuinely not yet wired:** enum4linux, masscan, hydra, john, amass — all already named in Tier 1 or Tier 2 above.

No new items added by this memo. Kept for the audit trail; no action.

### Addendum — reorganized tool candidate list (external), reviewed session 58

Source: whaxon_tool_candidates_reorganized.txt (Desktop). ~110 entries, grouped by function. Every entry is marked ADD in the source; several are flagged in the same row as covering an existing WHAXON capability or as out of scope. Recorded for the audit trail; not adopted.

**Active Directory & Windows:** BloodHound, SharpHound, RustHound, pywerview, LDAPmonitor, PowerView, Certipy, Rubeus, Mimikatz, SpearSpray, lsassy, krbrelayx, smbcrawler, enum4linux-ng, gpoParser, Seatbelt, SharpUp, winPEAS, SharpView.

**Cloud Security:** Pacu, PMapper, CloudFox, Cloudsplaining, ElectricEye, CloudQuery, Cloud Custodian, Gato-X, KICS, Kubescape, cloudbrute, matano, hammer, cloudsploit, terrascan, tfsec.

**Secrets & Source Code:** TruffleHog, GitGuardian, Semgrep Secrets, gitleaks, h8mail, GHunt, GitFive, git-hound.

**OSINT & Reconnaissance:** Photon, Osintgram, TorBot, tookie-osint, asnmap, csprecon, cloudlist, dnstwist, CloudFail, ScanCannon, smogcloud, bbot, osmedeus, xsubfind3r, uro, waybackurls.

**TLS & Network:** testssl.sh, sslyze, ssh-audit, CryptoLyzer, tls_prober, hping3, tcpreplay, dnschef, dsniff, MITMf, FakeNet-NG, Xplico, Snoopy, netsniff-ng, ettercap, bettercap, mitmproxy, Responder, mitm6, Coercer, Inveigh.

**Web Application & CMS:** CMSeeK, CMSmap, SSTImap, Vulmap, snallygaster, Vulmap Linux, w3af, Arachni, gauri, turbo_intruder.py, wafw00f, Wapiti, XSStrike, droopescan, joomscan.

**Container & Kubernetes:** kube-hunter, KubiScan, CDK, dockerscan.

**Password Cracking & Brute Force:** Ophcrack, L0phtCrack, RainbowCrack, Cain & Abel, Brutus, legba, THC-Hydra, hydra-gtk, RSMangler, Arsenal-ng, penelope, Weevely, PhpSploit.

**Privilege Escalation:** LinPEAS, LinEnum, Linux Exploit Suggester, linuxprivchecker.py, linux-smart-enumeration, GTFOBins, sudoKiller.

**Utilities & Integration:** shell-gpt, tailscale, oletools, penelope, Arsenal-ng, netcat, GnuPG.

---

# 8. CLOUD SCOPE (QUEUED, DESIGN FIRST)

**Decision:** Cloud is in scope. **Deferred:** Design work.

## Implications
1. New "cloud" category in data/tools.json
2. New finding kinds — ARNs, S3, IAM, security groups, subnets, exposures
3. New transport — SDK credentials/profile files
4. New correlation rules — public bucket + in-scope domain
5. Phase fit unclear

## Design questions
- **Q1. Which tools?** prowler, trivy, checkov, scoutsuite, kube-hunter, kubeaudit, kube-bench, aws/az/gcloud CLIs
- **Q2. Cloud phases?** Recommendation: scope dimension, not phase dimension.
- **Q3. Where does cloud scope live?** Recommendation: extend data/scope.json.

**Effort: ~12h / ~5 sessions.**

---

# 9. DISTRO PORTABILITY (QUEUED)

**Deferred:** v1.0.0 ships Kali/Debian-assuming.

## Gaps
- install_cmd.py:59 — hardcoded sudo/apt
- data/tools.json gobuster args — hardcoded /usr/share/wordlists/dirb/common.txt
- data/tools.json ffuf args — same
- data/tools.json package field — Debian package names

## Already portable
- catalog.py:53 uses shutil.which(binary)
- Runner uses subprocess
- Adapters parse stdout

**Effort: minimal ~1.5h / 1 session; full ~4h / 2 sessions.**

---

# 10. AI MODES — IMPROVEMENT BACKLOG (QUEUED)

## Current modes and gaps

| Mode | How it works | Gaps |
|---|---|---|
| interactive (default) | _stdin_ask_human prompts on every ask_human. Blocks the loop. | No queue, no preview, no batch. |
| --auto | _make_auto_ask → auto_answers.answer_question. Approves phases in WHAXON_AI_AUTO_PHASES, denies others, skips non-transitions. | Coarse. Binary y/n/skip. No confidence. No escalation path. |
| --resume | Reads history, rebuilds loop with initial_history + resume_state. Inherits mode. | Fresh executor. Some state reconstructed, not continued. |

## Highest value (5h / 2 sessions) — do first

| # | Item | Est | Why |
|---|---|---|---|
| 1 | ~~ai_source="auto" for auto-answered steps~~ | ~~1h~~ — **DONE** | ~~Correctness. Foundational. Same as §4.~~ |
| 2 | Confidence-gated auto approval | 2h | Add WHAXON_AI_AUTO_MIN_CONFIDENCE (default 0.85). Above: approve. Below: escalate. |
| 3 | Escalation path from --auto | 2h | Heartbeat after N consecutive skips → escalate or terminate. |

Turns --auto from "works" to "trustworthy."

## Medium value (13h / 5 sessions)

| # | Item | Est |
|---|---|---|
| 4 | --resume preserves interactive session state | 2h |
| 5 | Non-interactive batch approval | 3h |
| 6 | Pluggable auto policy module | 3h |
| 7 | whaxon ai --dry-run | 2h |
| 8 | --budget dollar cap | 3h |

## Lower value (8h / 3 sessions)

| # | Item | Est |
|---|---|---|
| 9 | --model per-run override | 30min |
| 10 | --provider per-run override | 30min |
| 11 | Session-based auto modes (--auto-lateral) | 4h |
| 12 | Cross-run memory for --auto | 3h |

**AI modes total: ~~26h / ~10 sessions~~ ~20h / ~8 sessions.**

---

# 11. FULL TIME SCALE

| Category | Time | Sessions |
|---|---|---|
| Small deferred (§4) | ~~5.5h~~ 0h | 0 |
| Medium deferred (§5) | 15h | 6 |
| Large deferred (§6) | 40h | 13–16 |
| Full tool adoption (§7) | 171h | 60–70 |
| Cloud (§8) | 12h | 5 |
| Distro portability minimal (§9) | 1.5h | 1 |
| AI modes (§10) | 20h | 8 |
| **Near-term total** | **~~271h~~ ~260h** | **~~97–110~~ ~93–105** |

At 2.5h/session: ~9–10 months evenings, or ~2.5 months full-time.

**Extended scope (§17–21) is separate and much larger.**

---

# 12. SUGGESTED SEQUENCING (NEAR-TERM)

| Version | Deliverable | Sessions |
|---|---|---|
| v0.9.x | Small deferred (§4) | ~~2~~ 0 |
| v0.10 | AI modes items 1–3 (§10) | ~~2~~ 2 |
| v0.11 | Medium deferred (§5, excl. WMI) | 6 |
| v0.12 | Distro portability minimal (§9) | 1 |
| v0.13 | Cloud design + first tool (§8) | 5 |
| v0.14 | Large deferred (§6) | 13–16 |
| v0.15+ | Tier 1 tools (§7) | 30 |
| v0.25+ | AI modes medium + lower (§10) | 8 |
| v0.30+ | Tier 2 tools (§7) | 28 |
| v0.40+ | Tier 3 tools (§7) | 14 |

**No version is a hard target. Each is a natural checkpoint.**

**URGENT override:** §19 (UI redesign) and §20.1 (PTaaS) take priority over the above.

---

# 13. EXPLICITLY OUT OF SCOPE (NEVER BUILT)

**From vision doc §11:**
- Wireless (Wifite, Kismet, Pentoo tools)
- SDR
- Forensics (Volatility, Autopsy, Sleuthkit, Guymager, dc3dd, dcfldd, Foremost, log2timeline, Plaso, libewf)
- Reverse-engineering (Radare2, Rizin, Ghidra, RetDec, binary-refinery, PyLingual, JSC Deobfuscator)
- Malware analysis (YARA, Thug, capa)
- Social engineering (SET)
- Hardware
- Network protocol attacks without structured findings (Ettercap, Yersinia, EtherApe, ntopng, nDPI, Softflowd, Scap-workbench)
- Mobile (apktool, MobSF, androbugs, drozer)
- Honeypots (Kippo, T-Pot)
- Commercial scanners without CLI parity (Nessus, Acunetix)

**Ethics boundary (never):**
- Unattended runs against non-consenting targets
- Auto-approval of scope expansion
- Circumventing the executor boundary
- Changing what the LLM may propose without human approval

---

# 14. THREE FAILURE MODES STILL GUARDED AGAINST

1. **Drift into "agent" before toolbox is complete.** Avoided: agent built, toolbox expanding.
2. **Build autonomous loop before human loop.** Avoided: F before H.
3. **Treat LLM as source of truth.** Avoided: store is source of truth.

These remain the design discipline for all future work.

---

# 15. COMPANION FILES

| File | Contents |
|---|---|
| whaxon_state.md | Project state snapshot (whaxon state) |
| whaxon_full_scope.md (this file) | Everything in scope, queued, excluded |
| whaxon_tools_master.md | Master tool list, tiered |
| whaxon_tool_candidates.md | Original 15-tool shortlist |
| whaxon_tool_candidates_full.md | Full distro-research list |
| whaxon_github_research.md | GitHub/MCP collections research |
| whaxon_web_research.md | Web search results |
| WHAXON RULES.md | Development rules (Parts 1–6) |
| PITCH DECK.MD | Investor pitch deck (10 slides + appendices) |
| VCS TO GET FUNDING.MD | Funding targets and application sequence |
| whaxon_tool_candidates_confirm.txt | External tool-candidate memo (session 58 review); items reconciled against §3, no new adoptions |
| whaxon_tool_candidates_reorganized.txt | Full reorganized tool-candidate list, ~110 entries by function; see §7 addendum |

---

# 16. MCP / COMPETITOR REFERENCE

## MCP server collections (reference material, not dependencies)

| Project | Wraps | Value |
|---|---|---|
| cyproxio/mcp-for-security | SQLMap, FFUF, NMAP, Masscan | Low — we have these |
| FuzzingLabs/mcp-security-hub | 40+ servers | High — wrapper patterns for tools we lack |
| hackersatyamrastogi/pentesting-cyber-mcp | 50+ servers | Highest — nearly every candidate tool |

**Why they matter:** Same tools, MCP interface. Their wrappers solve output normalization, argument construction, error handling.

## Competitor reference

| Project | Approach | Relevance |
|---|---|---|
| HexStrike AI | MCP, 150+ tools | Most popular |
| Pentest-Swarm-AI | Go multi-agent swarm | Architectural analogue |
| PhantomRed | Autonomous pipeline, scope.json gate | Ethical framework |
| Cybersecurity AI (CAI) | Open security AI framework | Prompt-injection defense |
| PentAGI | Docker multi-agent, Neo4j + Grafana | Memory-system reference |

**Cloud gap reinforced:** every collection includes prowler, trivy, kube-hunter. WHAXON has zero cloud coverage. See §8.

---

## 16.1 Competitor Reference Data (Research Oct 2026)

- **Sn1per (Pro 2026):** $984/yr. Orchestrator, 90+ tools, SC0PE parser. Read-only JSON API (`/pro/api.php`). Hard caps: 30 assets/workspace. Shipped `sn1per-mcp`. **The gap:** Claims "active verification" in marketing, but architecture is parse-and-report. No `verification_status`, no retest lifecycle.
- **HunterX (Apache-2.0):** Closest architectural analogue. Defines lifecycle: Detection -> Evidence -> Verification -> PoC. Features a "proof contract" registry (deterministic evidence requirements per vuln class). Read their model before expanding §32.2.
- **AUVAP (IEEE, June 2026):** Academic proof of our direction. Deterministic, policy-aware, uses Nmap NSE pre-validation to filter false positives. 92% exploitation success.
- **Vigil:** 18-phase PTES model with `validation` as a distinct phase. LLM-driven (violates R71). Phase vocabulary reference only.
- **Hacktronian:** Dead Python 2 wrapper. Zero adoption.

# 17. TEAM-READY CAPABILITIES (QUEUED)

Extends WHAXON from solo tool to small-team platform (2–5 pentesters).

| # | Item | Effort | Priority |
|---|---|---|---|
| 17.1 | MCP server integration | 6–8h | **Highest** |
| 17.2 | Verification layer | 5–7h | High |
| 17.3 | Multi-agent split | 8–10h | Medium-high |
| 17.4 | Persistent knowledge graph | 7–8h | High |
| 17.5 | RAG for pentest knowledge | 6–8h | Medium |
| 17.6 | Team-scale approvals | 5h | Medium |
| 17.7 | Additional items | 16h | Low-medium |

**Total: ~53–62h / ~20–25 sessions.**

## 17.1 MCP server (keystone)

Expose catalog + runner via Model Context Protocol. New module `src/whaxon/interfaces/mcp/`. Expose: list_tools, run_tool, get_findings, list_sessions, get_scope. Any MCP client (Claude Desktop, Cursor, Codex) drives WHAXON.

**Why:** MCP is the ecosystem standard. Turns WHAXON into a backend.

## 17.2 Verification layer

~~Findings become candidates → verified → reported. New field `verification_status` (candidate/verified/refuted). New adapter method `verify(finding)`. Report filter shows verified by default.~~
**(DONE — see §33.1, §34.2, and white paper findings. Validation engine is shipped with 1.0.0)**

## 17.3 Multi-agent split

Recon Agent · Exploit Planner · Validator Agent · Reporter Agent. Research: hallucination drop 12%→5%, subtask completion 52%→68%.

## 17.4 Knowledge graph

Extend pivot.py into a full graph. Nodes: host, service, credential, session, vulnerability, technique. Edges: runs_on, vulnerable_to, authenticates_to, reaches, discovered_via. SQLite backend.

## 17.5 RAG

Corpus: MITRE ATT&CK, exploit DB, CVE cache, team history. BM25 first (no new dependency). Inject top-K into planner prompt as RETRIEVED_KNOWLEDGE.

## 17.6 Team-scale approvals

Users table with roles. Extend approvals: role_required, delegated_to. Webhooks on set_ai_run_waiting.

## 17.7 Additional team items

Shared engagement workspaces (2 sessions) · Cross-engagement analytics (2) · Team-visible session state (2) · Approval delegation UI (1–2).

## 17.9 Recommended order

1. MCP server (17.1)
2. Knowledge graph (17.4)
3. ~~Verification layer (17.2)~~ **(DONE)**
4. Team-scale approvals (17.6)
5. Multi-agent split (17.3)
6. RAG (17.5)
7. Additional items (17.7)

## 17.11 Single most impactful

**MCP integration.** The keystone. Everything else builds on it.

---

# 18. COMPANY-GRADE PLATFORM (IN SCOPE, LONG-TERM)

**Effort: 70–95 sessions (~175–240h) on top of everything else.**

## 18.1 Organization layer
Orgs · Teams · Users · Engagements · Multi-tenancy. RBAC: Owner, Admin, Pentester, Reviewer, Client-viewer, Auditor. Auth: local (bcrypt), LDAP, SAML/OIDC, API tokens.
**8–10 sessions.**

## 18.2 Client engagement lifecycle
Intake → Scoping → Execution → Reporting → Review → Delivery → Retest → Close. Contracts, scope management, time tracking, deliverables, milestones, retest tracking, report templates, redaction.
**6–8 sessions.**

## 18.3 Compliance and audit
Immutable audit log (hash-chained, 7-year default) · Evidence chain-of-custody (SHA256, access log) · Data residency · Access logging.
**4–6 sessions.**

## 18.4 Operational maturity
Backup/restore · HA (Postgres + Redis, load balancer) · Horizontal scaling (job queue, worker pool) · Monitoring (Prometheus, Grafana, OpenTelemetry) · Rate limits · Health checks.
**12–16 sessions.**

## 18.5 Collaboration
Real-time collaboration · Comments and @mentions · Task assignment · Notification channels (email, Slack, Teams, Discord, webhook) · Peer review.
**6–8 sessions.**

## 18.6 Deployment
Docker Compose · Kubernetes (Helm) · Managed cloud · Air-gapped/on-prem · Bare-metal · Config management · Installer · Upgrade path · Secrets (Vault/AWS/Azure).
**6–8 sessions.**

## 18.7 Commercial layer
Licensing · Billing/usage metering (Stripe, Chargebee) · Support tooling · Admin console · Product analytics.
**8–12 sessions.**

## 18.8 Subtotal
**~50–68 sessions (~125–170h)** for §18 alone.
Plus §17: 20–25 sessions.
**Company-grade + team-ready: ~70–93 sessions (~175–235h).**

## 18.9 Two deployment scopes

| Version | Effort |
|---|---|
| Internal-only (one company's team) | 25–35 sessions (~65–90h) |
| SaaS product (multi-tenant) | 70–95 sessions (~175–240h) |

## 18.10 Recommended build order
1. §17.1 MCP server
2. §17.4 Knowledge graph
3. §18.1 Organization/RBAC
4. ~~§17.2 Verification layer~~ **(DONE)**
5. §17.6 Team approvals
6. §18.2 Client lifecycle
7. §18.3 Compliance/audit
8. §18.5 Collaboration
9. §18.6 Deployment
10. §18.4 Operational maturity
11. §18.7 Commercial layer
12. §17.3 Multi-agent
13. §17.5 RAG
14. §17.7 Additional

## 18.11 What "company-grade" flips

| Today | Company-grade |
|---|---|
| One user | Many users per org |
| One engagement | Many concurrent |
| SQLite | Postgres for HA |
| In-process state | Shared state across instances |
| Basic password | SSO/SAML/LDAP |
| No roles | RBAC 6+ roles |
| No audit log | Immutable, tamper-evident |
| Local deploy | Docker, K8s, air-gap, cloud |
| No billing | Usage metering per org |
| Single-tenant | Multi-tenant isolation |

Each is a design change, not a patch.

## 18.12 Honest assessment

- **v1.0.0 for one pentester:** complete
- **For small team (2–5):** usable with §17
- **For company:** not yet — needs §18

Near-term roadmap remains §§4–10 + §17 MCP/knowledge graph/verification/team approvals (~70–90 sessions). Company-grade is the layer above (~95–135 more).

---

# 19. NEW DEFAULT UI INTEGRATION AND ACCEPTANCE (URGENT)

**Status: NEW UI DESIGN ASSETS PRESENT; implementation and acceptance remain open. Legacy UIs are deprecated and reference-only.**

The repository contains the new Obsidian Kinetic design system, 32 HTML screens, and 32 matching renderings under `web ui files and rendering/`. This is a **new default UI**, not a redesign of the previous UI. Preserve the old UI source and assets unchanged for reference. Do not modify the legacy design to imitate the new one, and do not reuse its old interaction audit as the new UI's acceptance record.

**Acceptance rule:** make the new UI the default interface launched by WHAXON; map each intended production screen to its workflow and backend service; wire every visible action to supported, safe behavior; hide or disable unsupported live controls without deleting supplied design assets; and cover the new UI with browser interaction and visual regression tests. The supplied HTML and PNG renderings are the design/visual source of truth.

**Do not count uploading the design assets as completing the UI.**

**Problem:** Interfaces cluttered as features accumulated across sessions 1–54. No information hierarchy.

## Current state

| Interface | Files | State |
|---|---|---|
| Web (Flask + JS) | server.py 1183L, app.js 1055L, style.css 584L, 4 templates | Six tabs + catalog + run panel + MSF indicator + findings + live output |
| TUI (Textual) | main.py 465L, 4 screens | Catalog, history, target, live output |
| GUI (PySide6) | main_window.py 343L | Embeds web UI, duplicates layout |
| CLI | 21 subcommands | Inconsistent formatting |

## 19.1 Redesign — three candidate approaches

- **A. Sidebar navigation** — left sidebar, main panel per section. Desktop-app feel.
- **B. Workflow-oriented** — Target → Run → Findings → Report. Linear flow.
- **C. Split panes** — catalog left, work center, live output right.

**Recommendation:** B for web, C for TUI, CLI output consistency pass.

**Design artifact (deprecated):** the old reference to `mockups/ui-v4.html` on the founder's Desktop and all previous UI implementations are reference-only. The new default UI's source of truth is the checked-in files under `web ui files and rendering/` and `obsidian_kinetic/DESIGN.md`. The supplied screens must be integrated as the default frontend rather than replaced with, or visually blended into, the old UI. The intended system includes: sidebar navigation, six-stage workflow, right slide-over, command palette, AI banner, notifications, findings with severity donut + attack-surface graph + KPIs, CVE/exploit sections in slide-over, Threat Intel interactive lookup, Report Known Vulnerabilities preview, workspace switcher, and a components gallery. It is the spec that implementation follows.

## 19.2 Testing

- Rendering tests (web, TUI, GUI)
- Interaction tests (web, TUI)
- Visual regression (Playwright for web)
- CLI consistency tests (every subcommand has --help; documented exit codes)

## 19.3 Design questions
1. Primary interface for a team? (web, likely)
2. Primary workflow?
3. What can be removed/hidden/merged?
4. Mobile/tablet support? (probably no)
5. Dark/light mode?
6. Accessibility WCAG AA?
7. Keyboard or mouse driven?
8. What must always be visible vs. on demand?

## 19.4 Effort

| Work | Sessions |
|---|---|
| Web redesign | 2 |
| Web testing | 1–2 |
| TUI redesign | 1 |
| TUI testing | 1 |
| GUI redesign | 1 |
| GUI testing | 0.5 |
| CLI consistency pass | 1 |
| CLI consistency tests | 0.5 |

**Total: 8–9 sessions (~24h).**

## 19.5 Priority

Before §§4–10, §17, §18. A cluttered UI undermines every capability.

## 19.6 Rationale

Team value depends on humans understanding what the tool shows. Redesign is table stakes for company adoption. Do it first.

---

# 20. MARKET COVERAGE (IN SCOPE, LONG-TERM)

**20.1 is URGENT alongside §19.**

WHAXON's §1–19 is a pentest execution platform. §20 turns it into a pentest business platform.

**Effort: 57–72 sessions (~145–180h).**

## 20.1 PTaaS delivery layer (URGENT)

**Status:** Urgent. Priority alongside §19.

Client portal · Self-service scoping · On-demand test launches · Real-time status · Retest scheduling.

**Why:** PTaaS is how firms scale beyond billable hours. Cobalt, HackerOne, Bugcrowd play here.

**Effort: 10–12 sessions (~25–30h).**

## 20.2 Remediation tracking and verification

Finding state machine (open → acknowledged → in-progress → resolved → verified → closed) · Remediation evidence · Retest workflow · Regression tracking · Client-facing status · Time-to-fix metrics.

**Effort: 6–8 sessions (~15–20h).**

## 20.3 Attack Surface Management / continuous monitoring

Continuous monitoring · Asset inventory · Change detection · External attack surface discovery · Exposure scoring · Alerting.

**Effort: 8–10 sessions (~20–25h).**

## 20.4 Client reporting and deliverable management

Report templates (per-client, per-type, per-framework) · Executive summary generation · CVSS auto-population · Methodology section · Tester credentials · Report versioning · Redaction · Deliverable checklist.

**Effort: 4–6 sessions (~10–15h).**

## 20.5 Compliance framework mapping

Finding → framework mapping (OWASP, CWE, PCI-DSS, SOC 2) · Coverage reports · Compliance dashboard · MITRE ATT&CK mapping · NIST CSF alignment.

**Effort: 4–5 sessions (~10–12h).**

## 20.6 Collaboration beyond approvals

Real-time shared sessions · Team chat/comments · Task assignment · Peer review workflow · Playbook sharing · Shared wordlists/payloads/notes.

**Effort: 5–6 sessions (~12–15h).**

## 20.7 Threat intelligence integration

MITRE ATT&CK · Exploit DB + CVE into planner · Threat feeds (OTX, MISP, VirusTotal) · IOC matching · Actor profiling.

**Effort: 3–4 sessions (~8–10h).**

## 20.8 Training and certification mode

Scenario mode · Guided walkthrough · Score and feedback · Progress tracking · Certification prep.

**Effort: 6–8 sessions (~15–20h).**

## 20.9 Full CSPM / CIEM

Continuous posture assessment · Entitlement graph · Compliance checks · Drift detection · Remediation guidance · Multi-cloud.

**Effort: 8–10 sessions (~20–25h) on top of §8.**

## 20.10 API and integration ecosystem

Webhook system · SIEM integration · Ticketing integration · CI/CD · ChatOps · Public API SDK.

**Effort: 4–5 sessions (~10–12h).**

## 20.11 Multi-language / internationalization

UI i18n · Report language · Locale formatting · RTL support.

**Effort: 2–3 sessions (~5–8h).**

## 20.12 Offline / air-gapped deployment

Offline installer · Offline update · No-phone-home · Signed binaries · Air-gap docs.

**Effort: 3–4 sessions (~8–10h).**

## 20.13 Mobile / lightweight client

Responsive web UI · Push notifications · PWA.

**Effort: 2–3 sessions (~5–8h).**

## 20.14 BAS / AEV

Defensive control testing · Detection validation · Continuous simulation · Gap reporting · Blue team integration.

**Effort: 8–10 sessions (~20–25h).**

## 20.15 Section 20 effort summary

| Item | Effort |
|---|---|
| 20.1 PTaaS delivery | 10–12 sessions |
| 20.2 Remediation lifecycle | 6–8 sessions |
| 20.3 ASM / continuous monitoring | 8–10 sessions |
| 20.4 Client reporting | 4–6 sessions |
| 20.5 Compliance framework mapping | 4–5 sessions |
| 20.6 Collaboration beyond approvals | 5–6 sessions |
| 20.7 Threat intelligence | 3–4 sessions |
| 20.8 Training mode | 6–8 sessions |
| 20.9 Full CSPM / CIEM | 8–10 sessions |
| 20.10 API / integration ecosystem | 4–5 sessions |
| 20.11 Internationalization | 2–3 sessions |
| 20.12 Air-gapped deployment | 3–4 sessions |
| 20.13 Mobile / responsive | 2–3 sessions |
| 20.14 BAS / AEV | 8–10 sessions |
| **Total** | **~73–94 sessions (~185–235h)** |

## 20.16 What this completes

Execution + team/company infrastructure (§1–19) + business platform (§20):
- **Delivery** — PTaaS, remediation, continuous monitoring
- **Deliverables** — reports, compliance mapping, framework alignment
- **Ecosystem** — webhooks, SIEM, ticketing, CI/CD, SDK
- **Markets** — training, i18n, air-gapped, mobile
- **Adjacent** — BAS/AEV

## 20.17 Grand total across the entire scope

| Section | Effort |
|---|---|
| 1–3 (done) | — |
| 4–10 | ~260h |
| 17 (team-ready) | ~53–62h |
| 18 (company-grade) | ~125–170h |
| 19 (UI redesign, urgent) | ~24h |
| 20 (market coverage) | ~185–235h |
| **Total** | **~647–751h** |

At 2.5h/session: **~260–300 sessions**, roughly **24–30 months of evenings** or **12–15 months full-time.**

This is not a single project. It's a multi-year platform.

---

# 21. REPORT AND UI QUALITY ISSUES (FROM LIVE ENGAGEMENT)

**Source:** Real WHAXON v0.9.0 reports against DVWA at 127.0.0.1. Four PDFs reviewed.
**Status:** Small fix list. Not urgent, but client-visible.
**Effort: ~5–8h / 2–3 sessions.**

## 21.1 Correlated findings appended to every finding

**Problem:** Same `correlated` findings (`web_service`, `recon_activity_burst`, `vulnerable_service`) appear at the bottom of every finding block. Correlations are per-engagement, not per-finding.
**Fix:** Move to their own "Engagement Correlations" section.
**Effort:** 1h.

## 21.2 started_at not rendered

**Problem:** Reports show `- Started:` with empty value. Field exists in store.
**Fix:** Render `started_at` (and `finished_at` / `duration_s`) in per-job header.
**Effort:** 30min.

## 21.3 CVE IDs not hyperlinked despite lookup_hint

**Problem:** nmap findings carry `data["lookup_hint"]`. Report shows CVE as plain text.
**Fix:** For any finding with `lookup_hint`, run `whaxon lookup` and attach "N known exploits" note. Link CVE IDs to NVD.
**Effort:** 2h.

## 21.4 Nikto "+" prefix not stripped

**Problem:** Every nikto finding renders as `+ [000287] /: ...`. Leading `+ ` is the raw marker.
**Fix:** Strip `+ ` prefix in nikto adapter parse.
**Effort:** 15min.

## 21.5 vulnerable_service severity escalation undocumented

**Problem:** Correlator escalates severity (nmap HIGH → correlator CRITICAL for CVE match). Deliberate but undocumented.
**Fix:** Document escalation rules in `docs/reports-and-evidence.md`. Optionally surface reason in report.
**Effort:** 30min.

## 21.6 URLs truncated at 200 chars in raw_line — DONE (session 66)

**Problem:** raw_line truncated to 200 chars. URLs cut mid-string.
**Fix:** Detect URL-shaped substrings, preserve intact. Or raise cap to 300. Or ellipsis non-URL parts only.
**Effort:** 1h.

## 21.7 Possible nondeterminism in severity assignment — DONE (session 66)

**Problem:** Two reports against 127.0.0.1 show different severities on same finding. Direct findings agree; correlated ones differ. Needs investigation.
**Fix:** Investigate. If nondeterministic, fix ordering in correlator input pipeline. If deterministic, document.
**Effort:** 1–2h.

## 21.8 _lookup_hint alias map misidentifies products — DONE (session 66)

**Problem:** src/whaxon/adapters/nmap.py defines a fixed alias map (http -> apache, https -> apache, ssh -> openssh, ftp -> vsftpd, smb -> samba) that fabricates a product name from the nmap service label. When the version string names a different product, the hint is wrong. Example: nmap reports "http Werkzeug httpd 3.1.8" — the hint becomes "apache 3.1.8" — searchsploit returns 7 Apache exploits, none of which apply to Werkzeug. The hint is not just unhelpful; it is misleading.

**Fix:** Extract the product from the version string when it names one. Fall back to service-name-without-alias only when the product is unidentifiable. Never fabricate. Unknown products should produce empty hints, not wrong hints.

**Effort:** 2h. Rewrite _lookup_hint, add a product-extraction helper, extend the test suite to cover the product-naming cases (Werkzeug, nginx, Apache, OpenSSH, vsftpd, Tomcat, Jetty, Gunicorn, Uvicorn).

**Source:** Session 56 — diagnosed while verifying the CVE/exploit UI pipeline.

## 21.9 Section 21 effort summary

| Item | Effort |
|---|---|
| 21.1 Correlated findings per-finding noise | 1h |
| 21.2 started_at not rendered | 30min |
| 21.3 CVE hyperlinks from lookup_hint | 2h |
| 21.4 Nikto + prefix | 15min |
| 21.5 Severity escalation docs | 30min |
| 21.6 URL truncation | 1h — **DONE** |
| 21.7 Severity nondeterminism investigation | 1–2h — **DONE** |
| **Total** | **~6–8h / 2–3 sessions** |

## 21.10 Priority

**Above nice-to-haves. Below §19 (UI redesign) and §20.1 (PTaaS).**

Report-quality issues a client sees. Erode confidence. Fix before adding new report-renderer features, but after UI redesign.

## 21.11 Companion observation

The reports are **the first live-verified end-to-end run of WHAXON v0.9.0 against a real target with real tools.** Correlator fired across seven of eight rules (see correction below), CVE lookup hints worked, suggestion engine produced actionable steps.

**Validated:** nmap parse · nikto parse · correlator rules (web_service, recon_activity_burst, vulnerable_service) · CVE lookup hints · suggestion engine · per-engagement correlation · PDF rendering.

**Correction (session 57):** rule_vulnerable_service referenced an undefined `_VULNERABLE_VERSIONS` name and raised NameError on every call. The exception was swallowed by `except Exception: continue` in `correlate()`. The rule never fired. The table was added in session 57 and the rule now works; `correlate()` now logs rule failures at WARNING. The claim "fired across all seven rules" was wrong; the correct count of working rules was seven until session 57, eight afterward.

**Revealed:** seven quality issues above.

Target was DVWA at 127.0.0.1 — the canonical first pentest target. WHAXON MVP working in the wild.

## 21.12 Advisories (verified session 57 — see §21.13 for resolutions)

**Status:** Superseded by §21.13. Kept for the audit trail. Original text below. Source: external audit (Cline) cross-referenced against §21. Session 57 verified all five claims in §21.12.B; see §21.13 for results.

**Rule basis:** Rule 10 (read the file first), Rule 11 (diagnostic before change), Rule 37 (anchors prove landing, not coherence), Rule 42 (design first if >2 files), Rule 50 (test count from pytest).

### A. Scope mismatch between §21 and the external audit

The audit reframes two of the eight §21 items as correlator correctness bugs rather than report-renderer polish:

- **§21.1** may be a symptom, not the bug. The proposed fix (move correlated findings to their own section) would mask a store-level dedup failure if the dedup is genuinely dead.
- **§21.7** may not be "possible nondeterminism." The audit claims it is `rule_web_login_surface` truncating `login_lines[:5]` from `findings_by_target()` which is `ORDER BY started_at DESC` — i.e. wall-clock-dependent truncation, a violation of the determinism guarantee (Rules Part 3).

If either is confirmed, the §21.1 / §21.7 effort estimates and framings are wrong and must be corrected before work begins.

### B. Audit claims that must be verified against real code

Each of the following is an advisory, not a fact. **Verify before patching.**

1. **Correlator dedup key mismatch (§21.1 root cause).** Audit claims `correlator.py:295-302` builds existing keys as 2-tuples `(kind, pattern)` but looks up 3-tuples `(kind, pattern, cve or service)`, so dedup never fires. **Caveat:** the audit's "PROVE" script *constructs* the 2-tuple vs 3-tuple mismatch in the test itself rather than importing and calling the real correlator function. It therefore demonstrates the script is inconsistent, not that the production code is. Must be verified by calling the actual correlator entry point with two identical correlations and inspecting the store.

2. **Rule input nondeterminism (§21.7 root cause).** Audit claims the rule slices `[:5]` before sorting, so results depend on row order from the store. Must be verified by running the rule twice with shuffled input and asserting identical output. If the real code already sorts, the audit is wrong and §21.7 is a different bug.

3. **`_lookup_hint` fabrication (§21.8).** Audit's script imports the real function (`from whaxon.adapters.nmap import _lookup_hint`), so this claim is stronger than (1). Still must be re-run locally against current `HEAD` to confirm the output has not changed since the audit. The nine cases in the audit's script must be extended to include Tomcat and Uvicorn, which §21.8 explicitly names.

4. **CI lint is decorative.** Audit claims `.github/workflows/*.yml` contains `ruff check src tests || true`. Must be verified by reading the workflow file. The claim that 453 lint errors exist in `src/` must be verified by running `ruff check src` at current `HEAD`, because the number will have moved.

5. **Dead / duplicate code paths.** Audit claims `executor.py:263-276` contains a verbatim-duplicated session-liveness check, and `ai_bridge.py:191-203` contains unreachable branches in `_default_model_for()` that reference `sys` without importing it. Both must be verified by reading the files. The `ai_bridge.py` claim is potentially a latent `NameError` and should be checked first — if `sys` is genuinely not imported in that scope, that is a correctness issue, not a dead-code issue.

### C. Audit claims NOT present in §21

The audit raises two items §21 does not list at all. These are **new** if confirmed:

- **CI lint gate does not fail** (see B4). Not in §21. Would become §21.x if verified.
- **Two dead / duplicate code paths** (see B5). Not in §21. Would become §21.x if verified.

### D. Verification hygiene

- **Do not trust the audit's test-count figure.** The audit reports "538 passing, 45s." The pre-commit hook on record ran "538 tests in 15.97s." These differ. Rule 16 applies: test count and timing come from `pytest` at current `HEAD`, not from the audit and not from arithmetic.
- **Do not accept the audit's effort estimates as authoritative.** The audit proposes ~3h total for five fixes. This does not include: a verification session, the `# noqa` / config pass required to make the CI lint gate land cleanly, or regression tests for the correlator fixes. Re-estimate after verification.
- **Do not accept the audit's fix ordering as authoritative.** The audit's suggested order (CI lint → correlator dedup → rule ordering → `_lookup_hint` → dead paths) may be sound, but it was produced without the verification step. Confirm order after B1–B5 are resolved.
- **Do not accept the audit's framing of §21.1 as a report problem.** If B1 confirms the dedup is dead, the fix belongs in `correlator.py`, not `report.py`, and §21.1 must be re-scoped accordingly.

### E. What this advisory session does *not* do

- No patches.
- No test runs beyond what verification requires.
- No changes to §21.1–21.8 until B1–B5 are resolved.
- No new roadmap items created. Advisories only.

### F. Next-session sequence (verification only)

1. Read the six files named in B1–B5 at current `HEAD`.
2. Run `pytest -q` once, record the number.
3. Run `ruff check src` once, record the number.
4. Run the audit's `_lookup_hint` script against current `HEAD`, record output.
5. Write a two-identical-correlations reproducer that calls the real correlator entry point, record whether dedup fires.
6. Write a shuffled-input reproducer for `rule_web_login_surface`, record whether output is stable.
7. Report findings. No fixes in this session.

## 21.13 Session 57 — verification results and fixes

**Session 57 date:** 2026-10-08
**HEAD after session:** 3638901 (PR #6 merged)
**Test count after session:** 540

### Verification of §21.12.B claims against real code

| Claim | §21.12 ref | Verdict | Evidence |
| --- | --- | --- | --- |
| Correlator dedup key mismatch (2-tuple vs 3-tuple) | B1 | CONFIRMED | correlator.py:298 builds (kind, pattern), line 301 looks up (kind, pattern, cve or service or ""). Dedup never fires. |
| Rule input nondeterminism in rule_web_login_surface | B2 | CONFIRMED in shape | Line 233 appends in input order, line 241 slices [:5] with no sort. Exact input order depends on _all_findings_for merge, not fully read. |
| _lookup_hint fabricates product identity | B3 | CONFIRMED | nmap.py:205-225. Alias map maps http to apache unconditionally. |
| CI lint gate is decorative | B4 | CONFIRMED | ci.yml:38 = run: ruff check src tests with OR true. Only in ci.yml, not release.yml. |
| Dead / duplicate code paths | B5a, B5b | B5a CONFIRMED, B5b FIXED | B5a: executor.py:263-276 duplicated verbatim. B5b: ai_bridge.py:198-203 deleted in session 57 as part of F821. |

### Additional finding, not in §21.12.B

rule_vulnerable_service had never fired. correlator.py:197 referenced _VULNERABLE_VERSIONS, a name that did not exist anywhere in the repo. Every call raised NameError, swallowed by except Exception: continue in correlate(). The rule was dead since it was written. Fixed in session 57.

### What shipped in session 57

| Fix | File | Commit |
| --- | --- | --- |
| ruff autofix (imports, whitespace) | 115 files | b660e3f |
| F821 x4, F601 x4, _VULNERABLE_VERSIONS table, WARNING log in correlate() | correlator.py, ai_bridge.py, splash.py, msf_parsers.py | 3d21b99 |
| import subprocess, duplicate PARSERS key removed | server.py, msf_parsers.py | 2de9eff |
| Two tests for rule_vulnerable_service | tests/test_correlator.py | 31d2d0f |
| Sister projects section (KILN, Aletheia) | README.md, docs/README.md | 96b0c1c |
| Test count 538 to 540, session 57 CHANGELOG | README.md, docs/CHANGELOG.md | 2ec2452 |

### What remains from §21.12.B — session 58 work plan

1. B1 — correlator dedup key. One-line fix at correlator.py:298 plus decide which of two dedup mechanisms wins (correlator's, or store.py:315 findings_by_target). Plus regression test.
2. B2 — sort login_lines before [:5] in rule_web_login_surface. Check other rules for the same pattern. Plus shuffled-input test.
3. B3 — rewrite _lookup_hint to extract product from version string, empty on unknown. Extend tests with Tomcat and Uvicorn.
4. B5a — delete duplicate liveness block at executor.py:263-276.
5. CI lint — remove OR true from ci.yml:38. Add ruff config to pyproject.toml for BLE001/S110/S112/RUF012 in the same commit so CI stays green.

### §21.12.D hygiene resolutions

- Test-count discrepancy resolved: audit said 538, pre-commit hook said 538, both correct at the time. Now 540.
- Effort estimates in §21.12.D remain authoritative for B1-B5a until each is fixed.
- §21.1 framing confirmed wrong: dedup is a correlator bug, not a report-renderer bug. Fix in correlator.py, not report.py.

---

## 22. Session log

### Session 57 — 2026-10-08 — lint hardening and correlator repair

**Branch:** session-57-lint-and-correlator
**PR:** #6 (merged, fast-forward to 3638901)
**Tests:** 538 to 540

Shipped:

- ruff autofix across 115 files (mechanical: import order, whitespace, __all__ ordering)
- ruff F821 x4 fixed: undefined sys, _VULNERABLE_VERSIONS, TImage, subprocess
- ruff F601 x2 pairs fixed: duplicate PARSERS keys were shadowing specific parsers with generic ones
- _VULNERABLE_VERSIONS table added — rule_vulnerable_service was raising NameError on every call and had been dead since it was written
- correlate() now logs rule failures at WARNING instead of silently skipping
- Two tests added for rule_vulnerable_service
- README: sister-projects section (KILN, Aletheia Framework), test count 538 to 540
- docs/CHANGELOG.md: session 57 entry

Root cause found and fixed that was not in §21 or the external audit:

- A silent-swallow except Exception: continue in correlate() had hidden a NameError in one of the eight correlation rules. The rule had never fired. Any future rule failure of the same class would have been equally invisible.

### Session 61 - 2026-10-15 - severity correctness and report redesign PR 1a, PR 1b

**Branches:** session-61-severity-correctness, session-61-report-1b

**PRs:** #18, #19 (merged)

**Tests:** 540 to 673

Shipped:

- PR 1a (#18): CVE-driven severity, local vulnerability database, nikto pattern fixes
- PR 1b (#19): report dedup by (kind, signature), test-job filter, narrative executive summary, severity correction policy, retroactive severity resolver

### Session 62 - 2026-10-15 - report redesign PR 2

**Branch:** session-62-report-2

**PR:** #20 (merged, HEAD 9fc5d1c)

**Tests:** 673

Shipped:

- Report restructure: Executive Brief, Remediation Roadmap, appendices
- Pivot Chains renamed to Attack Surface
- New helpers: _priority_band, _md_remediation_roadmap, _md_findings_appendix, _md_job_history_appendix

### Session 63 - 2026-10-15 - report redesign PR 3, business-impact severity

**Branch:** session-63-report-3 (pending)

**Tests:** 673 to 689 (16 new in tests/test_report_business_impact.py)

Shipped:

- New module core/business_impact.py: base band per finding kind, production-target modifier, published incident-cost tables with per-row sources
- core/severity.py annotates business_impact at resolve time
- core/resolve_stored.py persists the field into finding enrichment
- core/report.py: executive brief ranks by business impact, roadmap bands shift up, appendix shows both scales
- docs/business-impact.md, docs/reports-and-evidence.md, docs/CHANGELOG.md updated

See section 25 for the full track.

### Session 71 — 2026-10-19 — Validation engine: re-execution

**Tests:** 781

- `Validator.validate(finding, target_url)`: real HTTP replay via urllib. Baseline vs payload comparison. SQL error markers and XSS reflection markers. Returns `(status, reason)`.
- `whaxon validate` fetches the job target and builds the URL. Prints reason alongside status.
- `PayloadLoader` mapping fixed (`sqli`, not `sql_injection`).
- 6 new live-replay tests, 3 rewritten CLI tests.

**Deferred (R29):**
- Full request context (method, headers, cookies, body) is not persisted by adapters. POST, authenticated, and header-dependent findings return `candidate` with a named reason. Own unit: "adapters persist replayable request context."
- Blind SQLi / blind XSS (timing-based) not detected. Baseline vs payload comparison only catches error-based and reflected. Own unit.

---

### Session 70 — 2026-10-19 — Trust Layer: validation engine

**Tests:** 775

- Vendored PayloadsAllTheThings (6 chapters) into data/payloads/ at SHA 3ac2790 (MIT, ATTRIBUTION.md)
- findings.verification_status column (default candidate), idempotent migration
- Store.update_verification; get_findings returns seq + verification_status
- core/validator.py: PayloadLoader parses fenced blocks (70 SQLi payloads extracted); Validator stubbed
- whaxon validate <job_id> <seq> CLI

**Deferred (R29):**
- Validator re-execution engine: pick first payload deterministically, re-run via runner, parse response, set verified/refuted. Next unit.

---

### Session 79b - 2026-10-20 - Dogfooding fixes, part 2

**Tests:** 793

Three fixes from session 79 were in the working tree but did not land
in v0.11.9. v0.11.9 shipped without them.

- executor.py: phase transition denial now stops the chain (was looping).
- ai_cmd.py: verbose streams JobStarted and JobFailed.
- catalog: nmap uses -Pn (ICMP-blocked hosts).
- data/proof-cloud/: four cloud-target runs.

Four-target test complete: flaws.cloud, flaws2.cloud, rest.vulnweb.com,
pentest-ground.com. All clean stops.

---

### Session 79 - 2026-10-20 - Dogfooding fixes

**Tests:** 793

First end-to-end dogfooding run. Target: Juice Shop on 127.0.0.1:8888,
plus a local reflecting server for XSS verification.

Ten bugs found and fixed:
1. `_replay_ctx` never injected the payload. `whaxon validate` had never
   verified a real finding.
2. `cli.py` dropped the first positional for validate/retest/coverage.
3. Missing `--verbose` on validate/retest.
4. `validate`/`retest` hardcoded data_dir, rejected `--data`.
5. sqlmap catalog forced `--crawl=1` and duplicate `-u`.
6. `extract_target` lost the port.
7. Rules nmap action passed no `-p`.
8. Target lock compared host vs host:port.
9. `_already_ran` did not block repeat failures. Chain looped.
10. Web-port list missing 8888 and other common non-standard ports.

Verified:
- `whaxon validate` on a live reflecting target: VERIFIED.
- `whaxon ai --auto` runs to completion with clean stop.

4 new regression tests. No new user-facing capability; patch release.

---

### Session 78 - 2026-10-20 - UI Pass 1

**Tests:** 793

- Full interaction audit written to docs/WEB_UI_INTERACTION_AUDIT.md (94 lines, 40+ controls classified).
- Wired: Report page (md/html/pdf downloads), Retest page (live queue + per-row retest), Sessions page (live + stored), Catalog page (real tools), Scope modal (override logged).
- Hidden until backend exists: Audit, Settings, Compliance, Intel, Notifications, Workspace switcher, AI banner, bulk actions.
- Verified via curl: report endpoints, retest data source, sessions, catalog, scope check.

---

### Session 77 - 2026-10-20 - Trust Layer UI wiring

**Tests:** 793

- Web UI: Validate and Retest buttons in findings slide-over.
- Web UI: Live Coverage page replacing static Monitoring mockup.
- Web UI: Approvals page pending review section with Mark Verified/Refuted.
- API: Four new routes (validate, retest, coverage, resolve).
- DB: verified_by column.
- Tests: 4 new in test_web_trust_layer.py.

---

### Session 68 — 2026-10-18 — hydra wired end-to-end

**Tests:** 774

- hydra adapter registered via _autoload() tuple (was: defined + unit-tested, never imported, get_adapter returned None, every run parsed nothing)
- hydra catalog entry added (data/tools.json, data/proof-dvwa/tools.json)
- initial-access ladder step in RulesProvider: run hydra, then ask_human for post-access
- 3 ladder tests + 1 misc-segment parse test
- DVWA proof: [2 findings] weak_credential admin/admin and admin/password

**Deferred (R29):**
- rockyou.txt.gz ships gzipped on Kali; catalog points at /usr/share/wordlists/rockyou.txt. Tool error 255 reported as completed run, not failure. Fix with runner error-handling work, not this unit.

---

### Session 67 - 2026-10-17 - §4 small deferred closed

**Branch:** session-67-small-deferred
**Tests:** 733 passing (was 712; +21); ruff 0; mypy 0

Shipped:

- §4.1 `ask_human_source` threaded through Executor / build_executor / ai_cmd; auto-answered steps record "auto"
- §4.2 smb_ls command templated (`use {command}\nls`); share required via --extra
- §4.3 RulesProvider `_confidence` helper uses prior_runs for confidence only, ladder unchanged (determinism preserved)
- §4.4 Approvals page: nav item, section, app.js block, owner filter, answer form, badge; 5 Playwright tests

Found and fixed a pre-existing store bug:

- `add_approval` never cleared `status='waiting'`, so answered runs stayed in `/api/ai/pending` forever. Now sets status='running' and clears pending_question.

§4 is now closed. Remaining near-term: §5 medium deferred (15h, minus blocked WMI), §10 AI modes, §23 determinism tests.

### Session 66 - 2026-10-17 - report quality §21 closed

**Branch:** session-66-report-quality
**PR:** pending
**Tests:** 712 passing (was 689; +23); ruff 0; mypy 0

Shipped:

- §21.8 `_lookup_hint` rewritten: product extracted from the version string via a known-product list; alias map removed; protocol labels with no named product return empty. New `_extract_product`. 16 tests.
- §21.7 `rule_web_login_surface`: `sorted(set(login_lines))[:5]` — deterministic and deduped.
- §21.6 URL truncation: new `_truncate_preserving_urls` keeps any straddling URL intact; both render sites wired. 7 tests.
- README WMI label corrected (mocked -> untested, blocked), carried from session-65-wmi-label.

§21 is now fully closed. Remaining roadmap next: §20.1 PTaaS (URGENT), or §23 determinism regression tests.

### Session 65 - 2026-10-17 - quality gates made real

**Branch:** session-65-quality-gates
**PR:** #24
**Tests:** 689 passing; ruff 0; mypy 0

Shipped:

- `[tool.ruff.lint]` select/ignore with per-rule rationale; 332 errors to 0
- `[tool.mypy]` with no_site_packages and named overrides; 70 errors to 0
- CI: removed `|| true` from ruff; added `mypy src`
- Fixed: duplicate `_build_job_report`, `Provider.plan_step` prior_runs drift, `App.exit(reason=)` x2, `write_bytes(str)`, cve_cmd union narrowing, autopivot IPv6 guard

Deferred:

- UP031 (32 sites, 10 files) — own unit
- msf_tracker timing flake — pre-existing, xdist-load sensitive

### Session 64 - 2026-10-17 - standalone ui-v4 report generator

**Tests:** 689 passing

Shipped:

- to_html rewritten as a pure Python-to-HTML generator. No Jinja rendering, no server. Self-contained output with inline CSS, inline vanilla JS, and the engagement dict as JSON.
- XSS-safe JSON injection using u003c escaping to prevent raw tool output from truncating the script block.
- Interactive report UI: KPI filtering, sortable table, slide-over with technical severity, business impact, Cyentia cost range, evidence, remediation, Escape-key close.
- Copy-to-Jira workflow utilities (per-finding and engagement summary).
- render_pdf and _build_job_report restored. to_pdf_bytes now renders the standalone HTML via weasyprint instead of pandoc-converting markdown.
- report_pdf.j2 removed. Deleted report_findings.js.

Root cause found and fixed that was not in the plan:

- The _render_template Jinja path was left in to_pdf_bytes after to_html was rewritten. Deleted the Jinja template but not the call, which broke PDF export. Restored a render_pdf helper that builds a job-shaped report dict and routes through the new to_html.

Lessons:

- The standalone report does not need app.js modifications. The app.js edits for business_impact and cost_range in the slide-over broke 13 Playwright tests. Reverted.

---

# 23. AGENTIC PENTESTING BLIND SPOTS (from Picus Security, Oct 2026)

Source: "The Blind Spots of Agentic Pentesting and How to Close Them," BleepingComputer, 2026-10-14, sponsored by Picus Security.

The article names five structural issues with agentic pentesting. WHAXON mitigates three by design; two are real gaps already partially scoped.

## Already mitigated by design (verify with tests, do not rebuild)

- **Non-determinism across runs.** WHAXON is deterministic-first; AI is optional and never in the parse/correlate/report path (R71). Add a regression test: same target, two runs, byte-identical findings + report. ~2h. New item.
- **Unverified AI-authored exploits.** Executor never lets the LLM author a command; it selects from a human-authored catalog. No change.
- **Token cost.** AI is opt-in; deterministic path is the default. Add per-run token tracking + budget cap. Already scoped as section 10 item 8 (3h).

## Real gaps (already in roadmap)

- **Reachability.** An agent can only test what it can reach. HTTP tools do not currently use the route resolver, so pivot-reachable targets are untested by nmap/nikto/nuclei. Already scoped as section 6 "Full pivot-through-tool wiring" (6-8h). Promote to first item after section 26 ships.
- **No PoC means no verdict.** Roughly 75 percent of CVEs have no public exploit, so an agent that only tests by running exploits produces no verdict for them. The correct answer is exposure validation, not exploit execution. Already scoped as section 20.14 "BAS / AEV" (8-10 sessions).

## New items from this article

- **Determinism regression test** (~2h). Same input, two runs, assert identical findings and identical report bytes. Locks in R71 at test level.
- **AI-mode determinism assertion** (~3h). Rules provider and null provider: same goal + same history = same action sequence. Proves the deterministic AI path is actually deterministic. Real LLMs excluded by definition.
- **Promote section 20.14 above section 7 tool adoption.** RECOMMENDATION, not decision. A platform that gives every asset a verdict, including unreachable ones, is worth more than 100 tools. Decision pending section 26 completion.

## Not in scope

Picus specific product (control validation via attacker-behavior testing) is a defensive-control-testing product, not offensive. Section 20.14 already covers the capability. No separate integration.

---

# 24. EXTERNAL FEATURE LIST TRIAGE (AI-generated, 2026-10-14)

Source: an external AI-generated feature proposal, ~65 items, produced in
escalating rounds without reference to WHAXON's repo, roadmap, or §13
exclusions. Triage below. Roughly one third already exists in WHAXON, one
third is excluded by §13, and a small remainder is genuinely new. This
section records the disposition so the same list is not re-triaged later.

None of these items block the current sequence: finish the UI, then the
bounty add-on (§26), then everything else.

## 24.1 Adopted (new small items, ~20h total)

- **Deterministic replay / session dump (~4h).** Record raw tool stdin/stdout during a run; replay offline without hitting a target.
- **Global rate/bandwidth governor (~4h).** One adaptive throttle across all concurrent jobs. Reacts to HTTP 429/503 and latency.
- **In-flight scope mutation (~2h).** Kill an active job when scope changes mid-run.
- **Tool version pinning (~2h).** Record the version of nmap/nuclei/etc. that produced each finding.
- **Account lockout governor (~2h).** Stateful tracking of auth-endpoint responses; pause credential testing before triggering lockouts.
- **OOB interaction / callback server (~4h).** Self-hosted DNS/HTTP listener to confirm blind vulnerabilities. Fits §17.2.
- **Indirect prompt injection defense (~2h).** Sanitize inbound text before it reaches the LLM planner. Fits §26.3.

## 24.2 Folded into existing sections

- **MITRE ATT&CK mapping** → §20.5
- **Target delta / drift detection** → §20.3
- **Timestamped evidence ledger** → §18.3
- **CRDT multi-operator sync** → §17.6 and §18.5
- **Live SIEM / detection validation** → already §20.14

## 24.3 Considered, deferred

- **SBOM / SCA correlation** — new adapter family. Revisit after §7 Tier 1.
- **Natural-language intent compiler** — consider as a §10 AI-modes item.
- **Local privilege escalation tree solver** — post-exploitation subsystem.
- **Micro-container tool isolation** — consider for §18.6.
- **Honeypot / deception fingerprinting** — low priority.
- **Automated remediation code generator** — its own product.

## 24.4 Rejected, with reasons

**Ethics:** Payload mutation engine. Fails §13 ethics boundary.

**Excluded by §13 (re-proposed by generator; still excluded):** SDR/RF, drone telemetry, hardware (JTAG/UART/CAN bus/OBD-II), firmware unpacking, BLE/NFC, physical access control, ICS/SCADA, BACnet/BMS, biometrics, covert channels, smart contracts, ZK circuits, quantum cryptanalysis.

**Already exists in WHAXON:** attack graph, loot pipeline, evidence attachments, verification layer, retest engine, MCP server, RAG, multi-agent split.

## 24.5 Note on the source

The document is a triage artifact, not a spec. Any item later promoted to active work gets its own design doc per R3.

---

# 25. REPORT REDESIGN TRACK (sessions 61-63)

**Design of record:** docs/report-redesign.md

A five-PR track that rewrote how the engagement report is structured and how findings are ranked. Independent of the tool work in sections 4-10.

## 25.1 PR 1a - Severity correctness (merged #18)

CVE-driven severity from a local vulnerability database, nikto pattern fixes.

## 25.2 PR 1b - Dedup, filter, narrative summary (merged #19)

Report dedup by (kind, signature); test-job filter; narrative executive summary; severity correction policy; retroactive severity resolver. Engagement report: 570 raw findings to 220 unique.

## 25.3 PR 2 - Restructure (merged #20)

Report leads with Executive Brief and Remediation Roadmap. Findings and job history move to appendices. Pivot Chains renamed to Attack Surface.

## 25.4 PR 3 - Business-impact severity (this session)

Second severity scale on every finding, computed deterministically at resolve time. Published incident-cost tables with per-row sources. Design doc: docs/business-impact.md. See session 63 log entry.

## 25.5 PR 4 - Visual design (not started)

HTML/PDF rendering beyond the current pre-wrap; severity chart; per-finding cards. See docs/report-redesign.md for the PR 4 spec.

## 25.6 What is not in scope

New finding model; new adapters; attack graph engine (section 25 elsewhere); live collaboration; client portal.

---

# 26. BUG-BOUNTY ADD-ON (IN SCOPE, DESIGNED)

**Design of record:** docs/bounty-addon.md (428 lines, 2026-10-13).
**Status:** Designed, not built. This section gives it a roadmap row, effort estimates, and dependency order so it stops being an unroadmapped design doc (R9).

A per-program mode that encodes the platform's rules and the program's rules before any request is sent. Distinct from the pentest flow: the pentest flow assumes a client engagement with a written scope; a bounty program has a published policy, a rate limit, a disclosure deadline, and a qualifying/non-qualifying bug class list. The add-on makes those machine-readable and gates every action on them.

## 26.0 Purpose and capability model

Three capabilities, in order:
1. **Program policy enforcement** — refuse to touch a target until a policy file exists, parses, and matches the host.
2. **Differential and invariant analysis** — compare sessions, infer workflows, detect state-machine violations. Deterministic, no LLM.
3. **Human-gated AI assistance** — the AI may select actions only if the policy explicitly allows it. Default deny.

The one unconditional non-goal: **no unattended runs against a bounty target.** Every session requires a human in the loop, because a bounty program's rules are not the same as a client's written authorization.

## 26.1 Program policy layer

**Location:** `data/programs/<slug>.yaml`, `data/programs/<slug>.overrides.log`.
**Schema:** 12 top-level keys — slug, platform, program_url, last_reviewed, identity, rate, scope, tools, ai_policy, reporting, bug_classes, override_log. Full schema in docs/bounty-addon.md §26.1.
**Behavior:** missing file / malformed YAML / missing tools.mode / empty in_scope / unknown platform / unknown key — all refuse, each with a named error.
**Two-gate model:** program gate (scope.in_scope) then host gate (data/scope.json). Out-of-scope wins. Existing scope.py preserved.
**Resolution:** target matched against each policy's in_scope. Exactly one match wins. Zero or multiple = refusal.
**Effort: 8–12h.** Loader, validator, resolver, gate wiring, override log.

## 26.1.1 Override log specification

Append-only. Every policy override recorded with timestamp, operator, reason, before/after. Cross-checked at report time. **Effort: 2h.**

## 26.2 Core analysis capabilities

**§26.2.1 Differential session analysis** — compare two sessions against the same target, surface what changed. Deterministic. **6–8h.**
**§26.2.2 Invariant engine** — declarative invariants (e.g. "admin endpoint never returns 200 to a non-admin token"), evaluated per session. **8–10h.**
**§26.2.3 Workflow inference** — infer the state machine from observed requests, flag transitions that skip a step. **6–8h.**

**§26.2.4 Browser-driven capture** — a managed browser session WHAXON owns, configured by the program policy. The operator drives a target inside the WHAXON web UI; every request streams to the HAR adapter live, so findings appear as they browse. First candidate: Clawbrowser (CDP-native, fingerprint and proxy layer, Playwright connects unchanged). Fallback: any CDP-capable Chromium. Six capabilities, only the first two in v1 scope:

1. **Live browser-in-UI with streaming capture** — the web UI gains an interactive browser pane; the HAR adapter becomes a live feed, not a file import. Product change: scanner becomes analyst workbench. *(v1)*
2. **Policy applied to the browser, not the human** — §26.1's `identity.user_agent_suffix`, `email_alias`, `rate`, and geo config the Clawbrowser profile. A written policy is a checklist; a policy that configures the browser is a gate. *(v1)*
3. **Per-program persistent identities** — one profile per bounty program: that program's alias, UA, geo, cookies. Matches every program's stated hunting requirements.
4. **Authenticated findings in the report** — a report section that says what was reachable *as an authenticated user*. New report capability, not new data.
5. **Persistent sessions for monitoring** — keeps §20.3 ASM from re-authenticating on every check.
6. **Observable-not-exploited verdicts** — partially closes §23's gap: a CVE with no public PoC can still be *observed* as reachable, without exploitation.

Dependency: after §26.1 (done). Before §26.4 (reports consume captured findings). Effort: ~6–10h real for v1 (#1–#2); #3–#6 are follow-ons that become cheap once the browser session exists.

## 26.3 AI role (gated)

Policy field `ai_policy.allow_action_selection` defaults false. When false, the AI cannot propose actions — only annotate findings. When true, the executor guardrails from §B/H apply unchanged. Indirect prompt injection defense folded in here (§24.1). **Effort: 6h.**

## 26.4 Report generation

Bounty report shape, not pentest report shape. Platform-specific form templates (yeswehack, hackerone, bugcrowd). Redaction boundary: evidence that identifies the hunter is stripped before any draft. **Effort: 8h.**

## 26.5 Scope

Unconditional non-goal: unattended runs. Gated: any action the policy's `tools.denylist` names. Out of scope project-wide: the §13 list, unchanged. **Effort: 2h** (mostly wiring the existing scope gate to the policy gate).

## 26.6 Relationship to existing components

Policy gate wraps `core/scope.py`. Analysis engines consume the existing findings store. Report generation reuses `core/report.py` helpers. No new transport. **Effort: 2h.**

## 26.7 Program state

Per-program state: last run, findings submitted, findings accepted, disclosure deadline. Stored in `data/programs/<slug>.state.json`. **Effort: 4h.**

## 26.8 Legal and ethical boundary

Every bounty session requires a human in the loop. The policy file must name the program URL and last_reviewed date. Reports cross-check the override log. **Effort: 2h** (mostly documentation and test).

## 26.9 Effort summary

| Item | Effort |
|---|---|
| 26.1 Policy layer | 8–12h |
| 26.1.1 Override log | 2h |
| 26.2.1 Differential analysis | 6–8h |
| 26.2.2 Invariant engine | 8–10h |
| 26.2.3 Workflow inference | 6–8h |
| 26.3 AI gating | 6h |
| 26.4 Report generation | 8h |
| 26.5 Scope wiring | 2h |
| 26.6 Component relationships | 2h |
| 26.7 Program state | 4h |
| 26.8 Legal boundary | 2h |
| **Total** | **~54–64h** |

Against measured throughput (roadmap estimates run 3–5× high; §19 was 8×), realistic calendar: **~12–20h of actual work**, i.e. 1–3 working sessions, not the 20+ the raw hours suggest.

## 26.10 Dependency order

1. 26.1 + 26.1.1 — policy layer and override log. Everything else gates on this.
2. 26.5 + 26.6 — wire the policy gate into the existing scope gate.
3. 26.7 — program state, so analysis engines have somewhere to read from.
4. 26.2.1 → 26.2.2 → 26.2.3 — analysis engines, in order of independence.
5. 26.4 — report generation, consumes the analysis output.
6. 26.3 — AI gating, last because it depends on everything above.
7. 26.8 — legal boundary docs and tests, closes the section.

## 26.12 Program URL ingestion and policy extraction — NEW

**Status:** Proposed roadmap addition; queued for implementation. Reuse the existing policy schema, YesWeHack clipboard parser, program validation, scope gate, AI gate and report templates rather than creating a parallel bounty subsystem.

**Goal:** The operator can provide a public bounty-program URL (for example, a YesWeHack program page). WHAXON ingests accessible program information, extracts policy rules into a structured draft, presents source evidence and uncertainty, and prepares a scope-constrained plan for human approval.

**Required workflow:**
1. Accept a URL or pasted/exported program text. Record source URL, retrieval timestamp, parser/version and content hash where practical. Respect authentication and platform access restrictions; provide a manual paste/import fallback when content cannot be accessed.
2. Parse assets and asset types, explicit in-scope entries, exclusions, testing permissions/prohibitions, rate limits, authentication requirements, disallowed vulnerability classes, disclosure rules, bounty eligibility and report-submission requirements.
3. Produce a structured policy draft using the existing §26.1 schema. Preserve source excerpts/locations for every material extracted rule. Label missing, inferred, contradictory, stale or ambiguous rules; do not silently invent policy values.
4. Require operator review/confirmation before saving the policy or running any tests. Refresh/review policy before a session when the source may have changed.
5. Enforce the program policy gate and existing host scope gate together. Deny by default when scope is missing, conflicting, stale, ambiguous or cannot be resolved uniquely. No AI-generated interpretation may weaken deterministic enforcement.
6. Generate a proposed test plan from only confirmed in-scope assets and permitted test classes. Require human approval before execution; no unattended bounty runs.
7. Keep provenance from source page → extracted rule → approved policy → test/action → evidence/finding → platform-specific report draft. Report drafts must satisfy §26.4 and must never be submitted without explicit human approval.

**Security requirements:** Treat page contents and linked documents as untrusted data, not instructions. Defend against prompt injection, SSRF and unsafe redirects during URL ingestion; restrict schemes and destinations, block loopback/private/link-local/metadata destinations as appropriate, revalidate redirects and DNS resolution, limit response size/time/content types, and avoid executing downloaded content. Do not bypass authentication, paywalls, platform controls or access restrictions. A URL alone is not proof of authorization.

**Acceptance tests:**
- Fixtures for valid, malformed, contradictory, incomplete, stale and changed program pages.
- Source-backed extraction with uncertainty and no fabricated scope entries.
- URL-fetch tests for redirects, private-address/SSRF attempts, oversized responses, timeouts, unsupported schemes and hostile prompt-injection text.
- Scope-gate tests proving excluded or ambiguous targets cannot run even when the AI recommends them.
- Human approval required before policy activation, testing and submission.
- End-to-end tests from fixture/page import through approved policy, plan, evidence and report draft.
- Platform-specific fixtures and report validation for YesWeHack first, with other platforms added only after their terms/access methods are reviewed.

**Sequencing:** Extend the existing §26.1 policy layer and §26.2.4 capture/report workflow. Build ingestion and policy extraction only after confirming the current clipboard parser and existing YesWeHack terms/permissions. Treat third-party platform access as a capability that must be reviewed, not assumed.

## 26.11 Not in scope

---

# 32. SOLO-FIRST v1.0 — THE VALIDATED PENTEST

**Status:** In scope, urgent. Everything else deferred until one pentester can run the full chain end to end. Full session record: ~/Desktop/whaxon_SESSION72_BRIEF.md.

**Stopping condition (R135, newly created session 72):** one pentester runs recon -> enumeration -> vulnerability -> validated initial access -> findings -> coverage-disclosed report -> retest lifecycle, on a lab target, end to end, zero false positives in the report, every finding reproducible.

**Baseline:** PR #30 commits Proof A (DVWA, four tools, 45 findings, web_service correlated, 15 reports). Proves recon-through-findings. Does NOT prove initial access, validation, coverage disclosure, or retest.

**Supersedes:** the earlier 1-2 sessions to v1.0 estimate.

**Team/enterprise forward-compat:** verification_status, coverage_ref, retest_state, actor, nullable org_id are columns from day one. Workflow model per-engagement, not per-run. Coverage queryable. Finding state machine has owner. AIRT gets its own adapter contract. Every new verb lands in a shared services layer; CLI and web UI are both clients; a parity test asserts the command and route surfaces match.

**Deferred:** §7 breadth beyond the six-tool chain, §8, §9, §10 beyond ladder needs, §17 beyond MCP stub, §18, §20, §26 beyond §26.1-§26.1.1.

## 32.0 The eleven-bug pattern

Eleven bugs this session, one shape: the framework reports success when a tool failed or did nothing. Stuck running rows, findings grouped by raw target, enumeration running no tool, nuclei fataling as success, ok unconditional, orphaned pending jobs, initialize draining, gobuster regex, ffuf scheme, stale rows with no sweep, TUI data-dir guessing. Validation and coverage are the systemic fix. Name the pattern.

## 32.1 Initial access — hydra

hydra, medusa, ncrack, patator all installed at /usr/bin, none in catalog. hydra absent from all three §7 tiers: defect.

Decision: hydra. Catalog entry with http-post-form template; adapter parses [80][http-post-form] host: X login: Y password: Z into weak_credential; ladder step in initial-access runs hydra against the discovered login path. v1 static template + --extra form fields; dynamic form discovery is follow-on.

Proof target: DVWA with admin/password.

Credential stored as a finding with credential_ref, not a bare string.

## 32.2 Validation

Demand: 87.8% say AI findings need manual review; 250 of 300 findings from one tool were junk; false-positive rate is top purchase criterion (63%), ahead of exploitability (53%) and cost (47%).

Design: whaxon validate <finding> re-runs the exact payload and confirms the response before the finding enters the report. verification_status column: candidate / verified / refuted. Report shows verified by default.

Cross-ref §17.2; §32.2 ships first.

## 32.3 Business logic inference — the unsolved core

OWASP: logic flaws cannot be detected by a vulnerability scanner — illegal state transitions, not illegal data flows.

What works: LLM-SID (88% recall, LLM infers intent + verifier executes PoC), HERETIC (reasons with an LLM, proves with deterministic code), SAGA (docs-vs-code mismatch), LogicPwn (IDOR/authz half).

Gap: all need source and docs. A bounty hunter has neither. Unsolved core.

Design: 32.3.1 observation layer (Clawbrowser/Playwright, fed to HAR adapter, depends on §26.2.4). 32.3.2 core/workflow.py state machine. 32.3.3 invariant check (LLM proposes what should NOT be possible; deterministic layer replays the violation). 32.3.4 verifier.

Six Clawbrowser capabilities, first two in v1: (a) live browser-in-UI with streaming capture, (b) policy applied to the browser not the human. Follow-on: (c) per-program persistent identities, (d) authenticated findings in the report, (e) persistent sessions for monitoring, (f) observable-not-exploited verdicts.

Provider blocker: see §32.11.

## 32.4 Coverage and non-testing disclosure

Demand: 78% saw automated scanners miss critical vulns; trust in full automation 29% to 9% in one year. Complaint is silence, not noise.

Structural: a pipeline missing one of four concerns (SAST, DAST, PT, AIRT) has a hard recall ceiling.

Design: per-job and per-engagement coverage record — endpoints behind auth not reached, WAFs that blocked tools, phases where a tool failed, concerns not covered. Report gains a Coverage section.

Blocked by the initialize() drain fix (§32.8): a run can execute unrequested jobs and coverage would report them as tested. Also blocked by the findings_by_target grouping bug (fixed session 71).

## 32.5 Remediation and retest lifecycle

Demand: AI findings 32% high-risk vs 13%; only 32% ever resolved; MTTR 19 to 36 days. Outcome bottleneck is larger than discovery.

Design: state machine open / acknowledged / in-progress / resolved / verified / closed; retest scheduling; retest re-runs validation; client-facing status.

Cross-ref §20.2; promoted. owner and org_id from day one.

## 32.6 AIRT — AI/LLM system testing

Demand: 75.3% of engagements already include AI systems, 92.4% within a year. 32% high-risk density vs 13%. Prompt injection up 540% YoY.

Without AIRT, hard recall ceiling on AI-containing applications.

Design: new adapter contract, new finding kinds, prompt injection probes, agent permission audits, RAG exposure checks.

Scope: in v1.0 only if the proof target has an AI surface; otherwise deferred with the reason recorded.

## 32.7 The six-tool access chain (§7 restructure)

Chain: subfinder -> httpx -> naabu -> katana/waybackurls -> wafw00f -> nuclei/dalfox -> gitleaks -> hydra/kerbrute -> session tools.

Six-tool minimum: subfinder, httpx, katana, wafw00f, gitleaks, hydra.

Promote: subfinder, httpx, katana, gau, kerbrute, asreproast, responder (out of Tier 3), hydra.

Demote/reject: spiderfoot, recon-ng, sn1per, red-hawk (frameworks); crunch, wgen; CMS scanners on demand.

nuclei templates are an unmanaged environment dependency (~/.local/nuclei-templates). Must be a project dependency before team use.

§26 honesty: bounties are structurally hostile to depth (58% PTaaS vs 15% public bounties; 51% first-to-file). §26 is a workflow tool, not the product center. Mobile-scope mismatch recorded: Mon Espace Sante pays 8,000 EUR for mobile criticals; §13 rejects mobile.

## 32.8 Prerequisite correctness fixes

1. initialize() drains pending jobs — one-shot whaxon run silently executes queued jobs. Decision required. Blocks §32.4.
2. data/proof-*/whaxon.db committed — remove, add regeneration READMEs.
3. nuclei templates unmanaged.
4. hydra omission from all §7 tiers — defect.
5. Mobile-scope mismatch in §26.

## 32.9 Adapter harness contract (CLI-Anything methodology)

Source: HKUDS/CLI-Anything, HARNESS.md. Six properties: State, Commands, Inspection, Rendering, Verification, Discovery.

Decision: read HARNESS.md, adopt the contract for the adapter layer, reference in docs/adapters.md. Do NOT run the generator against nmap/ffuf/nuclei. Generator use case: Burp Suite.

Actions: read and document (~2h); dual-mode CLI (~2h/adapter); --json as hard requirement; evaluate CLI-Anything for Burp (~4-6h).

## 32.10 How §32.3 consumes §26

§26 is ~24% built: platform-agnostic schema, six refusal paths, YesWeHack clipboard parser, override log, bounty policy init/list/validate and bounty run gate. Validated against five real YesWeHack pages.

The workflow model reads from the program policy — identity, rate, scope, hunting requirements. The policy file is the engagement identity.

ToS decision: YesWeHack has no supported hunter API; ToU forbids derivative use; clipboard-parse + managed browser is sanctioned. That is why §32.3 depends on §26.2.4.

## 32.11 AI provider strategy

Local inference stalled: Latitude 7490 cannot run a large enough model. Zero budget.

Tier 1 — free API for the spike: Google AI Studio Gemini Flash (free key, no billing, ~10-15 req/min, hundreds to 1,500/day). Fallback Groq (30 req/min, 1,000/day). OpenRouter :free (20 req/min, 50/day). Aggregators freelm / zerogateway. Constraint: free-tier prompts train the provider — lab targets only, not client traffic.

Tier 2 — Ollama Cloud (product path): ollama launch --model gemma4:cloud or qwen3.5:cloud. Same local API, pay-as-you-go, starter credits, gemma4 ~0.14 USD/M input tokens. Private, no hardware ceiling, no code change cloud-to-local.

Tier 3 — local inference: deferred until hardware upgrade. 7B needs ~8GB weights; 7490 ceiling is Gemma 3 4B on 16GB. Documented fallback only.

Spike: Google AI Studio key, WHAXON_AI_PROVIDER=google, workflow-labeling test against DVWA or Gruyere. Success = model labels a multi-step workflow and proposes a testable invariant.

Recorded: spike uses free API solely to prove labeling; product is Ollama Cloud; local waits for hardware.

## 32.12 Interface surface — three tabs

Discover (read-heavy): Scope, Run with phase indicator, Findings, Attack Surface, Catalog.
Operate (action-heavy): Validate, Access, Retest queue, Coverage gaps.
Report (delivery-heavy): report builder, business-impact review, coverage disclosure, CVE/exploit research, client-facing preview, export.

Parity rule (§32.12.0): every CLI verb lands in a services module; CLI and web route are both clients; a parity test asserts the command and route surfaces match, or records deliberate differences.

New shapes: validate is an action on a finding; coverage is a negative view, not a severity view — needs its own visual vocabulary; retest is a lifecycle control per finding.

Accessibility: Discover keeps ui-v4 patterns. Operate and Report need keyboard paths, focus management, screen-reader announcements, non-color meaning (WCAG 1.4.1).

Order: service layer + parity test -> schema fields -> three tabs -> features land in the right tab. Building tabs on the current split is the tear-out the strategy forbids.

Sidebar restructure is its own unit; Playwright navigation tests update in the same PR.

## 32.13 Effort and sequence

Prerequisites (incl. service layer, schema) 12h / 3 sessions. Discovery and access 16h / 4. Validation and coverage 13h / 3-4. Retest 7h / 2. Three-tab UI and accessibility 14h / 3-4. Harness contract and §26 wiring 6h / 2. End-to-end proof 3h / 1. TOTAL ~71h / ~18-20 sessions at roadmap pace; ~8-10 at measured pace. With §32.3 and §32.6: +24h / ~95h, and §32.3 needs the §32.11 provider first.

Highest-risk unit: the service-layer refactor. Touches server.py (1,218L), every CLI command, and the Playwright tests. Could produce a losing batch if done carelessly.


---

# 33. THE TRUST LAYER & COMPETITIVE MOAT (IN SCOPE, URGENT)

**Context:** Research (October 2026) reveals the market has split into three tiers: Wrappers (Sn1per), AI Agents (Shannon, XBOW, HackerOne), and Deterministic Validation (AUVAP, WHAXON). The "validation" wedge is closing, but the AI agents have a fatal flaw: high false-positive rates and LLM hallucination. WHAXON wins by being the deterministic, auditable, air-gapped **Trust Layer**. 

## 33.1 The Hybrid Validation Architecture (§32.2 refinement)
Do not build human-only queues. Do not let an LLM decide what is verified.
- **Layer 1 (Deterministic Core):** `whaxon validate <finding>` re-runs the payload. Parses response deterministically (status code, content match, timing). Sets `verification_status` to `verified` or `refuted`. No LLM.
- **Layer 2 (Human Exception Gate):** If Layer 1 is ambiguous, mark as `candidate` and queue for human review. Human reads evidence, does not re-run the payload.
- **Layer 3 (LLM Triage):** LLM summarizes evidence for the human reviewer. LLM *never* sets `verification_status`. (R71 preserved).

## 33.2 The `--reproduce` Flag (The "Proof" Moat)
To beat Sn1per and XBOW, output the deterministic proof, not just a verdict.
- Every `verified` finding must output a raw, standalone payload artifact (e.g., a `curl` command or minimal Python script) that a client can run themselves to see the bug.
- Store the HTTP request/response pair or timing delta in the finding's evidence blob.

## 33.3 The Retest Loop (§32.5 refinement)
Turn the scanner into a platform by closing the remediation loop.
- Add a `whaxon retest <finding_id>` command.
- Re-runs the exact validation payload from §33.2 against the target.
- If the hash/response no longer matches the original `verified` state, transition the finding state to `fixed`. If it still matches, transition to `still_vulnerable`.

## 33.4 Coverage Ledger (§32.4 refinement)
Clients want to know what *wasn't* tested.
- For every run, record what was skipped (e.g., "Skipped /admin, requires auth", "Skipped port 8443, WAF blocked").
- Generate a "Confidence Score" in the report based on the ratio of validated vs. inferred endpoints.

## 33.5 Air-Gapped / On-Prem Hardening
- Ensure `whaxon validate` and the deterministic core have zero external network dependencies beyond the target itself.
- Document Ollama integration explicitly for users who want local AI planning without sending target data to a SaaS provider.

## 33.6 Payload Sourcing (§32.2 dependency)
- Vendor a curated subset of `PayloadsAllTheThings` into `data/payloads/`.
- Pin to a specific commit SHA. Record MIT attribution in `ATTRIBUTION.md`.
- Build a loader that extracts payloads from code fences and maps them to finding kinds (e.g., `sql_injection`, `xss`).

## 33.7 Documentation & Design References (READ FIRST)
Before writing the code for §32.2 / §33, read these:
- **AUVAP (IEEE, June 2026):** The academic proof of deterministic pre-validation (Nmap NSE). The benchmark for filtering false positives before exploitation.
- **HunterX (Apache-2.0):** The closest architectural analogue. Read its "proof contract" model (deterministic evidence requirements per vuln class).
- **Aegis (aegis-pentest):** Read the 43 in-process verification probes (SQLi, XSS, SSRF, LFI, JWT). The cleanest taxonomy for deterministic checks.
- **Shannon:** "No Exploit, No Report" policy. Good phase architecture, but LLM-driven (violates R71).

## 33.8 Public Surface Drift (Immediate Cleanup)
The Piwheels/Google description is stale and commodity-focused. 
- Update `pyproject.toml` description to the §1 product claim (the R107 sentence).
- Update the README to lead with "Deterministic, validated pentest platform" rather than "modular portable cybersecurity testing platform."
- These changes propagate to the next PyPI release.

## 33.9 Execution Order
1. Public surface drift fix (33.8) — quick win, corrects the brand.
2. Vendor PayloadsAllTheThings (33.6).
3. Build Layer 1 Deterministic Validation + `--reproduce` (33.1, 33.2).
4. Build Retest Loop (33.3).
5. Build Coverage Ledger (33.4).

---

# 34. THE SOLO V1.0 & COMPETITIVE LAUNCH PLAN

**Status:** URGENT. Supersedes §12 (Sequencing) and §33.9 (Execution Order).

## 34.1 The Strategic Reality (Friction vs. Competitors)

To beat Sn1per, HunterX, and the AI agents, we cannot out-tool them. We must out-trust them. 
- **vs Sn1per:** They are a scanner wrapper with a read-only API and hard asset caps (30/workspace). We win by having no limits (SQLite scales) and by actually validating findings.
- **vs AI Agents (XBOW, Shannon):** They hallucinate. We win because our Validator uses urllib and deterministic baselines. No LLM decides if a bug is real.
- **vs HunterX:** They have "proof contracts" but are heavy. We win by being a single, air-gapped, stdlib-only package.

## 34.2 The Solo V1.0 Execution Path — reconciled 2026-10-25

*No unrelated feature expansion until the v1.0 acceptance checks below are complete. No Enterprise, no MCP expansion, no Clawbrowser expansion.*

The old “Next 10–12 Sessions” title and ~31h remaining implication are stale. Steps 1–4 and the core Trust Layer have implementation evidence in the current repository. Their original DONE labels mean code was reported as landed, not that every v1.0 end-to-end acceptance criterion is closed. The UI step is **not complete** merely because a prior UI pass landed or the design assets were uploaded.

1. **Adapter Request Context:** Finding model gains `request_context` (method, url, headers, body). Adapters populate it. Validator uses it to replay POST and authenticated endpoints. (~4h) — **DONE (session 73)**
2. **Blind Validation:** Timing delta check in Validator. Payload > 3s longer than baseline = `verified (blind)`. (~3h) — **DONE (session 74)**
3. **The Retest Loop (§32.5):** `whaxon retest <job_id> <seq>`. Flip status to `fixed` or `still_vulnerable`. (~2h) — **DONE (session 75)**
4. **Coverage Ledger (§32.4):** Runner logs skipped items. Report renders them + a Confidence Score. (~4h) — **DONE (session 76)**
5. **New default UI / supplied design integration (§32.12):** **PARTIAL — design assets are in the repository; new frontend integration, default-entry-point switch, backend wiring and interaction acceptance remain open. Previous UIs are deprecated reference-only and must remain unchanged.**
   - Service layer + CLI/web route parity test.
   - **Discover** (Scope, Run, Findings, Attack Surface, Catalog).
   - **Operate** (Validate, Access, Retest queue, Coverage gaps) - WCAG 1.4.1, keyboard paths.
   - **Report** (report builder, business impact, coverage disclosure, export).
   - Sidebar restructure. Playwright tests updated in the same PR.
6. **Layer 2 & 3 Trust Layer (§33.1):** Core/web approval and triage paths are present with tests. **PARTIAL acceptance:** verify ambiguous findings end to end; ensure no LLM path can promote a finding to verified.

**Remaining effort:** do not use the old ~31h / 10–12 session estimate as current remaining work. Estimate only after the release checklist below is evidenced; prioritize integration/verification rather than rebuilding framework components that already exist.

## 34.3 The Launch Sequence (after acceptance, not merely after implementation)

1. **Dogfood:** run controlled lab targets (DVWA, Juice Shop, bWAPP as available) and preserve reproducible logs; distinguish tests actually run from historical notes.
2. **Artifact:** generate reports with verification status/reasons and inspect whether each reported proof artifact is genuinely reproducible. Do not claim `curl --reproduce` support until a real artifact is emitted and tested.
3. **Content:** Write "Why AI scanners have a trust problem".
4. **Launch:** Post to HN (regular submission), then "Show HN", then r/SideProject and r/cybersecurity.

## 34.4 Deferred (The Rest of the Business)
- **MCP Server (§17.1):** Deferred until a team asks for it.
- **Business Logic Inference (§32.3):** Only if a customer explicitly asks.
- **Company-Grade (§18) & Market Coverage (§20):** Zero work until 10 private beta users.

## 34.5 Versioning Cadence (Supersedes §12)
- **Patch (v0.11.x):** Bugfixes.
- **Minor (v0.12.0):** New CLI verb (`retest`, `coverage`) or major feature.
- **Major (v1.0.0):** all release blockers in §38 closed, CI/release workflow verified, package/tag/publication state confirmed, and v1.0 acceptance evidence recorded. Version metadata alone does not constitute a release.

---

# 35. PORTFOLIO R&D PIPELINE (POST-WHAXON)

**Status:** Deferred until WHAXON, Aletheia, and KILN are stable, shipped, and have paying users. 
**Strategic Thesis:** The AI era's bottleneck is not capability, it is *trust and governance*. We win by building the trust layer for agents (Loom), for defenses (Aegis), and for data (Trove).

## 35.1 Tier 1: Build Next (The Triad)
These three form a coherent product line that builds on our existing architecture.

1. **Project Loom (Agent Governance Gateway)**
   - **What:** Framework-agnostic B2B SaaS. Sits between AI agents and enterprise APIs. Enforces Aletheia's Intent Provenance Protocol (IPP) and the Narrowing Invariant (agents cannot escalate authority).
   - **Why:** Enterprises want to use agents but cannot grant them unrestricted access. Loom is "Okta for AI Agents."
   - **Dependency:** Aletheia M1 (Governance Foundation).

2. **Project Aegis (Autonomous Adversary Emulator)**
   - **What:** Automated Red vs. Blue loop. Safely executes offensive mechanics (wrapped in WHAXON scope + Aletheia IPP) and measures if the EDR/SOC caught it. Generates a cryptographic audit trail.
   - **Why:** Clients don't just want to know they have a bug (WHAXON); they want to know if their defense caught it. (This is §20.14 BAS/AEV, formalized as a standalone product).
   - **Dependency:** WHAXON's catalog, scope, and executor.

3. **Project Trove (Data Residency Engine)**
   - **What:** DLP for the AI era. Deterministic classifiers tag data (S1/S2/S3) before it hits the LLM context. Routes S3 data to KILN (local) and S1 to cloud. 
   - **Why:** Solves GDPR and IP leakage for enterprise RAG. The AI doesn't police itself; the data layer does.
   - **Dependency:** KILN (local inference).

## 35.2 Tier 2: Defer (Requires Customer Demand)
Do not start these until a paying enterprise customer explicitly asks for them.

- **Project Vanguard (API Identity Mesh):** Temporary scoped tokens for agents to prevent prompt-injection damage. (Crowded market: Okta, Auth0).
- **Project Forge (Legacy Wrapper):** Auto-generates agent-native CLIs from legacy scripts. (Violates R160 - use CLI-Anything SOP instead).
- **Project Ostrakon (Air-Gapped Threat Intel):** Signed offline knowledge bundles for defense/healthcare. (18-month sales cycles).

## 35.3 Tier 3: Kill (Do Not Build)
- **Project Beacon (AI IR Bot):** Forensics for rogue agents. Requires selling to SOC teams; it is a feature, not a platform.
- **Project Sentry (VLM Security Cam):** Hardware play. Zero synergy with WHAXON, Aletheia, or KILN. Deleted.

## 35.4 R&D Archive Cleanup
- The `pmotadeee` / "Cascade failure" archive is a liability. It violates §13 (Ethics boundary) and R83 (Never-Build). **Delete it.** If Aegis needs adversary emulation, use MITRE ATT&CK and Atomic Red Team.
- The PENTESTING-BIBLE and Hacktronian references are redundant (PayloadsAllTheThings is already vendored). Archive or delete.

---

# 36. WEB-CHECK-STYLE RECON STAGE (WHAXON STEP ZERO)

**Status:** Phase 1 SHIPPED (commit `0e871b8`, merged via PR #65). Phase 2 PASSIVE COMPLETE (10 passive checks + parallel dispatch + CLI verb). Phase 2 remaining: third-party APIs (Shodan, CertSpotter, etc.) and active checks (traceroute, port scan, screenshots).

**Phase 2 Shipped:**
- 6 more passive checks: robots/sitemap, security.txt (RFC 9116), cookies, redirect chain (HTTPS to HTTP detection), WAF/CDN fingerprinting, DNS CAA/DMARC/SPF.
- `whaxon recon <target>` CLI verb.
- Parallel dispatch via `ThreadPoolExecutor` - wall clock = slowest single check, not the sum. 9 checks against `example.com` complete in ~6s.
- HTTP fallback: HTTPS first, HTTP on timeout - fixes timeout against HTTP-only targets.
- Per-check timeout 10s -> 5s.
- Job_id unique per run (`recon:<target>:<uuid>`) - repeat runs no longer collide on `(job_id, seq)`.

**Phase 1 Shipped:**
- `ReconRunner` (`core/recon.py`): scope-gated, exception-isolated, publishes standard `JobFindings`.
- 4 passive checks (`core/recon_checks.py`): DNS (A/AAAA/MX/NS/TXT/SOA), SSL (cert + SANs), Security Headers, Tech Stack (with correlator-shaped `open_port` emission).
- Out-of-scope targets emit `recon_out_of_scope` and are never touched.
- Core fix: `_wire_store()` now subscribes before correlator/suggester, fixing a latent race for single-event producers.
- Dependencies: `dnspython` added; HTTP uses stdlib `urllib.request`.
**Inspired by:** web-check.xyz / Lissy93/web-check (MIT)
**Scope:** Add a passive-first reconnaissance stage that feeds WHAXON's existing finding → correlator → CVE → report pipeline. Web-Check is a *starting point*, not a destination.

## 36.1 Rationale

WHAXON's deterministic, scope-controlled pipeline needs a clean "step zero" before active scanning: a passive observation pass that produces **structured findings**, not display tiles. Web-Check demonstrates the right *checks*; WHAXON supplies the missing *pipeline*.

## 36.2 Key Principles

1. **Output is findings, not a dashboard.** Every check emits a `Finding` with `kind`, `severity`, `cvss`, `cwe`, `evidence`, `source`.
2. **Every check passes through `ScopeManager`.** Passive or active, all egress is scope-gated.
3. **Discovered out-of-scope hosts are surfaced, never auto-scoped.** SANs, related infrastructure, third-party API hits — proposed as "out-of-scope discovery," awaiting human authorization via the override log.
4. **Third-party intelligence is tagged distinctly.** `source: "provider:shodan"` etc., separating it from direct observation for evidence integrity.
5. **Active checks are gated separately.** Traceroute, port scan, headless-Chromium screenshots require explicit invocation.
6. **Skip the novelties.** Carbon footprint, global rank, social presence — not pipeline-relevant, excluded.

## 36.3 Phase 1 — Prove the pipeline (small, structural)

**Goal:** Answer — *does WHAXON's finding/correlator/report machinery consume passive recon cleanly, or does it need extending?*

Four checks only:
- **DNS** (A / AAAA / MX / NS / TXT / SOA)
- **SSL / certificate SANs** (highest-value pivot source)
- **Security headers** (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, etc.)
- **Technology stack** (framework / CMS / CDN / JS library from headers + HTML)

**Success criterion:** end-to-end — scope → observation → finding → correlator → CVE match → report line. With 4 working, 26 more is mechanical.

## 36.4 Phase 2 — Fill the pipe (everything else)

- **Remaining passive checks** — robots.txt, sitemap, security.txt, cookies, redirect chain, WAF detection, full DNS record set
- **Third-party API integrations** (`provider:*`, gated behind optional keys): Shodan, Google Cloud (PageSpeed + Safe Browsing), Cloudmersive, Tranco, CertSpotter, GitHub
- **Active checks** (separately gated): traceroute, port scan, headless Chromium screenshot
- **UI** — built last, once real data flow is known

## 36.5 Rejected Approach

Do **not** split by passive-first / active-second. The load-bearing axis is "pipeline exists" vs "checks exist." Passive/active is a safety concern, handled orthogonally by `ScopeManager` on every check.

## 36.6 Explicit Non-Goals

- No dashboard-first design
- No auto-scope-expansion from discovered hosts
- No porting of Web-Check's Node.js implementation (Python stdlib + `httpx` + `dnspython` + existing Playwright)
- No novelties (carbon, rank, social) in the pipeline

---

# 37. POST-V1.0 STRATEGIC PIVOTS (DEFERRED)

The following items are deferred until v1.0 is fully deployed. They represent the transition from an "Orchestrator" to a "Full-Loop Vulnerability Management Platform" and a response to competitive architectures like Cairn.

## 37.1 The Fact-Intent Graph (Cairn Architecture)
**Status:** DEFERRED until v1.0.
**Goal:** Replace the linear AI planner with a Directed Acyclic Graph (DAG) state-space search.
*   **Primitives:** Facts (confirmed findings), Intents (declared exploration directions), Hints (human-injected judgment).
*   **Coordination:** Stigmergic (agents read/write to a shared board, no direct chatter).
*   **Trust Layer Integration:** Agents cannot write "Facts" directly. They submit a "Candidate". The Trust Layer replays the payload. Only verified candidates become Facts on the graph.
*   **Convergence Monitor ("The Gardener"):** A supervisor that detects stagnation (no new facts after N iterations) and pauses for human review.

## 37.2 Hints System
**Status:** DEFERRED until v1.0.
**Goal:** Allow human operators to inject guidance without restarting the agent.
*   Add a "Hints" input to the Classic UI.
*   Hints are logged with timestamp, operator identity, and cryptographic signature.
*   The AI planner absorbs the hint on its next OODA loop.

## 37.3 Bounded Autonomy & Governance
**Status:** DEFERRED until v1.0.
**Goal:** Prevent the 23+ hour unbounded runs seen in Cairn.
*   **Budget Caps:** Hard limits on API tokens and tool executions per project.
*   **High-Impact Approval:** Exploitation actions (RCE, file upload, DB write) require explicit human approval via the UI.
*   **Playwright Pre-Screen:** Validate a target is "alive" before spawning an AI worker.

## 37.4 App-to-Backend (A2B) Attack Chain
**Status:** DEFERRED until v1.0.
**Goal:** Match Cairn's ability to reverse-engineer Android APKs to find backend API endpoints.
*   **Workflow:** Download APK -> Reverse engineer (apktool/jadx) -> Extract API spec.
*   **Governance:** Extracted endpoints are *proposed* to the operator. The operator must approve adding them to `data/scope.json` before the AI can test them.

## 37.5 Proof-Driven Remediation (The Full Loop)
**Status:** DEFERRED until v1.0.
**Goal:** Transition from finding the bug to telling the user how to fix it.
*   **Static Mapping:** Add `data/remediation_rules.json`. Map verified finding kinds (e.g., `sqli`) to exact remediation text (e.g., "Use parameterized queries").
*   **Report Enrichment:** The report renders the remediation context *next* to the verified proof.
*   **Post-Fix Verification:** The report includes the exact `whaxon retest` command for the client to verify the patch.

---



---

# 38. V1.0 RELEASE BLOCKERS AND ACCEPTANCE CHECKLIST

**Status: OPEN until each item has evidence recorded.** This section is the operational release gate and supersedes optimistic DONE labels elsewhere when acceptance evidence is missing.

- [ ] **Framework-to-roadmap crosswalk:** map each v1.0 stopping-condition stage (recon, enumeration, vulnerability discovery, initial access where supported, deterministic validation, findings, coverage/non-testing disclosure, reporting, retest) to the actual source path and automated test(s). Mark unsupported scope explicitly; do not claim zero false positives as a universal property.
- [ ] **Validation trust boundary:** test SQL/error-marker, reflected-XSS, timing/blind, observation-probe and request-context replay paths. Candidate/inconclusive results must not be reported as verified; the LLM must never set verification status. Record timing caveats.
- [ ] **Retest semantics:** verify that retest accepts only eligible previously verified findings and produces the documented `fixed`, `still_vulnerable`, or `inconclusive` result with a reason. Align the older “flip status” language in §§32–34 with the current implementation.
- [ ] **Coverage honesty:** prove that skipped/failed/unrequested work is not silently counted as tested. Confirm the report's coverage section and confidence claims are based on persisted evidence; if this is not implemented end to end, mark it as a blocker rather than DONE.
- [ ] **New default UI:** implement the supplied design as WHAXON's default frontend, matching the checked-in HTML/PNG references and design system. Connect supported actions to the framework/services; hide/disable unsupported controls in the live UI; add/execute Playwright navigation, interaction and visual regression tests. Create a separate new-UI interaction audit. Preserve all previous UI templates, CSS/JS, mockups, screenshots and `docs/WEB_UI_INTERACTION_AUDIT.md` unchanged as deprecated reference material.
- [ ] **Security regressions:** run the scope fail-closed, target-boundary, auth fail-closed, job cancellation/descendant termination and request-context regression tests. Document residual deployment constraints (including external egress enforcement and DNS rebinding/pinning limitations).
- [ ] **Packaging:** build wheel and sdist; install the wheel in a clean environment; verify CLI help, packaged payload/catalog resources, scope initialization, and local observation-validation smoke test.
- [ ] **CI and release workflow:** verify all required Python-version jobs are green on the candidate commit; resolve or explicitly disposition any open CI blocker. A workflow definition or a past green run is not proof of current green status.
- [ ] **Release identity:** confirm the intended tag matches `pyproject.toml`, the release workflow succeeds, and the intended package index shows the expected version. Do not state “released” until checked.
- [ ] **Docs synchronization:** refresh `docs/STATE.md` after the above checks; update the UI audit and this roadmap with observed results and commit/test references. Remove stale estimates only when the replacement evidence is recorded.

**Release decision rule:** any unchecked item that affects correctness, safety, the user-visible UI, report honesty, or installability blocks calling the product release-ready. Deferred commercial/team features are not blockers unless required by the agreed solo v1.0 scope.

# 39. TOOLING PORTFOLIO REVIEW — ADDITIONS, SUBSTITUTIONS AND ACCEPTANCE GATES

**Status:** Proposed roadmap amendment, based on a portfolio review of §7 and the candidate inventory. This section refines priorities; it does not mean the tools below have already been integrated or tested. Existing §7 remains the historical inventory until §39.8 reconciles it.

## 39.1 Decision

Keep the strategic objective of broad tool coverage, but optimise for **distinct capability, maintainability, structured evidence and verified end-to-end behaviour**, not raw adapter count. Do not add a tool solely to reach 120.

A tool integration is not production-ready merely because its adapter is registered or its parser passes fixture tests. Track these states separately:

1. `planned`
2. `implemented`
3. `installed`
4. `smoke-tested`
5. `validated-on-lab`
6. `end-to-end-verified`

Only the final state counts as production-ready coverage. Every integration must have a named supported version/platform, input contract, scope policy, timeout/cancellation behaviour, structured output, error semantics, evidence provenance, test fixtures and at least one end-to-end lab proof.

## 39.2 Priority additions and promotions

These are candidates or capability priorities, not claims of current integration.

### Promote or make first-class

- **Nuclei:** already in the current catalog; make its template-based checks a first-class pipeline stage. Pin/review template sources, preserve template ID and version, enforce scope, capture raw evidence and send candidates through WHAXON validation. Template output alone must not imply `verified`.
- **Naabu:** evaluate for fast port discovery complementary to Nmap. Use as an asset-discovery stage, not an Nmap replacement.
- **Gowitness:** promote from Tier 2 to the asset triage/reporting workflow for screenshots, with headless-browser isolation and resource limits.
- **gau:** retain as a complementary historical URL source to waybackurls where source coverage differs; deduplicate results.

### Add as evaluation candidates

- **OWASP ZAP:** evaluate for active web/API scanning and automation API integration, comparing coverage, output quality and operating cost against existing Burp and scanner workflows.
- **Interactsh:** evaluate for controlled out-of-band evidence for blind vulnerabilities. Prefer a controlled instance where practical; correlate every callback to a unique test, enforce scope, document external data flows and never let a callback alone bypass the Trust Layer.
- **Syft + Grype:** evaluate as a paired SBOM-generation and component-vulnerability workflow. Preserve SBOM provenance and component/package identifiers.
- **Kubescape:** benchmark against Trivy, kube-bench and kubeaudit before adoption; add only for demonstrated coverage gaps.
- **TruffleHog:** benchmark against Gitleaks before adoption; keep both only if measured source/secret coverage justifies the maintenance burden.
- **RESTler or another schema-aware API fuzzer:** evaluate only after OpenAPI/Swagger ingestion, authentication/session handling, per-operation scope enforcement and deterministic validation are available.
- **SharpHound:** evaluate as an alternative/addition to bloodhound-python only if Windows collection materially expands supported environments.
- **enum4linux-ng:** prefer for new SMB/Windows enumeration work over the older enum4linux, subject to compatibility tests.
- **ssh-audit:** evaluate as a clearly identified SSH configuration-audit capability; first confirm the exact project and supported output contract.

## 39.3 Recommended substitutions and de-duplication

Apply these as review decisions, not blind deletions. Confirm the exact upstream project, current maintenance, license, supported platforms and test results before changing the active inventory.

- **enum4linux → enum4linux-ng** for the preferred modern SMB enumeration path; retain the original only if a real compatibility requirement exists.
- **wfuzz vs ffuf:** keep ffuf as the default directory/content fuzzing integration. Retain wfuzz only for a demonstrated distinct workflow.
- **XSStrike vs Dalfox:** benchmark both against a controlled XSS corpus. Keep both only if the measured coverage or workflow difference justifies maintaining both.
- **testssl vs SSLyze vs sslscan:** choose a primary TLS assessment path and preserve a second tool only where it adds distinct checks or independent corroboration. Normalise overlapping findings.
- **Droopescan vs Drupwn:** favour one maintained CMS coverage path; do not maintain duplicate Drupal enumeration without evidence of a gap.
- **WhatWeb vs CMSeeK vs other CMS/fingerprint checks:** share deduplication and technology-identification logic; retain tools only for distinct supported technologies or measurable coverage.
- **Medusa vs Ncrack vs Patator vs Hydra:** select a primary authorised authentication-audit integration based on protocol coverage, reliability and rate-limit controls. Do not integrate all four merely for breadth.
- **Hashcat vs John the Ripper:** keep Hashcat as the existing baseline; evaluate John only for demonstrated format or workflow coverage not already met.
- **Subfinder vs Sublist3r vs Assetfinder vs Amass:** keep the tools that contribute distinct passive sources or discovery modes; deduplicate assets and record provenance.
- **Scoutsuite vs Prowler:** benchmark cloud-service and rule coverage. Keep Scoutsuite only if it fills an evidenced gap.
- **Skipfish, Dmitry, Red-Hawk, Infoga, Recon-ng, Ghost-Eye, Cero and similar lower-priority candidates:** defer until project identity, maintenance, licensing, output quality and distinct capability are verified.
- **Sn1per:** do not prioritise as a normal scanner dependency because it is itself an orchestration product and risks duplicating WHAXON's core role.
- **SQLNinja:** defer unless it adds a tested SQL Server-specific workflow not covered by SQLMap and WHAXON's validation layer.
- **Crunch and other wordlist generators:** treat as supporting utilities, not vulnerability scanners; adopt only if a concrete workflow needs them.

## 39.4 Reconnaissance pipeline

Target flow:

`passive sources → DNS resolution → HTTP probing → port/service discovery → crawling and historical URLs → vulnerability checks`

Candidate sequence:

- Passive asset sources: Subfinder, Amass, certificate-transparency/DNS sources, gau/waybackurls.
- DNS resolution: dnsx and the existing resolver path.
- HTTP metadata: httpx.
- Port discovery: evaluate Naabu alongside existing Nmap.
- URL discovery: Katana plus historical URL sources.
- Visual triage: Gowitness.
- Vulnerability checks: existing catalog scanners and Nuclei, subject to template and scope controls.

Every discovered hostname/IP/URL must retain provenance, be deduplicated, and pass scope evaluation before active requests. Related infrastructure discovered through certificates or third-party providers is a proposal for operator review, never an automatic scope expansion.

## 39.5 Cloud, code, containers and software supply chain

Keep Prowler, Trivy, Checkov, Semgrep and Gitleaks as foundational candidates. Design separate contracts for each data plane:

- **Cloud posture:** cloud account/tenant identity, least-privilege permissions, region/service coverage, API-call audit and explicit cloud scope.
- **Infrastructure as code:** repository/path input, policy/rule identifiers, file/line evidence and SARIF-compatible output where supported.
- **Containers and dependencies:** image/repository/filesystem input, package identity, fixed-version information, SBOM linkage and provenance.
- **Kubernetes:** cluster/context identity, permissions, namespace/resource scope, read-only default and explicit approval for any active action.
- **Secrets:** secret type and location evidence, with secret values redacted from normal logs and reports.

Evaluate Syft/Grype, Kubescape and TruffleHog as in §39.2. Avoid adding multiple tools with substantially duplicate rules unless measured results justify the extra install and maintenance burden.

## 39.6 API security capability

Add a capability workstream, not just a tool name:

- Import OpenAPI/Swagger specifications and enumerate operations.
- Retain authentication/session context safely, including refresh/expiry handling.
- Enforce scope at the operation, host and redirect levels.
- Support schema-aware input mutation and rate limits.
- Distinguish discovery from validation; preserve request/response evidence with secrets redacted.
- Evaluate ZAP and RESTler only after these foundations have acceptance tests.

## 39.7 Tier 3 session and high-impact tool policy

Do not treat Windows-native utilities, credential-access tools, network poisoning tools and command-and-control frameworks as equivalent scanner adapters.

Before admitting any Tier 3 tool, define: supported session type, OS/version, privilege requirement, permitted operation classes, human-approval boundary, output contract, timeout/recovery, cleanup, audit trail and lab verification. Default to read-only collection. Credential-access, permission-changing, network-poisoning and C2 capabilities require separate explicit policy and must not run as ordinary unattended scan steps. Covenant and Empire should be deferred from the normal tool catalog unless a separate, justified adversary-emulation product boundary is approved.

## 39.8 Inventory and estimate reconciliation — blocking bookkeeping task

Before the next tool-adoption batch:

1. Reconcile the stated target of 120, current count of 25, and claim of 95 additions against the actual unique tool IDs in the catalog and Tier lists.
2. Resolve Tier totals (44 + 42 + 14 = 100) and category/list discrepancies, including the Tier 2 knockmail note.
3. Distinguish tools, adapters, commands, providers, data sources and capabilities; do not count aliases or multiple wrappers for one executable as separate tools without a documented reason.
4. For every candidate, record upstream URL, license, maintenance/activity check date, install method, supported OS, required privileges, output format, unique capability, overlap, scope risk, test plan and decision.
5. Re-estimate integration effort after a representative pilot from each execution class: CLI scanner, cloud SDK/API, source-code scanner, GUI-driven integration and session-scoped Windows tool. The existing ~171h figure is a planning hypothesis, not a validated delivery commitment.

## 39.9 Acceptance gates for every adapter

- Scope is checked before every target-bearing action, including redirects, discovered hosts, callbacks and child processes.
- No automatic scope expansion; proposed new assets require operator approval.
- Tool output is structured and normalised without losing raw evidence or source attribution.
- Exit code, timeout, partial output and tool-level errors are represented distinctly; exit code 0 is not proof of success.
- Repeated findings are deduplicated while preserving all source references.
- Findings enter the deterministic Trust Layer; the LLM may summarise evidence but never sets verification status.
- Tests cover malformed output, missing executable, unsupported version, timeout, cancellation, out-of-scope input, partial output and false-positive/false-negative lab cases.
- Documentation states prerequisites, permissions, side effects, rate limits, supported targets and safe-use constraints.

## 39.10 Recommended execution order

1. Reconcile the inventory and add per-tool decision records.
2. Finish and regression-test the v1.0 Trust Layer, request-context replay, retest and coverage disclosure.
3. Make Nuclei first-class and strengthen the existing recon → scan → validate → report pipeline.
4. Pilot Naabu and Gowitness; retain only if end-to-end results justify the adapters.
5. Design cloud/code/SBOM contracts, then pilot Syft/Grype and one cloud workflow.
6. Evaluate ZAP and Interactsh in controlled labs.
7. Add API-spec-driven testing after authentication, operation scope and validation are proven.
8. Reassess Tier 2 based on measured unique coverage.
9. Implement Tier 3 only after the session contract and explicit high-impact policy pass tests.

**Success metric:** verified, reproducible coverage across supported asset and finding classes, with documented gaps and low false-positive rates—not the number of tool names in the catalog.

---

# 40. DEPENDENCY READINESS AND GUIDED INSTALLATION (NEW)

**Status:** Proposed roadmap addition; queued for implementation. Cross-cutting product capability for first install, upgrades and runtime health checks. This does not replace §39's per-tool install metadata or §38's clean-install release gate.

## 40.1 Goal

WHAXON should identify whether its runtime requirements and selected external tools are present and usable on the user's machine. When something is missing or incompatible, it should explain the impact and offer a safe, user-approved installation or repair path.

## 40.2 Required capabilities

1. **Dependency inventory:** Maintain a versioned, machine-readable manifest that distinguishes required runtime/package dependencies, optional integrations and external executables. Record version constraints, supported OS/platforms, detection method, install options, privilege requirements, license/source and smoke-test command.
2. **Preflight checks:** Run at install/upgrade and on demand or first use. Check interpreter/runtime compatibility, Python packages, executable presence and version, configured paths, required data/resources and tool health. Distinguish missing, incompatible, misconfigured, installed-but-broken, unsupported and not-yet-checked states.
3. **Feature impact:** Map each dependency to the WHAXON capabilities that require it. Do not block unrelated features because an optional tool is absent; clearly disclose when a feature cannot run.
4. **Guided remediation:** Offer platform-appropriate instructions and supported install methods for Windows, Linux and macOS, with distro-specific handling where necessary. Prefer virtual environments/user-local installs and package-manager-native methods where safe. Provide manual/offline instructions when automated installation is unavailable.
5. **Explicit consent:** Show the proposed command, source, package/version, privileges, likely changes and any costs/network access before executing an installation. Never silently elevate privileges, alter security controls, install unrelated software or execute commands copied from tool output.
6. **Safe execution and recovery:** Use allowlisted installers/commands and trusted package sources; validate inputs; apply timeouts and cancellation; capture exit status/output; avoid shell-string construction where argument arrays are available. Make partial failures recoverable and report exactly what changed.
7. **Post-install verification:** Re-detect version and path, run a safe non-target smoke test, and only mark a tool as installed or smoke-tested when that state is supported by observed evidence. Installation success alone does not mean production-ready.
8. **Audit and privacy:** Record check results and user-approved actions with timestamps and dependency versions. Do not collect unrelated machine inventory or upload local environment details without clear consent.
9. **Offline and restricted environments:** Support diagnostic-only mode and documented manual installation when internet, package managers, permissions or repositories are unavailable.
10. **Documentation and diagnostics:** Provide human-readable and machine-readable reports, actionable remediation, and copyable diagnostics that redact secrets and sensitive paths where appropriate.

## 40.3 Acceptance criteria

- Test on clean and partially provisioned environments for each supported OS/platform.
- Correctly classify missing, wrong-version, broken, optional and healthy dependencies.
- Verify no installation or privileged action occurs without explicit approval.
- Verify cancellation, timeouts, offline operation, failed package managers, malicious/malformed tool output and interrupted installs.
- Confirm installed executables are found reliably without relying on a developer's local PATH or hardcoded personal paths.
- Confirm each dependency's smoke test is safe and does not send requests to third-party targets.
- Confirm absent optional dependencies disable only dependent capabilities and are clearly reported.
- Confirm preflight and post-install results agree with the actual executable/version and the §39 tool-readiness states.
- Add CI tests for manifest validation, dependency detection and mocked installation flows; use isolated clean-environment integration tests for actual installer behavior.
- Update packaging, install documentation and §38 release acceptance checklist once implemented.

## 40.4 Recommended implementation order

1. Inventory current runtime, package, catalog/resource and external-tool dependencies; reconcile with §7, §38 and §39.
2. Define the manifest schema and deterministic detection interfaces.
3. Implement read-only preflight and a clear diagnostic report first.
4. Add OS-specific remediation plans and explicit approval UX; keep command execution allowlisted.
5. Add post-install smoke tests and auditable readiness states.
6. Integrate checks into packaging/first-run/upgrade flows and the existing UI without redesigning it.
7. Validate on clean Windows, Linux and macOS environments and document unsupported cases.

**Relationship to other roadmap items:** §7 tool adoption supplies per-tool install metadata; §9 distro portability defines platform coverage; §18 deployment/installer/upgrade work consumes this capability; §38 packaging and clean-install acceptance verifies it; §39.8 inventory reconciliation is a prerequisite for a trustworthy manifest.
