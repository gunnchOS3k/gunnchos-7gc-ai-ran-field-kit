# FAILED_EXPORT_ATTEMPT_REPORT

1. Measurement completed on Pixel 6a (run `pixel-cal-1784755600830`, ~60.6s, 13 samples).
2. JSON was written to app `cache/pixel-cal-1784755600830.json` before FileProvider failed.
3. Android share export failed with toast: Couldn't find meta-data for provider with authority org.gu...
4. Session recovered via `adb exec-out run-as org.gunnchos.edgeio.debug cat cache/pixel-cal-1784755600830.json` into ignored local raw storage.
5. Root cause: FileProvider authority mismatch (`$packageName.files` vs `${applicationId}.provider`).
6. App cache file left untouched after pull.
7. Schema validation does not accept this export as physical evidence while consent.status=`withdrawn` and producer.commit is non-SHA.
8. Raw/sanitized measurement JSON not committed.
