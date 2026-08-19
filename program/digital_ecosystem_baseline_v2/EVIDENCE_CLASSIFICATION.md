# Evidence Classification (Baseline V2)

| Class | Meaning |
| --- | --- |
| E0 | Document-only / charter |
| E1 | Unit or schema test on accepted main |
| E2 | Integrated CI PASS on accepted main |
| E3 | Cross-repo reproduction harness |
| E4 | Independent VP artifact with explicit negative space |

Five-pass search precedence: exact ID → tokens → traceability maps → implementation paths → verification tests.
