#!/usr/bin/env bash
# Build a public release archive from ARTIFACT_MANIFEST.json paths.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
MANIFEST="${ROOT}/release/ARTIFACT_MANIFEST.json"
OUT_DIR="${ROOT}/release/dist"
STAMP="$(date -u +%Y%m%dT%H%M%SZ)"
ARCHIVE="${OUT_DIR}/gunnchos-7gc-ai-ran-field-kit-public-${STAMP}.tar.gz"
CHECKSUMS="${OUT_DIR}/gunnchos-7gc-ai-ran-field-kit-public-${STAMP}.sha256"

if [[ ! -f "${MANIFEST}" ]]; then
  echo "Missing manifest: ${MANIFEST}" >&2
  exit 1
fi

mkdir -p "${OUT_DIR}"

python3 - <<'PY' "${MANIFEST}" "${ROOT}" > /tmp/release_file_list.txt
import json, pathlib, sys
manifest = json.loads(pathlib.Path(sys.argv[1]).read_text())
root = pathlib.Path(sys.argv[2])
for entry in manifest.get("artifacts", []):
    rel = entry["path"]
    p = root / rel
    if p.is_file():
        print(rel)
    elif p.is_dir():
        for f in sorted(p.rglob("*")):
            if f.is_file() and ".git" not in f.parts:
                print(f.relative_to(root).as_posix())
    else:
        print(f"WARN missing: {rel}", file=sys.stderr)
PY

if [[ ! -s /tmp/release_file_list.txt ]]; then
  echo "No files listed in manifest" >&2
  exit 1
fi

tar -czf "${ARCHIVE}" -C "${ROOT}" -T /tmp/release_file_list.txt
shasum -a 256 "${ARCHIVE}" | tee "${CHECKSUMS}"

echo "Created:"
echo "  ${ARCHIVE}"
echo "  ${CHECKSUMS}"
