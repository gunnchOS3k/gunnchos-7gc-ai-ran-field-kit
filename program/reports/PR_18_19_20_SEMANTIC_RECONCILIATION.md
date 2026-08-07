# PR #18/#19/#20 Semantic Reconciliation

Updated: `2026-08-07T22:52:29Z`  
Replacement branch: `cursor/reconcile-nonphysical-gates0-3`  
Current main: `a10fda31bba2573a94a979f44e6141cca44fb56c`  
Merge base: `01bacaed5d6e11bd59bd6494a612c25c91465f2a`

## Why dirty

PRs #18/#19/#20 branched from post-PR-17 (`01bacae`). Gates 4–8 (#21–#25) merged to `main` first and overlapped on:

- `.github/workflows/application-readiness.yml`
- `.github/workflows/gate2-integrated-system.yml`
- `gate1/ring_fabrication/README.md`
- `program/gates/gate_status.yaml`
- `program/physical/MASTER_ACCEPTANCE_DECISION_BOOK.md`
- `program/physical/MASTER_ASSEMBLY_SEQUENCE.md`
- `program/physical/MASTER_BRINGUP_SEQUENCE.md`
- `program/physical/MASTER_EVIDENCE_CAPTURE_SEQUENCE.md`
- `program/physical/MASTER_PHYSICAL_BUILD_AND_TEST_BOOK.md`
- `program/physical/MASTER_PROCUREMENT_BOM.csv`
- `program/physical/MASTER_TEST_EQUIPMENT_LIST.csv`
- `scripts/checkout_locked_repositories.py`

## Topology

- PR #19 = PR #20 history + `gate2/nonphysical/STATUS.yaml` (G2-C6 IN_PROGRESS correction)
- Duplicate Gate 2/3 content collapsed via PR #19 checkout only

## Classification summary

- PR #18 vs main: {'CONFLICT_REQUIRES_UNION': 11, 'MISSING_FROM_MAIN': 22, 'ALREADY_PRESENT_IDENTICAL': 1}
- PR #19 vs main: {'CONFLICT_REQUIRES_UNION': 11, 'MISSING_FROM_MAIN': 192, 'ALREADY_PRESENT_IDENTICAL': 1}

## Port method

- MISSING_FROM_MAIN trees checked out from #18/#19 deliberately
- CONFLICT files reconciled by union (deploy-key workflows/scripts from #18; physical CSVs union; status rewritten for Gates 0–8 truth)
- Generated reports regenerated from reconciled source-of-truth
- No wholesale merge of dirty branches; no force-push; no rewrite of #18/#19/#20

## Superset proof targets

- #18 unique semantic content preserved: YES
- #19 unique semantic content preserved: YES
- #20 unique semantic content preserved through #19 ancestry: YES
- Gate4–8 merged content preserved: YES
