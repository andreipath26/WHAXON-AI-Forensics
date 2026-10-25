# Literature Review

Scope: what is already known about (a) measuring black-box web-scanner accuracy, (b) validating
findings and false positives, (c) authorising a *destination* rather than a *name*, and (d) the
test application used here.

Citations were checked against the publisher or the project itself; where verification failed the
entry says so (see §5).

## 1. Scanner accuracy: the established measurement frame

**Bau, Bursztein, Gupta & Mitchell (2010), "State of the Art: Automated Black-Box Web Application
Vulnerability Testing", IEEE S&P, pp. 332–345.** DOI 10.1109/SP.2010.27.
They evaluated eight tools against a custom application with known vulnerabilities plus vulnerable
versions of real applications. Two lessons transfer directly: the ground truth must be *constructed*
rather than inferred from scanner output, and detection must be separated from exploitation
(tools report many "potential" issues that are not exploitable). The authors explicitly declined to
publish vendor comparisons — a caution against reading rankings into small studies.

**Doupé, Cova & Vigna (2010), "Why Johnny Can't Pentest: An Analysis of Black-Box Web Vulnerability
Scanners", DIMVA, LNCS 6201, pp. 111–131.** DOI 10.1007/978-3-642-14215-4_7.
Evaluated eleven scanners; the decisive finding is that *reachability* (crawling) dominates
end-to-end detection: a scanner cannot find what it never reaches. Implication for this study:
"not reported" and "not vulnerable" must be distinguished, which is precisely the difference between
WHAXON's `candidate` and `refuted`.

**Fonseca, Vieira & Madeira (2007), "Testing and Comparing Web Vulnerability Scanning Tools for SQL
Injection and XSS Attacks", PRDC, pp. 365–372.** DOI 10.1109/PRDC.2007.55.
Proposes fault injection to create ground truth for SQLi/XSS scanner benchmarking. This study adopts
the same principle with a lighter mechanism: a local HTTP benchmark whose vulnerable and safe
behaviours are implemented deliberately and whose labels are asserted independently
(`tests/test_research_observations.py`).

**OWASP Benchmark Project (OWASP Foundation; Java suite v1.0, 2015; Python suite later).**
Provides labelled test cases and a scoring tool. Its score is **Youden's J = TPR − FPR**, with raw
TP/FN/TN/FP also reported, precisely because a single scalar hides whether a tool misses
vulnerabilities or cries wolf. E8 uses the same metric for the same reason.
<https://owasp.org/projects/benchmark?tab=scoring>

**Youden (1950), "Index for rating diagnostic tests", Cancer 3(1):32–35.** DOI
10.1002/1097-0142(1950)3:1<32::AID-CNCR2820030106>3.0.CO;2-3. The original J statistic used above.

## 2. Verification, false positives and the "proof" claim

The OWASP Web Security Testing Guide (v4.2, 2020; OWASP community) states the operational norm that
automated results are generic and require investigation before being reported as findings
<https://wstg.owasp.org/v4.2/>. PTES (Penetration Testing Execution Standard) formalises the same
expectation in its reporting phase; **note:** the official site
(`pentest-standard.org`) timed out during this study's verification attempt, and the accessible
mirror self-describes as an unofficial fork, so no author/year is asserted here.

What the literature does **not** contain is a measurement of *automatic* replay-based verification
as a false-positive filter inside a pentest orchestrator. The closest framing is the general
"scanner output is a hypothesis" result above; the specific question — *does automatically replayed
evidence make the "verified" label trustworthy?* — is where this study contributes measurements
(§4 of `docs/research-contribution.md`).

## 3. Authorising a destination, not a name

**Saltzer & Schroeder (1975), "The Protection of Information in Computer Systems", Proc. IEEE
63(9):1278–1308.** DOI 10.1109/PROC.1975.9939. Source of *fail-safe defaults*: "base access decisions
on permission rather than exclusion". WHAXON explicitly implements this (deny by default, RFC1918-only
when unconfigured), which is why its string-level behaviour is clean under adversarial encodings
(E10) — and why the remaining gap is interesting: the permission is granted to a *name*, not to the
address that name denotes.

**OWASP SSRF Prevention Cheat Sheet (OWASP community).**
<https://cheatsheetseries.owasp.org/cheatsheets/Server_Side_Request_Forgery_Prevention_Cheat_Sheet.html>
Documents the name-vs-destination hazard: a validated hostname can resolve to a forbidden address, and
a fresh lookup at connection time can invalidate an earlier check. WHAXON is not an SSRF proxy, but its
scope gate is structurally the same allow-list, so the same hazard applies — demonstrated in E11
(redirect) and in the DNS-binding probe of E10.

**GitLab, "Filtering outbound requests" (GitLab Docs).** <https://docs.gitlab.com/security/webhooks/>
An engineering account of DNS-rebinding protection for outbound webhooks: resolve, check the *address*,
and pin it for the connection. This is the concrete mitigation whose absence in WHAXON is measured here.

## 4. The test application

**DVWA — Damn Vulnerable Web Application** (project copyright from 2008; maintained by Ryan Dewhurst
with credits to RandomStorm and Robin Wood). <https://github.com/digininja/DVWA>
Its README describes a deliberately vulnerable PHP/MariaDB application for practice and warns against
internet exposure. Important for this study: DVWA is a *teaching* application with a documented
low/medium/high/impossible ladder, not a labelled benchmark; it does not publish expected-results
files the way OWASP Benchmark does. That is why the study (i) uses it for live confirmation of
capabilities, and (ii) uses a purpose-built labelled server for scoring soundness and completeness.

## 5. Verification status of citations

| Reference | Verified how | Note |
| --- | --- | --- |
| Bau et al. 2010 | publisher page + Crossref DOI | —
| Doupé et al. 2010 | ASU/ UCSB publication records + DOI | —
| Fonseca et al. 2007 | Crossref + IEEE Xplore record | full text not read |
| OWASP Benchmark | official project + scoring pages | version author not asserted |
| OWASP WSTG v4.2 | official project + versioned guide | community work, no single author |
| Youden 1950 | Crossref + PubMed metadata | publisher page returned 403 |
| Saltzer & Schroeder 1975 | MIT-hosted text + Crossref | —
| OWASP SSRF Cheat Sheet | live page | no author/year stated |
| GitLab outbound-request docs | live page | no author/year stated |
| DVWA | repository + OWASP VWAD entry | exact initial release not verified |
| **PTES** | official site timed out | **author/year unverified — not asserted** |

## 6. What the literature leaves open (feeds `docs/research-gaps.md`)

1. No published evaluation of replay-based *automatic* verification as a false-positive filter.
2. Scanner benchmarks score "did it report the vuln", not "is the recorded evidence faithful"
   (status codes, sizes, bodies) — the adapter question is essentially unstudied.
3. Scope enforcement in orchestration tooling is discussed as a policy feature, not measured as a
   security boundary under adversarial naming/redirection.
