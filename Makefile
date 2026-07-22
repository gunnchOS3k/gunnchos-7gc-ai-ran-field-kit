.PHONY: setup lint test contract-test benchmark ablation sensitivity integrated-pipeline reproduce clean

PYTHON ?= python3
SCHEMA_DIR := $(CURDIR)/contracts
REPOS_ROOT ?= $(CURDIR)/..
EDGE_INPUT ?= fixtures/valid/edge_measurement_batch.valid.json
OUTPUT_ROOT ?= results/integrated

setup:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -r $(REPOS_ROOT)/edge-io-measurement-node/requirements.txt
	$(PYTHON) -m pip install -r $(REPOS_ROOT)/7gc-digital-twin/requirements.txt
	$(PYTHON) -m pip install -r $(REPOS_ROOT)/spectrumx-ai-ran-gary/requirements.txt || true
	$(PYTHON) -m pip install 'scipy>=1.11' 'numpy>=1.24' jsonschema pytest pyyaml

lint:
	$(PYTHON) -m compileall -q scripts
	$(PYTHON) scripts/validate_contract.py --help >/dev/null

test: contract-test
	$(PYTHON) -m pytest -q tests

contract-test:
	$(PYTHON) -m pytest -q tests/contracts tests/failure_cases

benchmark:
	@echo "Benchmarks are produced by integrated-pipeline (benchmark_results.csv)"
	@test -n "$(RUN_DIR)" && test -f "$(RUN_DIR)/benchmark_results.csv"

ablation:
	@echo "Ablations are produced by integrated-pipeline (ablation_results.csv)"
	@test -n "$(RUN_DIR)" && test -f "$(RUN_DIR)/ablation_results.csv"

sensitivity:
	@echo "Sensitivity results are produced by integrated-pipeline (sensitivity_results.csv)"
	@test -n "$(RUN_DIR)" && test -f "$(RUN_DIR)/sensitivity_results.csv"

integrated-pipeline:
	$(PYTHON) scripts/run_integrated_pipeline.py \
		--edge-input $(EDGE_INPUT) \
		--repos-root $(REPOS_ROOT) \
		--output-root $(OUTPUT_ROOT) \
		--strict

reproduce:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) scripts/run_integrated_pipeline.py \
		--edge-input $(EDGE_INPUT) \
		--repos-root $(REPOS_ROOT) \
		--output-root $(OUTPUT_ROOT) \
		--strict
	$(PYTHON) scripts/verify_provenance.py --run-dir $$(ls -d $(OUTPUT_ROOT)/* | tail -n 1)

clean:
	rm -rf results/integrated/*
