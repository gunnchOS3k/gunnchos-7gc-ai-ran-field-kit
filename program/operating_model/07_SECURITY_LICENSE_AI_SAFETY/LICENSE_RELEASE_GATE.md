# License Release Gate

Before Beta/RC/manufacturing release, every distributable component needs an explicit license determination.

Cover:
- source/binaries
- Linux/kernel
- Flatpak/apps
- Wine/Proton-related pieces
- Godot/plugins
- llama.cpp and AI runtimes
- model weights
- datasets/scientific data
- media/codecs/fonts/icons/art
- Matrix/WebRTC/messaging
- drivers/firmware

For each record:
license, attribution, redistribution/commercial rights, copyleft/source obligations, patent/codec concerns, model restrictions, distribution restrictions.

Statuses:
- CLEAR
- CLEAR_WITH_OBLIGATIONS
- REVIEW_REQUIRED
- BLOCKED

No release ships with BLOCKED or critical unresolved REVIEW_REQUIRED.
