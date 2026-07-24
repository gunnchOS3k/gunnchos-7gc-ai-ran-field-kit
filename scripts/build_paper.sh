#!/usr/bin/env bash
# Build paper/main.pdf using pinned Tectonic (preferred) or pinned TeX Live Docker.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PAPER_DIR="${ROOT}/paper"
TOOLS_DIR="${ROOT}/.tools"

# Pinned tooling (do not use docker :latest)
readonly TECTONIC_VERSION="0.16.9"
readonly TECTONIC_RELEASE_TAG="tectonic%40${TECTONIC_VERSION}"
readonly TEXLIVE_IMAGE="texlive/texlive@sha256:ee8ab695a9640d119482eff320c79b2292c70694d068aeb15ff4720761af8839"
readonly TEXLIVE_IMAGE_LABEL="texlive/texlive:TL2024-historic (digest-pinned)"
readonly MIN_PAGE_COUNT=6
readonly MAX_PAGE_COUNT=8
# Stabilize PDF timestamps where tools honor SOURCE_DATE_EPOCH (Unix epoch).
export SOURCE_DATE_EPOCH="${SOURCE_DATE_EPOCH:-0}"
export TZ="${TZ:-UTC}"

MAIN="main"
PDF="${PAPER_DIR}/${MAIN}.pdf"
BUILD_LOG="${PAPER_DIR}/.paper_build.log"
REPORT="${PAPER_DIR}/PAPER_BUILD_REPORT.md"
MANIFEST="${PAPER_DIR}/PAPER_BUILD_MANIFEST.json"
CHECKSUMS="${PAPER_DIR}/PAPER_CHECKSUMS.sha256"

BUILD_METHOD=""
BUILD_TOOL_VERSION=""
BUILD_STATUS="failed"
PAGE_COUNT=""
PDF_SHA256=""
TEX_FIXES=()
VALIDATION_ERRORS=()

log() { printf '%s\n' "$*" | tee -a "${BUILD_LOG}"; }
fail() { log "ERROR: $*"; exit 1; }

tectonic_asset_for_platform() {
  local os arch
  os="$(uname -s)"
  arch="$(uname -m)"
  case "${os}-${arch}" in
    Darwin-arm64)  echo "tectonic-${TECTONIC_VERSION}-aarch64-apple-darwin.tar.gz" ;;
    Darwin-x86_64) echo "tectonic-${TECTONIC_VERSION}-x86_64-apple-darwin.tar.gz" ;;
    Linux-x86_64)  echo "tectonic-${TECTONIC_VERSION}-x86_64-unknown-linux-gnu.tar.gz" ;;
    Linux-aarch64) echo "tectonic-${TECTONIC_VERSION}-aarch64-unknown-linux-musl.tar.gz" ;;
    *) return 1 ;;
  esac
}

ensure_pinned_tectonic() {
  local asset dest bin url tmp
  asset="$(tectonic_asset_for_platform)" || return 1
  dest="${TOOLS_DIR}/tectonic-${TECTONIC_VERSION}"
  bin="${dest}/tectonic"
  if [[ -x "${bin}" ]]; then
    printf '%s\n' "${bin}"
    return 0
  fi
  mkdir -p "${dest}"
  url="https://github.com/tectonic-typesetting/tectonic/releases/download/${TECTONIC_RELEASE_TAG}/${asset}"
  log "Downloading pinned Tectonic ${TECTONIC_VERSION}: ${url}" >&2
  tmp="$(mktemp -d)"
  curl -fsSL "${url}" -o "${tmp}/${asset}"
  tar -xzf "${tmp}/${asset}" -C "${dest}"
  chmod +x "${bin}"
  rm -rf "${tmp}"
  printf '%s\n' "${bin}"
}

clean_intermediates() {
  rm -f "${PAPER_DIR}/${MAIN}.aux" \
        "${PAPER_DIR}/${MAIN}.bbl" \
        "${PAPER_DIR}/${MAIN}.blg" \
        "${PAPER_DIR}/${MAIN}.log" \
        "${PAPER_DIR}/${MAIN}.out" \
        "${PAPER_DIR}/${MAIN}.synctex.gz" \
        "${PAPER_DIR}/${MAIN}.fdb_latexmk" \
        "${PAPER_DIR}/${MAIN}.fls"
}

build_with_tectonic() {
  local tectonic_bin="$1"
  log "Building with Tectonic: ${tectonic_bin}"
  (
    cd "${PAPER_DIR}"
    "${tectonic_bin}" -X compile "${MAIN}.tex" --synctex --keep-logs --keep-intermediates
  )
  BUILD_METHOD="tectonic"
  BUILD_TOOL_VERSION="$("${tectonic_bin}" --version 2>/dev/null | head -1 || echo "tectonic ${TECTONIC_VERSION}")"
}

build_with_docker() {
  command -v docker >/dev/null 2>&1 || return 1
  log "Building with pinned Docker image: ${TEXLIVE_IMAGE_LABEL}"
  docker run --rm \
    -v "${PAPER_DIR}:/workdir" \
    -w /workdir \
    "${TEXLIVE_IMAGE}" \
    bash -lc "pdflatex -interaction=nonstopmode ${MAIN}.tex && bibtex ${MAIN} && pdflatex -interaction=nonstopmode ${MAIN}.tex && pdflatex -interaction=nonstopmode ${MAIN}.tex"
  BUILD_METHOD="docker-texlive"
  BUILD_TOOL_VERSION="${TEXLIVE_IMAGE_LABEL}"
}

validate_sources() {
  python3 - <<'PY' "${PAPER_DIR}"
import glob
import re
import sys
from pathlib import Path

paper = Path(sys.argv[1])
errors = []

main_tex = (paper / "main.tex").read_text(encoding="utf-8")
tex_sources = main_tex + "\n".join(
    p.read_text(encoding="utf-8") for p in sorted((paper / "sections").glob("*.tex"))
)
tex_sources += (paper / "appendix" / "reproducibility.tex").read_text(encoding="utf-8")

expected_title = "Resilience-Aware, Human-Centric AI-RAN Orchestration"
if expected_title not in main_tex:
    errors.append(f"missing expected title fragment: {expected_title}")
if "Edmund Gunn Jr." not in main_tex:
    errors.append("missing author: Edmund Gunn Jr.")
if "7GC Research Product Spine" not in main_tex:
    errors.append("missing affiliation: 7GC Research Product Spine")

required_marker = "RESULTS_PENDING_AUTHENTIC_GATE3_DATA"
normalized = tex_sources.replace("\\_", "_")
if required_marker not in normalized:
    errors.append(f"missing required marker: {required_marker}")
results_text = (paper / "sections" / "results.tex").read_text(encoding="utf-8")
if required_marker not in results_text.replace("\\_", "_"):
    errors.append("results.tex must preserve RESULTS_PENDING_AUTHENTIC_GATE3_DATA")

# Block invented submission metadata (methods manuscript only)
forbidden_patterns = [
    (r"\\IEEEpubid\{", "invented IEEE pub ID"),
    (r"submitted to [A-Z]", "invented submission venue"),
    (r"under review at", "invented review status"),
    (r"doi\.org/10\.[0-9]{4,}/7gc", "invented repository DOI"),
    (r"p\s*[<=>]\s*0\.[0-9]", "invented p-value"),
    (r"effect size\s*=\s*[0-9]", "invented effect size"),
]
for pattern, label in forbidden_patterns:
    if re.search(pattern, tex_sources, flags=re.IGNORECASE):
        errors.append(f"forbidden content detected ({label})")

# Bibliography key coverage
bib_text = (paper / "references.bib").read_text(encoding="utf-8")
bib_keys = set(re.findall(r"@\w+\{([^,\s]+)", bib_text))
cite_groups = re.findall(r"\\cite\{([^}]+)\}", tex_sources)
cited = set()
for group in cite_groups:
    for key in group.split(","):
        cited.add(key.strip())
missing = sorted(k for k in cited if k not in bib_keys)
if missing:
    errors.append(f"missing bibliography keys: {', '.join(missing)}")
unused = sorted(k for k in bib_keys if k not in cited)
if unused:
    errors.append(f"unused bibliography keys (warning-level): {', '.join(unused)}")

if errors:
    for err in errors:
        print(f"VALIDATION_ERROR: {err}")
    sys.exit(1)
print("VALIDATION_OK")
PY
}

pdf_page_count() {
  local pdf_path="$1"
  if command -v pdfinfo >/dev/null 2>&1; then
    pdfinfo "${pdf_path}" | awk '/^Pages:/ {print $2; exit}'
    return 0
  fi
  if [[ "$(uname -s)" == "Darwin" ]] && command -v mdls >/dev/null 2>&1; then
    local md
    md="$(mdls -name kMDItemNumberOfPages -raw "${pdf_path}" 2>/dev/null || true)"
    if [[ -n "${md}" && "${md}" != "(null)" ]]; then
      echo "${md}"
      return 0
    fi
  fi
  # Stdlib fallback: inflate PDF streams then count /Type /Page leaves.
  # Tectonic/xdvipdfmx often compress page dictionaries (no plaintext /Type /Page).
  python3 - <<'PY' "${pdf_path}"
import re
import sys
import zlib
from pathlib import Path

data = Path(sys.argv[1]).read_bytes()
parts = [data]
for m in re.finditer(rb"stream\r?\n(.*?)\r?\nendstream", data, flags=re.S):
    chunk = m.group(1)
    for wbits in (zlib.MAX_WBITS, -zlib.MAX_WBITS):
        try:
            parts.append(zlib.decompress(chunk, wbits))
            break
        except Exception:
            continue
expanded = b"\n".join(parts)
pages = re.findall(rb"/Type\s*/Page(?![sA-Za-z])", expanded)
if pages:
    print(len(pages))
    raise SystemExit(0)
counts = [int(x) for x in re.findall(rb"/Type\s*/Pages.*?/Count\s+(\d+)", expanded, flags=re.S)]
if counts:
    print(max(counts))
    raise SystemExit(0)
print("")
PY
}

validate_page_count() {
  local count="$1"
  if [[ -z "${count}" || "${count}" == "unknown" || "${count}" == "(null)" ]]; then
    VALIDATION_ERRORS+=("page count unavailable (required ${MIN_PAGE_COUNT}-${MAX_PAGE_COUNT})")
    return 1
  fi
  if ! [[ "${count}" =~ ^[0-9]+$ ]]; then
    VALIDATION_ERRORS+=("non-numeric page count: ${count}")
    return 1
  fi
  if (( count < MIN_PAGE_COUNT || count > MAX_PAGE_COUNT )); then
    VALIDATION_ERRORS+=("page count ${count} outside required range ${MIN_PAGE_COUNT}-${MAX_PAGE_COUNT}")
    return 1
  fi
  return 0
}

write_checksums() {
  (
    cd "${PAPER_DIR}"
    shasum -a 256 "${MAIN}.pdf" PAPER_BUILD_REPORT.md PAPER_BUILD_MANIFEST.json 2>/dev/null \
      | tee "${CHECKSUMS}"
  )
}

write_manifest() {
  local ts utc_iso page_count_json page_count_ok
  ts="$(date -u +%Y%m%dT%H%M%SZ)"
  utc_iso="$(date -u +"%Y-%m-%dT%H:%M:%SZ")"
  PDF_SHA256="$(shasum -a 256 "${PDF}" | awk '{print $1}')"
  if [[ -n "${PAGE_COUNT}" && "${PAGE_COUNT}" != "unknown" && "${PAGE_COUNT}" != "(null)" ]]; then
    page_count_json="${PAGE_COUNT}"
  else
    page_count_json="None"
  fi
  if [[ "${BUILD_STATUS}" == "success" ]]; then
    page_count_ok="True"
  else
    page_count_ok="False"
  fi
  python3 - <<PY
import json
from pathlib import Path

manifest = {
    "artifact": "paper/main.pdf",
    "status": "${BUILD_STATUS}",
    "built_at_utc": "${utc_iso}",
    "build_stamp": "${ts}",
    "build_method": "${BUILD_METHOD}",
    "tool_version": """${BUILD_TOOL_VERSION}""".strip(),
    "tectonic_pin": "${TECTONIC_VERSION}",
    "docker_image": "${TEXLIVE_IMAGE_LABEL}",
    "docker_digest": "sha256:ee8ab695a9640d119482eff320c79b2292c70694d068aeb15ff4720761af8839",
    "source_date_epoch": "${SOURCE_DATE_EPOCH}",
    "page_count": ${page_count_json},
    "page_count_required_min": ${MIN_PAGE_COUNT},
    "page_count_required_max": ${MAX_PAGE_COUNT},
    "pdf_sha256": "${PDF_SHA256}",
    "validation": {
        "title_ok": True,
        "authorship_ok": True,
        "results_pending_marker_ok": True,
        "bibliography_keys_ok": True,
        "no_invented_submission_or_doi": True,
        "page_count_in_range": ${page_count_ok},
    },
    "outputs": [
        "paper/main.pdf",
        "paper/PAPER_BUILD_REPORT.md",
        "paper/PAPER_BUILD_MANIFEST.json",
        "paper/PAPER_CHECKSUMS.sha256",
    ],
}
Path("${MANIFEST}").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
PY
}

write_report() {
  local ts
  ts="$(date -u +"%Y-%m-%d %H:%M:%S UTC")"
  cat > "${REPORT}" <<EOF
# Paper Build Report

| Field | Value |
|-------|-------|
| Status | **${BUILD_STATUS}** |
| Built at | ${ts} |
| Method | ${BUILD_METHOD} |
| Tool | ${BUILD_TOOL_VERSION} |
| Output | \`paper/main.pdf\` |
| Page count | ${PAGE_COUNT:-unknown} (required ${MIN_PAGE_COUNT}--${MAX_PAGE_COUNT}) |
| PDF SHA-256 | \`${PDF_SHA256}\` |
| SOURCE_DATE_EPOCH | \`${SOURCE_DATE_EPOCH}\` (\`TZ=${TZ}\`) |

## Validation

- Title and authorship preserved (Edmund Gunn Jr.; 7GC Research Product Spine)
- \`RESULTS_PENDING_AUTHENTIC_GATE3_DATA\` preserved in results and manuscript
- No invented submission venue, repository DOI, p-values, or effect sizes
- All \`\\cite{...}\` keys resolve in \`references.bib\`
- Page count within ${MIN_PAGE_COUNT}--${MAX_PAGE_COUNT} inclusive

## Reproducibility notes

Builds export \`SOURCE_DATE_EPOCH=0\` and \`TZ=UTC\` before compilation.
Residual PDF byte differences may still occur from hyperref object IDs, tool-specific XMP metadata, or Tectonic cache state even when content is unchanged.
Compare \`PDF SHA-256\` together with page count and pinned tool version rather than expecting cross-machine byte identity.

## Tooling pins

| Tool | Pin |
|------|-----|
| Tectonic | ${TECTONIC_VERSION} (GitHub release binary → \`.tools/\`) |
| Docker fallback | ${TEXLIVE_IMAGE_LABEL} |

## Fallback (manual)

1. **Tectonic (recommended):** \`bash scripts/build_paper.sh\` downloads pinned Tectonic into \`.tools/\` when needed.
2. **Docker:** \`docker pull ${TEXLIVE_IMAGE_LABEL}\` then re-run \`make paper\`.
3. **Local TeX Live / MacTeX:** \`cd paper && pdflatex main.tex && bibtex main && pdflatex main.tex && pdflatex main.tex\`

## TeX fixes applied this run

$(if [[ ${#TEX_FIXES[@]} -eq 0 ]]; then echo "- None"; else printf '%s\n' "${TEX_FIXES[@]}" | sed 's/^/- /'; fi)

See also \`paper/PAPER_BUILD_MANIFEST.json\` and \`paper/PAPER_CHECKSUMS.sha256\`.
EOF
}

main() {
  : > "${BUILD_LOG}"
  log "Paper build started: ${ROOT}"
  cd "${PAPER_DIR}"

  validate_sources >> "${BUILD_LOG}" 2>&1 || fail "source validation failed (see ${BUILD_LOG})"

  clean_intermediates
  rm -f "${PDF}"

  if command -v tectonic >/dev/null 2>&1; then
    build_with_tectonic "$(command -v tectonic)"
  elif tectonic_bin="$(ensure_pinned_tectonic 2>>"${BUILD_LOG}")"; then
    build_with_tectonic "${tectonic_bin}"
  elif build_with_docker 2>>"${BUILD_LOG}"; then
    :
  else
    cat >&2 <<EOF
BLOCKED: No paper build tooling available.
  - Install Docker and pull ${TEXLIVE_IMAGE_LABEL}, or
  - Allow scripts/build_paper.sh to download pinned Tectonic ${TECTONIC_VERSION}, or
  - Install TeX Live / MacTeX locally.
Manuscript sources remain methods-ready; see paper/README.md.
EOF
    exit 2
  fi

  [[ -f "${PDF}" ]] || fail "build finished but ${PDF} missing"

  PAGE_COUNT="$(pdf_page_count "${PDF}" | tr -d '[:space:]')"
  [[ -n "${PAGE_COUNT}" ]] || PAGE_COUNT="unknown"

  PDF_SHA256="$(shasum -a 256 "${PDF}" | awk '{print $1}')"

  if ! validate_page_count "${PAGE_COUNT}"; then
    BUILD_STATUS="failed"
    write_manifest
    write_report
    write_checksums
    for err in "${VALIDATION_ERRORS[@]}"; do
      log "ERROR: ${err}"
    done
    fail "page count validation failed (${PAGE_COUNT} pages; required ${MIN_PAGE_COUNT}-${MAX_PAGE_COUNT})"
  fi

  BUILD_STATUS="success"

  write_manifest
  write_report
  write_checksums

  log "SUCCESS: ${PDF} (${PAGE_COUNT} pages, sha256=${PDF_SHA256})"
}

main "$@"
