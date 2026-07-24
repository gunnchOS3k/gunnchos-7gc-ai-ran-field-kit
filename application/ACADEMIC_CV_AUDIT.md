# Academic CV Audit — Edmund Gunn Jr.

**Date:** 2026-07-24  
**Status:** HUMAN_ACTION_REQUIRED  
**Purpose:** Pre-submission audit of CV claims against verifiable evidence

---

## Audit protocol

Each CV line item must map to: (a) verifiable document, (b) status PASS / pending / do-not-claim, (c) red-line flag if overstated.

**Rule:** Remove or downgrade any item that fails red-line review (`../phd_application_readiness_package/checklists/red_line_review_checklist.md`).

---

## Education (verify transcripts)

| Claim | Evidence required | Audit status |
|-------|-------------------|--------------|
| MS Computer Engineering, NYU Tandon | Official transcript | HUMAN_ACTION_REQUIRED — attach PDF |
| Relevant coursework (6G URLLC, wireless lab) | Transcript / syllabus | HUMAN_ACTION_REQUIRED |
| Prior degrees | Transcripts | HUMAN_ACTION_REQUIRED |

**Do not claim:** PhD enrollment, Oulu affiliation, or supervisor relationship before formal acceptance.

---

## Research and engineering portfolio

| Claim | Allowed wording | Evidence | Status |
|-------|-----------------|----------|--------|
| Multi-repo AI-RAN research spine | "Research prototype integrating Edge-IO, digital twin, AI-RAN, NTN modules" | Gate 2 PASS | PASS |
| Gate 1 locked thesis | "Locked doctoral research plan (3 RQs, 3 papers)" | GATE1_LOCKED_RESEARCH_THESIS.md | PASS |
| Physical pilot | "Preregistered 54-session pilot; 0/54 eligible as of 2026-07-24" | Pilot protocol | PASS (honest count) |
| Gate 4 evaluation | "Preregistered evaluation design; not yet run on complete physical data" | EVALUATION_PREREGISTRATION.md | PASS |
| gunnchOS / device quartet | "Research components — not commercial products" | phd package NON_NEGOTIABLES | PASS |
| WAIKE curriculum | "Workload context generator; draft curricula exist" | phd package STATUS_DASHBOARD | PASS |

**Do not claim:** Deployed 6G network, finished hardware product line, completed campuses, live NTN control.

---

## Publications and submissions

| Claim | Audit status | Notes |
|-------|--------------|-------|
| IEEE conference draft | HUMAN_ACTION_REQUIRED | Verify acceptance/submission status before listing |
| SpectrumX competition entry | HUMAN_ACTION_REQUIRED | Verify year, outcome, co-authors |
| Any DOI | BLOCKED unless verified | No fabricated DOIs |

**CV rule:** Use "submitted," "under review," or "draft" only with evidence. Remove "published" without DOI/venue proof.

---

## Awards and recognition

| Claim | Audit status |
|-------|--------------|
| Any award | HUMAN_ACTION_REQUIRED — verify each |

---

## Professional experience

| Claim | Audit status |
|-------|--------------|
| Systems / software engineering roles | HUMAN_ACTION_REQUIRED — verify dates and titles |
| Community / education work (Gary) | PASS if framed as motivation/context, not deployed product |

---

## Skills (evidence-backed only)

| Skill | Evidence |
|-------|----------|
| Python / JSON Schema / validation pipelines | Gate validators in repo |
| Wireless systems fundamentals | Coursework + integrated pipeline |
| Reproducible research practices | Preregistration, provenance, gate taxonomy |
| Academic writing | Paper drafts — verify before claiming proficiency |

---

## Red-line phrases to remove from CV

- "Oulu PhD candidate" (unless enrolled)  
- "Supervised by Professor X" (unless contractual)  
- "Published in [venue]" without proof  
- "Gate 3/4 PASS"  
- "54/54 pilot complete"  
- "6G deployment" or "commercial NTN operator"  

---

## Pre-submission checklist

- [ ] All dates and titles match transcripts  
- [ ] Publication statuses verified  
- [ ] Research description matches Gate 1 title (not old scaffold title)  
- [ ] No Oulu affiliation implied without enrollment  
- [ ] Portfolio link points to honest status dashboard  
- [ ] AI-use disclosure consistent with `10_ai_use_statement.md`  

---

## Action items

1. Export official CV PDF after edits  
2. Cross-check against `CLAIMS_VERIFICATION_MATRIX.csv`  
3. Second-person review before referee packet  

---

*Maintainer: Edmund Gunn Jr. — update after each gate milestone.*
