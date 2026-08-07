# Dev key hierarchy

- `root_dev` — offline root (test only)
- `boot_dev` — signs boot images
- `update_dev` — signs OTA capsules

Never commit private production keys. Fixtures use generated ephemeral keys in tests.
