# Definition of Maintainable — gunnchOS3k

A repository is maintainable for this baseline when a competent engineer can, within about five minutes:

1. Identify the product entrypoint(s)
2. Separate production code from proof/evidence/wave harnesses
3. Find the tests that exercise a chosen production module
4. Trust that those tests would fail if the production behavior were meaningfully broken
5. Locate ownership boundaries (what this repo is / is not)

## Signals we measure
- Production/proof path classification clarity
- Proof-independence under temporary proof-strip
- Anti-test-theater static scan (S0–S3)
- Runtime-path authenticity
- Mutation-resistance sampling (temp worktrees only)
- Complexity hotspots
- Orphan/dead-code candidates
- Fixture honesty
- Documentation / five-minute maps
- Architecture diagrams that match accepted main

## What “done” does *not* mean
- Green CI alone
- High line coverage alone
- Presence of RESULT/ACCEPTANCE JSON alone
- Wave duplicate trees that shadow canonical modules
