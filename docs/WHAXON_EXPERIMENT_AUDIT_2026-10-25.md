# WHAXON experiment audit — 2026-10-25

**Purpose:** translate the read-only `whaxon-experiment-2026-10-25/` evidence into current WHAXON engineering and release actions.

**Repository boundary:** this audit does not edit, rename, delete, or regenerate any file under `whaxon-experiment-2026-10-25/`. The experiment folder is treated as immutable evidence.

**Review scope:** inventoried all 102 paths in the experiment folder and reviewed the textual research documents, scripts, test file, JSON results, logs, and captured response artefacts. The two SQLite databases (`experiments/lab/lab.db` and `evidence/whaxon-run/whaxon.db`) were identified by metadata but could not be queried through the available GitHub text-file reader, which rejects binary SQLite content. The large JSONL access logs were parsed as complete text and summarised.

## Executive assessment

The experiment is valuable because it supplies counterexamples, not just a successful demo. It shows that an older WHAXON snapshot could (1) contact a denied destination through a redirecting external tool, (2) record unobserved HTTP status values, (3) lose contradictory scanner evidence during aggregation, and (4) misclassify both positive and negative validation results. It also documents important limitations of the live target and research method.

Some of those defects are already corrected in the current `main` code, which is newer than the snapshot used for the experiment. The fixes must be assessed against current code, not inferred from the old benchmark. Current CI has passed on Python 3.11, 3.12 and 3.13, including lint/type checks, tests and the clean-wheel smoke check, at commit `f323224bfe826f9fe42f7ed8a0cb616cbc921ebd`. Passing CI is not, by itself, proof of safe network-boundary enforcement or sufficient vulnerability-verification accuracy.

## 1. High-priority engineering findings

### E-A1 — Scope checks still do not contain every network request

**Experiment evidence:** `evidence/scope/redirect-escape.json` records an in-scope loopback server redirecting a tool to `127.0.0.2`, explicitly denied by scope. The denied server's own log records the request. The direct request is blocked, while the redirecting tool's follow-up escapes. The experiment also distinguishes this from the validator, whose replay code blocks redirects.

**Current status:** `src/whaxon/core/scope.py` now resolves hostnames when IP/CIDR rules apply and checks resolved addresses during preflight. `ToolRunner.run_tool` checks scope, and the web job path now calls the guarded core runner. The scope code itself correctly documents that DNS preflight is not network-level egress enforcement. External scanners may still follow redirects, make secondary requests, or resolve DNS again after preflight.

**Release action:** treat scope as an application-level preflight guard, not a firewall. Before scans can be run against arbitrary or public networks, deploy with an independently enforced egress boundary (for example, a constrained scanner container/network or a scope-aware outbound proxy/firewall) and test redirects, DNS changes, IPv4/IPv6 and secondary requests from the actual supported tools. Until that exists, beta use should be limited to isolated labs or explicitly controlled network ranges. Do not claim that a hostname check alone guarantees all contacted destinations are in scope.

### E-A2 — Path-discovery evidence must preserve disagreements

**Experiment evidence:** `evidence/adapters/fidelity.json` records silent ffuf lines with no status being represented as HTTP 200 in the old snapshot. In the shipped prior engagement, ffuf and gobuster disagree on 9 of 12 paths. The old target aggregation kept the first observation and discarded the conflicting measurement.

**Current status:** `src/whaxon/adapters/ffuf.py` now preserves missing status as `None` and uses neutral informational severity when the status is unknown. This fixes the invented-status defect. The aggregation layer still needed a correction so the same path's conflicting observations did not collapse into the first row.

**Change made outside the protected folder:** `src/whaxon/core/store.py` now includes observed status/size in a `found_path` signature and preserves source provenance during target-level aggregation. `tests/test_store.py` adds a regression test proving that a status-less ffuf observation and a gobuster 403 observation both survive. CI passed after these changes.

**Release action:** keep source, raw line, status and response size attached to each observation. Do not promote a path to “confirmed exposed” merely because a directory-discovery tool found its name; a 200/403/301/302 and an unknown status mean different things.

### E-A3 — Validator confidence needs to stay conservative and measurable

**Experiment evidence:** `evidence/benchmark/results.json` and `confusion.json` document a 12-case authored benchmark. The older code labelled a timing-only decoy `verified`, accepted a generic database word on a decoy, and labelled a genuine UNION-based SQLi `refuted` when its chosen payload failed. The payload loader also extracted the first line from arbitrary Markdown code fences, so examples could be mistaken for executable probes. LFI and some request shapes were outside the replay coverage.

**Current status:** current `src/whaxon/core/validator.py` no longer treats timing alone as proof, no longer uses bare DBMS names as SQL error markers, uses curated probes rather than the first documentation code fence, and returns `candidate` when replay cannot establish proof rather than inferring `refuted`. Command-injection checks use per-run canaries. The context replay restricts methods and blocks redirects.

**Remaining limitation:** a repeatable SQL error after a quote probe is stronger evidence than a generic word, but it is not a comprehensive exploitability proof. A finding that cannot be safely replayed must remain “candidate / not automatically tested”; this is a coverage limit, not evidence that the finding is false. Current behavior needs a maintained labelled benchmark that is run against the current implementation, with per-kind precision/recall and regression cases.

**Release action:** never describe `verified` as universal proof. Keep “candidate”, “verified”, and “inconclusive/not supported by this replay” distinct. Do not mark a finding refuted solely because one payload failed. Keep unsafe or state-changing POST replay disabled by default unless a kind-specific safe protocol is designed and tested.

### E-A4 — The experiment access log is not a pure validator trace

The complete `evidence/benchmark/access-log.jsonl` contains 3,473 valid JSON records. Of these, 3,358 requests target `sqli_low`; the remainder are spread across the benchmark endpoints. The file records method, path, status, query and body, but no caller/tool identity or experiment/run identifier. Its tail contains SQLmap-style `ORDER BY` probes, so the file combines benchmark traffic with other local test activity and cannot safely be interpreted as 3,473 validator requests.

This is loopback evidence, not evidence of 3,473 requests to the public target. Nevertheless, it weakens attribution: the log proves what hit the benchmark server, but not which WHAXON component made each request.

**Release action:** add run IDs and caller identity to test-harness logs in future experiments, and separate validator, scanner, and manual traffic into distinct logs. Keep the existing evidence unchanged.

## 2. Deployment and security hygiene findings from the folder

### E-A5 — The evidence package contains a plaintext lab credential

`evidence/whaxon-run/whaxon.env` includes `WHAXON_MSF_USER=msf` and `WHAXON_MSF_PASS=test123`. The surrounding comments say these lab variables are not read by WHAXON, and the configuration disables the related auto-chain. This appears to be a lab/default credential rather than proof of a production secret, but it is still a plaintext credential in a public repository and conflicts with a strict “credentials are never stored” publication policy.

**Constraint respected:** this file has not been modified because the experiment directory is explicitly protected. For a later, separately authorised evidence-publication cleanup, replace lab credentials with inert placeholders or move them to an untracked local environment file; do not reuse this value outside the disposable lab.

### E-A6 — Raw target responses are more sensitive than the “public-safe” label suggests

The folder contains raw responses including `/etc/passwd` output, command-injection output, phpinfo details, application paths and configuration metadata. The redaction manifest specifically documents session-ID redaction in four artefacts; that is not the same as a full secret/PII review of every raw response. No obvious live PHP session ID was detected in the textual artefacts inspected, but the raw phpinfo and passwd bodies remain detailed operational disclosures about a third-party hosted practice instance.

**Constraint respected:** none of the evidence was edited. Before future publication of live-target captures, run a broader secret/PII review and confirm the target owner's disclosure expectations. Prefer minimal excerpts for public reports and retain raw captures in a controlled evidence store when appropriate.

### E-A7 — The target authorisation record is not equivalent to written permission

The experiment's `docs/scope-and-rules.md` explicitly says there were no written rules of engagement from the host and that `robots.txt` said `Disallow: /`. The study used a self-imposed non-destructive ceiling, but its request accounting reports 65 requests against the shared public target, above its planned 40-request budget. The report is transparent about this; the risk remains a process lesson.

**Release action:** WHAXON's release process should require the operator to define and confirm the authorised scope before active scans. Do not rerun the public-target scripts from this evidence folder as part of CI or routine validation. Use loopback fixtures or an explicitly controlled lab for regression testing.

### E-A8 — A broad scope file can intentionally grant an enormous target range

`evidence/whaxon-run/scope-bug-demo.json` contains `0.0.0.0/0` as an in-scope range, with only the metadata range excluded. This is a deliberate reproduction artefact, not the default scope. It demonstrates that a syntactically valid but dangerously broad rule can make the operator's scope effectively global.

**Release action:** surface a prominent warning or require explicit confirmation when an operator configures `0.0.0.0/0` or `::/0`. Do not silently reinterpret a user-supplied broad rule, but make its reach unmistakable and audit the acknowledgement.

## 3. Evidence quality and reproducibility limits

- The benchmark has only 12 labelled cases and one payload family per kind; its metrics are useful counterexamples, not a reliable estimate of real-world scanner accuracy.
- The benchmark is authored by the same agent that wrote the analysis. The behavioural tests and negative controls improve credibility, but third-party replication is still needed.
- The public target's database was uninitialised, so SQLi and other stateful DVWA modules were not fully assessed. The live XSS evidence is based on executable HTML context, not an actual browser DOM execution.
- Native scanner binaries were absent in the research runner. The live findings were independently rechecked with curl, but this does not prove every native WHAXON tool's end-to-end behavior.
- The two SQLite files in the evidence directory were identified but their internal tables were not inspected in this pass because the available GitHub file reader does not support binary SQLite content.
- The study's reported baseline suite was `779 passed, 1 failed, 63 errors, 14 skipped` due to missing local system/browser dependencies. The current repository CI now installs its required dependencies and passes on Python 3.11/3.12/3.13; these are different environments and should not be conflated.

## 4. Current release decision

**The codebase is improving, but this audit does not certify WHAXON as ready for unrestricted production use.** The latest CI is green and the known ffuf evidence-loss issue is corrected, with regression coverage for conflicting path observations. The remaining release gate is the scope boundary for external tools and their redirects/sub-requests, plus a current labelled validator benchmark and a clearly limited beta deployment model.

Recommended v1.0 beta acceptance gates:

1. Keep active scans constrained to a controlled lab until network egress restrictions are tested.
2. Run a current validator benchmark with the false-positive and false-negative counterexamples from this folder represented as regression tests outside the immutable experiment directory.
3. Preserve provenance and conflicting observations in reports.
4. Keep package build/install smoke tests and the Python 3.11–3.13 CI matrix green.
5. Make the limitations explicit in the release notes; do not claim full destination enforcement or universal vulnerability verification.
6. Do not modify or rerun anything inside `whaxon-experiment-2026-10-25/` without separate permission.

---
*Generated from a read-only audit of the 2026-10-25 experiment evidence and current repository code. The protected experiment folder was not changed.*
