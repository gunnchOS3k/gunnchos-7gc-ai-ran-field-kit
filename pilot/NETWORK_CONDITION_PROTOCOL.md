# Network Condition Protocol

## Safety

- Never apply shaping automatically.
- Require explicit operator command and privilege check.
- Always support `--dry-run`.
- Trap interrupts and restore interface.
- Log before/after state.
- Reject unverified impairment.

## Linux primary path

```bash
./pilot/scripts/apply_condition.sh --condition wifi_degraded --interface eth0 --dry-run
./pilot/scripts/apply_condition.sh --condition wifi_degraded --interface eth0
./pilot/scripts/verify_condition.sh --condition wifi_degraded --interface eth0
./pilot/scripts/restore_condition.sh --interface eth0
```

macOS/Windows: document platform-specific guarded alternatives; prefer a Linux shaping host or lab gateway when available.
