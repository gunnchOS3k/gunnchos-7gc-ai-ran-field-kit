"""Scaffold a new R6G-style adoption package (digital-only; no SoA claims)."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PKG_ROOT = ROOT / "research" / "r6g" / "adoption" / "packages"

TEMPLATE_FILES = {
    "PROBLEM.md": "# Problem\n\n{title}: falsifiable digital hypothesis under R6G doctrine.\n",
    "METHOD.md": "# Method\n\nSeeded digital experiment. Document RNG seeds before analysis.\n",
    "METRICS.md": "# Metrics\n\nDefine primary metric, negatives, and ablations before running.\n",
    "FAILURE_MODES.md": "# Failure modes\n\nList conditions where the method must lose or show no-gain.\n",
    "LIMITATIONS.md": "# Limitations\n\nSynthetic channel only. PHYSICAL_REPRODUCTION_PENDING.\n",
    "REPRODUCTION.md": "# Reproduction\n\n`make r6g-reproduce`\n",
    "SECURITY_PRIVACY.md": "# Security / privacy\n\nNo PII. No production keys.\n",
    "README.md": "# {packet} Adoption Package — {title}\n\nStatus: SCAFFOLD_ONLY until seeded runs exist.\n",
}


def scaffold(packet: str, title: str) -> Path:
    dest = PKG_ROOT / packet
    dest.mkdir(parents=True, exist_ok=True)
    for name, body in TEMPLATE_FILES.items():
        path = dest / name
        if not path.exists():
            path.write_text(body.format(packet=packet, title=title), encoding="utf-8")
    manifest = {
        "packet": packet,
        "title": title,
        "adoption_level": "A0",
        "status": "SCAFFOLD_ONLY",
        "IMPROVED_STATE_OF_ART": False,
        "EXTERNAL_REPRODUCTION_PENDING": True,
        "PHYSICAL_REPRODUCTION_PENDING": True,
        "STANDARDIZED_6G": False,
        "COMPLIANT": False,
    }
    (dest / "manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    # Also drop a pointer under research/new/
    new_dir = ROOT / "research" / "new" / packet
    new_dir.mkdir(parents=True, exist_ok=True)
    (new_dir / "POINTER.md").write_text(
        f"Scaffold lives at `research/r6g/adoption/packages/{packet}/`.\n",
        encoding="utf-8",
    )
    return dest


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--packet", required=True, help="e.g. R6G-012")
    p.add_argument("--title", required=True)
    args = p.parse_args()
    dest = scaffold(args.packet, args.title)
    print(json.dumps({"ok": True, "path": str(dest.relative_to(ROOT)), "IMPROVED_STATE_OF_ART": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
