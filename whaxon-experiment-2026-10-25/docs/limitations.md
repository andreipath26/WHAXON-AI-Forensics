# Limitations

Grouped by whether they bound the *target* conclusions, the *instrument* conclusions, or the
*publication* of this study. Nothing here is a hedge: each item names what would be needed to remove it.

## 1. Target-side limitations

| # | Limitation | Effect on conclusions | What would remove it |
| --- | --- | --- | --- |
| T1 | The DVWA instance has **no initialised database**. | SQL injection, brute force, stored XSS, CSRF, weak-session-ID and insecure-CAPTCHA could not be assessed. Claims about "the target's SQLi" are absent by necessity. | An instance owner pressing *Create / Reset Database* (prohibited here), or a self-hosted copy (blocked: no Docker daemon). |
| T2 | The instance is **shared and public**. | Destructive capabilities (`setup.php` reset, upload, brute force) were observed but not exercised; F5 is a presence-only finding. | A dedicated, disposable instance with written authorisation. |
| T3 | No **browser** is available. | XSS is established by HTML-context analysis, not by observing script execution in a DOM. | Playwright/Chromium in the runner. |
| T4 | The deployment behaves unlike upstream DVWA (modules execute unauthenticated). | The root cause is not diagnosed; only the behaviour is recorded. | Source access to the deployment, or a controlled instance for comparison. |
| T5 | One deployment, one point in time (2026-10-25). | Cross-deployment comparisons (e.g. the repository's 2026-10-17 run against `172.17.0.3`) differ in the login gate, which affects 2 of 12 adjudicated paths. | Repeated measurements across instances and dates. |

## 2. Instrument-side limitations

| # | Limitation | Effect | What would remove it |
| --- | --- | --- | --- |
| I1 | WHAXON's native scanners are absent and cannot be installed (no root). | The adapter and validator layers were exercised directly with recorded/benchmark input; the *orchestration* layer was exercised with a trivial local catalogue tool, not with Nmap/Nikto/Nuclei. | A runner with those binaries. |
| I2 | The benchmark is **authored by the same agent** that wrote the analysis. | Ground truth could in principle be shaped to flatter a conclusion. Mitigations: labels are asserted behaviourally in independent tests; matched negatives per positive; decoys were added specifically to try to break the tool; the two findings that make WHAXON look worst (`refuted` on a real vuln; `verified` on a decoy) are the ones a self-serving benchmark would omit. | Third-party replication of `scripts/validator_benchmark.py`. |
| I3 | Only 12 benchmark cases, one payload family per kind. | Metrics have wide uncertainty; Youden J is reported as a point estimate with no confidence interval, because n is too small for one to be meaningful. | Expand towards OWASP Benchmark scale (hundreds of cases). |
| I4 | The commit under test is a git snapshot (`research/forensics-2026-10-25` from upstream HEAD, whaxon 0.11.16). | Findings are version-specific; upstream may already have changed. | Re-run `scripts/*` against later commits; the characterisation tests will fail loudly if behaviour changes. |
| I5 | No source patch was proposed or merged. | The study measures; it does not prove a fix. H8 is explicitly a natural experiment comparing two existing code paths, not a controlled trial. | A patch + benchmark delta, reviewed upstream. |

## 3. Method limitations

| # | Limitation | Note |
| --- | --- | --- |
| M1 | Both verifiers (Python client, curl) share the OS resolver and TLS stack. | Common-mode failure possible; TLS chain checked separately with `openssl s_client`. |
| M2 | Timing measurements on a remote target over the public internet. | Only used for the *slow-baseline* argument, and the argument is made on a local server where jitter is controlled. |
| M3 | Severity scores are analyst-assigned, not tool-derived. | Each is labelled as an estimate with its vector; CVSS v3.1 has known subjectivity for confidentiality-only disclosures. |
| M4 | Request accounting is by construction, from the code, cross-checked against `request-log.jsonl`. | If a request failed before being logged it would be missing; the client logs after the attempt, including failures. |

## 4. Publication limitation (blocking)

**The study could not be published to GitHub from this runner.**

- `gh auth status` → "You are not logged into any GitHub hosts."
- No `~/.ssh`, no `~/.gitconfig`, no `~/.git-credentials`, no `credential.helper`, and **0**
  `GITHUB_TOKEN`/`GH_TOKEN` environment variables.
- Public **read** works (the repository was cloned over HTTPS), so the account/repo exist; only
  credentials for **write** are missing.

Consequences and what was done instead:

1. Every checkpoint was committed locally on branch `research/forensics-2026-10-25`.
2. A push was attempted and the exact server response recorded in `logs/publication-log.md`.
3. A `git bundle` and the branch tip hash are produced so an authorised person can transfer the
   work with `git fetch <bundle> research/forensics-2026-10-25`.
4. Enablement instructions are in `logs/publication-log.md` §4.

## 5. What these limitations do **not** license

They do not license weakening the findings that *were* established under controlled conditions.
The instrument measurements (E8–E11) are loopback-local, deterministic and repeatable; the target
findings (F1–F8) were each reproduced by a second client with matched controls. The limitations
above explain what is *outside* the study, not what is doubtful inside it.
