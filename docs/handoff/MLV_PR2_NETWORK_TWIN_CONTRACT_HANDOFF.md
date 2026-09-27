# Handoff — stack Network Twin extension on live 3k MLV PR #2

This document is the contract consumer handoff for the next 3k MLV agent.

Do not infer schemas. Use the files listed here.

## Live MLV base (do not mutate in the backend lane)

```text
3k MLV PR #2
branch: world/home-7gc-campus-gallery-v2
head: 5ce416d25f7821ee5506be1a60fd30315372956c
base: revival/gunnchos-world-workspace-v1 @ 5e99c64673557efe7cbdfbbfb4d4ebcdcabfaab7
url: https://github.com/gunnchOS3k/3k-mlv/pull/2
```

Current source-version identifier (not a permanent global constant):

```text
source_manifest_sha256 = 520cbba99541b1505ebba899a2f34bfa905eadd7af8f5b5e8fa050c884067be1
```

## Canonical schemas (field-kit)

- `contracts/campus_design_bundle.v1.schema.json`
- `contracts/campus_optimization_result.v1.schema.json`
- `contracts/twin_calibration_bundle.v1.schema.json`
- `contracts/ran_actuation_request.v1.schema.json`
- `contracts/ran_actuation_receipt.v1.schema.json`
- `contracts/campus_measurement_mapping.v1.schema.json`

Existing V1 contracts are unchanged:

- `twin_state_bundle.v1`
- `airan_decision_bundle.v1`
- `edge_measurement_batch.v1`
- `measurement_session_context.v1`
- `resilience_decision_bundle.v1`
- `integrated_run_manifest.v1`

## TS-compatible definitions

- `contracts/ts/closed_loop_v2.ts`

## Canonical fixtures

- `fixtures/valid/campus_design_bundle.valid.json`
- `fixtures/valid/campus_optimization_result.valid.json`
- `fixtures/valid/twin_calibration_bundle.valid.json`
- `fixtures/valid/ran_actuation_request.valid.json`
- `fixtures/valid/ran_actuation_receipt.valid.json`
- `fixtures/valid/campus_measurement_mapping.valid.json`
- seven-campus set: `fixtures/closed_loop_v2/<site>.*.json`
- hashes: `artifacts/closed_loop_v2/FIXTURE_HASHES.json`

## Required zone reference fields

Every network zone must include:

```text
campus_slug
phase
campus_requirement_id
digital_object
digital_route
geometry_fidelity
source_manifest_sha256
```

Representative current requirement IDs:

```text
GARY.FULL.HARDWARE_REPAIR_LAB
GHANA.FULL.MENTOR_WORKSPACE
GUYANA.FULL.CLIMATE_GIS_STUDIO
GEELONG.FULL.DESIGN_BUILD_STUDIO
GERMANY.FULL.INDUSTRY40_TWIN_LAB
GAZA.RECOVERY.OFFLINE_LEARNING_STUDIO
GRAHAM.FULL.NTN_LAB
```

Do not duplicate the 473-room catalog. Consume a campus design export from MLV later.

## Geometry and control truth

Campus V2 geometry is `AUTHORED_PLANNING_LAYOUT`.

3k MLV may visualize / propose / compare. It must not:

- hold RAN credentials
- call E2
- control srsRAN / OAI
- transmit RF commands

`REAL_ACTUATION_ENABLED=false` by default. No browser-direct actuation path.

## Next MLV action

Authorized only after live field-kit PR #120 exact-head CI is green:

```text
NEXT_7GC_AIRAN_ACTION=RUN_PHASE2_MLV_NETWORK_TWIN_ON_LIVE_PR2
```

Use playbook:

`CURSOR_PHASE2_3K_MLV_AIRAN_NETWORK_TWIN_ON_PR2.md`

This file cannot contain the SHA of the commit that adds it. Consume the live PR #120 tip from GitHub, not an embedded self-hash.

```text
pr_branch: integration/7gc-campus-airan-closed-loop-v2
implementation_commit: 93614673e7d57213f34df07f46c1fc233c6e3515
handoff_generated_from_commit: 93614673e7d57213f34df07f46c1fc233c6e3515
live_head_at_report_time: recorded in PR #120 body after push
```

Backend draft PR refs (siblings unchanged):

```text
field-kit     https://github.com/gunnchOS3k/gunnchos-7gc-ai-ran-field-kit/pull/120
              consume live PR tip (implementation 93614673e7d57213f34df07f46c1fc233c6e3515)

7gc-digital-twin  https://github.com/gunnchOS3k/7gc-digital-twin/pull/33
              1d3c159ed942bb499a83af0c4e1533bf439a5970

spectrumx-ai-ran-gary  https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/pull/104
              bffa5161de5b8f3118e89f210f43f375e6cde717

edge-io-measurement-node  https://github.com/gunnchOS3k/edge-io-measurement-node/pull/41
              1af382b489732d4dfa745f67eef9ee61ec1ba9a4

WAIKE PR #25
              f0176c2c45c1c366ad22f46407e6c55c3c5f3e8e

3k MLV PR #2
              5ce416d25f7821ee5506be1a60fd30315372956c
```

Also recorded in:

`artifacts/integration/7GC_AIRAN_CLOSED_LOOP_V2_MANIFEST.json`
