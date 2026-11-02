# Interfaces

WHAXON exposes a shared assessment core through CLI, terminal, desktop and Flask web interfaces. The installed command surface varies by package version and optional dependencies; `whaxon --help` is authoritative for the executable actually installed.

## CLI

The dispatcher includes setup, diagnostics, initialization, lifecycle/server, TUI/GUI, scope, installation, tool execution, workflows, findings, reports, evidence, validation/retest, coverage, Metasploit, AI and lookup operations. Consult `whaxon --help` for the exact installed command list and each command's `--help` for its options. Do not rely on historical fixed subcommand counts.

## Terminal UI

Launch with `whaxon tui`. The Textual interface is an optional extra (`pip install "whaxon[tui]"`). Key bindings and available screens may change; use in-app help and current source rather than treating old screenshots or notes as a complete interaction specification.

## Desktop UI

Launch with `whaxon gui`. The desktop interface uses PySide6 and embeds the web application. Install the `gui` extra. It is not a separate backend or a guarantee that every web route is available in every desktop environment.

## Web UI and headless service

For development, run `whaxon web` in the foreground. For the service-oriented WSGI daemon, use `whaxon serve --help` and `whaxon serve --daemon`; see [Deployment](deployment.md) for PID, logging and shutdown behavior.

The server's startup output reports the effective address and browser URL. The default root route redirects to the **canonical Obsidian Kinetic interface at `/ui-v2`**. The previous `/ui` interface is retained as a legacy/reference route; it is not the default frontend.

The new UI has 22 page routes/templates and page-specific browser tests. Implementation does not equal final acceptance: the current audit and roadmap §38 still record open visual-regression, control-inventory, accessibility, service-parity and deployment-asset checks. Unsupported capabilities must remain hidden or disabled. See [New UI interaction and acceptance audit](NEW_UI_INTERACTION_AUDIT.md).

## Authentication and deployment

Loopback requests use a local-peer authentication shortcut after Host and cross-origin protections. Non-loopback requests require explicit non-default Basic authentication credentials. The local default credentials are not suitable for remote exposure. Review [HTTP API](api.md) and [Deployment](deployment.md) before changing the bind address or placing the service behind a proxy.

## Current UI routes

The current route map, templates and browser-test references are maintained in [NEW_UI_INTERACTION_AUDIT.md](NEW_UI_INTERACTION_AUDIT.md). That audit is subordinate to the master roadmap's §38 acceptance checklist; use the audit's remaining-work section rather than historical session notes.

## Related references

- [HTTP API](api.md)
- [Scope and authorization](scope.md)
- [Dependency readiness](dependency-readiness.md)
- [Deployment](deployment.md)
- [Master roadmap](../WHAXON%20ROAD%20MAP%20-%20WHATS%20NEXT%20-%20FULL%20SCOPE.md)
