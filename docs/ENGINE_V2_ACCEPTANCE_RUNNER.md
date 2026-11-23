# Engine V2 local acceptance evidence runner

The repository provides one command for the repeatable checks that can run
locally without contacting a target system:

```sh
WHAXON_SOURCE_REVISION=<full-source-sha> make engine-v2-acceptance
```

The same runner can be called directly with `python
scripts/engine_v2_acceptance.py --source-revision <sha>`. It does not invoke
Git. If the revision is omitted, the report records `unknown`; supply the
exact source SHA from the branch or CI so evidence can be tied to a candidate.

Each run creates a new directory under
`artifacts/engine-v2-acceptance/<UTC>-<revision>/`. Existing evidence is never
overwritten. The bundle contains an incrementally checkpointed `report.json`,
`report.sha256`, complete command logs, built wheel and source archive, and a
fresh virtual environment used for the installed-wheel smoke. The report
records versions/platform, command, status, return code, duration, log digest,
package filenames, sizes and SHA-256 digests, and unresolved gates. The SHA-256 sidecar detects accidental changes only when
the report and digest are retained independently; it is not a signed audit
anchor.

The local checks cover the AI/core import boundary, Ruff, Mypy, the full pytest
suite, wheel/source builds, Twine metadata, required source-archive runtime
data, and installation of the wheel into a fresh virtual environment followed
by CLI, doctor, and packaged-data checks. A failure does not prevent later
checks from running. Missing executables and missing distributions are marked
blocked and explained in the report.

This command is an evidence collector, not a deployment approval. It always
records `deployment_decision: HOLD`, even when every local check passes. Exact
head GitHub CI across supported Python versions and operating systems, the
authorized controlled-provider lab, independent audit-anchor retention,
manual accessibility review, production-like service recovery, independent
engineering acceptance, and release artifact publication remain distinct
gates. The current G10 decision remains authoritative.

## Local prerequisites

The runner uses the active Python environment; it does not install project extras or browser binaries. Provision the same test dependencies as CI before running it (at minimum, `.[dev,web]`). The full suite includes Playwright UI tests: install the matching Chromium browser, or point `WHAXON_TEST_CHROMIUM` at an installed compatible Chromium executable. CI installs Playwright's pinned browser. If the active environment is incomplete, the runner records the actual failed or blocked test result in its log rather than treating unexecuted coverage as passed.
