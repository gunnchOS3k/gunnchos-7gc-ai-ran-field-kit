# Application-readiness command map

```bash
make setup
make verify
make verify-repo-lock
python -m pytest -q
make integrated-pipeline
make gate4-evaluation-ready
make pilot-assignments
make pilot-validate-assignments
make pilot-rehearsal
make pilot-coverage
make pilot-daily-gate DAY=day_01
make evaluate-baselines   # blocked scientifically without DATASET=
make evaluate-holdouts
make evaluate-ablations
make evaluate-sensitivity
make evaluate-missing-data
make evaluate-all
make reproduce-core
make reproduce-paper
make paper
make release-candidate
make application-readiness
```

Reports land in `research-application-control/reports/`.
