# Faculty Fit Memo — Markku Juntti

**Applicant:** Edmund Gunn Jr.  
**Faculty:** Professor Markku Juntti, University of Oulu  
**Unit:** CWC-Radio Technologies (Research Unit Leader); CSP Research Group  
**Date:** 2026-07-24  
**Access date for sources:** 2026-07-24

---

## Disclaimer

**NO commitment, endorsement, funding guarantee, or supervision agreement is claimed.** This memo is applicant-prepared fit analysis for potential outreach only.

---

## 1. Faculty research summary (public sources)

Professor Juntti (IEEE Fellow) leads CWC-Radio Technologies and the Communications Signal Processing (CSP) group. Public profiles emphasize **signal processing for wireless networks**, MIMO, beamforming, detection/decoding, radio resource management, interference coordination, and **terahertz communications and sensing for 6G**. He serves as PI in numerous EU and national projects (e.g., TERA6G, ARIADNE, TERRANOVA, DUPLO) and contributes to doctoral education development at CWC.

---

## 2. Research overlap with dissertation

| Dissertation element | Juntti group overlap |
|---------------------|----------------------|
| RQ2 fairness / worst-user performance | RRM; interference coordination |
| Optional ReadyGary PHY | Beamforming / blockage sensitivity |
| 6G PHY abstraction for orchestration | THz/sensing surveys — parameter bounds |
| RQ3 NTN (secondary) | Multi-access at PHY/MAC boundary |
| RQ1 device measurement (tertiary) | Less central than IoT/edge groups |

**Strongest fit:** PHY-aware sensitivity analysis and RRM baselines for Paper 2; optional beam/blockage assumptions for ablations—not primary supervisor unless PHY-forward thesis desired.

---

## 3. Completed vs pending evidence (applicant)

| Evidence | Status |
|----------|--------|
| readygary-6g-beam-selection (optional repo) | Optional — not required for thesis |
| Gate 2 AI-RAN orchestration | PASS |
| PHY-layer field measurements | **Not claimed** |
| Joint publication | **None** |
| Eligible pilot sessions | **0/54** |

---

## 4. Proposed first joint paper (if supervision aligned)

**Working title:** *PHY-Sensitive Ablations for Twin-Informed AI-RAN Service Continuity*

- **RQ focus:** RQ2 with optional PHY sensitivity (not a fourth paper)  
- **Contribution:** Quantify when beam/blockage assumptions change orchestration rankings; keep ReadyGary optional  
- **Juntti group role:** PHY parameter credibility; RRM baseline review  
- **Applicant role:** Orchestration pipeline, preregistered ablations  
- **Boundary:** ReadyGary remains optional per Gate 1; no fourth RQ  

---

## 5. Lab / infrastructure needs

| Need | Notes |
|------|-------|
| CWC-RT lab / THz test assets | Sensitivity studies only if accepted |
| Channel measurement campaigns | Not required Year 1 |
| RRM simulation tools | Align optimization_based baseline |
| Doctoral training in CWC-RT | If primary supervisor |

---

## 6. Co-supervision angle

| Partner | Rationale |
|---------|-----------|
| Ari Pouttu | System-level testbed integration |
| Mehdi Bennis | ML/edge-intelligence policies |
| Konstantin Mikhaylov | NTN leg if PHY-MAC co-design needed |

Juntti as **co-supervisor** often pairs with experimental-networks or edge-AI primary.

---

## 7. First-year plan (summary)

Q1–Q2: Literature map THz/beamforming assumptions vs orchestration metrics.  
Q3: Optional ReadyGary sensitivity branch if time permits.  
Q4: Ablations section for Paper 2 — PHY uncertainty bands.

---

## 8. Funding routes (unconfirmed)

| Route | Status |
|-------|--------|
| CWC-RT / EU project doctoral lines | EXTERNAL_DEPENDENCY |
| 6G Flagship | EXTERNAL_DEPENDENCY |
| Business Finland co-innovation | EXTERNAL_DEPENDENCY |

**No funding route is confirmed.**

---

## 9. One technical question for faculty

> When orchestration policies are evaluated at service-continuity timescales (seconds-level recovery), which PHY-layer parameters (beam misalignment, blockage, SINR thresholds) does CWC-RT treat as mandatory explicit ablations versus safely abstractable in AI-RAN studies?

---

## 10. Source list

| Source | URL | Accessed |
|--------|-----|----------|
| 6G Flagship biography | https://www.6gflagship.com/people/markku-juntti/ | 2026-07-24 |
| CWC-Radio Technologies unit page | https://www.oulu.fi/en/university/faculties-and-units/faculty-information-technology-and-electrical-engineering/cwc-radio-technologies | 2026-07-24 |
| Google Scholar profile | https://scholar.google.co.uk/citations?user=1QahFcsAAAAJ | 2026-07-24 |

---

*Prepared for internal outreach planning — not a letter of support.*
