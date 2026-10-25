# Environment Report

**Engagement:** WHAXON AI Forensics — autonomous research, security testing, decision trace
**Record type:** contemporaneous observation (captured 2026-10-25T11:38Z–11:44Z)
**Runner workspace:** `/workspace/chats/631d3594b40a92b083bca535`

All values below were produced by commands executed in the runner and are reproducible with
`scripts/env_probe.sh`. Values are observations, not assumptions.

## 1. Host and platform

| Property | Observed value | How observed |
| --- | --- | --- |
| Kernel | `Linux 6.1.102 #1 SMP PREEMPT_DYNAMIC x86_64` | `uname -a` |
| Hostname / FQDN | `freestyle-vm` / `freestyle-vm` (not a public FQDN) | `hostname`, `hostname -f` |
| Distribution | Ubuntu 24.04.5 LTS (Noble) | `/etc/os-release` |
| Virtualisation | Cloud VM (Freebuff "Cloud mode" worktree) | workspace context + `/proc` capabilities |
| Timezone / clock | UTC (`date -u` = 2026-10-25T11:43:51Z) | `date -u` |

## 2. Identity and effective permissions

- `uid=104028665(fb631d3594b40a92b083bca535) gid=1001(freebuff) groups=1001(freebuff)` — **non-root**.
- `CapPrm: 0000000000000000`, `CapEff: 0000000000000000` — **no effective Linux capabilities** for the agent user.
- `sudo -n true` → `The "no new privileges" flag is set, which prevents sudo from running as root.`
  → privilege escalation on the *runner* is not available and was not attempted.
- Docker CLI 29.1.3 present but `docker info` → `permission denied while trying to connect to the docker API at unix:///var/run/docker.sock`.
  → **no container runtime control**; a local DVWA container cannot be started. This removes one
  planned control environment (see `logs/errors-and-blockers.md`, B-001).
- Bindable loopback addresses verified: `127.0.0.1` and `127.0.0.2` (Python `socket.bind`).
  This makes a self-contained two-host scope-boundary experiment possible without external traffic.

## 3. Resource limits

| Resource | Observed |
| --- | --- |
| CPU | 2 vCPU (`nproc`) |
| Memory | 3.8 GiB total, ~3.0 GiB free, no swap |
| Disk | 16 GiB total on `/`, 9.8 GiB available |
| Open files | `ulimit -n` = 1024 (soft) |
| Core dumps | disabled (`ulimit -c` = 0) |
| cgroup v2 files (`memory.max`, `cpu.max`) | not readable from inside the container |

Practical consequences: single-worker scanning only; no parallel port scanning at scale; evidence
files must be text/JSON rather than large binaries.

## 4. Network

| Probe | Result |
| --- | --- |
| DNS resolution | `github.com` → `172.182.252.133`, `dig` present |
| HTTPS egress | `https://github.com` → 200, `https://example.com` → 200 |
| Package egress | `pip download requests` succeeded (PyPI reachable) |
| Assessment target | `https://pentest-ground.com:4280/` → **200**, 5930 bytes, 1.09 s |
| Target TLS | Certificate `CN=pentest-ground.com`, issuer `Let's Encrypt YE2`, valid 2026-09-22 → 2026-12-21 |

Target response headers on first contact (raw, see `evidence/`):

```
HTTP/1.1 200 OK
Server: nginx/1.31.8
Date: Sun, 25 Oct 2026 11:39:44 GMT
Content-Type: text/html;charset=utf-8
Content-Length: 5930
X-Powered-By: PHP/8.5.12
Set-Cookie: security=low; path=/
Set-Cookie: PHPSESSID=2ed3f769...; expires=Mon, 26 Oct 2026 11:39:44 GMT; Max-Age=86400; path=/
Expires: Tue, 23 Jun 2009 12:00:00 GMT
Cache-Control: no-cache, must-revalidate
Pragma: no-cache
Vary: Accept-Encoding
```

Observations that matter for the research plan:

1. The application identifies itself as **Damn Vulnerable Web Application (DVWA)** and exposes the
   full DVWA vulnerability menu (`brute`, `exec`, `csrf`, `fi`, `upload`, `captcha`, `sqli`,
   `sqli_blind`, `weak_id`, `xss_r`, `xss_s`, ...).
2. The server sets `security=low` by default — the **easiest** DVWA security level is the default
   presented to any unauthenticated client.
3. `Expires: Tue, 23 Jun 2009` is DVWA's own anti-cache header (application fingerprint, not a
   server misconfiguration).
4. The response advertises `nginx/1.31.8` while the application is PHP — a reverse proxy in front
   of PHP-FPM. Version strings are self-reported and are treated as untrusted data.
5. `robots.txt` returns `User-agent: * / Disallow: /` over HTTPS. Semantics and the resulting
   authorization decision are analysed in `docs/scope-and-rules.md` §3.

## 5. Installed languages and package managers

| Tool | Version / path | Notes |
| --- | --- | --- |
| Python | 3.12.3 (`/usr/local/bin/python3`) | venv creation works |
| pip | 26.2.1 | PyPI reachable |
| Node.js | v24.21.0 (`/usr/local/bin/node`) | not required by this study |
| npm | 11.19.0 | not required |
| Bun | present | not required |
| Go / Rust / gcc | not checked in detail; no security toolchain preinstalled | see below |
| git | 2.43.0 | see §7 |
| jq | present | used for evidence post-processing |
| openssl | 3.0.13 | TLS inspection |

## 6. Security tooling

**None of the following were preinstalled:** `nmap`, `nikto`, `nuclei`, `sqlmap`, `whatweb`,
`gobuster`, `ffuf`, `wpscan`, `hydra`, `whois`, browser/Chromium.

Available: `curl`, `dig`, `openssl`, `jq`, `python3`, `docker` (client only), `git`.

Consequences:

- WHAXON's *tool-orchestration* layer cannot be exercised end-to-end against the target with its
  native third-party scanners in this runner (documented blocker B-002). Its **adapters,
  validator, scope engine and reporting** are exercised directly, which is where the research
  questions live.
- The live assessment is implemented with **purpose-written Python HTTP tooling** (stdlib
  `urllib`/`http.client` + `requests`), so every request, header and payload is auditable in this
  repository rather than hidden inside a third-party binary. This is a deliberate methodological
  choice: it maximises reproducibility and minimises uncontrolled target interaction.
- Optional installations (`nmap`/`ffuf`) via `apt` are **not** possible without root (B-001b);
  single-binary Go releases could be fetched from GitHub releases but were judged unnecessary and
  were not installed, since no finding in this study depends on them.

Browser automation: no Chromium/Playwright browser binary. `pytest-playwright` is installed as a
WHAXON dev dependency but no browser is bundled, so **XSS evaluation is done by response analysis,
not by DOM execution**. This is a stated limitation of the XSS conclusions
(`docs/limitations.md` §XSS).

## 7. Git and GitHub access

- Workspace is a git **worktree** of a shared bare repository: `.git` → `gitdir: /workspace/repo.git/worktrees/631d3594b40a92b083bca535`.
- Base branch: `freebuff/631d3594b40a92b083bca535`, HEAD commit `898264e Import cloud project files`,
  parent `29c50db Initial cloud project`. Working tree was **empty apart from `.git`** before this engagement.
- The shared bare repo also contains `refs/heads/main` and `refs/heads/freebuff/635f18543bdb9513fe80d634`
  at the same commit `cc82ec5`; those belong to other chats and were **not** modified.
- Upstream repository cloned successfully over HTTPS (public read): `https://github.com/andreipath26/WHAXON-AI-Forensics.git`,
  git 2.43.0, depth 50, into `/tmp/whaxon-clone`. Working tree copied into this workspace, `origin` set to the same URL.
- Git identity: no `user.email` was configured initially; this engagement set **repository-local**
  `user.name` / `user.email` only (no global configuration touched).
- GitHub authentication: `gh auth status` → **"You are not logged into any GitHub hosts."**
  No `~/.ssh` directory, no `~/.gitconfig`, no `~/.git-credentials`, `credential.helper` unset,
  and no `GITHUB_TOKEN`/`GH_TOKEN` in the environment.

  → **Authenticated write access to the upstream repository is not available in this runner.**
  Publication is therefore attempted and its failure recorded verbatim in
  `logs/publication-log.md`; the full research tree is preserved locally and in the local
  bare-repo commit history so an authorized person can push it.

## 8. Execution, networking and installation restrictions

- No root, no capabilities, `no_new_privileges` set: system package installation is impossible.
- No Docker daemon: no local vulnerable-app container.
- Outbound HTTPS and DNS work; the assessment target is reachable directly (no proxy variables set).
- Shell commands are limited to 5 minutes synchronous execution; long work is chunked and each
  chunk is logged.
- Filesystem is persistent within this chat worktree and is checkpointed by the host. The
  `/workspace` bare repo is shared with other chats: only the current worktree's own branch is used.

## 9. Reproduction

```bash
bash scripts/env_probe.sh          # regenerates every observation in this report
. .venv/bin/activate && pytest -q  # WHAXON baseline test suite (see docs/verification-results.md)
```

The environment probe writes machine-readable output to `evidence/env/environment.json`.

## 10. What this environment can and cannot establish

Can establish: properties of the target's HTTP surface, application logic, and injected-code
execution, observed through audited requests; properties of WHAXON's code paths, measured directly.

Cannot establish: kernel/container-level exploitation, browser-side script execution, effects that
require a Docker control plane, or GitHub publication, all of which are unavailable here and are
reported as blockers rather than assumed.
