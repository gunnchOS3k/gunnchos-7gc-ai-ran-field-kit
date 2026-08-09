# Phase X — NPI / DFM / EVT Quotation & Vendor Collateral Report (A–P)

Generated: 2026-08-09T22:00:34Z  
PHYSICAL_EXECUTION_FREEZE active · No purchase · No external RFQ send · Cursor never merges

## A — Accepted-main lock

| Repo | SHA | Evidence |
|------|-----|----------|
| field-kit | `029da075038cc5a388d993827fb8ffbd981afbeb` | #43 merged on origin/main |
| device-os | `657e195de91f8f20766a4257e6ef1636eb9f2014` | #69 merged on origin/main |
| hardware | `cd1d906c5f08eb26c350851a4faeb05e2bf2e79f` | #52 Cont IX |
| edge-io | `a1cd2e95c62eb0eefd507b976158232b83f5b33b` | accepted tip |
| gunnchAI | `91a9f135b6423a7627ed61946b16e9ab9d79de6e` | accepted tip |
| anime | `249270383eab87cf4d1240ea17e66bfff44d4b8c` | accepted tip |
| pedestrian | `a2c6da5b4d4635af1281dbb12b8564ba70f994c6` | accepted tip |
| archive | `948ca172bb77b4caf1bd3c2d809d74ee6d4b6c75` | accepted tip |
| beatlink | `e0c18f3dbb964608271c14611e1068cff9c17205` | accepted tip |

`DIGITAL_OPEN=0` · `DIGITAL_RELEASE_LOCK_COMPLETE=true` · Lock file: `program/pre_evt/ACCEPTED_MAIN_LOCK.json`

## B — RFQ digital-defect count

```text
RFQ_PACKAGE_DIGITAL_DEFECTS = 0
```

Validator: `program/pre_evt/RFQ_PACKAGE_VALIDATION.json`

## C — Five RFQ package status

| Product | Version | Token | RFQ path | Status |
|---------|---------|-------|----------|--------|
| student_14_5 | STUDENT145-EVT0-R0 | CONDITIONAL_VENDOR_COLLATERAL | `npi/student_14_5/rfq/` | DRAFT_READY |
| ds_xl_coder | DSXL-EVT0-R0 | CONDITIONAL_VENDOR_COLLATERAL | `npi/ds_xl_coder/rfq/` | DRAFT_READY |
| handheld_hybrid | HHYBRID-EVT0-R0 | MANUFACTURER_PACKAGE_READY | `npi/handheld_hybrid/rfq/` | DRAFT_READY |
| edge_io_rings | RING-EVT0-R0 | RING_MANUFACTURER_PACKAGE_READY | `npi/edge_io_rings/rfq/` | DRAFT_READY |
| first_party_dock | DOCK-EVT0-R0 | CONDITIONAL_VENDOR_COLLATERAL | `npi/first_party_dock/rfq/` | DRAFT_READY |

## D — Vendor-collateral requests

Exact matrix: `program/pre_evt/shared/VENDOR_COLLATERAL_MATRIX.json`  
Public-first integration: `program/pre_evt/shared/PUBLIC_VENDOR_COLLATERAL_INTEGRATED.json`  
Packets: ADLINK COM-HPC, Intel JHL8440/JHL9040R (NOT TB5), display/touch/hinge, battery, antenna/RF, paste/torque.

EXTERNAL residual remains for NDA pin/ball maps after public wiki/ARK/PICMG CDG integrated.

## E — NPI/manufacturer shortlist

See `program/pre_evt/shared/NPI_MANUFACTURER_SHORTLIST.json`.  
Hybrid strategy recommended (multi-vendor EVT0 specialty + primary CM candidates for EVT1).

## F — EVT0/EVT1 quantity scenarios

See `program/pre_evt/shared/EVT_QUANTITY_SCENARIOS.json` (MIN/REC + spares/destructive/reserve). **No orders.**

## G — BOM price / availability / supply-risk

Per-product `npi/*/bom/QUOTE_READY_BOM.csv` + `SUPPLY_RISK_MATRIX.json`.  
Public indicative: Intel JHL8440 RCP ~$12.05, JHL9040R ~$3.00; ADLINK/Radxa/Quectel = contact/distributor check. Availability = UNKNOWN_AT_RFQ_TIME.

## H — DFM / high-speed / RF review questions

`npi/*/dfm/DFM_REVIEW_QUESTIONS.md` (+ ring special section) and mechanical/battery/display/RF inquiry packets.

## I — Fixture and equipment plans

`npi/*/factory_test/FIXTURE_PLAN.json` — ICT/FCT/programming/RF/mechanical + equipment classification.

## J — EVT acceptance matrix

`npi/*/evt/EVT_ACCEPTANCE_MATRIX.md` — unknown limits marked `TARGET_TO_CONFIRM`.

## K — Risk register

`npi/*/risk/RISK_REGISTER.json` + shared cost/strategy risks (NDA latency, long-lead modules, host cert gap).

## L — Cost model and quote-comparison system

- `program/pre_evt/shared/PROTOTYPE_COST_MODEL_RANGES.json`
- `program/pre_evt/shared/QUOTE_COMPARISON_TEMPLATE.md`
- `program/pre_evt/shared/QUOTE_COMPARISON_WORKBOOK.csv`
- `program/pre_evt/shared/MANUFACTURER_SELECTION_RUBRIC.md`

## M — Compliance / carrier pre-scan

`program/pre_evt/shared/COMPLIANCE_CARRIER_PRESCAN_PLAN.json` — RM520N-GL module public certs noted; **host not claimed certified/carrier-approved**.

## N — Edmund action packets

`program/pre_evt/edmund_packets/A01`…`A07` — objective, recipient, files, proposed text, risks, expected response. **Not sent.**

## O — PRs

| repo | PR | branch | SHA | CI | autoMergeRequest |
|------|----|--------|-----|----|------------------|
| field-kit | (opening) | `phase-x/npi-dfm-evt-quotation` | (head after push) | pending | `null` |

Hardware: Cont IX artifacts reused via SHA pointers — no mandatory hardware delta PR.

## P — Recommendation

```text
READY_TO_SEND_RFQS
```

Does **not** authorize purchase, fab, NDA accept, or external RFQ send without Edmund A06/A07.
Forbidden token not used: `READY_TO_PURCHASE`.

### Digital blockers
None — RFQ_PACKAGE_DIGITAL_DEFECTS=0
