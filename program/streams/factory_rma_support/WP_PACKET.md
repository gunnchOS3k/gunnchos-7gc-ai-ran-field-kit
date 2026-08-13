# STREAM packet — factory / RMA / support digital operational model

## Why now
Factory identity, RMA, support, supply-chain fields, and first-use were
partially present as WP-013 tooling and docs. This packet makes the
DEV/TEST operational model *executable and honest* without claiming a
factory, a warranty, or a production release.

## Scope
- device-os factory station: serial, MAC, cert *request*, key *interface*,
  eSIM *interface*, calibration, test import, flash, device record, repair,
  rework, digital secure wipe
- device-os support: diagnostic bundle, fault codes, RMA states, service
  history, repair mode, replacement transfer, wipe, spares mapping,
  update-support/EOL metadata
- device-os first-use software flow
- hardware-industrial-design supply-chain field overlay
- field-kit STREAM ledger + honesty gate

## Out of scope
- PRODUCTION_RELEASE_CLAIMED
- Production keys / CA issuance / HSM ceremony
- Carrier eSIM credentials
- RFQ, purchase, fab
- Commercial warranty
- Inventing stock, price, lead-time, or MOQ
- Cursor merge

## Change class
B (operational model + honesty fields)

## Severity
S2 for missing factory/RMA software path; S1 if a production claim leaked

## Verification class
V1 digital tests in owner repos + field-kit honesty tests

## Exit (digital)
- [x] implementation
- [x] implementer tests
- [ ] independent verification
- [ ] Edmund merge (Cursor never merges)
- [ ] HUMAN/EXTERNAL CA, eSIM, warranty, supplier quotes
