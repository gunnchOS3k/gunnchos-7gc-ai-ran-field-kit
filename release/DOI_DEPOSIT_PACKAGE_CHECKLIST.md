# DOI Deposit Package Checklist

**Generated:** 2026-07-24T15:05:00Z  
**DOI status:** **DOI_PENDING**  
**Zenodo metadata:** `release/ZENODO_METADATA.json`

---

## Pre-deposit gates (must be honest)

| Gate | Required for deposit | Current |
|------|---------------------|---------|
| No raw-private in tarball | YES | PASS — verified in `LOCAL_RELEASE_CANDIDATE_AUDIT.md` |
| Claim boundaries documented | YES | `release/CLAIM_BOUNDARIES.md` |
| Scientific results claimed | NO | PASS — not claimed (0/54 Gate 3) |
| Human metadata review | YES | HUMAN_ACTION_REQUIRED |

---

## Package contents checklist

- [x] Build archive: `make release-candidate`
- [x] Verify SHA256: `release/dist/*.sha256`
- [x] List contents: `release/PUBLIC_ARCHIVE_CONTENTS.txt`
- [x] Validate `release/ZENODO_METADATA.json` structure (title, creators, description, license, keywords, related_identifiers with DOI_PENDING)
- [ ] Human confirms title/description match public claims
- [ ] Human confirms no affiliation implied beyond metadata
- [ ] Upload tarball to Zenodo
- [ ] Replace `DOI_PENDING` in metadata, `CITATION.cff`, and landing page after issuance
- [ ] Tag GitHub release matching archive checksum

---

## Metadata field validation

| Field | Present | Notes |
|-------|---------|-------|
| title | YES | Methods + preregistration scope |
| creators | YES | Edmund Gunn Jr. — no invented ORCID |
| description | YES | States 0/54, Gate 4 blocked |
| license | YES | MIT |
| keywords | YES | 8 keywords |
| related_identifiers | YES | DOI_PENDING + GitHub URL |

---

## Exclusions (must never upload)

- `datasets/controlled/raw-private/**`
- `datasets/controlled/raw/**`
- Calibration sanitized JSON with device identifiers
- Any unreleased referee or faculty correspondence

---

## Post-deposit

1. Record DOI in `release/ZENODO_METADATA.json` and `CITATION.cff`
2. Update `portfolio/LANDING_PAGE.md` DOI row
3. Set `integrity.doi_claimed: true` in `MASTER_STATUS.json` only after authentic DOI exists
