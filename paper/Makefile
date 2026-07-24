# IEEE methods manuscript — build via pinned Tectonic or Docker (see scripts/build_paper.sh)

ROOT := $(abspath ..)
BUILD_SCRIPT := $(ROOT)/scripts/build_paper.sh

MAIN = main
TEX = $(MAIN).tex
PDF = $(MAIN).pdf

.PHONY: all pdf clean check-tools blocked

all: pdf

pdf:
	@bash "$(BUILD_SCRIPT)"

# Legacy target: direct pdflatex when a full TeX Live install is present locally.
pdf-local-tex: check-tools
	pdflatex -interaction=nonstopmode $(TEX)
	bibtex $(MAIN)
	pdflatex -interaction=nonstopmode $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)

check-tools:
	@command -v pdflatex >/dev/null 2>&1 || { \
	  echo "BLOCKED: pdflatex not found. Use: make pdf (runs scripts/build_paper.sh)"; \
	  exit 2; \
	}
	@command -v bibtex >/dev/null 2>&1 || { \
	  echo "BLOCKED: bibtex not found. Use: make pdf (runs scripts/build_paper.sh)"; \
	  exit 2; \
	}

blocked:
	@echo "PDF build blocked on this machine (no Tectonic, Docker, or pdflatex)."
	@echo "Run from repo root: bash scripts/build_paper.sh"
	@echo "Sources: main.tex, sections/*.tex, references.bib"
	@exit 0

clean:
	rm -f $(MAIN).pdf $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out \
	      $(MAIN).synctex.gz $(MAIN).fdb_latexmk $(MAIN).fls \
	      PAPER_BUILD_REPORT.md PAPER_BUILD_MANIFEST.json PAPER_CHECKSUMS.sha256 \
	      .paper_build.log
