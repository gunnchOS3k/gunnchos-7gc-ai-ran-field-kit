# OULU-001 — Table III vs eq.(15) discrepancy resolution

**Packet:** C-PKT-003  
**Status:** `SPEC_DISCREPANCY_DOCUMENTED` (does **not** auto-earn `DIGITAL_REPRODUCTION_PASS`)  
**Policy:** source published parameters win; **do not** invent an aperture / window formula to “fix” Table III.

## Sources consulted (full paper)

| Role | Citation |
|---|---|
| Primary Table I/III + eqs.(15)–(17) | Taghavi, Saarnisaari, Juntti — *Fundamental and Practical Performance Assessment in Monostatic ISAC: From Sub-6GHz to Sub-THz*, 6GNet 2024, DOI [10.1109/6GNet63182.2024.10765635](https://doi.org/10.1109/6GNet63182.2024.10765635), OuluRepo [10024/54707](https://oulurepo.oulu.fi/handle/10024/54707) |
| IEEE / EuCNC cross-record | DOI [10.1109/EuCNC/6GSummit68295.2026.11577293](https://doi.org/10.1109/EuCNC/6GSummit68295.2026.11577293) (IEEE record 11577293) — same monostatic ISAC KPI family; used for venue completeness, not to rewrite Table III |
| Adjacent FR3 Oulu context (NOT Table III source) | Aghaei et al., *FR3 for 6G Networks…*, arXiv [2604.07482](https://arxiv.org/abs/2604.07482) — FR1/FR2/FR3 ray-tracing comparative study; **no** Taghavi Table III numbers |

## What eq.(15) says

Paper §IV.C (OCR-normalized):

\[
\delta R = \frac{c_0}{2 B}
\]

with \(B\) = allocated sensing bandwidth from **Table I**.

## Numerical audit (source params)

| Band | \(f_c\) (GHz) | Table I \(B\) (GHz) | \(c_0/(2B)\) (m) | Table III \(\delta R\) (m) | Rel. err vs Table III |
|---|---:|---:|---:|---:|---:|
| FR1 | 3.5 | 0.1 | 1.499 | 1.49 | ~0.6% |
| FR3 | 7.0 | 0.2 | 0.749 | 0.74 | ~1.3% |
| FR3 | 15.0 | 0.2 | 0.749 | 0.74 | ~1.3% |
| FR2 | 28.0 | 0.4 | 0.375 | **0.49** | **~30.7%** |
| FR2 | 72.0 | 0.4 | 0.375 | **0.49** | **~30.7%** |
| sub-THz | 100.0 | 0.5 | 0.300 | **0.37** | **~23.4%** |

**Conclusion:** FR1/FR3 Table III range rows are consistent with eq.(15) + Table I \(B\). FR2 / sub-THz Table III range rows are **not**. Angular Table III rows remain closer to an empirical \(66.5/N\) fit than to pure eq.(16) co-array \(\arcsin(1/(2N-1))\); that angle gap is separately documented and is **not** repaired by inventing a new aperture identity.

## Resolution rule (C-PKT-003)

1. **Source params win** for citing published KPIs: when quoting “paper Table III”, use the printed Table III numbers.
2. **Analytical verifier** continues to implement eq.(15) with Table I \(B\) exactly — it must not be mutated to force-fit FR2 Table III.
3. **Forbidden:** inventing an effective-bandwidth, window, or aperture fudge so that \(c_0/(2B_{\mathrm{eff}})=0.49\) at 28 GHz and then claiming `DIGITAL_REPRODUCTION_PASS`.
4. **Classification:** remain `REFERENCE_SPEC_INCOMPLETE` for full-table PASS; FR1/FR3 narrative + \(\delta R=c/(2B)\) match stays documented as scoped digital success.
5. SoA / PHYSICAL / OTA / CERTIFIED / CARRIER / EXTERNAL_REPRODUCTION_COMPLETE stay **false**.

## What would earn `DIGITAL_REPRODUCTION_PASS` later

Author errata, clarified \(B_{\mathrm{sense}}\) distinct from Table I \(B\), or released code that defines the Table III FR2 rows — not a unilateral formula rewrite.
