#!/usr/bin/env bash
# Phase A environment probe.
#
# Purpose: regenerate every observation in docs/environment-report.md as
# machine-readable evidence. Read-only: it inspects the runner and performs
# a few benign HTTPS GETs (github.com, example.com, the assessment target)
# with short timeouts. It installs nothing and writes only inside this repo.
#
# Usage: bash scripts/env_probe.sh
# Output: evidence/env/environment.json, evidence/env/probe.log,
#         evidence/env/target_root.headers, evidence/env/target_root.html
set -uo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
OUT="$ROOT/evidence/env"
mkdir -p "$OUT"
LOG="$OUT/probe.log"
JSON="$OUT/environment.json"
: > "$LOG"

TARGET="${WHAXON_TARGET:-https://pentest-ground.com:4280/}"
TS="$(date -u +%FT%TZ)"
echo "== env probe $TS ==" | tee -a "$LOG"

tools_json() {
  local first=1
  for t in "$@"; do
    local p; p="$(command -v "$t" 2>/dev/null || true)"
    [ $first -eq 1 ] || printf ','
    first=0
    if [ -n "$p" ]; then printf '"%s":"%s"' "$t" "$p"; else printf '"%s":null' "$t"; fi
  done
}

export P_TS="$TS"
export P_UNAME="$(uname -a)"
export P_OS="$(grep PRETTY_NAME /etc/os-release | cut -d= -f2 | tr -d '"')"
export P_ID="$(id 2>&1)"
export P_CAPS="$(grep -E '^Cap' /proc/self/status 2>/dev/null | tr '\n' ' ')"
export P_SUDO="$(sudo -n true 2>&1 | head -2 | tr '\n' ' ')"
export P_DOCKER="$( { timeout 10 docker info 2>&1 | grep -iE 'cannot|error|permission' | head -2 | tr '\n' ' '; } || true )"
export P_NPROC="$(nproc 2>/dev/null || echo unknown)"
export P_MEMTOTAL="$(awk '/MemTotal/{print $2" kB"}' /proc/meminfo 2>/dev/null)"
export P_MEMAVAIL="$(awk '/MemAvailable/{print $2" kB"}' /proc/meminfo 2>/dev/null)"
export P_DISK="$(df -h "$ROOT" 2>/dev/null | tail -1 | tr -s ' ' ' ')"
export P_NOFILE="$(ulimit -n 2>/dev/null || echo unknown)"
export P_TOOLS="$(tools_json nmap nikto nuclei sqlmap whatweb gobuster ffuf wpscan hydra curl dig openssl jq git python3 pip3 node npm bun docker gh zip unzip whois nc chromium chromium-browser google-chrome)"
export P_PY="$(python3 --version 2>&1)"
export P_PIP="$(pip3 --version 2>&1)"
export P_GITV="$(git --version 2>&1)"
export P_CURL="$(curl --version 2>&1 | head -1)"
export P_JQ="$(jq --version 2>&1)"
export P_SSL="$(openssl version 2>&1)"
export P_NODE="$(node --version 2>&1)"
export P_NPM="$(npm --version 2>&1)"
export P_DNS="$(getent hosts github.com 2>/dev/null | head -1 || true)"
export P_GH="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 https://github.com/ 2>/dev/null || echo error)"
export P_EX="$(curl -s -o /dev/null -w '%{http_code}' --max-time 15 https://example.com/ 2>/dev/null || echo error)"
export P_TARGET="$TARGET"
export P_TMETA="$(curl -sk -D "$OUT/target_root.headers" -o "$OUT/target_root.html" -w 'code=%{http_code} size=%{size_download} time=%{time_total}' --max-time 25 "$TARGET" 2>/dev/null || echo 'code=error')"
export P_TLS="$(timeout 20 openssl s_client -connect pentest-ground.com:4280 -servername pentest-ground.com </dev/null 2>/dev/null | openssl x509 -noout -subject -issuer -dates 2>/dev/null | tr '\n' ' ' || true)"
export P_LOOP="$(python3 - <<'PY'
import json, socket
res = {}
for ip in ("127.0.0.1", "127.0.0.2", "127.0.0.3"):
    s = socket.socket()
    try:
        s.bind((ip, 0)); res[ip] = True
    except OSError:
        res[ip] = False
    finally:
        s.close()
print(json.dumps(res))
PY
)"
export P_BRANCH="$(git -C "$ROOT" rev-parse --abbrev-ref HEAD 2>/dev/null || echo none)"
export P_HEAD="$(git -C "$ROOT" rev-parse HEAD 2>/dev/null || echo none)"
export P_REMOTE="$(git -C "$ROOT" remote get-url origin 2>/dev/null || echo none)"
export P_GHAUTH="$(gh auth status 2>&1 | head -3 | tr '\n' ' ' || true)"
export P_TOKENS="$(env | grep -cE '^(GITHUB_TOKEN|GH_TOKEN|GITHUB_PAT|GIT_ASKPASS)=' || true)"
export P_SSH="$(ls -1 "$HOME/.ssh" 2>/dev/null | wc -l)"
export P_CREDHELPER="$(git config --global --get credential.helper 2>/dev/null || true)"

python3 - <<'PY' > "$JSON"
import json, os
e = os.environ
def g(k, d=""):
    return e.get(k, d)
data = {
  "probe_timestamp_utc": g("P_TS"),
  "record_type": "contemporaneous observation produced by scripts/env_probe.sh",
  "runner": {
    "uname": g("P_UNAME"), "os_release": g("P_OS"), "identity": g("P_ID"),
    "capabilities": g("P_CAPS"), "sudo_probe": g("P_SUDO"),
    "docker_probe": g("P_DOCKER"),
  },
  "resources": {"nproc": g("P_NPROC"), "mem_total": g("P_MEMTOTAL"),
                "mem_available": g("P_MEMAVAIL"), "disk": g("P_DISK"),
                "nofile": g("P_NOFILE")},
  "tool_paths": json.loads("{" + (g("P_TOOLS") or "") + "}"),
  "versions": {"python": g("P_PY"), "pip": g("P_PIP"), "git": g("P_GITV"),
               "curl": g("P_CURL"), "jq": g("P_JQ"), "openssl": g("P_SSL"),
               "node": g("P_NODE"), "npm": g("P_NPM")},
  "network": {
    "dns_github": g("P_DNS"), "https_github": g("P_GH"), "https_example": g("P_EX"),
    "target_url": g("P_TARGET"), "target_response": g("P_TMETA"),
    "target_tls": g("P_TLS"),
    "loopback_bindable": json.loads(g("P_LOOP") or "{}"),
  },
  "git": {"branch": g("P_BRANCH"), "head": g("P_HEAD"), "origin": g("P_REMOTE"),
          "gh_auth_status": g("P_GHAUTH"),
          "github_token_env_vars": int(g("P_TOKENS") or 0),
          "ssh_key_files": int(g("P_SSH") or 0),
          "global_credential_helper": g("P_CREDHELPER")},
}
print(json.dumps(data, indent=2))
PY

if jq -e . "$JSON" >/dev/null 2>&1; then
  echo "wrote $JSON (valid JSON)" | tee -a "$LOG"
  jq -c '{target: .network.target_response, gh: .git.gh_auth_status, tokens: .git.github_token_env_vars}' "$JSON" | tee -a "$LOG"
else
  echo "ERROR: $JSON is not valid JSON" | tee -a "$LOG"
fi
sha256sum "$JSON" >> "$LOG" 2>/dev/null || true
echo "== done ==" | tee -a "$LOG"
