# Configuration Management

Every physical build/release candidate has a named immutable configuration.

Examples:
- gunnchOS3k-EVT0-1.0
- gunnchOS3k-EVT0-1.1
- gunnchOS3k-EVT1-1.0

Pin:
- five hardware revisions
- firmware SHAs
- gunnchOS/gunnchAI/game/WAIKE SHAs
- factory/recovery hashes
- BOM/CAD/PCB/test-book revisions

Once a physical build is authorized, nothing changes silently. Any change creates a new configuration revision and revalidation scope.
