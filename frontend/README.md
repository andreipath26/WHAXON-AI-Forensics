# Obsidian Kinetic React frontend

This is the typed React + TypeScript migration workspace for the Obsidian Kinetic UI.

## Development

```sh
npm install
npm run typecheck
npm test
npm run build
```

The Vite build targets `src/whaxon/interfaces/web/static/obsidian/` and emits a manifest. Flask does **not** yet serve this bundle. The existing server-rendered Obsidian Kinetic interface remains the active UI until asset packaging, Flask manifest integration, route tests, full browser acceptance coverage, and visual comparison against the supplied design references are complete.

## Integration rules

- Use real backend endpoints; never seed sample targets, findings, telemetry, or success states in the UI.
- Backend scope and execution policy remain authoritative.
- Hide workflows until the end-to-end backend operation and its tests are available.
- Keep the deprecated legacy UI and design-reference files unchanged.
- Do not switch the default route to this frontend until the production wheel/sdist includes the built assets and deployment smoke tests pass.
