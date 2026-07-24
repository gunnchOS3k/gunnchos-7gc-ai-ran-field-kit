# Material Placeholder Report

**Generated:** 2026-07-24T15:05:00Z  
**Purpose:** Enumerate placeholders that block `APPLICATION_PACKET_READY = PASS`

---

## Material placeholders (submission-blocking)

These placeholders appear in application or pilot documents and require human-provided authentic values. **Do not auto-fill.**

### Pilot protocol

| Placeholder | Files | Required action |
|-------------|-------|-----------------|
| `PENDING_ZONE_*` | `application/RESEARCH_PLAN_6_PAGE.md`, `pilot/configs/zones_and_days.yaml` | Approve zone identifiers |
| `PENDING_DATE_*` | `application/RESEARCH_PLAN_6_PAGE.md`, `pilot/configs/zones_and_days.yaml` | Approve Day 1–3 dates |
| Network degradation parameters | `protocols/CONTROLLED_PILOT_PROTOCOL.md` | Freeze with attestation |
| `pilot/PILOT_DESIGN_APPROVAL.md` signature | pilot/ | Sign after approval |

### Eligibility and CV

| Placeholder | Files | Required action |
|-------------|-------|-----------------|
| MS transcript PDF | `ACADEMIC_CV_AUDIT.md`, `ELIGIBILITY_AND_DOCUMENT_CHECKLIST.md` | Attach official transcript |
| Prior degree transcripts | `ACADEMIC_CV_AUDIT.md` | Attach |
| English proficiency proof | `ELIGIBILITY_AND_DOCUMENT_CHECKLIST.md` | TOEFL/IELTS or exemption |
| Publication verification | `ACADEMIC_CV_AUDIT.md` | Verify IEEE draft + SpectrumX entry |
| Employment dates/titles | `ACADEMIC_CV_AUDIT.md` | Verify each role |
| Awards | `ACADEMIC_CV_AUDIT.md` | Verify each |

### Referees and funding

| Placeholder | Files | Required action |
|-------------|-------|-----------------|
| `PENDING_REFEREE_1` | `REFEREE_PACKET_CHECKLIST.md` | Name, email, relationship |
| `PENDING_REFEREE_2` | `REFEREE_PACKET_CHECKLIST.md` | Name, email, relationship |
| Funding plan | `ELIGIBILITY_AND_DOCUMENT_CHECKLIST.md` | Program-specific plan |

### Supervision

| Placeholder | Files | Required action |
|-------------|-------|-----------------|
| Confirmed supervisor | `SUPERVISION_PLAN.md` | External commitment only — not invented |

---

## Non-material placeholders (do not block packet automation)

| Item | Reason excluded |
|------|-----------------|
| Mock defense scores | Defense gate, not application packet |
| DOI string | EXTERNAL_DEPENDENCY; labeled DOI_PENDING |
| External reviewer names | EXTERNAL_DEPENDENCY |
| Gate 3 session count 0/54 | Honest status, not a fill-in placeholder |

---

## APPLICATION_PACKET_READY determination

**Material placeholders present:** YES (15 categories above)  
**Verdict:** **APPLICATION_PACKET_READY = HUMAN_ACTION_REQUIRED**

Pass criteria: all material placeholders resolved with authentic human-provided values and claims audit green.
