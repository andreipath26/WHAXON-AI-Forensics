# Engine V2 P2-A client lifecycle parity

**Review date:** 2026-11-28  
**Code base:** `9b4b2417fa37557e7d726905dec39d93716234d8`  
**Current decision:** **PARTIAL — full client parity remains OPEN.**

## Scope and evidence

Engine V2 workflow state is persisted by shared Core and workflow request services. A request accepted by one client is not proof of provider execution or completion. The supervised worker owns execution; the TUI must not drain provider work inline.

The focused cross-client regression added in this batch,
`tests/test_workflow_client_parity.py::test_tui_approved_run_is_observed_by_api_and_cancelled_by_cli`,
performs one durable, inert lifecycle across clients:

1. TUI creates a mission and persisted plan, records task approval, and submits a run request.
2. A separate Core instance and API client read the same request snapshot and see `queued`, no lease credential, and no completion claim.
3. The headless CLI cancels that request through the persisted request service.
4. The API and the original TUI read the same terminal `cancelled` state.
5. The test asserts no workflow attempts were created and patches the TUI drain method to fail if inline provider work is attempted.

Related existing regression sources include:
- `tests/test_workflow_run_requests.py`: CLI/API submission deduplication, request persistence/restart, snapshot, cancellation, and uncertainty.
- `tests/test_tui_workflows.py`: TUI create/propose, approve, durable request submission, screen restart/reconnect, cancellation and worker ownership.
- `tests/test_server_workflow_v2.py`: API mission/plan authoring, read-only views, cancellation and route contracts.

## Client disposition

| Client | Proven behavior | Remaining parity work |
|---|---|---|
| Headless CLI | Persists plans, approvals, run requests, status, cancellation, recovery snapshots and queue summaries via Core services. | Full end-to-end parity for every supported operation and deployment mode remains unverified. |
| HTTP API | Creates and observes persisted plans/requests, exposes recovery snapshots, and cancels through shared services. | Full route-by-route UI/control parity and every failure/recovery state remain unverified. |
| TUI | Creates proposals, records approval, submits durable requests, reconnects and observes cancellation. PR #280 removed inline worker draining. | Complete action parity and accessibility/manual acceptance remain open. |
| Web UI | Uses shared API/Core workflow services; page and route regression suites exist. | Not every displayed control is proved to perform the matching supported operation and lifecycle transition. |
| Desktop compatibility GUI | Legacy/dormant compatibility surface; not counted as a qualified V2 client. | Keep isolated or retire after inventory-based disposition; no V2 parity claim. |

## Limitations

This regression uses only the reserved documentation address `192.0.2.10` and does not run a scanner or contact a target. It proves persisted request visibility and cancellation across TUI/API/CLI for this workflow state; it does not prove provider execution, worker recovery across hosts, all web controls, every API/CLI command, or deployment readiness. Legacy execution and excluded session transports remain outside the V2 parity claim.
