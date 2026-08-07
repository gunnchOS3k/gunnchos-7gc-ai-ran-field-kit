# License and IP Boundary Report

Updated: 2026-08-08 UTC  
**Not legal advice / not legal certification.**

## Firewall rules (machine-enforceable)

See `program/industry_adoption/license_boundaries.yaml`.

| Family | Policy |
|---|---|
| Apache / MIT / BSD | May integrate subject to notices / normal review |
| GPLv2 | External simulator/test boundary unless deliberate product licensing decision |
| AGPLv3 | Standalone external service/test tool unless deliberate compliance decision |
| OAI CSSL | Research/test allowed per license; commercial Essential Patent → FRAND/legal review |
| Standards specs | Reference IDs/requirements; do not bulk-copy normative text |

## Flagged review points

1. **5G-LENA / ns-3 (GPL-2.0)** — must remain out-of-process; product binary must not link.  
2. **Open5GS (AGPL-3.0)** — container/process only; no embed.  
3. **Grafana OSS (AGPL-3.0)** — standalone observability backend only.  
4. **OAI CSSL** — research adapters OK; commercial EP usage requires human legal/FRAND review.  
5. **Catalogue of Life / GBIF / Smithsonian** — preserve per-dataset/record license + citation; verify rights before media use.  

## Automation

`scripts/validate_industry_license_boundaries.py` fails CI on GPL/AGPL product-path contamination and missing provenance for adopted adapters.


## Post-merge re-verification (2026-08-07T23:45:00Z)

- GPL (5G-LENA): external/test-only — PASS
- AGPL (Open5GS/Grafana): standalone/test-only — PASS
- OAI CSSL: research/test boundary — PASS
- Apache/MIT/BSD adapters preserve notices — PASS
- CC-BY CoL/GBIF provenance required — PASS
- No bulk standards text — PASS
- `scripts/validate_industry_license_boundaries.py` — run on this branch
