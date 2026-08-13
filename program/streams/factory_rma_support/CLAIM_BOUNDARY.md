# STREAM claim boundary — factory / RMA / support

Cursor never merges.

| Token | Value |
| --- | --- |
| PRODUCTION_RELEASE_CLAIMED | false |
| Production keys | false |
| Production CA | false (request only) |
| eSIM credentials | EXTERNAL_PENDING |
| RFQ / purchase / fab | NOT_THIS_STREAM |
| Commercial warranty | EXTERNAL |
| Physical factory line | EXTERNAL/PHYSICAL |
| Physical Ring / dock | EXTERNAL |
| Quoted stock / price / lead-time / MOQ | UNKNOWN unless a cited quote exists (none here) |

## Digital prep (this STREAM)

Owner implementation lives in `gunnchos-device-os` (factory station, RMA desk,
first-use flow). Supply-chain *fields* live in
`gunnchos-hardware-industrial-design`. This field-kit packet is the program
ledger + honesty gate.

## Pending EXTERNAL / PHYSICAL

- Production identity CA and HSM ceremony
- Carrier eSIM
- Contract manufacturer line, RFQ, purchase, fab
- Warranty legal terms and depot logistics
- Supplier AVL quotes
- Physical Ring pairing and dock discovery

Unknown stays unknown. This STREAM does not invent inventory or prices.
