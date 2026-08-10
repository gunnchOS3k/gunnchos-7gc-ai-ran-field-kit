# Priority Engine

Recommended score:

```text
priority =
(severity_weight + risk_exposure + late_discovery_cost +
 unblock_value + user_value + external_lead_time + uncertainty_reduction)
 / estimated_effort
```

Numerator factors 0–5 except severity:
S0=10, S1=8, S2=5, S3=2, S4=1.
Effort 1–8.

S0 and blocking S1 preempt ordinary ranking.

Tie breakers:
1. earlier physical learning
2. external lead time
3. dependency unblock
4. smaller bounded packet
