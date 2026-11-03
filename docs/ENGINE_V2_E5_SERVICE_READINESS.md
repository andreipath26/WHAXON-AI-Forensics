# Engine V2 E5 — Core service readiness and optional integration health

This batch makes `GET /api/health` report **core readiness** separately from
optional Metasploit RPC availability.

- A writable **actual Core data directory** and a successful SQLite `SELECT 1`
  are required for `core_ready: true` and HTTP 200.
- A missing or failing Core database, or an unwritable Core data directory,
  produces `core_ready: false`, `status: degraded` and HTTP 503.
- Metasploit is an optional transport. Its `checks.msf` may be `up`,
  `down` or `unavailable`; a non-up value appears in
  `optional_degraded` but does not alone make the Core unready.
- The writable-directory check uses a unique temporary file in
  `Core.data_dir` and cleans it up. It no longer creates a predictable
  `.healthz` path or probes an unrelated `WHAXON_DATA` fallback.
- Internal errors are not returned verbatim by the health endpoint.

**Limits:** Readiness is a momentary local Core/store check, not proof of a
live dedicated worker, external tool availability, safe network egress,
application authorization, restored backup or complete daemon/container
acceptance. Existing `/api/health/simple` is a separate liveness probe.
The endpoint does not grant any execution permission or alter the supplied UI.

Source: `src/whaxon/interfaces/web/server.py`.

Regressions: `tests/test_engine_v2_e5_core_readiness.py` checks optional
RPC outage, correct data path, SQLite failure, data-path failure, optional
RPC exception and cleanup behavior. Deployment-specific end-to-end health
acceptance remains open under the master roadmap's P2/P3 and E5 gates.
