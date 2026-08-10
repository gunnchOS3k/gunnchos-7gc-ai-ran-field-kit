# Evidence Levels

| Level | Meaning |
|---|---|
| E0 | Requirement/design only |
| E1 | Implementation exists |
| E2 | Component/unit test |
| E3 | Integrated automated execution |
| E4 | Independent digital verification |
| E5 | Actual target-hardware validation |
| E6 | Human/user validation |
| E7 | External lab/vendor/carrier validation |
| E8 | Production/field evidence |

Rules:
- `DIGITALLY_VALIDATED` normally requires E3.
- High-risk V1 requirements require E4.
- Physical claims require E5.
- UX preference/usability requires E6.
- certification/carrier claims require E7.
- operational reliability requires E8.
