# Operating Cycle 2 — Final Report (WP-007R correction)

**Generated:** 2026-08-10T22:45:00Z  
**Control plane:** `gunnchos-7gc-ai-ran-field-kit`  
**Cycle scope:** WP-010 + WP-008 + WP-007 only (EVT measurement readiness, NFR freeze, internal red-team readiness)  
**Supersedes:** merged field-kit [#67](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/pull/67) WP-007 evidence pointer — this PR is **DRAFT** correction (Edmund merges LAST; auto-merge OFF).  
**WP-007R brief:** `program/operating_cycle_2/WP-007R_REPORT.md`  
**Promotion honesty:** Cycle 2 **digital stop condition MET** · **accepted-close readiness TRUE** · **accepted-closed FALSE** until Edmund declares. Physical/external/human remain open. RFQs **not** sent. Purchase/fab **not** authorized. WP-001 / Cycle 3 / WP-005+ **not** started.

```text
READY_FOR_EVT0_MEASUREMENT_EXECUTION = true   (digital only; PHYSICALLY_VALIDATED=false)
NFR_TARGETS_FROZEN_FOR_EVT0          = true
INTERNAL_RED_TEAM_READY              = true   (E4 digital Independent PASS; EXTERNAL_PENDING)
independent_verified                 = true
SECURITY_S0 = 0 · SECURITY_S1 = 0
WP007_CANONICAL_EVIDENCE_CONTRADICTIONS = 0
WP-007 = INDEPENDENT_PASS_E4
CYCLE_2_ACCEPTED_CLOSE_READINESS     = true
CYCLE_2_ACCEPTED_CLOSED              = false  (Edmund declaration pending)
VF4/VF5/VF6 = PHYSICAL_PENDING
RFQ_SENT = false · FRONTIER_PARITY = false
purchase_authorized = false
WP-001 / CYCLE_3 = NOT STARTED
```

---

## Correction addendum (WP-007R → Independent PASS E4)

Prior aggregate #67 cited device-os [#93](https://github.com/gunnchOS3k/gunnchos-device-os/pull/93) / tip `4a51298…` as WP-007 PASS. Owner canonical Independent PASS is now:

| Item | Value |
|---|---|
| Status | **`INDEPENDENT_PASS_E4`** |
| Remediation tip (#94) | `7e5ab2f290704ea3fde3b05a23cc171bc901fefb` |
| Independent tip_verified / accepted main at verify | `3908de7c35882b500368475ce13d2243435f6443` |
| Evidence PR | [#96](https://github.com/gunnchOS3k/gunnchos-device-os/pull/96) tip `f627830…` → merge `43bbe20…` (**MERGED**; auto-merge was OFF) |
| Current device-os `origin/main` | `43bbe200f6c55ad77f2f1a4eb2fc5e0a395863b5` (includes #95 + #96) |
| Closures | WP007-IV-DEF-001 **CLOSED**; WP007-IV-RES-001 **CLOSED_DIGITAL**; HOSTILE_NETWORK_DIGITAL=**E4_PASS**; LOCAL_SAVE_INTEGRITY_DIGITAL=**E4_PASS** |
| Consistency | `WP007_CANONICAL_EVIDENCE_CONTRADICTIONS=0` |
| FAIL history | preserved at `artifacts/wp007/history/VP-007-RESULT.initial-fail.0e46609…json` |
| Still pending | EXTERNAL pentest · PRODUCTION_TRUST_ROOT · RF field · authoritative multiplayer |

**WP-010 / WP-008 outcomes unchanged** (READY_FOR_EVT0 / NFR freeze PASS). Hardware [#58](https://github.com/gunnchOS3k/gunnchos-hardware-industrial-design/pull/58) merge state refreshed to MERGED as fact only.

---

## A. Accepted baseline and Cycle 1 close record

**Cycle 1 digital close:** `program/operating_cycle_1/CYCLE_1_DIGITAL_CLOSE_DECISION.json`  
`decision=CLOSED_ACCEPTED` · `authority=EDMUND_USER_DIRECTION_2026-08-10` · `decision_scope=DIGITAL_ONLY`  
Landed via field-kit bootstrap [#64](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/pull/64) (merged).

Known Cycle-start closure refs (newer `origin/main` wins):

| Repo | Cycle-start / known ref | Current `origin/main` (git-verified) | Delta |
|---|---|---|---|
| `gunnchos-device-os` | `99a9825e…` (#89) | **`43bbe200f6c55ad77f2f1a4eb2fc5e0a395863b5`** | +#90..#96 incl. WP-007R remediation #94 + Independent PASS #96 |
| `gunnchos-7gc-ai-ran-field-kit` | `80230dce…` (#63) | **`5ebcc7bf12942e7863927cf93118a6d84c9b243d`** | +#64..#67; this DRAFT supersedes #67 WP-007 pointer |
| `gunnchos-hardware-industrial-design` | `3db78363…` (#55) | **`45c301a3a335d4bfd54970d80ec7ee717736ad07`** | +#56..#58; #58 WP-010R1 **MERGED** (READY outcome unchanged) |
| `gunnchAI3k` | `a28c35c8…` (#30) | **`a28c35c82b45b0a8bfb97648b5941bf0a6b52163`** | unchanged |

**Cycle 1 tokens reconfirmed (digital close record; not re-transformed to physical PASS):**

```text
WP-002 PASS (E4) · WP-003/R/R.1 Independent PASS · WP-004 READY_FOR_EDMUND_RFQ_SEND_REVIEW
G01–G08/G10 E4/D6 · G09 E4/D5 · GJ-DEFECT-005..008 CLOSED
COMPETITOR_MATRIX_CONTRADICTIONS=0 · VF4/5/6 PHYSICAL_PENDING
FRONTIER_PARITY=false · RFQ_SENT=false
```

Verification method this report: `git fetch` / `ls-remote` / `merge-base --is-ancestor` + `gh api` for PR merge state.

---

## B. Active WIP = 3

```text
ACTIVE: WP-010, WP-008, WP-007
WIP_LIMIT: 3
BROAD_COMPLETION_PHASES_FROZEN=true
MAX_UNMERGED_DEPENDENT_PR_CHAIN=3
WP-001=READY_NEXT_AFTER_CYCLE_2
```

| Packet | Status (post-verifier) |
|---|---|
| WP-010 | `INDEPENDENT_PASS_E4` · `READY_FOR_EVT0_MEASUREMENT_EXECUTION=true` |
| WP-008 | `INDEPENDENT_PASS_E4` · `NFR_TARGETS_FROZEN_FOR_EVT0=true` |
| WP-007 | `INDEPENDENT_PASS_E4` · `INTERNAL_RED_TEAM_READY=true` |

All three Independent PASS digitally → **Cycle 2 accepted-close readiness**. Edmund still declares close. No WP-001 / WP-005 / WP-006 / WP-009 / LAB-FUTURE-* / Cycle 3 started.

---

## C. WP-010 result

**Independent VP-010:** **PASS** (E4 digital) after WP-010R1 remediation.  
**Token:** `READY_FOR_EVT0_MEASUREMENT_EXECUTION=true` (**outcome unchanged**)  
**Not claimed:** `PHYSICALLY_VALIDATED=false` · `purchase_authorized=false` · `PHYSICAL_EXECUTION_FREEZE=true`

| Item | Value |
|---|---|
| Prior FAIL | hardware [#57](https://github.com/gunnchOS3k/gunnchos-hardware-industrial-design/pull/57) tip `b968202…` (DEFECT-VP010-001..003) — **MERGED** (historical FAIL; superseded by #58) |
| PASS / RESULT | [#58](https://github.com/gunnchOS3k/gunnchos-hardware-industrial-design/pull/58) head `b4eee53…` → merge **`45c301a…` MERGED** on hardware main |
| Device Lab interfaces | device-os [#90](https://github.com/gunnchOS3k/gunnchos-device-os/pull/90) **MERGED** |
| Closed defects | DEFECT-VP010-001 (audio gate), 002 (AUD/CAM IDs), 003 (KEY/controls IDs) |
| Counts | 41 master tests · 23 instruments · 11 fixtures · RISK-001..012 traced · GOLDEN-01..10 mapped |

Owner artifacts: `gunnchos-hardware-industrial-design/npi/evt0_measurement_readiness/`  
Independent RESULT: `…/independent_verifier/VP-010-RESULT.json`

---

## D. Fixture / instrument matrix

| Register | Count | Path |
|---|---|---|
| Instruments | 23 | `EVT0_INSTRUMENT_MATRIX.json` |
| Fixtures | 11 | `EVT0_FIXTURE_REGISTER.json` |
| Master tests | 41 | `EVT0_MASTER_TEST_MATRIX.json` |

Classification enum used: REQUIRED_OWN / GOOD_TO_OWN / RENT / BORROW / VENDOR_DFM / EXTERNAL_LAB / NOT_NEEDED_EVT0.  
`do_not_purchase_under_freeze=true`. Fixtures digitally complete / **NOT_FABRICATED**. Bring-up order: **network → audio → dock** (mandatory gate restored by WP-010R1).

---

## E. EVT evidence system

`EVT0_EVIDENCE_SCHEMA.json` requires identity (configuration/serial/HW+FW/OS/AI/game SHAs), instrument + calibration fields, raw artifacts, unit/measurement/uncertainty, pass_fail, defect_id, claim_boundary, physical_execution_status.

Supporting:

- `EVT0_BRINGUP_SEQUENCE.md` + safety plan
- `EVT0_RISK_TEST_TRACEABILITY.json` (RISK-001..012)
- `EVT0_ACQUISITION_ACTION_LIST.json` — all PLAN_ONLY; purchase_authorized=false
- `READY_FOR_EVT0_MEASUREMENT_EXECUTION.json` — implementer token with honesty boundary

No pre-populated physical PASS records.

---

## F. Device Lab calibration readiness

device-os [#90](https://github.com/gunnchOS3k/gunnchos-device-os/pull/90) merged interfaces only:

```text
physical_test_id_schema · calibration_ingestion · metric_mapping
prediction_vs_measurement · evidence_linkage · instrument_import_adapters
VF4=VF5=VF6=PHYSICAL_PENDING · CALIBRATED_EVT0=false
public_hosting=false · full_3d_hil=false · LAB-FUTURE-007/008/009 not executed
```

Artifact: `artifacts/wp010_lab_calibration/LAB_CALIBRATION_INTERFACE_READINESS.json`  
Hardware bridge: `DEVICE_LAB_CALIBRATION_BRIDGE_SCHEMA.json` (vf_status const PHYSICAL_PENDING).

---

## G. WP-008 target registry

**Independent VP-008:** **PASS** (E4) on tip `60a0d5ba035c020b30d16cae0f1802fe96dd2184`  
**Token:** `NFR_TARGETS_FROZEN_FOR_EVT0=true` (**outcome unchanged**)  
**PRs:** implementer [#65](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/pull/65) + RESULT [#66](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/pull/66) — **both MERGED** onto field-kit main.

| Metric | Value |
|---|---|
| Targets | 47 |
| Numeric threshold present | 38 |
| Honest TBD residuals | 9 |
| competitor_score non-null | 0 |
| Strategies | MUST_MATCH 34 · MUST_EXCEED 10 · DIFFERENT_APPROACH 2 · NOT_RELEVANT 1 |

Registry path: `program/operating_cycle_2/wp-008_evt0_nfr_target_freeze/`  
(`EVT0_NFR_TARGET_REGISTRY.json`, source ledger, competitor matrix, measurement map, TBD residuals, validator).

---

## H. Competitor target rationale

WP-008 converts competitor strategy into measurable targets without inventing competitor measurements:

- **MUST_MATCH** — parity floors (thermal skin, storage reserve, dock PD class, Wi-Fi 6E minimum, crash/data-loss zeros, etc.)
- **MUST_EXCEED** — local-first AI privacy/offline, Rings safety/confidence gates, offline education continuity, network intent differentiators
- **DIFFERENT_APPROACH** — e.g. local AI power accounting vs cloud energy
- **NOT_RELEVANT** — e.g. fan acoustic until fan decision frozen

External citations are dated class/outcome references only; every `competitor_score` remains **null**. Frontier parity **not** claimed.

---

## I. Target gaps / TBDs

Nine honest residuals (`EVT0_TBD_RESIDUALS.json`); none block immediate EVT safety/integrity decisions:

| ID | Residual |
|---|---|
| NFR-RING-004 | pose drift mm — needs reference fixture |
| NFR-AI-001/002/003/005 | Fast/Pro TTFT, tok/s, RSS, power — EVT silicon |
| NFR-PWR-001 | idle/load watts — EVT characterization |
| NFR-ACOUSTIC-001 | fan dBA — N/A or TBD if fan |
| NFR-STOR-002 | microSD write class matrix |
| NFR-NET-002 | Wi-Fi Mbps — lab AP profile |

Instrument fields were provisionally `TBD_WP010` at freeze time; WP-010 matrices now exist digitally — consume on WP-001 freeze / physical planning without moving goalposts retroactively (change-control required for numeric edits).

---

## J. WP-007 threat model

Owner: `gunnchos-device-os/docs/security/wp007/THREAT_MODEL.md` (+ living `docs/security/THREAT_MODEL.md`).

STRIDE + privacy/AI across boot/update/identity/secrets/packages/sandbox/dev-mode/MDM/AI/Rings/Fabric/Continuity/Device Lab/modem/game/WAIKE/telemetry/factory.  
S0/S1 block readiness; external pentest remains E7 / `EXTERNAL_PENDING`.

Coverage adequate for **E4 digital** (`threat_model_coverage_adequate_for_e4_digital=true`); honest external gaps: pentest, physical FI, carrier, live MCP/Skills, multiplayer anti-cheat, production HSM/TPM signing.

---

## K. Attack corpus / results (canonical Independent PASS)

| Layer | Result |
|---|---|
| Implementer harness | `artifacts/wp007/RED_TEAM_RESULTS.json` — S0=0 S1=0 (comparison only) |
| Independent plan | `artifacts/wp007/independent_verifier/INDEPENDENT_ATTACK_PLAN.md` |
| Independent runner | `run_independent_attacks.py` → `INDEPENDENT_ATTACK_RESULTS.json` |
| Independent suite | **35/35 PASS · S0=0 · S1=0** |
| Lab probes | IV-LAB-001..005 PASS (deny unapproved/unregistered/host; allow registered + default; no escape) |
| Remediation tip | `7e5ab2f…` (#94) ⊆ Independent accepted main `3908de7…` |
| Evidence on main | #96 merge `43bbe20…` |

Prior Independent **FAIL** preserved (`history/VP-007-RESULT.initial-fail.0e46609…json` from #92 era). Early #93 lab-path PASS superseded as **canonical** by WP-007R Independent PASS on #96 / main `3908de7` verify baseline.

---

## L. Security defects / remediations

Implementer register `docs/security/wp007/DEFECT_REGISTER.json` + Independent residual status:

| ID | Severity | Status |
|---|---|---|
| WP007-DEF-001..008 | S1 | FIXED / HOLDS |
| WP007-DEF-009 | S2 | HOSTILE_NETWORK_DIGITAL=**E4_PASS** · RF **EXTERNAL_PENDING** |
| WP007-DEF-010 | S2 | LOCAL_SAVE_INTEGRITY_DIGITAL=**E4_PASS** · multiplayer **EXTERNAL_PENDING** |
| WP007-IV-DEF-001 | S2 | **CLOSED** (reconfirmed on `3908de7`) |
| WP007-IV-RES-001 | S2 | **CLOSED_DIGITAL** · PRODUCTION_TRUST_ROOT **EXTERNAL_PENDING** |
| WP007-IV-RES-002 | S2 | HOSTILE_NETWORK_DIGITAL=**E4_PASS** |
| WP007-IV-RES-003 | S2 | LOCAL_SAVE_INTEGRITY_DIGITAL=**E4_PASS** |

`SECURITY_S0_open=0` · `SECURITY_S1_open=0` · `in_scope_residual_digital_s2_open=0` · contradictions=0.

---

## M. External security work

`docs/security/wp007/EXTERNAL_ASSESSMENT_PACKET.md` — **PREPARED_NOT_EXECUTED**.  
`EXTERNAL_PENDING=true` · `production_ready=false` · `frontier_security_parity=false`.  
Do not claim EXTERNAL pentest PASS / production trust / RF field / multiplayer integrity.

---

## N. Golden Journey E5 / E6 mapping

`EVT0_E5_GOLDEN_JOURNEY_MEASUREMENT_MAP.json` maps GOLDEN-01..10 → EVT-* measurement IDs and `e4_to_e5_required` evidence lists. Doctrine: digital ≠ physical; VF4/5/6 PHYSICAL_PENDING.

Notable physical gaps retained from Cycle 1:

- G04 dock SI · G06 dual-panel · G07 Ring SI → E5 PHYSICAL_PENDING  
- G08 tutoring/UX → E6 HUMAN_VALIDATION_PENDING  

WP-007 GJ control map: `docs/security/wp007/GOLDEN_JOURNEY_CONTROL_MAP.json`. Owner: GJ merge gate supporting_run_ok on Independent PASS tip; S0/S1 regression blocks merge recommendation.

---

## O. Risks / unknowns updated

Light Cycle 2 updates only (no invented score collapses):

- **RISK-001..012** all traced into WP-010 master matrix / bring-up; next experiment = physical EVT after WP-001 freeze + freeze lift (not authorized here).
- **RISK-009** (graphics/display/AV): EVT-AUD-001 / EVT-CAM-001 / EVT-KEY-* bindings (digital).
- **RISK-007** (Ring drift): measurement IDs exist; numeric mm NFR remains TBD (NFR-RING-004).
- **RISK-008** (local AI perf): NFR AI family frozen with silicon TBDs.
- **UNK / Device Lab:** VF4/5/6 still PHYSICAL_PENDING; calibration interfaces only.
- **WP-007R:** digital S2 residuals closed at E4; EXTERNAL gaps unchanged.

Risk register scores in field-kit operating model remain the Cycle 1 baseline (RISK-004 still 48 post Outcome A); no silent likelihood edits in this aggregate.

---

## P. PRs / CI / merge order

| Repo | PR | Head / merge SHA | State | Role | autoMerge |
|---|---|---|---|---|---|
| hardware | #56 | `611d51d…` / `9877b3c…` | **MERGED** | WP-010 implementer base | null |
| hardware | #57 | `b968202…` | **MERGED** (FAIL RESULT) | historical; superseded by #58 | null |
| hardware | #58 | `b4eee53…` / **`45c301a…`** | **MERGED** | WP-010R1 + VP-010 PASS | was OFF |
| device-os | #90 | `d5ff4ea…` | **MERGED** | Lab calibration interfaces | null |
| device-os | #91 | `9bf235a…` | **MERGED** | WP-007 implementer | null |
| device-os | #92 | `90939a4…` | **MERGED** | VP-007 FAIL artifacts (history) | null |
| device-os | #93 | `4a51298…` / `0e46609…` | **MERGED** | lab-path CI fix (superseded as canonical by #96) | null |
| device-os | #94 | `7e5ab2f…` / **`3908de7…`** | **MERGED** | WP-007R remediation | was OFF |
| device-os | #96 | `f627830…` / **`43bbe20…`** | **MERGED** | Independent PASS artifacts | was OFF |
| field-kit | #64 | `2437a69…` / `d9c3c07…` | **MERGED** | Cycle 2 bootstrap + ACTIVE_WIP | null |
| field-kit | #65/#66 | `60a0d5b…` / `d4637b6…` | **MERGED** | WP-008 + VP-008 PASS | null |
| field-kit | #67 | `4ab360f…` / `5ebcc7b…` | **MERGED** | prior Cycle 2 aggregate (WP-007 pointer superseded) | was OFF |
| field-kit | [#68](https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/pull/68) | `01503ef…` / merge `7ab5467…` | **MERGED** (created DRAFT; Edmund merged) | WP-007R correction aggregate | was OFF |
| field-kit | **this** | *(tip after push)* | **OPEN DRAFT** | tip/merge metadata sync only | **OFF** |

**Exact Edmund merge order (remaining):**

1. **Confirm already-merged:** hardware #58 · device-os #90/#91/#92/#93/#94/#96 · field-kit #64/#65/#66/#67  
2. **LAST: this field-kit DRAFT** — after review; keep DRAFT until then; auto-merge OFF  
3. **Declare Cycle 2 digital accepted-close** (or reject with defects) — #96 merge alone ≠ program close  

CI: VP-010/VP-008/VP-007R recorded PASS on verified tips. This aggregate aims CI green (docs/JSON only).

---

## Q. Edmund-only actions

1. **Confirm hardware #58 MERGED** — READY_FOR_EVT0 on hardware main; **does not** authorize purchase/fab/run. Outcome unchanged.  
2. **Confirm device-os #94/#96 MERGED** — remediation + Independent PASS evidence on main.  
3. **Accept Cycle 2 digital stop / declare accepted-close** for WP-010/008/007 Independent PASS (or reject with defects).  
4. **Do not send RFQs** — Cycle 1 WP-004 still `RFQ_SENT=false`.  
5. **Do not lift PHYSICAL_EXECUTION_FREEZE / purchase_authorized** in this cycle.  
6. **Do not start WP-001 / Cycle 3 / WP-005+** automatically — choose next packet deliberately after close.  
7. **Review & merge this field-kit DRAFT last** (keep DRAFT until then; auto-merge OFF).  
8. **External pentest / physical EVT / human panels** remain human/external scheduling — packets prepared, not executed.

---

## R. WP-001 readiness inputs (DISPLAY — do not start)

WP-001 (Freeze `gunnchOS3k-EVT0-1.0`) should pin, when Edmund starts it later:

- Accepted hardware SHA (post-#58) + Cont IX / BOM/CAD/PCB refs  
- device-os accepted main (incl. WP-007R Independent PASS + Lab interfaces) + gunnchAI SHA  
- Device Lab profile/version + VF honesty tokens  
- Golden Journey suite SHAs / scorecards  
- WP-010 test-book + instrument/fixture matrices + evidence schema  
- WP-008 `EVT0_NFR_TARGET_REGISTRY.json` (+ TBD residual list)  
- WP-007 threat model + Independent PASS RESULT (`VP-007R-RESULT.json`) + EXTERNAL packet pointer  

Only after that freeze should fabrication/purchase authorization be considered.

---

## S. Next top five backlog items — DISPLAY ONLY

Output of `python3 scripts/next_work_packet.py` with ACTIVE still holding WP-010/008/007 (do **not** start):

```text
ACTIVE: WP-010,WP-008,WP-007
WIP_LIMIT: 3
NEXT_READY_AFTER_CYCLE:
  WP-001 score=20 Freeze EVT0 configuration manifest
  WP-006 score=18 License release gate first complete audit
  WP-005 score=15 Human digital usability panel pilot
```

**Top 5 READY display (not started):**

1. **WP-001** — Freeze EVT0 configuration manifest (score 20) — **first next after Cycle 2**  
2. **WP-006** — License release gate first complete audit (score 18)  
3. **WP-005** — Human digital usability panel pilot (score 15)  
4. **WP-009** — Unit economics from RFQ quotes (score 12) — **BLOCKED** (`RFQ_SENT=false`) — display only  
5. **CYCLE_3 / LAB-FUTURE-*** — **NOT STARTED** — do not open  

**Do not start any of the above in this session.**

---

## T. Whether Cycle 2 is truly accepted-closed

```text
All three packets Independent PASS digitally     = YES
CYCLE_2_ACCEPTED_CLOSE_READINESS                 = true
CYCLE_2_ACCEPTED_CLOSED                          = false until Edmund declares
device-os #96 evidence on main                   = YES (already merged)
field-kit correction DRAFT merged                = NO (this PR)
Physical / EXTERNAL / RFQ / purchase             = NOT CLOSED
WP-001 / Cycle 3                                 = NOT STARTED
```

**Honest verdict:** Cycle 2 is **digitally accepted-close ready**, **not** accepted-closed pending Edmund declaration after this DRAFT. Merging #96 alone did not close the cycle.

---

## Stop / honesty footer

- Cycle 2 stop condition **MET** digitally: WP-010 READY · WP-008 NFR frozen · WP-007 **INDEPENDENT_PASS_E4** · S0=S1=0 · contradictions=0.  
- Accepted-close readiness **TRUE**; accepted-closed **FALSE** until Edmund declares.  
- PHYSICALLY_VALIDATED=false · VF4/5/6 PHYSICAL_PENDING · EXTERNAL_PENDING · RFQ_SENT=false · frontier=false.  
- WP-001 / Cycle 3 / WP-005+ **not** started. This PR is **DRAFT** aggregation correction only (auto-merge OFF).
