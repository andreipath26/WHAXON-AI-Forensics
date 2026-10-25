# New Default UI — Interaction and Acceptance Audit

**Implementation:** Obsidian Kinetic frontend  
**Route:** `/` and `/ui`  
**Legacy reference route:** `/ui/legacy`  
**Status:** Initial integration implemented; automated CI/browser verification pending. Do not treat this document as a claim that tests have passed.

## Product boundary

- The checked-in Obsidian Kinetic screen designs and `web ui files and rendering/obsidian_kinetic/DESIGN.md` are the design source.
- The previous UI templates and static assets remain unchanged and are accessible only through the legacy reference route.
- This audit is separate from `docs/WEB_UI_INTERACTION_AUDIT.md`, which remains a historical audit of the deprecated UI.
- Live controls must not imply unsupported capabilities. Backend authorization and scope checks remain authoritative.

## New UI route map

| View | Data/action | Backend endpoint | Initial implementation status |
|---|---|---|---|
| Overview | Health, job count, tool count, finding count, recent jobs | `/api/health`, `/api/history`, `/api/tools`, `/api/report?format=json` | Wired; verify in browser/CI |
| Scope & targets | Read scope summary and check a target | `GET /api/scope`, `POST /api/scope/check` | Wired; no scope override exposed |
| Run orchestration | List available tools, launch scoped job, stream output, request cancellation | `GET /api/tools`, `POST /api/run`, `GET /api/jobs/<id>/stream`, `POST /api/jobs/<id>/cancel` | Wired; end-to-end tests pending |
| Verified findings | Severity summary, search/filter, request deterministic validation | `GET /api/report?format=json`, `POST /api/validate/<job>/<seq>` | Wired; verify report field mapping |
| Remediation & retest | Show only currently verified findings; revalidate | `POST /api/retest/<job>/<seq>` | Wired; backend eligibility and scope checks remain authoritative |
| Trust layer | Review unverified findings; record explicit human verified/refuted decision | `POST /api/approvals/<job>/<seq>/resolve` | Wired; human decision is labelled separately from engine validation |
| Coverage & reports | Export Markdown, HTML, JSON, PDF, WHAXON envelope | `GET /api/report?format=...` | Wired; PDF depends on renderer availability |
| Job history | Read persisted jobs and inspect job output | `GET /api/history`, `GET /api/jobs/<id>/output.txt` | Wired; verify response schemas in CI |
| Sessions | Read Metasploit session status | `GET /api/msf/sessions` | Read-only; interactive session control intentionally omitted |
| Adapter catalog | Tool availability and adapter support | `GET /api/tools` | Wired |
| Diagnostics | Check health, catalog, scope, report endpoints | `/api/health`, `/api/health/simple`, `/api/tools`, `/api/scope`, `/api/report?format=json` | Wired; verify in browser/CI |

## Acceptance checklist

- [ ] CI passes for the candidate branch on all required Python versions.
- [ ] Root and `/ui` render the new UI; `/ui/legacy` renders the old interface.
- [ ] Browser tests pass for navigation, mobile navigation, live tool catalog, scope summary and scope checks.
- [ ] Run flow confirms scope before submission, backend rejects unauthorized targets, and output stream displays lines/final status.
- [ ] Cancellation requests are reflected accurately; UI does not claim cancellation succeeded when the backend returns false.
- [ ] Finding severity/status fields map correctly from actual report payloads; validate and retest refresh state after completion.
- [ ] Human review is clearly distinguished from deterministic engine verification.
- [ ] Report download formats and failure handling are tested.
- [ ] No demo target, fake telemetry, fabricated finding, default credential or unsupported hardware-enforcement claim is shown as live system state.
- [ ] Keyboard and small-screen interactions are checked.
- [ ] Visual comparison is performed against the checked-in screen renderings, and mismatches are corrected without changing the design direction.
- [ ] Existing legacy source assets remain unchanged; old UI tests use the legacy route.

## Known limits of this first integration

- This is the initial operational shell, not yet a claim that every one of the 32 design screens has been implemented as a distinct production workflow.
- The initial UI intentionally omits unsupported mockup features (for example, CVE lookup, client portal/team management, cryptographic audit-log viewer and plugin installation controls) until a safe, real backend workflow is available.
- Visual regression screenshots and browser execution results still need to be produced by CI or a local browser run.
