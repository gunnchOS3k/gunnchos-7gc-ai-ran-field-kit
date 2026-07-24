# Paper Build Report

| Field | Value |
|-------|-------|
| Status | **success** |
| Built at | 2026-07-24 15:59:54 UTC |
| Method | tectonic |
| Tool | Tectonic 0.16.9 |
| Output | `paper/main.pdf` |
| Page count | 7 (required 6--8) |
| PDF SHA-256 | `252aa8467b2f37fad7f4f5b5d4381adee27590ddfe857e1f8ea25ece0851e836` |
| SOURCE_DATE_EPOCH | `0` (`TZ=UTC`) |

## Validation

- Title and authorship preserved (Edmund Gunn Jr.; 7GC Research Product Spine)
- `RESULTS_PENDING_AUTHENTIC_GATE3_DATA` preserved in results and manuscript
- No invented submission venue, repository DOI, p-values, or effect sizes
- All `\cite{...}` keys resolve in `references.bib`
- Page count within 6--8 inclusive

## Reproducibility notes

Builds export `SOURCE_DATE_EPOCH=0` and `TZ=UTC` before compilation.
Residual PDF byte differences may still occur from hyperref object IDs, tool-specific XMP metadata, or Tectonic cache state even when content is unchanged.
Compare `PDF SHA-256` together with page count and pinned tool version rather than expecting cross-machine byte identity.

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
