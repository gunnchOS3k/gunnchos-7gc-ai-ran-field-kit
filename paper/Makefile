# IEEE methods manuscript — build

MAIN = main
TEX = $(MAIN).tex
PDF = $(MAIN).pdf

.PHONY: all pdf clean check-tools blocked

all: pdf

check-tools:
	@command -v pdflatex >/dev/null 2>&1 || { \
	  echo "BLOCKED: pdflatex not found. Install TeX Live or MacTeX."; \
	  echo "Manuscript sources are methods-ready; PDF build is optional."; \
	  exit 2; \
	}
	@command -v bibtex >/dev/null 2>&1 || { \
	  echo "BLOCKED: bibtex not found. Install TeX Live or MacTeX."; \
	  exit 2; \
	}

pdf: check-tools
	pdflatex -interaction=nonstopmode $(TEX)
	bibtex $(MAIN)
	pdflatex -interaction=nonstopmode $(TEX)
	pdflatex -interaction=nonstopmode $(TEX)

blocked:
	@echo "PDF build blocked on this machine (pdflatex/bibtex unavailable)."
	@echo "Sources: main.tex, sections/*.tex, references.bib"
	@exit 0

clean:
	rm -f $(MAIN).pdf $(MAIN).aux $(MAIN).bbl $(MAIN).blg $(MAIN).log $(MAIN).out
