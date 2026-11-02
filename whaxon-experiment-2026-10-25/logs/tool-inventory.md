# Tool Inventory

Contemporaneous record. Regenerate with `bash scripts/env_probe.sh` (writes
`evidence/env/environment.json`). Versions verified 2026-10-25T11:39Z–11:47Z.

## 1. Preinstalled and usable

| Tool | Version | Path | Used for |
| --- | --- | --- | --- |
| curl | 8.5.0 (OpenSSL 3.0.13, nghttp2 1.59) | `/usr/bin/curl` | target probing, header capture, proof replay |
| openssl | 3.0.13 | `/usr/bin/openssl` | TLS certificate inspection |
| dig | (bind9-dnsutils) | `/usr/bin/dig` | DNS resolution checks |
| jq | 1.6 | `/usr/bin/jq` | evidence post-processing, manifest generation |
| git | 2.43.0 | `/usr/bin/git` | version control, publication |
| gh | 2.45.0 | `/usr/bin/gh` | GitHub auth probe (unauthenticated) |
| python3 | 3.12.3 | `/usr/local/bin/python3` | harness, adapters, analysis |
| pip3 | 26.2.1 | `/usr/local/bin/pip3` | dependency installation |
| node / npm | v24.21.0 / 11.19.0 | `/usr/local/bin/` | present, unused |
| bun | present | `/usr/local/bin/bun` | present, unused |
| docker (client) | 29.1.3 | `/usr/bin/docker` | **no daemon access** (`permission denied` on `/var/run/docker.sock`) |
| nc, zip, unzip | present | `/usr/bin/` | present, not central |

## 2. Deliberately absent (checked, not installed)

`nmap`, `nikto`, `nuclei`, `sqlmap`, `whatweb`, `gobuster`, `ffuf`, `wpscan`,
`hydra`, `whois`, and any browser (`chromium`, `chromium-browser`, `google-chrome`).

Installation was **not attempted** for these:

- `apt` requires root; the runner has no capabilities and `no_new_privileges`
  is set (`logs/errors-and-blockers.md` B-001).
- Single-binary Go releases could be downloaded, but no research question in
  this study depends on a third-party scanner's own verdict. Where scanner
  behaviour matters (adapter fidelity), the study feeds **recorded scanner
  output** to WHAXON's adapters, which is more reproducible than re-running an
  external binary whose version changes.
- Consequence: WHAXON cannot be driven end-to-end with real scanners here
  (blocker B-002). Its scope engine, adapters, validator, correlator and store
  are exercised directly instead.

## 3. Python environment created for this engagement

```
python3 -m venv .venv
. .venv/bin/activate
pip install -e ".[dev]"          # WHAXON 0.11.16 from this working tree
```

Resolved versions relevant to the study (`pip list`):

| Package | Version |
| --- | --- |
| whaxon | 0.11.16 (editable, this repo) |
| pytest | 9.1.1 |
| pytest-asyncio | 1.4.0 |
| pytest-playwright | 0.10.0 (no browser binary → DOM-level tests skipped) |
| pytest-xdist | 3.8.0 |
| requests | 2.34.2 |
| requests-toolbelt | 1.0.0 |

`pip download` from PyPI succeeded, so dependency installation is permitted and
working. `.venv/` is git-ignored by the repo's existing `.gitignore` (verified
before committing; see `logs/publication-log.md`).

## 4. Purpose-written tooling (this engagement)

| Artefact | Purpose |
| --- | --- |
| `scripts/env_probe.sh` | reproducible Phase A environment capture |
| `scripts/whaxon_scope_probe.py` | offline scope-engine behaviour matrix (no target traffic) |
| `scripts/scope_escape_demo.py` | two-loopback-host demonstration that a tool/validator-independent HTTP client can be moved off-scope by a redirect |
| `scripts/dvwa_client.py` | audited DVWA session client (login, CSRF, security level, request logging) |
| `scripts/run_assessment.py` | executes the experiment set, writes raw evidence + JSON results |
| `scripts/verify_findings.py` | independent re-verification of each finding with negative controls |
| `scripts/adapter_fidelity.py` | feeds recorded tool output to WHAXON adapters, diffs claimed vs. actual |
| `scripts/build_manifest.py` | writes `evidence/manifest.json` with SHA-256 hashes |

## 5. Libraries intentionally avoided

- No third-party vulnerability scanner verdicts are used as evidence.
- No LLM call is made during assessment; all conclusions derive from recorded HTTP
  observations and code reading. (WHAXON's own optional AI layer is out of scope:
  no provider credentials exist in this runner, and enabling it would delegate
  judgement that this study is designed to test.)
