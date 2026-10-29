# WHAXON Competitor Capability and Vulnerability Remediation Roadmap Addendum

**Status:** QUEUED — approved product direction; not yet implemented.
**Applies to:** `andreipath26/WHAXON-AI-Forensics`.
**Relationship to the master roadmap:** This addendum expands the remediation lifecycle already described in §20.2 of `WHAXON ROAD MAP - WHATS NEXT - FULL SCOPE.md`. Read it alongside the master roadmap; it does not replace the roadmap, change release gates, or mark any capability DONE.
**Execution constraint:** Respect the master roadmap's UI-first execution gate. Complete and verify the agreed existing UI work before beginning this larger capability implementation. Preserve the approved UI assets/design; do not redesign the UI as part of remediation work.

## 1. Product objective

Make remediation a core WHAXON capability, not merely a report containing generic advice. For vulnerabilities WHAXON discovers—and, by design, supported findings imported from other scanners—WHAXON should be able to:

1. Explain the finding, likely root cause, evidence, affected asset/component, and security/business impact.
2. Recommend a mitigation or corrective action appropriate to the finding and its context.
3. Generate a concrete, reviewable patch whenever sufficient evidence, source/configuration context, and a defensible fix are available.
4. Test the proposed patch in an isolated or otherwise controlled environment.
5. Offer a user-controlled path to apply an approved patch through an authorized workflow.
6. Retest the original finding and record whether the vulnerability is fixed, partially fixed, unresolved, or not verifiable.
7. Preserve a traceable before/after evidence record and an auditable history of proposed, approved, applied, rolled-back, and verified changes.

The goal is broad coverage across vulnerability types and remediation surfaces. This is a product objective, **not a claim that every vulnerability can always be fixed automatically**. If context is missing, a fix is ambiguous, or a patch cannot be validated with sufficient confidence, WHAXON must state the limitation and provide the safest useful next step rather than fabricate certainty.

## 2. Scope: broad vulnerability and remediation coverage

Design the remediation engine to support these classes and allow future categories to be added through adapters/strategies rather than hard-coded into one narrow patcher:

- Injection vulnerabilities, XSS, unsafe parsing, insecure input handling, and output encoding.
- Authentication, authorization, access-control, session-management, and identity flaws.
- Vulnerable or unsupported dependencies, including compatible upgrades, replacement options, and lockfile changes.
- TLS, HTTP security headers, insecure service settings, and application/server configuration.
- Exposed credentials and secrets, including safe removal/rotation guidance and prevention of recurrence. A patch alone cannot invalidate a leaked credential; rotation/revocation must be represented separately.
- Insecure file permissions and operating-system/service configuration.
- Container images, Dockerfiles, Kubernetes manifests, deployment definitions, and infrastructure-as-code.
- Cloud policies, identities, network exposure, and resource configuration.
- Business-logic vulnerabilities requiring domain-specific context and regression tests.
- Vulnerabilities reported by external tools where a safe fix can be derived from normalized finding data and additional repository/asset context.
- Novel, complex, or poorly understood findings where automated patching is not yet reliable; provide structured investigation, compensating controls, and manual remediation guidance.

Remediation targets can include source code, dependencies, application/server configuration, operating-system/service configuration, containers, Kubernetes, infrastructure-as-code, and cloud configuration/resources. Actual application to a live target must depend on explicit authorization, supported integrations, and the risk policy; a finding's presence never grants permission to modify a system.

## 3. Finding intake and context normalization

Create a normalized remediation request that can originate from:
- WHAXON-native findings; and
- imported findings from other scanners or security tools.

Retain source/provenance and original identifiers. Normalize severity, confidence, affected asset/component, location, evidence, reproduction/validation status, references, and remediation context without discarding tool-specific data. Correlate duplicates while preserving links to every source.

Before patch generation, determine whether the finding has enough actionable context. Retrieve source/configuration/dependency context only from authorized workspaces and connections. Do not infer missing source code, business rules, cloud permissions, or deployment details. Imported findings with insufficient evidence should be enriched or returned for clarification before a patch is proposed.

## 4. End-to-end remediation lifecycle

### Stage A — Triage and root-cause analysis
- Review finding evidence and validation status; distinguish confirmed, probable, unverified, and informational findings.
- Identify the likely root cause, affected component, attack path, and impact.
- Explain uncertainty and identify missing context.
- Recommend the appropriate remediation strategy, including a compensating mitigation when a permanent fix is not immediately feasible.

### Stage B — Patch generation
- Generate a concrete diff or equivalent reviewable change when justified by available context.
- Explain the root cause, why each material change is needed, expected security benefit, compatibility/performance implications, and residual risk.
- Include relevant tests or test changes, migration notes, dependency constraints, and operational steps.
- Keep the patch minimal and scoped; avoid unrelated refactoring.
- Never treat hiding a finding, disabling a feature, suppressing a scanner rule, or weakening a control as a successful fix.
- If no defensible patch can be generated, say why and give actionable manual steps or a mitigation plan.

### Stage C — Pre-application validation
Use an isolated worktree, sandbox, test environment, or equivalent controlled mechanism appropriate to the target. Where relevant, run:
- syntax/build checks and static analysis;
- unit and integration tests;
- regression tests for the affected functionality;
- security-specific tests and negative/bypass cases;
- dependency, configuration, container, or infrastructure validation;
- the original finding's reproduction/validation procedure.

Record commands/checks actually run, their environment, exit status, output/evidence, and checks not run. Never claim a test passed when it was skipped, unavailable, or not executed. A successful build alone does not prove the vulnerability is fixed.

### Stage D — User-controlled application
Support these workflow modes:
1. **Advisory:** explain the fix and provide a patch artifact; the user applies it.
2. **Approval-based (recommended default):** generate, test, and present the patch; apply only after explicit approval.
3. **Explicitly authorized bounded automation:** permit automatic application only within user-defined target, scope, and risk constraints, with audit trail and rollback/recovery planning.

Keep patch generation and patch application as separate permissions. Never silently change production or other live systems. Require explicit approval for high-impact, destructive, externally visible, credential/identity, cloud-permission, or production changes. Respect least privilege and authorization boundaries. Provide dry-run/review mode, diff preview, backup/snapshot where appropriate, and rollback guidance or mechanism where feasible. If rollback is not feasible, disclose this before application.

### Stage E — Post-application verification and evidence
- Re-run the relevant original validation/reproduction check and regression tests.
- Classify the outcome as **fixed**, **partially fixed**, **unresolved**, or **unable to verify**, with a reason and supporting evidence.
- Check that the finding was not merely suppressed and that the fix did not introduce obvious regressions or an alternate bypass.
- Preserve before/after evidence, patch/diff, test results, timestamps, target identity, approval and actor, application outcome, and rollback details.
- Link the remediation record to the original finding and subsequent retest history/report.

## 5. Confidence, safety, and trust requirements

These are non-negotiable design requirements:

- **Do not conflate patch creation with a verified fix.** Report patch status, application status, and verification status separately.
- **No fabricated certainty.** Label assumptions, missing context, unsupported checks, and uncertainty.
- **No live modification by default.** Testing a target and changing it are separate actions requiring separate authorization.
- **Least privilege and scope enforcement.** Imported findings or AI-generated plans cannot expand the authorized target/scope or bypass WHAXON scope checks.
- **Preserve functionality.** Evaluate regressions, compatibility, performance, and security side effects; do not "fix" a finding by breaking intended behavior.
- **Secrets safety.** Never echo secret values into reports or patch descriptions unnecessarily. Credential rotation/revocation is a distinct operation and needs authorization.
- **Auditable provenance.** Store the origin of the finding, evidence used, patch generation method/version, reviewer/approval, checks performed, and final outcome.
- **Safe failure.** If scope, target identity, patch context, or authorization cannot be confirmed, stop before application and explain what is needed.
- **Rollback and recovery.** Plan for reversal where feasible; disclose when recovery is not straightforward.
- **No unverified blanket support claims.** Coverage grows by vulnerability/target adapters with acceptance tests; unsupported cases remain visible as unsupported or manual.

## 6. Architecture direction

Implement remediation as a modular lifecycle/orchestration layer rather than embedding patching logic into one scanner or UI page.

Expected conceptual components (names are provisional):
- Finding normalizer/provenance layer for WHAXON and imported findings.
- Root-cause/context resolver with explicit evidence and confidence.
- Remediation strategy registry/adapters keyed by vulnerability class and target type.
- Patch generator that emits a diff plus structured rationale and assumptions.
- Isolated validation runner with bounded commands, resource/time limits, and recorded results.
- Approval/policy gate separating generation, validation, and application.
- Target-specific application adapters with least-privilege credentials and dry-run support.
- Retest/evidence recorder connected to the existing finding and retest lifecycle.
- Audit/event history and report/API/UI surfaces.
- Extensible capability matrix documenting what each adapter can generate, apply, and verify.

Reuse existing finding, request-context, validation, retest, reporting, scope enforcement, and evidence mechanisms where appropriate. Inspect actual code and contracts before deciding implementation details; do not duplicate existing functionality or assume an interface is complete just because its module exists.

## 7. UI and user workflow

After the UI-first gate is satisfied, integrate remediation into the approved existing UI without redesigning it. The user should be able to:
- inspect the original finding and evidence;
- view the proposed remediation and a readable patch diff;
- understand impact, confidence, assumptions, risk, and tests;
- select advisory, approval-based, or explicitly authorized bounded automation where supported;
- approve/reject a patch and see what permissions are required;
- inspect application/test progress and logs;
- review before/after evidence and verification outcome;
- retry, roll back, or follow manual recovery instructions where supported.

Controls must be wired to real backend behavior and safe authorization checks. Hide or disable unsupported actions; never present mock buttons or imply that an action succeeded before the backend confirms it.

## 8. Delivery sequence and dependencies

1. **Respect the current UI-first gate:** finish and verify the already-approved UI work before implementation of the broader remediation engine. Do not use this roadmap item as permission to redesign the UI.
2. **Inventory existing lifecycle primitives:** inspect finding schemas, validation/retest, report/evidence, scope/authorization, storage, and API contracts. Record what can be reused and gaps with file/test evidence.
3. **Define normalized remediation and audit contracts:** include source provenance, target identity, permissions, confidence, patch artifact, validation results, approvals, and outcome states.
4. **Build read-only/advisory remediation first:** guidance, context checks, structured patch proposal, diff output, and explicit unsupported/uncertain outcomes.
5. **Add isolated patch validation:** reproducible tests, recorded results, regression checks, and security-specific verification.
6. **Add approval-gated application adapters:** start with a small, well-defined set of target types where safe end-to-end testing is feasible; expand through adapter contracts rather than weakening safeguards.
7. **Support imported findings:** normalize/import, preserve provenance, correlate, enrich context, and reject unsafe or context-free patch attempts.
8. **Expand vulnerability/target coverage incrementally:** maintain a published capability matrix and prioritize by customer value, exploitability, frequency, safe testability, and implementation confidence.
9. **Integrate the approved UI and reports:** only after the UI-first gate; maintain truthful state transitions and complete evidence.
10. **Acceptance and release gate:** require automated tests, controlled lab demonstrations, failure-path tests, authorization/scope tests, rollback/recovery checks, and end-to-end proof before calling each capability verified or shipped.

Do not invent time estimates until the code inventory and test plan establish the actual remaining work.

## 9. Required acceptance criteria

A remediation capability is not complete until tests demonstrate, at minimum:

- A WHAXON-native finding can produce an evidence-linked recommendation and, when context supports it, a reviewable patch.
- An imported finding retains its source/provenance and can be remediated when sufficient context is available.
- Missing/ambiguous context results in a safe, explicit refusal to generate or apply an unreliable patch.
- Generated patches are isolated from the original working tree until an approved application step.
- The user can inspect a diff and understand the expected change and risks before approval.
- Application cannot bypass target scope, authorization, or least-privilege policy.
- Production/high-impact changes are not applied without explicit approval.
- Validation distinguishes passed, failed, skipped, and unavailable checks.
- A test can prove the original vulnerability is fixed, or the system accurately reports that it cannot verify the result.
- Regression tests detect representative cases where a patch breaks intended behavior or only suppresses the finding.
- The audit record links finding, patch, approvals, applied change, checks, and retest outcome.
- Failure, cancellation, partial application, and rollback/recovery paths are tested where supported.
- UI controls map to real backend routes and show truthful status; unsupported controls are disabled/hidden.
- Documentation and capability matrix distinguish **generated**, **tested**, **applied**, and **verified** states.

## 10. Success measures

Track measurable indicators rather than marketing claims:
- percentage of findings with actionable guidance;
- patch-generation coverage by vulnerability class and target type;
- patch acceptance rate and human edit rate;
- validation pass/failure rate and false-fix rate from controlled tests;
- regression rate;
- percentage of applied fixes independently retested;
- time from validated finding to verified remediation;
- rate of safe refusal when evidence/context is insufficient;
- imported-finding coverage and provenance retention.

Do not optimize for raw patch volume at the expense of correctness, safety, or evidence quality.

## 11. Relationship to existing roadmap and status discipline

This addendum expands existing remediation lifecycle scope in §20.2 and complements the roadmap's validation, retest, reporting, evidence-reproduction, and scope-safety work. When the master roadmap is next edited, add a short cross-reference from §20.2 to this addendum so the relationship is visible from the canonical section.

Until implementation and acceptance tests are completed, all capabilities described here remain **QUEUED**. Planning approval does not mean code exists, tests pass, a patch is safe, or a vulnerability has been remediated.
