# Obsidian Kinetic — Production UI Architecture

## Decision

The production frontend will use **React, TypeScript, and Vite**. Flask remains the Python web/API layer and WHAXON core remains authoritative for execution, scope, validation, evidence, persistence, approvals, and reports.

This is an architecture decision, not a statement that the migration or UI is complete.

## Non-negotiable product rules

1. The Obsidian Kinetic screens and design tokens in `web ui files and rendering/` are the visual source of truth.
2. The new frontend becomes the default at `/` and `/ui`; the deprecated interface remains available only at `/ui/legacy` and its assets stay unchanged.
3. A feature is visible only when its complete user workflow is supported by a real backend capability and covered by integration/browser tests.
4. Roadmap-only and partially integrated features are omitted from production navigation, pages, actions, and dashboards. No disabled placeholders, fake telemetry, fabricated findings, sample targets, or simulated success.
5. Hiding a control is not an authorization boundary. Flask must independently enforce authentication, authorization, scope, and execution policy.
6. Errors and unavailable optional capabilities must be visible and truthful. A failed request must never be rendered as success.
7. Existing API behavior must be preserved unless a separately tested API-contract change is required.

## Target structure

- `frontend/`: React application, TypeScript domain/API types, feature modules, shared UI components, design tokens, and frontend tests.
- Flask templates: minimal production shell that mounts the built frontend and loads hashed assets.
- Flask static assets: built frontend artifacts included in Python distributions so installed-package deployments do not require Node.js.
- Existing Python modules: source of truth for policy and business operations.
- `docs/NEW_DEFAULT_UI_INTERACTION_AUDIT.md`: living workflow and acceptance ledger.
- `docs/WEB_UI_INTERACTION_AUDIT.md` and deprecated templates/assets: reference-only; do not modify them.

## API and state conventions

- Centralize HTTP requests, response validation, error handling, and credentials in one typed API client.
- Use typed request/response schemas at the frontend boundary. Do not silently coerce unknown backend payloads into plausible live values.
- Keep job state, findings, evidence, scope, and AI-run decisions separate domain concepts.
- Use server-sent events for job output where the current backend supports them; handle reconnects, terminal states, and cancellation results honestly.
- Use capability checks only when grounded in real backend responses. A roadmap item without a functioning endpoint is not a capability.
- Keep security-sensitive decisions in Python; client-side checks are for usability only.

## Migration and deployment gates

1. Inventory current endpoints, schemas, design screens, and actual backend support. Mark each workflow as visible, hidden, or blocked.
2. Establish the frontend build, type-check, lint, unit-test, and browser-test pipeline.
3. Port only ready workflows to React while preserving the existing Flask API and visual design.
4. Keep unfinished workflows hidden; do not publish an empty page or a nonfunctional nav item as a placeholder.
5. Verify every visible button, form, link, upload, download, streaming action, and error state against the live Flask test server.
6. Compare browser screenshots with the supplied Obsidian Kinetic renderings at desktop and mobile breakpoints.
7. Verify the built static assets are included in wheel/sdist and the installed package can serve the UI without a frontend toolchain.
8. Require CI on Python 3.11, 3.12, and 3.13, frontend checks, browser acceptance tests, and package smoke tests before deployment.
9. Retain `/ui/legacy` only as a reference route; root and `/ui` must resolve to the production frontend.

## Release status

**Not deployment-ready until all gates above are evidenced by passing automated checks and the acceptance ledger is complete.** Creating the React scaffold, wiring a route, or passing static checks alone does not meet this standard.
