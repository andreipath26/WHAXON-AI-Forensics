# Data Handling and Retention

**Status reviewed 2026-11-02.** This is an operational guide, not a legal opinion, a certification statement, or a claim that WHAXON enforces a retention schedule. Set applicable retention rules in the engagement contract and under the law that applies to the data and parties.

## 1. Data WHAXON may persist

The default data directory is `data/`; an operator may select another path. Depending on enabled features and the engagement, persistent data may include:

| Data | Typical location | Notes |
|---|---|---|
| Scope and authorization configuration | `data/scope.json` | Application-level scope policy |
| Jobs and lifecycle state | `data/whaxon.db` | SQLite database |
| Raw tool output | `lines` table in SQLite | May contain hostnames, paths, banners, tokens or other sensitive output |
| Findings and verification state | `findings` and related tables | Payloads and request context may contain sensitive target data |
| Evidence metadata | `evidence` table | Referenced files may be stored separately from SQLite |
| AI run history | `ai_runs` and `ai_run_steps` tables | Prompts, proposed actions and results may contain target data |
| Scope override records | `data/scope_overrides.log` | Authorization and operator decision trail |
| Logs, exports and reports | Operator-configured paths | May contain copies of findings and raw evidence |

The exact paths depend on the configured data directory, evidence handling, logging and export choices. Backups, copied reports and uploaded evidence must be inventoried separately.

## 2. Sensitive information

Do not assume findings, raw output, request context, evidence, logs or reports are automatically scrubbed. A tool can return credentials, session tokens, personal data or other secrets; those values may be persisted as part of raw output or a finding. Redaction of recognized secret-valued settings is not a general-purpose sanitizer for engagement evidence.

Use dedicated lab credentials, restrict filesystem permissions, avoid collecting unnecessary data, and inspect exports before sharing them. If a real credential is captured, treat it as exposed and rotate it through the system owner.

## 3. External services and AI providers

Local persistence does not mean every enabled operation is offline. When a cloud AI provider is explicitly configured, WHAXON sends the prompt and context needed for that provider to generate a planning response. External tools and optional integrations may also communicate with their own services or target systems. Review each provider's data terms and configure only services approved for the engagement. The default AI provider is `null`; no AI planning provider is selected unless configured and enabled.

## 4. Retention and deletion

WHAXON does not impose a universal engagement-retention period or guarantee automatic deletion of every copy. The operator must define the schedule based on the engagement contract, applicable law, client policy and backup requirements.

At engagement close:

1. Export and deliver only the approved report and evidence.
2. Identify the configured WHAXON data directory, separately stored evidence, logs, exports and reports.
3. Retain only records required by the agreed schedule; protect archives with appropriate access controls and encryption.
4. When retention expires, stop WHAXON and remove the relevant data and separately stored copies using the organization's approved deletion process.
5. Account for backups, snapshots, cloud-provider retention, endpoint backups and removable media. Deleting the active directory does not delete those copies.
6. Record what was deleted, when, by whom and which backup-retention exceptions remain.

Removing a row or evidence reference through an API is not proof that every underlying file or backup copy has been securely erased. Do not claim secure erasure unless the storage medium and deletion process have been independently verified.

## 5. Operator responsibility

The operator is responsible for lawful authorization, data minimization, access control, encryption, backup protection, retention decisions, disclosure to clients and deletion verification. This document does not establish PASSI compliance or prescribe a legally required 30-day or one-year retention period.

## 6. References

- [ANSSI — PASSI certification](https://cyber.gouv.fr/offre-de-service/certification-des-prestataires-daudit-de-securite-informatique/)
- [OWASP Automated Threats to Web Applications](https://owasp.org/www-project-automated-threats-to-web-applications/)
- [French Penal Code, Article 323-1](https://www.legifrance.gouv.fr/codes/article_lc/LEGIARTI000006418292)
