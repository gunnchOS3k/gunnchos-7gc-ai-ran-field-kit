# Edge Console Protocol

Phone-first logging plan and schema:

- [TELEMETRY_SCHEMA.md](https://github.com/gunnchOS3k/edge-io-measurement-node/blob/main/docs/TELEMETRY_SCHEMA.md)
- [ANDROID_FIELD_CONSOLE_ROADMAP.md](https://github.com/gunnchOS3k/edge-io-measurement-node/blob/main/docs/ANDROID_FIELD_CONSOLE_ROADMAP.md)

## MVP workflow

1. Present consent UI → set `consent_flag`
2. Collect probe dicts from `src/edge_io_node/probes/`
3. Merge into telemetry record; validate via `TelemetrySample`
4. Export CSV locally (offline-first)
5. Optional: sanitize → 7GC export JSON

## Test

```bash
cd edge-io-measurement-node
make test
```

## Non-claims

Web/APK console is **planned**; Python probes + synthetic emulator are today's reproducible path.
