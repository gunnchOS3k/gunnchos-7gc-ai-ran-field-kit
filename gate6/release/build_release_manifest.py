#!/usr/bin/env python3
"""Create DEV-signed release manifest + SBOM stub. Not a production factory image."""
from __future__ import annotations
import argparse, json, hashlib
from pathlib import Path
from datetime import datetime, timezone
def main() -> int:
    ap=argparse.ArgumentParser(); ap.add_argument("--version", default="0.0.0-rc.dev")
    ap.add_argument("--out", type=Path, required=True); args=ap.parse_args()
    digest=hashlib.sha256(b"dev-factory-candidate-bytes").hexdigest()
    manifest={"version":args.version,"created_at":datetime.now(timezone.utc).isoformat(),
      "signature_realm":"DEV","reproducible_build":True,
      "reproducible_hooks":["SOURCE_DATE_EPOCH","locked_toolchains"],
      "artifacts":[{"name":"system_image.dev.bin","sha256":digest,"label":"DEV_SIGNED_NOT_PRODUCTION_FACTORY_IMAGE"}],
      "sbom":"sbom.dev.json","recovery_image":"recovery.dev.bin","rollback_image":"rollback.dev.bin",
      "warning":"Never call DEV-signed artifact a production factory image"}
    sbom={"bomFormat":"CycloneDX","specVersion":"1.5",
          "components":[{"name":"gunnchos-field-kit-gate6","version":args.version,"type":"application"}]}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(manifest, indent=2))
    args.out.with_name("sbom.dev.json").write_text(json.dumps(sbom, indent=2))
    print("wrote", args.out, "realm=DEV"); return 0
if __name__ == "__main__": raise SystemExit(main())
