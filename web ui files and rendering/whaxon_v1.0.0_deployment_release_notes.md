# WHAXON v1.0.0 — Production Release Notes

**Release Tag:** `v1.0.0-gold`  
**License:** AGPL-3.0-or-later  
**Target Environment:** Python 3.11+ / Kali Linux / Debian Stable / Hardened Containers  
**Verification Suite:** Full deterministic test pass (`pytest tests/ -q` — 0 warnings, 0 flakes, 0 lint regressions)

---

## 1. Executive Summary

WHAXON v1.0.0 marks the transition from an autonomous prototype orchestrator to a **forensically hardened, deterministic security operations and penetration testing platform**. 

Built to solve the critical "trust problem" plaguing automated security scanners, WHAXON enforces an uncompromising invariant: **No LLM decides if a vulnerability is real. Deterministic proof does.** 

Every verified finding produces an offline-reproducible proof artifact (`curl` command, isolated canary verification, or non-destructive probe replay). Findings without verifiable proof remain strictly classified as `candidate` and are quarantined in an auditable human review queue, ensuring zero false-positive leakage into final executive deliverables.

---

## 2. Key Capabilities & Architectural Pillars

### 2.1 The Trust Layer & Deterministic Verification
- **Active Canary Verification Engine:**
  - **Cross-Site Scripting (XSS):** Verifies that injected payloads parse as an active SVG/DOM event handler, eliminating inert reflection false positives.
  - **Remote Code Execution (RCE):** Strictly requires an execution canary token verified to be absent from the submitted input payload string to prevent command echo mirroring.
  - **SQL Injection (SQLi):** Employs non-destructive SQL error probe matching and parameterized baseline validation.
  - **Blind Timing Metrology:** Median-of-3 baseline vs. injected timing delta verification with jitter rejection to prevent network latency spikes from falsifying findings.
- **Three-Way Retest State Machine:**
  - Findings transition strictly between `FIXED`, `STILL_VULNERABLE`, and `INCONCLUSIVE`.
  - Inconclusive replays (e.g., target timeouts, rate-limiting) never default to remediation, preventing premature closure of open risks.
- **Reproducible Evidence Proofs:**
  - Standalone `curl` commands with context replay headers (`X-SecOps-Audit`, `X-SecOps-Proof-Author`) and SHA-256 evidence integrity hashes.

### 2.2 Forensic Hardening & Process Isolation
- **Zero-Credential `argv` Guarantee:**
  - All transport credentials (SMB, WMI, RPC) are streamed via newline-delimited standard input (`stdin`) with strict control-character hygiene validation. Passwords and session hashes never leak into `/proc` or `ps` listings.
- **Recursive Process Tree Teardown:**
  - Subprocess runner tracks leader PIDs and active descendant trees. Aborting or timing out a tool execution triggers a recursive cascade (`SIGTERM` → `SIGKILL`) preventing orphaned daemon processes from lingering in the background.
- **Context Replay SSRF Defense:**
  - Mandatory authorization guard requires explicit target registry matching prior to payload replay.
  - Automatic rejection of embedded credentials (`http://user:pass@host`) and parameter-tampered alternate targets.
- **Global Scope CIDR Anomaly Guard:**
  - Active detection and hard-blocking for overbroad CIDR definitions (`/0` through `/8`) requiring explicit cryptographic sign-off.

### 2.3 Coverage Ledger & Non-Testing Disclosure
- **Methodology Transparency:**
  - Quantifies skipped paths, unreachable services, and WAF-blocked endpoints grouped by PTES phases (Recon, Enumeration, Vulnerability).
  - Reports disclose non-tested attack surface explicitly, preventing false senses of security.

---

## 3. Web UI Operations Suite (24 Operational Views)

The unified Web UI delivers end-to-end mission workflows across four core domains:

| Domain | Key Modules & Screens |
| :--- | :--- |
| **I. Core Architecture** | • **Dashboard & Engagement Hub:** Zero-state onboarding, real-time KPI metrics, active engagements.<br>• **Scope & Target Definition:** Atomic write rules, BGP route matching, CIDR guard alerts.<br>• **Run & Tool Orchestration:** SSE execution bus, live terminal, process group isolation monitor.<br>• **Trust Layer & Verified Findings:** Canary verification badges, neutral discovery filters.<br>• **PTES Coverage & Reports:** Real-time methodology gap ledger, standalone PDF/HTML5 generator. |
| **II. Verification & Simulation** | • **Remediation Retest Studio:** 3-way verdict state machine, median-of-3 timing delta metrology.<br>• **Correlated Attack Chains:** Graph traversal of pivot nodes, loot correlation, root-cause trees.<br>• **AI Strategy Gate:** Bounded LLM task planner, human-in-the-loop approval gate.<br>• **BAS & Detection Validation:** Automated adversary emulation, SIEM/EDR detection gap analysis.<br>• **Attack Surface Monitoring:** Continuous discovery, DNS change detection, exposure scoring.<br>• **Bug Bounty Studio:** Managed browser harness, program policy compliance, differential session inspection. |
| **III. Audit & Forensics** | • **Cryptographic Audit Log:** Tamper-evident hash-chained activity ledger with operator signatures.<br>• **Evidence File Inspector:** Raw response body viewer, Merkle root verification, redaction flags.<br>• **Job Execution History:** Subprocess stdout/stderr archive, duration profiling, exit code audit.<br>• **System Diagnostics & Health:** Daemon telemetry, memory/socket leak detection, worker thread pools.<br>• **Adapter & Plugin Manager:** Adapter capability matrix, binary path validator, CLI argument contracts.<br>• **Settings & Secrets Vault:** Enclave credential storage, rate governor, webhook dispatchers. |
| **IV. Client & Delivery** | • **PTaaS Client Portal:** Executive deliverable repository, self-service scoping, client ticketing.<br>• **Threat Intel & Exploit Arsenal:** Offline Searchsploit index, CISA KEV feeds, EPSS percentiles.<br>• **Compliance Crosswalk:** Direct mapping to SOC 2, PCI-DSS v4.0, ISO 27001, and NIST CSF. |

---

## 4. Breaking Changes & Upgrade Path

1. **Replay URL Syntax:** URLs containing embedded user credentials (e.g. `https://admin:pass@api.corp.net`) will now throw an `InvalidReplayTargetError`. Pass authentication tokens via `--headers` or `WHAXON_AUTH_*` environment variables.
2. **Subprocess Credential Transport:** Any custom adapters relying on passing passwords via CLI command-line arguments must migrate to the `stdin` newline-delimited stream protocol.
3. **HTTP 200 Path Discoveries:** Paths discovered via directory fuzzers (`ffuf`, `gobuster`) are strictly categorized as `informational` and will no longer increment vulnerability counts without active canary proof.
4. **Scope Storage Format:** Scope files now use atomic writes (`0600` permissions with `os.replace`). Legacy unversioned scope files will be migrated automatically on first boot.

---

## 5. Deployment & Quick Start

### 5.1 Package Installation
```bash
python -m pip install --upgrade pip
python -m pip install "whaxon[tui,web,gui,metasploit]"
```

### 5.2 System Initialization
```bash
# Initialize local database and default scope boundary
whaxon init
whaxon scope --show

# Verify adapter binaries and execution environment
whaxon state
```

### 5.3 Starting the Web Daemon
```bash
# Production background service binding to loopback
whaxon serve --host 127.0.0.1 --port 5001 --workers 4

# Or launch the desktop workbench directly
whaxon gui
```

> **Security Advisory:** When binding `whaxon serve` outside `127.0.0.1`, set `WHAXON_AUTH_PASS_HASH` in `.env` immediately. The service will refuse to bind to public interfaces with default credentials.

---

**Artifact SHA-256:** `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`  
**Signed by:** Lead Security Engineer (`OP//7749-ALPHA`)  
**Status:** Certified for Production Deployment
