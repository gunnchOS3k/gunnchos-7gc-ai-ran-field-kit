# DR-0004 — Ring Workstream Ownership

## Decision
Document cross-repo responsibility for Edge I/O Rings across industrial/electrical design, firmware, sensing/inference, secure pairing, gunnchOS input service, calibration, haptics, SDK, game integration, measurement, privacy, safety, and manufacturing.

## Workstream matrix (ownership ≠ existence)

| Workstream | Accountable owner | Supporting | Notes |
|---|---|---|---|
| Industrial / electrical design | `gunnchos-hardware-industrial-design` | EdgeGesture, edge-io-measurement-node | No production ring claim |
| Ring firmware | `CONTROL_PLANE_PENDING_DECISION` | hardware-industrial-design, EdgeGesture | No dedicated firmware repo proven |
| Sensing and inference | `EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon` | edge-io-measurement-node, gunnchAI3k | Research / hackathon provenance |
| Secure pairing and authentication | `gunnchos-device-os` | EdgeGesture | Anti-replay / pairing / revocation |
| gunnchOS input service | `gunnchos-device-os` | EdgeGesture | OS-side input routing |
| Calibration | `EdgeGesture-Fall-2025-Edge-AI-Qualcomm-Hackathon` | edge-io-measurement-node, device-os | Per-user / per-surface |
| Haptics | `CONTROL_PLANE_PENDING_DECISION` | EdgeGesture, hardware-industrial-design | No validated haptics stack claimed |
| Application SDK | `gunnchos-device-os` | games, EdgeGesture | Pending dedicated SDK package |
| Game integration | per-game repos | EdgeGesture, device-os | Optional gestures only |
| Measurement and validation | `edge-io-measurement-node` | field-kit, EdgeGesture | Lab / field measurement |
| Privacy | `gunnchos-device-os` | EdgeGesture, gunnchAI3k | Local motion processing / consent |
| Safety | `gunnchos-device-os` | EdgeGesture | No silent destructive actions |
| Manufacturing | `CONTROL_PLANE_PENDING_DECISION` | hardware-industrial-design | No manufacturer engaged |

## Status
DOCUMENTED in this decision record and applied via `control_plane.generate.apply_ring_workstream_ownership`.

## Critical disclaimer
Ownership assignment does **not** claim that a dedicated production ring repository, manufactured ring, or validated firmware exists.
