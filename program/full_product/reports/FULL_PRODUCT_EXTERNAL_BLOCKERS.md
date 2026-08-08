# FULL PRODUCT EXTERNAL BLOCKERS

Updated: 2026-08-08T00:50:00Z

See `../external_blockers.yaml`.

## EDMUND_ACTION_REQUIRED

```
EDMUND_ACTION_REQUIRED: Approve the macOS administrator/install prompt for KiCad.
```

Wave A2 (`cursor/full-product-wave-a2-hardware-depth`): `kicad-cli` **ABSENT**. Ring ERC/DRC/Gerber CLI deferred; digital depth shipped without hanging. No fab.

Also may need:

```
sudo chown -R $(whoami) /opt/homebrew /Users/gunnchos/Library/Logs/Homebrew
```

Then Cursor continues immediately to `RING_KICAD_CLI_VALIDATION_PASS`.
