# Environment

## Python

- Recommended: **Python 3.11+**
- Install: `pip install -r requirements.txt`
- Optional integrated deps: repo `Makefile` `setup` target pulls sibling requirements when present

## Repository layout

| Variable | Default | Purpose |
|----------|---------|---------|
| `REPOS_ROOT` | parent of this repo | Sibling research repos |
| `EDGE_INPUT` | `fixtures/valid/edge_measurement_batch.valid.json` | Integrated pipeline input |
| `OUTPUT_ROOT` | `results/integrated` | Pipeline outputs |

Expected siblings (not vendored):

- `edge-io-measurement-node`
- `7gc-digital-twin`
- `spectrumx-ai-ran-gary`
- `ntn-resilience-sim` (for resilience paths)

## Core commands

```bash
make setup          # optional full sibling setup
make test
make contract-test
make integrated-pipeline
make gate1-validate
make verify-repo-lock REPOS_ROOT=..
```

## TeX (paper PDF)

- Requires `pdflatex` and `bibtex` (TeX Live / MacTeX)
- Build: `cd paper && make pdf`
- If unavailable: `cd paper && make blocked`

## Private data paths (local only)

- `datasets/controlled/raw-private/` — device exports (gitignored)
- `datasets/controlled/raw/` — legacy raw path (gitignored)

## CI

GitHub Actions workflows under `.github/workflows/` run smoke/contract tests on push.
They do not collect pilot data or mint DOIs.

## OS notes

Developed on macOS; Linux expected compatible.
Android/device collection requires separate edge-io tooling — not required for fixture reproduction.
