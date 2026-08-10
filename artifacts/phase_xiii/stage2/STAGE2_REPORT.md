# Phase XIII Stage 2 — Frontier Foundations Evidence Report

**Generated:** 2026-08-10T01:29:05Z  
**Control plane:** `gunnchos-7gc-ai-ran-field-kit` branch `phase-xiii/stage2-frontier-foundations`  
**Doctrine:** `PHYSICAL_EXECUTION_FREEZE=ACTIVE` · DRAFT PRs only · `autoMerge=null` · Cursor never merges  

## Claim correction (MUST remain false)

```text
GUNNCHOS_FRONTIER_OS_PARITY = false
GUNNCHAI_FRONTIER_PRODUCT_PARITY = false
GUNNCHOS3K_FRONTIER_ECOSYSTEM_PARITY = false
```

Individual foundation gates may be `DIGITALLY_VALIDATED`. Full frontier parity is not claimed.

---

## 1. Accepted-main baseline

| Repo | Accepted main SHA |
|---|---|
| gunnchos-device-os | `07c4e8e415c14031b6b797dcf2c8f36ef0ab3fdd` |
| gunnchos-7gc-ai-ran-field-kit | `8e3720ef0669b432994bf85a97f00ba61029f3fa` |
| gunnchAI3k | `0529a9ce57dc335a7f20a87d43157942a7302d51` |

Precondition merges (Edmund): device-os #73/#74, field-kit #48/#49, gunnchAI #27 — see `ACCEPTED_MAIN_BASELINE.json`.

### Owner DRAFT tips (not yet accepted-main)

| Owner | PR | Draft tip SHA | CI |
|---|---|---|---|
| device-os | [#75](https://github.com/gunnchOS3k/gunnchos-device-os/pull/75) | `1cf3c5d6b0c8f6c4b764817eb72f716f073a79ec` | green |
| gunnchAI | [#28](https://github.com/gunnchAI3k/gunnchAI3k/pull/28) | `ddf2a53e37f19fe23844d4857b5cf8a9a65c408c` | green |

Suggested Edmund merge order: **#75 → #28 → this field-kit PR**.

---

## 2. Phase XII X residuals

| Residual | Value | Evidence |
|---|---:|---|
| `REAL_APP_X0_OPEN` | 0 | field-kit main `CI_X1_RESIDUALS.json` |
| `REAL_APP_X1_OPEN` | 0 | same |
| `REAL_APP_X2_OPEN` | 0 | same |

Phase XII Wave 0 closed on accepted mains before Stage 2 started.

---

## 3. FOS gate old → new

| Gate | Old | New |
|---|---|---|
| `UPDATE_ROLLBACK` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `RECOVERY` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `GRAPHICS_COMPOSITOR` | INCOMPLETE_DIGITAL | INCOMPLETE_DIGITAL |
| `DESKTOP_SHELL` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `TOUCH_TABLET_SHELL` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `DUAL_SCREEN_SHELL` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `HANDHELD_SHELL` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `DOCK_TRANSITION` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `APP_RUNTIME` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `APP_COMPATIBILITY` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `SANDBOX_PERMISSIONS` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `BOOT_SECURITY` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `ENCRYPTION_KEYSTORE` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `AI_SYSTEM_API` | INCOMPLETE_DIGITAL | INCOMPLETE_DIGITAL |
| `LOCAL_AI` | INCOMPLETE_DIGITAL | INCOMPLETE_DIGITAL |

**Still INCOMPLETE_DIGITAL:** `GRAPHICS_COMPOSITOR`, `AI_SYSTEM_API`, `LOCAL_AI`.

---

## 4. FAI gate old → new

| Gate | Old | New |
|---|---|---|
| `MODEL_QUALITY` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `MODEL_ROUTING` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `MEMORY` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `PROJECTS` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `WEB_SEARCH` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `DEEP_RESEARCH` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `AGENTS` | INCOMPLETE_DIGITAL | INCOMPLETE_DIGITAL |
| `OS_NATIVE_INTELLIGENCE` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `LOCAL_FIRST` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `SECURITY` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `EVALS` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |

**Still INCOMPLETE_DIGITAL:** `AGENTS`.

---

## 5. FEC gate old → new

| Gate | Old | New |
|---|---|---|
| `SHARED_IDENTITY` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `RESOURCE_AWARE_AI` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |
| `CROSS_PRODUCT_CALLERS` | INCOMPLETE_DIGITAL | INCOMPLETE_DIGITAL |
| `COMPETITIVE_HARNESS` | INCOMPLETE_DIGITAL | **DIGITALLY_VALIDATED** |

**Still INCOMPLETE_DIGITAL:** `CROSS_PRODUCT_CALLERS` — `OS_CALLER_CONTRACT.md` + gunnchAI HTTP `/v1/capability/*` adapter exist; device-os first-party Waike/Device Manager/Creator callers are not yet on a green tip (only reference `ai_interface.sh` stub). Documented incomplete until OS callers land.

---

## 6. OS image architecture

- A/B slots: `/system-a`, `/system-b` under writable Stage 2 sysroot
- Mutable layers: `/apps`, `/games`, `/models`, `/home`, `/data`, `/dev-environments`
- Recovery slot/image + factory reset (explicit confirm) + offline reinstall path
- Reproducible build: `make -C os_build/stage2 image` → `artifacts/stage2/image/`
- Prove: `OS_BASE_IMAGE_REAL=true` on draft tip `1cf3c5d6b0c8f6c4b764817eb72f716f073a79ec`

---

## 7. gunnchShell foundation / profiles / transitions

- Compositor foundation: **Weston** (documented; full `GRAPHICS_COMPOSITOR` parity deferred)
- Profiles: `STUDENT_DESKTOP`, `DSXL_DUAL_SCREEN`, `HANDHELD_GAMEPAD`, `HANDHELD_DOCKED`, `OFFICE_DOCKED`, `TOUCH_TABLET`
- E2E: handheld dock → desktop → undock; DS-XL external attach → detach
- Token: `ADAPTIVE_SHELL_FOUNDATION_REAL=true`

---

## 8. Compatibility runtimes / corpus / results

Lanes: `GUNNCH_NATIVE`, `LINUX_NATIVE`, `FLATPAK`, `WEB_PWA`, `OCI_DEV`, `STEAM_PROTON_USER` (Android evaluate-only / not claimed).

Classifier: `NATIVE` / `VERIFIED` / `PLAYABLE` / `LIMITED` / `UNSUPPORTED` / `UNKNOWN` from execution evidence (honest UNKNOWN when binaries absent).

Corpus sample from OS prove: VERIFIED for available host tools (e.g. LibreOffice/ffmpeg/bash/vim/git when present); UNKNOWN when absent — no fake pass.

Proton/Wine: Steam user-external; wine absent → UNKNOWN.

Token: `COMPATIBILITY_REGISTRY_REAL=true`.

---

## 9. Security / sandbox

- Signed update metadata + anti-rollback simulation
- Sandbox denial/revocation (bwrap or simulated backend)
- Per-user isolation + secret store abstraction
- Modes: `CONSUMER` / `DEVELOPER` / `SECURE_DEVELOPER` — escalation logged and reversible
- Physical TPM/SE RoT: **not claimed** (PHYSICAL_PENDING)

Token: `SANDBOX_FOUNDATION_REAL=true`.

---

## 10. AI model fleet and licenses

Dated matrix: `MODEL_CANDIDATE_MATRIX.md` (2026-08-09).

Roles: `NANO_LOCAL`, `LOCAL_FAST`, `LOCAL_PRO`, `EMBEDDING`, `RERANKER`, optional vision/speech, optional frontier cloud (consent-gated).

135M marked nano/fallback only. Large weights **not** committed — registry + hashes only. Licenses recorded (Apache-2.0 / MIT / provider ToS).

Token: `AI_MULTI_MODEL_FLEET_REAL=true`.

---

## 11. Router policies / fallback

Router covers unavailable / RAM / offline / cloud_denied / cloud_timeout / context_too_large / crash / low_battery / thermal / sensitive-privacy cloud denial.

Token: `AI_ROUTER_DIGITAL_PASS=true`.

---

## 12. Memory implementation / privacy tests

Encrypted gunnchMemory; domains; controls; contradiction resolution; cross-user/cross-project leakage blocked; deleted memories do not reappear; cloud sync rejected without permission.

Token: `AI_MEMORY_DIGITAL_PASS=true`.

---

## 13. Projects persistence / isolation

Wireless Lab E2E: create → files → ask → task → decision → restart → reopen. Two-project isolation with no leakage.

Token: `AI_PROJECTS_DIGITAL_PASS=true`.

---

## 14. Research / citation integrity

Offline local-only marks web unavailable. Fabricated citations fail against controlled local sources.

Token: `AI_CITATION_FOUNDATION_DIGITAL_PASS=true`.

---

## 15. Real first-party AI callers

- **gunnchAI:** Capability HTTP adapter `GET /health`, `GET /v1/capabilities`, `POST /v1/capability/{…}` + permission broker + shared `user_id`
- **Contract:** `OS_CALLER_CONTRACT.md` (copied into field-kit stage2 trees)
- **device-os:** reference `ai_interface.sh` supervised service stub only — **no** Waike/Device Manager/Creator Stage-2 smoke on green tip yet
- FEC `CROSS_PRODUCT_CALLERS` remains `INCOMPLETE_DIGITAL`

Token from AI smoke: `AI_OS_NATIVE_API_INTEGRATED=true` (API + adapter proven in gunnchAI; OS first-party callers still a gap).

---

## 16. Competitive harness initial corpus

≥50 tasks across education/coding/research/office/device/network/archive/privacy with latency/cost/human_score fields.

`BETTER_THAN_*` all remain **false**. FEC `COMPETITIVE_HARNESS` = foundation DIGITALLY_VALIDATED only.

---

## 17. Storage / RAM / performance budgets

See `BUDGETS.json` (`class: digital_reference_only`).

Performance targets (ms): shell_login=3000, profile_switch=1500, model_route=50, memory_lookup=100.

RAM concurrent budgets for Student/DS-XL/Handheld recorded; no silent HW upgrade — open NPI defect if Student SKU insufficient.

---

## 18. Defects found / fixed

Owner repos fixed defects during Stage 2 implementation CI loops prior to this evidence PR. Field-kit consumes green tips `1cf3c5d6b0c8…` and `ddf2a53e37f1…` without amending owner PRs.

---

## 19. Remaining digital gaps

- `GRAPHICS_COMPOSITOR` full parity beyond Weston foundation
- `AI_SYSTEM_API` / `LOCAL_AI` OS-side primitives
- `AGENTS` multi-agent runtime
- `CROSS_PRODUCT_CALLERS` first-party OS → AI callers on a green tip
- Continuity / Play / Fabric / Spatial / MDM / SDK (later stages)
- Competitive BETTER_THAN_* qualification (Stage 5)

---

## 20. Physical / external gaps

- Physical TPM/SE / measured boot / power / RF
- Physical shell usability / performance on EVT/DVT hardware
- External model provider production keys / certifications
- `PHYSICAL_EXECUTION_FREEZE=ACTIVE` unchanged

---

## 21. PRs / CI / auto-merge

| PR | Role | Draft | autoMerge |
|---|---|---|---|
| device-os #75 | OS foundations | yes | null |
| gunnchAI #28 | AI foundations | yes | null |
| field-kit (this) | Evidence LAST | yes | null |

CI: owner Stage 2 workflows green; field-kit `claim-firewall` must PASS locally before push.

**Cursor never merges.**

---

## 22. Exact individual parity gates earned (`DIGITALLY_VALIDATED`)

**OS:** UPDATE_ROLLBACK, RECOVERY, DESKTOP_SHELL, TOUCH_TABLET_SHELL, DUAL_SCREEN_SHELL, HANDHELD_SHELL, DOCK_TRANSITION, APP_RUNTIME, APP_COMPATIBILITY, SANDBOX_PERMISSIONS, BOOT_SECURITY, ENCRYPTION_KEYSTORE  

**AI:** MODEL_QUALITY, MODEL_ROUTING, MEMORY, PROJECTS, WEB_SEARCH, DEEP_RESEARCH, OS_NATIVE_INTELLIGENCE, LOCAL_FIRST, SECURITY, EVALS  

**FEC:** SHARED_IDENTITY, RESOURCE_AWARE_AI, COMPETITIVE_HARNESS  

---

## 23. Stage 2 success tokens

| Token | Value |
|---|---|
| OS_BASE_IMAGE_REAL | true |
| ATOMIC_UPDATE_ROLLBACK_DIGITAL_PASS | true |
| RECOVERY_DIGITAL_PASS | true |
| ADAPTIVE_SHELL_FOUNDATION_REAL | true |
| COMPATIBILITY_REGISTRY_REAL | true |
| SANDBOX_FOUNDATION_REAL | true |
| AI_MULTI_MODEL_FLEET_REAL | true |
| AI_ROUTER_DIGITAL_PASS | true |
| AI_MEMORY_DIGITAL_PASS | true |
| AI_PROJECTS_DIGITAL_PASS | true |
| AI_CITATION_FOUNDATION_DIGITAL_PASS | true |
| AI_OS_NATIVE_API_INTEGRATED | true |
| FRONTIER_PARITY_CLAIM_FIREWALL_PASS | true |

Full frontier parity tokens: **all false**.

---

## 24. Next finite stage recommendation

**Stage 3 — Ecosystem differentiators:** close `CROSS_PRODUCT_CALLERS` with first-party device-os AI callers; deepen compositor; start Continuity / Play / Fabric / local-first OS AI / education-MDM slices with prove artifacts — still without claiming full frontier OS/AI/ecosystem parity.
