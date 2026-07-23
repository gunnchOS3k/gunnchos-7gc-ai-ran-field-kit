# Pilot Assignment Canonical Hashing

## Algorithm

| Field | Value |
|---|---|
| Name | `gunnchos-canonical-json-sha256-v1` |
| JSON field | `assignment_hash_algorithm` |
| Digest | SHA-256 |
| Encoding | UTF-8 |
| Hex | lowercase `[0-9a-f]{64}` |

## Payload construction

1. Start from the full assignment JSON object.
2. **Omit** the top-level `assignment_hash` property from the hashed payload.
3. Retain `assignment_hash_algorithm` inside the hashed payload.
4. Recursively canonicalize the remaining value.

## Object keys

- Sort every object’s keys lexicographically by Unicode code point order.
- Nested objects (including `producer`) are sorted independently.
- Array element order is preserved.

## Compact serialization

- No insignificant whitespace.
- Separators are exactly `,` between members/elements and `:` between keys and values.
- No trailing commas.

## Scalars

| JSON type | Canonical form |
|---|---|
| `null` | `null` |
| `true` / `false` | `true` / `false` |
| string | RFC 8259 / Python `json.dumps(..., ensure_ascii=True)` quoting |
| integer | decimal digits, optional leading `-`, no leading zeros (except `0`) |
| non-integer number | finite only; no locale; no scientific notation; shortest plain decimal that preserves the value |

## Deterministic numeric rule for this schema

`planned_duration_seconds`:

- Must be an **integer** number of seconds.
- Emit `300`, never `300.0`.
- Schema type: integer.
- Android and Python both serialize it as an integer token.

Do not rely on Python `json.dumps` float defaults or `org.json.JSONObject.toString()` defaults as the cryptographic form.

## Hash

```
assignment_hash = lowercase_hex( SHA-256( UTF-8( canonicalize(payload_without_assignment_hash) ) ) )
```

## Interoperability requirement

The same golden fixture bytes must produce identical:

- canonical UTF-8 payload
- canonical byte count
- SHA-256 digests

in field-kit Python and Edge-IO Android (JVM unit tests and on-device import).
