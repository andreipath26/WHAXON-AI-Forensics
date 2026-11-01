# CBC 2026 — WHAXON Partnership, Customer and Funding Playbook

**Event:** Cybersecurity Business Convention (CBC), 25–26 November 2026, MEETT, Toulouse  
**Purpose:** Turn convention attendance into concrete support for WHAXON: commercial pilots, strategic partnerships, infrastructure/engineering help, introductions and (where realistic) funding.  
**Prepared:** 1 November 2026  
**Repository:** \`andreipath26/WHAXON-AI-Forensics\`  
**Status:** Working field guide. Update attendance and meeting status as organizers publish new information.

---

## 1. Executive objective

WHAXON is the most mature project in the portfolio and the only one that should be presented as the immediate commercial product. The other projects (KILN, Aletheia, SYBIL and ZALMOXIS) are longer-term research/product directions, not integrated WHAXON capabilities. Do not imply otherwise.

The objective at CBC is not to collect business cards or pitch every exhibitor. It is to leave with:

1. **One or more qualified pilot conversations** with a cybersecurity services provider or end-user organization.
2. **A credible strategic partner lead** able to provide engineering, deployment infrastructure, distribution, customer access or operational expertise.
3. **A financing pathway** appropriate to the project's current stage and the founder's current legal/company status.
4. **Specific follow-up commitments**: named owner, next meeting, requested material and date.

A partner who provides a first deployment, infrastructure or customer access may be more valuable immediately than an investor who cannot invest at the current stage.

### The core positioning

> WHAXON is an operator-governed cybersecurity assessment and validation platform. It orchestrates supported security tools, applies explicit scope controls, normalizes findings, validates selected finding types deterministically, preserves evidence and produces engagement reports. It is being developed for authorized security assessments, with the CLI as the dependable operator interface and a browser UI as the operational/presentation layer.

Keep the product claim aligned with the actual repository and current acceptance evidence. WHAXON is not a universal autonomous pentester, does not guarantee complete vulnerability coverage, and is not a hosted scanning service.

### The ask

Do not open with “I need money.” Open with the product, the problem and the reason the other party is relevant. Then ask for one specific next step:

- a controlled pilot;
- a technical/product review;
- a channel or delivery partnership discussion;
- infrastructure or engineering support;
- an introduction to the relevant decision-maker;
- advice on an eligible financing route.

---

## 2. Important corrections and evidence rules

This document deliberately separates **confirmed organizational participation** from **confirmed personal attendance**.

| Evidence label | Meaning | How to use it |
|---|---|---|
| **Confirmed exhibitor** | The company or organization has publicly announced a stand or exhibitor presence | Prioritize a stand visit and request a meeting |
| **Confirmed speaker / scheduled contributor** | A named person is publicly listed for a CBC session | Plan around the session, but still confirm availability |
| **CBC partner / delegation / club** | The organization is listed in the event ecosystem | Ask whether a representative will attend and who handles introductions |
| **External prospect — not confirmed at CBC** | The organization is strategically relevant but no public CBC attendance evidence was found | Contact before the event; do not assume they will be there |
| **Person to identify** | The organization is relevant but no named attending decision-maker is verified | Ask the stand representative for the correct role/name |

An exhibitor announcement confirms the organization, not that its CEO, founder or a particular executive will personally attend. Do not tell someone that a named executive is confirmed unless CBC or the organization explicitly says so.

**Do not rely on the previous shortlist as complete.** CBC says more exhibitors will be announced. Recheck the official directory, programme, CBC LinkedIn announcements and the meeting platform before the event.

---

## 3. Priority order

### Priority A — contact before the event and request a meeting

1. **Advens — Sébastien Francillon**: strongest immediately actionable commercial lead; public CBC stand announcement, named regional director and direct professional contact.
2. **ITrust — Sébastien Goudouly / Mathieu Lagorse / Jean-Nicolas Piotrowski**: strong local strategic and technical fit; confirm which executive is actually attending before requesting a meeting.
3. **CHEOPS Technology — Jérémy Voisin**: confirmed stand and named Cyberdefense session; infrastructure and service-delivery fit.
4. **Cyber'Occ**: regional cybersecurity ecosystem and possible route to pilot organizations and local partners.
5. **Digital 113**: access to the regional digital ecosystem and named pavilion members.
6. **Occitanie Angels**: important financing network to approach, but current published eligibility criteria create a material obstacle for an unincorporated solo founder. Seek an eligibility discussion/referral, not an assumption of immediate investment.
7. **Orange Cyberdefense — Olivier de Paillerets**: named keynote/speaker and senior industry contact; seek advice and introductions, not an immediate investment pitch.

### Priority B — approach at CBC, or request a referral to the right person

- Cyberwatch
- Gatewatcher
- Stormshield
- AntemetA
- Bitdefender
- Docaposte
- Keyfactor
- Exaprobe
- TechValley
- YoungData
- CESI
- Groupama
- Heliaq
- HS2
- Cyblex Consulting
- Hornetsecurity
- ManageEngine
- Predicta Lab
- TheGreenBow
- TYREX Cyber
- Apixis

### Priority C — external funding prospects; attendance not verified

- Auriga Cyber Ventures
- IRDI Capital Investissement
- Bpifrance
- Other investors identified through Occitanie Invest and the regional financing ecosystem

Do not book travel or spend money solely to pursue an unconfirmed external prospect. Start with email/online outreach and request an introduction.

---

## 4. Target-by-target meeting briefs

Each brief gives the objective, likely fit, what to say, what to ask, what to avoid and the next step to secure.

### 4.1 Advens — first commercial target

**Attendance evidence:** Advens publicly announces its Occitanie team on **stand 15**, 25–26 November.  
**Named contact:** **Sébastien Francillon**, Directeur Advens Sud-Ouest.  
**Published contact:** [sebastien.francillon@advens.fr](mailto:sebastien.francillon@advens.fr)  
**Published CBC page:** https://www.advens.com/evenements/cbc-2026/  
**Company contact page:** https://www.advens.com/nous-contacter/

**Why prioritize:** Advens provides cybersecurity consulting and services, including SOC, vulnerability/exposure management, incident response and security consulting. This makes it a plausible pilot/delivery partner. It is more immediately actionable than a generic large-vendor approach because the regional director and direct contact are published.

**Opening (in person or email):**

> Hello Mr. Francillon. I'm an independent developer based in the Toulouse area, building WHAXON, an operator-governed platform for authorized security assessments. It orchestrates supported tools, consolidates findings, validates selected findings with deterministic checks and preserves evidence for reporting. I saw that your Occitanie team will be at CBC on stand 15. I'd value 20 minutes to show you the working CLI workflow and understand whether it could complement an Advens consulting or assessment workflow.

**What to ask:**

1. Which recurring part of your assessment workflow is most expensive or difficult to reproduce consistently: tool orchestration, evidence collection, validation, retesting or reporting?
2. Would Advens consider a tightly scoped pilot on a lab or explicitly authorized client environment?
3. What would WHAXON have to demonstrate before your team would trust it in a real engagement?
4. Who owns technical evaluation and partnership decisions for the South-West team?
5. If a pilot is premature, could you introduce me to the colleague best placed to assess it?

**Specific pilot proposal:** one bounded engagement on a customer-approved lab or test environment; agree scope and rules of engagement in writing; run a defined set of supported discovery/enumeration/validation workflows; compare normalized findings, evidence completeness, analyst time and report quality against the existing process. No production testing without written authorization and explicit rules.

**What to show:** a short, real CLI workflow from engagement/scope setup through supported tool execution, findings, deterministic validation, evidence and report. Show an actual output generated by the current code, not slides or mocked data. Be candid about supported finding types and any incomplete workflows.

**Avoid:** claiming universal pentest automation, claiming every finding is verified, claiming the UI is fully complete if it is not, or asking Advens to resell an unproven product immediately.

**Desired outcome:** a named technical evaluator and a date for a follow-up demonstration or pilot-scoping call.

---

### 4.2 ITrust — strategic, technical and channel partner

**Attendance evidence:** ITrust appears in CBC's published exhibitor announcements. Confirm its current stand number and the individual attending through the CBC directory or ITrust before the event.  
**Relevant leadership published by ITrust:**
- **Jean-Nicolas Piotrowski** — President.
- **Sébastien Goudouly** — Director Channel & Alliances, presales and Professional Services.
- **Mathieu Lagorse** — Director R&D.

**Official sources:**
- Company and management: https://www.itrust.fr/entreprise-itrust
- Partner information: https://www.itrust.fr/partenaires/

**Why prioritize:** ITrust is a Toulouse cybersecurity software/services company with intrusion-testing roots and its own security products. Sébastien Goudouly is the most practical first contact for a channel/services discussion; Mathieu Lagorse is the technical/R&D route; Jean-Nicolas Piotrowski is the executive route if a strategic fit emerges.

**Opening:**

> Hello. I'm developing WHAXON, a scope-controlled platform for authorized security assessments. It focuses on orchestration, evidence-backed findings, deterministic validation and reproducible reporting. Given ITrust's cybersecurity product and services activity, I'd like to understand whether there is a complementary technical or delivery use case rather than assume we should compete.

**Ask Sébastien Goudouly:**

- Could WHAXON complement any ITrust service or channel workflow?
- What integration, support, documentation, licensing or maturity requirements would be expected before a partner evaluation?
- Is there a customer segment where repeatable assessment evidence or retesting is a clear unmet need?
- Who should own a technical evaluation?

**Ask Mathieu Lagorse:**

- Which technical integration boundary would be most useful: tool orchestration, finding normalization, validation, evidence/reporting or API integration?
- What would be the minimum technical proof required for an evaluation?
- Would ITrust be open to a code/architecture review under an appropriate confidentiality arrangement?

**Ask Jean-Nicolas Piotrowski:**

- Does WHAXON solve a problem that is commercially meaningful alongside ITrust's existing offering?
- Would he recommend a technical pilot, channel discussion or a different market positioning?
- Who is the right person internally to sponsor a next step?

**Avoid:** pitching WHAXON as an alternative to ITrust's products without understanding overlap; implying an existing integration; asking for a broad partnership before agreeing a narrow use case.

**Desired outcome:** referral to the appropriate technical and channel owners, followed by a scoped evaluation.

---

### 4.3 CHEOPS Technology — infrastructure and cyberdefense partner

**Attendance evidence:** CHEOPS confirms **stand 55**, 25–26 November. Its published programme names:
- **Jérémy Voisin**, Director of Cyberdefense division — workshop Wednesday 25 November, 11:30–12:00.
- **Bastien Bobe**, Commvault Field Security CTO — pitch Wednesday 25 November, 10:40–10:50.
- **Mathieu Saada**, HPE Cyber Security Sales Specialist — pitch Thursday 26 November, 10:50–11:00.

**Official event page:** https://www.cheops-technology.com/fr/evenements/cbc-2026

**Why prioritize:** CHEOPS works across infrastructure, cloud and cybersecurity services. It may be able to help with deployment architecture, infrastructure access, managed-service delivery or customer introductions. Jérémy Voisin is the most relevant initial contact for WHAXON.

**Opening:**

> Hello Mr. Voisin. I'm building WHAXON, a local-first security assessment platform intended for authorized operator-led engagements. I'm looking for a partner who understands both cybersecurity delivery and the infrastructure needed to deploy a dependable tool. I would like your view on whether a small technical pilot or deployment partnership could make sense.

**Ask:**

1. Would CHEOPS consider WHAXON as an internal tool, a complementary service capability or a partner product?
2. What would be required to run it reliably in a controlled customer environment or headless Linux server?
3. Could CHEOPS advise on a suitable deployment model and operational requirements?
4. Is there a customer or service team that could evaluate the workflow?
5. Who handles technology partnerships or innovation evaluation?

**Secondary conversations:**
- Bastien Bobe: ask about evidence recovery, resilience, backups and operational requirements for a security platform. Do not pitch WHAXON as a backup product.
- Mathieu Saada: ask about secure network deployment and enterprise infrastructure considerations. Do not force an unrelated post-quantum discussion.

**Desired outcome:** technical discovery meeting with the Cyberdefense team and/or an infrastructure specialist; ideally a pilot environment or referral to a customer team.

---

### 4.4 Orange Cyberdefense — senior industry advice and introductions

**Attendance evidence:** **Olivier de Paillerets** is announced in CBC speaker/keynote material; the exact session time should be reconfirmed in the current programme. Orange Cyberdefense is also named in CBC ecosystem/delegation material. Do not assume he is available for an unarranged private meeting.

**Person:** Olivier de Paillerets, EVP Strategy, Transformation & Security (verify current title before the event).  
**CBC programme source:** https://cbc-convention.com/

**Why prioritize:** a senior industry perspective and potential route to the right innovation, partnerships or regional business contact. This is not the most likely immediate funding route.

**Opening after a session:**

> Thank you for the talk. I'm an independent developer building WHAXON, an operator-governed security assessment and validation platform. It is the most mature product in a broader research portfolio, and I'm preparing it for commercial deployment. I would value one piece of advice: which kind of partner or customer should I prove the product with first?

**Ask:**

- Which buyer is most likely to pay for a product like WHAXON: a pentest consultancy, MSSP, internal security team or SME?
- What proof would make a new vendor credible to a large cybersecurity provider?
- Is there a specific team or regional contact he would recommend speaking with?
- Would he be comfortable with a short follow-up email containing a concise product brief?

**Avoid:** asking a keynote speaker for funding on the spot, monopolizing their time, or claiming Orange is a prospective partner without an invitation.

**Desired outcome:** one useful referral or a permission-based follow-up contact.

---

### 4.5 Cyber'Occ — regional ecosystem and pilot introductions

**Attendance evidence:** listed in CBC partner/delegation ecosystem material. Confirm which Cyber'Occ representatives will be present and whether they have scheduled meetings.  
**Official information:** https://cyberocc.com/cyberocc/  
**Contact:** https://cyberocc.com/contact/  
**Published regional contact:** contact@cyberocc.fr  
**Public regional cyber contact listing:** https://messervices.cyber.gouv.fr/contacts/fr-occ

**Why prioritize:** Cyber'Occ is the regional cybersecurity resource and ecosystem organization. Its role includes structuring the regional cybersecurity sector, supporting organizations and connecting local capabilities. It is not a venture capital fund.

**Opening:**

> I'm developing WHAXON, an independent cybersecurity product based in the region. It is focused on authorized security assessments, evidence-based validation and repeatable reporting. I'm preparing it for commercial deployment and looking for a first regional pilot partner and experienced technical feedback. Could Cyber'Occ help me identify the right companies or programs?

**Ask:**

1. Which regional SMEs, service providers or public organizations are actively looking for assessment or validation capabilities?
2. Are there pilot, experimentation, innovation or procurement programmes appropriate for an independent developer?
3. What membership or ecosystem route would help WHAXON build credibility?
4. Could Cyber'Occ introduce me to two or three relevant regional providers or CISOs?
5. Are there upcoming calls, events or demonstrators where WHAXON could be evaluated?

**Avoid:** treating Cyber'Occ as a buyer or asking it to endorse product security without a formal evaluation.

**Desired outcome:** two named introductions, a clear route to a pilot programme, and the correct follow-up contact.

---

### 4.6 Digital 113 — regional commercial access

**Attendance evidence:** Digital 113 confirms its CBC pavilion and says the following members have confirmed participation: **YoungData, CESI, Groupama and TechValley**.  
**Contact:** contact@digital113.fr  
**Event information:** https://www.digital113.fr/event/cbc-2026-126/register

**Why prioritize:** it is a route to regional digital businesses and potential end users. The pavilion is particularly useful for reaching smaller organizations and service providers.

**Opening:**

> I'm developing WHAXON, a cybersecurity assessment and validation platform for authorized engagements. I'm looking for a small number of regional organizations willing to evaluate a working product and give structured feedback. Which members or pavilion participants would be best suited to a pilot?

**Ask:**

- Which members have an internal security team or deliver cybersecurity services?
- Can Digital 113 introduce WHAXON to SME/ETI decision-makers or CISOs?
- Are there member demonstration sessions, working groups or innovation programmes?
- Which pavilion participants are potential pilot users rather than simply technology vendors?

**Specific pavilion conversations:**
- **YoungData:** ask whether its data governance/security customers have a need for repeatable security assessment and evidence.
- **CESI:** ask about a controlled lab evaluation, student/research collaboration or technical feedback. Do not assume it is a commercial buyer.
- **Groupama:** ask for the correct security/procurement contact only if the representative indicates a relevant use case; do not try to pitch an enterprise deployment at the stand.
- **TechValley:** ask about the SME security product ecosystem and potential partner/customer introductions. CBC has announced its pitch for the Cybiance Box; use that as a conversation starter about accessible SME cybersecurity, not as a claim of product compatibility.

**Desired outcome:** two warm introductions and one possible SME pilot.

---

### 4.7 Occitanie Angels — financing route, with eligibility caveat

**Attendance evidence:** no public evidence found that Occitanie Angels as an organization or a particular member is confirmed to attend CBC. Treat this as pre-event outreach, not a confirmed convention meeting.

**Official contacts:**
- contact@occitanie-angels.fr
- 06 88 69 20 20
- https://occitanie-angels.fr/contact/
- Funding process and eligibility: https://occitanie-angels.fr/levee-de-fonds/
- Team: https://occitanie-angels.fr/equipe/

**Important eligibility issue:** its published criteria currently include:
- a French startup registered with the RCS and domiciled in Occitanie;
- ideally a complementary team;
- non-dilutive funding already raised where relevant;
- a first meaningful equity round of at least **€200,000**;
- pre-money valuation no higher than €4 million;
- enough cash runway for at least 6 months, ideally 12;
- a POC;
- commercial traction already achieved or imminent within 3 months, or a deep-tech model with validated economics.

Its published average submission-to-closing timeline is 3–6 months.

**Practical consequence:** as a currently unincorporated individual developer without runway, WHAXON does **not** appear ready to meet the published investment criteria. Do not submit as if eligible or promise a round you cannot yet execute. Ask for a candid eligibility conversation and referrals to earlier-stage/non-dilutive support. Recheck the criteria before applying.

**Opening email:**

> Subject: WHAXON — request for early-stage funding-path guidance
>
> Hello,
>
> I'm an independent developer in Occitanie building WHAXON, a cybersecurity assessment and validation platform. The product is the most mature project in my portfolio and I am preparing a controlled commercial launch.
>
> I have reviewed your published eligibility criteria and understand that your standard process expects an incorporated Occitanie company, a POC, commercial traction and a first equity round of at least €200,000. I am not yet incorporated and do not want to submit an application that does not meet your requirements.
>
> Would you be willing to advise which regional non-dilutive programmes, founder-support structures or earlier-stage investor networks I should approach first, and what milestones I should reach before returning to Occitanie Angels?
>
> I can provide a concise product brief and a live demonstration.
>
> Kind regards,
> [Name]

**At a meeting, ask:**
1. What is the correct legal and commercial milestone before applying?
2. Which non-dilutive financing routes should be pursued first?
3. Are there members who mentor cybersecurity founders before an equity round?
4. Would a technical/business co-founder or commercial advisor materially improve eligibility?
5. Can they refer you to the right Bpifrance, AD'OCC or regional programme contact?

**Desired outcome:** written advice on the next eligible funding route and one warm referral. Do not expect an immediate cheque.

---

### 4.8 Auriga Cyber Ventures — specialist cyber investor, external prospect

**Attendance evidence:** no public CBC attendance confirmation found. Contact separately.  
**Official site:** https://www.aurigacyberventures.com/

**Why relevant:** it explicitly focuses on early-stage European cybersecurity and digital-trust founders. This is a better thematic fit than a generalist investor, but thematic fit does not imply investment readiness.

**Opening:**

> I'm building WHAXON, an operator-governed cybersecurity assessment and validation product. It is currently an independently developed product, and I am working toward a first repeatable commercial deployment. I would like to understand what evidence your team would need before considering a company at this stage.

**Ask:**
- What stage, company structure and team profile do you require?
- Do you invest in pre-incorporation projects or only established companies?
- What commercial traction and technical proof are expected?
- Is there a preferred route for submitting a short deck or product brief?
- Would you recommend a strategic angel or pilot partner before approaching the fund?

**Avoid:** presenting an investment amount, valuation or growth forecast without a defensible financial model and incorporated-company plan.

**Desired outcome:** a clear fit/no-fit decision and, if appropriate, permission to send a short deck after the next milestone.

---

### 4.9 IRDI Capital Investissement — regional investment route

**Attendance evidence:** no CBC attendance confirmation found.  
**Official site:** https://www.irdi.fr/

**Objective:** establish whether WHAXON could fit its investment mandate later and ask for the appropriate early-stage route if it is currently too early.

**Say:**

> WHAXON is an independently developed cybersecurity software product in the process of moving toward commercial deployment. I am trying to understand the financing sequence that makes sense for a solo founder before approaching regional investment funds. Could you tell me what company stage, traction and team structure you would expect?

**Ask:** stage/sector fit, minimum ticket, incorporation requirements, traction expectations, preferred introduction route, and relevant co-investment/seed partners.

**Desired outcome:** qualification guidance and a referral, not an assumed funding meeting.

---

### 4.10 Bpifrance — non-dilutive and innovation-financing guidance

**Attendance evidence:** no CBC attendance confirmation found.  
**Official site:** https://www.bpifrance.fr/

**Objective:** identify financing/support mechanisms suitable for product development and commercialization, including the correct regional contact and eligibility conditions. Do not assume a grant is automatically available to an individual.

**Say:**

> I'm an independent developer in Occitanie with a working cybersecurity software product and a clear commercialization objective. Before creating a company or committing to a financing structure, I need to identify which innovation and founder-support mechanisms are genuinely available at this stage and what prerequisites apply.

**Ask:**
- Which mechanisms can support an individual before incorporation, if any?
- Which require an incorporated company, matching funds, R&D classification or co-financing?
- Which regional contact should review the project?
- Are there non-dilutive routes for product validation, prototype development or first commercialization?
- What documents should be prepared before applying?

**Desired outcome:** named regional advisor, correct programme, eligibility checklist and next appointment.

---

## 5. Other CBC exhibitors — what to say and what to ask

For these companies, do not assume a particular executive is attending. Ask the stand representative for the person responsible for partnerships, product integrations, technical alliances or innovation.

| Organization | Why it may matter to WHAXON | Opening question / ask |
|---|---|---|
| **Cyberwatch** | Vulnerability-management adjacency | “Do your customers need a repeatable way to validate selected findings and preserve reproducible evidence after discovery?” Ask for product/partnership owner. |
| **Gatewatcher** | Detection/NDR and incident visibility | “Do you see a need to connect detection outcomes with controlled offensive validation or exposure assessment?” Attend its published CBC pitch if possible. |
| **Stormshield** | Network, endpoint and data security ecosystem | “Do you work with independent assessment tools or service partners that validate security posture around your products?” |
| **AntemetA** | Infrastructure, cloud and managed services | “Could your teams provide a controlled deployment environment or introduce customers who need repeatable security assessments?” |
| **Bitdefender** | Endpoint/security ecosystem and channel | “Is there a partner ecosystem route for complementary assessment and validation products?” Seek alliances, not frontline sales. |
| **Docaposte** | Digital trust and enterprise/public-sector relationships | “Who handles security innovation or external technology partnerships, and is there a route to a controlled pilot?” |
| **Keyfactor** | Machine identity, PKI and crypto-agility; confirmed stand 47 | “Do customers need independent assessment of exposed services and security configuration around machine identities and certificates?” Do not imply WHAXON currently audits PKI deeply unless demonstrated. |
| **Exaprobe** | Integrator and CrowdStrike ecosystem; CBC pitch | “Do your customer engagements need a repeatable assessment/evidence tool alongside detection and response?” |
| **TechValley** | SME cybersecurity and Cybiance Box pitch | “Could WHAXON complement an SME security offering through authorized assessment, evidence and retesting?” |
| **YoungData** | Data governance/security ecosystem | “Are your customers asking for repeatable technical security assessments to support data-risk governance?” |
| **CESI** | Education, engineering and potential lab environment | “Is there a route to a controlled lab evaluation or applied technical collaboration?” |
| **Groupama** | Potential end-user / enterprise pilot route | “Who is the appropriate CISO/security innovation contact for a small, controlled product evaluation?” |
| **Heliaq** | IT and cybersecurity services | “Do you deliver security assessments, and would a pilot around repeatability/evidence be useful?” |
| **HS2** | Cybersecurity services/consulting | “Which part of a pentest workflow would benefit most from better orchestration, validation or reporting?” |
| **Cyblex Consulting** | Security consulting | “Would your consultants evaluate a CLI-first tool for evidence-backed assessment workflows?” |
| **Hornetsecurity** | Email/cloud security ecosystem | “Is there a partner route for complementary security assessment and exposure validation?” |
| **ManageEngine** | IT management and security software | “Is there an integration or partner channel for an independent assessment product?” |
| **Predicta Lab** | Security/AI innovation | “Would you be open to reviewing the deterministic verification boundary and evidence model?” |
| **TheGreenBow** | Secure connectivity/VPN | “Do you have partners or customers who need independent validation of network and remote-access configurations?” |
| **TYREX Cyber** | Cybersecurity technology/services | “Would your team review a product focused on repeatable authorized testing and evidence?” |
| **Apixis** | IT solutions integration; CBC exhibitor post interaction | “Do you have customers who need security assessment capabilities or a specialist partner?” |

**Do not spend equal time at every stand.** If the first question reveals no product fit, no customer access and no partnership route, thank them and move on.

---

## 6. CBC programme targets

The published programme gives useful opportunities to meet people around a shared topic. Check the current official schedule before travel because sessions may change.

### Wednesday 25 November

- **10:30 — Gatewatcher:** “De la détection à la décision…” Attend if possible; introduce yourself afterward and ask about assessment/validation complementarity.
- **10:40 — Commvault:** cyber resilience pitch. Useful context for operational resilience, evidence retention and recovery.
- **10:50 — HPE Aruba Networking:** post-quantum network transition.
- **11:00 — Exaprobe:** securing AI environments with CrowdStrike.
- **11:30–12:00 — CHEOPS Technology / Jérémy Voisin:** “Pourquoi attendre l'attaque pour découvrir que votre SOC est aveugle ?” Strong session for the CHEOPS conversation.
- **15:00 — YoungData.io:** data control and security.
- **15:10 — Ordre des Avocats de Toulouse:** legal role in a cyber crisis; useful for understanding authorization, evidence and liability.
- **15:20 — NOVENCI:** insider-risk topic.

### Thursday 26 November

- **10:40 — Pulsiv'IT:** Microsoft Purview/data governance.
- **10:50 — TechValley:** Cybiance Box for SME cybersecurity. Strong opportunity to discuss SME needs.
- **14:40 — Formalize:** AI governance and AI Act.

**Session strategy:** arrive a few minutes early, listen, ask one relevant question, then introduce yourself briefly. Do not hijack Q&A to pitch WHAXON. Ask permission before sending a product brief.

Official programme announcement: https://cbc-convention.com/ and CBC LinkedIn.

---

## 7. The WHAXON demonstration — what to show

The demonstration must be real and repeatable. Do not rely on screenshots alone or present a planned capability as working.

### Recommended 8–10 minute sequence

1. **Position the product (45 seconds).** Explain the problem: fragmented tool execution, inconsistent findings, weak reproducibility and expensive reporting.
2. **Show the CLI (1 minute).** Start with help/version and a prepared lab engagement. Emphasize that the CLI is the operator's primary workflow and does not depend on the browser UI.
3. **Show authorization and scope (1 minute).** Demonstrate the explicit in-scope/out-of-scope configuration and explain that written authorization and external egress controls remain necessary.
4. **Run a controlled lab workflow (2 minutes).** Show discovery/enumeration and a supported scanner/tool adapter. Use only a target you own or have written permission to test.
5. **Show orchestration and findings (1 minute).** Explain how tool output becomes normalized findings and how follow-up work is handled. Do not claim every tool or follow-up path is complete unless tested.
6. **Show deterministic validation (1–2 minutes).** Demonstrate one finding type that is genuinely supported. Explain candidate/verified/inconclusive semantics. An LLM does not assign the verification verdict.
7. **Show evidence and retest (1 minute).** Show preserved request/response or other relevant evidence, provenance and the current retest workflow where supported.
8. **Show the report (1 minute).** Open a report generated from the same engagement. Point out evidence, severity, limitations and what was not tested.
9. **Show the UI only if its exposed workflows are live (optional).** Use the supplied UI and real backend. Hide or avoid pages/controls that remain unimplemented or unverified.

### Demo safety checklist

- Use a disposable local lab or a specifically authorized test target.
- Have a pre-run dataset and a backup demonstration path, but label recorded material honestly.
- Disable external network access unless required for the controlled lab.
- Do not expose credentials, tokens, customer data, private URLs or personal information.
- Have a known-good report already generated in case the live demo fails.
- Do not run scans against an exhibitor, event network, public IP or another attendee's device without explicit written authorization.
- If a capability fails, say so plainly and show the last verified state. Do not improvise a claim.

### Questions to ask the prospect during the demo

- Which part of this workflow is most valuable to your team?
- What would prevent you from using it?
- Which evidence or report fields are mandatory?
- What tool integrations are essential in your environment?
- What would a successful 2–4 week pilot have to prove?
- Who needs to approve a pilot and what would the rules of engagement require?

---

## 8. The 30-second, 90-second and 3-minute pitch

### 30 seconds

> I'm building WHAXON, a cybersecurity assessment platform for authorized engagements. It brings supported security tools into a scope-controlled workflow, normalizes findings, deterministically validates selected issues and preserves evidence for retesting and reporting. I'm looking for a first group of service-provider and end-user partners to validate the commercial workflow.

### 90 seconds

> A lot of security assessment work is still fragmented across tools, output formats, analyst notes and reporting processes. WHAXON is designed to make that workflow more repeatable. The operator defines the engagement and scope, runs supported tools through a common workflow, investigates normalized findings, validates selected finding types using deterministic checks and keeps the evidence connected to the final report and retest.
>
> It is operator-governed: AI may help propose next steps, but it does not authorize testing or decide that a vulnerability is verified. The product is being developed CLI-first so a practitioner can work without depending on the browser UI.
>
> I'm preparing it for commercial deployment and looking for a cybersecurity services partner or pilot customer who can evaluate it against a real, authorized workflow.

### 3 minutes

Add:
- one specific pain point the prospect has identified;
- one actual demonstration;
- one measurable pilot hypothesis;
- a candid list of current limitations;
- one clear ask.

Do not fill three minutes with the entire technical architecture or the other research projects.

---

## 9. The exact asks by category

| Target type | Primary ask | Secondary ask | What counts as success |
|---|---|---|---|
| Cybersecurity services provider | Controlled pilot | Delivery/channel partnership | Named evaluator and pilot-scoping meeting |
| Cybersecurity software vendor | Technical/product review | Integration or partner route | Technical contact and evaluation criteria |
| Infrastructure provider | Deployment support | Hosted lab or customer introduction | Architecture session or pilot environment |
| End-user / CISO | Problem validation and pilot | Referral to procurement/security owner | Discovery meeting and agreed test use case |
| Regional ecosystem | Introductions | Pilot/innovation programme | Two warm introductions and a programme route |
| Business angel network | Funding-readiness review | Mentor/referral to non-dilutive support | Eligibility guidance and named referral |
| Venture fund | Stage/fit assessment | Permission to send deck later | Clear next milestone and fit/no-fit |
| Senior executive | Strategic advice | Introduction to relevant owner | One warm introduction |

### A pilot offer that is small enough to say yes to

Propose a short, bounded evaluation:
- one lab or explicitly authorized environment;
- one defined workflow and a small set of supported tools;
- agreed success criteria before starting;
- no production testing unless authorized in writing;
- compare time-to-assessment, evidence completeness, finding reproducibility, retest usefulness and report quality;
- a short findings review at the end;
- no promise of unsupported integrations or coverage.

Do not offer free indefinite development or unlimited customization. Define a time box and the contribution expected from the partner.

---

## 10. What to prepare before contacting anyone

### Product material

- [ ] One-page WHAXON product brief.
- [ ] 8–10 minute live CLI demonstration.
- [ ] Short recorded backup demo, clearly labelled as a recording.
- [ ] One anonymized sample report generated by the current code.
- [ ] Capability matrix: working, partial, environment-dependent, unverified, unsupported.
- [ ] Supported tool/adapter list with version/platform notes.
- [ ] Validation coverage and verdict semantics.
- [ ] Security model: scope, approval, execution boundaries, credentials, audit/evidence and network-egress limitations.
- [ ] Deployment requirements for a supported Linux/headless setup.
- [ ] Pricing hypothesis and target buyer assumptions, clearly labelled as hypotheses until validated.
- [ ] Short roadmap showing only the next commercially relevant milestones.

### Founder / business material

- [ ] One-page founder profile and relevant experience.
- [ ] Current legal status stated accurately: individual developer; do not imply an incorporated company if none exists.
- [ ] A realistic 6–12 month milestone and cost plan.
- [ ] A funding/use-of-funds outline: engineering capacity, test infrastructure, packaging/deployment, security review, customer pilots and commercial development.
- [ ] A clear explanation of what kind of partner is being sought.
- [ ] A list of what is negotiable and what is not (ownership, IP, exclusivity, support obligations, data handling).
- [ ] A plan for incorporation only after checking the implications and the right structure.

### Do not claim

- [ ] “Fully autonomous pentesting.”
- [ ] “Works against any target” without qualification.
- [ ] “All findings are verified.”
- [ ] “All tools are fully integrated.”
- [ ] “The UI is complete” unless all exposed workflows have passed browser acceptance.
- [ ] “Enterprise-ready” without deployment, security, support and recovery evidence.
- [ ] “AI proves vulnerabilities.”
- [ ] Any existing customer, revenue, partnership or integration that does not exist.

---

## 11. Contact templates

### A. Advens — direct meeting request

**To:** sebastien.francillon@advens.fr  
**Subject:** CBC 2026 — short WHAXON demonstration / potential assessment workflow pilot

> Hello Mr. Francillon,
>
> I saw that the Advens Occitanie team will be at CBC on stand 15. I'm an independent developer in the Toulouse area building WHAXON, an operator-governed platform for authorized security assessments.
>
> WHAXON brings supported tools into a scope-controlled workflow, normalizes findings, deterministically validates selected finding types and preserves evidence for retesting and reporting.
>
> I'd appreciate 20 minutes during CBC to show you the working CLI workflow and understand whether a small, controlled pilot could complement an Advens assessment or consulting process.
>
> I can adapt the demonstration to a lab scenario and will be clear about current coverage and limitations.
>
> Would you have a suitable slot on 25 or 26 November?
>
> Kind regards,  
> [Name]  
> [Email] | [Phone] | [GitHub/repository]

### B. ITrust — channel / technical evaluation

**Route:** official company contact or partner channel; ask for Sébastien Goudouly (Channel & Alliances) and, if appropriate, Mathieu Lagorse (R&D).  
**Subject:** CBC Toulouse — WHAXON technical and channel fit

> Hello,
>
> I'm developing WHAXON, a scope-controlled platform for authorized security assessments, with a focus on tool orchestration, normalized findings, deterministic validation and reproducible evidence/reporting.
>
> ITrust's cybersecurity software and services activity makes it a particularly relevant company for me to speak with. I would like to understand whether WHAXON could complement an ITrust delivery or partner workflow, rather than assume a direct product overlap.
>
> Would it be possible to arrange a short technical/channel discussion during CBC, ideally with the person responsible for alliances or R&D?
>
> I can show a working CLI demonstration and a report generated from a controlled lab.
>
> Kind regards,  
> [Name]

### C. CHEOPS — infrastructure / cyberdefense

**Route:** CBC appointment platform or stand 55; address Jérémy Voisin's team.  
**Subject:** CBC 2026 — WHAXON deployment and cyberdefense partnership discussion

> Hello Mr. Voisin,
>
> I am building WHAXON, a local-first platform for authorized security assessments. I am preparing the product for dependable deployment and am looking for a partner with cybersecurity delivery and infrastructure expertise.
>
> Given CHEOPS Technology's Cyberdefense and infrastructure activities, I would value a short discussion about whether a controlled pilot, deployment review or customer introduction could make sense.
>
> I will bring a real CLI demonstration and be explicit about what is currently supported.
>
> Would you be available during CBC?
>
> Kind regards,  
> [Name]

### D. Cyber'Occ — ecosystem introductions

**To:** contact@cyberocc.fr or official form.  
**Subject:** WHAXON — regional cybersecurity pilot and partner introductions

> Hello,
>
> I'm an independent developer in Occitanie building WHAXON, a cybersecurity assessment and validation platform for authorized engagements. The product is the most mature project I am developing and I am preparing it for commercial deployment.
>
> I would like to identify regional cybersecurity service providers or end-user organizations willing to evaluate a working product in a controlled pilot. Could you advise which regional companies, programmes or contacts would be most relevant?
>
> I can provide a concise product brief and demonstrate the current CLI workflow.
>
> Kind regards,  
> [Name]

### E. Digital 113 — member introductions

**To:** contact@digital113.fr  
**Subject:** CBC 2026 — request for introductions to potential WHAXON pilot users

> Hello,
>
> I am developing WHAXON, a cybersecurity assessment and validation platform for authorized engagements. I saw that Digital 113 will have a pavilion at CBC with regional members.
>
> I am looking for a small number of organizations that could evaluate a working product or provide structured feedback on a real security-assessment workflow. Could you point me toward the most relevant members or decision-makers?
>
> Thank you,  
> [Name]

### F. Occitanie Angels — eligibility-first request

Use the template in section 4.7. Do not submit a formal funding application until the company and eligibility requirements are understood.

### G. Auriga / IRDI / Bpifrance — external prospect

Use a short, tailored note asking for stage-fit guidance. Do not imply they are attending CBC. Attach no large deck until the recipient requests it.

---

## 12. How to run the two days

### Before the event

- [ ] Register and activate the CBC visitor/business-meeting platform.
- [ ] Complete the visitor profile accurately.
- [ ] Search the latest exhibitor and speaker directory for all Priority A and B targets.
- [ ] Request meetings with Advens, ITrust, CHEOPS, Cyber'Occ and Digital 113.
- [ ] Contact Occitanie Angels and Bpifrance separately for funding-path guidance.
- [ ] Ask ITrust to confirm which of the named management contacts will be present.
- [ ] Ask Cyber'Occ and Digital 113 who will attend and who can introduce pilot customers.
- [ ] Recheck all stands, session times and names.
- [ ] Prepare the demo laptop, offline lab, charger, hotspot fallback and printed one-page brief.
- [ ] Do not purchase any paid service, travel upgrade or equipment without checking cost and necessity.

### Wednesday 25 November — commercial and strategic day

Suggested order:
1. Arrive early and confirm appointments.
2. Advens stand 15: highest priority commercial discussion.
3. ITrust: technical/channel discussion.
4. Gatewatcher pitch at 10:30 if useful.
5. CHEOPS/Commvault/HPE pitches and CHEOPS workshop; meet Jérémy Voisin after his session.
6. Digital 113 pavilion: identify actual pilot users, not just other vendors.
7. Orange Cyberdefense speaker/session if available; ask for one referral.
8. End the day by recording notes and sending promised material while conversations are fresh.

### Thursday 26 November — pilots and follow-up day

1. Follow up with any Priority A contact missed on Wednesday.
2. TechValley pitch at 10:50; explore SME pilot/customer access.
3. Keyfactor stand 47; ask for the correct partnership/technical contact.
4. Continue targeted meetings with Cyberwatch, Stormshield, AntemetA, Docaposte and other relevant exhibitors.
5. Revisit any prospect who asked for a demonstration or additional evidence.
6. Before leaving, secure the date and owner for each serious next step.

Do not attempt to visit every stand. Protect time for booked meetings and technical demonstrations.

---

## 13. Conversation discipline and qualification

Use this simple sequence in every meeting:

1. **Ask:** “What are you responsible for, and what are you currently trying to improve?”
2. **Listen:** identify one real workflow pain.
3. **Connect:** explain only the WHAXON capability that addresses that pain.
4. **Demonstrate:** show the smallest real workflow that proves the point.
5. **Qualify:** ask about owner, timing, approval process, environment and success criteria.
6. **Ask:** propose one next step.
7. **Record:** write down the name, role, exact request and agreed follow-up.

### Qualify a potential partner

- Does the organization have a relevant customer or internal workflow?
- Is there a person who owns the problem?
- Can they provide a test environment or authorized pilot?
- Can they contribute technical feedback or infrastructure?
- Is there a realistic route to a paid deployment?
- What procurement, legal, security and support requirements apply?
- What is the next action and date?

### Red flags

- They want free unlimited development with no defined pilot.
- They ask for broad exclusivity before proving commercial value.
- They request access to source code or IP before an agreed evaluation framework.
- They want WHAXON to test a third-party target without written authorization.
- They ask you to make claims or sign commitments you cannot substantiate.
- They offer “exposure” but no concrete introduction, pilot or deliverable.

Do not sign an NDA, exclusivity, IP assignment, reseller agreement, investment term sheet or customer contract on the spot without reviewing it carefully and obtaining appropriate legal advice.

---

## 14. Follow-up messages

### Same day after a useful meeting

**Subject:** CBC follow-up — WHAXON / [agreed topic]

> Hello [Name],
>
> Thank you for taking the time to speak with me at CBC. I appreciated your perspective on [specific point].
>
> As agreed, I am sending [requested item]. The next step we discussed was [specific action] with [owner] by [date].
>
> Please let me know if I have misunderstood anything. I would be glad to arrange the follow-up session.
>
> Kind regards,  
> [Name]

### If they requested a demo

> Hello [Name],
>
> Following our CBC discussion, I would like to schedule the WHAXON technical demonstration around [use case]. I suggest we use a controlled lab and evaluate [two or three agreed criteria].
>
> Would [date/time option] work for you?
>
> Kind regards,  
> [Name]

### If they offered an introduction

> Hello [Name],
>
> Thank you for offering to introduce me to [person/team]. To make the introduction easy, here is a short description you can forward:
>
> “WHAXON is an operator-governed platform for authorized security assessments. It orchestrates supported tools, normalizes findings, deterministically validates selected finding types and preserves evidence for retesting and reporting. The developer is looking for a pilot/technical partner to validate the commercial workflow.”
>
> Thank you again,  
> [Name]

### If no reply after the first approach

Send one concise follow-up after 5–7 business days. If there is no response after that, move on; do not repeatedly chase.

---

## 15. Contact and meeting tracker

Update this table as information changes. Use the CBC meeting platform for actual booking status.

| Priority | Organization / person | Attendance evidence | Contact route | Status | Next action |
|---|---|---|---|---|---|
| A1 | Advens — Sébastien Francillon | Confirmed exhibitor, stand 15; named regional director | sebastien.francillon@advens.fr | Not contacted | Request 20-minute meeting |
| A2 | ITrust — Sébastien Goudouly / Mathieu Lagorse | Company in CBC exhibitor announcement; personal attendance to confirm | Official ITrust site / partner route | Not contacted | Ask who attends and request meeting |
| A3 | CHEOPS — Jérémy Voisin | Confirmed stand 55 and scheduled workshop | CBC platform / stand 55 | Not contacted | Request meeting after workshop |
| A4 | Cyber'Occ | CBC ecosystem/partner listing | contact@cyberocc.fr | Not contacted | Ask for two pilot introductions |
| A5 | Digital 113 | Confirmed CBC pavilion | contact@digital113.fr | Not contacted | Ask for member/customer introductions |
| A6 | Occitanie Angels | Attendance not verified | contact@occitanie-angels.fr | Not contacted | Eligibility-first discussion |
| A7 | Orange Cyberdefense — Olivier de Paillerets | Speaker/keynote listing; personal availability to confirm | CBC programme/platform | Not contacted | Attend session; seek referral |
| B | Cyberwatch | Exhibitor announcement | CBC platform / stand directory | Not contacted | Find alliances/product contact |
| B | Gatewatcher | Exhibitor + published pitch | CBC platform / pitch | Not contacted | Meet after pitch |
| B | Stormshield | Exhibitor announcement | CBC platform / stand directory | Not contacted | Find partnerships contact |
| B | AntemetA | Exhibitor announcement | CBC platform / stand directory | Not contacted | Ask about deployment/customer route |
| B | Bitdefender | Exhibitor announcement | CBC platform / stand directory | Not contacted | Find alliances contact |
| B | Docaposte | Exhibitor announcement | CBC platform / stand directory | Not contacted | Find security innovation contact |
| B | Keyfactor | Confirmed stand 47 | CBC platform / stand 47 | Not contacted | Ask about complementary assessment use case |
| B | Exaprobe | Exhibitor/pitch announcement | CBC platform / pitch | Not contacted | Ask for customer/partner contact |
| B | TechValley | Digital 113 pavilion + pitch | Digital 113 / pavilion | Not contacted | SME pilot discussion |
| B | YoungData | Digital 113 pavilion + pitch | Digital 113 / pavilion | Not contacted | Data-risk customer use case |
| B | CESI | Digital 113 pavilion | Digital 113 / pavilion | Not contacted | Lab/technical collaboration |
| B | Groupama | Digital 113 pavilion | Digital 113 / pavilion | Not contacted | Ask for CISO/security contact |
| B | Heliaq | Exhibitor announcement | CBC platform / stand directory | Not contacted | Find services lead |
| B | HS2 | Exhibitor announcement | CBC platform / stand directory | Not contacted | Find consulting lead |
| B | Cyblex Consulting | Exhibitor announcement | CBC platform / stand directory | Not contacted | Ask about assessment workflow |
| B | Hornetsecurity | Exhibitor announcement | CBC platform / stand directory | Not contacted | Find partner lead |
| B | ManageEngine | Exhibitor announcement | CBC platform / stand directory | Not contacted | Find alliance lead |
| B | Predicta Lab | Exhibitor announcement | CBC platform / stand directory | Not contacted | Technical feedback |
| B | TheGreenBow | Exhibitor announcement | CBC platform / stand directory | Not contacted | Network assessment partner |
| B | TYREX Cyber | Exhibitor announcement | CBC platform / stand directory | Not contacted | Find technical/commercial contact |
| B | Apixis | CBC exhibitor social post interaction | CBC directory | Not contacted | Verify exhibitor presence and relevant contact |
| C | Auriga Cyber Ventures | CBC attendance not verified | Official website | Not contacted | External stage-fit approach |
| C | IRDI Capital Investissement | CBC attendance not verified | Official website | Not contacted | Funding-path enquiry |
| C | Bpifrance | CBC attendance not verified | Regional innovation contact | Not contacted | Eligibility and programme advice |

Suggested status values: \`Not contacted\`, \`Contacted\`, \`Reply received\`, \`Meeting requested\`, \`Meeting booked\`, \`Met\`, \`Follow-up due\`, \`Pilot scoped\`, \`Pilot active\`, \`Closed / no fit\`.

---

## 16. What success looks like after CBC

Do not measure success by the number of stands visited or cards collected.

### Minimum acceptable outcome

- 3–5 relevant conversations with named decision-makers or technical owners;
- 2 warm introductions;
- 1 scheduled technical follow-up;
- 1 realistic pilot opportunity or clear explanation of what is missing;
- 1 credible financing/support route with eligibility and next steps documented.

### Strong outcome

- A services provider agrees to scope a pilot;
- an infrastructure or technical partner offers concrete deployment/engineering support;
- a regional ecosystem organization introduces two prospective customers;
- a financing advisor identifies an eligible non-dilutive route and helps prepare the next application;
- a follow-up meeting is already scheduled.

### After the event — within 7 days

- Send all promised material.
- Schedule the pilot scoping session.
- Write a one-page summary of feedback and product changes.
- Update the product roadmap only for validated customer needs.
- Record any commercial commitments in writing.
- Do not begin unpaid custom development without a scoped agreement.

---

## 17. Research sources and verification links

### Official CBC and event sources

- CBC main event page: https://cbc-convention.com/
- CBC exhibitor announcement (first selection): https://fr.linkedin.com/posts/cbc-cybersecurity-business-convention_exposants-2026-ils-seront-pr%C3%A9sents-activity-7440387240129630208-uJ9t
- CBC exhibitor announcement (additional selection): https://fr.linkedin.com/posts/cbc-cybersecurity-business-convention_cbc2026-cybersecurity-toulouse-activity-7519307400915505152-G0bk
- CBC pitch programme announcement: https://fr.linkedin.com/posts/cbc-cybersecurity-business-convention_pitchs-cbc-j1-j2-activity-7521858688052207616-uETT
- CBC event description and visitor/business format: https://cbc-convention.com/
- Digital 113 CBC pavilion and confirmed members: https://www.digital113.fr/event/cbc-2026-126/register

### Company attendance and contacts

- Advens CBC event and Sébastien Francillon contact: https://www.advens.com/evenements/cbc-2026/
- Advens contact page: https://www.advens.com/nous-contacter/
- ITrust management: https://www.itrust.fr/entreprise-itrust
- ITrust partner information: https://www.itrust.fr/partenaires/
- CHEOPS CBC event, stand 55 and programme: https://www.cheops-technology.com/fr/evenements/cbc-2026
- Keyfactor CBC event, stand 47: https://www.keyfactor.com/events/cyber-security-business-conference/

### Regional ecosystem and funding

- Cyber'Occ overview: https://cyberocc.com/cyberocc/
- Cyber'Occ contact: https://cyberocc.com/contact/
- Official regional cyber contacts: https://messervices.cyber.gouv.fr/contacts/fr-occ
- Occitanie Angels contact: https://occitanie-angels.fr/contact/
- Occitanie Angels funding process and eligibility: https://occitanie-angels.fr/levee-de-fonds/
- Occitanie Angels team: https://occitanie-angels.fr/equipe/
- Auriga Cyber Ventures: https://www.aurigacyberventures.com/
- IRDI Capital Investissement: https://www.irdi.fr/
- Bpifrance: https://www.bpifrance.fr/

### Verification notes

- CBC's public exhibitor list is being updated; more exhibitors may be announced.
- Company-level attendance does not confirm the attendance of a specific executive.
- The names and roles in this playbook should be rechecked shortly before outreach and again before the event.
- Investor organizations listed as external prospects are not represented as CBC attendees.
- Funding criteria can change; re-read the official eligibility page before applying.
- The public information supports a targeted shortlist, not a complete list of all registered visitors. The full visitor register is not publicly available.

---

## 18. Final operating principle

**Make WHAXON the reason someone wants to meet you; make the commercial opportunity the reason they agree to a next step.**

Be specific, demonstrate what works, be candid about limitations, protect your IP and authorization boundaries, and leave every serious conversation with a named owner and a dated action.
