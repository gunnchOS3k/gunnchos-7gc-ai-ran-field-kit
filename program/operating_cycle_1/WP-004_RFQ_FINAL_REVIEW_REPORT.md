# WP-004 — RFQ Send Packet Final Review (Implementer / Preparation)

Generated: 2026-08-10T14:24:37Z  
Role: PREPARATION AGENT (verifier owns `VP-004-RFQ-RESULT.json`)  
Token: `READY_FOR_EDMUND_RFQ_SEND_REVIEW=true` · `RFQ_SENT=false`

## Freeze / authorization

- `PHYSICAL_EXECUTION_FREEZE=ACTIVE`
- `rfq_external_send_authorization=false`
- `purchase_authorized=false`
- Forbidden gates not opened: `RFQ_SENT` / `PURCHASED` / `FABRICATING`
- Cursor will not send RFQs, accept NDAs, purchase, or fab

## Package roots (exact five)

| Product | Root | Version |
|---------|------|---------|
| student_14_5 | `npi/student_14_5/` | STUDENT145-EVT0-R0 |
| ds_xl_coder | `npi/ds_xl_coder/` | DSXL-EVT0-R0 |
| handheld_hybrid | `npi/handheld_hybrid/` | HHYBRID-EVT0-R0 |
| edge_io_rings | `npi/edge_io_rings/` | RING-EVT0-R0 |
| first_party_dock | `npi/first_party_dock/` | DOCK-EVT0-R0 |

RFQ local triad per product: `RFQ_COVER_LETTER.md`, `RFQ_PACKAGE_MANIFEST.json`, `RFQ_QUESTIONNAIRE.md`.

## Hardware revision

| Pin | SHA | PR |
|-----|-----|----|
| Accepted hardware tip | `8705f5a25065e02c7513e990a43e4762967906c5` | #53 Handheld storage NPI |
| Cont IX manufacturing lock | `cd1d906c5f08eb26c350851a4faeb05e2bf2e79f` | #52 Pre-EVT lock |
| Field-kit baseline | `d1922f69bda04f01f47f762d209c36734116f5ce` | #55 |

All 320 Cont IX release file hashes in the five `RELEASE_MANIFEST.json` files match byte-identical content at both Cont IX lock and accepted tip. Tip adds NPI policy artifacts only (no gerber/PnP/STEP/drill delta).

## Digital validation

```text
RFQ_PACKAGE_DIGITAL_DEFECTS = 0
READY_FOR_EDMUND_RFQ_SEND_REVIEW = TRUE
READY_TO_SEND_RFQS = TRUE   # digital coherence token; NOT send authorization
RFQ_SENT = FALSE
```

Validator: `scripts/validate_rfq_packages.py` → `program/pre_evt/RFQ_PACKAGE_VALIDATION.json`

## Defect disclosure (Handheld)

`NPI_DEFECT-HANDHELD-STORAGE-HEADROOM-001` is open under WP-002 (OPERATIONALY_UNSAFE headroom on RM121-D8E32). Disclosed in:

- `npi/handheld_hybrid/rfq/RFQ_COVER_LETTER.md`
- `npi/handheld_hybrid/risk/RISK_REGISTER.json` (`R-HAN-06`)
- Field-kit Phase XV decision JSON

Hardware #53 recommendation favors system eMMC + enforced external/user-media policy; does not invent larger NX5 SKUs. `blocks_rfq_send=false`.

## Confidentiality

All five RFQ covers marked **CONFIDENTIAL — gunnchOS3k internal / Edmund review only** plus DRAFT / DO NOT SEND.

## Recipient / portal readiness

Sourced public routes only (no invented personal contacts):  
`program/operating_cycle_1/RECIPIENT_PORTAL_RESEARCH.json`

| Vendor class | Public route class | Ready for Edmund? |
|--------------|--------------------|-------------------|
| Sierra Circuits | Custom Quote / Turnkey PRO portals | Yes — portal URL sourced |
| AdvancedPCB | Quoting page + support@ email | Yes — portal/email sourced |
| Summit Interconnect | Request-a-quote + contact email | Yes — portal/email sourced |
| ADLINK | Ask an Expert / product pages | Collateral NDA still human |
| Intel RDC | CNDA/Premier access howto + ARK | CNDA human-only |
| Other shortlist CMs | Company class only | Select via A06 before asserting portals |

## NDA decision points

1. **ADLINK COM-HPC** — human NDA before pin-accurate production fanout; draft RFQ allowed with public caveats.
2. **Intel JHL8440/JHL9040R** — human CNDA/RDC before ball maps; draft RFQ allowed with ARK-only.
3. **CM mutual NDA** — human before uploading Cont IX gerbers to any portal (`RFQ_SENT` gate).

## Quote / DFM / shipping

- Quote schema: `program/operating_cycle_1/QUOTE_RESPONSE_SCHEMA.json`
- Quote workbook: `program/pre_evt/shared/QUOTE_COMPARISON_WORKBOOK.csv`
- DFM index: `program/operating_cycle_1/DFM_QUESTION_INDEX.json`
- Quantities: `program/pre_evt/shared/EVT_QUANTITY_SCENARIOS.json`
- Shipping scenarios: `program/operating_cycle_1/SHIPPING_QUANTITY_SCENARIOS.json`

## Edmund packets

A01–A07 remain DRAFT / `do_not_send_from_cursor=true`. External send still requires A06 selection + A07 approval.

## Operating model bootstrap

- `program/operating_model/` mirrored
- `BROAD_COMPLETION_PHASES_FROZEN=true`
- `MAX_ACTIVE_MAJOR_WORKSTREAMS=3`
- `MAX_UNMERGED_DEPENDENT_PR_CHAIN=3`
- `make next-work-packet` → `scripts/next_work_packet.py`
- `ACTIVE_WIP` = WP-002, WP-003, WP-004 only
- `PARITY_REGISTRY_ACCEPTED_MAIN_SYNC_PASS=True` (from frontier_parity tokens; not fabricated)

## Depends-on (for aggregator DRAFT PR)

- WP-002 remains ACTIVE (storage defect open but disclosed)
- WP-003 ACTIVE (parallel; no merge prerequisite found open)
- Prior Phase X package merged as field-kit #44; this PR is Cycle-1 WP-004 reproof + operating-model bootstrap on baseline #55

## Recommendation

```text
READY_FOR_EDMUND_RFQ_SEND_REVIEW = true
```

Edmund may review the packet for eventual send after A06/A07. This does **not** authorize external RFQ send, NDA accept, purchase, or fabrication.
