# Physical / External Evidence Automation Packets

These packets are **automation-complete runbooks only**. Execution remains pending.

## Semantics

| Status | Meaning |
|---|---|
| `AUTOMATION_COMPLETE` | Runbook, schemas, validators, and capture commands exist |
| `PHYSICAL_EXECUTION_PENDING` | Requires hardware / RF / participants |
| `EXTERNAL_EXECUTION_PENDING` | Requires reviewers, partners, DOI service, or admin |

Never convert a dry-run into PASS.

---

## 1. NVIDIA GPU lab

**Automation:** `AUTOMATION_COMPLETE` (in `gunnchos-gpu-nr-baseband-platform` targets)  
**Execution:** `PHYSICAL_EXECUTION_PENDING` / `BLOCKED_HARDWARE` / `BLOCKED_GPU_RUNNER`

Commands (on GPU host):

```bash
make cuda-build
make cuda-correctness
make cuda-equivalence
make optimization-study-gpu
make nsight
```

Required artifacts: device info, correctness manifests, Nsight Systems/Compute reports, deadline percentiles — no numeric GPU results without `nvidia-smi`.

---

## 2. NIC / PTP lab

**Automation:** schemas + dry-run under Gate 6  
**Execution:** `PHYSICAL_EXECUTION_PENDING`

Capture: NIC model, driver/firmware, PTP sync state, timestamps, PCAP, latency/jitter, invalid-clock detection.

---

## 3. SDR / RU lab

**Automation:** FAPI/RU emulator + Gate 6 fixtures  
**Execution:** `PHYSICAL_EXECUTION_PENDING` (+ RF safety)

No unauthorized RF transmission.

---

## 4. Independent reproduction

**Automation:** clean-clone reproduce targets + reviewer forms  
**Execution:** `EXTERNAL_EXECUTION_PENDING` / `BLOCKED_EXTERNAL_REVIEWER`

Author reproduction ≠ independent reproduction.

---

## 5. User / customer trial

**Execution:** `BLOCKED_ETHICS_APPROVAL` / `BLOCKED_PARTICIPANT_RECRUITMENT` / `BLOCKED_CUSTOMER_PARTNER`

Consent, minimization, approved protocol required before any participant data.

---

## 6. Publication services

DOI / Zenodo / visibility: `BLOCKED_USER_APPROVAL` / `BLOCKED_PUBLICATION_SERVICE`
