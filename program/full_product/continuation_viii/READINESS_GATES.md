# Continuation VIII — Release Readiness Gates (R1–R6)

Frozen machine-checkable gates for Cont VIII Lane J.  
Doctrine: `FULL_PRODUCT_ENTIRETY` + `DIGITAL_EXHAUSTION` + `PRE_MANUFACTURING_RELEASE`.  
`PHYSICAL_EXECUTION_FREEZE=ACTIVE`. Cursor never merges. Accepted tips are merged `origin/main` SHAs only.

Schema: [`readiness_gates.schema.json`](readiness_gates.schema.json)  
Instance: [`READINESS_GATES.json`](READINESS_GATES.json)

| Gate | Title | Pass condition (accepted mains only) |
|------|-------|--------------------------------------|
| **R1** | Digital requirement totality | `DIGITALLY_EXECUTABLE_SCHEMA_ONLY/STUB/MOCK = 0` on Cont VIII `DIGITAL_BACKLOG.json` |
| **R2** | Accepted-main baseline integrity | `ACCEPTED_MAIN_BASELINE.json` pins Cont VIII sibling mains; no draft tip as accepted |
| **R3** | Release / claim firewall | `validate_release_firewall.py` + `validate_claim_firewall.py` PASS |
| **R4** | Physical honesty under freeze | Physical audit present; `physical_validation_pending=true`; no physical-complete tokens |
| **R5** | External honesty | External audit present; `external_validation_pending=true`; no cert/carrier-complete tokens |
| **R6** | Scorecard honesty | Manufacturer/assembly/adopter/recreation/student/office_work booleans false unless required artifacts exist |

## Non-claims

- Passing R1–R3 does **not** authorize `DIGITAL_PRE_EVT_RELEASE_READY`, manufacturing orders, or ecosystem user-ready tokens.
- Cont VIII product draft PRs (if any) are registered as pending and must not appear in final umbrella evidence.
- Hardware structural completeness ≠ manufacturer_ready / assembly_ready.
