# Engine V2 provider effect reconciliation runbook

**Scope:** operator handling of an Engine V2 attempt whose external effect is uncertain.  
**Status:** operational guidance only. It does not qualify a provider, authorize a target, or lift the G05/G10 deployment hold.

## Before changing any attempt

1. Stop new submissions for the affected plan while reviewing it. A cancellation request does not prove a provider that already started has stopped.
2. Read the durable attempt and reconciliation views:

   ```sh
   whaxon workflow plan attempts --id PLAN_ID
   whaxon workflow plan reconciliation-report --id PLAN_ID
   whaxon workflow plan events --id PLAN_ID
   whaxon workflow plan audit --id PLAN_ID
   ```

3. Match the attempt ID, plan/task identity, provider ID/version, manifest fingerprint, target, dispatch-start event, and any provider result to retained external evidence. Preserve the original database and artifact hashes before making a decision.
4. Use an evidence source independent of the WHAXON process when possible (for example, an authorized fixture/server request log or operator-controlled network/service log). A timeout, process exit, missing local output, or absent WHAXON finding does not establish that no effect occurred.
5. Keep any retained evidence under operator-controlled storage. Record a stable reference and digest in the reconciliation record. Do not put credentials, session tokens, or sensitive payloads in the note.

## Choose exactly one disposition

| Disposition | Use only when | Expected workflow result | Next action |
| --- | --- | --- | --- |
| `no_effect_verified` | Independent evidence supports that the provider did not cause the relevant external effect during the attempt. The basis and observation window must be recorded. | The task becomes failed and may be retried only through a separate run request. Automatic replay is false. | Review scope, plan digest, approval, budget, and duplicate-effect risk again. Submit a separate approved request only after that review. |
| `effect_observed` | Evidence shows an external effect occurred, but this does not establish that WHAXON verified a finding or that the provider output is complete. | The task becomes blocked. | Preserve the evidence and use a separately authorized verification workflow. Do not retry the original operation to obtain a cleaner result. |
| `unresolved` | Evidence is incomplete, contradictory, unavailable, or cannot distinguish no effect from an effect. This is the safe choice when uncertain. | The attempt and task remain uncertain. | Keep the plan stopped and obtain more evidence or escalate to the designated reviewer. Do not submit a retry. |

Record the selected disposition with the exact CLI contract:

```sh
whaxon workflow plan resolve-attempt \
  --id PLAN_ID \
  --attempt-id ATTEMPT_ID \
  --disposition unresolved \
  --actor "OPERATOR_LABEL" \
  --evidence-ref "OPERATOR_CONTROLLED_EVIDENCE_REFERENCE" \
  --note "Concise basis, evidence digest, and review window"
```

Replace `unresolved` only after the evidence satisfies the corresponding row above. The command records a claimed actor label and an evidence reference; it does **not** authenticate the actor or independently fetch/verify the referenced evidence. Use an authenticated, access-controlled operator process and retain reviewer identity and evidence outside the WHAXON database.

## Verify and retain the decision

After recording the reconciliation, inspect the persisted result and audit state:

```sh
whaxon workflow plan reconciliation-report --id PLAN_ID
whaxon workflow plan attempts --id PLAN_ID
whaxon workflow plan events --id PLAN_ID
whaxon workflow plan audit --id PLAN_ID
whaxon workflow plan readiness --id PLAN_ID
whaxon workflow plan audit-snapshot --id PLAN_ID
```

Retain the output, the exact code SHA, database snapshot/hash, evidence artifact and its hash, reviewer identity, and decision together in an independently protected location. A matching local audit snapshot is not an independent trust anchor. If an external witness recorded a digest, compare it with:

```sh
whaxon workflow plan audit-verify --id PLAN_ID --expected-digest EXPECTED_SHA256
```

A successful comparison checks the local lifecycle digest against the supplied value; it does not prove who supplied that value or prevent an attacker from rewriting both the database and the expected digest.

## Provider evidence boundary

The 2026-11-28 retained CI smoke is bounded to its recorded cases: actual Nmap, Gobuster, FFuf, and SQLmap loopback runs in the Linux isolated lane, plus the recorded macOS Nuclei template check. It is not qualification for every input, host, version, target, resource limit, cancellation path, or production egress behavior. The other admitted providers have no corresponding real-effect qualification in that evidence. Keep all twelve admitted providers marked `not_qualified` until provider/version/OS-specific smoke, controlled-lab, workflow and recovery evidence is reviewed and retained.

Relevant regression coverage includes:

- `tests/test_workflow_cli.py::test_workflow_cli_records_manual_attempt_reconciliation` — CLI contract and no automatic replay result.
- `tests/test_engine_v2_e3_external_effect_crash.py` — loopback side effect, disconnect/cancellation uncertainty, and no automatic replay.
- `tests/test_engine_v2_e3_catalog_provider_crash.py` — bounded fake-`dig` provider recovery path. This is not real-provider qualification.

The outbox may deliver at least once and external effects cannot generally be guaranteed exactly once. Do not treat retry, recovery, a successful process exit, or an operator disposition as proof that a security finding is verified.
