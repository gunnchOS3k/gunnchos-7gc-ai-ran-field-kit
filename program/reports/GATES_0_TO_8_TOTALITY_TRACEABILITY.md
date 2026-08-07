# Gates 0–8 Totality Traceability

Updated: `2026-08-07T22:25:00Z`  
Program mode: **NONPHYSICAL_TOTALITY**  
Physical execution freeze: **ACTIVE**

## Rules

- Evidence class uses `program/nonphysical/evidence_classification.yaml`.
- `PHYSICAL_PENDING` means authentic measured/human/external evidence is not yet captured; digital artifacts may still exist.
- This matrix does **not** assert `GATE_N_PASS` for any `N >= 1`.
- Gate 0 retains historical `GATE_0_PASS` on the pass axis only where already accepted in control-plane records.

## Artifact roots

| Root | Role |
|---|---|
| `program/` | Control-plane charters, requirements, claims, gates, nonphysical status, physical prep packs, reports |
| `gate1/` … `gate8/` (and `gate2/`–`gate3/` packets) | Gate execution packets, nonphysical modules, software evidence |
| `device_designs/` | Per-device digital design packages (CAD/BOM/ICD/firmware manifests); physical build still `PHYSICAL_PENDING` |
| `standards/` | Standards mapping / watch artifacts (create when Gate 8 nonphysical mapping lands) |

## Traceability table

| Gate | Criterion ID | Criterion | Linked artifacts | Evidence class | Blocker |
|---|---|---|---|---|---|
| 0 | G0-C1 | Product charter approved | `program/charters/CHARTER_APPROVAL_RECORD.yaml`, `program/charters/CHARTER_SOURCE_RECORD.yaml` | DIGITAL_DESIGN_ARTIFACT | — |
| 0 | G0-C2 | Device roles frozen | `program/requirements/device_role_baseline.yaml`, `program/decisions/DR-0002-DEVICE-ROLE-BASELINE.md` | DIGITAL_DESIGN_ARTIFACT | — |
| 0 | G0-C3 | Requirement identifiers assigned | `program/requirements/requirements.yaml`, `program/reports/GATE_0_REQUIREMENTS_TRACEABILITY_MATRIX.md` | DIGITAL_DESIGN_ARTIFACT | — |
| 0 | G0-C4 | Claims classified | `program/claims/claims.yaml`, `program/claims/claim_taxonomy.yaml` | DIGITAL_DESIGN_ARTIFACT | — |
| 0 | G0-C5 | Repository ownership established | `program/repositories/repository_ownership.yaml`, `program/repositories/ecosystem_version_lock.yaml`, `program/decisions/DR-0005-CANONICAL-REPOSITORY-SET.md` | DIGITAL_DESIGN_ARTIFACT | — |
| 1 | G1-C1 | gunnchOS boots on representative hardware | `gate1/reports/GATE_1_AUTOMATED_COMPLETION_REPORT.md`, `gate1/contracts/device_identity.schema.json`, `gate1/evidence/pending/` | SOFTWARE_TEST (+ MEASURED required for PASS) | REQUIRES_LOCAL_HARDWARE; PHYSICAL_PENDING |
| 1 | G1-C2 | Ring prototype sends authenticated input | `gate1/contracts/authenticated_input.schema.json`, `gate1/reports/GATE_1_IMPLEMENTATION_MATRIX.md`, `device_designs/edge_io_rings/` (when present) | SOFTWARE_TEST / DIGITAL_DESIGN_ARTIFACT | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 1 | G1-C3 | At least one device docks successfully | `gate1/contracts/dock_session.schema.json`, `gate1/evidence/pending/` | SOFTWARE_TEST | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 1 | G1-C4 | gunnchAI3k local runtime functions | `gate1/contracts/local_ai_runtime.schema.json`, `gate1/reports/GATE_1_IMPLEMENTATION_MATRIX.md` | SOFTWARE_TEST | REQUIRES_LOCAL_HARDWARE; PHYSICAL_PENDING |
| 1 | G1-C5 | Each game completes one core loop | `gate1/contracts/game_core_loop.schema.json`, game repos via `program/repositories/ecosystem_version_lock.yaml` | SOFTWARE_TEST | AUTOMATABLE_AFTER_DEPENDENCY; PHYSICAL_PENDING |
| 2 | G2-C1 | Representative enclosure | `device_designs/*/mechanical/`, `gate2/GATE_2_EXECUTION_PACKET.md`, `program/physical/MASTER_PHYSICAL_BUILD_AND_TEST_BOOK.md` | DIGITAL_DESIGN_ARTIFACT | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 2 | G2-C2 | Working display and controls | `device_designs/*/`, `gate2/GATE_2_EXECUTION_PACKET.md` | SOFTWARE_TEST / DIGITAL_DESIGN_ARTIFACT | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 2 | G2-C3 | Real battery and thermal measurements | `program/physical/MASTER_TEST_EQUIPMENT_LIST.csv`, `program/physical/MASTER_EVIDENCE_CAPTURE_SEQUENCE.md`, `program/gates/physical_gate_registry.yaml` | MEASURED (required) | REQUIRES_LOCAL_HARDWARE; PHYSICAL_PENDING |
| 2 | G2-C4 | Secure boot | `device_designs/*/firmware/`, `gate2/GATE_2_EXECUTION_PACKET.md` | SOFTWARE_TEST / DIGITAL_DESIGN_ARTIFACT | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 2 | G2-C5 | Signed update | `device_designs/*/firmware/`, `gate2/GATE_2_EXECUTION_PACKET.md` | SOFTWARE_TEST / DIGITAL_DESIGN_ARTIFACT | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 2 | G2-C6 | Device-specific game UX | `gate2/GATE_2_EXECUTION_PACKET.md`, game repos lock pins | SOFTWARE_TEST | AUTOMATABLE_AFTER_DEPENDENCY |
| 2 | G2-C7 | Ring calibration and fallback | `device_designs/edge_io_rings/`, EdgeGesture lock pin | SOFTWARE_TEST / SIMULATED | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 3 | G3-C1 | Cross-device identity and continuity | `gate3/GATE_3_EXECUTION_PACKET.md`, `gate3/GATE_3_REQUIREMENTS_MATRIX.md`, `program/requirements/requirements.yaml` | SOFTWARE_TEST | AUTOMATABLE_AFTER_DEPENDENCY |
| 3 | G3-C2 | Multi-device saves | `gate3/GATE_3_EXECUTION_PACKET.md` | SOFTWARE_TEST | AUTOMATABLE_AFTER_DEPENDENCY |
| 3 | G3-C3 | Connectivity manager | `gate3/GATE_3_EXECUTION_PACKET.md`, connectivity research repos in lock | SOFTWARE_TEST / SIMULATED | AUTOMATABLE_AFTER_DEPENDENCY |
| 3 | G3-C4 | Fleet observability | `gate3/GATE_3_EXECUTION_PACKET.md`, `edge-io-measurement-node` pin | SOFTWARE_TEST / SIMULATED | AUTOMATABLE_AFTER_DEPENDENCY |
| 3 | G3-C5 | Security threat models | `gate3/GATE_3_EXECUTION_PACKET.md`, `program/claims/` | ANALYSIS / DIGITAL_DESIGN_ARTIFACT | AUTOMATABLE_NOW |
| 3 | G3-C6 | 7GC test plans | `gate3/GATE_3_EXECUTION_PACKET.md`, `7gc-digital-twin` / SpectrumX / NTN pins | PREPARATION_PACKET / SIMULATED | AUTOMATABLE_NOW |
| 3 | G3-C7 | Repair procedure | `gate3/GATE_3_EXECUTION_PACKET.md`, `program/physical/MASTER_ASSEMBLY_SEQUENCE.md` | DOCUMENTATION / DIGITAL_DESIGN_ARTIFACT | AUTOMATABLE_NOW |
| 4 | G4-C1 | Real users | `program/gates/human_action_registry.yaml`, `program/backlog/human_action_backlog.yaml` | HUMAN_PARTICIPANT | REQUIRES_HUMAN_PARTICIPANTS; PHYSICAL_PENDING |
| 4 | G4-C2 | Real connectivity conditions | `program/gates/physical_gate_registry.yaml`, NTN/SpectrumX pins | MEASURED | REQUIRES_LOCAL_HARDWARE; PHYSICAL_PENDING |
| 4 | G4-C3 | Long-duration operation | `program/physical/MASTER_EVIDENCE_CAPTURE_SEQUENCE.md` | MEASURED | REQUIRES_LOCAL_HARDWARE; PHYSICAL_PENDING |
| 4 | G4-C4 | Terrestrial and NTN experiments | `ntn-resilience-sim` pin, `program/gates/external_gate_registry.yaml` | MEASURED / EXTERNAL_ACCEPTANCE | REQUIRES_EXTERNAL_PARTNER; PHYSICAL_PENDING |
| 4 | G4-C5 | Accessibility evaluation | `program/backlog/human_action_backlog.yaml` | HUMAN_PARTICIPANT | REQUIRES_HUMAN_PARTICIPANTS |
| 4 | G4-C6 | Local-language evaluation | `program/backlog/human_action_backlog.yaml`, `waike-research-ops` pin | HUMAN_PARTICIPANT | REQUIRES_HUMAN_PARTICIPANTS |
| 4 | G4-C7 | Community governance review | `program/gates/human_action_registry.yaml` | EXTERNAL_ACCEPTANCE | REQUIRES_ETHICS_OR_GOVERNANCE_APPROVAL |
| 4 | G4-C8 | Incident and support exercises | `program/backlog/human_action_backlog.yaml` | HUMAN_PARTICIPANT / PREPARATION_PACKET | REQUIRES_HUMAN_PARTICIPANTS |
| 5 | G5-C1 | Design for manufacture | `program/physical/MASTER_PROCUREMENT_BOM.csv`, `device_designs/*/manufacturing/` | PREPARATION_PACKET / DIGITAL_DESIGN_ARTIFACT | REQUIRES_MANUFACTURER |
| 5 | G5-C2 | Supply-chain audit | `program/physical/MASTER_PROCUREMENT_BOM.csv`, `program/backlog/external_dependency_backlog.yaml` | PREPARATION_PACKET | REQUIRES_EXTERNAL_PARTNER |
| 5 | G5-C3 | Regulatory test candidates | `program/physical/MASTER_TEST_EQUIPMENT_LIST.csv`, `program/gates/external_gate_registry.yaml` | PREPARATION_PACKET | REQUIRES_CERTIFICATION_LAB |
| 5 | G5-C4 | Carrier engagement | `program/backlog/external_dependency_backlog.yaml` | PREPARATION_PACKET | REQUIRES_CARRIER |
| 5 | G5-C5 | Privacy and security review | `program/claims/`, `program/gates/human_action_registry.yaml` | ANALYSIS / EXTERNAL_ACCEPTANCE | REQUIRES_ETHICS_OR_GOVERNANCE_APPROVAL |
| 5 | G5-C6 | Production provisioning | `program/physical/MASTER_BRINGUP_SEQUENCE.md` | PREPARATION_PACKET | REQUIRES_MANUFACTURER |
| 5 | G5-C7 | Packaging and support system | `program/physical/MASTER_PHYSICAL_BUILD_AND_TEST_BOOK.md` | PREPARATION_PACKET | REQUIRES_EXTERNAL_PARTNER |
| 6 | G6-C1 | No unresolved critical safety or security defects | `program/physical/MASTER_ACCEPTANCE_DECISION_BOOK.md`, `program/reports/NONPHYSICAL_REMAINING_BLOCKERS.md` | EXTERNAL_ACCEPTANCE | REQUIRES_EDMUND_ACCEPTANCE |
| 6 | G6-C2 | Signed factory image | `device_designs/*/firmware/`, `program/physical/MASTER_BRINGUP_SEQUENCE.md` | DIGITAL_DESIGN_ARTIFACT (dev) / MEASURED (factory) | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 6 | G6-C3 | Verified update and rollback | `program/physical/MASTER_EVIDENCE_CAPTURE_SEQUENCE.md` | MEASURED | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 6 | G6-C4 | Clean install and recovery | `program/physical/MASTER_BRINGUP_SEQUENCE.md` | MEASURED | REQUIRES_PHYSICAL_PROTOTYPE; PHYSICAL_PENDING |
| 6 | G6-C5 | Complete applications and game paths | game repos + `gate1/contracts/game_core_loop.schema.json` | SOFTWARE_TEST | AUTOMATABLE_AFTER_DEPENDENCY |
| 6 | G6-C6 | Published support lifecycle | `program/backlog/external_dependency_backlog.yaml` | PREPARATION_PACKET | REQUIRES_EXTERNAL_PARTNER |
| 6 | G6-C7 | Pilot evidence accepted | `program/physical/MASTER_ACCEPTANCE_DECISION_BOOK.md` | EXTERNAL_ACCEPTANCE / HUMAN_PARTICIPANT | REQUIRES_EDMUND_ACCEPTANCE; PHYSICAL_PENDING |
| 7 | G7-C1 | Required regional certifications | `program/gates/external_gate_registry.yaml`, `standards/` (when present) | NORMATIVE_CONFORMANCE | REQUIRES_CERTIFICATION_LAB |
| 7 | G7-C2 | Carrier or network acceptance | `program/backlog/external_dependency_backlog.yaml` | EXTERNAL_ACCEPTANCE | REQUIRES_CARRIER |
| 7 | G7-C3 | Production manufacturing | `program/physical/MASTER_PROCUREMENT_BOM.csv`, `device_designs/*/manufacturing/` | EXTERNAL_ACCEPTANCE | REQUIRES_MANUFACTURER |
| 7 | G7-C4 | Support staffing | `program/backlog/human_action_backlog.yaml` | EXTERNAL_ACCEPTANCE | REQUIRES_EXTERNAL_PARTNER |
| 7 | G7-C5 | Fleet operations | `gate3` fleet artifacts, measurement node pin | SOFTWARE_TEST / MEASURED | AUTOMATABLE_AFTER_DEPENDENCY; PHYSICAL_PENDING |
| 7 | G7-C6 | Vulnerability-response process | `program/claims/`, SECURITY docs across locked repos | DIGITAL_DESIGN_ARTIFACT | AUTOMATABLE_NOW |
| 7 | G7-C7 | Repair and replacement inventory | `program/physical/MASTER_PROCUREMENT_BOM.csv` | PREPARATION_PACKET | REQUIRES_EXTERNAL_PARTNER |
| 8 | G8-C1 | Map finalized 3GPP/ITU requirements | `standards/` (planned), `program/gates/gate_definitions.yaml` Gate 8 | ANALYSIS / STANDARDS_MAPPING | REQUIRES_STANDARD_FINALIZATION |
| 8 | G8-C2 | Upgrade compatible components | `standards/`, ecosystem lock pins | ANALYSIS | REQUIRES_STANDARD_FINALIZATION |
| 8 | G8-C3 | Replace non-compliant components | `standards/`, `device_designs/` | ANALYSIS / DIGITAL_DESIGN_ARTIFACT | REQUIRES_STANDARD_FINALIZATION |
| 8 | G8-C4 | Complete formal conformance testing | `standards/`, certification lab packets | NORMATIVE_CONFORMANCE | REQUIRES_CERTIFICATION_LAB |
| 8 | G8-C5 | 6G certification language only after path exists | `program/claims/prohibited_claim_patterns.yaml`, claim firewall | ANALYSIS | REQUIRES_STANDARD_FINALIZATION; GATE_8_PASS forbidden |

## Living status source

Two-axis gate status: `program/nonphysical/gate_nonphysical_status.yaml`  
Criterion baseline: `program/gates/gate_status.yaml`  
Ecosystem pins: `program/repositories/ecosystem_version_lock.yaml`
