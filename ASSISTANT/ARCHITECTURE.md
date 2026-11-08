# Architecture and authority

WHAXON UI V2 / CLI / text assistant / optional voice -> Assistant intent and presentation services -> existing WHAXON application services -> policy/approval/mission/plan/scheduler/provider/evidence. Only the existing WHAXON services may authorize security-tool execution.

Desktop conveniences (opening an editor, local search, read-only host diagnostics) live behind separate, least-privileged capability adapters and never inherit security tool permissions. Unsupported upstream JARVIS security categories stay inventoried but not implicitly admitted to the WHAXON registry.

## Invariants
1. Every supported WHAXON setting remains accessible through full professional controls. Assistant shortcuts cannot discard advanced options or mutate scope silently.
2. Intent and model output are untrusted input, transformed into typed, versioned proposals and validated server-side. Never execute raw AI-produced shell commands.
3. Approvals remain authenticated, actor-bound and scoped to exact plan/parameters. Voice transcription is not authentication or approval.
4. Model, audio and conversation data are isolated by tenant/engagement and redacted before optional cloud use. Cloud routing must be opt-in and visible.
5. Persist operation identifiers and reconstruct job state from WHAXON's durable services; do not equate launching a thread with successful execution.
6. Local-only operation and deterministic intents continue without a cloud provider.
7. Existing Engine V2 / UI V2 completion precedes external real-target and production qualification, in accordance with the master roadmap.

The ASSISTANT directory owns assistant-specific source, specs and tests. Integration points in WHAXON core/UI must be minimal adapters using the existing service contracts rather than duplicate implementations.
