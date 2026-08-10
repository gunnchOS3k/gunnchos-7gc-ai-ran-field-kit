# Cursor Bootstrap Prompt — Permanent Operating Model

This is a ONE-TIME process bootstrap after Phase XV. It is NOT Phase XVI and must not start another broad feature wave.

Workspace:
`/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos`

## Preconditions
Verify accepted main contains current successors of:
- device-os #77
- gunnchAI #30
- hardware #53
- field-kit #55

Verify:
```text
INCOMPLETE_DIGITAL_FRONTIER_GATES = 0
RFQ_PACKAGE_DIGITAL_DEFECTS = 0
READY_TO_SEND_RFQS = true
```

## Install
Copy the provided `gunnchOS3k_Operating_Model` content into:
`program/operating_model/`

Owner repos receive only minimal hooks/mirrors needed for evidence/verifier/Golden Journey integration.

## Required process implementation

1. Add machine-readable `status`, E0–E8 evidence, D0–D8 depth, V0–V3 verification.
2. Create independent verifier workflows for V1 claims; verifier derives tests independently.
3. Install 10 Golden Journeys; run relevant subset on major PRs and full set weekly/pre-freeze.
4. Enforce WIP=3 and max dependent PR chain=3, with Edmund exception record.
5. Install canonical backlog + priority engine.
6. Seed initial post-XV backlog, but do not activate more than 3 workstreams.
7. Install ADR policy + seeded accepted ADRs; Class E without ADR fails governance.
8. Install Class A–E change control; D/E require explicit Edmund approval.
9. Create release configuration system and draft `gunnchOS3k-EVT0-1.0`.
10. Fetch current accepted SHAs before any freeze; do not authorize fabrication.
11. Install risk, known unknowns and supply registers.
12. Require every RED risk to have an owner and next experiment.
13. Install Product Quality Gate and Golden Journey scorecards.
14. Prepare human-study packet; never claim E6 without participants.
15. Install License Release Gate and scan code/models/data/media/dependencies.
16. Add gunnchAI adversarial suite.
17. Add internal independent security/red-team lane; no fake external pentest claim.
18. Install centralized NFR registry; unknown numbers stay `TARGET_TBD`.
19. Install competitive strategy matrix.
20. Install economics model; use only real quotes/known data.
21. Install risk-first EVT philosophy and test plan.
22. Install S0–S4 release severity.
23. Install privacy-minimized field telemetry loop.
24. Set `BROAD_COMPLETION_PHASES_FROZEN=true`.
25. Create `make next-work-packet` or equivalent that reads backlog/risk/unknowns, respects WIP, outputs ONE work packet plus matching verifier packet, and does not automatically execute it.

## Recommended initial ACTIVE set
Only:
- WP-002 Handheld storage headroom
- WP-003 independent Golden Journey verification
- WP-004 RFQ send packet final review

Everything else stays READY/BLOCKED.

## Governance
- draft PRs
- no auto-merge
- Edmund merges
- control plane consumes owner evidence, never manufactures it

## Final report
A accepted baseline
B operating-model files
C owner hooks
D WIP
E backlog top 10
F active 3
G independent verifier
H Golden Journeys
I ADR/change control
J release config
K risk/unknowns
L supply
M licensing
N security/adversarial
O NFR target gaps
P economics
Q human-study readiness
R EVT readiness
S external actions
T PRs/CI/merge order

After bootstrap:
```text
one finite work packet
→ implement
→ independent verify
→ merge
→ accepted-main reproof
→ next packet
```
