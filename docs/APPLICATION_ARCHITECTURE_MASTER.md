# WHAXON — APPLICATION ARCHITECTURE, AGENTS, TOOLS AND API MASTER

> **Verified source / CI reconciliation — 2026-11-05.** Inspected `main` `55618da47724b9d6c4d2377cee34517171770b56` and source paths `src/whaxon/cli.py`, `core/__init__.py`, `core/providers.py`, `core/workflow_requests.py`, `interfaces/web/server.py` and GUI `embed.py`. The CLI dispatch list and persistent core/provider boundaries described here are implemented, as are both V2 durable APIs and separate legacy direct `/api/run` and `/api/ai/run` endpoints. The legacy transports are **not** universally migrated. [Exact-SHA CI run 42033360849](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/42033360849) passed 13/13 jobs at `fc056d0`; no production acceptance is inferred.

**Canonical shared application and developer reference, consolidated 2026-11-05.** This master covers the application outside the separately governed Engine V2 and UI V2 contracts. Operational and implementation assertions in original snapshots must be checked against current code/tests. Security authorization remains deterministic; AI proposals never grant execution permission. The root roadmap controls priorities.

## Navigation

- Part 1: architecture.md
- Part 2: agent-architecture.md
- Part 3: autonomous-loop.md
- Part 4: session-execution.md
- Part 5: METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md
- Part 6: TOOL_INTELLIGENCE_AND_ONBOARDING.md
- Part 7: adapters.md
- Part 8: ai.md
- Part 9: plugins.md
- Part 10: tools.md
- Part 11: scope.md
- Part 12: interfaces.md
- Part 13: api.md

---

## Part 1 — architecture.md

# Architecture

WHAXON is a shared Python assessment core exposed through CLI, terminal, desktop and Flask web interfaces. External tools are described by a catalog and connected through adapters/providers. The architecture is evolving toward the durable, capability-driven Engine v2 described in [the Engine v2 crosswalk](ENGINE_V2_MASTER.md); that target design is not the same as a fully accepted deployment architecture.

## Layers

    Interfaces
      TUI (Textual)   GUI (PySide6 + QWebEngineView)
      Web (Flask + SSE + Basic auth)
      CLI (mode dispatcher; see `whaxon --help` for the installed command surface)
                |
          whaxon.core.Core
            EventBus       pub/sub, async
            ToolCatalog    reads data/tools.json -> Tool dataclasses
            ScopeManager   fail-closed policy, data/scope.json
            Settings       data/settings.json
            ToolRunner     build_argv + subprocess + stream pump
            JobStore       SQLite (data/whaxon.db): jobs, lines, findings,
                           coverage, evidence, sessions and workflow state
            MSFClient      pymetasploit3 RPC
                |
          whaxon.adapters
            Adapter ABC   parse(lines, ctx) -> list[Finding]
            register()    module-level self-registration
            built-ins     catalog-backed adapters; see adapters.md and the live catalog

## Data flow - one job end to end

1. Interface calls core.runner.run_tool(tool_id, target, extra_args=...).
2. ScopeManager checks target. Out of scope and no allow_out_of_scope -> OutOfScopeError, no process spawned.
3. ToolRunner.build_argv looks up the Tool, formats its args template with {target}, appends extra_args.
4. ToolRunner.run spawns the subprocess via asyncio.create_subprocess_exec, pumps stdout/stderr line by line, publishes JobStarted, JobOutput, JobFinished / JobFailed.
5. JobStore persists job lifecycle, output lines, findings, coverage and evidence through the event/store integration.
6. Runner._publish_findings looks up the adapter for tool_id, calls adapter.parse(lines, ctx={tool_id, extra_args, argv, target}), publishes JobFindings.
7. Interface renders. Web streams events via SSE at /api/jobs/<id>/stream.

## Adapter contract

Adapter.parse(lines, ctx):

- lines: list[tuple[str, str]] - (stream, text), stream in {stdout, stderr}
- ctx: dict - recognized keys: tool_id, extra_args, argv, target

Returns list[Finding]. Each Finding may carry severity, CVSS, CWE, impact, remediation, references, and a structured data dict.

Adapters autodetect by content or dispatch on ctx[extra_args]. The impacket adapter uses extra_args to select the subtool (secretsdump / smbclient / wmiexec), falling back to autodetect when ctx is empty.

See adapters.md.

## Persistence

SQLite at the configured data directory (default `data/whaxon.db`). The schema is created and migrated by `src/whaxon/core/store.py`. The following is a concise source-derived inventory; migrations may add columns to older databases.

- `jobs`: id, tool, target, status, exit_code, error, started_at, finished_at, duration_s and worker lease/heartbeat fields.
- `lines`: job_id, seq, stream, text.
- `findings`: job_id, seq, kind, severity, source, data_json, raw_line, enrichment_json, verification_status, verified_by and verification_reason.
- `coverage`: job_id, seq, tool_id, target, kind, detail, phase and timestamp (`at`).
- `sessions`: id, host, type, info_json, opened_at, last_seen and status.
- `evidence`: job_id, seq, kind, name, path, note and added_at.
- `ai_runs`, `ai_run_steps` and `approvals`: AI run state, step history and approval records.
- Engine v2: `missions`, `workflow_plans`, `workflow_tasks`, `capability_manifests` and `task_attempts`.

The schema above is not a promise that every subsystem has completed production acceptance. Engine v2's remaining guarantees and migration work are tracked in [the Engine v2 crosswalk](ENGINE_V2_MASTER.md) and master roadmap §49.

## Fail-closed design

Two things are deliberately strict:

1. Scope - missing scope.json writes a strict default on load; unreadable scope.json raises. Never silently allows everything. See scope.md.
2. Reports - HTML output escapes markdown before wrapping in <pre>, so a tool that prints <script> cannot inject script into a browser viewing a report.

## Extending

- New tool: add an entry to data/tools.json (id, binary, args template).
- New adapter: subclass Adapter, implement parse, register(MyAdapter()) at module level, and import it from whaxon/adapters/__init__.py.
- New interface: import Core, subscribe to the EventBus, call runner.run_tool. No core changes needed.

---

## Part 2 — agent-architecture.md

# Agent Architecture

**Status (2026-11-02): HISTORICAL DESIGN RECORD.** This proposal predates the current agent and Engine v2 implementation. The module table below is an older snapshot; statements describing the agent as one-step-only, unable to resume, or otherwise unimplemented must not be treated as current without checking `src/whaxon/ai/`, `src/whaxon/core/` and their tests. Current delivery status is governed by the master roadmap and [Engine v2 crosswalk](ENGINE_V2_MASTER.md).
**Historical scope:** An early autonomous-driving proposal. The referenced `whaxon_vision.md` is not part of the current repository tree.
**Non-goals:** Anything that changes the pipeline, the executor's deterministic boundary, or the adapter layer.

## 1. Purpose

At the time this design was written, WHAXON was primarily operated one tool at a time. A human picks the tool, picks the
target, presses run, reads the output, and decides what to do next. The
AI layer (`whaxon/ai/`) can propose a single next action and a
deterministic executor will validate and run it — but only within a
bounded loop that stops at the first `ask_human` and never resumes.

This document describes how to grow that into an agent that can drive
a whole engagement: given an objective, plan a sequence of steps, run
them, react to results, and hand control to the human whenever it needs
to. **The human stays in charge at all times.** The agent proposes; the
executor disposes; the human decides what the executor is allowed to do.

## 2. What existed in the original design snapshot

Verified by reading the source, not from memory.

| Module | What it provides |
|---|---|
| `whaxon/ai/actions.py` | `Action` (frozen dataclass, one of `run_tool` / `ask_human` / `stop`), `ActionResult` (per-step outcome fed back to the planner) |
| `whaxon/ai/agent.py` | `Agent.next_action()` — one step of planning; `Agent.audit()` — pre-run feasibility check |
| `whaxon/ai/provider.py` | `Provider` ABC: `plan_step(...)`, `audit_prompt(...)`. `NullProvider` returns stop immediately. |
| `whaxon/ai/providers/rules.py` | `RulesProvider` — deterministic ladder (nmap, then nikto if a web port is up, then stop) |
| `whaxon/ai/providers/llm.py` | `LLMProvider` — planner over any `LLMBackend` (Ollama, OpenAI, Anthropic, Google) |
| `whaxon/ai/executor.py` | `Executor.run()` — the loop. Validates each Action against catalog, scope, target_lock, dedup. Bounds: `ExecutorLimits(max_steps, max_wall_seconds, min_confidence)`. Halts on 2 consecutive failures. |
| `whaxon/core/ai_bridge.py` | The single sanctioned import point from `core/` into `whaxon/ai/`. Everything else in `core/` and `adapters/` is forbidden from importing `whaxon.ai` (enforced by `tests/test_ai_boundary.py` and CI). |

**Historical limitation at the time of this design:** `Executor.run()` returns the moment an
`ask_human` Action is emitted. There is no resume. The loop cannot pause
and continue in a later process.

## 3. The four-layer model

```
┌─────────────────────────────────────────────────────┐
│  Human (in charge)                                  │
│    approves / rejects / adjusts / takes over        │
└─────────────────────────────────────────────────────┘
                    ▲
                    │ approvals, guidance, overrides
                    ▼
┌─────────────────────────────────────────────────────┐
│  Agent (planner)                                    │
│    proposes Action objects, tracks phases, asks     │
│    for help when uncertain                          │
└─────────────────────────────────────────────────────┘
                    ▲
                    │ Action objects
                    ▼
┌─────────────────────────────────────────────────────┐
│  Executor (deterministic)                           │
│    catalog check, scope check, target lock, dedup,  │
│    stagnation stop — the existing machinery         │
└─────────────────────────────────────────────────────┘
                    ▲
                    │ JobStarted / JobOutput / JobFindings
                    ▼
┌─────────────────────────────────────────────────────┐
│  Pipeline (existing WHAXON)                         │
│    catalog + runner + adapters + store + events +   │
│    correlation + reports                            │
└─────────────────────────────────────────────────────┘
```

**Nothing in the bottom two layers changes** for this design. The agent
is a new top layer. The pipeline is what makes it possible.

## 4. Objectives

An **objective** is a short natural-language sentence describing what
the run should accomplish. Examples:

- `"enumerate 10.0.0.5"` — reconnaissance only, no exploitation
- `"find a foothold on 10.0.0.5"` — recon through initial access
- `"test the vsftpd service on 10.0.0.5"` — narrow, tool-specific
- `"recon scanme.nmap.org"` — public-target practice

Objectives are **not**: "pwn X", "own the whole subnet", "get domain
admin". Those are outcomes, not tasks — they don't terminate in a
definable way, and they encourage the agent to attempt unauthorised
actions. The objective grammar is deliberately modest.

**How the agent knows it's been met.** Three signals:

1. **The LLM planner emits `stop`** with a rationale. Default case.
2. **The budget runs out** (max_steps). The run ends with a "budget exhausted" stop.
3. **Stagnation** — 2 consecutive failed steps. The run halts.

There is no verification that the objective *was* accomplished, only
that the agent *decided it was done*. That's honest: this is a
task-execution loop, not a goal-verification system. The human reads
the report and decides whether the objective is achieved.

## 5. Phases

A **phase** is a named stage of the kill chain with a scoped set of
tools and a definition of "enough has been done here."

| Phase | Tools | Definition of done |
|---|---|---|
| `recon` | nmap, masscan (plugin), whois, dig, subfinder (future) | Ports mapped; DNS records collected; subdomains enumerated |
| `enumeration` | gobuster, ffuf, whatweb, wpscan, nuclei (light mode), nikto | Endpoints discovered; web tech identified; low-severity issues logged |
| `vulnerability` | nuclei, sqlmap, nikto (deep), searchsploit lookups | Known CVEs identified for detected versions |
| `initial-access` | msf (exploit modules), impacket (protocol exploits) | At least one session obtained |
| `post-access` | msf (post modules), impacket (secretsdump, smbclient, wmiexec), hashcat | Credentials extracted; privilege level known; loot catalogued |
| `lateral` | netexec (plugin), impacket (with extracted creds), ligolo-ng (future) | Reachable hosts beyond the initial target mapped |
| `done` | — | Objective met or budget exhausted |

Phases are **suggested by the agent, confirmed by the human**. The agent
proposes a transition ("recon is complete, move to enumeration?") via an
`ask_human` Action. The human answers y/n. This is the phase-boundary
check.

**Where phase state lives.** The `ai_runs` table (in `data/whaxon.db`)
gains a `phase` column and a `phase_history` JSON column. Phase
transitions are appended to `phase_history` so the whole progression is
auditable after the run.

**v1 scope:** phases are informational. The agent proposes them, the
report shows them, but they don't restrict which tools can run in which
phase. **v2 scope:** tools are filtered by phase — the planner only
sees the tools relevant to its current phase, which both narrows the
search space and reduces the chance of the LLM proposing something
nonsensical ("run hashcat against 10.0.0.5 in the recon phase").

## 6. The loop

**Today:**

```
executor.run() calls agent.next_action() in a bounded for-loop.
ask_human -> loop ends.
No resume. No phase tracking. No persistence beyond ai_runs.
```

**Target (v1):**

```
executor.run(goal) {
    audit = agent.audit(goal)
    if not audit.feasible: return [stop]
    history = []
    for step in 1..max_steps:
        action = agent.next_action(goal, history, catalog, scope, step, phase)
        on_action(action)
        if action.kind == "stop":        return history
        if action.kind == "ask_human":
            answer = await self.ask_human(action)   # <-- new: pauses and resumes
            history.append(synthetic_result_from(answer))
            continue                                 # <-- new: loop continues
        if action.kind == "run_tool":
            result = await self._validate_and_run(action, history)
            history.append(result)
            on_result(result)
            if not result.ok: consecutive_failures += 1
            else:              consecutive_failures = 0
            if consecutive_failures >= 2:
                return history  # stagnation stop
    return history
}
```

The only new primitive is `await self.ask_human(action)`. Everything else
in the loop is unchanged from today.

**`ask_human` mechanism (v1):**

The Executor gains a new constructor argument:

```python
ask_human: Callable[[Action], Awaitable[str]] | None = None
```

If `None`, `ask_human` behaves as today (loop ends). If provided, the
executor awaits it. The interface (CLI, web route) provides the
implementation.

**CLI implementation:**

```python
async def _cli_ask_human(action: Action) -> str:
    print(f"[agent] {action.rationale}")
    return await asyncio.to_thread(lambda: input("> ").strip())
```

The `asyncio.to_thread` is because `input()` is blocking; the loop is
async. This keeps the executor's loop shape intact.

**Answer semantics:**

| Answer | Meaning |
|---|---|
| `y` / `yes` | Approve. If the action was `run_tool`, run it. If it was a phase transition, transition. |
| `n` / `no` | Reject. Feed back to the planner; next step sees the rejection in history. |
| `skip` | Drop the action, continue to the next step without running anything. |
| any other text | Freeform guidance. Appended to history as a synthetic result with the text as `summary`. |

**Persistence (v2):** `ai_runs` gains `status='waiting'` and a
`pending_question` JSON column. A new CLI subcommand:

```
whaxon ai --resume <run_id> --answer y
```

reconstructs the executor state from `ai_runs` and `ai_run_steps` and
resumes at the next step. This survives crashes and lets the human
answer hours later. **Out of scope for v1.**

## 7. State persistence

**Per-run state that must survive a crash (v2):**

| State | Where |
|---|---|
| Run id, goal, phase, current step | `ai_runs` row |
| Every step's Action + ActionResult | `ai_run_steps` rows (already exists) |
| Pending question (if `status='waiting'`) | `ai_runs.pending_question` |
| Phase history | `ai_runs.phase_history` (JSON) |
| Answer to the last question | Appended to `ai_run_steps` |

**Per-run state that may be in-memory only (v1):**

Everything. A crashed run is a lost run. The findings it produced are
still in `findings` (the store subscribes to the event bus), but the
agent's history is gone and the run cannot be resumed.

**v1 → v2 transition:** adding the `pending_question` column and a
`--resume` subcommand. The `ai_runs` schema already exists and has
`status`; the change is small.

## 8. Human-in-the-loop protocol

**Who the human is (v1):** the person running `whaxon ai "..."` in a
terminal. One human, one run, blocking. No queue. No web UI. No
concurrency.

**When the human is asked:**

1. **When the planner is uncertain.** LLM confidence below
   `WHAXON_AI_MIN_CONFIDENCE` (default 0.55) → automatic demotion to
   `ask_human`. This is already in `Agent.next_action`.
2. **When the planner asks.** LLM explicitly emits `ask_human` with a
   rationale.
3. **At phase boundaries.** The planner proposes a transition; human
   confirms.
4. **When an action fails twice in a row.** The run halts; the human
   gets a `stop` with the failure reason. Not a resume — a fresh run.

**What the human sees:**

```
[agent] Step 4 of 12. Phase: enumeration.
[agent] Proposing: run gobuster against 10.0.0.5 with extra_args
        "-u http://10.0.0.5 -w /usr/share/wordlists/dirb/common.txt"
[agent] Rationale: nmap found port 80 open; gobuster will enumerate
        endpoints on the web service.
[agent] Confidence: 0.72
[agent] Approve? [y/n/skip/text]
>
```

**What the human answers:** see section 6.

**What happens when the human never answers:** the CLI blocks. There is
no timeout in v1. If you walk away, the run waits. `Ctrl+C` cancels the
run cleanly; the store still has every finding produced so far.

**Where the human CANNOT intervene:** mid-run, the human cannot change
the executor's `ExecutorLimits`, cannot add targets to scope, cannot
change the objective. Any of these requires killing the run and starting
a fresh one. This is deliberate. v2 may add a "pause and reconfigure"
verb.

## 9. Scope expansion policy

**The problem.** The agent runs nmap on `10.0.0.5`. nmap's output
reveals a DNS name (`db.internal`), a second IP (`10.0.0.6`), and a
SMB share name. Does the agent get to scan `10.0.0.6`? Scan
`db.internal`? Look for the share?

**Three policies, must pick one:**

| Policy | Behavior | Legal posture |
|---|---|---|
| **Strict** | Only explicitly-listed targets. Discovered hosts are never automatically in scope. The agent may propose adding one; the human must approve. | Safest. Most pentest contracts are written for explicitly-listed targets. |
| **Inherited** | Any host that resolves from an in-scope domain, and any host in the same RFC1918 subnet as an in-scope host, is in scope. | Common in internal pentests. Riskier if the discovered range includes systems outside the written scope. |
| **Recommended** | As inherited, but every auto-expansion is logged and the human can veto before the first action against the discovered host. | Middle ground. |

**v1 ships `strict`.** Every discovered host is out of scope until the
human adds it to `data/scope.json` and re-runs. The agent may *propose*
expansion via `ask_human`, but the executor will reject any action
against an out-of-scope target regardless of the answer. Scope is
enforced at the executor's check, not at the LLM's.

**Why strict for v1:**

1. Scope enforcement is the safety property the whole tool rests on.
   Loosening it is a policy change, not a feature.
2. Discovery-driven expansion makes the tool's behavior hard to predict.
   An autonomous agent that scans a subnet it found is a legal and
   operational liability.
3. Adding inherited or recommended later is a small change to the scope
   checker plus a config flag. Starting strict and moving to looser is
   easy. Starting loose and trying to tighten is a rewrite.

**Config:**

```
WHAXON_AI_SCOPE_EXPANSION=strict|inherited|recommended
```

Default `strict`. Documented in `README.md` and `docs/scope.md`. Any
value other than `strict` prints a startup warning.

## 10. LLM authority

**The LLM may decide on its own:**

- Which tool to run next (within its current phase's tool set)
- What extra args to pass
- When to stop
- When to ask a question

**The LLM may propose but not execute:**

- Expanding the scope (subject to `ask_human` and executor check)
- Transitioning phases (subject to `ask_human`)
- Running a tool not in the catalog (**never allowed** — executor refuses)
- Running against a target outside scope (**never allowed** — executor refuses)
- Running the same action twice successfully (**never allowed** — dedup check)
- Exceeding the step budget (**never allowed** — bounded loop)

**The LLM may never:**

- Write to the store
- Modify `data/scope.json`
- Spawn a subprocess (only the executor does this)
- Read raw tool output (only structured findings and summaries)
- Access the filesystem except through the pipeline's own tools
- Reach any tool that isn't in `data/tools.json`

These are enforced by the executor, not by prompting. The LLM cannot
talk its way past a check that happens after it emits an Action.

## 11. Cross-run learning

**v1: none.** Every run starts from scratch. The agent's history is
empty at step 1. Nothing from previous runs is visible.

**Rationale:** cross-run learning requires the agent to read the store,
which violates the "planner sees only structured findings, never the
store" boundary. Opening that boundary is a meaningful change to the
threat model and should be done deliberately, with a separate design.

**Future direction (v2+):** the agent is given a *summary* of prior
runs — "in the last 5 runs against this target, gobuster found X, Y, Z;
no new findings were produced" — computed by a deterministic function,
not read directly from the store. That keeps the boundary intact while
letting the planner benefit from history.

## 12. What "done" looks like

Three ways a run ends:

1. **The LLM emits `stop`.** Default, common case. The report shows the
   final rationale.
2. **The step budget is exhausted.** `for step in 1..max_steps` falls
   through. The last entry in `ai_run_steps` is a synthetic stop.
3. **Stagnation.** Two consecutive failed steps. The executor halts with
   a "halting on stagnation" result.

**The report** includes a run summary at the top: phase history, number
of steps, findings count, and whether the run stopped naturally or was
cut off. The human reads this and decides whether the objective was
achieved.

## 13. Migration plan

What code changes, in what order, to get from today to the v1 design.

| Step | Change | Scope |
|---|---|---|
| 1 | `Executor` gains `ask_human: Callable[[Action], Awaitable[str]] | None`. When set, `ask_human` Actions pause and resume instead of terminating. When unset, existing behavior is preserved. | 1 file, `executor.py`. Tests for both paths. |
| 2 | `ai_runs` gains a `phase` column, default `"recon"`. `store.create_ai_run` and `get_ai_run` round-trip it. | `store.py` and a small migration. Tests. |
| 3 | `Agent.next_action` gains a `phase` parameter, passed through to `provider.plan_step`. `LLMProvider` includes the phase in its prompt. | `agent.py`, `provider.py`, `providers/llm.py`. |
| 4 | `whaxon ai` CLI (`ai_cmd.py`) uses the new `ask_human` callback. Prints the question, reads stdin, resumes the loop. | `interfaces/cli/ai_cmd.py`. |
| 5 | Phase transitions become `ask_human` Actions emitted by the LLM when it decides a phase is complete. Phase string is stored in `ai_runs.phase`. | Design done; implementation is a small addition to `LLMProvider` + the store field. |
| 6 | `WHAXON_AI_SCOPE_EXPANSION` env var, read by `ai_bridge.build_executor`. Passed to the executor's scope check. | `ai_bridge.py`, `scope.py`, `executor.py`. |
| 7 | **`whaxon ai --resume <run_id>`** — persistence of paused runs. `ai_runs.pending_question` column. | Out of scope for v1; see section 6. |

**Steps 1–4 are the v1 MVP.** After step 4, `whaxon ai "enumerate 10.0.0.5"`
works, the human approves each step, and the loop runs to completion
or the human kills it.

**Steps 5–6 are v1.x.** Phase awareness and configurable scope policy.

**Step 7 is v2.** Persistent, resumable runs.

## 14. What this document does not answer

Honest list of open questions deferred to future sessions:

1. **Multi-user concurrency.** If two humans run `whaxon ai` at once
   against the same store, do they see each other's runs? Probably not,
   but the store is shared. Deferred.
2. **Cost tracking.** LLM calls cost real money. Nothing in the current
   code tracks per-run cost. Needed before the agent runs unattended
   for hours. Deferred.
3. **Rate limiting the LLM.** Same problem as NVD rate limits — a
   run that fires 50 LLM calls in 30 seconds will hit provider rate
   limits and fail. Not handled today. Deferred.
4. **What an LLM's "confidence" actually means.** Today it's a float
   the model emits. It has no calibration. In practice it's noise below
   0.5 and reliable above 0.9. The threshold of 0.55 is a first guess,
   not a tuned value. Needs empirical work.
5. **Structured objectives.** "Enumerate 10.0.0.5" is parsed by the
   LLM, not by a grammar. A stricter objective grammar would make the
   audit step more reliable but less flexible. Trade-off not resolved.
6. **Interaction with `/api/ai/run`.** The web route already submits
   runs asynchronously. When the executor's `ask_human` blocks, does
   the web route block too? Needs a "pause into DB" primitive, which
   is the v2 work. Deferred.
7. **The safety implications of the phase model.** Some phases
   (initial-access, lateral, post-access) can cause real harm to real
   systems if authorised incorrectly. The doc treats phases as
   informational. Whether the tool should refuse to enter those phases
   without additional warnings is a policy question, not a technical
   one. Deferred.

## 15. What ships in v1 vs. what waits

**v1 (this design, ~4 sessions):**

- `ask_human` becomes a pause/resume instead of a terminate
- CLI-only human-in-the-loop
- Phase field on `ai_runs`, no enforcement
- Scope expansion: strict only
- `whaxon ai "objective"` works end-to-end

**v2 (later):**

- Persistent paused runs (`--resume`)
- Web UI for approval
- Inherited / recommended scope expansion
- Cross-run summaries
- Cost and rate limiting

**v3 (Phase 4 in the vision):**

- Phase-scoped tool filtering
- ML-driven severity re-scoring
- Report narrative synthesis

**Never in scope:**

- Fully unattended runs against non-consenting targets
- Operations that persist on target systems beyond the engagement window
- Circumventing the executor boundary in any way
## 16. Approval queue and multi-user (v2 design note)

v1 ships single-user, single-run, blocking. `whaxon ai --resume` (session 36) makes paused runs persistable, but the approval loop is still synchronous stdin in the same terminal.

**Multi-user model.** Two problems appear when N humans share a WHAXON instance:
1. Multiple paused runs at once. Each has a `pending_question` (session 36). The CLI prompt doesn't scale.
2. Who approved what. The executor currently records `ai_source="human"` with no user identity.

**Proposed shape.**
- `ai_runs` gains an `owner` column (default `"local"`). Set at `create_ai_run` from an env var or CLI flag.
- `ai_runs` gains an `approvals` table: `(run_id, seq, user, answer, at, note)`. Every human answer is a row, not a mutation of the run's status.
- A new route `GET /api/ai/pending` lists all runs with `status='waiting'`, filtered by owner unless the caller is admin.
- Web UI gains a queue view: table of pending questions, each with approve/reject/skip buttons and a free-text field. Clicking submits `POST /api/ai/runs/<id>/answer`.
- The existing CLI `--resume` becomes one frontend for the same answer API.

**Authority boundary.** The queue does not change what the LLM may propose — the executor's validation is still the last word. The queue changes *who* can approve. Authorization for approvals is a policy decision: any authenticated user, or only the run's owner, or a role with an approval permission. Recommended: owner-only by default, admin override.

**What this does NOT need.**
- No change to the executor's loop. The `ask_human` callback contract stays the same.
- No change to the store's `ai_run_steps` schema.
- No change to the LLM provider interface.

**Effort estimate.** Two sessions. Session 1: schema (`owner` + `approvals` table), `/api/ai/pending`, `POST /api/ai/runs/<id>/answer`, tests. Session 2: web UI queue view, tests, docs. The CLI keeps working unchanged throughout — this is additive.

**Blocking dependency.** None. Can be built anytime.

## 17. GUI slice of Phase D (deferred)

The report (session 28), web UI (session 30), and TUI (session 36) all show AI runs with phase and status. The GUI (PySide6) does not.

**Why deferred, not built.** Two reasons:
1. The GUI is a thin wrapper around the web interface — `interfaces/gui/embed.py` loads the web UI in a WebEngineView. Anything visible in the web UI is visible in the GUI, already.
2. Building a native PySide6 AI-runs panel would mean duplicating logic that already exists in three places (report, web, TUI). The value is aesthetic, not functional.

**If it becomes worth doing.** The minimal version is a `QTableView` bound to `core.store.list_ai_runs()`, refreshed on a timer. Roughly 150 lines. Not worth a dedicated session unless someone actually wants a native app feel; the web-in-GUI embedding already covers the use case.

**Recommendation.** Do nothing. If a user complains the GUI lacks AI visibility, redirect to the web UI tab (which is what the GUI renders anyway).

## 18. Resolved / deferred status of §14 questions

Reviewed after sessions 39-47. Every item is now either answered or deferred with rationale.

| # | Question | Status | Where |
|---|---|---|---|
| 1 | Multi-user concurrency | **Partial.** Approval queue + owner column handle multi-user approvals. Per-owner run visibility in the web UI deferred. | sessions 39, 40 |
| 2 | Cost tracking | **Answered.** tokens_in/out/cost_usd, LLMProvider.usage, _record_usage. | session 38 |
| 3 | LLM rate limiting | **Deferred.** No backoff on 429/503. Attempted session 47; reverted. | — |
| 4 | Confidence calibration | **Deferred.** Empirical, not code. | — |
| 5 | Structured objectives | **Deferred.** Grammar trade-off unresolved. | — |
| 6 | /api/ai/run interaction | **Partial.** Resume mechanism exists. Web route pause attempted session 47; reverted. | — |
| 7 | Phase safety implications | **Deferred.** Policy question. | — |


---

## Part 3 — autonomous-loop.md

# Autonomous Loop

> **Historical design record (2026-11-02).** This document captures an early autonomy proposal and must not be used as a current implementation specification. Its factual snapshot explicitly refers to v0.8.0. Current behavior and delivery status are governed by `src/whaxon/ai/`, the Engine v2 crosswalk and master roadmap §49.

**Status:** Historical proposal; implementation status has evolved since this document was written.
**Historical scope:** An early Phase H proposal from `whaxon_vision.md`, which is not present in the current repository tree.
**Non-goals:** Multi-target engagements, cost budgets, rate limiting, anything that touches the executor boundary.

## 1. Purpose

At the time this proposal was written, the `whaxon ai` loop was described as:

- **Interactive.** Every `ask_human` stops the process and waits for stdin.
- **Single-process.** A paused run cannot be resumed by a fresh process without reconstructing state by hand.
- **Unaware of objectives.** It follows the goal string as a hint, not as a definable success state it can track against.

Phase F gave us the human-in-the-loop machinery: approvals persist, overrides are recorded, resumes are locked. Phase H turns that machinery into a loop that can run unattended *when the human allows it*, and can be paused and resumed across process boundaries *by default*.

**The human is still in charge.** `--auto` is opt-in, gated behind `WHAXON_AI_AUTO_ALLOW=1`. Default behavior is unchanged: the loop pauses on every `ask_human` and waits.

## 2. What existed at the v0.8.0 snapshot (historical)

This table records the source state at v0.8.0 only; it is not a current verification.

| Component | Current behavior |
|---|---|
| `Executor.run(goal, job_id_prefix, target_lock, initial_history)` | Bounded loop. Calls `agent.next_action` per step. Emits `on_action`/`on_result`. Halts on `stop`, `ask_human` (if no callback), budget, or 2 consecutive failures. |
| `ask_human` callback | Async callable. If `None`, loop terminates on `ask_human`. If set, loop awaits it and appends a synthetic `ActionResult(ai_source="human")` to history. |
| `ai_runs` schema | `id, goal, provider, status, started_at, finished_at, error, phase, phase_history, pending_question, tokens_in, tokens_out, cost_usd, owner`. |
| `--resume` | Reads stored `ai_run_steps`, rebuilds history as `ActionResult` objects, appends a synthetic ack with the supplied answer, runs a fresh executor with `initial_history`. |
| Phase transitions | `Action.ask_human` with `proposed_phase` set. Executor validates the phase against the fixed vocabulary; on `y` writes to `ai_runs.phase` and `phase_history`. |
| Approval queue | `approvals` table: `(run_id, seq, user, answer, note, at)`. Web UI and CLI both write to it. |

**What's missing:**

1. **Objective tracking.** The loop has no notion of "have we made progress toward the goal." It stops when the model says stop, or when the budget runs out. No verification that the objective was met.
2. **Cross-process state.** A paused run needs the whole process to keep living, or a human to reconstruct. `--resume` approximates this but starts a fresh executor with carried-over history — not a continuation of the same logical loop.
3. **Unattended phase decisions.** Every phase transition fires an `ask_human`. In `--auto` mode this needs a policy so the loop can cross from recon to enumeration without a human at the keyboard.
4. **Auto-answer policy.** The loop has no way to answer its own questions. Every `ask_human` either blocks or (with no callback) terminates.


## 3. The three questions

Phase H is fundamentally three design questions, not one big one. Each gets its own answer.

### 3.1 Objective tracking

**What it means.** Given a goal like `"enumerate 10.0.0.5"`, does the loop know when the objective has been met?

**Why it matters.** Without an objective, "stop" is entirely the model's judgment. A model that stops too early leaves work undone. A model that never stops burns the step budget. Neither is verifiable after the fact.

**Three options:**

| Option | Definition | Trade-off |
|---|---|---|
| **A. Grammar** | Objectives parsed by a fixed grammar: `verb target [constraint]`. Supported verbs: `enumerate`, `scan`, `recon`, `foothold`, `test`. Each verb maps to a definition of done. | Deterministic, auditable, but rigid — free-text goals must be rephrased. |
| **B. Heuristic** | Each phase has a "done" signal. `recon` done when open ports recorded. `enumeration` done when endpoints or versions found. `vulnerability` done when CVEs matched. Combined with a step budget as a backstop. | Flexible, but the heuristics are guesses. |
| **C. LLM judgment** | The planner decides when the objective is met, and the executor verifies that the stop decision is *reasoned*, not just asserted. | Matches how humans evaluate — but the source-of-truth problem returns. |

**Recommendation: B, with A as an optional gate.**

Heuristics per phase, evaluated deterministically against findings in the store:

- **`recon` done** when `nmap` has produced at least one `open_port` finding against the target, OR when the recon step budget (default 3) is exhausted with no ports found.
- **`enumeration` done** when at least one endpoint, version, or service fingerprint has been recorded, OR enumeration budget (default 4) exhausted.
- **`vulnerability` done** when a vuln-scanner has run against each discovered service, OR the vuln budget (default 3) is exhausted.
- **`initial-access` done** when any session exists for the target, OR the initial-access budget (default 3) is exhausted with no session.
- **`post-access` done** when at least one loot-kind finding has been recorded from inside a session, OR post-access budget exhausted.
- **`lateral` done** when either a new host has been discovered through the pivot, OR the lateral budget is exhausted.

The heuristic answers "is the *phase* done," not "is the *objective* done." The objective is done when the phase the loop is in is the terminal phase for the objective's verb:

| Verb | Terminal phase |
|---|---|
| `recon` | `recon` |
| `enumerate` | `enumeration` |
| `test` | `vulnerability` |
| `foothold` | `initial-access` |
| `exploit` | `post-access` |

If the goal doesn't parse to a known verb, the loop runs until the model emits `stop` or the budget runs out — the current behavior, unchanged.

### 3.2 Cross-process persistence

**What it means.** A run pauses. The process exits. A new process resumes it. The loop continues as if it never stopped.

**What "resumption" needs to preserve:**

- The goal (already stored: `ai_runs.goal`)
- The full history (`ai_run_steps` — already stored)
- The current phase (`ai_runs.phase` — already stored)
- The step budget consumed so far (`len(ai_run_steps)` — derivable)
- The consecutive-failure counter (`ai_runs.consecutive_failures` — **new column needed**)
- Whether the run is in `--auto` mode (`ai_runs.auto` — **new column needed**)

**The mechanism.** Today's `--resume` rebuilds history from steps and starts a fresh loop. That's *approximate* resumption. The design change is small: two new columns carry the state that isn't derivable. `Executor.run` gains an optional `resume_state: dict | None` parameter that seeds `consecutive_failures` from the store when provided.

**Why not a full state machine?** Because the store already *is* the state machine. Every Action, every Result, every phase transition is persisted. Rebuilding history from `ai_run_steps` produces the same loop the previous process was running. The only thing not captured is the failure counter — a small addition.

**Resumability is not "rehydrate Python objects."** It's "replay stored state through the same deterministic loop." The loop is deterministic; the store is durable; resumption is just replay.

### 3.3 Unattended phase decisions

**What it means.** In `--auto` mode, the loop should cross phase boundaries without a human answering each transition.

**The policy.** `--auto` mode answers with one of:

1. **Auto-approve** if the proposed phase is in `WHAXON_AI_AUTO_PHASES` (comma-separated env var).
2. **Auto-deny** if the proposed phase is not in the list, or if the env var is unset. Deny means: append a synthetic answer of `"n"`, the loop continues from the current phase.
3. **Auto-ask** if the proposed phase is in the list but `WHAXON_AI_AUTO_CONFIRM=1` — this re-enables the interactive prompt for transitions even in auto mode.

**Default `WHAXON_AI_AUTO_PHASES` is empty.** With no phases listed, `--auto` mode crosses no boundaries. The loop can still do multi-step work within a phase, but a phase change is refused. This is the safest default.

**The dangerous list.** The three high-risk phases — `initial-access`, `post-access`, `lateral` — should never be in `WHAXON_AI_AUTO_PHASES` by default, and their inclusion should log a warning at run start.

### 3.4 Auto-answer policy

**What it means.** In `--auto` mode, the loop answers its own `ask_human` questions that aren't phase transitions.

**The general case.** A non-transition `ask_human` has no `proposed_phase`. The loop can:

- **Answer `skip`** — the loop drops the pending action, continues. Default in auto mode.
- **Answer `stop`** — the loop terminates cleanly with a rationale.

**Recommendation: `skip`.** Least-committal answer. Drops the ambiguous step and continues, letting the model try a different approach on the next step. If the model keeps producing `ask_human`s, the step budget will exhaust naturally.

**Never in auto mode:**

- The loop never emits a raw tool action on the human's behalf when the answer was ambiguous.
- The loop never auto-approves a scope expansion.
- The loop never auto-approves a run against an out-of-scope target. That's the executor's check, not the answerer's job.


## 4. The mode

**New flag:** `whaxon ai "<goal>" --auto`.

**New env vars:**

| Env | Default | Meaning |
|---|---|---|
| `WHAXON_AI_AUTO_ALLOW` | `0` | Master switch. `--auto` refuses to run if this is not `1`. Prevents accidental unattended runs. |
| `WHAXON_AI_AUTO_PHASES` | `` (empty) | Comma-separated phases the loop may cross unattended. |
| `WHAXON_AI_AUTO_CONFIRM` | `0` | If `1`, phase transitions in the allowed list still prompt. |
| `WHAXON_AI_AUTO_MAX_STEPS` | `50` | Step budget for `--auto` runs. Separate from the interactive default of 12. |

**Precedence:**

1. If `--auto` is not passed: current behavior, no changes.
2. If `--auto` is passed and `WHAXON_AI_AUTO_ALLOW != 1`: exit with a clear error.
3. If `--auto` is passed and `WHAXON_AI_AUTO_ALLOW == 1`: the auto-answer callback replaces `_stdin_ask_human`.

**The run record.** `ai_runs.auto` (new column, 0/1) records whether the run was started in auto mode. A resumed run inherits the mode from the stored flag.

**Interruption.** `--auto` can be interrupted with Ctrl+C. The run is marked `status='paused'` and can be resumed with `--resume` in either mode.

## 5. The loop after Phase H

    Executor.run(goal, initial_history, resume_state) {
        audit = agent.audit(goal)
        if not feasible: return [stop]

        history = initial_history or []
        consecutive_failures = resume_state.get("consecutive_failures", 0)
        start_step = len(history) + 1
        for step in start_step..max_steps:
            action = agent.next_action(goal, history, catalog, scope, step, phase, prior_runs)
            on_action(action)

            if action.kind == "stop":
                on_result(...); return history

            if action.kind == "ask_human":
                on_result(...)
                if ask_human is None: return history
                answer = await ask_human(action)
                history.append(synthetic_ack(answer))
                on_result(synthetic_ack)
                if action.proposed_phase and answer_was_yes(answer):
                    phase_set(action.proposed_phase)
                if phase_is_terminal_for_objective(goal):
                    history.append(synthetic_stop("objective met"))
                    return history
                continue

            if action.kind == "run_tool":
                result = await validate_and_run(action, ...)
                history.append(result); on_result(result)
                if result.ok: consecutive_failures = 0
                else:
                    consecutive_failures += 1
                    store.set_ai_run_consecutive_failures(run_id, consecutive_failures)
                    if consecutive_failures >= 2:
                        history.append(synthetic_stop("stagnation"))
                        return history
        return history
    }

**Two new lines compared to today:** the objective-completion check after phase transitions, and the `consecutive_failures` persist.

## 6. Migration plan

| Step | Change | Scope |
|---|---|---|
| 1 | `ai_runs` gains `consecutive_failures INTEGER DEFAULT 0` and `auto INTEGER DEFAULT 0`. Idempotent migration. | `store.py` |
| 2 | `JobStore.set_ai_run_consecutive_failures`, `JobStore.get_ai_run` returns the fields. | `store.py` |
| 3 | `Executor.run` accepts `resume_state: dict | None`. Seeds `consecutive_failures` from it. Persists the counter via an injected callable. | `ai/executor.py` |
| 4 | `ai/objectives.py` — verb parser and `is_terminal_phase(goal, phase)` helper. | new file |
| 5 | `ai/auto_answers.py` — policy module: `answer_question(action, goal, env) -> str`. Returns `y` / `n` / `skip` based on phase list, env vars, action kind. | new file |
| 6 | `ai_cmd.py` — `--auto` flag, mode gate, wire the auto-answer callback, thread `resume_state` through `_run_fresh` and `_resume_body`. | `ai_cmd.py` |
| 7 | `--resume` reads `auto` from the store and reconstructs the same mode. | `ai_cmd.py` |

**Steps 1–4 are prerequisites for step 6.** Step 5 is independent. Step 7 is a small addition.

**Estimated: 3 sessions.** Session 1: steps 1–3 (store + executor). Session 2: steps 4–5 (objectives + auto_answers). Session 3: steps 6–7 (CLI wiring) plus tests.


## 7. What this document does not answer

1. **Multi-target engagements.** The loop tracks one goal, one target. "Enumerate 10.0.0.0/24" is not supported; the loop would need to fan out per host and aggregate. Deferred.
2. **Cost budgets.** `--auto` runs have a step budget but not a cost budget. A run that hits 50 steps on `gpt-4o` costs real money. Enforcement is deferred; the tokens and cost are already recorded, so enforcement can be added later without schema changes.
3. **Rate limiting.** The loop makes one LLM call per step. At 50 steps in a fast loop, that's 50 calls in a short window. Provider rate limits may fire. Retry-with-backoff was attempted in session 47 and reverted; a proper design is still missing.
4. **Concurrent runs.** The lock file prevents two resumes of the *same* run. Nothing prevents two `--auto` runs against the same target. Deferred.
5. **What an auto-answered run reports.** The report currently shows the human answer in history; in auto mode the answers are `"skip"` and `"y"` with `ai_source="human"` — misleading, because no human answered. Should the `ai_source` be `"auto"` instead? Design decision deferred.
6. **The safety of the terminal-phase heuristic.** If the objective's terminal phase is wrong, the loop stops early or runs long. The heuristics in §3.1 are the first guess, not a validated set.
7. **What happens when the objective is met but the model disagrees.** If the heuristic says "recon done" but the model wants to keep running, who wins? Recommendation: heuristic wins — it's deterministic. But this is a policy choice, not a technical one.

## 8. What ships in v1 of Phase H vs. what waits

**v1 (this design, ~3 sessions):**

- `ai_runs.consecutive_failures` and `ai_runs.auto` columns
- `Executor.run` accepts `resume_state`
- `ai/objectives.py` with the five-verb grammar and terminal-phase mapping
- `ai/auto_answers.py` with the env-var-driven policy
- `whaxon ai --auto` gated on `WHAXON_AI_AUTO_ALLOW=1`
- `--resume` inherits the mode from the store
- Tests for objectives, auto_answers, resume_state, and the full loop

**v2 (later):**

- Cost budget enforcement
- Multi-target fan-out
- Concurrent run isolation
- `ai_source="auto"` in history for auto-answered steps

**Never in scope:**

- Unattended runs against non-consenting targets
- Auto-approval of scope expansion
- Circumventing the executor boundary
- Any behavior that changes what the LLM may propose

## 9. Closing note

Phase H is the last phase the vision doc names. What it delivers is not "the AI does everything on its own" — it's "the AI can keep working without a human at the keyboard, *when the human has explicitly allowed it*." The default stays interactive. `--auto` is a mode, not the new normal.

The human is still in charge. The store is still the source of truth. The executor's boundary still holds. Phase H changes who answers the questions, not what the questions are or who they're answered for.

---

## Part 4 — session-execution.md

# Session-Based Execution

**Status (2026-11-02): HISTORICAL DESIGN RECORD.** This document predates the session-scoped implementation. The current source and the later session implementation notes supersede the original design assumptions. Check `src/whaxon/core/msf.py`, `src/whaxon/core/portfwd.py`, `src/whaxon/core/autopivot.py`, `src/whaxon/adapters/msf.py` and their tests for current behavior.
**Scope:** Post-exploitation primitives that run *inside* a session, not *against* a host.
**Non-goals:** Changing the pipeline, the executor's deterministic boundary, or the existing MSF module-execution path.

## 1. Purpose

In the original design snapshot, ordinary host-scoped tools executed this way: build an argv, spawn a subprocess, capture stdout, parse findings. That model works for scanning a host. It does not work for acting *through* a host.

A Metasploit session is a live connection to a compromised machine. Once you have it, the useful operations are not new commands against a target — they are commands *inside* the session: `sysinfo`, `getuid`, `hashdump`, `enum_network`, `portfwd add`. These have no argv. They have a session id and a verb.

The runner has no concept of this. The AI planner has no concept of this. The catalog has no concept of this. That is the gap Phase E closes.

**Original design scope (historical): Metasploit sessions only.** SSH, SMB, and WMI are deferred — the abstraction should accommodate them, but the first implementation reads from and writes to `MSFClient` and nothing else.

## 2. Implementation facts recorded in the historical design note

Verified by reading the source, not from memory.

| Module | What it provides |
|---|---|
| `whaxon/core/msf.py` | `MSFClient` — RPC wrapper. `sessions()` lists sessions. `session_exec(sid, cmd, timeout)` writes a command and polls for output. `execute(type, name, options)` runs a module through a console. |
| `whaxon/core/msf_tracker.py` | Polls the RPC for session changes, fires `SessionStarted` / `SessionClosed` on the event bus. |
| `whaxon/core/pivot.py` | `pivot_edges` table. Kinds: `exploit`, `session`, `forward`. Relations: `from_exploit`, `tunnels_via`, `reached_through`. `chain_for_session()` walks descendants. |
| `whaxon/core/portfwd.py` | Local port forwarding through a raw shell session. `add_forward`, `remove_forward`, `list_live`. |
| `whaxon/core/autopivot.py` | Detects additional RFC1918 networks a session can reach. |
| `whaxon/adapters/msf.py` | Turns MSF module output into findings. Emits `msf_session`, `msf_loot`, `msf_chain`, `msf_chain_error`. Has an opt-in post-module autochain. |
| `whaxon/core/events.py` | `SessionStarted`, `SessionClosed`, `SessionOutput` events. |

**Note (session 56):** This design doc was written in session 31 before the abstraction was built. The session-scoped path landed in sessions 32-35. The text below describes the state at design time. Read it as a historical snapshot, not the current state.

**Historical limitation at the time of session 31 (superseded):** the runner had no session-scoped path. Every tool invocation goes through `ToolRunner.run_tool(tool_id, target, ...)`, which builds an argv and calls `subprocess`. The MSF session-exec path is called **directly** by the `msf` adapter and by the web route `POST /api/msf/sessions/<id>/exec`. There is no catalog entry, no adapter contract, no AI planner visibility for "run a command in session N."

## 3. The new abstraction: a session-scoped tool

A **session-scoped tool** is a unit of work that takes a session id instead of a target. Its execution path is:

    session_id  ->  MSFClient.session_exec(session_id, command)  ->  stdout  ->  adapter.parse  ->  findings

Compare to a host-scoped tool:

    target  ->  ToolRunner.build_argv  ->  subprocess  ->  stdout  ->  adapter.parse  ->  findings

Same *shape*. Different *transport*. The adapter contract is unchanged — it takes lines and a context, returns findings. Only the dispatcher differs.

### 3.1 The catalog

Session-scoped tools live in the same `data/tools.json` catalog but carry a new required field:

    {
      "id": "msf_sysinfo",
      "name": "MSF sysinfo",
      "category": "session",
      "transport": "msf_session",
      "command": "sysinfo",
      "description": "Collect system information from the session",
      "package": ""
    }

Key changes to the schema:

- **`category`: `"session"`.** New category value. Existing values (`recon`, `web`, `vuln`, `test`) are host-scoped and unchanged.
- **`transport`: `"msf_session"`.** Required on session-scoped tools. Absent on host-scoped tools, meaning `"cli"` by default.
- **`command`**: for `msf_session` transport, the literal string written to the session. Replaces `args` (which would be argv).
- **No `binary` or `package`.** A session-scoped tool does not need an installed binary.

### 3.2 The Action

`Action` gains one new optional field:

    session_id: str | None = None

- When `session_id` is set, the tool_id must resolve to a `category == "session"` entry.
- When `session_id` is set, `target` is ignored and should be `None`.
- When `session_id` is not set, behavior is exactly as today.

This mirrors how `proposed_phase` was added in session 24: additive, optional, round-tripped through `to_dict`, no new `ActionKind`.

### 3.3 The runner path

`ToolRunner` gains a second public method:

    async def run_in_session(
        self,
        tool_id: str,
        session_id: str,
        job_id: str,
        timeout_s: float = 15.0,
    ) -> str:
        """Run a session-scoped tool. Returns the job id."""

Inside, it:

1. Looks up the catalog tool. Refuses if `transport != "msf_session"` or `category != "session"`.
2. Verifies the session exists via `MSFClient.sessions()`.
3. Writes `tool.command` to the session, collects output via `session_exec`.
4. Emits `JobStarted`, `JobOutput`, `JobFinished` on the bus — same events as a host-scoped run.
5. Runs the adapter's `parse()` on the collected output; publishes `JobFindings`.
6. Records the job in the store with the same schema.

The store schema does not change. `jobs.tool` holds the tool id, `jobs.target` holds the session id (as `"session:3"` — a namespaced value so host targets and session targets can be distinguished in the history table). This is a hack; a proper `jobs.session_id` column is v2 work.

### 3.4 The adapter

An adapter for a session-scoped tool is the same class as for a host-scoped tool. It overrides `parse(lines, ctx)` and receives the session output as `lines`. The `ctx` dict carries `session_id`, `job_id`, and `store` — same as host-scoped runs plus session specifics.

The MSF adapter already has per-module parsers in `msf_parsers.py` (`parse_sysinfo`, `parse_hashdump`, `parse_enum_network`, etc.). These are reusable. A new `SessionAdapter` can dispatch on `tool_id` to the right parser, or — cleaner — each session tool gets its own adapter module.

**v1 decision:** one `SessionAdapter` in `src/whaxon/adapters/session.py` that dispatches on `tool_id` to the existing `msf_parsers` functions. When a parser is missing, `parse()` returns `[]` and logs a warning. Splitting into per-tool adapters is v2.

### 3.5 The executor

`Executor._validate_and_run` gains a session branch:

- If `action.session_id` is set:
  - Refuse if `action.target` is also set (ambiguous).
  - Refuse if `action.tool_id` resolves to a host-scoped tool.
  - Verify the session exists via a new injected callable `session_check(session_id) -> bool`.
  - Call `run_in_session` instead of `run_tool`.
- Otherwise, unchanged.

The scope check does **not** run on the session id. Scope was checked when the session was established. Re-checking the session's target host is a v2 concern (session state can drift — a session that was in-scope when opened may not be after scope changes).

### 3.6 The planner

The catalog the LLM sees already gets slimmed by `_slim_catalog()` (session 27). Add `category` to the slim shape — it's already there. The model sees session-scoped tools marked `"category": "session"`.

The prompt needs a rule:

> To act inside an existing session, emit `run_tool` with `session_id` set to the session id and `target` omitted. Session ids appear in HISTORY as `msf_session` findings.

The `RulesProvider` learns one new ladder step: after a `msf_session` finding appears in history and the current phase is `post-access`, propose a session-scoped `sysinfo` against that session.

## 4. Objectives this enables

An **objective** that was previously impossible:

- `"enumerate the session on 10.0.0.5"` — the planner sees a `msf_session` finding with `session_id: "3"`, proposes `msf_sysinfo` on session 3, gets system info, proposes `msf_hashdump` next.

An objective that remains impossible:

- `"pivot to 10.0.0.7 through the session on 10.0.0.5"` — the pivot graph exists (`pivot.py`), but the runner has no path for "run a tool through a forward tunnel." That is Phase E.2 work, not this design.

## 5. Phases and session scope

The kill-chain phases (`recon`, `enumeration`, `vulnerability`, `initial-access`, `post-access`, `lateral`, `done`) already exist on `ai_runs.phase` (session 23). Session-scoped tools belong to `post-access` and `lateral`.

**v1: informational only.** Phase does not gate which tools the planner may propose — same as the existing design. **v2:** filter the catalog by phase so the planner only sees session-scoped tools when phase is `post-access` or later.

## 6. What "done" looks like

Three ways a session-scoped run ends:

1. The tool returns output. The adapter parses it into findings. The planner sees them in history on the next step.
2. The tool returns no output within `timeout_s`. The run records a `JobFailed` with `error="session timeout"`. This is a soft failure — the session may still be alive.
3. The session is gone (closed by Metasploit, target rebooted). `session_exec` returns an error string. The adapter produces a `session_lost` finding; the executor records a failure; on the next step the planner sees the session is unavailable.

## 7. Migration plan

| Step | Change | Scope |
|---|---|---|
| 1 | Add `transport` and `command` to the tools schema. Add `session` category. Update `data/tools.json` with the first three session tools (`msf_sysinfo`, `msf_getuid`, `msf_hashdump`). | `catalog.py`, `data/tools.json` |
| 2 | `Action` gains `session_id`. `to_dict` round-trips it. `run_tool` classmethod accepts it. | `ai/actions.py` |
| 3 | `ToolRunner.run_in_session()` — the session-scoped execution path. Refuses unknown transports, verifies session exists, writes command, collects output, emits events, records job. | `core/runner.py` |
| 4 | `SessionAdapter` dispatches on `tool_id` to `msf_parsers`. Register it. | `adapters/session.py` (new), `adapters/__init__.py` |
| 5 | `Executor` gains `session_check` callable and a session branch in `_validate_and_run`. `ai_bridge` wires it. | `ai/executor.py`, `core/ai_bridge.py` |
| 6 | Planner prompt: session rule. `RulesProvider`: post-access ladder step. | `ai/prompts/planner_v1.md`, `ai/providers/rules.py` |
| 7 | Report: session-scoped jobs render in Job History with `session:<id>` as the target; findings correlate normally. | `core/report.py` (likely no change needed) |

**Steps 1–5 are the v1 MVP.** After step 5, `whaxon run msf_sysinfo session:3` works from the CLI. After step 6, `whaxon ai "enumerate the session on 10.0.0.5"` works end-to-end.

**Steps 6–7 are v1.x.**

**v2 deferrals:** SSH/SMB/WMI transports, per-tool adapters, phase-gated catalog, proper `jobs.session_id` column, scope re-check on session target.

## 8. What this document does not answer

1. **Multi-session objectives.** "Enumerate all sessions" — the planner sees multiple `msf_session` findings and must iterate. The current single-action-per-step loop can do this, but the dedup guard will reject the second `msf_sysinfo` on a *different* session. Needs a dedup rule that treats `(tool_id, session_id)` as the uniqueness key, not `(tool_id, target)`.
2. **Session output size.** `sysinfo` on a Linux target is small. `hashdump` on a domain controller is megabytes. The current adapter contract assumes a `list[str]` of lines. Large output needs a cap or a streaming path.
3. **Long-running session tools.** `portfwd` and some post modules run indefinitely. The current `session_exec` has a 15-second timeout with a quiet-period heuristic. Tools that legitimately take minutes need a separate execution mode.
4. **Session errors vs. tool errors.** When the session dies mid-command, the output is an error string indistinguishable from a tool that produced no output. Needs a structured error channel.
5. **Interaction with `msf_tracker`.** The tracker fires `SessionClosed` when the session disappears. If the executor proposed a session action at the same instant, race conditions are possible. Needs a lock or an "is session alive" re-check between proposal and execution.
6. **The web UI.** `POST /api/msf/sessions/<id>/exec` already exists and works. Wiring it into the *job* model (as opposed to a raw exec) is a separate design.

## 9. What ships in v1 vs. what waits

**v1 (this design, ~4 sessions):**

- Session-scoped tool transport in the catalog and the runner
- `Action.session_id`
- `SessionAdapter` dispatching to existing MSF parsers
- Three built-in session tools (`sysinfo`, `getuid`, `hashdump`)
- Executor session branch with `session_check`
- CLI: `whaxon run msf_sysinfo session:3`
- Planner can see and propose session-scoped tools

**v2 (later):**

- SSH/SMB/WMI transports
- Per-tool adapters
- Phase-gated catalog
- Proper `jobs.session_id` column
- Scope re-check on session target
- Report integration for phase → session correlation

**v3 (Phase E.2):**

- Tools that run *through* a pivot (`portfwd` + host-scoped tools combined)
- Multi-session objectives

**Never in scope:**

- Sessions as a way to bypass scope
- Persisting on target systems beyond the engagement window
- Anything the MSF session model does not natively support

## 10. SMB and WMI transports (v2 design note)

SSH landed in v0.4.x as the second transport (`transport="ssh"`, session id format `ssh:user@host[:port]`). The pattern generalizes: a transport is any runner path that takes a session id and produces stdout-shaped output.

**SMB.** `impacket` already ships in the WHAXON optional deps. A `transport="smb"` tool would shell out to `impacket-smbclient` or `impacket-wmiexec` with the same `session_id` shape used for SSH (`smb:user:pass@host`). The runner's `_run_ssh_session` pattern (subprocess with auth args, scope check on the extracted host) maps directly.

Key open questions for the SMB design:
- **Credential handling.** SSH relies on the user's pre-existing key agent. SMB needs credentials passed in — either via env vars at session start or embedded in the session id. The latter is a security smell (credentials in strings that get logged). Recommend: session id is `smb:user@host`, credentials come from a separate env var (`WHAXON_SMB_PASS`) scoped to the runner process.
- **Pass-the-hash.** Impacket supports PTH directly. The session id could encode `smb:user@host#nthash` but that's the same logging problem. Defer to a credentials store, not the session id.
- **Output parsing.** impacket tools emit unstructured text. Existing impacket adapter (`adapters/impacket.py`) already has SAM/SMB parsing that could be reused.

**WMI.** Same shape as SMB — impacket's `wmiexec` and `atexec` produce stdout. Session id `wmi:user@host`, credentials from env. Functionally identical to SMB for our purposes; the same runner helper handles both.

**Effort estimate.** Two full sessions: one for SMB (runner path + adapter reuse + tests), one for WMI (much smaller, mostly copy-paste from SMB). Both blocked on a live SMB target for end-to-end verification, same blocker as the MSF session path.

**Not in scope for either:** interactive shells. The runner is command-in, output-out. Anything requiring a stateful interactive session (meterpreter, ssh interactive) is a different abstraction and would need a session-object model, not the current session-id-as-string model.

## 11. Phase E.2 — tools through a pivot (v2 design note)

The vision doc calls this the "next architectural gap" after session-based execution. It is.

**The problem.** A pivot is a route: `localhost:1080 -> session 3 -> target:22`. Once a pivot exists, a host-scoped tool (nmap, nikto) should be able to run *as if* it were on the far side of the tunnel. Currently the runner has no concept of this — `run_tool` executes on the local machine only, against whatever host it can reach.

**Why it's hard.**
- **Scope semantics.** Is the destination host in scope? It must pass `ScopeManager.check()` even though it's reachable only via the pivot. Yes — that check already exists and runs.
- **Which runner path?** Either (a) the pivot exposes a SOCKS proxy on localhost and host-scoped tools get a `--proxy` env var; or (b) the pivot forwards a specific port and the tool is pointed at `localhost:<forwarded>`.
- **Finding the right pivot.** For a given target host, which session/forward reaches it? `pivot.py` has the graph edges but no route resolver.
- **Reporting.** A finding produced through a pivot should be attributed to the target, not the pivot host. The `target` label in the job record needs to be the final host, with pivot metadata elsewhere.

**Proposed shape.**

Option (a) — SOCKS proxy:
- `MSFClient` gains `start_socks_proxy(session_id, lport)` using `socks_proxy` post module.
- The runner sets `ALL_PROXY=socks5://127.0.0.1:<lport>` in the tool's env when a pivot route exists.
- Many CLI tools honour `ALL_PROXY` (curl, some HTTP tools); most do not (nmap, nikto). So this only works for a subset.

Option (b) — port-forward per service:
- `portfwd` already exists (`core/portfwd.py`). A route is `(target_host, target_port) -> local_forward_port`.
- The runner rewrites the tool's `target` argument from `target_host` to `127.0.0.1:<forwarded_port>` for tools that accept a port. For tools that don't (nmap service scan), harder.
- Works for HTTP-focused tools (nikto, gobuster, ffuf, nuclei, sqlmap). Doesn't work for nmap.

**Recommendation.** Ship (b), scope it to HTTP tools. Document the limitation. nmap through a pivot is genuinely hard and probably out of scope.

**New abstraction needed.** A route resolver:
Populated from `portfwd` state + `pivot.py` graph. The runner consults it, rewrites `target`, tags the job with the original host.

**Effort estimate.** Three sessions. Session 1: route resolver + `portfwd` state integration. Session 2: runner integration for HTTP tools. Session 3: report tagging, tests, docs.

**Not in scope.** Tools that don't play well with a forwarded port (nmap full scan). Any interactive-through-pivot path.


---

## Part 5 — METASPLOIT_ARMITAGE_ENGINE_INTEGRATION.md

> **Status (2026-11-02): PROPOSED INTEGRATION DESIGN — PARTIAL IMPLEMENTATION ONLY.** WHAXON currently contains Metasploit RPC, module/session, adapter and pivot-related code, but this document's broader module-family, payload/handler, data, collaboration and Engine v2 acceptance matrix is not a statement that all those capabilities are shipped or tested. Check current source/tests and roadmap §§49–51 for the exact implemented subset and remaining gates.

# Metasploit and Armitage — Engine Integration Design

**Status:** Architecture and roadmap requirement; design approved for implementation planning, not yet implemented.  
**Repository:** `andreipath26/WHAXON-AI-Forensics`  
**Architecture parent:** `docs/ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md`  
**Roadmap parent:** `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md`, §51  
**Baseline:** E0 static inventory at commit `71c3e8c2b73bf7f05bd0e064fa77c4aa81113802`.

## 1. Product objective

Make the installed Metasploit Framework a first-class, dynamically discovered execution provider for WHAXON. WHAXON must be able to understand and orchestrate the supported capabilities of the actual connected Framework instance, not just call a narrow set of exploit, auxiliary and post modules.

Metasploit supplies the extensible security-testing and execution framework. Armitage contributes proven operator-workflow ideas: host/session visualization, attack candidate discovery, contextual session operations, pivot awareness and collaboration/deconfliction. WHAXON must combine those ideas with its own mission engine, deterministic authorization, evidence, verification, scheduler and supplied UI.

**Division of responsibility:**
- Metasploit owns its native modules, module semantics, Framework jobs, consoles, sessions, payload/handler mechanisms, plugins and native data.
- WHAXON owns mission intent, scope, policy, approvals, task graphs, provider selection, budgets, durable orchestration, evidence provenance, verification, reporting and operator experience.
- Armitage is a design reference, not a runtime dependency or a UI to clone.
- Metasploit Pro-only capabilities must never be assumed to exist in the open-source Framework. Detect edition and API capability, and implement WHAXON-native equivalents only where justified.

## 2. Architectural placement

Metasploit is a provider under Engine v2, not a second orchestration engine and not a collection of hard-coded entries in `data/tools.json`.

Target flow:

```text
CLI / supplied Web UI / API / headless
                |
        Shared application services
                |
          Mission Engine
   Plan -> Policy -> Approval -> Budget
                |
       Durable task scheduler
                |
     Capability / provider resolver
                |
        Metasploit provider
   +------------+-------------+
   |            |             |
Module       Runtime       Session &
intelligence lifecycle     maneuver
   |            |             |
   +------ Framework data ----+
                |
       Version-aware RPC bridge
                |
       Metasploit Framework
                |
   Events / observations / artifacts
                |
   WHAXON evidence + verification
                |
    mission graph / attack-surface view
```

The provider must use the existing versioned Engine v2 contracts: `Mission`, `AuthorizationContext`, `Plan`, `Task`, `Attempt`, `Manifest`, `Provider`, `PolicyDecision`, `Approval`, `Budget`, `ExecutionContext`, `Observation`, `Verification`, `Evidence`, `Audit` and `Readiness`.

The provider is responsible for adapting Framework-specific identifiers and semantics to these contracts. It must not bypass the shared scheduler, scope gate, policy engine, approval binding, audit or evidence service.

## 3. Framework capability coverage

Capability discovery is performed against the connected Framework version and actual RPC/API surface. No fixed module counts, static allowlists pretending to represent the installation, or assumptions that every version exposes identical methods.

### 3.1 Module families and intelligence

Discover and represent all installed and API-supported module families:
- auxiliary;
- exploit;
- post;
- payload;
- encoder;
- NOP;
- evasion.

For each module, capture a versioned metadata snapshot containing:
- canonical module type and full name;
- description, authors, references/CVEs and disclosure metadata where supplied;
- rank, reliability/stability/side-effect metadata where supplied;
- supported platform, architecture and target list;
- required, optional, advanced and evasion options, types, defaults and constraints;
- check support and check result semantics;
- compatible payloads and target-compatible payloads;
- compatible session types for post modules;
- prerequisites, dependencies and Framework version constraints;
- provider-reported availability and metadata retrieval time.

Module metadata is advisory input, not authorization. A high rank or successful check does not authorize execution. Unknown or conflicting metadata must be treated conservatively.

### 3.2 Module search, recommendation and validation

Provide structured search and filtering across module families, references, CVEs, platform, architecture, service/product, target compatibility and capabilities.

Build an Armitage-inspired **Find Attacks** workflow, extended beyond simple service-to-exploit matching:
1. correlate WHAXON asset/service observations and their confidence/provenance;
2. discover matching Framework modules and non-Metasploit validation providers;
3. check platform, version, target, options, prerequisites and compatible payload/session requirements;
4. distinguish confirmed evidence, plausible match and weak fingerprint correlation;
5. identify safe checks or independent non-invasive verification methods where available;
6. present candidates with reasons, limitations, impact class and missing information;
7. require policy evaluation and approval before any consequential action;
8. record the actual result and update the asset/vulnerability knowledge graph.

A module existing or matching a service banner is never proof that a vulnerability exists. A module's `check` method may be incomplete, unsupported or inconclusive; its result must be represented with those limitations and independently corroborated where possible.

### 3.3 Execution, jobs and consoles

Replace fixed sleeps and console-text parsing as the normal lifecycle mechanism with structured RPC methods wherever available.

Required operations:
- validate and prepare a module request;
- dispatch and persist Framework job/console identifiers;
- list, inspect, wait for and stop jobs;
- collect structured progress/output and bounded console output;
- classify success, failure, timeout, cancellation and unknown outcome;
- create, own, interact with, detach and destroy consoles;
- enforce concurrency, resource limits, output caps and deadlines;
- reconcile jobs after WHAXON restart before any retry;
- preserve the exact module metadata snapshot, normalized options and task-attempt association.

A lost RPC response after dispatch is an **unknown outcome**, not proof that the operation did not start. Reconcile Framework jobs, sessions and events before deciding whether retry is safe. Exploit and handler operations must never be blindly replayed.

Console interaction remains a bounded compatibility path for features without a supported structured API. It must have explicit ownership, command allowlisting or typed wrappers, output limits, timeout, audit and authorization. It must not become a free-form command path for the AI planner.

### 3.4 Payload and handler lifecycle

Model payloads and handlers as distinct capabilities with explicit relationships:
- staged/single payload semantics and platform/architecture compatibility;
- compatible payload selection for a particular module and target;
- handler configuration, start, status, stop and cleanup;
- correlation between module execution, handler, Framework job and resulting session;
- cleanup and orphan detection following failure or cancellation.

Payload generation, delivery, handler deployment and session establishment are consequential operations and must be separately authorized. A handler's listener configuration must be constrained to approved interfaces/ports and deployment policy.

### 3.5 Sessions and Meterpreter

A session is a durable Framework resource, not merely an integer ID or command string.

Session identity must include:
- Framework instance ID and Framework version;
- Framework-local session ID and stable UUID where available;
- type, platform, architecture and transport/tunnel metadata;
- peer/target host, local endpoint and route ancestry;
- originating module, payload, job and WHAXON task/attempt;
- user/privilege context where safely available;
- creation, last-seen and lifecycle state;
- discovered capabilities/extensions and their provenance.

Discover session capabilities by session type, platform, Framework version and loaded extensions. Provide typed operations where supported for:
- system and identity information;
- filesystem metadata and explicitly authorized file collection;
- process inventory and bounded process interaction;
- network interfaces, routes and connection information;
- channels and interactive I/O;
- supported Meterpreter extension capabilities;
- shell command execution as a separate, lower-level compatibility operation;
- session backgrounding, interaction and termination.

Do not conflate shell commands with Meterpreter APIs. Long-running operations require streaming, cancellation, output caps and durable ownership. Revalidate live session identity, host, route ancestry, task ownership and scope immediately before every consequential operation. An unknown or changed peer/host must fail closed.

### 3.6 Framework data and artifacts

Integrate supported Framework database services and records:
- workspaces/projects where exposed;
- hosts and host attributes;
- services and observed versions;
- vulnerabilities and references;
- credentials and login records;
- loot and artifact metadata;
- notes and other supported records.

WHAXON remains the canonical mission/evidence authority. Preserve Framework source IDs, workspace, instance identity, timestamps and original provenance. Use idempotent synchronization and explicit conflict rules; never overwrite stronger WHAXON evidence with weaker imported data.

Credentials and secrets must be stored as protected secret references, not copied into plans, ordinary logs, UI payloads or unredacted reports. Loot ingestion must record source, size, media type, integrity hash, access policy and retention classification. Do not silently collect or exfiltrate arbitrary files.

### 3.7 Pivoting and network maneuver

Extend the existing pivot, route and port-forward components into one route-aware network model. Represent:
- pivot session and Framework instance;
- route/subnet and forwarding mechanism;
- local/remote endpoints and protocol;
- route ancestry and path to destination;
- creation owner/task, policy decision and approval;
- health, expiry, teardown and last validation.

Include supported port-forward and SOCKS capabilities only after API/version discovery. Validate authorization both when creating a route and when using it. A route through an authorized foothold does not automatically authorize the newly reachable subnet. DNS resolution, redirects and actual network destination must remain bound to the approved scope; this integrates with Engine v2's DNS/TOCTOU controls.

### 3.8 Plugins and extensibility

Discover installed Framework plugins and their exposed capabilities, but do not load or execute arbitrary plugins automatically. Plugin installation/loading is an administrative operation with explicit trust, version, provenance and approval.

New Metasploit capabilities should be added by manifests/provider adapters, not changes to the mission engine or scheduler. Support version-specific adapters and capability negotiation. Unsupported methods must be reported explicitly.

## 4. Armitage patterns to adopt

### 4.1 Attack-surface and session graph

Extend WHAXON's existing asset and pivot graph rather than create a duplicate graph. Represent hosts, services, findings, Framework instances, jobs, sessions, handlers and routes as linked entities. Preserve provenance and confidence for each edge.

Provide graph and table projections from the same canonical data model. Graph selection should expose contextual, policy-filtered operations; it must not bypass the planner or authorization service.

### 4.2 Find Attacks

Adopt Armitage's host/service-to-module recommendation concept, but improve it with evidence quality, module compatibility, check availability, impact classification, alternative validation methods, policy decisions and explainable recommendations. Recommendations are not automatic dispatch.

### 4.3 Contextual session operations

Use session type and discovered capability to show relevant operations. The UI must not show actions the backend/provider cannot actually perform. Every operation uses shared application services and the same approval, task and evidence lifecycle.

### 4.4 Pivot awareness

Display how routes change reachability and which session provides each path. Route reachability is not scope authorization. Re-evaluate the route and destination before execution.

### 4.5 Collaboration and deconfliction

Armitage's shared-session/deconfliction concept should inform a future multi-operator design. Engine v2 should establish session leases/locks, operation ownership, command serialization where required, shared event streams and conflict detection. This is a future capability; do not add distributed collaboration complexity before the solo durable scheduler is correct.

### 4.6 UI integration constraint

Do not clone Armitage's Java UI, introduce a second UI, or redesign the supplied WHAXON UI. Add backend contracts and connect only existing supplied UI pages/components when the relevant functionality is truly implemented. Hide unavailable capabilities rather than showing mock controls. Keep the legacy UI untouched.

## 5. AI, automation and playbooks

AI may propose module candidates, task graphs, parameter suggestions and follow-up work. It may not directly issue unrestricted RPC calls, console commands, shell strings or Meterpreter commands.

Every proposed action must become a typed task and pass:
- schema and module-option validation;
- deterministic scope and target authorization;
- customer engagement or bug-bounty policy;
- operation/module/session risk classification;
- impact, rate, time and resource budgets;
- approval bound to immutable plan/task digest, target, parameters, Framework version, policy version and expiry;
- runtime revalidation at dispatch and on session/route actions.

Replace fixed `WHAXON_MSF_AUTOCHAIN` behavior and its hard-coded post-module list with declarative, evidence-driven graph transitions. A newly created session may trigger discovery and recommendations, but must not silently trigger post-exploitation. Every follow-up task is independently authorized. Bounty policy remains separate from customer-pentest policy; a program prohibition overrides Framework capability.

Playbooks should be reusable, versioned task-graph templates with typed parameters, preconditions, policy requirements, rollback/cleanup behavior and evidence expectations. They should support partial completion and safe resume, not a blind linear macro.

## 6. MCP and external interoperability

Keep the native WHAXON provider as the source of truth. Evaluate MCP as an optional interoperability surface for selected, already-authorized WHAXON capabilities and for compatible external clients. MCP tools must call the same application services and policy gates; they must not expose a second bypass around them.

Before depending on any Metasploit MCP server, verify its current maintainer, release status, supported Framework versions, tool coverage, authentication, transport security and dangerous-action defaults. Treat it as an optional adapter, not as a replacement for full provider coverage or durable orchestration.

## 7. Security and deployment requirements

- Remove weak built-in RPC credentials; require explicit secret configuration.
- Verify TLS certificates and hostnames by default. Insecure TLS is explicit development-only configuration, visibly warned and rejected by production policy.
- Prefer loopback/private network binding; remote RPC is opt-in, authenticated, network-restricted and encrypted.
- Store credentials in secret references and rotate them without exposing values.
- Enforce least privilege and Framework instance identity.
- Revalidate target/session/route scope immediately before dispatch.
- Enforce per-operation side-effect classifications; unknown impact is denied or requires human review.
- Keep customer and bounty policies independent.
- Record auditable plan, approval, RPC operation, job/session/handler, route, output and evidence correlations.
- Support optional Framework absence, truthful readiness and dependency diagnostics.
- Support headless Linux/server deployments with no GUI, desktop or interactive console requirement.
- Bound RPC timeouts, output size, concurrency, memory and orphan cleanup.

## 8. Implementation gates and sequence

This work is subordinate to roadmap §0 and the Engine v2 E1–E9 dependency sequence. It must not bypass the supplied UI gate or solo v1.0 acceptance.

| Engine stage | Metasploit deliverable | Exit condition |
|---|---|---|
| E1 — correctness/security | TLS/auth defaults, session-host authorization, RPC error handling, blocking/fixed-wait correctness, scope/route validation, regression tests | Critical security and lifecycle defects closed |
| E2 — contracts | Framework instance, module metadata, option schema, job, console, handler, session, route, loot, secret and readiness contracts | Versioned contracts and compatibility tests |
| E3 — durable runtime | Job/session/handler ownership, leases, heartbeats, event correlation, cancellation, restart reconciliation | No duplicate replay; recoverable operations |
| E4 — provider/capabilities | Dynamic discovery, search, metadata, compatibility, module families, typed session and database services | New capability added without scheduler changes |
| E5 — shared services/headless | CLI/API/UI/headless access through same services | Same policy and lifecycle across interfaces |
| E6 — solo v1.0/UI | Expose only implemented Metasploit functions in supplied UI; accurate readiness and diagnostics | UI and release acceptance |
| E7 — bounded autonomy | Find Attacks, explainable recommendations, safe checks, declarative follow-ups/playbooks | Adversarial policy and evidence acceptance |
| E8/E9 — scale/expansion | Multi-target fan-out, multiple Framework instances, deconfliction/collaboration | Measured concurrency and isolation acceptance |

Do not start broad feature implementation before E1 security and recovery gates are closed. Parallel work is permitted only where contracts and ownership boundaries are stable.

## 9. Acceptance matrix

1. Detect Framework version, edition where determinable, API namespaces and actual module-family availability.
2. Search and retrieve metadata for each supported module family without hard-coded module totals.
3. Retrieve required/advanced options, targets, references, check support and compatible payload/session data.
4. Validate options and reject incompatible or incomplete requests before dispatch.
5. Execute approved lab auxiliary and exploit test cases; track structured job state to terminal outcome without fixed sleeps.
6. Start/stop a handler and correlate it to the originating task and any resulting session.
7. Discover shell and Meterpreter sessions and verify typed capability discovery.
8. Exercise bounded session operations, streaming, timeout, cancellation and closure in an isolated lab.
9. Import and reconcile supported host/service/vulnerability/credential/loot records with source provenance and secret redaction.
10. Create, inspect and tear down supported forwards/routes; prove route use cannot exceed scope.
11. Restart WHAXON during a Framework job/session and reconcile state without duplicate dispatch.
12. Prove unknown, prohibited, out-of-scope and unapproved module/session/route actions are denied, including AI-proposed actions.
13. Prove customer and bounty policy differences are enforced.
14. Prove TLS verification, secret storage, authentication failures and unsafe remote configurations are handled correctly.
15. Run headlessly without desktop dependencies and report optional dependency readiness truthfully.
16. Verify all UI exposure uses existing supplied design and hides unsupported capabilities.
17. Add a provider capability without changing mission engine, scheduler or evidence core.
18. Verify Framework/Pro-only features are not falsely advertised as open-source Framework capabilities.

## 10. Research references

The following primary references informed this design. API behavior must still be verified against the actual installed Framework version during implementation.

- Rapid7, [Metasploit RPC API](https://docs.rapid7.com/metasploit/rpc-api/) — RPC services, handlers, authentication and Framework connectivity.
- Rapid7, [Standard API Methods Reference](https://docs.rapid7.com/metasploit/standard-api-methods-reference/) — module execution and structured job/session methods.
- Rapid7, [Metasploit Framework overview](https://docs.rapid7.com/metasploit/msf-overview/) — module families and Framework concepts.
- Rapid7, [Metasploit codebase architecture](https://docs.metasploit.com/docs/development/get-started/navigating-and-understanding-metasploits-codebase.html) — modules, libraries, plugins and scripts.
- Rapid7, [How payloads work](https://docs.metasploit.com/docs/using-metasploit/basics/how-payloads-work.html) — staged/single payloads and handler relationship.
- Rapid7, [Running modules](https://docs.metasploit.com/docs/using-metasploit/basics/using-metasploit.html) — module search and execution concepts.
- Rapid7, [MessagePack RPC guide](https://github.com/rapid7/metasploit-framework/blob/master/docs/metasploit-framework.wiki/How-to-use-Metasploit-Messagepack-RPC.md) — Framework RPC usage.
- Armitage, [source repository](https://github.com/rsmudge/armitage) — original client and workflow reference. Armitage-derived features must be re-evaluated against current WHAXON requirements rather than copied wholesale.



---

## Part 6 — TOOL_INTELLIGENCE_AND_ONBOARDING.md

> **Status (2026-11-02): PROPOSED SUBSYSTEM DESIGN — NOT A SHIPPED TOOL-INTELLIGENCE PRODUCT.** This document defines a desired source-backed portfolio audit and candidate-onboarding workflow. Existing tool catalog, adapters, dependency diagnostics and capability contracts are foundations, not proof that the full discovery/research/reporting lifecycle exists. Use roadmap §52 and current source/tests for implementation status.

# WHAXON Tool Intelligence & Controlled Onboarding

**Status:** Architecture specification — implementation queued behind Engine v2 dependency gates  
**Scope:** andreipath26/WHAXON-AI-Forensics  
**Authority:** Roadmap §0 and §52; Engine v2 architecture crosswalk

## 1. Purpose

WHAXON needs a repeatable way to understand tools it already integrates and tools it may add later. A catalog entry or adapter is not proof that WHAXON exposes the upstream tool's full capability set. An upstream feature is not proof that WHAXON implements, validates or is permitted to execute it.

Tool Intelligence provides two entry points:
- **Audit portfolio:** inspect installed/registered tools, adapters, transports and providers; compare upstream functionality with WHAXON's actual implementation and verification.
- **Research candidate:** investigate a proposed tool from authoritative sources; determine distinct value, overlap, integration cost, risk and a controlled onboarding path.

The subsystem produces evidence-backed reports and proposals. It does not silently expand execution authority.

## 2. Architectural placement

Tool Intelligence belongs beside the Engine v2 capability registry and provider resolver. It is not a replacement and must not create a parallel manifest, scheduler, policy engine or execution path.

Portfolio audit and candidate intake share:
discovery → source research → capability extraction → normalization → gap/overlap analysis → compatibility/risk assessment → versioned report → operator decision → integration → validation.

The implementation may split responsibilities into modules for discovery, research, documentation ingestion, extraction, gap analysis, compatibility, risk, onboarding and reports. These are logical boundaries, not a mandate to create every file independently.

## 3. Shared pipeline

### 3.1 Discovery

For the existing portfolio, collect:
- catalog records and aliases;
- built-in and entry-point adapters;
- session transports, RPC integrations and non-CLI providers;
- executable identity/version and bounded readiness checks;
- dispatch wiring, parser/normalizer, evidence path and interface exposure;
- tests and the exact version/platform they cover.

For a candidate, capture canonical identity, publisher, official repository/docs, release channel and candidate version. Discovery must not operationally exercise the candidate.

### 3.2 Source-backed research

Prioritise official documentation and API specifications, official source/tagged releases, release notes/advisories/support matrices, maintainer statements and authoritative package metadata. Community sources are supplementary and labelled as such.

Record URL, source type, retrieval date, relevant version, extracted claim, confidence and contradictions. Unknown claims remain unknown. Research licensing, redistribution, maintenance, supported platforms, dependency footprint, privilege, credential model, remote services and supply-chain risks.

### 3.3 Capability extraction and normalization

Extract capabilities into the existing Engine v2 model with stable IDs independent of executable names. Record version/edition constraints and source provenance for each material claim.

Useful sources include CLI version/help/subcommand and documented machine-readable introspection; REST/OpenAPI descriptions and authentication schemes; JSON Schema; MCP tools/list metadata; Python package metadata/entry points; plugin/module inventories; and CycloneDX SBOM/component metadata.

These are evidence sources, not trust roots. MCP annotations are hints, not authorization. OpenAPI/JSON Schema describes an interface but does not prove safe behavior or WHAXON implementation. CycloneDX complements but does not replace the capability manifest.

### 3.4 Gap and overlap analysis

For every upstream capability, classify WHAXON status as absent; implemented but not registered; registered but not dispatchable; dispatchable but not exposed; partial; implemented but untested; tested in a named environment/version; verified and ready; intentionally excluded; deprecated or incompatible.

Identify duplicate capabilities, existing alternatives, migration impact, parser/evidence gaps and distinct value. Never count an upstream feature as a WHAXON feature merely because the tool supports it.

### 3.5 Compatibility and risk

Assess runtime and OS/architecture support, target/protocol coverage, authentication, session/transport model, dependencies, licensing, maintenance, API stability, concurrency, resource use, cancellation, idempotency, output stability and evidence quality.

Classify side effects and impact. Unknown impact or uncertain authorization is denied or sent for explicit review. Candidate safety labels are untrusted until independently checked.

## 4. Capability manifest additions

Extend the canonical Engine v2 manifest; do not create a second schema.

| Dimension | Required information |
|---|---|
| Identity | Stable provider/tool ID, publisher, upstream repository, version and supported range |
| Capability | Stable capability ID, operation, family and deprecation |
| Interface | CLI, library, REST/OpenAPI, RPC, MCP, plugin, session or other transport |
| Schemas | Versioned typed inputs/outputs, validation and compatibility |
| Applicability | Targets, protocols, platforms, architectures, authentication/session requirements |
| Prerequisites | Dependencies, permissions, environment and secret references |
| Behavior | Preconditions, postconditions, state changes, external effects and impact |
| Execution | Timeout, cancellation, concurrency, resource/rate limits, idempotency and reconciliation |
| Evidence | Raw formats, parser/normalizer versions, provenance, redaction and retention |
| Readiness | Capability-specific state, environment, verification time and evidence |
| Provenance | Source URLs/version, retrieval time, confidence and deprecation |

Suggested readiness states: discovered, researched, installed, registered, smoke-tested, lab-validated, verified, degraded and unsupported. Attach readiness to a capability and environment/version. A tool-level available boolean is insufficient.

**Trust invariant:** a manifest describes a capability; it never grants permission. Engagement/bounty policy and runtime authorization remain separate and deterministic.

## 5. Tool Capability Report

Each assessment creates an immutable, versioned report; revisions supersede rather than overwrite. Include:
1. Executive decision and assessment scope.
2. Identity, version, publisher and provenance.
3. Source-backed upstream capability inventory.
4. WHAXON catalog/provider/adapter/dispatch/exposure inventory.
5. Gap and overlap matrix.
6. Compatibility, prerequisites, licensing and maintenance.
7. Security, side-effect, privilege, credential and data-handling assessment.
8. Evidence/parser/normalization implications.
9. Required code, schema, migration and service/UI changes.
10. Test and controlled-lab plan.
11. Recommendation: integrate, extend, replace, defer, reject or investigate.
12. Unknowns, confidence and acceptance criteria.

Explicitly separate upstream capability, WHAXON implementation, WHAXON verification/readiness and current authorization to execute.

## 6. Existing portfolio reconciliation

The first audit reconciles data/tools.json; built-in and Python entry-point adapters in adapters/registry.py; adapters/base.py; actual runner dispatch and dependency checks; session transports/RPC providers; CLI/API/UI exposure; parser/evidence paths; and tests.

Detect catalog-only, adapter-only, duplicate, stale, missing-binary, unsupported-transport, unreachable-dispatch, parser-gap and advertised-but-unverified cases. Preliminary baseline inspection found catalog/adapter discrepancies; E4 must generate the complete mismatch set rather than assume counts from a partial inspection.

Migration is additive and compatibility-preserving. Keep ToolCatalog, existing parsers and ToolRunner behind a bridge until manifest-backed provider resolution passes regression tests. Do not silently drop or rename definitions.

## 7. Candidate onboarding lifecycle

Persist explicit states:

| State | Meaning |
|---|---|
| proposed | Candidate and reason recorded |
| researched | Source-backed upstream/operational research completed |
| assessed | Gap, overlap, compatibility and risk completed |
| approved_for_implementation | Operator accepts bounded proposal; not installation/execution permission |
| integrated | Provider, schemas, parser/evidence path and service wiring implemented |
| validated | Declared tests passed with environment/version evidence |
| enabled | Available for deterministic resolution, still subject to runtime policy |
| rejected | Declined with rationale |
| deprecated | Retired with migration/replacement details |

Record actor, timestamp, report version, decision and evidence on every transition. Approval for implementation is not approval to install, load plugins, use credentials or execute. Decisions are revocable. Material upstream changes trigger reassessment and may invalidate readiness.

## 8. Safe discovery and operational boundary

Discovery is read-only and bounded: inspect local metadata, entry points, executable identity/version and documented help/list commands; use allowlisted introspection with timeout/output/resource limits; research public docs, source, releases, advisories and licensing.

Discovery must not run scans, exploits, listeners, post-exploitation, arbitrary RPC/session commands or downloaded code; install/upgrade packages; load/enable plugins; use credentials; contact arbitrary endpoints; or alter system state.

Each later install, plugin load, credential use, networked test or consequential validation needs separate explicit approval, a bounded plan and deterministic policy authorization. Remote descriptions, MCP annotations, schemas and generated manifests are untrusted. AI can extract and recommend, not authorize, enable or execute.

## 9. Continuous upstream monitoring

After provenance and registry contracts stabilize, compare releases, version support, capability additions/removals/deprecations, API/schema/output changes, plugins, advisories, ownership/maintenance, platform and licensing changes.

Create versioned delta reports and proposed manifest/parser/test updates. Never auto-upgrade, change provider selection, load plugins, enable or execute. Affected readiness becomes stale until revalidated.

## 10. Dependencies and implementation sequence

| Stage | Work | Gate |
|---|---|---|
| Architecture | Specify pipeline, trust boundary, report and acceptance | No competing contracts |
| E1 | Close current correctness/security blockers | Scope, DNS, session, RPC/TLS, recovery and evidence safety |
| E2 | Define manifest, provenance, readiness, report and lifecycle contracts | Shared versioned domain model and compatibility façade |
| E3 | Persist reports/lifecycle events; later schedule monitoring | Durable leases, idempotency, cancellation and recovery |
| E4 | Reconcile portfolio; migrate manifests; local discovery, extraction and gap analysis | Deterministic registry/provider resolution and regression |
| E4/E5 | Candidate research and operator-reviewed onboarding | Shared services and auditable transitions |
| After registry stabilizes | Upstream monitoring and revalidation | Provenance, readiness and durable scheduler |
| E6 onward | Expose only implemented, verified, authorized capabilities | Supplied UI and release gates |

Do not move ahead of E1, bypass E2/E3 contracts, delay solo v1.0/UI work, or introduce a second scheduler/manifest/policy implementation.

## 11. Proposed logical module boundaries

Possible modules:
- intelligence/discovery.py — safe local portfolio discovery;
- intelligence/research.py — source collection and version-aware research;
- intelligence/documentation.py — docs/spec ingestion and provenance;
- intelligence/capability_extractor.py — normalized capability claims;
- intelligence/gap_analyzer.py — upstream/WHAXON comparison;
- intelligence/compatibility.py — platform/version/schema fit;
- intelligence/risk_assessment.py — side effects, privilege and trust;
- intelligence/onboarding.py — persisted candidate lifecycle and decisions;
- intelligence/reports.py — versioned reports and deltas.

Exact paths are implementation decisions. Modules consume canonical contracts and shared services; they do not own execution, authorization, scheduling or a second registry.

## 12. Acceptance test matrix

- Full reconciliation across catalog, adapters, transports, dispatch, interfaces and tests.
- Detection of catalog-only, adapter-only, duplicate, stale and unreachable entries.
- Safe discovery without operational execution or system mutation.
- Reproducible reports from versioned source-backed evidence.
- Explicit upstream/implemented/tested/authorized separation.
- Compatibility and licensing/maintenance risk detection.
- Malicious descriptions, malformed schemas, prompt injection and untrusted annotations cannot execute or grant permission.
- No automatic install, upgrade, plugin load, credential use or operational invocation.
- Auditable/revocable transitions and stale-report invalidation.
- Upstream drift reports without runtime changes.
- New provider registration without mission, policy, scheduler or evidence core rewrites.
- Existing catalog, adapter, runner, CLI/API and end-to-end regressions remain green.

## 13. Definition of done

An operator can audit the current portfolio or assess a new candidate and receive a reproducible, source-backed capability, gap, compatibility and risk report with an implementation proposal. Approved providers are integrated and validated through the same versioned Engine v2 contracts as existing and future tools. Discovery never silently becomes executable authority.


---

## Part 7 — adapters.md

# Writing an Adapter

An adapter parses tool output into structured `Finding` objects. The runner executes the tool; the adapter must not launch a second process.

**Adding an adapter inside WHAXON:** use this guide. **Shipping an adapter as a separate Python package:** use [Plugins](#part-9--pluginsmd).

## Adapter contract

`whaxon.adapters.base.Adapter` is an abstract base class with one required method, `parse`:

```python
from whaxon.adapters.base import Adapter
from whaxon.core.findings import Finding


class MyAdapter(Adapter):
    tool_id = "mytool"  # must match the catalog tool id

    def parse(self, lines, ctx=None) -> list[Finding]:
        findings = []
        for stream, text in lines:
            if stream != "stdout":
                continue
            # Parse the line and append Finding(...) objects.
        return findings
```

The runner supplies `lines` as a list of `(stream, text)` tuples; `stream` is `"stdout"` or `"stderr"`. The optional `ctx` dictionary may contain `tool_id`, `target`, `extra_args` and the executed `argv`.

## Finding fields

The `Finding` dataclass accepts:

- `kind`, `severity`, `source`, `data` — required structured fields.
- `raw_line` — original source line; the dataclass does not impose a universal truncation limit.
- `remediation`, `impact`, `cvss`, `cwe`, `references` — optional enrichment.
- `lookup_hint` — optional search hint for a later lookup.
- `request_context` — optional request context used by deterministic validation and retest flows.

Keep raw evidence useful but minimize unnecessary sensitive data. Do not assume the persistence or report layer will scrub secrets from a finding.

## Registration

Built-in adapters are imported by `src/whaxon/adapters/registry.py` and self-register by tool ID. To add an in-repository adapter:

1. Implement the adapter in `src/whaxon/adapters/`.
2. Add its module to the registry's built-in autoload list.
3. Ensure its tool ID exists in the effective catalog.
4. Add parser and runner integration tests.

Third-party packages use the `whaxon.adapters` Python entry-point group; see [Plugins](#part-9--pluginsmd). The runtime registry is available through `whaxon.adapters.list_adapters()`.

## Using context

Context can distinguish subcommands that share one catalog tool ID. For example:

```python
def parse(self, lines, ctx=None):
    ctx = ctx or {}
    extra = (ctx.get("extra_args") or "").strip()
    argv = ctx.get("argv") or []
    subtool = extra.split()[0] if extra else (argv[1] if len(argv) > 1 else "")

    if subtool == "secretsdump":
        return self._parse_secretsdump(lines)
    return []
```

See `src/whaxon/adapters/impacket.py` for a concrete multi-command adapter.

## Testing

Test parsers against representative captured output; parser tests should not spawn the external tool.

```bash
python -m pytest tests/test_myadapter.py -v
```

## Built-in adapter modules

The registry's built-in loader currently includes Nmap, Nikto, Burp, SQLmap, Gobuster, ffuf, Nuclei, WPScan, Hashcat, WHOIS, dig, WhatWeb, theHarvester, DNSRecon, Hydra, Metasploit, generic session, SMB session, NetExec, Arjun, WMI session and Commix adapters. The Impacket adapter is imported by the adapters package. The effective registry may skip an adapter whose import fails; inspect `list_adapters()` at runtime rather than treating this source list as proof that every adapter loaded.

## Anti-patterns

- Do not spawn the tool from `parse()`; the runner already executed it.
- Do not mutate the supplied `lines` list.
- Do not swallow parser exceptions or silently turn parse failures into empty findings.
- Do not put credentials or other secrets into finding payloads.


---

## Part 8 — ai.md

# AI Planning and Execution

WHAXON's optional AI subsystem separates **planning** from **execution**. The provider proposes one typed action at a time. The deterministic executor validates the proposal and, when allowed, invokes the existing tool runner. The model itself does not own a process runner, database or scope manager.

AI is disabled by default. With the default `null` provider, a run stops without invoking tools.

## Configuration

Set the master switch and select a provider explicitly:

```bash
export WHAXON_AI_ENABLED=true
export WHAXON_AI_PROVIDER=ollama   # null, rules, ollama, openai, anthropic, google
export WHAXON_AI_MODEL=qwen2.5:1.5b
whaxon ai "assess the explicitly authorized lab target"
```

Provider credentials and model settings are backend-specific:

- Ollama uses `WHAXON_OLLAMA_HOST` (default `http://127.0.0.1:11434`).
- OpenAI uses `OPENAI_API_KEY` and optionally `WHAXON_OPENAI_HOST`.
- Anthropic uses `ANTHROPIC_API_KEY`.
- Google uses `GOOGLE_API_KEY` or `GEMINI_API_KEY`.

`WHAXON_AI_PROVIDER=rules` selects a deterministic rules provider, not an LLM. Unknown provider names fall back to the null provider. Default model names are defined in `src/whaxon/core/ai_bridge.py`; they can change and are not model compatibility guarantees.

## Safety boundary

The planner returns a typed `Action`; it cannot directly invoke a tool. The executor is the only AI path that turns an action into a tool invocation. It checks the catalog and current scope before calling the runner, and records action results. Human questions and stop actions do not invoke tools.

This boundary does not make autonomous execution risk-free. The operator remains responsible for explicit authorization, scope configuration, provider choice, model quality, credentials and review of results. A proposal is not proof that a scan ran; persisted job state and evidence are the record of execution.

## Limits and controls

- `WHAXON_AI_MAX_STEPS` sets the step budget (default 12).
- `WHAXON_AI_MIN_CONFIDENCE` sets the confidence floor for tool proposals (default 0.55).
- The executor also applies a wall-clock limit and deterministic validation.
- Provider responses can be malformed, inaccurate or based on hallucinated targets; validation must reject actions that do not pass policy.
- A cloud provider receives the prompt and context sent to it. Do not send client data to a provider unless the engagement permits it.
- The AI run event stream is available through `GET /api/ai/runs/<run_id>/stream`; this is run-event streaming, not a guarantee that the underlying model streams token-by-token output.

## Audit trail

AI run and step records are persisted in SQLite (`ai_runs` and `ai_run_steps`). The API exposes:

- `GET /api/ai/runs`
- `GET /api/ai/runs/<run_id>`
- `GET /api/ai/pending`
- `POST /api/ai/runs/<run_id>/answer`
- `GET /api/ai/runs/<run_id>/stream`

See the source under `src/whaxon/ai/` and `src/whaxon/core/ai_bridge.py` for the current planner/executor contract.


---

## Part 9 — plugins.md

# Writing a WHAXON Plugin

A WHAXON plugin is a pip-installable package that registers an adapter through the `whaxon.adapters` entry-point group. This lets WHAXON parse output for that tool without modifying the WHAXON package. **The adapter alone does not add a runnable tool to the catalog:** to execute the tool, the operator must also add an authorized catalog entry and install/configure the executable.

This doc is for the case: **you use a tool, WHAXON doesn't parse it,
you want to fix that.** If you want to add an adapter to WHAXON itself
(inside the repo), read [`adapters.md`](#part-9--pluginsmd) instead. That's a
shorter path, but it means maintaining a fork.

## 1. The contract

An adapter is a Python class that:

- Subclasses `whaxon.adapters.base.Adapter`
- Sets `tool_id` to the tool's id (as it appears in `data/tools.json`)
- Implements `parse(lines, ctx=None) -> list[Finding]`

Everything else — the `remediate`, `impact`, `cvss`, `suggest_next_steps`
hooks on the ABC — is optional and has sensible defaults.

```python
from whaxon.adapters.base import Adapter
from whaxon.core.findings import Finding


class MyAdapter(Adapter):
    tool_id = "mytool"

    def parse(self, lines, ctx=None):
        findings = []
        for stream, text in lines:
            if stream != "stdout":
                continue
            # parse text, append Finding(...) objects
        return findings
```

## 2. What `parse` receives

**`lines`** — a list of `(stream, text)` tuples. `stream` is either
`"stdout"` or `"stderr"`. Each tuple is one line of the tool's output,
with the trailing newline stripped.

**`ctx`** — a dict the runner passes through, containing:

| Key | Value |
|-----|-------|
| `tool_id` | The tool id (same as `self.tool_id` in most cases) |
| `target` | The target the operator passed |
| `extra_args` | The raw extra-args string |
| `argv` | The full argv that was executed |

Use `ctx["extra_args"]` when your tool has subtools, e.g.
`impacket-secretsdump` vs. `impacket-smbclient` — the `extra_args` field
distinguishes them, and the adapter can branch on it.

## 3. What a `Finding` is

```python
Finding(
    kind="open_port",              # required; a short classifier
    severity="info",               # required; critical/high/medium/low/info
    source="mytool",               # required; usually the tool id
    data={"port": 80},             # required; structured payload
    raw_line="80/tcp open http",   # original source line; no global truncation guarantee
    remediation="...",             # optional; human-readable fix
    impact="...",                  # optional; business impact
    cvss=5.3,                      # optional; CVSS 3.1 base score
    cwe="CWE-200",                 # optional; CWE id
    references=(),                 # optional; tuple of URLs
    lookup_hint="apache 2.4.7",    # optional; search string for exploit lookup
)
```

**`kind`** is what the correlator keys on. Two adapters that emit findings
with the same `kind` and the same target will be cross-referenced. Common
kinds in the built-in set: `open_port`, `found_path`, `web_issue`,
`vulnerability`, `ntlm_hash`, `smb_share`, `sqli`, `tech_detected`.

**`lookup_hint`** is new (v0.3). Set it when your finding identifies a
versioned service — e.g. `"apache 2.4.7"` or `"openssh 6.6.1"`. WHAXON
will cross-reference it against the local Exploit-DB mirror and print
matches in the engagement report. Leave it empty if the tool doesn't
report a version.

## 4. A worked example: `masscan`

Masscan is a port scanner. Its default text output looks like:

```
Discovered open port 80/tcp on 10.0.0.5
Discovered open port 443/tcp on 10.0.0.5
```

Here's a full plugin that wraps it.

### 4a. Project layout

```
whaxon-masscan/
├── pyproject.toml
├── README.md
├── src/
│   └── whaxon_masscan/
│       └── __init__.py
└── tests/
    └── test_masscan.py
```

### 4b. `src/whaxon_masscan/__init__.py`

```python
"""Masscan adapter for WHAXON."""
from __future__ import annotations

import re

from whaxon.adapters.base import Adapter
from whaxon.core.findings import Finding


_LINE_RE = re.compile(
    r"^Discovered open port (?P<port>\d+)/(?P<proto>tcp|udp) on (?P<ip>\S+)$"
)


class MasscanAdapter(Adapter):
    tool_id = "masscan"

    def parse(self, lines, ctx=None):
        findings = []
        for stream, text in lines:
            if stream != "stdout":
                continue
            m = _LINE_RE.match(text.strip())
            if not m:
                continue
            port = int(m.group("port"))
            findings.append(Finding(
                kind="open_port",
                severity="info",
                source="masscan",
                data={
                    "port": port,
                    "protocol": m.group("proto"),
                    "ip": m.group("ip"),
                },
                raw_line=text,
            ))
        return findings
```

**Nothing is registered here.** The registry finds the class via the
entry-point declaration in `pyproject.toml` (next section). That's the
whole point of the plugin mechanism — you don't reach into WHAXON's
package to register yourself.

### 4c. `pyproject.toml`

```toml
[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[project]
name = "whaxon-masscan"
version = "0.1.0"
description = "Masscan adapter for WHAXON"
requires-python = ">=3.11"
dependencies = ["whaxon>=0.3"]

[project.entry-points."whaxon.adapters"]
masscan = "whaxon_masscan:MasscanAdapter"

[tool.hatch.build.targets.wheel]
packages = ["src/whaxon_masscan"]
```

The important line is `[project.entry-points."whaxon.adapters"]`. The
left side is the entry-point name (any short identifier); the right
side is `<module>:<ClassName>`. WHAXON reads this dict at startup,
imports your class, instantiates it, and calls `register()` on it.

### 4d. The test

```python
# tests/test_masscan.py
from whaxon_masscan import MasscanAdapter


def test_parses_open_port():
    lines = [
        ("stdout", "Discovered open port 80/tcp on 10.0.0.5"),
        ("stdout", "Discovered open port 443/tcp on 10.0.0.5"),
        ("stdout", "Discovered open port 22/tcp on 10.0.0.6"),
    ]
    findings = MasscanAdapter().parse(lines)
    assert len(findings) == 3
    assert findings[0].kind == "open_port"
    assert findings[0].data["port"] == 80
    assert findings[1].data["protocol"] == "tcp"


def test_ignores_noise():
    lines = [
        ("stdout", "Starting masscan 1.3.2"),
        ("stdout", "rate: 100 packets/second"),
        ("stderr", "Discovered open port 22/tcp on 10.0.0.6"),
    ]
    assert MasscanAdapter().parse(lines) == []
```

### 4e. Installing locally

From the plugin project directory:

```
pip install -e .
```

WHAXON will pick it up on the next invocation. Confirm:

```
python -c "import whaxon.adapters as a; print(a.list_adapters())"
```

You should see `masscan` in the list.

## 5. What not to do

- **Don't spawn the tool from `parse`.** The runner already ran it. You
  receive its output; you don't re-run it.
- **Don't mutate `lines`.** Read it, don't modify it.
- **Don't import from `whaxon.ai`.** The adapter layer is deterministic
  and offline. The AI layer is on the other side of a hard boundary that
  WHAXON's CI enforces. Adapters that import `whaxon.ai` will fail the
  boundary test.
- **Don't swallow exceptions.** If your parser raises, WHAXON catches it
  and logs it with the tool id. That's more useful than silently returning
  `[]` and pretending the tool found nothing.

## 6. Adding to the catalog

Installing the adapter makes WHAXON able to *parse* the tool. To make it
able to *run* the tool, add an entry to `data/tools.json`:

```json
{
  "id": "masscan",
  "name": "Masscan",
  "category": "recon",
  "binary": "masscan",
  "description": "Fast port scanner",
  "args": "-p1-65535 --rate=1000 {target}",
  "package": "apt install masscan"
}
```

Then `whaxon run masscan 10.0.0.5` works, and any findings carry your
adapter's `source: "masscan"`.

## 7. Publishing to PyPI

Once the adapter works locally, publish it the same way you'd publish any
package:

```
pip install build twine
python -m build
twine upload dist/*
```

Naming convention: `whaxon-<tool>` on PyPI, so a search for `whaxon`
surfaces your plugin. Add `whaxon-plugin` and the tool name to your
package's keywords for discoverability.

## 8. What's available to import

From `whaxon.core.findings`:

- `Finding` — the dataclass you return

From `whaxon.adapters.base`:

- `Adapter` — the ABC you subclass

From `whaxon.adapters.registry`:

- `register(adapter)` — manual registration; not needed for entry-point
  plugins, but available if you're writing a local-only adapter

That's the whole public surface a plugin needs. Anything else in `whaxon`
is internal and may change without notice.

## 9. What the built-in adapters look like

Reference implementations, roughly in order of complexity:

| Adapter | Lines | What it demonstrates |
|---------|-------|----------------------|
| `dig.py` | ~40 | Simplest — one regex, info-only findings |
| `gobuster.py` | ~110 | Status-to-severity lookup table |
| `nmap.py` | ~265 | Service knowledge table + `lookup_hint` emission |
| `nikto.py` | ~215 | Issue pattern matching |
| `impacket.py` | ~150 | Sub-tool dispatch via `ctx["extra_args"]` |
| `msf.py` | ~260 | Running a tool through RPC, not a subprocess |

Start with `dig.py` or `gobuster.py` if you're modeling a new adapter.
Start with `nmap.py` if your tool reports versioned services and you
want to set `lookup_hint`.

## 9. Trust boundary

A WHAXON plugin is arbitrary Python code that runs in the WHAXON
process, with the operator's privileges and access to the same data
directory, environment variables, and network. Installing a plugin is
equivalent to running a script the plugin author wrote.

WHAXON does not sandbox plugins. There is no in-process isolation, no
capability restriction, and no code review of installed packages. The
catalog's parsing contract validates the shape of returned Finding
objects; it does not and cannot validate what the plugin did before
returning them.

Operational consequences:

- Install plugins only from sources you trust, the same way you would
  install any Python package with pip.
- A plugin that fails at import time will break whaxon startup. Test
  in a disposable environment first.
- A plugin that raises during parse() will surface the exception
  through the runner; the operator sees it and can decide what to do.
- Pin plugin versions in your deployment. An updated plugin is a new
  version of arbitrary code.

If a plugin needs capabilities beyond parsing tool output, that is a
signal that it belongs in WHAXON itself, subject to the adapter review
process in adapters.md, not in a shipped package.


---

## Part 10 — tools.md

# Tool Catalog and Execution

The packaged catalog is maintained at `src/whaxon/data/tools.json`. It describes command-backed tools and session operations. The effective runtime catalog and availability should be checked through `GET /api/tools`; do not assume every catalog entry is installed or usable on every host.

## Catalog model

A command-backed entry may include:

- `id`: stable tool identifier used by the runner, API and adapters.
- `name`: display name.
- `category`: functional grouping.
- `binary`: executable name or path resolved by the runtime.
- `description`: operator-facing summary.
- `args`: argument template used by the adapter and runner.
- `package`: package hint; it is not by itself permission to install software.

Session-backed entries use a transport and command rather than a local executable. They operate through an existing session and are not standalone binaries. The tool catalog is not an authorization policy: scope checks and the execution path still govern whether an action can run.

## Catalog entries in the current main snapshot

The packaged catalog contains 24 entries:

| ID | Kind |
|---|---|
| `nmap` | Command |
| `nikto` | Command |
| `gobuster` | Command |
| `echo` | Test command |
| `sqlmap` | Command |
| `whois` | Command |
| `dig` | Command |
| `nuclei` | Command |
| `commix` | Command |
| `ffuf` | Command |
| `wpscan` | Command |
| `impacket` | Command |
| `theharvester` | Command |
| `dnsrecon` | Command |
| `msf_sysinfo` | Metasploit session |
| `msf_getuid` | Metasploit session |
| `msf_hashdump` | Metasploit session |
| `ssh_cmd` | SSH session |
| `smb_shares` | SMB session |
| `smb_ls` | SMB session |
| `netexec` | Command |
| `arjun` | Command |
| `wmi_exec` | Session operation |
| `hydra` | Command |

This list is a snapshot of the packaged catalog on 2026-11-02. The live API is authoritative for the runtime actually installed.

## Availability and installation

Use `GET /api/tools` to inspect tool IDs and current availability. A missing optional executable does not mean the WHAXON core is unavailable. Use `whaxon doctor` and the [dependency readiness guide](OPERATIONS_MASTER.md) to diagnose dependencies and review an allowlisted installation plan. A catalog `package` value is not sufficient approval to invoke a package manager.

## Adding or changing a tool

1. Update the packaged catalog and any relevant adapter or provider registration.
2. Add or update parser, invocation, scope and failure-mode tests.
3. Confirm exact argv construction and that user-controlled values cannot bypass scope validation.
4. Update dependency diagnostics and installation policy separately where appropriate.
5. Verify the effective catalog through the API and run the relevant tests.

For output parsing, see [Writing an Adapter](#part-7--adaptersmd). For third-party adapter packages, see [Plugins](#part-9--pluginsmd).


---

## Part 11 — scope.md

# Scope

WHAXON enforces scope fail-closed. A missing or broken config never silently permits everything.

## Default config

If data/scope.json does not exist at Core.__init__, ScopeManager.load() writes:

    {
      engagement: default,
      enabled: true,
      in_scope: [
        127.0.0.0/8,
        10.0.0.0/8,
        172.16.0.0/12,
        192.168.0.0/16,
        ::1,
        fe80::/10,
        fc00::/7
      ],
      out_of_scope: [],
      notes: Auto-generated default scope. Loopback and RFC1918 only.
    }

Covers:

- IPv4 loopback 127.0.0.0/8
- RFC1918 (10/8, 172.16/12, 192.168/16)
- IPv6 loopback ::1
- IPv6 link-local fe80::/10
- IPv6 unique-local fc00::/7

Does NOT cover 169.254.0.0/16 (link-local / cloud metadata) - treating that as an accidental target would be a mistake.

## Precedence

check(target) returns a result with .allowed and .reason. Order:

1. enabled == false -> allowed (operator opt-out, explicit).
2. out_of_scope match -> denied, regardless of in_scope.
3. in_scope match -> allowed.
4. No match -> denied.

## CLI

    whaxon scope --show                # Print the current config
    whaxon scope --check <target>      # Exit 0 allowed / 1 denied
    whaxon scope --set scope.json      # Replace config from file
    whaxon scope --enable              # Set enabled=true
    whaxon scope --disable             # Set enabled=false
    whaxon scope --clear               # Delete file (default rewritten next load)

## HTTP API

- GET  /api/scope             - current config
- POST /api/scope/check       - body: {target: ...} -> {allowed, reason}
- POST /api/scope/override    - body: {target, reason} -> allow once, logged to data/scope_overrides.log

## Explicit scope overrides

The normal execution path rejects targets outside the configured scope. There are deliberately separate, explicit override paths:

- CLI: `whaxon run ... --allow-out-of-scope` requests a per-run override. Use only when the engagement authorization explicitly covers the target; review the command's output and persisted job record.
- Web API: `POST /api/scope/override` records a target and reason for a one-time override. The subsequent run must use the matching recorded override; a request parameter alone cannot bypass scope.
- Python integrations: the runner exposes a per-call `allow_out_of_scope=True` option to trusted calling code.

These are not substitutes for authorization, and they do not provide network-level containment. Keep scope enforcement enabled by default. Setting `enabled: false` disables the application-level scope guard globally and should be reserved for deliberately isolated labs.

## AI scope expansion

The AI planner obeys the same fail-closed scope checker as everything else. `WHAXON_AI_SCOPE_EXPANSION` selects the policy for how discovered hosts are treated:

| Value | Behavior | Status |
| --- | --- | --- |
| `strict` | Only explicitly-listed targets. Discovered hosts are never automatically in scope. The agent may *propose* adding one via `ask_human`, but the executor refuses any action against an out-of-scope target regardless of the human's answer. | **v1 default and only implemented policy.** |
| `inherited` | Any host that resolves from an in-scope domain, and any host in the same RFC1918 subnet as an in-scope host, would be in scope. | Documented; **not implemented in v1**. Selecting it logs a warning and falls back to `strict`. |
| `recommended` | As inherited, but every auto-expansion is logged and the human can veto before the first action against the discovered host. | Documented; **not implemented in v1**. Selecting it logs a warning and falls back to `strict`. |

**Why strict for v1.** Scope enforcement is the safety property the whole tool rests on. Starting strict and moving to looser is a small change. Starting loose and trying to tighten is a rewrite. The design (`docs/agent-architecture.md` §9) makes this explicit.

**Env var default:** unset = `strict`. Any value other than `strict` warns at startup and uses `strict`.

## Failure modes

- File missing: strict default written, enforcement enabled
- File unreadable / malformed JSON: RuntimeError at Core.__init__ - WHAXON refuses to start
- enabled key missing: defaults to true (fail-closed)
- in_scope missing: empty list; everything denied

## Tests

Scope behavior is covered by the `tests/test_scope*.py` suite and execution-boundary regressions, including default loopback/private ranges, IPv6 local ranges, out-of-scope precedence, malformed/missing configuration, DNS resolution failure, unsafe target arguments and explicit override handling. Run:

```bash
python -m pytest tests/test_scope*.py tests/test_validator_security_regressions.py -q
```

The test suite is evidence for the exercised cases only; it is not proof of connection-time network containment.

## Broad CIDR warning

An enabled scope containing `0.0.0.0/0` or `::/0` emits a warning when loaded because it effectively permits every IPv4 or IPv6 address in that family. WHAXON does not silently rewrite an explicitly configured rule, but operators should treat it as a global-scope decision and verify that the engagement authorization truly covers that reach.

## DNS and connection-time enforcement limits

When the scope contains IP/CIDR rules, hostname checks resolve the hostname and compare the current A/AAAA answers against the configured rules. Resolution errors fail closed, and an out-of-scope address overrides an allow rule. This is a **preflight check**, not a guarantee about the address ultimately contacted: DNS answers can change between the check and a tool's connection, and many external tools resolve the hostname independently.

For any deployment, do not treat the scope checker as a network firewall or as complete DNS-rebinding protection.

- Run tests in an isolated lab/VM or container with outbound network access restricted to the approved target ranges.
- Use a dedicated test engagement and a written target allowlist; review redirects, proxy settings, VPN routes, and pivot/port-forward paths.
- Do not use the default scope as authorization to scan arbitrary public hosts. It is intentionally limited to loopback and private ranges.
- Do not expose WHAXON to untrusted users or allow untrusted users to edit scope, configure tools, or invoke runner APIs.
- Keep `enabled: true`. Disabling scope removes this application-level guard and should only be considered in a deliberately isolated lab.
- Before production use, enforce destination IP policy at connection/egress level for each execution path (including external tools and pivoted sessions), then add integration tests proving that the actual connection cannot escape the allowlist.

A successful `whaxon scope --check` means the target passed the current application-level policy check. It does **not** prove that a later network connection is pinned to the checked address.


---

## Part 12 — interfaces.md

# Interfaces

WHAXON exposes a shared assessment core through CLI, terminal, desktop and Flask web interfaces. The installed command surface varies by package version and optional dependencies; `whaxon --help` is authoritative for the executable actually installed.

## CLI

The dispatcher includes setup, diagnostics, initialization, lifecycle/server, TUI/GUI, scope, installation, tool execution, workflows, findings, reports, evidence, validation/retest, coverage, Metasploit, AI and lookup operations. Consult `whaxon --help` for the exact installed command list and each command's `--help` for its options. Do not rely on historical fixed subcommand counts.

## Terminal UI

Launch with `whaxon tui`. The Textual interface is an optional extra (`pip install "whaxon[tui]"`). Key bindings and available screens may change; use in-app help and current source rather than treating old screenshots or notes as a complete interaction specification.

## Desktop UI

Launch with `whaxon gui`. The desktop interface uses PySide6 and embeds the web application. Install the `gui` extra. It is not a separate backend or a guarantee that every web route is available in every desktop environment.

## Web UI and headless service

For development, run `whaxon web` in the foreground. For the service-oriented WSGI daemon, use `whaxon serve --help` and `whaxon serve --daemon`; see [Deployment](OPERATIONS_MASTER.md) for PID, logging and shutdown behavior.

The server's startup output reports the effective address and browser URL. The default root route redirects to the **canonical Obsidian Kinetic interface at `/ui-v2`**. The previous `/ui` interface is retained as a legacy/reference route; it is not the default frontend.

The new UI has 22 page routes/templates and page-specific browser tests. Implementation does not equal final acceptance: the current audit and roadmap §38 still record open visual-regression, control-inventory, accessibility, service-parity and deployment-asset checks. Unsupported capabilities must remain hidden or disabled. See [New UI interaction and acceptance audit](V2_UI_MANDATORY_CROSSWALK.md).

## Authentication and deployment

Loopback requests use a local-peer authentication shortcut after Host and cross-origin protections. Non-loopback requests require explicit non-default Basic authentication credentials. The local default credentials are not suitable for remote exposure. Review [HTTP API](#part-13--apimd) and [Deployment](OPERATIONS_MASTER.md) before changing the bind address or placing the service behind a proxy.

## Current UI routes

The current route map, templates and browser-test references are maintained in [NEW_UI_INTERACTION_AUDIT.md](V2_UI_MANDATORY_CROSSWALK.md). That audit is subordinate to the master roadmap's §38 acceptance checklist; use the audit's remaining-work section rather than historical session notes.

## Related references

- [HTTP API](#part-13--apimd)
- [Scope and authorization](#part-11--scopemd)
- [Dependency readiness](OPERATIONS_MASTER.md)
- [Deployment](OPERATIONS_MASTER.md)
- [Master roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md)


---

## Part 13 — api.md

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

A scope check is an application-level preflight decision, not proof that every subsequent network connection remains inside scope. See [Scope](#part-11--scopemd).

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

These routes do not turn the installer into a general package manager. Exact-plan approval, allowlists, host restrictions and recovery limitations apply. See [Dependency readiness](OPERATIONS_MASTER.md).


## AI, validation and approvals

- `POST /api/ai/run` — submit an AI planning request.
- `GET /api/ai/runs` and `GET /api/ai/runs/<run_id>` — list and inspect runs.
- `GET /api/ai/pending` — pending human questions.
- `POST /api/ai/runs/<run_id>/answer` — answer a pending question.
- `GET /api/ai/runs/<run_id>/stream` — stream run events.
- `POST /api/validate/<job_id>/<int:seq>` — request deterministic validation.
- `POST /api/retest/<job_id>/<int:seq>` — request a retest.
- `POST /api/approvals/<job_id>/<int:seq>/resolve` — resolve a pending approval.

AI proposals are not authorization or execution evidence. Validation and retest outcomes may be inconclusive; do not interpret a missing observation as proof of safety.

## Metasploit and pivot

- `GET /api/msf/status`, `GET /api/msf/sessions`, `POST /api/msf/run`.
- `GET /api/msf/sessions/<session_id>` and `POST /api/msf/sessions/<session_id>/exec`.
- `GET /api/msf/modules/<module_type>`.
- `GET`, `POST` and `DELETE` `/api/msf/sessions/<session_id>/portfwd`.
- `GET /api/pivot/graph`, `GET /api/pivot/sessions/<session_id>/chain`, `GET /api/pivot/candidates`.

Their availability depends on the optional Metasploit integration and its configuration. Consult the route definitions and [Deployment](OPERATIONS_MASTER.md) before enabling them.

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
- `GET /ui-v2/<page>` — implemented page routes; see [New UI interaction and acceptance audit](V2_UI_MANDATORY_CROSSWALK.md).
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

