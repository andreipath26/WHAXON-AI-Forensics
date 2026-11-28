# Engine V2 provider qualification and effect recovery status

**Review baseline:** `be5acd974c38560be4b0a32ee64d4218b5a31e20` (2026-11-23 main).
**Decision:** Provider portfolio is inventoried and bounded, but **not qualified for deployment**. This record distinguishes code-contract evidence from installed binaries, smoke tests, controlled-lab checks, full workflow verification, and production acceptance.

## Admitted catalog portfolio

All rows below are admitted by the fixed catalog adapter bridge. “Admitted” means a versioned local-process provider contract is registered; it does not establish an installed tool, successful invocation, safe egress, validated output, or deployment readiness. The provider inventory reports `qualification_status=not_qualified` unless a future qualification process supplies evidence. Binary presence alone is reported as `readiness=installed`, with reason `installed_unverified` and basis `catalog_contract_and_binary_presence_only`.

| Catalog tool | Adapter | Declared V2 target types | Existing parser/provider test source | Qualification result |
| --- | --- | --- | --- | --- |
| `arjun` | `src/whaxon/adapters/arjun.py` | URL | `tests/test_providers.py` covers provider binding; no dedicated Arjun parser test was identified in this inventory | Not qualified |
| `dig` | `src/whaxon/adapters/dig.py` | Hostname | `tests/test_adapters_whois_dig_whatweb.py`; `tests/test_engine_v2_e3_catalog_provider_crash.py` | Not qualified |
| `dnsrecon` | `src/whaxon/adapters/dnsrecon.py` | Hostname | `tests/test_adapters_theharvester_dnsrecon.py` | Not qualified |
| `ffuf` | `src/whaxon/adapters/ffuf.py` | URL | `tests/test_adapters_gobuster_ffuf_nuclei_wpscan.py` | Not qualified |
| `gobuster` | `src/whaxon/adapters/gobuster.py` | Hostname | `tests/test_adapters_gobuster_ffuf_nuclei_wpscan.py` | Not qualified |
| `nikto` | `src/whaxon/adapters/nikto.py` | Hostname, IP, URL | `tests/test_adapters_parse.py`; `tests/test_e1_nikto_regressions.py` | Not qualified |
| `nmap` | `src/whaxon/adapters/nmap.py` | Hostname, IP | `tests/test_adapters_parse.py` | Not qualified |
| `nuclei` | `src/whaxon/adapters/nuclei.py` | URL | `tests/test_adapters_gobuster_ffuf_nuclei_wpscan.py` | Not qualified |
| `sqlmap` | `src/whaxon/adapters/sqlmap.py` | URL | `tests/test_adapters_parse.py`; controlled G01 lab evidence is recorded in `docs/ENGINE_V2_LEGACY_EXECUTION_INVENTORY.md` | Not qualified |
| `theharvester` | `src/whaxon/adapters/theharvester.py` | Hostname | `tests/test_adapters_theharvester_dnsrecon.py` | Not qualified |
| `whois` | `src/whaxon/adapters/whois.py` | Hostname, IP | `tests/test_adapters_whois_dig_whatweb.py` | Not qualified |
| `wpscan` | `src/whaxon/adapters/wpscan.py` | URL | `tests/test_adapters_gobuster_ffuf_nuclei_wpscan.py` | Not qualified |

The target declarations come from `src/whaxon/core/providers.py::_CATALOG_TARGETS`. They constrain parsing/dispatch shape only; they do not authorize a target. Each task still requires the shared scope and approval path. Catalog adapter input schemas reject dynamic arguments and dispatch uses the fixed packaged command through `ToolRunner`.

### Qualification evidence still required

The repository's prior release inventory states that its inspected local environment had no installed V2 provider binaries and none of the admitted set was smoke-, lab-, or end-to-end-verified. Parser fixtures and provider bridge tests are source-level regression evidence, not executable qualification. This PR adds a regression that exercises all 12 inventory entries with a synthetic PATH resolver and proves that even a present binary remains explicitly unqualified. That test intentionally is not counted as a provider smoke test.

To qualify each provider, retain an exact-candidate run record for the supported OS and tool version, including package/source provenance, resolved executable/version, fixed argv and target class, expected and observed outputs, cancellation/timeout behavior, resource usage, network/effect boundaries, durable job/evidence records, reviewer, and retained CI artifact. A real target requires explicit operator authorization and a controlled scope. Do not promote a provider based on tool registration, parser-only tests, fake executables, or a successful process exit alone.

## Effect accounting and restart recovery

- `src/whaxon/core/outbox.py` documents lifecycle publication as at-least-once. If a callback can cause a remote effect then fail before acknowledgement, delivery may be duplicated; consumers must deduplicate by `(plan_id, event.id)`. Exactly-once delivery is not claimed.
- Workflow dispatch attempts persist an identity and mark dispatch-start before invoking a provider. Where a worker is lost after dispatch may have begun, the result remains uncertain and is not automatically dispatched again.
- `tests/test_engine_v2_e3_catalog_provider_crash.py` is bounded evidence for a fake-`dig` catalog-provider crash/recovery scenario. `tests/test_engine_v2_e3_external_effect_crash.py` exercises a real loopback HTTP receiver with accepted, disconnected, and cancelled response cases. These tests establish conservative uncertain-effect handling in those fixtures; they do not qualify all scanner effects, provider versions, external networks, or cross-host recovery.
- Operator reconciliation is explicit and audited. “No effect verified” requires operator evidence and a new run; an observed or unresolved effect is not certified as success and is not blindly replayed.

## Added real-provider loopback acceptance (pending exact-head CI)

This branch extends the curated CI tool smoke to run in a new Linux network
namespace with only loopback enabled. The fixture and scanner subprocesses share
that namespace, so the scanner cannot reach external networks during the
acceptance step. Apt/setup work occurs before isolation. The candidate exercises
real `nmap`, `gobuster`, `ffuf`, and `sqlmap` binaries; Nmap, Gobuster, ffuf,
and SQLmap run through approved Engine V2 plans with persisted, integrity-checked
evidence. It also holds one real Gobuster request, cancels after the fixture
observes the request, restarts the Core, and asserts the attempt remains
uncertain and is not replayed. The CI artifact records binary paths, version
output, SHA-256 identities, provider IDs, versions, manifest fingerprints, and
the bounded outcome summary.

This exact-head acceptance is **pending** until CI passes and the artifact is
retained. The workflow still obtains package versions from the runner package
manager; it records the exact binary hashes used, but does not yet lock binary
versions before installation. This evidence can qualify only the four named
tools for the stated loopback cases, never the remaining eight providers or
external-target/production behavior.

## Gate disposition

Provider inventory and conservative fake/loopback effect recovery have source and regression coverage, but the complete admitted provider portfolio, real-provider effect behavior, multi-process/outbox recovery, and operator recovery across the supported deployment matrix remain open. **G01/G05/G08/G10 provider acceptance must remain open; this record does not authorize deployment.**
