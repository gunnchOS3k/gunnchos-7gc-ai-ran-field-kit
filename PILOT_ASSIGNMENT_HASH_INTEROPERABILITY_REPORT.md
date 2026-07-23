# PILOT_ASSIGNMENT_HASH_INTEROPERABILITY_REPORT

## Original failure (import only — no measurement session)

| Field | Value |
|---|---|
| Classification | Failed assignment import (not physical evidence) |
| assignment_id | `asn_7cd312d6fa594505` |
| Stored `assignment_hash` | `bf4aa8eabedb953bafd19029a47a91cb993a5ed728ad27b31f89c04032ea3c84` |
| File SHA-256 | `196bf429cfde250263659a1979d78095c4a4421c4b0dc92ae6856373cde49ec8` |
| Preserved original | `/tmp/gate3_hash_diag/original_failed_assignment.json` (also Mac Downloads copy) |

Edmund independently verified the stored hash equals SHA-256 over the
field-kit canonical payload (omit `assignment_hash`, recursively sorted
keys, compact JSON, UTF-8). That verification is confirmed.

## Root cause

Android `PilotAssignment.computeCanonicalHash` previously did:

```kotlin
val copy = JSONObject(obj.toString())
copy.remove("assignment_hash")
```

`JSONObject.toString()` collapsed `planned_duration_seconds: 300.0` to
integer `300`. After reparse, Android hashed `"planned_duration_seconds":300`
while field-kit (Python `json.dumps`) hashed `"planned_duration_seconds":300.0`.

### Exact mismatch (failed file)

| Side | Canonical SHA-256 | Byte length |
|---|---|---|
| Field-kit (declared) | `bf4aa8eabedb953bafd19029a47a91cb993a5ed728ad27b31f89c04032ea3c84` | 994 |
| Android old path | `ed97926958255eed4dbf11b06d4cdf02b7d7697d3337b78aea99f874350c88ff` | 992 |

First differing byte index: **643**

- Field-kit context: `"planned_duration_seconds":300.0,"producer":...`
- Android old context: `"planned_duration_seconds":300,"producer":...`

Artifacts:

- `/tmp/gate3_hash_diag/fieldkit_canonical_assignment.json`
- `/tmp/gate3_hash_diag/android_canonical_assignment.json`
- `/tmp/gate3_hash_diag/assignment_hash_comparison.txt`

## Canonicalization contract

Authoritative spec:

`docs/PILOT_ASSIGNMENT_CANONICAL_HASHING.md`

Algorithm:

`gunnchos-canonical-json-sha256-v1`

Numeric rule for this schema:

- `planned_duration_seconds` is an **integer**
- emit `300`, never `300.0`
- both languages serialize the integer token identically

Implementations:

- field-kit: `scripts/assignment_canonical.py`
- Android: `AssignmentCanonicalJson.kt` (no `JSONObject.toString()` crypto path)

New assignments include `assignment_hash_algorithm`.

## Golden fixtures

Under `fixtures/pilot_assignment/`:

| Fixture | Expected |
|---|---|
| `valid_rehearsal.json` | PASS |
| `valid_pilot.json` | PASS |
| `valid_calibration.json` | PASS |
| `reordered_keys.json` | same hash as valid |
| `producer_reordered.json` | same hash as valid |
| `tampered_zone.json` | FAIL hash |
| `modified_value.json` | FAIL hash |
| `wrong_algorithm.json` | FAIL algorithm |
| `expired.json` | FAIL expiry (hash ok after restamp) |

## Regenerated rehearsal assignment (v2)

| Field | Value |
|---|---|
| File | `gate3_rehearsal_assignment_v2.json` |
| assignment_id | `asn_33c87f5e180c45ad` |
| assignment_hash | `30adbabcd1a059d0d4362c31da2030259d8943fcefa4c27dbd80ba44b35f48b2` |
| algorithm | `gunnchos-canonical-json-sha256-v1` |
| planned_duration_seconds | `300` (integer) |
| Field-kit validate | PASS |
| Field-kit verify-roundtrip | PASS |
| Android JVM golden tests | PASS |

Failed original file was **not** overwritten.

## Android build after fix

| Field | Value |
|---|---|
| versionName | `0.4.1-gate3-pilot` |
| versionCode | 7 |
| Install | Success |
| Launch | No crash |

## Pilot coverage

**0 / 54** — failed import is not evidence; rehearsal not started.

## On-device import

Requires Edmund to import `gate3_rehearsal_assignment_v2.json` and confirm
**PASS** on screen before any five-minute rehearsal.
