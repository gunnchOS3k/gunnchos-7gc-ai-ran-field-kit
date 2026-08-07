# Conference → Requirement Traceability

Updated: 2026-08-08 UTC  
Signals are inputs, not standards. No marketing claims of carrier access.

## MWC / GSMA 2026 → integrations

| Signal | Requirement | Integration |
|---|---|---|
| Open Gateway / CAMARA scaling | G3-C3 NetworkCapabilityProvider | CAMARA UNAVAILABLE/SIMULATED/SANDBOX/REAL_OPERATOR modes |
| Interoperable app↔network APIs | connectivity insights / edge discovery | optional adapters; no REAL_OPERATOR without credentials |

## Brooklyn AI-Native 6G → research

| Signal | Requirement | Integration |
|---|---|---|
| AI supercycle / AI-native nets | AI-assisted network policy experiment | research experiment + OTel `gunnchos.ai.*` |
| Energy efficiency | energy-aware network selection | ConnectivityManager preference scoring |
| Network digital twins | twin comparison harness | Sionna + fixture twin compare |
| NTN integration | abstracted NTN handoff sim | existing NTN_ABSTRACTED claim boundary |
| ISAC readiness | research-lane interface contract | ISAC readiness schema only — no hardware claim |

## GDC 2026 → game engineering

| Signal | Requirement | Integration |
|---|---|---|
| Shipping-quality evidence | G2-C6 product quality contract | `product_quality_contract.yaml` |
| Networking / live service | authoritative state + reconnect | Beat Link room/state validation |
| Anti-cheat | score validation, audience anti-grief, save integrity | trust boundaries (no kernel anti-cheat) |
| Accessibility tracks | WCAG/GAG aligned tests | per-game accessibility suites |

## Accessibility signals → validation

| Signal | Validation |
|---|---|
| Keyboard operability / concurrent input | menu operable with every gameplay input class |
| Same-input UI | menus via gameplay input method |
| Target sizing | touch/device profiles |
| Focus visibility / remapping / UI scale | accessibility options + tests |
| Color-independent state | important state not color-only |
