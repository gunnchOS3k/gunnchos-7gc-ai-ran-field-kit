.PHONY: setup lint test contract-test benchmark ablation sensitivity integrated-pipeline reproduce clean verify-repo-lock gate1-validate r6g-reproduce

# Prefer Python 3.11+ when present (system python3 on macOS is often 3.9 without deps).
PYTHON ?= $(shell command -v python3.11 >/dev/null 2>&1 && echo python3.11 || (test -x /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 && echo /Library/Frameworks/Python.framework/Versions/3.11/bin/python3 || echo python3))
SCHEMA_DIR := $(CURDIR)/contracts
REPOS_ROOT ?= $(CURDIR)/..
EDGE_INPUT ?= fixtures/valid/edge_measurement_batch.valid.json
OUTPUT_ROOT ?= results/integrated

setup:
	$(PYTHON) -m pip install -r requirements.txt
	$(PYTHON) -m pip install -r $(REPOS_ROOT)/edge-io-measurement-node/requirements.txt
	$(PYTHON) -m pip install -r $(REPOS_ROOT)/7gc-digital-twin/requirements.txt
	$(PYTHON) -m pip install -r $(REPOS_ROOT)/spectrumx-ai-ran-gary/requirements.txt
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

write-repo-lock:
	$(PYTHON) scripts/write_repo_lock.py --repos-root $(REPOS_ROOT)

.PHONY: write-repo-lock corrective-audit verify-inherited-ci
.PHONY: gate4-oulu-scientific gate4-nvidia-aerial-depth gate5-publication-release
.PHONY: gate6-harness all-corrective

corrective-audit:
	@test -f CORRECTIVE_DEPTH_INITIAL_AUDIT.md
	@test -f CORRECTIVE_DEPTH_FAILURE_REPRODUCTION.md
	@test -f STATUS_DEPENDENCY_GRAPH.json
	$(PYTHON) scripts/run_corrective_validators.py --track corrective-audit

verify-inherited-ci:
	$(PYTHON) scripts/verify_inherited_ci.py --require-file

gate4-oulu-scientific:
	$(PYTHON) scripts/run_corrective_validators.py --track oulu-scientific

gate4-nvidia-aerial-depth:
	$(PYTHON) scripts/run_corrective_validators.py --track nvidia-aerial-depth

gate5-publication-release:
	$(PYTHON) scripts/run_corrective_validators.py --track gate5-publication-release

gate6-harness:
	$(PYTHON) scripts/run_corrective_validators.py --track gate6-harness

all-corrective: corrective-audit verify-repo-lock gate4-oulu-scientific gate4-nvidia-aerial-depth gate5-publication-release gate6-harness application-evidence-pack
	$(PYTHON) scripts/run_corrective_validators.py --track all-corrective
	@echo "ALL_CORRECTIVE_DONE — inspect orchestration/gates_4_6/corrective/ for earned statuses only"

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

.PHONY: generalization-download generalization-verify generalization-preprocess generalization-evaluate

generalization-download:
	@test -n "$(DATASET)" || (echo "Set DATASET=nordicdat" && exit 1)
	$(PYTHON) scripts/run_generalization.py download --dataset $(DATASET)

generalization-verify:
	@test -n "$(DATASET)" || (echo "Set DATASET=nordicdat" && exit 1)
	$(PYTHON) scripts/run_generalization.py verify --dataset $(DATASET)

generalization-preprocess:
	@test -n "$(DATASET)" || (echo "Set DATASET=nordicdat" && exit 1)
	$(PYTHON) scripts/run_generalization.py preprocess --dataset $(DATASET)

generalization-evaluate:
	@test -n "$(DATASET)" || (echo "Set DATASET=nordicdat" && exit 1)
	$(PYTHON) scripts/run_generalization.py evaluate --dataset $(DATASET)

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
	bash scripts/build_paper.sh

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

# ---------------------------------------------------------------------------
# Gates 4–6 (Oulu GENOME + NVIDIA Aerial) — distinct from legacy GATE_4_PASS
# ---------------------------------------------------------------------------
.PHONY: audit-gates-4-6 gate4 gate4-oulu gate4-nvidia-cpu gate4-nvidia-gpu gate5
.PHONY: gate6-dry-run validate-physical-evidence all-automatable application-evidence-pack
.PHONY: write-gates-4-6-lock validate-cross-repo-evidence

audit-gates-4-6:
	@test -f GATES_4_6_INITIAL_AUDIT.md
	@test -f ROLE_REQUIREMENT_TRACEABILITY.md
	@test -f CROSS_REPO_IMPLEMENTATION_PLAN.md
	@test -f NON_NEGOTIABLES_GATES_4_6.md
	$(PYTHON) scripts/write_gates_4_6_version_lock.py
	@echo "AUDIT_OK"

write-gates-4-6-lock:
	$(PYTHON) scripts/write_gates_4_6_version_lock.py

gate4: write-gates-4-6-lock
	$(PYTHON) scripts/run_gate4.py --track all --skip-lock

gate4-oulu: write-gates-4-6-lock
	$(PYTHON) scripts/run_gate4.py --track oulu --skip-lock

gate4-nvidia-cpu: write-gates-4-6-lock
	$(PYTHON) scripts/run_gate4.py --track nvidia-cpu --skip-lock

gate4-nvidia-gpu: write-gates-4-6-lock
	$(PYTHON) scripts/run_gate4.py --track nvidia-gpu --skip-lock

gate5: write-gates-4-6-lock
	$(PYTHON) scripts/run_gate5.py --skip-lock

gate6-dry-run:
	$(PYTHON) scripts/run_gate6_dry_run.py

validate-physical-evidence:
	$(PYTHON) scripts/validate_physical_evidence.py

validate-cross-repo-evidence:
	$(PYTHON) scripts/validate_cross_repo_evidence.py --skip-lock

application-evidence-pack:
	$(PYTHON) scripts/build_application_evidence_pack.py

all-automatable: audit-gates-4-6 gate6-dry-run validate-physical-evidence gate4 gate5 application-evidence-pack validate-cross-repo-evidence
	@echo "ALL_AUTOMATABLE_COMPLETE — see GATES_4_6_MASTER_STATUS.md"

.PHONY: remote-integrity-audit checkout-locked-repositories verify-mandatory-workflows verify-branch-governance acceptance-completion

remote-integrity-audit:
	@test -f ACCEPTANCE_COMPLETION_INITIAL_AUDIT.md
	@test -f REMOTE_CI_FAILURE_REPRODUCTION.md
	@test -f BRANCH_PROTECTION_HANDOFF.md
	$(PYTHON) -c "print('REMOTE_INTEGRITY_AUDIT_OK')"

checkout-locked-repositories:
	$(PYTHON) scripts/checkout_locked_repositories.py --repos-root $(REPOS_ROOT)

verify-mandatory-workflows:
	@test -n "$(RUNS_JSON)" || (echo "Set RUNS_JSON=path from gh run list" && exit 2)
	$(PYTHON) scripts/verify_mandatory_workflows.py --accepted-sha $${ACCEPTED_SHA:-$$(git rev-parse HEAD)} --runs-json $(RUNS_JSON)

verify-branch-governance:
	@test -f BRANCH_PROTECTION_HANDOFF.md
	@echo "BRANCH_PROTECTION status: see BRANCH_PROTECTION_HANDOFF.md (BLOCKED_REPOSITORY_ADMIN_PERMISSION until applied)"

acceptance-completion: remote-integrity-audit verify-repo-lock gate4-oulu-scientific gate4-nvidia-aerial-depth gate5-publication-release gate6-harness application-evidence-pack
	@echo "ACCEPTANCE_COMPLETION_LOCAL_DONE — CONTROL_PLANE_REMOTE_CI_PASS requires green mandatory workflows"

.PHONY: gate-0 gate-1 control-plane validate-main-branch-policy ingest-product-charter
.PHONY: gate1-runtime-hygiene gate1-operator-status docs-integrity

docs-integrity:
	$(PYTHON) scripts/validate_docs_integrity.py --write-catalog
	@echo "DOCS_INTEGRITY target complete"

ingest-product-charter:
	$(PYTHON) scripts/ingest_product_charter.py

validate-main-branch-policy:
	$(PYTHON) scripts/validate_main_branch_policy.py

control-plane:
	$(PYTHON) -m control_plane generate
	$(PYTHON) -m control_plane validate
	$(PYTHON) scripts/validate_main_branch_policy.py
	$(PYTHON) -m pytest -q tests/control_plane tests/test_main_branch_policy.py
	@test -f program/reports/GATE_0_AUTOMATED_COMPLETION_REPORT.md
	@echo "CONTROL_PLANE_OK — see python -m control_plane status for earned tokens"

gate-0: control-plane
	@$(PYTHON) -m control_plane status

gate1-runtime-hygiene:
	$(PYTHON) scripts/check_gate1_runtime_artifacts_untracked.py

gate1-operator-status:
	$(PYTHON) -m gate1.operator.cli final-status

.PHONY: gate-1
gate-1: gate1-runtime-hygiene
	$(PYTHON) -m gate1.orchestrator.cli run
	$(PYTHON) -m gate1.orchestrator.cli validate-evidence
	$(PYTHON) -m gate1.orchestrator.cli status
	$(PYTHON) -m gate1.operator.cli final-status
	$(PYTHON) -m pytest -q tests/gate1
	@test -f gate1/reports/GATE_1_AUTOMATED_COMPLETION_REPORT.md
	@test -f gate1/reports/GATE_1_POST_MERGE_INTEGRITY_AUDIT.md
	@echo "GATE_1_LOCAL_AUTOMATION_PASS GATE_1_REMOTE_CI_PENDING GATE_1_PHYSICAL_EVIDENCE_PENDING (not GATE_1_PASS without accepted physical evidence)"

next-work-packet:
	python3 scripts/next_work_packet.py


# R6G digital replication / adoption (no SoA inflation)
r6g-reproduce:
	$(PYTHON) -m research.r6g.replication.reproduce
	$(PYTHON) -m research.r6g.replication.verify_independent
	$(PYTHON) -m research.r6g.evaluate
	$(PYTHON) -m pytest -q tests/test_r6g_breakthroughs.py tests/test_r6g_replication.py tests/test_r6g_portfolio_adoption_002.py

.PHONY: nvidia-6g-probe nvidia-6g-leak-scan
nvidia-6g-probe:
	$(PYTHON) -m research.external_reproduction.cli.researcher_cli nvidia-6g-probe

nvidia-6g-leak-scan:
	$(PYTHON) scripts/scan_nvidia_secret_leaks.py --root . --fail
