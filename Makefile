.PHONY: setup lint test contract-test benchmark ablation sensitivity integrated-pipeline reproduce clean verify-repo-lock gate1-validate

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

verify-repo-lock:
	$(PYTHON) scripts/verify_repo_lock.py --repos-root $(REPOS_ROOT)

gate1-validate:
	$(PYTHON) scripts/validate_gate1_thesis.py

.PHONY: gate3-evidence assemble-controlled-dataset external-data-download external-data-verify external-data-transform gate3-integrated-evidence

gate3-evidence:
	$(PYTHON) scripts/run_gate3_evidence_pipeline.py \
		--controlled-sessions datasets/controlled/sanitized \
		--collection-matrix protocols/controlled_pilot_matrix.csv \
		--external-registry datasets/external/registry/external_dataset_registry.json \
		--repos-root $(REPOS_ROOT) \
		--output-root results/gate3 \
		--android-builds

assemble-controlled-dataset:
	$(PYTHON) scripts/assemble_controlled_dataset.py \
		--sessions datasets/controlled/sanitized \
		--matrix protocols/controlled_pilot_matrix.csv \
		--output-root results/gate3 \
		--repos-root $(REPOS_ROOT)

external-data-download:
	@echo "M-Lab archival download requires AUA/GCS credentials; registry records the unresolved step."
	$(PYTHON) scripts/register_external_dataset.py register

external-data-verify:
	$(PYTHON) scripts/verify_external_dataset.py

external-data-transform:
	$(PYTHON) scripts/transform_external_dataset.py --output datasets/external/transformed/ntn_sim_metadata.json

gate3-integrated-evidence:
	@test -n "$(CONTROLLED_DATASET)" || (echo "Set CONTROLLED_DATASET=path/to/dataset_manifest.json" && exit 1)
	$(PYTHON) -c "import json,sys; m=json.load(open(sys.argv[1])); assert m.get('evidence_level')=='controlled_device_measurement'; 'refusing synthetic'; print('ok', m['dataset_id'])" $(CONTROLLED_DATASET)

.PHONY: gate4-evaluation-ready gate4-evaluate pilot-status pilot-next pilot-import pilot-validate-day pilot-report
.PHONY: verify reproduce-core reproduce-paper paper release-candidate application-readiness
.PHONY: pilot-assignments pilot-validate-assignments pilot-rehearsal pilot-coverage pilot-daily-gate
.PHONY: pilot-preflight pilot-start pilot-ingest
.PHONY: evaluate-baselines evaluate-holdouts evaluate-ablations evaluate-sensitivity evaluate-missing-data evaluate-all

gate4-evaluation-ready:
	$(PYTHON) scripts/run_gate4_evaluation.py \
		--repos-root $(REPOS_ROOT) \
		--output-root results/gate4 \
		--dry-run \
		--strict

gate4-evaluate:
	@test -n "$(DATASET)" || (echo "Set DATASET=path/to/dataset_manifest.json" && exit 1)
	$(PYTHON) scripts/run_gate4_evaluation.py \
		--dataset $(DATASET) \
		--repos-root $(REPOS_ROOT) \
		--output-root results/gate4 \
		--strict

pilot-status:
	$(PYTHON) scripts/pilotctl.py status

pilot-next:
	$(PYTHON) scripts/pilotctl.py next

pilot-import:
	@test -n "$(SESSION)" || (echo "Set SESSION=path/to/session.json" && exit 1)
	$(PYTHON) scripts/pilotctl.py import-session $(SESSION)

pilot-validate-day:
	@test -n "$(DAY)" || (echo "Set DAY=day_01" && exit 1)
	$(PYTHON) scripts/pilotctl.py validate-day $(DAY)

pilot-report:
	$(PYTHON) scripts/pilotctl.py report

verify: lint verify-repo-lock gate1-validate
	$(PYTHON) scripts/validate_master_status.py
	$(PYTHON) scripts/validate_preregistration.py
	$(PYTHON) scripts/validate_pilot_assignments.py
	$(PYTHON) -m pytest -q tests

reproduce-core: verify
	$(MAKE) integrated-pipeline
	$(MAKE) gate4-evaluation-ready

reproduce-paper:
	@if command -v pdflatex >/dev/null 2>&1; then \
		$(MAKE) -C paper pdf; \
	else \
		$(MAKE) -C paper blocked || true; \
		echo "BLOCKED: pdflatex unavailable — paper sources are methods-ready"; \
		exit 0; \
	fi

paper: reproduce-paper

release-candidate:
	bash release/build_release_archive.sh

application-readiness:
	$(PYTHON) scripts/run_application_readiness.py --repos-root $(REPOS_ROOT)

pilot-assignments:
	@test -f pilot/54_CELL_ASSIGNMENT_MATRIX.csv || (echo "missing pilot/54_CELL_ASSIGNMENT_MATRIX.csv" && exit 1)
	$(PYTHON) scripts/validate_pilot_assignments.py --matrix pilot/54_CELL_ASSIGNMENT_MATRIX.csv
	@echo "54-cell matrix present; design dates remain PENDING until Edmund approval"

pilot-validate-assignments:
	$(PYTHON) scripts/validate_pilot_assignments.py

pilot-rehearsal:
	$(PYTHON) scripts/pilotctl.py emit-rehearsal --help >/dev/null
	@echo "Rehearsal mode is structurally available; sessions never count toward Gate 3."
	$(PYTHON) scripts/pilotctl.py status

pilot-coverage:
	$(PYTHON) scripts/pilotctl.py status
	$(PYTHON) scripts/audit_collection_coverage.py \
		--matrix protocols/controlled_pilot_matrix.csv \
		--sessions datasets/controlled/sanitized \
		--output datasets/controlled/coverage/coverage_audit.json || true
	@echo "GATE_3 eligible sessions remain HUMAN_ACTION_REQUIRED until 54 authentic PILOT sessions exist."

pilot-daily-gate:
	@test -n "$(DAY)" || (echo "Set DAY=day_01" && exit 1)
	$(PYTHON) scripts/pilotctl.py validate-day $(DAY)

pilot-preflight:
	@test -n "$(ASSIGNMENT)" || (echo "Set ASSIGNMENT=path/to/assignment.json" && exit 1)
	$(PYTHON) scripts/pilotctl.py validate-assignment $(ASSIGNMENT)
	$(PYTHON) scripts/verify_repo_lock.py --repos-root $(REPOS_ROOT)
	@echo "preflight: confirm consent, battery, thermal, storage, backup before start"

pilot-start:
	$(PYTHON) scripts/pilotctl.py start

pilot-ingest:
	@test -n "$(RAW_FILE)" || (echo "Set RAW_FILE=..." && exit 1)
	$(PYTHON) scripts/pilotctl.py import-session $(RAW_FILE)

# Evaluation targets refuse silent synthetic scientific success.
# Without DATASET, they run infrastructure dry-run only and label blocked for science.
evaluate-baselines:
	@if [ -z "$(DATASET)" ]; then \
		echo "BLOCKED:scientific_eval_pending_authentic_dataset"; \
		$(MAKE) gate4-evaluation-ready; \
	else \
		$(PYTHON) scripts/run_baselines.py --dataset $(DATASET) --output results/gate4/baselines.csv; \
	fi

evaluate-holdouts:
	@if [ -z "$(DATASET)" ]; then \
		echo "BLOCKED:scientific_eval_pending_authentic_dataset"; \
		$(MAKE) gate4-evaluation-ready; \
	else \
		$(PYTHON) scripts/build_evaluation_splits.py --dataset $(DATASET) --output-root results/gate4/holdouts; \
	fi

evaluate-ablations:
	@if [ -z "$(DATASET)" ]; then \
		echo "BLOCKED:scientific_eval_pending_authentic_dataset"; \
		$(MAKE) gate4-evaluation-ready; \
	else \
		$(PYTHON) scripts/run_ablations.py --dataset $(DATASET) --output results/gate4/ablations.csv; \
	fi

evaluate-sensitivity:
	@if [ -z "$(DATASET)" ]; then \
		echo "BLOCKED:scientific_eval_pending_authentic_dataset"; \
		$(MAKE) gate4-evaluation-ready; \
	else \
		$(PYTHON) scripts/run_sensitivity.py --dataset $(DATASET) --output results/gate4/sensitivity.csv; \
	fi

evaluate-missing-data:
	@if [ -z "$(DATASET)" ]; then \
		echo "BLOCKED:scientific_eval_pending_authentic_dataset"; \
		exit 0; \
	else \
		$(PYTHON) scripts/analyze_failure_boundaries.py --dataset $(DATASET) --output-root results/gate4/missing_data; \
	fi

evaluate-all: evaluate-baselines evaluate-holdouts evaluate-ablations evaluate-sensitivity evaluate-missing-data
	@echo "evaluate-all complete (scientific PASS requires authentic DATASET + Gate 3 freeze)"
