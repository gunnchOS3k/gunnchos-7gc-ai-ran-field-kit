# Workload Protocols (300 s)

## learn
Purpose: continuous reading/learning continuity under connectivity stress.
Actions: open learning workload endpoint; request cadence every 5 s; payload small HTML/JSON.
Success: session completes 300 s with samples ≥ 50; unavailable metrics explicit nulls.

## create
Purpose: content-creation continuity.
Actions: periodic upload/create requests every 5–10 s; larger payload.
Success: same duration/sample rules; record degraded completion flags.

## sense
Purpose: sensing/telemetry continuity.
Actions: periodic sense posts every 5 s; small JSON.
Success: same duration/sample rules.

All workloads: timeouts documented in Edge-IO sampler; no private cloud required for public reproduction path when using local/fixture endpoints.
