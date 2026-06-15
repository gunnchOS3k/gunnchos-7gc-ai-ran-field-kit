# Field Measurement Protocol

Canonical field steps live in the edge component repo:

**[edge-io-measurement-node/docs/FIELD_TEST_PROTOCOL.md](https://github.com/gunnchOS3k/edge-io-measurement-node/blob/main/docs/FIELD_TEST_PROTOCOL.md)**

## Summary

1. Opt-in consent (`consent_flag=true`)
2. Waypoint labels (no raw GPS in public export)
3. Repeated probe runs: latency, jitter, loss, RSSI (if available), device status
4. Schema validation before CSV export
5. Aggregated reporting only
6. SDR: receive-only if used — no transmission

## Evidence status

Field measurements are **planned** for conference claims beyond synthetic examples unless a validated campaign artifact is published.
