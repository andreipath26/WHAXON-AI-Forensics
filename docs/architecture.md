# Architecture

WHAXON is a shared Python assessment core exposed through CLI, terminal, desktop and Flask web interfaces. External tools are described by a catalog and connected through adapters/providers. The architecture is evolving toward the durable, capability-driven Engine v2 described in [the Engine v2 crosswalk](ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md); that target design is not the same as a fully accepted deployment architecture.

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

The schema above is not a promise that every subsystem has completed production acceptance. Engine v2's remaining guarantees and migration work are tracked in [the Engine v2 crosswalk](ENGINE_V2_ARCHITECTURE_AND_ROADMAP_CROSSWALK.md) and master roadmap §49.

## Fail-closed design

Two things are deliberately strict:

1. Scope - missing scope.json writes a strict default on load; unreadable scope.json raises. Never silently allows everything. See scope.md.
2. Reports - HTML output escapes markdown before wrapping in <pre>, so a tool that prints <script> cannot inject script into a browser viewing a report.

## Extending

- New tool: add an entry to data/tools.json (id, binary, args template).
- New adapter: subclass Adapter, implement parse, register(MyAdapter()) at module level, and import it from whaxon/adapters/__init__.py.
- New interface: import Core, subscribe to the EventBus, call runner.run_tool. No core changes needed.