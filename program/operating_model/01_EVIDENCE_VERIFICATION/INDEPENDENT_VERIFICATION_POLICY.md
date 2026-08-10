# Independent Verification Policy

## Classes

- V0: self-test sufficient
- V1: independent digital verifier required
- V2: independent physical verifier required
- V3: external authority required

V1 applies at minimum to:
- security boundaries
- update/recovery
- identity/user isolation
- AI privacy/memory
- saves
- continuity
- Ring targeting
- connectivity
- package distribution
- MDM
- manufacturing/RFQ integrity

## Independence rule

The verifier receives the requirement and acceptance contract and independently derives tests before studying implementer-authored tests.

## Required V1 evidence

```text
IMPLEMENTATION_EVIDENCE
+ IMPLEMENTER_TESTS
+ INDEPENDENT_ACCEPTANCE_PLAN
+ INDEPENDENT_ACCEPTANCE_RESULTS
+ ACCEPTED_MAIN_SHA
```

Verifier failure opens a defect even if implementer CI is green.
