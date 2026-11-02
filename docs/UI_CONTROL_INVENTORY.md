# Supplied UI control inventory

**Source baseline:** `7ae5aa1` plus the current integration batch. Generated from all 22 production `ui_v2_*.html` templates using the stdlib HTML parser in `tests/test_web_ui_v2_control_inventory.py`. Regenerate after template changes. No supplied design was changed.

## Evidence boundary

This is a complete **static source-control registry**, not a declaration that every control is live or accepted. It covers anchors, buttons, inputs, selects, textareas, summaries explicit button/link roles, inline event handlers, focusable tabindex and editable elements, including initially hidden controls. IDs are template plus one-based line:column; minified shell markup can share a line. Controls dynamically created by JavaScript, computed CSS visibility, event delegation and backend permissions require runtime inspection.

`source-hidden` includes an explicit hidden ancestor/class/style and can be responsive; `disabled` is declared disabled; `declared-nav` has a canonical href; `inline-handler` declares JavaScript; `script-reference` only means an ID/data-path occurs in an inline script, **not** that an event handler or backend works; `unresolved-static` means no binding was established by this conservative inspection. Unresolved controls are review items, not automatically dead controls. Every source row retains its binding evidence for follow-up.

## Acceptance still open

- The cross-page browser contract checks all 22 rendered destinations and rejects visible placeholder/unknown sidebar links after page scripts run. Page-specific tests remain the behavioral evidence for other controls.
- Complete runtime action/service/authorization mapping for every visible control, including loading/error/cancellation/reconnect states and generated controls.
- Visual comparison against approved supplied reference choices; no screenshot baselines were fabricated or auto-approved.
- Keyboard/focus/screen-reader/non-color/manual accessibility acceptance. Static labels and ordinary Playwright clicks do not close it.
- Full CLI/API/UI operation parity and deliberate-difference register, plus deployment tests for external fonts/Tailwind/icons/images.

## Page summary

| Template | Controls | Source-hidden | Disabled | Declared nav | Inline handler | Script reference | Unresolved static |
|---|---:|---:|---:|---:|---:|---:|---:|
| ui_v2_adapters.html | 48 | 0 | 1 | 0 | 0 | 21 | 26 |
| ui_v2_ai.html | 21 | 0 | 0 | 0 | 0 | 16 | 5 |
| ui_v2_approvals.html | 37 | 9 | 0 | 0 | 10 | 4 | 14 |
| ui_v2_audit.html | 43 | 0 | 0 | 0 | 13 | 17 | 13 |
| ui_v2_bas.html | 32 | 0 | 0 | 0 | 0 | 20 | 12 |
| ui_v2_bug_bounty.html | 32 | 0 | 0 | 0 | 0 | 16 | 16 |
| ui_v2_chains.html | 25 | 0 | 0 | 0 | 0 | 15 | 10 |
| ui_v2_compliance.html | 40 | 0 | 0 | 0 | 0 | 20 | 20 |
| ui_v2_dashboard.html | 35 | 2 | 0 | 0 | 0 | 21 | 12 |
| ui_v2_diagnostics.html | 33 | 0 | 0 | 0 | 12 | 17 | 4 |
| ui_v2_evidence.html | 35 | 0 | 0 | 0 | 0 | 14 | 21 |
| ui_v2_findings.html | 25 | 0 | 0 | 1 | 4 | 7 | 13 |
| ui_v2_history.html | 31 | 0 | 3 | 0 | 0 | 16 | 12 |
| ui_v2_monitoring.html | 45 | 0 | 0 | 0 | 0 | 19 | 26 |
| ui_v2_ptaas.html | 42 | 5 | 0 | 0 | 11 | 17 | 9 |
| ui_v2_report.html | 22 | 1 | 0 | 1 | 0 | 5 | 15 |
| ui_v2_reports.html | 21 | 1 | 0 | 0 | 0 | 5 | 15 |
| ui_v2_retest.html | 36 | 0 | 0 | 0 | 0 | 14 | 22 |
| ui_v2_run.html | 37 | 0 | 0 | 1 | 7 | 9 | 20 |
| ui_v2_scope.html | 39 | 25 | 1 | 1 | 0 | 10 | 2 |
| ui_v2_settings.html | 61 | 15 | 0 | 0 | 12 | 15 | 19 |
| ui_v2_threat_intel.html | 53 | 0 | 0 | 0 | 13 | 20 | 20 |

**Total:** 793 source controls across 22 templates.

## Exact source registry

Labels and binding excerpts are shortened for readability; line:column identifies the complete source. No truncation changes the count or classification.

### ui_v2_adapters.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 7:4579 | a | Dashboard / Zero State | script-reference | # |
| 7:4836 | a | Scope & Targets | script-reference | # |
| 7:5087 | a | Run & Orchestration | script-reference | # |
| 7:5346 | a | Trust Layer & Findings | script-reference | # |
| 7:5611 | a | PTES Coverage & Reports | script-reference | # |
| 7:6086 | a | AI Strategy Gate | script-reference | # |
| 7:6333 | a | Remediation Retest Studio | script-reference | # |
| 7:6598 | a | Correlated Attack Chains | script-reference | # |
| 7:7061 | a | Job Execution History | script-reference | # |
| 7:7317 | a | Evidence File Inspector | script-reference | # |
| 7:7578 | a | Cryptographic Audit Log | unresolved-static | # |
| 7:8041 | a | System Diagnostics & Health | script-reference | # |
| 7:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 7:8585 | a | Settings & API Explorer | unresolved-static | # |
| 7:10949 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 7:11306 | button | add New | unresolved-static | — |
| 7:13011 | button | terminal Terminal Log | unresolved-static | — |
| 7:13350 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 18:1 | button | sync Sync whaxon.adapters | script-reference | btn-sync |
| 22:1 | button | restart_alt Reload Entry Points | script-reference | btn-reload |
| 26:1 | button | add_circle + Register New Adapter | script-reference | btn-register |
| 116:1 | input | Search adapters by tool name, entrypoint, author, tags... | script-reference | adapter-search |
| 121:1 | button | All (14) | unresolved-static | — |
| 124:1 | button | Recon (5) | unresolved-static | — |
| 127:1 | button | Vulnerability (4) | unresolved-static | — |
| 130:1 | button | Exploitation (3) | unresolved-static | — |
| 133:1 | button | Ingestion (2) | unresolved-static | — |
| 140:1 | select | All States Binary Found (12) Missing Binary (2) Untrusted (0) | script-reference | status-select |
| 188:1 | button | CONFIGURE tune | unresolved-static | — |
| 232:1 | button | CONFIGURE tune | unresolved-static | — |
| 276:1 | button | CONFIGURE tune | unresolved-static | — |
| 320:1 | button | CONFIGURE tune | unresolved-static | — |
| 363:1 | button | CONFIGURE tune | unresolved-static | — |
| 407:1 | button | CONFIGURE CONNECTION settings | unresolved-static | — |
| 451:1 | button | CONFIGURE tune | unresolved-static | — |
| 495:1 | button | CONFIGURE tune | unresolved-static | — |
| 545:1 | button | Close Panel | script-reference | close-drawer |
| 583:1 | button | Remove flag | unresolved-static | — |
| 587:1 | button | Remove flag | unresolved-static | — |
| 591:1 | button | Remove flag | unresolved-static | — |
| 595:1 | button | Remove flag | unresolved-static | — |
| 597:1 | input | + Add CLI parameter... | unresolved-static | add-flag-input |
| 631:1 | input | (unnamed) | unresolved-static | — |
| 638:1 | input | (unnamed) | disabled | — |
| 645:1 | input | (unnamed) | unresolved-static | — |
| 661:1 | button | play_arrow Test Adapter Execution with Mock Output | script-reference | btn-mock-test |
| 666:1 | button | Re-sign Manifest | script-reference | btn-resign |
| 669:1 | button | Save Configuration | script-reference | btn-save-conf |

### ui_v2_ai.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4579 | a | Dashboard / Zero State | script-reference | # |
| 4:4836 | a | Scope & Targets | script-reference | # |
| 4:5087 | a | Run & Orchestration | script-reference | # |
| 4:5346 | a | Trust Layer & Findings | script-reference | # |
| 4:5611 | a | PTES Coverage & Reports | script-reference | # |
| 4:6086 | a | AI Strategy Gate | script-reference | # |
| 4:6332 | a | Remediation Retest Studio | script-reference | # |
| 4:6597 | a | Correlated Attack Chains | script-reference | # |
| 4:7060 | a | Job Execution History | script-reference | # |
| 4:7317 | a | Evidence File Inspector | script-reference | # |
| 4:7578 | a | Cryptographic Audit Log | script-reference | # |
| 4:8041 | a | System Diagnostics & Health | script-reference | # |
| 4:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 4:8585 | a | Settings & API Explorer | script-reference | # |
| 4:10949 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 4:11306 | button | add New | unresolved-static | — |
| 4:13011 | button | terminal Terminal Log | unresolved-static | — |
| 4:13350 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 84:1 | button | close Reject & Re-plan [Esc] | script-reference | btn-reject |
| 91:1 | button | bolt Authorize & Execute [Enter] | script-reference | btn-authorize |
| 258:1 | button | content_copy Copy | unresolved-static | — |

### ui_v2_approvals.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | target Scope & Targets | script-reference | # |
| 4:4807 | a | terminal Run & Orchestration | script-reference | # |
| 4:5149 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5502 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9037 | button | terminal Terminal Log | unresolved-static | — |
| 4:9376 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 30:1 | button | replay Retest Verified Scope | inline-handler | runRetestAll() |
| 126:1 | button | ALL | unresolved-static | — |
| 127:1 | button | CRIT (1) | unresolved-static | — |
| 128:1 | button | HIGH (2) | unresolved-static | — |
| 129:1 | button | MED (1) | unresolved-static | — |
| 130:1 | button | LOW (0) | unresolved-static | — |
| 135:1 | button | VERIFIED (6) | unresolved-static | — |
| 136:1 | button | CANDIDATE (11) | unresolved-static | — |
| 137:1 | button | REVIEW NEEDED | unresolved-static | — |
| 142:1 | button | Nuclei | unresolved-static | — |
| 143:1 | button | sqlmap | unresolved-static | — |
| 144:1 | button | Nikto | unresolved-static | — |
| 149:1 | input | Filter proof pattern, URL, CVE... | unresolved-static | — |
| 164:1 | div | CRITICAL SQLi: Time-based Blind VERIFIED /api/v1/catalog/items?id= C | inline-handler | selectFinding(1) |
| 191:1 | div | HIGH Stored Cross-Site Scripting (XSS) VERIFIED /v1/reviews/post (co | inline-handler | selectFinding(2) |
| 218:1 | div | HIGH BOLA Authorization Bypass CANDIDATE /api/v2/tenant/billing (ten | inline-handler | selectFinding(3) |
| 245:1 | div | MEDIUM Exposed .env Backup Secret File VERIFIED /backup/.env.product | inline-handler | selectFinding(4) |
| 332:1 | button | content_copy Copy Command | inline-handler | copyProofCurl() |
| 407:1 | button | play_arrow Replay Test (Retest) | inline-handler | triggerReplayAction() |
| 411:1 | button | check Mark Fixed | inline-handler | markFixedAction() |
| 417:1 | button | file_export Export Proof to Issue Tracker | inline-handler | exportProofAction() |
| 421:1 | button | how_to_reg Send to Approvals | inline-handler | sendToApprovalsAction() |
| 521:1518 | button | close | source-hidden | document.getElementById('approvals-modal').remove() |
| 529:600 | input | (unnamed) | source-hidden | — |
| 529:1089 | input | (unnamed) | source-hidden | — |
| 529:1561 | input | (unnamed) | source-hidden | — |
| 529:2020 | textarea | Cross-tenant billing data was exposed in JSON response payload despi | source-hidden | — |
| 529:2759 | button | redo Skip Item | source-hidden | — |
| 529:3032 | button | Refute / False Positive | source-hidden | document.getElementById('approvals-modal').remove() |
| 529:3289 | button | Hold for Retest | source-hidden | document.getElementById('approvals-modal').remove() |
| 529:3573 | button | how_to_reg Approve as Verified (Sign Proof) | source-hidden | document.getElementById('approvals-modal').remove() |

### ui_v2_audit.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4579 | a | Dashboard / Zero State | script-reference | # |
| 4:4836 | a | Scope & Targets | script-reference | # |
| 4:5087 | a | Run & Orchestration | script-reference | # |
| 4:5346 | a | Trust Layer & Findings | script-reference | # |
| 4:5611 | a | PTES Coverage & Reports | script-reference | # |
| 4:6086 | a | AI Strategy Gate | script-reference | # |
| 4:6333 | a | Remediation Retest Studio | script-reference | # |
| 4:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 4:6895 | a | Correlated Attack Chains | script-reference | # |
| 4:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 4:7443 | a | PTaaS Client Portal | script-reference | # |
| 4:7896 | a | Job Execution History | script-reference | # |
| 4:8153 | a | Evidence File Inspector | script-reference | # |
| 4:8414 | a | Cryptographic Audit Log | script-reference | # |
| 4:8876 | a | System Diagnostics & Health | script-reference | # |
| 4:9151 | a | Adapter & Plugin Manager | script-reference | # |
| 4:9420 | a | Settings & Secrets Vault | script-reference | # |
| 4:11786 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 4:12143 | button | add New | unresolved-static | — |
| 4:13848 | button | terminal Terminal Log | unresolved-static | — |
| 4:14187 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 38:1 | button | sync Verify Entire Merkle Root | inline-handler | triggerMerkleVerification() |
| 42:1 | button | enhanced_encryption Export Attestation (.sig) | inline-handler | downloadSigAttestation() |
| 157:1 | input | Search seq #, actor ID, SHA-256 digest, or payload target... | inline-handler | ledger-search |
| 162:1 | select | ALL SIGNALS (6) SCOPE MODIFICATION FINDING VERIFICATION PAYLOAD DETO | inline-handler | category-filter |
| 171:1 | button | shield SEALED ONLY | unresolved-static | — |
| 178:1 | button | chevron_left | unresolved-static | — |
| 181:1 | button | chevron_right | unresolved-static | — |
| 203:1 | tr | 2026-03-30T14:22:08.892401Z #EVT-9941 Finding Verified person OP//77 | inline-handler | selectEvent('EVT-9941') |
| 235:1 | button | Inspect Hash Tree | unresolved-static | — |
| 241:1 | tr | 2026-03-30T14:18:41.119830Z #EVT-9940 Scope Change key OP//4108-BRAV | inline-handler | selectEvent('EVT-9940') |
| 273:1 | button | Inspect Hash Tree | unresolved-static | — |
| 279:1 | tr | 2026-03-30T14:05:12.601944Z #EVT-9939 Payload Detonation memory AUTO | inline-handler | selectEvent('EVT-9939') |
| 311:1 | button | Inspect Hash Tree | unresolved-static | — |
| 317:1 | tr | 2026-03-30T13:42:01.002195Z #EVT-9938 Emergency Halt gavel OP//7749- | inline-handler | selectEvent('EVT-9938') |
| 349:1 | button | Inspect Hash Tree | unresolved-static | — |
| 355:1 | tr | 2026-03-30T13:15:55.441920Z #EVT-9937 Tool Invocation terminal DAEMO | inline-handler | selectEvent('EVT-9937') |
| 386:1 | button | Inspect Hash Tree | unresolved-static | — |
| 392:1 | tr | 2026-03-30T12:59:10.104510Z #EVT-9936 Policy Override verified_user  | inline-handler | selectEvent('EVT-9936') |
| 423:1 | button | Inspect Hash Tree | unresolved-static | — |
| 446:1 | button | content_copy Copy Raw Hex | inline-handler | copyRawProof() |
| 561:1 | button | gavel Court-Ready Forensic Bundle (.zip) | inline-handler | downloadCourtReadyPackage() |
| 565:1 | button | Cryptographic QR Verification Slip | inline-handler | generateQrCert() |

### ui_v2_bas.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 5:6895 | a | Correlated Attack Chains | script-reference | # |
| 5:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 5:7443 | a | Threat Intel & Exploit Arsenal | script-reference | # |
| 5:7724 | a | BAS & Detection Validation | script-reference | # |
| 5:8209 | a | Job Execution History | script-reference | # |
| 5:8466 | a | Evidence File Inspector | script-reference | # |
| 5:8727 | a | Cryptographic Audit Log | script-reference | # |
| 5:8988 | a | Compliance & Framework Crosswalk | script-reference | # |
| 5:9473 | a | System Diagnostics & Health | script-reference | # |
| 5:9748 | a | Adapter & Plugin Manager | script-reference | # |
| 5:10017 | a | PTaaS Client Portal | script-reference | # |
| 5:10270 | a | Settings & Secrets Vault | script-reference | # |
| 5:12636 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:12993 | button | add New | unresolved-static | — |
| 5:14698 | button | terminal Terminal Log | unresolved-static | — |
| 5:15037 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 40:1 | button | play_circle Detonate Sequence | unresolved-static | — |
| 44:1 | button | chevron_forward Query Blue Telemetry | unresolved-static | — |
| 48:1 | button | assessment Gap Report | unresolved-static | — |
| 443:1 | button | tune Configure Vector Filters | unresolved-static | — |
| 495:1 | button | Push Rule to SIEM | unresolved-static | — |
| 573:1 | button | download Export Validation Matrix (Navigator JSON + PDF) | unresolved-static | — |
| 601:1 | button | rocket_launch Deploy to Sentinel | unresolved-static | — |
| 628:1 | button | publish Deploy to Splunk | unresolved-static | — |

### ui_v2_bug_bounty.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 206:1124 | a | terminal Dashboard / Zero State | script-reference | # |
| 206:1479 | a | radar Scope & Targets | script-reference | # |
| 206:1821 | a | play_circle Run & Orchestration | script-reference | # |
| 206:2177 | a | verified_user Trust Layer & Findings | script-reference | # |
| 206:2541 | a | description PTES Coverage & Reports | script-reference | # |
| 206:3082 | a | psychology AI Strategy Gate | script-reference | # |
| 206:3429 | a | build_circle Remediation Retest Studio | script-reference | # |
| 206:3796 | a | account_tree Correlated Attack Chains | script-reference | # |
| 206:4161 | a | open_in_browser Bug Bounty & Live Browser | script-reference | # |
| 206:4702 | a | history_toggle_off Job Execution History | script-reference | # |
| 206:5067 | a | folder_zip Evidence File Inspector | script-reference | # |
| 206:5428 | a | encrypted Cryptographic Audit Log | script-reference | # |
| 206:5957 | a | monitor_heart System Diagnostics & Health | script-reference | # |
| 206:6331 | a | extension Adapter & Plugin Manager | script-reference | # |
| 206:6695 | a | shield_person PTaaS Client Portal | script-reference | # |
| 206:7051 | a | key Settings & Secrets Vault | script-reference | # |
| 206:8931 | button | terminal LOGS | unresolved-static | — |
| 206:9234 | button | dangerous HALT SCAN | unresolved-static | — |
| 305:1 | button | Go back | unresolved-static | — |
| 306:1 | button | Go forward | unresolved-static | — |
| 307:1 | button | Reload target view | unresolved-static | — |
| 313:1 | input | (unnamed) | unresolved-static | — |
| 320:1 | select | User_A (Attacker Context) User_B (Victim / Target #092) Unauthentica | unresolved-static | — |
| 384:1 | input | (unnamed) | unresolved-static | — |
| 389:1 | input | (unnamed) | unresolved-static | — |
| 414:1 | button | send EXECUTE COMMIT (TAMPERED) | unresolved-static | — |
| 439:1 | button | CLEAR CACHE | unresolved-static | — |
| 440:1 | button | DUMP DOM SNAPSHOT | unresolved-static | — |
| 555:1 | button | terminal INSPECTOR: POST /app/transfer/commit | unresolved-static | — |
| 595:1 | button | cached SEND TO VALIDATOR | unresolved-static | — |
| 599:1 | button | difference DIFF ANALYSIS | unresolved-static | — |
| 603:1 | button | verified_user PROMOTE TO FINDING | unresolved-static | — |

### ui_v2_chains.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Correlated Attack Chains | script-reference | # |
| 5:7061 | a | Job Execution History | script-reference | # |
| 5:7318 | a | Evidence File Inspector | script-reference | # |
| 5:7579 | a | Cryptographic Audit Log | script-reference | # |
| 5:8042 | a | System Diagnostics & Health | script-reference | # |
| 5:8317 | a | Adapter & Plugin Manager | script-reference | # |
| 5:8586 | a | Settings & API Explorer | script-reference | # |
| 5:10950 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:11307 | button | add New | unresolved-static | — |
| 5:13012 | button | terminal Terminal Log | unresolved-static | — |
| 5:13351 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 29:1 | button | sync_saved_locally Re-compute Graph | script-reference | btn-recompute |
| 35:1 | select | Severity: All Vectors Severity: Critical & Compound 10.0 Severity: H | unresolved-static | — |
| 41:1 | button | download Export Graph SVG/JSON | unresolved-static | — |
| 338:1 | button | play_arrow Simulate Controlled Replay | unresolved-static | — |
| 342:1 | button | menu_book Export PTES Chapter | unresolved-static | — |
| 429:1 | button | Add Custom Mitigation Rule (Envoy WAF) | unresolved-static | — |
| 432:1 | button | Generate Red Team Retest Script | unresolved-static | — |

### ui_v2_compliance.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 5:6895 | a | Correlated Attack Chains | script-reference | # |
| 5:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 5:7443 | a | Threat Intel & Exploit Arsenal | script-reference | # |
| 5:7724 | a | BAS & Detection Validation | script-reference | # |
| 5:8209 | a | Job Execution History | script-reference | # |
| 5:8466 | a | Evidence File Inspector | script-reference | # |
| 5:8727 | a | Cryptographic Audit Log | script-reference | # |
| 5:8988 | a | Compliance & Framework Crosswalk | script-reference | # |
| 5:9473 | a | System Diagnostics & Health | script-reference | # |
| 5:9748 | a | Adapter & Plugin Manager | script-reference | # |
| 5:10017 | a | PTaaS Client Portal | script-reference | # |
| 5:10270 | a | Settings & Secrets Vault | script-reference | # |
| 5:12636 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:12993 | button | add New | unresolved-static | — |
| 5:14698 | button | terminal Terminal Log | unresolved-static | — |
| 5:15037 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 22:1 | button | tune Configure Scope | unresolved-static | — |
| 26:1 | button | picture_as_pdf Auditor Crosswalk PDF | unresolved-static | — |
| 30:1 | button | archive Export Package (.ZIP) | unresolved-static | — |
| 201:1 | button | PCI-DSS v4.0 (5) | unresolved-static | — |
| 204:1 | button | OWASP Top 10 (4) | unresolved-static | — |
| 207:1 | button | SOC 2 Type II (8) | unresolved-static | — |
| 210:1 | button | ISO 27001 (6) | unresolved-static | — |
| 213:1 | button | NIST CSF (3) | unresolved-static | — |
| 216:1 | button | MITRE ATT&CK | unresolved-static | — |
| 423:1 | button | PREV | unresolved-static | — |
| 425:1 | button | NEXT | unresolved-static | — |
| 479:1 | input | (unnamed) | unresolved-static | — |
| 486:1 | input | (unnamed) | unresolved-static | — |
| 493:1 | input | (unnamed) | unresolved-static | — |
| 500:1 | input | (unnamed) | unresolved-static | — |
| 522:1 | button | lock_clock Compile Signed Matrix (.PDF / .JSON) | unresolved-static | — |

### ui_v2_dashboard.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 17:4342 | a | Dashboard / Zero State | script-reference | # |
| 17:4598 | a | Scope & Targets | script-reference | # |
| 17:4849 | a | Run & Orchestration | script-reference | # |
| 17:5108 | a | Trust Layer & Findings | script-reference | # |
| 17:5373 | a | PTES Coverage & Reports | script-reference | # |
| 17:5848 | a | AI Strategy Gate | script-reference | # |
| 17:6095 | a | Remediation Retest Studio | script-reference | # |
| 17:6360 | a | Correlated Attack Chains | script-reference | # |
| 17:6823 | a | Job Execution History | script-reference | # |
| 17:7080 | a | Evidence File Inspector | script-reference | # |
| 17:7341 | a | Cryptographic Audit Log | script-reference | # |
| 17:7804 | a | System Diagnostics & Health | script-reference | # |
| 17:8079 | a | Adapter & Plugin Manager | script-reference | # |
| 17:8348 | a | Settings & API Explorer | script-reference | # |
| 17:8813 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 17:9110 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 17:9395 | a | PTaaS Client Portal | script-reference | # |
| 17:9648 | a | Threat Intelligence | script-reference | # |
| 17:9914 | a | BAS & Detection Validation | script-reference | # |
| 17:10187 | a | Compliance & Framework Crosswalk | script-reference | # |
| 17:10472 | a | Trust Layer Approvals Queue | script-reference | # |
| 17:12865 | button | No active engagement (No target selected) arrow_drop_down | unresolved-static | — |
| 17:13230 | button | add New | unresolved-static | — |
| 17:14943 | button | terminal Terminal Log | unresolved-static | — |
| 17:15282 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 39:1 | button | terminal CLI Help | unresolved-static | — |
| 43:1 | button | vpn_key Update Credentials Now | unresolved-static | — |
| 84:1 | button | history Switch Target Session | unresolved-static | — |
| 88:1 | button | rocket_launch Start New Engagement | unresolved-static | — |
| 199:1 | button | Open Scope Setup arrow_forward | source-hidden | — |
| 238:1 | button | upload Upload Artifact | unresolved-static | — |
| 279:1 | button | play_arrow Deploy Mock | unresolved-static | — |
| 304:1 | button | tune Configure Filters | source-hidden | — |
| 397:1 | input | Filter recent job history by ID, target, or tool | unresolved-static | — |
| 399:1 | button | download Export Archive | unresolved-static | — |

### ui_v2_diagnostics.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 7:4579 | a | Dashboard / Zero State | script-reference | # |
| 7:4836 | a | Scope & Targets | script-reference | # |
| 7:5087 | a | Run & Orchestration | script-reference | # |
| 7:5346 | a | Trust Layer & Findings | script-reference | # |
| 7:5611 | a | PTES Coverage & Reports | script-reference | # |
| 7:6086 | a | AI Strategy Gate | script-reference | # |
| 7:6333 | a | Remediation Retest Studio | script-reference | # |
| 7:6598 | a | Correlated Attack Chains | script-reference | # |
| 7:7061 | a | Job Execution History | script-reference | # |
| 7:7317 | a | Evidence File Inspector | script-reference | # |
| 7:7578 | a | Cryptographic Audit Log | script-reference | # |
| 7:8041 | a | System Diagnostics & Health | script-reference | # |
| 7:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 7:8585 | a | Settings & API Explorer | script-reference | # |
| 7:10949 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 7:11306 | button | add New | unresolved-static | — |
| 7:13011 | button | terminal Terminal Log | unresolved-static | — |
| 7:13350 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 42:1 | button | restart_alt Restart Engine Daemons | script-reference | btn-restart-daemons |
| 46:1 | button | file_download Export Health Report (.json) | script-reference | btn-export-json |
| 50:1 | button | play_circle Run Full Diagnostic [F5] | script-reference | btn-run-diag |
| 263:1 | button | Probe Socket | inline-handler | pingService('PostgreSQL') |
| 290:1 | button | Benchmark Cache | inline-handler | pingService('SQLite Replay') |
| 317:1 | button | Ping Handshake | inline-handler | pingService('Metasploit RPC') |
| 344:1 | button | Probe RingBuffer | inline-handler | pingService('eBPF Kernel') |
| 371:1 | button | Warmup Inference | inline-handler | pingService('AI Planner') |
| 398:1 | button | Check Queue | inline-handler | pingService('Redis Broker') |
| 425:1 | button | Verify Cgroup | inline-handler | pingService('Docker Sandbox') |
| 682:1 | button | Test MSF RPC Handshake | inline-handler | triggerSelfCheck('msf') |
| 685:1 | button | Benchmark SQLite Write Speed | inline-handler | triggerSelfCheck('sqlite') |
| 688:1 | button | Probe Ollama LLM Socket | inline-handler | triggerSelfCheck('llm') |
| 691:1 | button | Check eBPF Filter Integrity | inline-handler | triggerSelfCheck('ebpf') |
| 694:1 | button | Clear Console | inline-handler | clearTerminalLogs() |

### ui_v2_evidence.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 6:4579 | a | Dashboard / Zero State | script-reference | # |
| 6:4836 | a | Scope & Targets | script-reference | # |
| 6:5087 | a | Run & Orchestration | script-reference | # |
| 6:5346 | a | Trust Layer & Findings | script-reference | # |
| 6:5611 | a | PTES Coverage & Reports | script-reference | # |
| 6:6086 | a | AI Strategy Gate | script-reference | # |
| 6:6333 | a | Remediation Retest Studio | script-reference | # |
| 6:6598 | a | Correlated Attack Chains | script-reference | # |
| 6:7060 | a | Job Execution History | script-reference | # |
| 6:7317 | a | Evidence File Inspector | script-reference | # |
| 6:7578 | a | Cryptographic Audit Log | script-reference | # |
| 6:8041 | a | System Diagnostics & Health | script-reference | # |
| 6:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 6:8585 | a | Settings & API Explorer | script-reference | # |
| 6:10949 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 6:11306 | button | add New | unresolved-static | — |
| 6:13011 | button | terminal Terminal Log | unresolved-static | — |
| 6:13350 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 46:1 | button | cloud_sync Sync Merkle Tree | unresolved-static | — |
| 50:1 | button | inventory_2 Export TAR.GZ | unresolved-static | — |
| 145:1 | button | Collapse all | unresolved-static | — |
| 148:1 | button | Refresh | unresolved-static | — |
| 157:1 | input | Search filename, sha256, tool... | unresolved-static | — |
| 319:1 | button | content_copy Copy | unresolved-static | — |
| 361:1 | button | Formatted Tree View | unresolved-static | — |
| 364:1 | button | Raw XML Source | unresolved-static | — |
| 367:1 | button | Parsed Tables | unresolved-static | — |
| 370:1 | button | Hex View | unresolved-static | — |
| 387:1 | button | download Download Raw | unresolved-static | — |
| 391:1 | button | fingerprint Verify SHA-256 Hash | unresolved-static | — |
| 395:1 | button | auto_fix_high Re-parse into Finding Model | unresolved-static | — |
| 399:1 | button | send_to_mobile Send to Issue Tracker | unresolved-static | — |
| 600:1 | a | Entry #4409 | unresolved-static | # |
| 642:1 | button | Trace Proof | unresolved-static | — |
| 658:1 | button | Trace Proof | unresolved-static | — |

### ui_v2_findings.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4470 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 4:4816 | a | target Scope & Targets | script-reference | # |
| 4:5148 | a | terminal Run & Orchestration | script-reference | # |
| 4:5490 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5843 | a | analytics PTES Coverage & Reports | script-reference | # |
| 30:1 | button | replay Retest Verified Scope | inline-handler | runRetestAll() |
| 126:1 | button | ALL | unresolved-static | — |
| 127:1 | button | CRIT (1) | unresolved-static | — |
| 128:1 | button | HIGH (2) | unresolved-static | — |
| 129:1 | button | MED (1) | unresolved-static | — |
| 130:1 | button | LOW (0) | unresolved-static | — |
| 135:1 | button | ALL | unresolved-static | — |
| 136:1 | button | VERIFIED (6) | unresolved-static | — |
| 137:1 | button | CANDIDATE (11) | unresolved-static | — |
| 138:1 | button | REVIEW NEEDED | unresolved-static | — |
| 143:1 | button | ALL | unresolved-static | — |
| 144:1 | button | Nuclei | unresolved-static | — |
| 145:1 | button | sqlmap | unresolved-static | — |
| 146:1 | button | Nikto | unresolved-static | — |
| 151:1 | input | Filter findings by proof pattern, URL, or CVE | script-reference | whaxon-finding-filter |
| 247:1 | button | content_copy Copy Evidence | script-reference | copy-btn |
| 309:1 | button | play_arrow Replay Test (Retest) | script-reference | replay-btn |
| 313:1 | button | check Mark Fixed | inline-handler | markFixedAction() |
| 319:1 | button | file_export Export Proof to Issue Tracker | inline-handler | exportProofAction() |
| 323:1 | button | how_to_reg Send to Approvals | inline-handler | sendToApprovalsAction() |

### ui_v2_history.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 6:4579 | a | Dashboard / Zero State | script-reference | # |
| 6:4836 | a | Scope & Targets | script-reference | # |
| 6:5087 | a | Run & Orchestration | script-reference | # |
| 6:5346 | a | Trust Layer & Findings | script-reference | # |
| 6:5611 | a | PTES Coverage & Reports | script-reference | # |
| 6:6086 | a | AI Strategy Gate | script-reference | # |
| 6:6333 | a | Remediation Retest Studio | script-reference | # |
| 6:6598 | a | Correlated Attack Chains | script-reference | # |
| 6:7060 | a | Job Execution History | script-reference | # |
| 6:7317 | a | Evidence File Inspector | script-reference | # |
| 6:7578 | a | Cryptographic Audit Log | script-reference | # |
| 6:8041 | a | System Diagnostics & Health | script-reference | # |
| 6:8316 | a | Adapter & Plugin Manager | script-reference | # |
| 6:8585 | a | Settings & API Explorer | script-reference | # |
| 6:10949 | button | No engagement selected (No target selected) arrow_drop_down | unresolved-static | — |
| 6:11316 | button | add New | unresolved-static | — |
| 6:13022 | button | terminal Terminal Log | unresolved-static | — |
| 6:13361 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 26:1 | button | file_download Export Ledger (.csv / .json) | unresolved-static | — |
| 31:1 | button | verified_user Verify Integrity | unresolved-static | — |
| 133:1 | input | Filter history by recorded job ID, tool, or target | script-reference | history-search |
| 140:1 | select | Filter history by tool | script-reference | history-tool-filter |
| 147:1 | select | Date filter unavailable because timestamps are not recorded | disabled | history-date-filter |
| 154:1 | select | Runner filter unavailable because runner mode is not recorded | disabled | history-runner-filter |
| 163:1 | button | All (42) | unresolved-static | — |
| 167:1 | button | Success (38) | unresolved-static | — |
| 172:1 | button | Failed (3) | unresolved-static | — |
| 177:1 | button | Scope-Blocked (1) | unresolved-static | — |
| 182:1 | button | Active / Queued (0) | unresolved-static | — |
| 226:1 | button | chevron_left | disabled | — |
| 229:1 | button | chevron_right | unresolved-static | — |

### ui_v2_monitoring.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4579 | a | Dashboard / Zero State | script-reference | # |
| 4:4836 | a | Scope & Targets | script-reference | # |
| 4:5087 | a | Run & Orchestration | script-reference | # |
| 4:5346 | a | Trust Layer & Findings | script-reference | # |
| 4:5611 | a | PTES Coverage & Reports | script-reference | # |
| 4:6086 | a | AI Strategy Gate | script-reference | # |
| 4:6333 | a | Remediation Retest Studio | script-reference | # |
| 4:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 4:6895 | a | Correlated Attack Chains | script-reference | # |
| 4:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 4:7443 | a | PTaaS Client Portal | script-reference | # |
| 4:7896 | a | Job Execution History | script-reference | # |
| 4:8153 | a | Evidence File Inspector | script-reference | # |
| 4:8414 | a | Cryptographic Audit Log | script-reference | # |
| 4:8877 | a | System Diagnostics & Health | script-reference | # |
| 4:9152 | a | Adapter & Plugin Manager | script-reference | # |
| 4:9421 | a | Settings & Secrets Vault | script-reference | # |
| 4:11787 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 4:12144 | button | add New | unresolved-static | — |
| 4:13849 | button | terminal Terminal Log | unresolved-static | — |
| 4:14188 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 28:1 | button | dns Configure Cloud & DNS Probes | unresolved-static | — |
| 32:1 | button | radar Trigger Delta Recon Now | script-reference | recon-trigger-btn |
| 133:1 | input | Filter FQDN, IP, ASN (e.g. AS13335, 10.0.0.0/8), Cloud Provider... | script-reference | asset-search-input |
| 138:1 | button | All Infra | unresolved-static | — |
| 141:1 | button | AWS (84) | unresolved-static | — |
| 145:1 | button | GCP (36) | unresolved-static | — |
| 149:1 | button | CF (22) | unresolved-static | — |
| 158:1 | button | ALL (142) | unresolved-static | — |
| 161:1 | button | DRIFT DETECTED 7 | unresolved-static | — |
| 165:1 | button | CLOUD EXPOSURES 4 | unresolved-static | — |
| 169:1 | button | EXPIRED/WEAK TLS 3 | unresolved-static | — |
| 176:1 | button | SEVERITY DESC arrow_downward | unresolved-static | — |
| 217:1 | button | Lock Boundary | unresolved-static | — |
| 221:1 | button | Direct Dynamic Inspection | unresolved-static | — |
| 273:1 | button | Remediate S3 Bucket ACL | unresolved-static | — |
| 277:1 | button | Inspect Bucket Contents | unresolved-static | — |
| 323:1 | button | Order ACME Renewal | unresolved-static | — |
| 327:1 | button | tune Harden Ciphers | unresolved-static | — |
| 364:1 | button | terminal Session Shell | unresolved-static | — |
| 368:1 | button | more_vert | unresolved-static | — |
| 385:1 | button | PREV | unresolved-static | — |
| 386:1 | button | NEXT | unresolved-static | — |
| 475:1 | button | Expand Canvas open_in_full | unresolved-static | — |
| 592:1 | button | Stream Full Cryptographic Audit Logs → | unresolved-static | — |

### ui_v2_ptaas.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 206:1124 | a | terminal Dashboard / Zero State | script-reference | # |
| 206:1479 | a | radar Scope & Targets | script-reference | # |
| 206:1821 | a | play_circle Run & Orchestration | script-reference | # |
| 206:2177 | a | verified_user Trust Layer & Findings | script-reference | # |
| 206:2541 | a | description PTES Coverage & Reports | script-reference | # |
| 206:3082 | a | psychology AI Strategy Gate | script-reference | # |
| 206:3429 | a | build_circle Remediation Retest Studio | script-reference | # |
| 206:3796 | a | account_tree Correlated Attack Chains | script-reference | # |
| 206:4161 | a | open_in_browser Bug Bounty & Live Browser | script-reference | # |
| 206:4702 | a | history_toggle_off Job Execution History | script-reference | # |
| 206:5067 | a | folder_zip Evidence File Inspector | script-reference | # |
| 206:5428 | a | encrypted Cryptographic Audit Log | script-reference | # |
| 206:5957 | a | monitor_heart System Diagnostics & Health | script-reference | # |
| 206:6331 | a | extension Adapter & Plugin Manager | script-reference | # |
| 206:6695 | a | shield_person PTaaS Client Portal | script-reference | # |
| 206:7052 | a | key Settings & Secrets Vault | script-reference | # |
| 206:8932 | button | terminal LOGS | unresolved-static | — |
| 206:9235 | button | dangerous HALT SCAN | unresolved-static | — |
| 254:1 | button | add_moderator EXPAND SCOPE | inline-handler | openScopeModal() |
| 258:1 | button | schedule SCHEDULE RETEST | inline-handler | scrollToRetestConsole() |
| 262:1 | button | workspace_premium EXECUTIVE CERTIFICATE | inline-handler | triggerCertDownload() |
| 377:1 | input | e.g. stage-auth.stripe-internal.dev | script-reference | targetInput |
| 378:1 | button | RUN PRE-FLIGHT | inline-handler | runPreflightValidation() |
| 397:1 | input | (unnamed) | unresolved-static | — |
| 404:1 | input | (unnamed) | unresolved-static | — |
| 411:1 | input | (unnamed) | unresolved-static | — |
| 417:1 | button | rocket_launch DISPATCH ACCREDITED JOB | inline-handler | launchAssessment() |
| 437:1 | button | ALL (18) | unresolved-static | — |
| 438:1 | button | ACTION NEEDED (4) | unresolved-static | — |
| 439:1 | button | RESOLVED (14) | unresolved-static | — |
| 467:1 | button | VIEW RAW PACKET open_in_new | inline-handler | toggleProof('proof-1') |
| 493:1 | button | refresh REQUEST VERIFICATION RETEST | inline-handler | requestRetest('BOLA / IDOR in Merchant Transfer Settlement Route') |
| 523:1 | button | VIEW SCRIPT open_in_new | inline-handler | toggleProof('proof-2') |
| 619:1 | div | picture_as_pdf Executive Brief (PDF) v2.1 • 14 Pages • Cryptographic | inline-handler | downloadArtifact('Executive_Brief_Q4.pdf') |
| 632:1 | div | slideshow Board-Ready Deck (Slides) Keynote & PPTX • High-level KPIs | inline-handler | downloadArtifact('Board_Risk_Deck_2026.key') |
| 645:1 | div | table_chart Remediation Matrix (Jira CSV) Atlassian Schema • CVSS v3 | inline-handler | downloadArtifact('Findings_Jira_Sync.csv') |
| 683:1 | button | PING SEC-OPS | unresolved-static | — |
| 698:1 | button | close | source-hidden | closeScopeModal() |
| 705:1 | textarea | e.g. api-v3-staging.internal.stripe.com 192.168.12.0/24 (VPC Peered) | source-hidden | — |
| 711:1 | select | Synchronized with Primary RoE (Now through Nov 02, 2026) Restricted  | source-hidden | — |
| 722:1 | button | CANCEL | source-hidden | closeScopeModal() |
| 725:1 | button | SIGN & SUBMIT ROE ADDENDUM | source-hidden | confirmScopeExpansion() |

### ui_v2_report.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 4:4821 | a | target Scope & Targets | script-reference | # |
| 4:5153 | a | terminal Run & Orchestration | script-reference | # |
| 4:5495 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5848 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9396 | button | terminal Terminal Log | unresolved-static | — |
| 4:9735 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 279:1 | button | All Gaps (3) | unresolved-static | — |
| 280:1 | button | Policy (2) | unresolved-static | — |
| 281:1 | button | Safety (1) | unresolved-static | — |
| 363:1 | input | (unnamed) | unresolved-static | — |
| 371:1 | input | (unnamed) | unresolved-static | — |
| 379:1 | input | (unnamed) | unresolved-static | — |
| 387:1 | input | (unnamed) | unresolved-static | — |
| 428:1 | button | visibility Preview Markdown | script-reference | previewBtn |
| 432:1 | button | data_object Export Findings (.json) | unresolved-static | — |
| 436:1 | button | download Download Full Report (.pdf) | unresolved-static | — |
| 489:1 | a | download Raw | unresolved-static | # |
| 504:1 | a | download Raw | unresolved-static | # |
| 519:1 | a | download Raw | unresolved-static | # |
| 534:1 | a | download Raw | unresolved-static | # |
| 555:1 | button | close | source-hidden | closePreviewBtn |

### ui_v2_reports.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | target Scope & Targets | script-reference | # |
| 4:4807 | a | terminal Run & Orchestration | script-reference | # |
| 4:5149 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5502 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9037 | button | terminal Terminal Log | unresolved-static | — |
| 4:9376 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 279:1 | button | All Gaps (3) | unresolved-static | — |
| 280:1 | button | Policy (2) | unresolved-static | — |
| 281:1 | button | Safety (1) | unresolved-static | — |
| 363:1 | input | (unnamed) | unresolved-static | — |
| 371:1 | input | (unnamed) | unresolved-static | — |
| 379:1 | input | (unnamed) | unresolved-static | — |
| 387:1 | input | (unnamed) | unresolved-static | — |
| 428:1 | button | visibility Preview Markdown | script-reference | previewBtn |
| 432:1 | button | data_object Export Findings (.json) | unresolved-static | — |
| 436:1 | button | download Download Full Report (.pdf) | unresolved-static | — |
| 489:1 | a | download Raw | unresolved-static | # |
| 504:1 | a | download Raw | unresolved-static | # |
| 519:1 | a | download Raw | unresolved-static | # |
| 534:1 | a | download Raw | unresolved-static | # |
| 555:1 | button | close | source-hidden | closePreviewBtn |

### ui_v2_retest.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Correlated Attack Chains | script-reference | # |
| 5:7061 | a | Job Execution History | script-reference | # |
| 5:7318 | a | Evidence File Inspector | script-reference | # |
| 5:7579 | a | Cryptographic Audit Log | script-reference | # |
| 5:8042 | a | System Diagnostics & Health | script-reference | # |
| 5:8317 | a | Adapter & Plugin Manager | script-reference | # |
| 5:8586 | a | Settings & API Explorer | script-reference | # |
| 5:10950 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:11307 | button | add New | unresolved-static | — |
| 5:13012 | button | terminal Terminal Log | unresolved-static | — |
| 5:13351 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 13:1400 | button | tune FILTER BY 3-WAY VERDICT | unresolved-static | — |
| 13:1750 | button | play_arrow BATCH REPLAY (3x BASELINE + 3x INJECTED) | unresolved-static | — |
| 15:972 | input | Filter Finding, URL, Verification Reason... | unresolved-static | — |
| 15:1384 | button | ALL (5) | unresolved-static | — |
| 15:1571 | button | STILL_VULNERABLE (2) | unresolved-static | — |
| 15:1752 | button | FIXED (2) | unresolved-static | — |
| 15:1928 | button | INCONCLUSIVE (1) | unresolved-static | — |
| 15:12125 | button | Copy endpoint | unresolved-static | — |
| 15:18949 | button | content_copy copy curl | unresolved-static | — |
| 21:345 | button | refresh Re-Execute Replay (3x Baseline + 3x Injected) | unresolved-static | — |
| 21:1679 | input | (unnamed) | unresolved-static | — |
| 21:2308 | input | (unnamed) | unresolved-static | — |
| 21:2943 | input | (unnamed) | unresolved-static | — |
| 21:3692 | input | e.g., timing delta >3.0s (median of 3), xss marker present, candidat | unresolved-static | — |
| 21:4285 | textarea | Enter proof delta justification... | unresolved-static | — |
| 21:4959 | button | refresh RE-EXECUTE IMMEDIATE PROBE | unresolved-static | — |
| 21:5315 | button | data_object EXPORT PROOF AUDIT JSON | unresolved-static | — |
| 21:5679 | button | assignment_turned_in COMMIT 3-WAY VERDICT TO AUDIT LEDGER | unresolved-static | — |

### ui_v2_run.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 4:4821 | a | target Scope & Targets | script-reference | # |
| 4:5153 | a | terminal Run & Orchestration | script-reference | # |
| 4:5495 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5848 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9381 | button | terminal Terminal Log | unresolved-static | — |
| 4:9720 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 54:1 | button | tune Approval Gate: Active | unresolved-static | toggle-planner-gate |
| 105:1 | input | (unnamed) | unresolved-static | — |
| 109:1 | input | (unnamed) | unresolved-static | — |
| 113:1 | input | (unnamed) | unresolved-static | — |
| 117:1 | input | (unnamed) | unresolved-static | — |
| 121:1 | input | (unnamed) | unresolved-static | — |
| 125:1 | input | (unnamed) | unresolved-static | — |
| 129:1 | input | (unnamed) | unresolved-static | — |
| 133:1 | input | (unnamed) | unresolved-static | — |
| 137:1 | input | (unnamed) | unresolved-static | — |
| 141:1 | input | (unnamed) | unresolved-static | — |
| 149:1 | select | WHAXON tool | script-reference | run-tool-select |
| 150:1 | input | Authorized target host or URL | script-reference | run-target-input |
| 151:1 | button | play_arrow Run Selected Tool | script-reference | run-active-btn |
| 187:1 | input | ai-planner-toggle | script-reference | ai-planner-toggle |
| 223:1 | button | View stdout open_in_new | inline-handler | showNmapStdout() |
| 230:1 | button | Re-run | unresolved-static | — |
| 278:1 | button | Pause | unresolved-static | — |
| 281:1 | button | Abort | unresolved-static | — |
| 335:1 | button | Engage Replay | unresolved-static | — |
| 347:1 | button | explore WhatWeb | unresolved-static | — |
| 351:1 | button | folder_zip Gobuster | unresolved-static | — |
| 355:1 | button | security WPScan | unresolved-static | — |
| 392:1 | button | Clear buffer | inline-handler | clearLog() |
| 485:1 | input | Type command (e.g. validate --id=F-104, pause, resume, replay)... | script-reference | cli-input |
| 486:1 | button | Execute | inline-handler | sendManualCommand() |
| 494:1 | button | pause_circle Pause Pipeline | inline-handler | togglePipelinePause() |
| 499:1 | button | input Inject Payload | inline-handler | injectPayloadPrompt() |
| 504:1 | button | add_circle Spawn Sub-tool | inline-handler | spawnSubtoolModal() |
| 509:1 | button | emergency_home Emergency Abort | inline-handler | emergencyAbort() |

### ui_v2_scope.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 4:4475 | a | dashboard Dashboard / Zero State | declared-nav | /ui-v2 |
| 4:4821 | a | target Scope & Targets | script-reference | # |
| 4:5153 | a | terminal Run & Orchestration | script-reference | # |
| 4:5495 | a | verified_user Trust Layer & Findings | script-reference | # |
| 4:5848 | a | analytics PTES Coverage & Reports | script-reference | # |
| 4:9679 | button | terminal Terminal Log | unresolved-static | — |
| 4:10018 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 28:1 | button | file_upload Quick Import | script-reference | openImportDrawerBtn |
| 32:1 | button | add_circle Add In-Scope Target | script-reference | openTargetModalBtn |
| 101:1 | button | Waiting for scope | disabled | toggleScopeEnforcementBtn |
| 119:1 | input | Filter configured scope rules | script-reference | targetFilterInput |
| 147:3069 | button | link View Certificate SAN Chain | source-hidden | — |
| 147:3404 | button | block Mark Out-of-Scope Exclusion | source-hidden | — |
| 147:3702 | button | assignment_turned_in Promote to Scope (+ Signed Override Log) | source-hidden | — |
| 147:4827 | button | link View Certificate SAN Chain | source-hidden | — |
| 147:5162 | button | block Mark Out-of-Scope Exclusion | source-hidden | — |
| 147:5460 | button | assignment_turned_in Promote to Scope (+ Signed Override Log) | source-hidden | — |
| 147:6577 | button | link View Certificate SAN Chain | source-hidden | — |
| 147:6912 | button | block Mark Out-of-Scope Exclusion | source-hidden | — |
| 147:7210 | button | assignment_turned_in Promote to Scope (+ Signed Override Log) | source-hidden | — |
| 162:1 | input | hostname, IP, or URL | script-reference | scopeCheckTarget |
| 163:1 | button | Check | script-reference | runScopeCheckBtn |
| 164:1 | button | Copy CLI | script-reference | copyCliBtn |
| 223:1 | button | add_moderator Add Boundary Exclusion | source-hidden | addDenyRuleBtn |
| 266:1 | button | close | source-hidden | closeTargetModalBtn |
| 274:1 | input | Authorized target hostname, IP address, or CIDR | source-hidden | modalTargetInput |
| 279:1 | input | (unnamed) | source-hidden | — |
| 283:1 | input | (unnamed) | source-hidden | — |
| 288:1 | input | AUTHORIZATION-REFERENCE | source-hidden | — |
| 291:1 | input | authConfirmCheckbox | source-hidden | authConfirmCheckbox |
| 299:1 | button | Cancel | source-hidden | cancelTargetModalBtn |
| 300:1 | button | Commit to Scope | source-hidden | saveTargetBtn |
| 312:1 | button | close | source-hidden | closeImportDrawerBtn |
| 320:1 | button | Burp XML/JSON | source-hidden | — |
| 321:1 | button | scope.json | source-hidden | — |
| 322:1 | button | CIDR List | source-hidden | — |
| 327:1 | textarea | Paste scope JSON definition | source-hidden | — |
| 331:1 | button | Cancel | source-hidden | cancelImportDrawerBtn |
| 332:1 | button | Import & Parse Rules | source-hidden | executeImportBtn |

### ui_v2_settings.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 206:1124 | a | terminal Dashboard / Zero State | script-reference | # |
| 206:1479 | a | radar Scope & Targets | script-reference | # |
| 206:1821 | a | play_circle Run & Orchestration | script-reference | # |
| 206:2177 | a | verified_user Trust Layer & Findings | script-reference | # |
| 206:2541 | a | description PTES Coverage & Reports | script-reference | # |
| 206:3082 | a | psychology AI Strategy Gate | script-reference | # |
| 206:3429 | a | build_circle Remediation Retest Studio | script-reference | # |
| 206:3796 | a | account_tree Correlated Attack Chains | script-reference | # |
| 206:4161 | a | open_in_browser Bug Bounty & Live Browser | script-reference | # |
| 206:4702 | a | history_toggle_off Job Execution History | script-reference | # |
| 206:5067 | a | folder_zip Evidence File Inspector | script-reference | # |
| 206:5428 | a | encrypted Cryptographic Audit Log | unresolved-static | # |
| 206:5957 | a | monitor_heart System Diagnostics & Health | script-reference | # |
| 206:6331 | a | extension Adapter & Plugin Manager | script-reference | # |
| 206:6695 | a | shield_person PTaaS Client Portal | script-reference | # |
| 206:7051 | a | key Settings & Secrets Vault | script-reference | # |
| 206:8931 | button | terminal LOGS | unresolved-static | — |
| 206:9234 | button | dangerous HALT SCAN | unresolved-static | — |
| 224:1 | button | lock_reset SEAL VAULT | inline-handler | lockVaultMaster() |
| 329:1 | input | (unnamed) | inline-handler | — |
| 347:1 | input | (unnamed) | inline-handler | — |
| 365:1 | input | (unnamed) | inline-handler | — |
| 395:1 | input | budgetSlider | inline-handler | budgetSlider |
| 413:1 | input | confSlider | inline-handler | confSlider |
| 436:1 | input | Filter scope or host... | unresolved-static | — |
| 439:1 | button | add ENCLAVE KEY | inline-handler | openCredentialModal() |
| 479:1 | button | Test / Replay | unresolved-static | — |
| 482:1 | button | Rotate Key | unresolved-static | — |
| 485:1 | button | Revoke & Expunge | unresolved-static | — |
| 511:1 | button | Test / Replay | unresolved-static | — |
| 514:1 | button | Rotate Key | unresolved-static | — |
| 517:1 | button | Revoke & Expunge | unresolved-static | — |
| 543:1 | button | Test / Replay | unresolved-static | — |
| 546:1 | button | Renew Ticket | unresolved-static | — |
| 549:1 | button | Purge | unresolved-static | — |
| 575:1 | button | Test / Replay | unresolved-static | — |
| 578:1 | button | Rotate Key | unresolved-static | — |
| 581:1 | button | Revoke & Expunge | unresolved-static | — |
| 592:1 | a | VIEW COMPLETE REPOSITORY arrow_forward | unresolved-static | # |
| 604:1 | button | download RESYNC CORPUS | unresolved-static | — |
| 642:1 | button | + NEW KEY | inline-handler | triggerKeyGenModal() |
| 717:1 | button | PING | inline-handler | sendTestPing('Slack SecOps') |
| 732:1 | button | PING | inline-handler | sendTestPing('DefectDojo') |
| 747:1 | button | PING | inline-handler | sendTestPing('Jira Engine') |
| 762:1 | button | PING | inline-handler | sendTestPing('Discord Hook') |
| 767:1 | button | add_link REGISTER ENDPOINT | unresolved-static | — |
| 794:1 | button | close | source-hidden | closeKeyGenModal() |
| 804:1 | input | e.g. CI_TEST_PIPELINE | source-hidden | newTokenName |
| 808:1 | select | Operator (Execute scans, trigger payloads, write findings) Reviewer  | source-hidden | — |
| 817:1 | button | 30 Days | source-hidden | — |
| 818:1 | button | 90 Days | source-hidden | — |
| 819:1 | button | 365 Days | source-hidden | — |
| 824:1 | button | CANCEL | source-hidden | closeKeyGenModal() |
| 827:1 | button | GENERATE TOKEN | source-hidden | executeTokenGeneration() |
| 841:1 | button | close | source-hidden | closeCredentialModal() |
| 851:1 | input | 10.0.0.0/8 or admin.internal.corp | source-hidden | — |
| 856:1 | select | SSH Private Key (Ed25519) HTTP Bearer JWT Kerberos TGT Ticket AWS IA | source-hidden | — |
| 866:1 | input | admin or svc_account | source-hidden | — |
| 871:1 | textarea | -----BEGIN OPENSSH PRIVATE KEY-----... | source-hidden | — |
| 875:1 | button | ABORT | source-hidden | closeCredentialModal() |
| 878:1 | button | SEAL TO ENCLAVE | source-hidden | closeCredentialModal() |

### ui_v2_threat_intel.html

| Line:column | Tag | Label | Static state | Binding evidence |
|---|---|---|---|---|
| 5:4579 | a | Dashboard / Zero State | script-reference | # |
| 5:4836 | a | Scope & Targets | script-reference | # |
| 5:5087 | a | Run & Orchestration | script-reference | # |
| 5:5346 | a | Trust Layer & Findings | script-reference | # |
| 5:5611 | a | PTES Coverage & Reports | script-reference | # |
| 5:6086 | a | AI Strategy Gate | script-reference | # |
| 5:6333 | a | Remediation Retest Studio | script-reference | # |
| 5:6598 | a | Attack Surface & Continuous Monitoring | script-reference | # |
| 5:6895 | a | Correlated Attack Chains | script-reference | # |
| 5:7158 | a | Bug Bounty & Live Browser Studio | script-reference | # |
| 5:7443 | a | Threat Intel & Exploit Arsenal | script-reference | # |
| 5:7724 | a | BAS & Detection Validation | script-reference | # |
| 5:8209 | a | Job Execution History | script-reference | # |
| 5:8466 | a | Evidence File Inspector | script-reference | # |
| 5:8727 | a | Cryptographic Audit Log | script-reference | # |
| 5:8988 | a | Compliance & Framework Crosswalk | script-reference | # |
| 5:9473 | a | System Diagnostics & Health | script-reference | # |
| 5:9748 | a | Adapter & Plugin Manager | script-reference | # |
| 5:10017 | a | PTaaS Client Portal | script-reference | # |
| 5:10270 | a | Settings & Secrets Vault | script-reference | # |
| 5:12636 | button | ENG-2026-X892 (api.internal.corp) arrow_drop_down | unresolved-static | — |
| 5:12993 | button | add New | unresolved-static | — |
| 5:14698 | button | terminal Terminal Log | unresolved-static | — |
| 5:15037 | button | gavel Emergency Halt Scan | unresolved-static | — |
| 104:1 | button | sync Sync Upstream Feeds | unresolved-static | — |
| 108:1 | button | database Rebuild SQLite Vector DB | unresolved-static | — |
| 112:1 | button | terminal Searchsploit Terminal | unresolved-static | — |
| 203:1 | input | Filter by CVE-ID, service (OpenSSH, RDP, FortiOS), CVSS, EPSS... | unresolved-static | — |
| 207:1 | select | Severity (CVSS DESC) EPSS Probability Weaponized First CISA KEV List | unresolved-static | — |
| 217:1 | button | All (14) | inline-handler | toggleFilter('all', this) |
| 220:1 | button | CISA KEV (5) | inline-handler | toggleFilter('cisa', this) |
| 223:1 | button | Weaponized PoC (8) | inline-handler | toggleFilter('weaponized', this) |
| 226:1 | button | Remote Code Execution (4) | inline-handler | toggleFilter('rce', this) |
| 229:1 | button | PrivEsc (3) | inline-handler | toggleFilter('privesc', this) |
| 236:1 | div | CVE-2024-6387 RegreSSHion (OpenSSH Race Condition) CVSS 9.8 EPSS 88. | inline-handler | selectCve('CVE-2024-6387', 'RegreSSHion — OpenSSH Signal Handler Race  |
| 263:1 | button | code Inspect Exploit Code | unresolved-static | — |
| 266:1 | button | sensors Queue Safe Probe | unresolved-static | — |
| 269:1 | button | tune Simulate Dry-Run | unresolved-static | — |
| 275:1 | div | CVE-2024-38077 MadLicense (Windows RDP Gateway) CVSS 9.8 EPSS 94.6%  | inline-handler | selectCve('CVE-2024-38077', 'MadLicense — Windows Remote Desktop Licen |
| 301:1 | button | terminal Metasploit Harness | unresolved-static | — |
| 304:1 | button | data_object Inspect MSF Options | unresolved-static | — |
| 310:1 | div | CVE-2023-38606 BOLA in Internal Merchant API Endpoint CVSS 8.4 EPSS  | inline-handler | selectCve('CVE-2023-38606', 'Broken Object Level Authorization (BOLA)  |
| 335:1 | button | play_arrow Execute Curl Replay Test | unresolved-static | — |
| 341:1 | div | CVE-2024-21762 Fortinet FortiOS SSL-VPN OOB Write CVSS 9.6 EPSS 96.8 | inline-handler | selectCve('CVE-2024-21762', 'Fortinet FortiOS SSL-VPN Out-of-Bounds Wr |
| 366:1 | button | assignment_turned_in View Nuclei Heuristics | unresolved-static | — |
| 397:1 | button | Source Code | inline-handler | switchExploitTab('tab-source') |
| 400:1 | button | Mechanics | inline-handler | switchExploitTab('tab-mechanics') |
| 403:1 | button | Guardrails | inline-handler | switchExploitTab('tab-guardrails') |
| 406:1 | button | Artifacts | inline-handler | switchExploitTab('tab-artifacts') |
| 419:1 | button | content_copy Copy | unresolved-static | — |
| 503:1 | input | (unnamed) | unresolved-static | — |
| 510:1 | input | (unnamed) | unresolved-static | — |
| 518:1 | button | gavel Arm & Queue for HITL Approval Gate | unresolved-static | — |
