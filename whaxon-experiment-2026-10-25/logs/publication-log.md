# Publication Log

**Destination:** `https://github.com/andreipath26/WHAXON-AI-Forensics.git`
**Branch prepared:** `research/forensics-2026-10-25`
**Result:** **NOT PUBLISHED — write credentials are unavailable in this runner.** The remote was
verified not to contain the branch. Everything below is the evidence for that statement.

## 1. Pre-publication checks

| Check | Command | Result |
| --- | --- | --- |
| Baseline is upstream HEAD | `git -C /tmp/whaxon-clone rev-parse HEAD` vs `git ls-remote origin refs/heads/main` | both `a577fc7050b179aa8038e5423834143c3c084d0b` |
| Upstream source unmodified | `git diff --name-only dcb5982..HEAD -- src` | empty |
| Test suite after all additions | `python -m pytest -q` | 779 passed, 1 failed (`weasyprint` absent), 63 errors (no browser), 14 skipped — identical to baseline plus 23 new passing tests |
| Secret scan (value-shaped patterns) | `grep -rInE "PHPSESSID=[0-9a-zA-Z]{16,}\|ghp_[A-Za-z0-9]{20,}\|github_pat_[A-Za-z0-9_]{20,}\|-----BEGIN [A-Z ]*PRIVATE KEY-----"` | only a string constant inside `.venv/` (git-ignored) |
| Evidence sanitisation | `python scripts/redact_evidence.py && python scripts/build_manifest.py` | 4 files redacted (session-id values), manifest clean |
| Diff review | `git status --porcelain` before each commit | only intended paths staged; six commits, working tree clean before the bundle was generated |

## 2. Commit inventory (local branch)

| Commit | Message |
| --- | --- |
| `dcb5982` | Import WHAXON 0.11.16 tree as the research baseline (359 files) |
| `081f88b` | Record Phase A environment discovery |
| `8ad7a9a` | Add repository analysis, literature review and the test plan |
| `b603cf1` | Measure the instrument: adapters, replay verification and scope binding |
| `e5add6d` | Record the authorised live assessment and its independent verification |
| `70feb3e` | Add the decision trace, contribution statement and hashed evidence manifest |
| *(next)* | Record publication attempt and blocker |

Branch tip before the publication-log commit: `70feb3ec753c7ef6cfaaf2cf2b24fd5751e8155c`.

## 3. Push attempts

**Attempt 1** — 2026-10-25T12:21Z

```
$ GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/true git push -u origin research/forensics-2026-10-25
remote: No anonymous write access.
fatal: Authentication failed for 'https://github.com/andreipath26/WHAXON-AI-Forensics.git/'
exit code: 128
```

**Attempt 2** — 2026-10-25T12:32Z (without `-u`, to rule out a tracking-configuration issue)

```
$ GIT_TERMINAL_PROMPT=0 GIT_ASKPASS=/bin/true git push origin research/forensics-2026-10-25
remote: No anonymous write access.
fatal: Authentication failed for 'https://github.com/andreipath26/WHAXON-AI-Forensics.git/'
exit code: 128
```

Both failures are authentication, not network, permission-on-branch, or size. The server's own
message — `No anonymous write access` — states that the request arrived unauthenticated.

## 4. Remote verification (positive and negative)

Read access works, which proves the repository exists and is public:

```
$ git ls-remote --heads origin
869b794bad1c003b5676287da504f56c69471e55  refs/heads/dependabot/github_actions/actions/checkout-7.0.1
765bb26ab4cfeaa926314e00bba491f7fb73f673  refs/heads/dependabot/github_actions/actions/setup-python-7.1.0
a577fc7050b179aa8038e5423834143c3c084d0b  refs/heads/main
```

The branch is **not** on the remote:

```
$ git ls-remote origin 'refs/heads/research/*'
(no output)
MATCHES=0
```

Therefore no claim of successful publication is made anywhere in this study. `docs/limitations.md`
§4 states the same limitation.

## 5. Credential probe (why the failure was expected)

| Probe | Result |
| --- | --- |
| `gh auth status` | `You are not logged into any GitHub hosts.` |
| `ls ~/.ssh` | no such directory |
| `~/.gitconfig`, `~/.git-credentials` | absent |
| `git config --global credential.helper` | unset |
| `env \| grep -E '^(GITHUB_TOKEN\|GH_TOKEN\|GITHUB_PAT\|GIT_ASKPASS)='` | 0 matches |

## 6. What was preserved instead, and how to publish it

1. **Local branch** `research/forensics-2026-10-25` at tip `70feb3e` in this workspace (checkpointed
   by the host). This is the authoritative artefact.
2. **Bundle** `artifacts/whaxon-forensics-2026-10-25.bundle`
   SHA-256 `ccd5d995eff65b0ba8ad72351692a2ab976e8754337cae8e6bf9d41b7f839604` (4.4 MB).
   Deliberately not committed (binary, regenerable with
   `git bundle create artifacts/whaxon-forensics-2026-10-25.bundle research/forensics-2026-10-25`).
3. **Enablement instructions** for an authorised person:

```bash
# A. With a personal access token that has 'repo' scope (or fine-grained 'Contents: write'):
#    do NOT paste the token into chat or into a tracked file.
git clone https://github.com/andreipath26/WHAXON-AI-Forensics.git
cd WHAXON-AI-Forensics
git fetch /path/to/artifacts/whaxon-forensics-2026-10-25.bundle \
    research/forensics-2026-10-25:research/forensics-2026-10-25
git push origin research/forensics-2026-10-25
git ls-remote origin refs/heads/research/forensics-2026-10-25   # verify the tip hash

# B. Or re-authenticate this runner (no token in files): `gh auth login` in an interactive
#    terminal, then `git push -u origin research/forensics-2026-10-25`.
```

The work transfers without re-running any experiment: the branch contains the scripts, the raw
evidence, the hashes and the documentation.

## 7. Deliberate publication decisions

- **Redaction applied before publication.** Session identifiers were replaced with a placeholder in
  four artefacts; before/after SHA-256 values are in `evidence/redactions.json`. Nothing else in
  the evidence was altered.
- **No credentials were ever written** to the repository, the logs, this file or the chat.
- **Detailed live-target exploitation evidence is included** in `evidence/live/` — justified by the
  target being a public deliberately-vulnerable training application with no personal data, and by
  the absence of any credential in the captured material. If the repository owner prefers a
  sanitised variant, the bodies can be withheld while `evidence/live/confirm.json` (verdicts and
  excerpts) is retained; the analysis does not depend on the full bodies.
- **The bundle is untracked**, so `git status` will show `artifacts/` as untracked in the local
  workspace. That is intentional: binaries do not belong in the research branch.
