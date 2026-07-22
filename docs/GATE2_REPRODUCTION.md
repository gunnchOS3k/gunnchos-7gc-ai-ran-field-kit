# Gate 2 Reproduction

```bash
cd gunnchos-7gc-ai-ran-field-kit
make setup
make integrated-pipeline EDGE_INPUT=fixtures/valid/edge_measurement_batch.valid.json
make reproduce EDGE_INPUT=fixtures/valid/edge_measurement_batch.valid.json
```

Strict mode verifies `integration/repo-lock.json` against checked-out component SHAs.
