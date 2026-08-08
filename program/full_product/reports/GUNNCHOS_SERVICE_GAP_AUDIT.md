# gunnchOS Platform Service Gap Audit

**Audited repo:** `/Users/gunnchos/Downloads/gunnchos-7gc-research-product-spine/repos/gunnchos-device-os`  
**Remote:** `https://github.com/gunnchOS3k/gunnchos-device-os.git`  
**Fetched:** `origin/main` @ `c4d99234989264ec6d8017a328c75005c7df613a`  
**Working tree audited:** branch `cursor/gate1-digital-fabrication` @ `1b9a631ef87f3c8b9b02f3fbad60606ba5b348a9` (3 commits behind `origin/main`)  
**`origin/main` delta vs tree:** only `gate2_nonphysical/update_adapter_bridge.py` (+4-line stub) and its test — included below under OTA.  
**Audit date (UTC):** 2026-08-08T00:08:35Z  

## Status legend

| Status | Meaning |
|--------|---------|
| `DOC_ONLY` | Specs/markdown/YAML intent only; no meaningful executable service |
| `STUB_ONLY` | Executable code exists but returns mock/placeholder/`mock: true` / simulated-only; not a real platform service |
| `IMPLEMENTED` | Real software logic for a slice of the service (not necessarily OS-integrated or production-grade) |
| `INTEGRATED` | Wired across packages (Python policy ↔ shell ↔ config/CI) as a working prototype path |
| `DIGITALLY_VALIDATED` | Automated tests exercise real software behavior on a digital path; **does not** mean physical/hardware validation |

**Honesty rule used here:** modules that self-label `mock: True`, `PLACEHOLDER_*`, `SOFTWARE_SIMULATED`, or `PHYSICAL_*_PENDING` are stubs/simulations even when tested. Tests of stubs do **not** upgrade status past `STUB_ONLY` unless the underlying logic is non-mock (then `DIGITALLY_VALIDATED` is allowed for the software path only).

**Repo self-claim (accepted):** `docs/WHAT_IS_REAL_TODAY.md` — alpha shell + policy yes; beta/RC/GA no; no production secure boot/TPM/MDM/FDE.

---

## Summary scoreboard

| # | Service | Exists? | Kind | Tests? | Status |
|---|---------|---------|------|--------|--------|
| 1 | Unified identity | Partial | Local ID helpers; no SSO/accounts platform | Yes (narrow) | `STUB_ONLY` |
| 2 | HAL | Yes | Profile dicts + stub sensors | Yes (policy/HAL demos) | `STUB_ONLY` |
| 3 | Device-aware UI shell | Yes | React launcher mock + device profiles | Yes (Vitest + pytest) | `INTEGRATED` |
| 4 | Ring input | Yes | Adapter over sibling protocol; simulated evidence | Yes | `DIGITALLY_VALIDATED` |
| 5 | Touch | Partial | Fallback modality + UI targets; no gesture stack | Partial (a11y/UI) | `STUB_ONLY` |
| 6 | Controller | Partial | Policy/remap presets; no HID/SDL layer | Partial | `STUB_ONLY` |
| 7 | Keyboard/mouse | Partial | Fallback modalities + a11y checklists | Partial | `STUB_ONLY` |
| 8 | Voice | Placeholder | Config flag / docs only | No service tests | `DOC_ONLY` |
| 9 | Display manager | Name only | Boot manifest service string; no DM process | Probe tests only | `STUB_ONLY` |
| 10 | Dock manager | Yes | Continuity engine + stub state API | Yes | `DIGITALLY_VALIDATED` |
| 11 | Cross-device session continuity | Partial | Dock session snapshot/restore (simulated) | Yes | `IMPLEMENTED` |
| 12 | Secure app packaging | Partial | App packs YAML + mock deploy contract | Yes (contract/pack) | `STUB_ONLY` |
| 13 | Permissions | UI label | Settings text; no permission manager | No | `STUB_ONLY` |
| 14 | Local AI runtime integration | Stub | Mock tutor session; UI shell | Yes (mock module) | `STUB_ONLY` |
| 15 | Connectivity orchestration | Partial | QoS presets + network policy checks | Yes (QoS/policy) | `STUB_ONLY` |
| 16 | Offline sync | Stub | Offline capability map; LWW placeholder | Yes (offline manager) | `STUB_ONLY` |
| 17 | Encrypted storage | Prototype | Browser Web Crypto AES-GCM (not OS FDE) | Yes (Vitest) | `DIGITALLY_VALIDATED` |
| 18 | Secure/measured boot | Docs + probe observe | Architecture/checklist; probe does not verify | Partial | `STUB_ONLY` |
| 19 | Attestation | Docs only | Checklist / future MDM export | No | `DOC_ONLY` |
| 20 | OTA / rollback / recovery | Stub/sim | Mock updater/rollback; capsule sim; recovery playbook | Yes | `STUB_ONLY` |
| 21 | Fleet agent | Prototype | Local static MDM policy agent | Yes | `IMPLEMENTED` |
| 22 | Sandboxing | Missing | Explicitly not implemented | No | `DOC_ONLY` |
| 23 | Logging / diagnostics | Stub | In-memory redacted mock event log | Yes | `STUB_ONLY` |
| 24 | Accessibility | Prototype | Settings + manager + compliance docs | Yes | `INTEGRATED` |
| 25 | Parental/student/educator/admin profiles | Prototype | Profile enums + guardian/school policy | Yes | `IMPLEMENTED` |
| 26 | Developer mode | Policy | Mode YAML + docs + WSL mock | Yes (modes) | `STUB_ONLY` |

**Counts:** `DOC_ONLY` 2 · `STUB_ONLY` 15 · `IMPLEMENTED` 3 · `INTEGRATED` 2 · `DIGITALLY_VALIDATED` 4  

No service reaches production OS integration. Highest digital maturity: ring adapter, dock continuity simulation, encrypted browser workspace, device-aware shell.

---

## Per-service detail

### 1. Unified identity

| Field | Finding |
|-------|---------|
| **Exists?** | Partial |
| **Paths** | `gunnchos_device_os/identity.py`; `src/gunnchos_core/device_identity.py`; shell `apps/launcher_mock/src/data/studentProfile.ts`; `apps/launcher_mock/src/hooks/useLocalStorage.ts` |
| **Real vs stub** | `identity.py` is real local helpers (device/session/boot IDs, SHA-256, host fingerprint) for Gate 1 evidence — **not** unified identity (no SSO, no cross-device account, no credential provider). `device_identity.py` hardcodes `"student_14_5"`. Shell profile is browser `localStorage`. |
| **Tests?** | Yes — `tests/test_gate1_identity.py` |
| **Status** | `STUB_ONLY` (relative to required *unified* identity platform) |

### 2. HAL (hardware abstraction layer)

| Field | Finding |
|-------|---------|
| **Exists?** | Yes (thin) |
| **Paths** | `gunnchos_device_os/hardware_abstraction.py`; `src/hardware_abstraction/{battery,thermal}.py`; `gunnchos_device_os/hardware_*_policy.py`; `gunnchos_device_os/hardware_capability_detector.py`; `firmware_compat/probes/*` |
| **Real vs stub** | Device profiles are static dicts. Battery returns `87.0` stub; thermal returns `42.0` stub. Capability/policy engines evaluate YAML manifests in software. Firmware probes are host-observation / harness — not a production HAL. |
| **Tests?** | Yes — `tests/test_hardware_*`, `tests/test_firmware_probe.py`, `tests/test_os_modules.py` |
| **Status** | `STUB_ONLY` |

### 3. Device-aware UI shell

| Field | Finding |
|-------|---------|
| **Exists?** | Yes |
| **Paths** | `apps/launcher_mock/src/shell/GunnchOSShell.tsx`; `CampusMode.tsx`, `GameMode.tsx`, `MediaMode.tsx`, `FirstBootFlow.tsx`; `apps/launcher_mock/src/deviceProfiles.ts`; `src/gunnchos_launcher/device_profile.py`; `gunnchos_device_os/device_classes.py`; contract export `scripts/export_launcher_contract.py` |
| **Real vs stub** | Real React shell prototype with onboarding, mode bar, device profile awareness, policy enforcement service. Explicitly a **launcher mock**, not a compositor/OS shell. Policy + contract bridge Python→TS is real for the prototype path. |
| **Tests?** | Yes — Vitest under `apps/launcher_mock/src/services/*.test.ts`; pytest `tests/test_launcher*.py`, `tests/test_device_profiles.py` |
| **Status** | `INTEGRATED` |

### 4. Ring input

| Field | Finding |
|-------|---------|
| **Exists?** | Yes |
| **Paths** | `ring_input/adapter.py`; `ring_input/fallback_input.py`; `ring_input/STATUS.yaml`; `ring_input/README.md`; depends on sibling `gunnchos-hardware-industrial-design/ring_input/python` |
| **Real vs stub** | Adapter has real authenticated receive → OS action mapping. `STATUS.yaml`: `evidence_class: SOFTWARE_SIMULATED`, `physical_ring_claimed: false`. Not a physical ring driver. |
| **Tests?** | Yes — `tests/test_ring_input_adapter.py` |
| **Status** | `DIGITALLY_VALIDATED` (software-simulated path only) |

### 5. Touch

| Field | Finding |
|-------|---------|
| **Exists?** | Partial |
| **Paths** | `ring_input/fallback_input.py` (lists `"touch"`); `compliance/accessibility/CONTROLLER_TOUCH_NOTES.md`; shell touch targets in React; `gunnchos_device_os/accessibility_manager.py` (`touch_navigation`); dock `input_map` defaults |
| **Real vs stub** | No OS gesture/touchstack, no multi-touch dispatcher. Browser/React hit targets only. Gap matrix itself labels controller/touch as mock/prototype. |
| **Tests?** | Indirect a11y/UI only |
| **Status** | `STUB_ONLY` |

### 6. Controller

| Field | Finding |
|-------|---------|
| **Exists?** | Partial |
| **Paths** | `gunnchos_device_os/input_mapper.py`; `gunnchos_device_os/hardware_input_policy.py`; `config/hardware_input_matrix.yaml`; Game Mode UI labels; `compliance/accessibility/CONTROLLER_TOUCH_NOTES.md` |
| **Real vs stub** | `input_mapper.py` returns remap presets with `"mock": True`. No evdev/SDL/Bluetooth gamepad stack. |
| **Tests?** | Partial via hardware input policy / os_modules |
| **Status** | `STUB_ONLY` |

### 7. Keyboard / mouse

| Field | Finding |
|-------|---------|
| **Exists?** | Partial |
| **Paths** | `ring_input/fallback_input.py` (`keyboard`, `trackpad`); `compliance/accessibility/KEYBOARD_NAVIGATION_CHECKLIST.md`; device profiles declare keyboard presence; ring maps key events when protocol present |
| **Real vs stub** | No HID ownership, no OS input daemon. Fallback modality list + checklists + profile flags. Ring path can map authenticated key events in software tests only. |
| **Tests?** | Checklist docs + ring adapter tests (key events via protocol) |
| **Status** | `STUB_ONLY` |

### 8. Voice

| Field | Finding |
|-------|---------|
| **Exists?** | Placeholder only |
| **Paths** | `gunnchos_device_os/accessibility_manager.py` (`voice_input` feature name); `config/accessibility_defaults.yaml`; `requirements/ACCESSIBILITY_REQUIREMENTS.md` (“planned”); `docs/USER_FOCUSED_OS_LIMITATIONS.md`; `gunnchos_device_os/hardware_profile.py` (`voice_placeholder`) |
| **Real vs stub** | Explicit placeholder; no ASR/TTS runtime, no mic pipeline. |
| **Tests?** | No voice service tests |
| **Status** | `DOC_ONLY` |

### 9. Display manager

| Field | Finding |
|-------|---------|
| **Exists?** | Name reference only |
| **Paths** | Boot manifest services entry `display-manager` in `config/boot/sample_manifest.json` / tests; `gunnchos_device_os/boot/failure_injection.py` can omit it; `gunnchos_device_os/hardware_display_policy.py` (profile size checks); shell Settings “Display” tab (a11y toggles) |
| **Real vs stub** | **No** Wayland/X11/Weston/GNOME display manager implementation. Probe observes `DISPLAY`/`WAYLAND_DISPLAY` env only. |
| **Tests?** | Boot probe tests reference the service name |
| **Status** | `STUB_ONLY` |

### 10. Dock manager

| Field | Finding |
|-------|---------|
| **Exists?** | Yes |
| **Paths** | `gunnchos_device_os/dock_manager.py`; `gunnchos_device_os/dock/{continuity,simulator,collector,validator,capabilities,cli}.py`; `config/dock/*`; `docs/gate1/DOCK_CONTINUITY.md`; `gate1_digital_fabrication/dock/*` |
| **Real vs stub** | Continuity engine is real in-process state machine (attach/detach, layout profiles, snapshots). `dock_manager.dock_state()` is an explicit stub (`PHYSICAL_DOCK_EVIDENCE_PENDING`). Physical dock not claimed. |
| **Tests?** | Yes — `tests/test_gate1_dock_continuity.py` |
| **Status** | `DIGITALLY_VALIDATED` (simulation / software continuity; not physical dock) |

### 11. Cross-device session continuity

| Field | Finding |
|-------|---------|
| **Exists?** | Partial (dock-scoped) |
| **Paths** | `gunnchos_device_os/dock/continuity.py` (`snapshot_session`, restore/degraded undock); `docs/gate1/DOCK_CONTINUITY.md`; `apps/launcher_mock/src/FleetView.tsx` (UI, not sync fabric) |
| **Real vs stub** | Session snapshot/restore logic exists for dock cycles in software. No multi-device account sync, no cloud continuity bus, no peer device handoff. |
| **Tests?** | Yes — dock continuity tests |
| **Status** | `IMPLEMENTED` (dock simulation scope only; not product-wide continuity) |

### 12. Secure app packaging

| Field | Finding |
|-------|---------|
| **Exists?** | Partial |
| **Paths** | `gunnchos_device_os/app_pack_manager.py`; `config/app_packs.yaml`; `gunnchos_device_os/deploy_contract.py` (`mock: True`, rollback placeholder); `docs/APP_PACKS_AND_WORKSPACES.md`; `docs/software_supply_chain.md`; SBOM `scripts/generate_sbom.py` |
| **Real vs stub** | App packs are curated YAML bundles. Deploy contract is mock transport/safety model. No signed app container format, no store, no verified install pipeline. SBOM generation is a separate prototype. |
| **Tests?** | Yes — `tests/test_app_pack_manager.py`, `tests/test_deploy_contract.py`, `tests/test_sbom_generation.py` |
| **Status** | `STUB_ONLY` |

### 13. Permissions

| Field | Finding |
|-------|---------|
| **Exists?** | UI label / docs |
| **Paths** | `apps/launcher_mock/src/shell/SettingsPanel.tsx` (`App permissions` → `"Per-app sandbox"` static text); `docs/FULL_OPERATIONAL_GAP_MATRIX.md` (app permissions = mock); access-risk docs under `security/access-risk/` (IAM demo model, not device permissions) |
| **Real vs stub** | No permission manager, no grant/deny API, no sensor indicators backed by OS. |
| **Tests?** | No |
| **Status** | `STUB_ONLY` |

### 14. Local AI runtime integration

| Field | Finding |
|-------|---------|
| **Exists?** | Stub |
| **Paths** | `gunnchos_device_os/gunnchai_integration.py`; `src/gunnchos_launcher/gunnchai_bridge.py`; shell AI panel references; `docs/13_OFFLINE_FIRST_AND_LOCAL_AI.md`; `docs/issues/P1-ai-assistant-backend.md`; `gunnchos_device_os/waike_integration.py` |
| **Real vs stub** | `tutor_session_start` / safety check return `"mock": True`. No local model runtime (no Ollama/ONNX/llama.cpp binding), no IPC to gunnchAI3k process. |
| **Tests?** | Yes for mock modules (`tests/test_waike_integration.py`, launcher bridges) — not a runtime |
| **Status** | `STUB_ONLY` |

### 15. Connectivity orchestration

| Field | Finding |
|-------|---------|
| **Exists?** | Partial |
| **Paths** | `src/gunnchos_launcher/qos_policy.py`; `docs/05_CONNECTIVITY_AND_QOS.md`; `gunnchos_device_os/hardware_network_policy.py`; `firmware_compat/probes/network_probe.py`; MDM sample policies network fields; Settings Network tab (mock stats) |
| **Real vs stub** | QoS module is conceptual presets (“OS integration future work”). Network policy checks profile flags. No Wi-Fi/BT/cellular orchestrator, no captive portal, no multipath manager. |
| **Tests?** | Yes — `tests/test_qos_policy.py`, hardware network policy tests |
| **Status** | `STUB_ONLY` |

### 16. Offline sync

| Field | Finding |
|-------|---------|
| **Exists?** | Stub |
| **Paths** | `gunnchos_device_os/offline_mode_manager.py`; shell offline toggles / `OfflineModePanel` (if present via campus mode); `docs/OFFLINE_FIRST_USER_EXPERIENCE.md`; Settings cloud backup mock labels |
| **Real vs stub** | Capability map with `write_placeholder` apps and `conflict_handling: placeholder_last_write_wins`, `"mock": True`. No sync engine, no CRDT/queue, no conflict UI. |
| **Tests?** | Covered via offline/mode user-focused tests |
| **Status** | `STUB_ONLY` |

### 17. Encrypted storage

| Field | Finding |
|-------|---------|
| **Exists?** | Browser prototype |
| **Paths** | `apps/launcher_mock/src/services/workspaceCrypto.ts`; `encryptedWorkspaceStore.ts`; `EncryptedWorkspacePanel.tsx`; `docs/PHASE4A_ENCRYPTED_WORKSPACE.md`; `docs/STORAGE_SECURITY_BOUNDARY.md` |
| **Real vs stub** | Real Web Crypto PBKDF2 + AES-GCM for notes/workspace in `localStorage` — **not** OS full-disk encryption, not keyed to TPM. Repo claim boundary is explicit. |
| **Tests?** | Yes — `apps/launcher_mock/src/services/encryptedWorkspace.test.ts` |
| **Status** | `DIGITALLY_VALIDATED` (browser prototype scope only) |

### 18. Secure / measured boot

| Field | Finding |
|-------|---------|
| **Exists?** | Docs + observation hook |
| **Paths** | `security/secure_boot/{ARCHITECTURE,CLAIM_BOUNDARY,SECURE_BOOT_CHECKLIST}.md`; `docs/PHASE4D_SECURE_BOOT_MDM.md`; `docs/security/SECURE_BOOT_ARCHITECTURE.md`; `gunnchos_device_os/boot/probe.py` (`_secure_boot_state` — exposed EFI vars, `verified: False`); `scripts/generate_dev_signing_keys.sh`; `scripts/sign_release_manifest.py` |
| **Real vs stub** | Architecture/checklist/dev signing tooling. Claim boundary forbids production secure boot / TPM measured boot claims. Probe does not attest. |
| **Tests?** | Yes — `tests/test_secure_boot_mdm.py`, `tests/test_gate1_boot_probe.py` (software boot path) |
| **Status** | `STUB_ONLY` |

### 19. Attestation

| Field | Finding |
|-------|---------|
| **Exists?** | Documentation / checklist only |
| **Paths** | `security/secure_boot/SECURE_BOOT_CHECKLIST.md` (attestation ↔ MDM future); `security/secure_boot/ARCHITECTURE.md`; `os_build/*/ARTIFACT_MANIFEST.md` “not claimed” lines |
| **Real vs stub** | No PCR quotes, no attestation agent, no verifier. Boot probe explicitly “not attested measured boot.” |
| **Tests?** | No |
| **Status** | `DOC_ONLY` |

### 20. OTA / rollback / recovery

| Field | Finding |
|-------|---------|
| **Exists?** | Stub / simulation |
| **Paths** | `gunnchos_device_os/updater.py` (placeholder signature); `gunnchos_device_os/rollback.py` (`mock: True`); `gunnchos_device_os/boot/recovery.py` (playbook strings); `firmware_compat/compatibility/capsule_update_client.py` (refuses non-simulated; never flashes); `origin/main` `gate2_nonphysical/update_adapter_bridge.py` (4-line NONPHYSICAL adapter list); `docs/security/OTA_UPDATE_SECURITY.md`; `physical_evidence/os_validation/UPDATE_ROLLBACK_CHECKLIST.md` |
| **Real vs stub** | All update/rollback paths are mock or simulated. Recovery is instructional playbook, not a recovery partition/image. |
| **Tests?** | Yes — `tests/test_updater_rollback.py`, `tests/test_update_manifest.py`, `tests/test_capsule_update_client.py`, `tests/test_gate2_update_adapter_bridge.py` (on `origin/main`) |
| **Status** | `STUB_ONLY` |

### 21. Fleet agent

| Field | Finding |
|-------|---------|
| **Exists?** | Local prototype |
| **Paths** | `mdm/device_policy_agent.py`; `mdm/policy_schema.yaml`; `mdm/sample_policies/{school_default,library_session,guardian_home}.json`; `mdm/enrollment_profile.example.json`; `mdm/CLAIM_BOUNDARY.md`; `src/gunnchos_launcher/school_fleet_policy.py` (stub); shell `FleetView.tsx` |
| **Real vs stub** | Real local JSON policy load/validate/allow-deny decisions. **Not** production MDM: no remote server, enrollment, heartbeat, wipe/lock. Claim boundary is explicit. |
| **Tests?** | Yes — `tests/test_secure_boot_mdm.py` |
| **Status** | `IMPLEMENTED` |

### 22. Sandboxing

| Field | Finding |
|-------|---------|
| **Exists?** | No implementation |
| **Paths** | Mentions in `beta_gate/beta_gate_status.yaml` (`Native sandbox not implemented`); `docs/MOCK_RETIREMENT_PLAN.md`; mode docs; Settings static “Per-app sandbox” string |
| **Real vs stub** | Absent. No seccomp/namespaces/Flatpak/bubblewrap/app confinement. |
| **Tests?** | No |
| **Status** | `DOC_ONLY` |

### 23. Logging / diagnostics

| Field | Finding |
|-------|---------|
| **Exists?** | Stub |
| **Paths** | `gunnchos_device_os/security_event_log.py`; `gunnchos_device_os/device_health.py` (EVT-1 alpha mock metrics); `src/gunnchos_launcher/telemetry_contract.py`; boot probe evidence collectors |
| **Real vs stub** | In-memory event list with `"mock": True`. Device health returns mock metrics. Telemetry contracts are synthetic. Boot/dock collectors produce software evidence JSON — useful for Gate 1, not a diagnostics platform. |
| **Tests?** | Yes — `tests/test_security_event_log.py`, boot/dock evidence tests |
| **Status** | `STUB_ONLY` |

### 24. Accessibility

| Field | Finding |
|-------|---------|
| **Exists?** | Prototype |
| **Paths** | `gunnchos_device_os/accessibility_manager.py`; `gunnchos_device_os/accessibility.py` (tiny stub defaults); `config/accessibility_defaults.yaml`; shell Settings a11y toggles + `accessibilityAudit.ts`; `compliance/accessibility/*`; `docs/ACCESSIBILITY_BETA_BASELINE.md` |
| **Real vs stub** | Real settings merge/validate + shell class application. Not WCAG-certified; no screen-reader integration on device; voice/switch access placeholders. |
| **Tests?** | Yes — `tests/test_accessibility_manager.py`; `apps/launcher_mock/src/services/accessibility.test.ts` |
| **Status** | `INTEGRATED` (prototype shell + policy; not hardware-validated) |

### 25. Parental / student / educator / admin profiles

| Field | Finding |
|-------|---------|
| **Exists?** | Prototype |
| **Paths** | `gunnchos_device_os/profile_manager.py`; `gunnchos_device_os/parental_controls.py`; `gunnchos_device_os/guardian_controls.py`; `gunnchos_device_os/guardian_policy.py`; `gunnchos_device_os/user_profile_schema.py`; `config/personas.yaml`; shell `studentProfile.ts` + guardian/school mode; MDM sample policies |
| **Real vs stub** | Profile role matrix and mode transition rules are real policy code. Parental/guardian APIs largely return `"mock": True`. Enforcement is shell/UI + Python policy — not kernel/MDM remote. |
| **Tests?** | Yes — `tests/test_profile_manager.py`, `tests/test_parental_controls.py`, `tests/test_guardian_*.py`, `tests/test_user_profile_schema.py` |
| **Status** | `IMPLEMENTED` |

### 26. Developer mode

| Field | Finding |
|-------|---------|
| **Exists?** | Policy / docs |
| **Paths** | `docs/DEVELOPER_MODE.md`; `docs/15_DEVELOPER_MODE_AND_DEPLOY_PIPELINE.md`; `config/modes.yaml` Developer mode; `gunnchos_device_os/mode_manager.py` / `mode_policy.py`; `gunnchos_device_os/wsl_dev_tools.py` (mock detection); `configs/modes/developer.yaml`; shell `devMode` prop |
| **Real vs stub** | Mode allowlists and transition gates exist. No real toolchain container, no package manager integration, WSL checklist is mock. |
| **Tests?** | Yes — mode/policy tests (`tests/test_modes.py`, `tests/test_mode_policy.py`) |
| **Status** | `STUB_ONLY` |

---

## Related boot / image reality (context, not a listed service)

| Area | Reality |
|------|---------|
| Boot probe software path | `gunnchos_device_os/boot/*` — real probe/evidence/recovery playbook; status tokens keep `GUNNCHOS_PHYSICAL_BOOT_PENDING` |
| Installable image | `os_build/installable_image/` — tarball/policy bundle prototype; **not** bootable ISO/IMG |
| Container kiosk | `os_build/linux_desktop/` Docker prototype |
| Gap matrix (upstream) | `docs/FULL_OPERATIONAL_GAP_MATRIX.md` — aligns with this audit |

---

## Highest-priority gaps for FULL PRODUCT

1. **Sandboxing + permissions** — absent; Settings labels are fiction.  
2. **Unified identity** — local hashes ≠ accounts/SSO/cross-device identity.  
3. **Display manager + real input stacks** (touch/controller/keyboard/voice) — names/policies only.  
4. **Secure/measured boot + attestation + production OTA/rollback** — docs and mocks.  
5. **Local AI runtime** — mock session objects only.  
6. **Connectivity orchestration + offline sync** — presets/placeholders.  
7. **Fleet agent** — local JSON only; no remote fleet.  
8. **Secure app packaging** — YAML packs + mock deploy, not signed installable apps.

---

## Method notes

- Walked `gunnchos_device_os/`, `ring_input/`, `mdm/`, `security/`, `apps/launcher_mock/`, `firmware_compat/`, `os_build/`, `docs/`, `tests/`.  
- Treated self-declared `mock` / `PLACEHOLDER` / `SOFTWARE_SIMULATED` / claim-boundary docs as authoritative.  
- Did **not** claim physical validation for any service; Gate 1 physical captures remain pending per repo tokens.  
- `origin/main` was fetched; audit tree is 3 commits behind (gate2 4-line bridge only).
