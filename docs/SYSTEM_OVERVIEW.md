# System Overview

## Mission

Deliver an IEEE-style, reproducible research artifact for **gunnchos 7GC Field Console** — a **phone-first** toolkit for:

1. **AI-assisted O-RAN-style control experiments** (synthetic-first)
2. **Exploratory field measurements** (opt-in, privacy-preserving)
3. **Digital-equity context** (Gary / NWI anchor)

## Architecture

```text
                    ┌─────────────────────────────────────┐
                    │  gunnchos-7gc-ai-ran-field-kit      │
                    │  (umbrella docs, citation, CI)      │
                    └──────────────┬──────────────────────┘
           ┌───────────────────────┼───────────────────────┐
           v                       v                       v
 spectrumx-ai-ran-gary    edge-io-measurement-node   digital-equity-pilot
 (policy + twin stubs)    (telemetry + probes)        (consent ops, planned)
```

## Safe wording (required)

Use: **6G-aligned**, **IMT-2030-aligned**, **AI-assisted O-RAN-style control experiment**, **phone-first field console**, **exploratory field measurements**, **receive-only SDR observation**.

Avoid claiming: carrier-grade AI-RAN, deployable 6G, certified hardware, citywide impact, unauthorized RF transmission.

## Evidence tiers

1. **Smoke** — CI executes
2. **Synthetic reproducible** — scripts + CSV/figures
3. **Field validated** — planned
4. **Operational RAN** — not claimed

## Cross-links

- AI-RAN eval: [spectrumx-ai-ran-gary/docs/EVAL_PROTOCOL.md](https://github.com/gunnchOS3k/spectrumx-ai-ran-gary/blob/main/docs/EVAL_PROTOCOL.md)
- Telemetry: [edge-io-measurement-node/docs/TELEMETRY_SCHEMA.md](https://github.com/gunnchOS3k/edge-io-measurement-node/blob/main/docs/TELEMETRY_SCHEMA.md)
