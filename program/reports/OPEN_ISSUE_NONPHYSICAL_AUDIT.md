# Open Issue Nonphysical Audit

Audited: `2026-08-07T22:25:00Z`  
Method: `gh issue list --state open` across canonical program repos  
Scope: issues still open on GitHub; classification is nonphysical-control-plane triage, not issue closure.

## Classes

| Class | Meaning |
|---|---|
| DONE | Work described appears already present; issue is a close-candidate (still open on GitHub) |
| NONPHYSICAL_IMPLEMENTABLE_NOW | Software/docs/schemas/sims can proceed under physical freeze |
| PHYSICAL_ONLY | Needs hardware, fab, lab instruments, or measured capture |
| HUMAN_ONLY | Needs Edmund/mentor/participant/reviewer action |
| EXTERNAL_ONLY | Needs partner, carrier, lab, manufacturer, contest org, or outside system |
| OBSOLETE | Superseded by newer epic/issue or program direction |
| DUPLICATE | Same ask tracked elsewhere (often cross-repo WAIKE template) |

## Summary counts

| Repo | Open | Dominant classes |
|---|---:|---|
| gunnchos-7gc-ai-ran-field-kit | 0 | — |
| gunnchos-device-os | 0 | — |
| gunnchos-hardware-industrial-design | 0 | — |
| EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon | 0 | — |
| beatlink-party / archive / pedestrian / anime | 0 | — |
| gunnchos-emergent-service-intent-protocols | 0 | — |
| gunnchos-gpu-nr-baseband-platform | 0 | — |
| gunnchos-research-portal | 1 | DUPLICATE |
| gunnchAI3k | 12 | NONPHYSICAL_IMPLEMENTABLE_NOW / HUMAN_ONLY |
| edge-io-measurement-node | 8 | NONPHYSICAL_IMPLEMENTABLE_NOW / DUPLICATE |
| 7gc-digital-twin | 10 | NONPHYSICAL_IMPLEMENTABLE_NOW / DUPLICATE |
| ntn-resilience-sim | 10 | NONPHYSICAL_IMPLEMENTABLE_NOW / DUPLICATE |
| readygary-6g-beam-selection | 11 | NONPHYSICAL_IMPLEMENTABLE_NOW / DUPLICATE |
| spectrumx-ai-ran-gary | 47 | NONPHYSICAL_IMPLEMENTABLE_NOW / HUMAN_ONLY / EXTERNAL_ONLY / DUPLICATE / OBSOLETE |
| waike-research-ops | 26 | NONPHYSICAL_IMPLEMENTABLE_NOW / DUPLICATE |
| **Total open audited** | **125** | |

## Cross-repo duplicate pattern

Identical open issue title across multiple repos:

> Add WAIKE_INTEGRATION.md tutor cards and student tasks

| Repo | Issue | Class |
|---|---|---|
| gunnchos-research-portal | #2 | DUPLICATE (canonicalize in waike-research-ops) |
| edge-io-measurement-node | #9 | DUPLICATE |
| 7gc-digital-twin | #11 | DUPLICATE |
| ntn-resilience-sim | #11 | DUPLICATE |
| readygary-6g-beam-selection | #13 | DUPLICATE |
| spectrumx-ai-ran-gary | #84 | DUPLICATE |

Treat `waike-research-ops` as the home for the shared template; sibling issues become thin adoption checklists after the template lands.

## gunnchos-research-portal (1)

| Issue | Title | Class | Notes |
|---|---|---|---|
| #2 | Add WAIKE_INTEGRATION.md tutor cards and student tasks | DUPLICATE | See cross-repo WAIKE pattern |

## gunnchAI3k (12)

| Issue | Title | Class | Notes |
|---|---|---|---|
| #6 | Jaelysa onboarding profile/setup/learning goals | NONPHYSICAL_IMPLEMENTABLE_NOW | Docs/onboarding |
| #7 | Beginner model-training walkthrough notebook | NONPHYSICAL_IMPLEMENTABLE_NOW | Notebook/docs |
| #8 | AI reliability checklist + failure-case catalog | NONPHYSICAL_IMPLEMENTABLE_NOW | Docs/tests catalog |
| #9 | AI assistant threat model | NONPHYSICAL_IMPLEMENTABLE_NOW | Analysis artifact |
| #10 | Prompt-injection test case library | NONPHYSICAL_IMPLEMENTABLE_NOW | Test harness |
| #11 | Audit secrets/env/safe setup docs | NONPHYSICAL_IMPLEMENTABLE_NOW | Docs/security hygiene (no secret printing) |
| #12 | Model card / AI system card templates | NONPHYSICAL_IMPLEMENTABLE_NOW | Templates |
| #13 | AI security and reliability test plan | NONPHYSICAL_IMPLEMENTABLE_NOW | Test plan |
| #14 | Jaelysa AI security case study | NONPHYSICAL_IMPLEMENTABLE_NOW | Portfolio docs |
| #15 | Prototype safe-response evaluator | NONPHYSICAL_IMPLEMENTABLE_NOW | Stretch software |
| #16 | Weekly check-in template + sprint tracker | HUMAN_ONLY | Mentor-review labeled; needs human cadence |
| #17 | Career-fair readiness package final review | HUMAN_ONLY | Mentor/final review gate |

## edge-io-measurement-node (8)

| Issue | Title | Class | Notes |
|---|---|---|---|
| #1 | Define telemetry schema | NONPHYSICAL_IMPLEMENTABLE_NOW | Schema/contract |
| #2 | Create synthetic device emulator | NONPHYSICAL_IMPLEMENTABLE_NOW | Emulator (not measured PASS) |
| #3 | Latency/jitter/packet-loss probes | NONPHYSICAL_IMPLEMENTABLE_NOW | Software probes; real RF remains PHYSICAL_ONLY later |
| #4 | RSSI placeholder contract | NONPHYSICAL_IMPLEMENTABLE_NOW | Placeholder contract only |
| #5 | Offline AI inference benchmark contract | NONPHYSICAL_IMPLEMENTABLE_NOW | Contract/harness |
| #6 | Privacy-preserving telemetry policy | NONPHYSICAL_IMPLEMENTABLE_NOW | Policy docs |
| #7 | Integration export to 7GC digital twin | NONPHYSICAL_IMPLEMENTABLE_NOW | Integration code/docs |
| #9 | WAIKE_INTEGRATION.md tutor cards | DUPLICATE | Cross-repo WAIKE |

## 7gc-digital-twin (10)

| Issue | Title | Class | Notes |
|---|---|---|---|
| #1 | Define shared 7GC site schema | NONPHYSICAL_IMPLEMENTABLE_NOW | Schema |
| #2 | Implement Gary site profile v1 | NONPHYSICAL_IMPLEMENTABLE_NOW | Config/data |
| #3 | Ghana/Guyana/Germany site profiles | NONPHYSICAL_IMPLEMENTABLE_NOW | Config/data |
| #4 | Gaza remote-first humanitarian scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario (privacy-aware) |
| #5 | Graham Land polar research node scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario |
| #6 | Fairness/energy/latency/spectral metrics | NONPHYSICAL_IMPLEMENTABLE_NOW | Metrics notebooks |
| #7 | Streamlit dashboard | NONPHYSICAL_IMPLEMENTABLE_NOW | App |
| #8 | Professor demo script | NONPHYSICAL_IMPLEMENTABLE_NOW | Demo docs |
| #9 | City official demo script | NONPHYSICAL_IMPLEMENTABLE_NOW | Demo docs |
| #11 | WAIKE_INTEGRATION.md tutor cards | DUPLICATE | Cross-repo WAIKE |

## ntn-resilience-sim (10)

| Issue | Title | Class | Notes |
|---|---|---|---|
| #1 | Define scenario schema | NONPHYSICAL_IMPLEMENTABLE_NOW | Schema |
| #2 | Build outage model stub | NONPHYSICAL_IMPLEMENTABLE_NOW | Sim stub |
| #3 | Gary emergency connectivity scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario |
| #4 | Ghana rural fallback scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario |
| #5 | Guyana flood resilience scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario |
| #6 | Gaza remote-first scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario |
| #7 | Graham Land polar scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario |
| #8 | Simple link budget stub | NONPHYSICAL_IMPLEMENTABLE_NOW | Model stub |
| #9 | Resilience metrics report | NONPHYSICAL_IMPLEMENTABLE_NOW | Report tooling |
| #11 | WAIKE_INTEGRATION.md tutor cards | DUPLICATE | Cross-repo WAIKE |

## readygary-6g-beam-selection (11)

| Issue | Title | Class | Notes |
|---|---|---|---|
| #2 | Top-1/3/5 beam accuracy reporting | NONPHYSICAL_IMPLEMENTABLE_NOW | Metrics |
| #3 | dB loss vs oracle metric | NONPHYSICAL_IMPLEMENTABLE_NOW | Metrics |
| #4 | Spectral efficiency loss vs oracle | NONPHYSICAL_IMPLEMENTABLE_NOW | Metrics |
| #5 | CPU/GPU/ARM inference timing benchmark | NONPHYSICAL_IMPLEMENTABLE_NOW | Host benchmark (not field PASS) |
| #6 | Mobility scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario |
| #7 | Blockage scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario |
| #8 | Handover scenario | NONPHYSICAL_IMPLEMENTABLE_NOW | Scenario |
| #9 | Export ONNX model | NONPHYSICAL_IMPLEMENTABLE_NOW | Export |
| #10 | IEEE-style paper draft | NONPHYSICAL_IMPLEMENTABLE_NOW | Writing |
| #11 | Connect beam model to 7GC site configs | NONPHYSICAL_IMPLEMENTABLE_NOW | Integration |
| #13 | WAIKE_INTEGRATION.md tutor cards | DUPLICATE | Cross-repo WAIKE |

## spectrumx-ai-ran-gary (47)

### Portfolio / micro-twin track

| Issue | Title | Class | Notes |
|---|---|---|---|
| #74 | Convert Gary Micro-Twin export to shared 7GC site schema | NONPHYSICAL_IMPLEMENTABLE_NOW | Schema alignment with twin |
| #75 | Policy interface for beam/power/RB selection | NONPHYSICAL_IMPLEMENTABLE_NOW | API placeholder |
| #76 | Export synthetic IQ metadata contract | NONPHYSICAL_IMPLEMENTABLE_NOW | Contract (synthetic ≠ measured) |
| #77 | Fairness metric notebook | NONPHYSICAL_IMPLEMENTABLE_NOW | Notebook |
| #78 | Energy-per-bit metric notebook | NONPHYSICAL_IMPLEMENTABLE_NOW | Notebook |
| #79 | Professor demo mode | NONPHYSICAL_IMPLEMENTABLE_NOW | Demo |
| #80 | City/community demo mode | NONPHYSICAL_IMPLEMENTABLE_NOW | Demo |
| #81 | Integration notes for edge-io-measurement-node | NONPHYSICAL_IMPLEMENTABLE_NOW | Docs |
| #82 | Integration notes for ntn-resilience-sim | NONPHYSICAL_IMPLEMENTABLE_NOW | Docs |
| #84 | WAIKE_INTEGRATION.md tutor cards | DUPLICATE | Cross-repo WAIKE |
| #40 | EPIC 4: Portfolio Extension (Gary Micro-Twin) | NONPHYSICAL_IMPLEMENTABLE_NOW | Epic umbrella |
| #39 | EPIC 3: Reproducibility + Submission | NONPHYSICAL_IMPLEMENTABLE_NOW / EXTERNAL_ONLY | Bundle digital; SpX submit external |
| #38 | EPIC 2: Visualization + Demo | NONPHYSICAL_IMPLEMENTABLE_NOW | Viz |
| #37 | EPIC 1: Competition Core Detection | NONPHYSICAL_IMPLEMENTABLE_NOW | Core ML track |

### Core detection / MLOps backlog

| Issue | Title | Class | Notes |
|---|---|---|---|
| #3 | One-command baseline stub | NONPHYSICAL_IMPLEMENTABLE_NOW | Eval harness |
| #4 | Metrics + file-level split policy | NONPHYSICAL_IMPLEMENTABLE_NOW | Eval policy |
| #5 | EDA notebook sanitized for sharing | NONPHYSICAL_IMPLEMENTABLE_NOW | Notebook |
| #6 | Dataset inventory + dataset_map.md | NONPHYSICAL_IMPLEMENTABLE_NOW | Docs |
| #7 | Automated dataset download script | NONPHYSICAL_IMPLEMENTABLE_NOW / EXTERNAL_ONLY | Script local; dataset host external |
| #8 | Repo skeleton + coding standards | OBSOLETE / DONE candidate | Repo already structured; verify then close |
| #9 | Create Asana project fields + sections | EXTERNAL_ONLY | Outside Asana workspace |
| #10 | Rotate SDS token + move to .env + gitignore | HUMAN_ONLY | Secret rotation; do not print secrets |
| #11 | Robustness checklist for unseen data | NONPHYSICAL_IMPLEMENTABLE_NOW | Checklist |
| #12 | Create submission bundle | NONPHYSICAL_IMPLEMENTABLE_NOW | Zip/bundle |
| #13 | Submit to SpX-DAC | EXTERNAL_ONLY | Contest submission |
| #14 | Final review meeting + freeze decision | HUMAN_ONLY | Meeting/decision |
| #15 | Final QA run (fresh machine simulation) | NONPHYSICAL_IMPLEMENTABLE_NOW | QA procedure |
| #16 | Final narrative + resume bullets | NONPHYSICAL_IMPLEMENTABLE_NOW / HUMAN_ONLY | Draft digital; resume voice human |
| #17 | Final figures pack | NONPHYSICAL_IMPLEMENTABLE_NOW | Figures |
| #18 | Reproducibility hardening | NONPHYSICAL_IMPLEMENTABLE_NOW | MLOps |
| #19 | Low-level design doc draft | NONPHYSICAL_IMPLEMENTABLE_NOW | Docs |
| #20 | Visualization dashboard v2 | NONPHYSICAL_IMPLEMENTABLE_NOW | Dashboard |
| #21 | Model compression / efficiency pass | NONPHYSICAL_IMPLEMENTABLE_NOW | ML |
| #22 | Inference benchmark harness | NONPHYSICAL_IMPLEMENTABLE_NOW | Harness |
| #23 | Ablation table v1 | NONPHYSICAL_IMPLEMENTABLE_NOW | Eval |
| #24 | Hybrid ensemble experiment | NONPHYSICAL_IMPLEMENTABLE_NOW | Experiment |
| #25 | Calibration layer v1 | NONPHYSICAL_IMPLEMENTABLE_NOW | ML |
| #26 | Anomaly detector v1 | NONPHYSICAL_IMPLEMENTABLE_NOW | ML |
| #27 | Semi-supervised pipeline v1 | NONPHYSICAL_IMPLEMENTABLE_NOW | ML |
| #28 | Decision log: representation locked | NONPHYSICAL_IMPLEMENTABLE_NOW / HUMAN_ONLY | Log digital; lock decision human |
| #29 | Sprint 1 summary writeup | NONPHYSICAL_IMPLEMENTABLE_NOW | Docs |
| #30 | Baseline comparison mini-dashboard v1 | NONPHYSICAL_IMPLEMENTABLE_NOW | Dashboard |
| #31 | Error analysis v1 | NONPHYSICAL_IMPLEMENTABLE_NOW | Analysis |
| #32 | Evaluation harness v1 | NONPHYSICAL_IMPLEMENTABLE_NOW | Harness |
| #33 | Baseline 3: PSD + Logistic Regression | NONPHYSICAL_IMPLEMENTABLE_NOW | Baseline |
| #34 | Baseline 2: Spectral flatness detector | NONPHYSICAL_IMPLEMENTABLE_NOW | Baseline |
| #35 | Baseline 1: Energy detector | NONPHYSICAL_IMPLEMENTABLE_NOW | Baseline |

## waike-research-ops (26)

| Issue | Title | Class | Notes |
|---|---|---|---|
| #1 | Define WAIKE course release template | NONPHYSICAL_IMPLEMENTABLE_NOW | Canonical template home |
| #2 | Define research apprenticeship tracks | NONPHYSICAL_IMPLEMENTABLE_NOW | Curriculum |
| #3 | Add FOI rubric | NONPHYSICAL_IMPLEMENTABLE_NOW | Rubric |
| #4 | Add learning outcomes matrix | NONPHYSICAL_IMPLEMENTABLE_NOW | Matrix |
| #5 | Fair-chance/youth-safety policy draft | NONPHYSICAL_IMPLEMENTABLE_NOW / HUMAN_ONLY | Draft digital; policy acceptance human |
| #6 | Global campus ops playbook | NONPHYSICAL_IMPLEMENTABLE_NOW | Ops docs |
| #7 | Project story card template | NONPHYSICAL_IMPLEMENTABLE_NOW | Template |
| #10 | Founder education to curriculum map | NONPHYSICAL_IMPLEMENTABLE_NOW | Mapping |
| #11 | Build WAIKE 0-to-7 levels | NONPHYSICAL_IMPLEMENTABLE_NOW | Curriculum |
| #12 | Beyond the Founder Standard | NONPHYSICAL_IMPLEMENTABLE_NOW | Standard draft |
| #13 | gunnchAI3k tutor requirements | NONPHYSICAL_IMPLEMENTABLE_NOW | Requirements |
| #14 | WAIKE-to-gunnchAI3k API contract | NONPHYSICAL_IMPLEMENTABLE_NOW | API placeholder in ecosystem lock |
| #15 | Map WAIKE to CS2023 | NONPHYSICAL_IMPLEMENTABLE_NOW | Standards mapping (current-state) |
| #16 | Map WAIKE to ABET outcomes | NONPHYSICAL_IMPLEMENTABLE_NOW | Mapping |
| #17 | Map cybersecurity to NIST NICE | NONPHYSICAL_IMPLEMENTABLE_NOW | Mapping |
| #18 | Map digital skills to SFIA 9 | NONPHYSICAL_IMPLEMENTABLE_NOW | Mapping |
| #19 | Map software engineering to SWEBOK | NONPHYSICAL_IMPLEMENTABLE_NOW | Mapping |
| #20 | Map AI track to NIST AI RMF | NONPHYSICAL_IMPLEMENTABLE_NOW | Mapping |
| #21 | Map IT track to CompTIA A+ | NONPHYSICAL_IMPLEMENTABLE_NOW | Mapping |
| #22 | Map networking track to CCNA | NONPHYSICAL_IMPLEMENTABLE_NOW | Mapping |
| #23 | Map cyber track to ISC2 CC/Security+ | NONPHYSICAL_IMPLEMENTABLE_NOW | Mapping |
| #24 | Build WAIKE capstone library | NONPHYSICAL_IMPLEMENTABLE_NOW | Content |
| #25 | Build instructor training model | NONPHYSICAL_IMPLEMENTABLE_NOW | Content |
| #26 | Build student portfolio requirements | NONPHYSICAL_IMPLEMENTABLE_NOW | Requirements |
| #27 | Multilingual localization plan | NONPHYSICAL_IMPLEMENTABLE_NOW | Plan (human review later) |
| #28 | Build WAIKE evaluation dashboard | NONPHYSICAL_IMPLEMENTABLE_NOW | Dashboard |

## PHYSICAL_ONLY findings

No open issues in the audited set are purely `PHYSICAL_ONLY`. Physical closure for Gates 1–8 remains tracked by control-plane registries (`program/gates/physical_gate_registry.yaml`, `program/physical/*`) rather than GitHub issues.

## Actions for nonphysical totality

1. Prefer implementing `NONPHYSICAL_IMPLEMENTABLE_NOW` issues without claiming gate PASS.
2. Collapse WAIKE `DUPLICATE` issues to a single template in `waike-research-ops`, then thin per-repo adoption issues.
3. Route `HUMAN_ONLY` / `EXTERNAL_ONLY` into `program/backlog/human_action_backlog.yaml` and `program/backlog/external_dependency_backlog.yaml`.
4. Do not close issues from this audit automatically; owners confirm DONE/OBSOLETE before close.
