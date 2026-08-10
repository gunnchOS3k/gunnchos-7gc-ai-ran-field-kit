# gunnchOS3k Product Development Handbook

## Core principles

1. Accepted `main` is product truth.
2. Owner repos create product evidence; the field-kit aggregates it.
3. Digital, physical, human, and external evidence are distinct.
4. High-risk claims require independent verification.
5. Status and evidence level are separate.
6. Depth beats breadth after requirements are complete.
7. Functional correctness and product quality are separate gates.
8. Human evaluation starts before DVT.
9. WIP is capped at three major streams.
10. Broad giant prompts are frozen after Phase XV.
11. Architecture decisions live in ADRs.
12. Class D/E changes require Edmund approval.
13. Physical builds use frozen named configurations.
14. EVT is risk-first, not cosmetically perfect.
15. Risks are ranked by likelihood × impact × late-discovery cost.
16. Supply-chain risk is an engineering requirement.
17. Licensing is a release gate.
18. Agentic AI requires adversarial evaluation.
19. Security gets independent/red-team treatment.
20. NFR targets are centralized before EVT.
21. Competitor capabilities are MUST_MATCH / MUST_EXCEED / NOT_RELEVANT / DIFFERENT_APPROACH.
22. Economics and affordability are release inputs.
23. Each product has a Minimum Lovable Product outcome.
24. Ten Golden Journeys must not regress.
25. S0–S4 severity governs release blocking.
26. Known unknowns are managed intentionally.
27. Field telemetry creates future work.
28. One finite work packet is the normal unit of execution.

## Daily decision rule

Ask:

> What is the highest-risk, highest-user-value, lowest-regret unresolved item that can be advanced now without exceeding WIP?

Then create one bounded work packet.

## Product truth

A green JSON token is not the product.

The product becomes real through:
- independent acceptance;
- target hardware;
- human use;
- external labs/vendors;
- field operation.
