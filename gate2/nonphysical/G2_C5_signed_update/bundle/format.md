# Update bundle format v1

```
bundle/
  manifest.json   # version, target, hashes, rollback_min
  payload.bin
  signature.sig   # over canonical manifest+payload hash
```

Adapters: `emulator`, `device_os_capsule`, `ring_firmware`.
