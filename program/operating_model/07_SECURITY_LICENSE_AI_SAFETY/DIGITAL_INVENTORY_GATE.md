# Digital inventory gate (prep for WP-006)

WP-006 (license release gate first complete audit) is **not started** as a
cycle packet. This note records the digital automation that now exists in
`gunnchos-device-os`:

- CycloneDX-style SBOM from declared Python/npm/Godot/font/media
- HBOM rows from sibling NPI/hardware BOM CSVs
- AI-BOM from model manifests + datasets/scientific records
- `UNKNOWN_RELEASE_BLOCKING` when license or provenance is `UNKNOWN`

Statuses from [LICENSE_RELEASE_GATE.md](LICENSE_RELEASE_GATE.md) still apply:
CLEAR / CLEAR_WITH_OBLIGATIONS / REVIEW_REQUIRED / BLOCKED.

Machine inventory does **not** flip `REVIEW_REQUIRED` to CLEAR. Legal
approval remains HUMAN/EXTERNAL.

EXTERNAL_PENTEST_COMPLETE=false. E7 is not claimed.
