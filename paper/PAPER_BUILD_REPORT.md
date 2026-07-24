# Paper Build Report

| Field | Value |
|-------|-------|
| Status | **success** |
| Built at | 2026-07-24 15:07:47 UTC |
| Method | tectonic |
| Tool | Tectonic 0.16.9 |
| Output | `paper/main.pdf` |
| Page count | 4 |
| PDF SHA-256 | `c17726adc921b4c8d3486c8b1d6f5bed6947dac01d9b126cbe1d0e70f062f1d6` |

## Validation

- Title and authorship preserved (Edmund Gunn Jr.; 7GC Research Product Spine)
- `RESULTS_PENDING_AUTHENTIC_GATE3_DATA` preserved in results and manuscript
- No invented submission venue, repository DOI, p-values, or effect sizes
- All `\cite{...}` keys resolve in `references.bib`

## Tooling pins

| Tool | Pin |
|------|-----|
| Tectonic | 0.16.9 (GitHub release binary → `.tools/`) |
| Docker fallback | texlive/texlive:TL2024-historic (digest-pinned) |

## Fallback (manual)

1. **Tectonic (recommended):** `bash scripts/build_paper.sh` downloads pinned Tectonic into `.tools/` when needed.
2. **Docker:** `docker pull texlive/texlive:TL2024-historic (digest-pinned)` then re-run `make paper`.
3. **Local TeX Live / MacTeX:** `cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex`

## TeX fixes applied this run

- None

See also `paper/PAPER_BUILD_MANIFEST.json` and `paper/PAPER_CHECKSUMS.sha256`.
