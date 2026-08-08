# ADR-FP-005 — WWAN modem + eSIM baseline

- Status: **ACCEPTED (engineering baseline)**
- Date: 2026-08-08T00:07:41Z

## Decision
- Modem: **Quectel RM520N-GL** (M.2 3052, 5G NR Sub-6, fallback LTE) as primary openly documentable module
- eSIM: consumer eUICC compliant to **GSMA SGP.22 v2.7** architecture — **no compliance claim until testing**
- GNSS: modem-integrated GNSS + optional discrete
- Antennas: 4× cellular main/MIMO + GNSS — placement keep-outs in RF plan

## Forbidden claims
Not 6G certified. IMT-2030 migration via replaceable M.2 modem/RF boundary.
