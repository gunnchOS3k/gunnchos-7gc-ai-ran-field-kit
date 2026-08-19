# Evidence Classification (Baseline V2)

| Class | Meaning |
| --- | --- |
| E0 | Document-only / charter |
| E1 | Unit or schema test on accepted main |
| E2 | Integrated CI PASS on accepted main |
| E3 | Cross-repo reproduction harness |
| E4 | Independent VP artifact with explicit negative space |

Baseline V2 does **not** upgrade E1/E2 to product-shipping claims. `DIGITAL_IMPLEMENTATION_COMPLETE` rows require explicit evidence pointers on accepted main or verified L0 control-plane VPs only.
