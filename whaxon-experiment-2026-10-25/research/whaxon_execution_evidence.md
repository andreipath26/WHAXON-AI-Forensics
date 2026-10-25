# WHAXON Execution Evidence

**Purpose of this document:** prove that WHAXON itself performed the security assessment in this
study, distinguish WHAXON's results from independent verification, and record exactly what it could
and could not do.

**Engagement:** 2026-10-25, `research/forensics-2026-10-25`
**Result in one line:** WHAXON ran a real, scope-gated assessment (recon + ffuf + sqlmap) against an
authorized DVWA target and an authorized local ground-truth lab, discovered a genuine SQL injection,
correctly refused to mark it `verified`, and reproduced that behaviour on a repeat run.

---

## 1. Verified version and source commit

| Item | Value | How established |
| --- | --- | --- |
| WHAXON version | **0.11.16** | `importlib.metadata.version('whaxon')` inside the dedicated venv |
| WHAXON source commit | **`5b61fa5fc835fe2d4a97cd7977d295b1a642d0b3`** (branch `main`, 2026-10-23) | fresh clone of `https://github.com/andreipath26/WHAXON` |
| Python package path | `<workspace>/.venv-whaxon/lib/python3.12/site-packages/...` via `pip install -e ./work/WHAXON[dev,web]` | `whaxon.__file__` |
| CLI executable | `<workspace>/.venv-whaxon/bin/whaxon` (entry point `whaxon.cli:main`) | `which whaxon` |
| sqlmap (executed by WHAXON) | commit `c9745f883d2a5b70de8b786fcd3451e9b991da8a`, version `1.10.10.19#dev` | `git -C work/sqlmap rev-parse HEAD` |
| ffuf (executed by WHAXON) | v2.3.0, `sha256 4b52c335…ea52f`, verified against the project's official `ffuf_2.3.0_checksums.txt` | installed to `~/.local/bin/ffuf` |

### 1.1 The two repositories are not the same (and diverge)

The user's task names both a *tool* repository and a *research* repository. They are separate and
**their code differs**, which materially affects the results below:

| | Tool repo `andreipath26/WHAXON` | Research repo `andreipath26/WHAXON-AI-Forensics` |
| --- | --- | --- |
| commit used | `5b61fa5` (main) | `a577fc7` (main) |
| `version` in `pyproject.toml` | 0.11.16 | 0.11.16 (identical version string) |
| `core/validator.py` | `REPLAYABLE = {sqli, xss}` | adds `command_injection` + canary probes |
| `core/scope.py` | CIDR rules applied only to `kind == "ip"` | CIDR rules applied to every target |
| `adapters/` | no `commix.py` | has `commix.py` |
| `business_impact.py` | no `command_injection` mapping | has it |

`diff -rq work/WHAXON/src <research>/src` reports 6 differences. **All measurements in this
document are against the tool repo at `5b61fa5`**, which is the version published to users; the
research tree's extras are noted where they change the conclusion (§7, D2/D3).

## 2. Exact invocation / supported operations used

Every step used WHAXON's own documented CLI (derived from `whaxon --help` and the per-command
`--help` output, not from source reading):

```bash
# environment
python3 -m venv .venv-whaxon && .venv-whaxon/bin/pip install -e "./work/WHAXON[dev,web]"

# 1. initialise a data directory
whaxon init --data evidence/whaxon-run

# 2. authorization through WHAXON's own mechanism
whaxon scope --check "https://pentest-ground.com:4280/" --data evidence/whaxon-run   # -> denied (exit 1)
whaxon scope --set evidence/whaxon-run/authorized-scope.json --data evidence/whaxon-run
whaxon scope --check "https://pentest-ground.com:4280/" --data evidence/whaxon-run   # -> allowed

# 3. passive discovery
whaxon recon "https://pentest-ground.com:4280/" --data evidence/whaxon-run --verbose

# 4. active discovery through WHAXON's runner (ffuf registered in the documented catalog)
whaxon run ffuf "https://pentest-ground.com:4280" --data evidence/whaxon-run \
        --extra "-t 2 -rate 5 -timeout 15" --verbose

# 5. active vulnerability testing through WHAXON's runner (sqlmap)
whaxon run sqlmap "http://127.0.0.1:8100/low?id=1"   --data evidence/whaxon-run   # injectable
whaxon run sqlmap "http://127.0.0.1:8100/safe?id=1"  --data evidence/whaxon-run   # parameterized control
whaxon run sqlmap "http://127.0.0.1:8100/low?id=1"   --data evidence/whaxon-run   # repeat (reproducibility)

# 6. WHAXON's own validation layer
whaxon validate 86c7295507ae <seq> --data evidence/whaxon-run          # found_path findings
whaxon validate 66b0be3c50f2 <seq> --data evidence/whaxon-run --verbose # sqli findings
whaxon retest   66b0be3c50f2 0    --data evidence/whaxon-run

# 7. results and reporting
whaxon findings pentest-ground.com --data evidence/whaxon-run
whaxon jobs export 66b0be3c50f2 --format json --data evidence/whaxon-run
whaxon report --engagement default --format md --all-findings --out evidence/whaxon-run/whaxon-report.md
```

## 3. Evidence that the real WHAXON process executed

1. **Real child processes were spawned.** `whaxon run ffuf` streamed ffuf's own output lines and
   reported `[run] finished: exit=0 in 56.34s`; `whaxon run sqlmap` streamed sqlmap's own
   timestamped lines (`[INFO] testing 'MySQL …'`, `sqlmap identified the following injection
   point(s) with a total of 42 HTTP(s) requests`) and reported `exit=0 in 11.38s`.
2. **The store contains real job rows** (`evidence/whaxon-run/whaxon.db`, table `jobs`):

| job id | tool | target | exit | duration (s) |
| --- | --- | --- | --- | --- |
| `recon:https://pentest-ground.com:4280/:a68fecd9392b` | recon | DVWA | — (see §7 D6) | — |
| `86c7295507ae` | ffuf | `https://pentest-ground.com:4280` | 0 | 56.34 |
| `6f5b6e2a80f7` | sqlmap | lab (string-simulated, abandoned) | 0 | 150.93 |
| `66b0be3c50f2` | sqlmap | `http://127.0.0.1:8100/low?id=1` | 0 | 11.38 |
| `6e2f1e4da0f5` | sqlmap | `http://127.0.0.1:8100/safe?id=1` | 0 | 5.67 |
| `896f7ca115f0` | sqlmap | `http://127.0.0.1:8100/low?id=1` (repeat) | 0 | 11.61 |

3. **WHAXON's scope gate was live during the runs**: before authorization the target was
   `Allowed: NO / no matching in-scope rule` (exit 1); after `scope --set` it was allowed, and
   `https://169.254.169.254/latest/meta-data/` remained denied throughout.
4. **The findings in the store are not hand-written**: `kind`, `severity`, `data` and the embedded
   sqlmap payloads (`id=1' AND 2679=2679 AND 'DNHo'='DNHo`, JSON_EXTRACT, RANDOMBLOB, UNION) are
   sqlmap's own output, carried through WHAXON's adapter (source field `= sqlmap`).

## 4. Preserved raw logs

All under `evidence/whaxon-run/`:

| File | Content |
| --- | --- |
| `recon-run1.log` | full `whaxon recon --verbose` output (31 findings printed) |
| `ffuf-run1.log` | `whaxon run ffuf --verbose` incl. `[run]` line and 14 printed findings |
| `sqlmap-low-run2.log`, `sqlmap-low-run3.log` | the two sqlmap detections on the injectable endpoint |
| `sqlmap-safe-run1.log` | the negative control (`[no findings]`) |
| `sqlmap-low-run1.log` | first attempt against the abandoned simulated lab (`[no findings]`) |
| `validate-ffuf.log`, `validate-sqli-run1.log` | `whaxon validate --verbose` for both finding types |
| `whaxon-report.md` | WHAXON's own engagement report (46 findings) |
| `job-66b0be3c50f2.json`, `job-86c7295507ae.json` | `whaxon jobs export` |
| `whaxon.db` | WHAXON's store (jobs + findings + verification status) |
| `authorized-scope.json`, `tools.json` | the sanitized scope and catalog used |
| `independent-verification.json`, `independent-verification.log` | §6 |

## 5. Findings generated by WHAXON itself

**Against the authorized live target (DVWA practice instance):**

- `whaxon recon` → 31 findings: 8 DNS records, TLS certificate facts, 6 missing security headers
  (CSP medium), 6 cookie-flag issues (`PHPSESSID` missing `Secure`/`HttpOnly`, `SameSite`), tech
  detection (`nginx/1.31.8`, `PHP/8.5.12`), missing `security.txt`, missing SPF and DMARC (medium),
  plus two correlator findings.
- `whaxon run ffuf` → 14 `found_path` findings (login/setup/phpinfo/vulnerabilities/config/.htaccess/
  php.ini/server-status/…), all graded `low`.

**Against the authorized local ground-truth lab:**

- `whaxon run sqlmap …/low?id=1` → **5 findings: 4 × `sqli` (critical) + 1 × `sqli_info` (medium)**.
  Ground truth: the endpoint is genuinely injectable (a UNION payload returns attacker-chosen rows).
- `whaxon run sqlmap …/safe?id=1` → **`[no findings]`**. Ground truth: the parameterized endpoint is
  not injectable. **No false positive on the control.**
- Repeat run of the injectable endpoint → the same 5 findings (`896f7ca115f0`).

## 6. Validation outcomes and independently verified results

### 6.1 What WHAXON's own validation layer said

| Finding | WHAXON verdict | Reason printed by WHAXON |
| --- | --- | --- |
| 4 × `sqli` (critical, lab) | `CANDIDATE` | `context replay did not produce a baseline-differential proof` |
| 1 × `sqli_info` | `CANDIDATE` | `kind 'sqli_info' is not directly replayable` |
| 14 × `found_path` (DVWA) | `CANDIDATE` | `kind 'found_path' is not directly replayable` |
| `retest 66b0be3c50f2 0` | refused | `Finding … is not verified (status=candidate). Retest requires a previously verified finding.` |
| engagement report | — | every entry rendered as `_Verification: candidate by engine — <reason>_` |

**Store-wide distribution: 55 findings, all `candidate`, zero `verified`.** WHAXON never claimed a
verification it had not obtained — the guardrail worked.

### 6.2 Independent verification (separate implementation, curl only)

`scripts/verify_whaxon_findings.py` re-plays WHAXON's **stored** evidence using `curl` and no
WHAXON imports (`evidence/whaxon-run/independent-verification.json`):

| Check | Result |
| --- | --- |
| **V1** sqlmap's recorded payload, replayed, behaves like a real injection | error-based payload reproduces a database error; boolean/time/union payloads behave as their technique requires |
| **V2** a false condition of the same payload behaves differently | differential confirmed — this is what makes boolean-blind SQLi detectable |
| **V3** the payload WHAXON's *validator* replays (`\`+HERP`) | produces a response **byte-identical** to WHAXON's own baseline on all 4 findings → no marker, no differential |
| **V4** a minimal breakout payload (`id=1'`) on the same parameter | produces a real SQLite error whose text contains WHAXON's own marker `sqlite` → the validator *would* have said `verified` had it chosen that payload |

So the injection is real, and WHAXON's inability to verify it is caused by **payload selection**:
`PayloadLoader.get_payloads('sqli')[0] == '`+HERP'` — a MongoDB snippet harvested from a
documentation code fence — and `validate()` always replays index 0.

## 7. Failures encountered and how they were resolved

| # | Failure | Cause | Resolution | Before/after evidence |
| --- | --- | --- | --- | --- |
| F1 | `whaxon install ffuf` → `Unknown tool: ffuf`, although `whaxon install --list` lists it | `whaxon init` writes `scope.json`/`whaxon.env` but **no `tools.json`**, so the catalog is empty and `install --list` falls back to a built-in list | registered ffuf in `data/tools.json` using the documented format (`docs/tools.md`), then re-ran `whaxon install --list` → `ffuf … installed` | before: `Unknown tool: ffuf`; after: `installed`, and `whaxon run ffuf` succeeded |
| F2 | ffuf binary missing (no root, no apt) | environment | downloaded the official ffuf **v2.3.0** release and verified its tarball SHA-256 against the project's official checksum file | `ffuf version: 2.3.0`, checksum `b2a3c725…75ceb` matches |
| F3 | `whaxon scope --check http://127.0.0.1:8099/…` denied while `127.0.0.1` allowed | **product defect D3** (upstream `5b61fa5`) | added an *exact-host* rule `127.0.0.1` (narrower than the existing `127.0.0.0/8` rule); scope enforcement stayed enabled and out-of-scope targets stayed denied | before/after in §7 of the decision log |
| F4 | first sqlmap run (`6f5b6e2a80f7`, 150 s) reported *not injectable* on a genuinely injectable endpoint | **my fixture was wrong**: the first lab only *printed* error strings for quotes; sqlmap's heuristics correctly rejected it | replaced the fixture with a real SQLite-backed lab (`experiments/lab/app.py`) whose ground truth is a real database query | before: `[no findings]`; after: 5 findings including 4 critical |
| F5 | lab server kept serving stale code after an edit | an old process still held port 8100 | PID-based restart; recorded | new behaviour confirmed |
| F6 | my verification script reported `V1=False` | **my script's bug**: the payload was double-encoded (`id=` prefix inside the value) and the `curl -w` time was concatenated onto the body, corrupting comparisons | fixed reconstruction and separated the timing line; results then matched direct curl observation | V3 now `True`, matching the byte-identical bodies seen directly |
| F7 | `pkill -f "experiments/lab/app.py"` terminated my own shell (exit 143) | pattern matched the shell's own command line | switched to PID-file control; **no** pattern-based process killing used afterwards | recorded as an operator error, not a tool defect |

**Nothing was bypassed**: scope enforcement was never disabled, no `--allow-out-of-scope` was used,
no executable was shimmed, and the only configuration change (an additional, narrower in-scope host
rule) is documented in the scope file's `notes` field.

## 8. WHAXON functionality vs external verification

| Statement | Belongs to |
| --- | --- |
| "the target exposes nginx/1.31.8 and PHP/8.5.12; 6 cookie-flag issues; missing CSP/HSTS/SPF/DMARC" | **WHAXON** (`whaxon recon`) |
| "these 14 paths respond and are graded low" | **WHAXON** (`whaxon run ffuf`) |
| "the lab endpoint is SQL-injectable; the parameterized one is not" | **WHAXON** (`whaxon run sqlmap`), consistent with ground truth |
| "WHAXON could not prove those findings, so they stayed `candidate`" | **WHAXON** (`whaxon validate`, `retest`, report) |
| "the ffuf finding for `.htaccess` claims status 200; the true status is 403" | **independent verification** (curl), see D1 |
| "WHAXON's replay payload is `\`+HERP` and cannot produce a marker; `1'` would" | **independent verification** (curl), see D2 |
| "the DVWA instance executes LFI/XSS/command injection unauthenticated" | **not WHAXON** — established earlier in this engagement by a purpose-built client; WHAXON's active scanners cannot reach those conditions, so they are *not* reported as WHAXON discoveries |
| "the upstream tool repo lacks the research tree's command-injection validator and scope fix" | **repository comparison**, not a scan result |

## 9. Defects measured in WHAXON during real execution

| ID | Severity | Defect | Evidence |
| --- | --- | --- | --- |
| **D1** | high (evidence integrity) | `FfufAdapter` writes `status: 200` when ffuf's output contains no status. Job `86c7295507ae` records `.htaccess`/`server-status`/`config` as `200` with `size: null`; the true status for `.htaccess`/`server-status` is `403`. This field drives the severity ladder (all 14 graded `low`) and `whaxon validate` cannot check it (`found_path` is not replayable). | `job-86c7295507ae.json`; independent curl |
| **D2** | medium (completeness) | The validation layer cannot verify a genuine, sqlmap-confirmed injection because it always replays `payloads[0]`, which for `sqli` is the documentation fragment `` `+HERP ``. | `validate-sqli-run1.log`, `independent-verification.json` V3/V4 |
| **D3** | medium (correctness) | URL-form targets never consult CIDR rules: `http://127.0.0.1:8099/…` is denied while `127.0.0.1` is allowed, and an explicit CIDR *deny* rule is not reached for URL targets (reason reports "no matching in-scope rule"). | `whaxon scope --check` matrix, recorded in `logs/decision-log.md` |
| **D4** | low (operations) | `whaxon init` does not create `tools.json`; `whaxon install --list` lists tools that `whaxon install <id>` then rejects as unknown. `recon` is also absent from the top-level usage line. | F1 above |
| **D5** | low (product identity) | Two different repositories publish the same version string `0.11.16` with different `validator.py`, `scope.py`, adapters and business-impact tables. | §1.1 diff table |
| **D6** | low (evidence accuracy) | The `whaxon recon` job is stored with `status='failed'` although the command exited 0 and persisted 31 findings. The report says "Jobs: 6" and does not surface the discrepancy. | `whaxon.db` `jobs` table |

**Working as designed (recorded as positive results):** scope gate denies before authorization and
still denies metadata/cloud endpoints; `validate` never over-claims (`verified` appears nowhere in
55 findings); `retest` refuses non-verified findings; the parameterized control produced no findings;
a repeat run reproduced the same findings; the report prints each finding's verification reason.

## 10. Reproduction instructions

```bash
# 1. instrument
git clone https://github.com/andreipath26/WHAXON.git work/WHAXON      # commit 5b61fa5
python3 -m venv .venv-whaxon && .venv-whaxon/bin/pip install -e "./work/WHAXON[dev,web]"

# 2. tools WHAXON will execute (real binaries, checksums recorded)
#    ffuf v2.3.0 -> ~/.local/bin/ffuf  (sha256 4b52c335…ea52f)
git clone https://github.com/sqlmapproject/sqlmap.git work/sqlmap     # c9745f8
chmod +x work/sqlmap/sqlmap.py

# 3. ground-truth lab (local, real SQLite, known-injectable + parameterized control)
python3 experiments/lab/app.py &            # http://127.0.0.1:8100

# 4. WHAXON assessment
whaxon init --data evidence/whaxon-run
whaxon scope --set evidence/whaxon-run/authorized-scope.json --data evidence/whaxon-run
whaxon recon "https://pentest-ground.com:4280/" --data evidence/whaxon-run
whaxon run ffuf "https://pentest-ground.com:4280" --data evidence/whaxon-run --extra "-t 2 -rate 5"
whaxon run sqlmap "http://127.0.0.1:8100/low?id=1"  --data evidence/whaxon-run
whaxon run sqlmap "http://127.0.0.1:8100/safe?id=1" --data evidence/whaxon-run
whaxon validate <job_id> <seq> --data evidence/whaxon-run --verbose
whaxon report --engagement default --format md --all-findings --data evidence/whaxon-run

# 5. independent verification (no whaxon imports)
python3 scripts/verify_whaxon_findings.py
```

Expected: recon findings; 14 ffuf findings; 5 findings on `/low` and none on `/safe`; every
`validate` result `candidate`; the report's verification lines all "candidate by engine".

*Note on authorization:* the live DVWA stage requires the same authorization basis recorded in
`docs/scope-and-rules.md`. The lab stage is fully local and requires none.
