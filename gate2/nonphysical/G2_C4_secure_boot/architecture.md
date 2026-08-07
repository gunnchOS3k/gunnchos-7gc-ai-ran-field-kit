# Root of Trust architecture (NONPHYSICAL)

```
OTP/RoT pubkey hash
   └─ ROM bootloader verifies BL1
        └─ BL1 verifies BL2 / bootloader
             └─ bootloader verifies kernel+dtb+initramfs (signed)
                  └─ OS verifies signed update capsules
```

Dev keys only. Production HSM keys: REQUIRES_MANUFACTURER / PHYSICAL_PENDING.
Rollback: anti-rollback counter monotonic; emulator enforces.
