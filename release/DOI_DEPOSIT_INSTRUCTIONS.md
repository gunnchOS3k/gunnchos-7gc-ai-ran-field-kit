# DOI Deposit Instructions

**Status:** **DOI_PENDING** — no DOI is assigned in `CITATION.cff` until a human completes deposit.

## Preconditions

Complete items in [`RELEASE_CHECKLIST.md`](RELEASE_CHECKLIST.md):

- Authentic Gate 3 pilot evidence approved for publication (if claiming measured results)
- Sanitized dataset derivatives approved
- Author reproduction report outcome **PASS**
- Non-author reproduction report filed (recommended before DOI)
- `release/CHECKSUMS.sha256` matches `ARTIFACT_MANIFEST.json` entries
- Edmund Gunn Jr. release approval

## Build release archive

```bash
./release/build_release_archive.sh
```

Inspect tarball and checksum file before upload.

## Zenodo draft metadata

Start from [`ZENODO_METADATA_DRAFT.json`](ZENODO_METADATA_DRAFT.json).
Update version, description, and keywords only with verified facts.
Do **not** invent DOI, submission date, or download counts.

## CITATION.cff update (after deposit)

When Zenodo returns a DOI, add to root and `release/CITATION.cff`:

```yaml
doi: 10.5281/zenodo.XXXXXXX   # replace with assigned DOI only
```

Until then, omit `doi` or keep this document's **DOI_PENDING** note.

## What not to deposit

- `datasets/controlled/raw-private/**` (gitignored private exports)
- Unapproved sanitized sessions
- Synthetic Gate 4 CSVs mislabeled as field data

## Human-only steps

1. Create Zenodo record (or institutional equivalent)
2. Upload release tarball + checksums
3. Mint DOI
4. Update CITATION.cff and README
5. Create signed git tag (human approver, not CI)
