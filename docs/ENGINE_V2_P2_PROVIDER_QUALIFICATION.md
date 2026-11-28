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

## Exact-head real-provider loopback evidence — 2026-11-28

The curated provider smoke implementation passed exact-head CI at source head
`9f26e848642518b95138305a0ab43cedca23e1c4`, workflow run
[#46144343464](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/46144343464)
(**23/23 checks successful**). The run also passed the G01 controlled-lab chain.
The provider smoke evidence artifact is
[whaxon-p2-provider-loopback-b36b42006ee517a6935e7440496007cfd9dd2c46](https://github.com/andreipath26/WHAXON-AI-Forensics/actions/runs/46144343464/artifacts/15263048381),
artifact ID `15263048381`, SHA-256
`55827c0e93470b030de59cd5d5468564bbdcd6833d884c9d48d9644dd6d85261`.
GitHub retention is 30 days from 2026-11-28.

The Ubuntu apt lane runs actual `nmap`, `gobuster`, `ffuf`, and `sqlmap`
through approved Engine V2 plans inside a Linux network namespace containing
only loopback; evidence records binary paths, version output, SHA-256 identities,
attempt outcomes, and the observed fixture requests. It recorded a real
Gobuster request, cancellation after the fixture observed the effect, process
restart, an uncertain persisted attempt, and no automatic replay. The smoke
reported zero normalized directory findings for Gobuster and ffuf. That is
evidence about the current adapter result, not a successful directory-finding
qualification. The macOS Homebrew lane ran the same named loopback smoke and
Nuclei template-matching check, but it does not run inside the Linux network
namespace. Its evidence is limited to the loopback-configured test case.

The binary hashes and version outputs are pinned in the retained run artifact,
but the workflow does not pin package versions before installation. The
installed-tool set and these loopback fixtures do not establish coverage of
all provider inputs, resource use, general subprocess egress, production
cancellation, real-target output quality, cross-host recovery, or complete
end-to-end workflows. All 12 admitted providers therefore remain
`not_qualified`; the smoke is bounded evidence for the exact installed
versions and loopback cases only.

## Gate disposition

Provider inventory and conservative fake/loopback effect recovery have source and regression coverage, but the complete admitted provider portfolio, real-provider effect behavior, multi-process/outbox recovery, and operator recovery across the supported deployment matrix remain open. **G01/G05/G08/G10 provider acceptance must remain open; this record does not authorize deployment.**
