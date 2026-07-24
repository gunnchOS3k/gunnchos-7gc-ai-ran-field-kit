# Demo — 5 Minutes

**Audience:** Technical faculty / lab group  
**Status:** AUTOMATION_READY — aligns with Gate 3 five-minute rehearsal structure

---

## Pre-demo checklist

- [ ] Branch clean; Gate 1 validator passes  
- [ ] Gate 2 proof path runnable  
- [ ] Rehearsal fixture available (not counted as pilot)  
- [ ] No live claim of 54/54 or Gate 4 PASS  

---

## Minute-by-minute runbook

### Minute 1 — Thesis lock (30s talk + 30s command)

**Say:** "Gate 1 locks title, hypothesis, three RQs, and three papers. Any change requires version bump."

**Run:**
```bash
python scripts/validate_gate1_thesis.py
```
**Show:** GATE_1_PASS output.

---

### Minute 2 — Pipeline architecture (60s)

**Say:** "Edge-IO produces consent-ordered, privacy-scanned measurements. Twin state feeds five AI-RAN baselines and six resilience policies."

**Show:** Architecture from `defense/TECHNICAL_APPENDIX.md` or README diagram.

**Point to:** `contracts/gate1_locked_thesis.v1.json` repository map.

---

### Minute 3 — Gate 2 integrated run (60s)

**Say:** "Gate 2 PASS means executable schema-validated artifacts—not pilot completion."

**Show:** `results/gate2/post_merge_clean_system_proof/gate2_status.json` — `GATE2_SYSTEM_PASS`.

Optional: run integrated rehearsal target if environment configured.

---

### Minute 4 — Pilot + evaluation honesty (60s)

**Say:** "Fifty-four-cell matrix is preregistered. Eligible sessions: zero of fifty-four. Gate 4 is evaluation-ready; results pending authentic data."

**Show:**
- `pilot/PILOT_PROTOCOL_v1.md` matrix line  
- `evaluation/EVALUATION_PREREGISTRATION.md` primary outcome  
- `results/gate4/gate4-run-20260724T001141Z/gate4_status.json` — GATE4_EVALUATION_READY  

**Explicit:** Open `evaluation/GATE4_FINAL_REPORT.md` — RESULTS_PENDING.

---

### Minute 5 — Failure boundaries + Q&A seed (60s)

**Say:** "RQ3 documents where NTN fallback becomes counterproductive. External NTN evidence is source-validated simulation—not a substitute for pilot cells."

**Show:** `evaluation/FAILURE_BOUNDARIES.md` header + `results/external_evidence/EXTERNAL_EVIDENCE_REPORT.md` status.

**Close:** "Questions often focus on independence of sessions, privacy schema, and what happens if matrix stays partial—we preregister missing-data analysis."

---

## Fallback if live run fails

Show cached JSON artifacts and rehearsal report (`GATE3_FIVE_MINUTE_REHEARSAL_REPORT.md`).

---

## Red lines during demo

- Do not label synthetic output as pilot evidence  
- Do not run Gate 4 PASS narrative  
- Do not show faculty fit memos as endorsements  

---

*Rehearsal reference: GATE3_FIVE_MINUTE_REHEARSAL_REPORT.md — PASS on infrastructure.*
