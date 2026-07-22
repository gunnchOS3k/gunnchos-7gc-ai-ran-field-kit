# Gate 2 Test and Validation Report

Generated from executed commands on 2026-07-22.

## gunnchos-7gc-ai-ran-field-kit
- commit: `760062c84fa6bd760208c8f287fe58adc61e13a6`
- command: `python3 -m pytest -q tests`
- result: 19 passed

## edge-io-measurement-node
- commit: `9d04dd5bf3b726b21b76718ee80c7c2f5c6c18f7`
- command: `PYTHONPATH=src pytest -q tests/contracts`
- result: 11 passed

## 7gc-digital-twin
- commit: `323a88ca21b7ff7bee2a8549cddb09da96b0ed1b`
- command: `PYTHONPATH=src pytest -q tests/gate2`
- result: 6 passed

## spectrumx-ai-ran-gary
- commit: `0686d47d77cbc9fb9cbce262cdae732996f106b5`
- command: `PYTHONPATH=src pytest -q tests/gate2`
- result: 4 passed

## ntn-resilience-sim
- commit: `ea7800e22409f2d7b6a41e22560f81d59043475e`
- command: `PYTHONPATH=src pytest -q tests/gate2`
- result: 5 passed

## Integrated pipeline
- command: `python3 scripts/run_integrated_pipeline.py --edge-input fixtures/valid/edge_measurement_batch.valid.json --repos-root .. --output-root results/integrated --strict`
- run_id: `2026-07-22-synthetic-gary-learn-001`
- evidence_level: `synthetic`
- selected AI-RAN policy: `twin_informed`
- selected resilience mode: `terrestrial`
- output directory: `/agent/repos/gunnchos-7gc-ai-ran-field-kit/results/integrated/2026-07-22-synthetic-gary-learn-001`
- manifest: `/agent/repos/gunnchos-7gc-ai-ran-field-kit/results/integrated/2026-07-22-synthetic-gary-learn-001/manifest.json`
- checksums: `/agent/repos/gunnchos-7gc-ai-ran-field-kit/results/integrated/2026-07-22-synthetic-gary-learn-001/checksums.sha256`
- gate status: `AUTOMATED_PIPELINE_PASS`

Warnings: no physical-device dataset; ReadyGary unused; external evidence unmet.
