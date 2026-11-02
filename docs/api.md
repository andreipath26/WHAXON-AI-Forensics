# HTTP API

This document is a **selected route guide**, not a generated exhaustive OpenAPI specification. The route implementation in `src/whaxon/interfaces/web/server.py` is authoritative; check it before relying on an endpoint not listed here.

## Base URL and authentication

Default local address: `http://127.0.0.1:5001`.

The request gate first applies Host and browser cross-origin/Fetch Metadata protections. Requests whose peer is loopback (`127.0.0.1` or `::1`) then use the local-peer authentication shortcut. Non-loopback requests require HTTP Basic authentication using `WHAXON_AUTH_USER` and either `WHAXON_AUTH_PASS` or `WHAXON_AUTH_PASS_HASH`; repeated failures are rate-limited.

The local default identity is `whaxon` / `whaxon`. It is for loopback development only. Remote listeners require explicit non-default credentials; configure them before exposing the service. Do not interpret the loopback shortcut as safe for arbitrary Host headers or cross-origin browser requests.

`/favicon.ico` returns 204. Health endpoints pass through the same request gate: they are available without Basic credentials from loopback, but remote requests still require authentication.

## Health and status

- `GET /api/health` — readiness details; returns 200 when required checks pass and 503 when degraded.
- `GET /api/health/simple` — simple health/tool-count response.
- `GET /api/status` — runtime counters and Metasploit status.

## Tool execution and jobs

- `GET /api/tools` — catalog and availability information.
- `POST /api/run` — submit a tool job; JSON body includes `tool_id`, `target` and `extra_args`.
- `GET /api/jobs/<job_id>` — job details and persisted output lines.
- `GET /api/jobs/<job_id>/stream` — server-sent event stream for job lifecycle/output/findings.
- `POST /api/jobs/<job_id>/cancel` — request cancellation.
- `GET /api/jobs/<job_id>/findings` — findings for a job.
- `GET /api/jobs/<job_id>/report` — per-job report.
- `GET /api/jobs/<job_id>/evidence` — list evidence.
- `POST /api/jobs/<job_id>/evidence` — attach a note or upload.
- `DELETE /api/jobs/<job_id>/evidence/<seq>` — remove an evidence item.
- `GET /api/jobs/<job_id>/evidence/<seq>/download` — download evidence content.

## History, reports and scope

- `GET /api/history` — recent jobs.
- `GET /api/jobs/active` — active jobs.
- `GET /api/jobs/<job_id>/output.txt` — plain-text job output.
- `GET /api/jobs/<job_id>/findings.csv` and `GET /api/jobs/<job_id>/findings.json` — findings exports.
- `GET /api/coverage/<job_id>` — recorded coverage for a job.
- `GET /api/report?format=md` — engagement report.
- `GET /api/loot` — loot-kind findings.
- `GET /api/tree` — session/chain tree data.
- `GET /api/scope` — active scope configuration.
- `POST /api/scope/check` — check a target; body includes `target`.
- `POST /api/scope` — update scope configuration (subject to server-side validation).
- `POST /api/scope/override` — request a logged, one-time scope override; availability and authorization are controlled by the server.

A scope check is an application-level preflight decision, not proof that every subsequent network connection remains inside scope. See [Scope](scope.md).

## Dependency readiness

The current server also exposes dependency inventory, verification, audit/history, drift, snapshots, planning, installation and operation lifecycle routes, including:

- `GET /api/dependencies`
- `POST /api/dependencies/verify`
- `GET /api/dependencies/audit`
- `GET /api/dependencies/history`
- `GET /api/dependencies/drift`
- `POST /api/dependencies/snapshots`
- `POST /api/dependencies/plan`
- `POST /api/dependencies/install`
- `POST /api/dependencies/install-batch`
- `GET /api/dependencies/install/<operation_id>`
- `POST /api/dependencies/install/<operation_id>/cancel`

These routes do not turn the installer into a general package manager. Exact-plan approval, allowlists, host restrictions and recovery limitations apply. See [Dependency readiness](dependency-readiness.md).


## AI, validation and approvals

- `POST /api/ai/run` — submit an AI planning request.
- `GET /api/ai/runs` and `GET /api/ai/runs/<run_id>` — list and inspect runs.
- `GET /api/ai/pending` — pending human questions.
- `POST /api/ai/runs/<run_id>/answer` — answer a pending question.
- `GET /api/ai/runs/<run_id>/stream` — stream run events.
- `POST /api/validate/<job_id>/<seq>` — request deterministic validation.
- `POST /api/retest/<job_id>/<seq>` — request a retest.
- `POST /api/approvals/<job_id>/<seq>/resolve` — resolve a pending approval.

AI proposals are not authorization or execution evidence. Validation and retest outcomes may be inconclusive; do not interpret a missing observation as proof of safety.

## Metasploit and pivot

- `GET /api/msf/status`, `GET /api/msf/sessions`, `POST /api/msf/run`.
- `GET /api/msf/sessions/<session_id>` and `POST /api/msf/sessions/<session_id>/exec`.
- `GET /api/msf/modules/<module_type>`.
- `GET`, `POST` and `DELETE` `/api/msf/sessions/<session_id>/portfwd`.
- `GET /api/pivot/graph`, `GET /api/pivot/sessions/<session_id>/chain`, `GET /api/pivot/candidates`.

Their availability depends on the optional Metasploit integration and its configuration. Consult the route definitions and [Deployment](deployment.md) before enabling them.

## Import and settings

- `POST /api/import/burp` — import Burp XML.
- `POST /api/bounty/import` — import bug-bounty program policy data.
- `GET /api/settings` and `POST /api/settings` — legacy settings API.
- `GET /api/ui-v2/findings` — UI-specific findings data.
- `GET /api/loot` — loot-kind findings.
- `GET /api/report` — engagement report in the requested supported format.

## Browser routes

- `GET /` — redirects to `/ui-v2`.
- `GET /ui-v2` — canonical Obsidian Kinetic dashboard.
- `GET /ui-v2/<page>` — implemented page routes; see [New UI interaction and acceptance audit](NEW_UI_INTERACTION_AUDIT.md).
- `GET /ui` — retained legacy/reference interface.
- `GET /settings` — legacy settings route.

## Example requests

Local health check:

```bash
curl http://127.0.0.1:5001/api/health
```

List tools:

```bash
curl -u whaxon:whaxon http://127.0.0.1:5001/api/tools | python3 -m json.tool
```

Submit a job against an explicitly authorized, in-scope lab target:

```bash
RESP=$(curl -s -u whaxon:whaxon \
  -H "Content-Type: application/json" \
  -X POST http://127.0.0.1:5001/api/run \
  -d '{"tool_id":"nmap","target":"10.10.10.20","extra_args":""}')
JID=$(echo "$RESP" | python3 -c 'import sys,json; print(json.load(sys.stdin)["job_id"])')
curl -u whaxon:whaxon "http://127.0.0.1:5001/api/jobs/$JID/findings"
```

Use the default credentials only for a local loopback instance. Never copy these examples unchanged into a remote deployment.
