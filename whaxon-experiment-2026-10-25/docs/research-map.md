# Research Map — the WHAXON repository

**Object of study:** `github.com/andreipath26/WHAXON-AI-Forensics` (cloned 2026-10-25, depth 50).
**Size:** 126 Python modules under `src/whaxon/` (~20,200 lines), 105 test modules, 33 documents
under `docs/`, plus packaged engagement artefacts under `data/`.

## 1. What the project claims

The README makes four claims that are specific enough to test:

| # | Claim (paraphrased) | Where |
| --- | --- | --- |
| C1 | Scope is enforced **fail-closed**: a missing or malformed config never permits everything; RFC1918-only default. | `README.md`, `docs/scope.md` |
| C2 | Findings stay `candidate` until a payload is **replayed** and the response shows the expected evidence (error marker / reflected marker / timing delta); only then is the finding `verified` and given a `curl` proof. | `README.md` §"Why WHAXON?" |
| C3 | "**No LLM decides if a finding is real. The proof does.**" | `README.md` |
| C4 | Adapters normalise tool output into a findings model with remediation, CVSS and CWE. | `README.md`, `docs/findings.md` |

The README also *self-declares* two limitations: only kinds with a replay path are covered, and
"timing-based verification can false-positive on a slow baseline". Both are relevant because a
study that rediscovers them adds nothing; a study that **quantifies** them and tests the adjacent
unstated claims does.

## 2. Architecture in one table

| Layer | Module(s) | Role |
| --- | --- | --- |
| Scope | `core/scope.py` | `ScopeManager.check(target)` → allow/deny with a matched rule |
| Catalog | `core/catalog.py`, `data/tools.json` | declared tools: binary, args template, capabilities |
| Runner | `core/runner.py` (`ToolRunner`) | scope gate → argv build → subprocess → event stream |
| Adapters | `adapters/*.py` (30+) | parse tool stdout into `Finding` objects |
| Validator | `core/validator.py` | replay payloads, decide `verified` / `refuted` / `candidate` |
| Proof | `core/reproduce.py` | render a `curl` command for a verified finding |
| Store / report | `core/store.py`, `core/report.py` | persist, deduplicate, render Markdown/HTML/PDF |
| Correlation | `core/correlator.py`, `core/suggester.py` | cross-tool patterns, next-step suggestions |
| AI | `ai/executor.py`, `core/ai_bridge.py` | optional planner; executor disposes |
| Interfaces | `interfaces/{cli,tui,gui,web}` | five front-ends over the same core |

## 3. Where the enforcement actually happens

`grep -rn "scope.check\|OutOfScopeError"` yields enforcement points at:

- `core/runner.py:134` (`run_tool`), `:230` (SMB session), `:294` (WMI session), `:355` (third session path)
- `core/recon.py:84`, `interfaces/cli/recon_cmd.py:51`, `run_cmd.py:168`
- `interfaces/web/server.py:417`, `:672`, `:794`
- `interfaces/gui/main_window.py:295`, `interfaces/tui/screens/main.py:435`
- `ai/executor.py:338` via `scope_check` callable injected by `core/ai_bridge.py:39`

**Observation:** every enforcement point receives a *target string*. None resolves the name to an
address, and none re-checks a redirect target or a tool's self-generated URLs. That is the design
decision the scope experiments test.

## 4. Where verification actually happens

`core/validator.py` has **two replay paths**:

| Path | Trigger | Method support | Redirects | Host pinning | Cookie stripping | Timing verdict |
| --- | --- | --- | --- | --- | --- | --- |
| `validate()` query-parameter path (`_fetch`) | finding has `data.parameter` | GET only | blocked (`NoRedirect`) | none | n/a (no headers sent) | **`verified`** if `delta ≥ 3.0 s` |
| `_replay_ctx()` | finding has `data._request_context` | GET/HEAD/OPTIONS only | blocked | host+port pinned to target | `Authorization`/`Cookie` removed | **`candidate`** ("needs independent confirmation") |

The two paths disagree by construction on timing evidence and on non-GET methods. That
inconsistency is the subject of E8.

Payload source: `src/whaxon/data/payloads/*.md`, harvested by `PayloadLoader` from *all* fenced
code blocks. `validate()` always uses `payloads[0]`.

## 5. What the repository already contains as "proof"

`data/proof-dvwa/` holds a prior engagement against a **different** DVWA instance
(`172.17.0.3`, a local Docker container) produced 2026-10-17: `engagement.json` (4 jobs: nmap,
nikto, ffuf, gobuster), Markdown/HTML job reports, and `scope.json` listing the container as
authorised.

This artefact is used in E9 as an internal-consistency witness, not as evidence about this
engagement's target. `docs/STATE.md` also records the maintainers' own known-unverified items
(WMI transport never run; report job-history counts show 0; raw job output not persisted), which
are treated as claims by the authors, not verified here.

## 6. Existing test coverage relevant to this study

| Area | Tests | What they pin |
| --- | --- | --- |
| Scope | `tests/test_scope.py`, `test_scope_failclosed.py` | precedence, wildcards, CIDR, fail-closed defaults, URL-host normalisation, IPv6 |
| Validator | `tests/test_command_injection.py`, `test_ai_boundary.py` | canary form, POST-replay refusal, scope gating in the AI executor |
| Adapters | `test_adapters_*` | shape of parsed findings, incl. ffuf silent mode |
| Web/TUI | `test_web_*`, `test_tui_*` | routes and rendering |

**Gap in their own suite:** no test asserts that a *fabricated* ffuf status is wrong, none
compares two adapters on the same input, none measures the validator against labelled truth, and
none tests destination binding (DNS or redirect). Those four gaps are what this study supplies.

## 7. Reading order for a reviewer

1. `src/whaxon/core/scope.py` — the safety boundary (all 249 lines).
2. `src/whaxon/core/validator.py` — the verification engine (369 lines; note the two paths).
3. `src/whaxon/adapters/ffuf.py` — 90 lines; line 74 is the `status` default.
4. `data/proof-dvwa/engagement.json` — the authors' own proof artefact.
5. This study's `scripts/*.py` and `experiments/benchmark/server.py` — what was measured.
