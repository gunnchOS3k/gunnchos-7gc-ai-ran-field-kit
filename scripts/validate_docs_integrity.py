#!/usr/bin/env python3
"""WP-012 docs integrity validator for field-kit control plane.

Checks:
- Canonical Product Charter markdown + YAML exist and load
- Approval tokens are not pre-set true before Edmund merge
- Completion register classifications are valid
- REPO_CATALOG.yaml loads and REPO_CATALOG.md is generated/synced
- ACCEPTED_MAIN_BASELINE.json exists
- No unsupported completion claim tokens flipped true in charter YAML
- Optional: sibling portal path for required portal docs

Exit 0 on pass, 1 on failure.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

ROOT = Path(__file__).resolve().parents[1]

REQUIRED_CHARTER = [
    ROOT / "program/charter/gunnchOS3k_PRODUCT_CHARTER.md",
    ROOT / "program/charter/gunnchOS3k_PRODUCT_CHARTER.yaml",
]

REQUIRED_ARTIFACTS = [
    ROOT / "artifacts/wp012/PROJECT_CHARTER_COMPLETION_REGISTER.json",
    ROOT / "artifacts/wp012/PROJECT_CHARTER_REMAINING_REAL_WORLD_GAPS.md",
    ROOT / "artifacts/wp012/REPO_CATALOG.yaml",
    ROOT / "artifacts/wp012/WP-001_INPUT_MANIFEST_PREVIEW.json",
    ROOT / "artifacts/cycle3a/ACCEPTED_MAIN_BASELINE.json",
]

VALID_CLASSES = {
    "DIGITALLY_COMPLETE",
    "DIGITAL_WORK_PENDING",
    "PHYSICAL_PENDING",
    "HUMAN_PENDING",
    "EXTERNAL_PENDING",
    "STANDARD_PENDING",
    "OWNER_DEFERRED",
    "OWNER_RELEASE_DECISION_PENDING",
}

OWNER_RELEASE_ONLY_IDS = {
    "PRODUCT_CHARTER_APPROVAL",
    "RFQ_SEND",
    "FAB_RELEASE_AUTHORIZATION",
    "WP001_START",
    "QUOTE_BACKED_ECONOMICS",
}

DIGITAL_WORK_PENDING_IDS = {
    "DEVICE_LAB_10_10_DIGITAL",
    "ECO010_FULL_SOAK",
    "FOUR_GAME_PRODUCTION_RUNTIME",
    "LIVE_GUNNCHOS_VISUAL",
    "DSXL_DUAL_COMPOSITOR_UX",
    "RING_APP_STATE_MUTATION",
}

FORBIDDEN_TRUE_TOKENS = {
    "PRODUCT_CHARTER_DEFINITION_COMPLETE",
    "owner_approval_token",
}

UNSUPPORTED_CLAIM_PHRASES = [
    "standardized commercial 6g certified",
    "carrier approved",
    "100% intelligence",
    "doctoral-level intelligence",
    "frontier parity achieved",
]

PORTAL_REQUIRED = [
    "README.md",
    "START_HERE.md",
    "ECOSYSTEM_MAP.md",
    "PRODUCT_FAMILY.md",
    "SOFTWARE_STACK.md",
    "MIDDLEWARE_MAP.md",
    "REPO_CATALOG.md",
    "REPO_CATALOG.yaml",
    "STATUS.md",
    "ROADMAP.md",
    "GOLDEN_JOURNEYS.md",
    "DEVICE_LAB.md",
    "GAMES.md",
    "WAIKE.md",
    "CONNECTIVITY.md",
    "RESEARCH.md",
    "MANUFACTURING.md",
    "EVIDENCE.md",
    "GLOSSARY.md",
]

PORTAL_AUDIENCES = [
    "CURIOUS.md",
    "STUDENT.md",
    "INTERN.md",
    "DEVELOPER.md",
    "RESEARCHER.md",
    "EDUCATOR.md",
    "MANUFACTURER.md",
    "SECURITY_REVIEWER.md",
]


def fail(msg: str, errors: list[str]) -> None:
    errors.append(msg)


def load_yaml(path: Path):
    if yaml is None:
        raise RuntimeError("PyYAML required: pip install pyyaml")
    with path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def generate_repo_catalog_md(catalog: dict, out_path: Path) -> str:
    lines = [
        "# gunnchOS3k Repository Catalog",
        "",
        f"Generated from `artifacts/wp012/REPO_CATALOG.yaml` (schema `{catalog.get('schema')}`).",
        "",
        f"**Control plane:** `{catalog.get('canonical_control_plane')}`  ",
        f"**Ecosystem portal:** `{catalog.get('ecosystem_portal')}`  ",
        f"**Profile front door:** `{catalog.get('profile_front_door')}`",
        "",
        "## Claim boundary",
        "",
        catalog.get("claim_boundary_global", ""),
        "",
        "## Repositories",
        "",
        "| Repo | Category | Purpose | Layer | State | Physical pending | External pending |",
        "|---|---|---|---|---|---|---|",
    ]
    for r in catalog.get("repositories", []):
        lines.append(
            "| `{repo}` | {category} | {purpose} | {layer} | {state} | {pp} | {ep} |".format(
                repo=r.get("repo"),
                category=r.get("category"),
                purpose=(r.get("purpose") or "").replace("|", "/"),
                layer=r.get("product_layer"),
                state=r.get("current_state"),
                pp=r.get("physical_pending"),
                ep=r.get("external_pending"),
            )
        )
    lines.extend(
        [
            "",
            "## Architecture (Mermaid)",
            "",
            "```mermaid",
            "flowchart TB",
            "  portal[research-portal START_HERE]",
            "  field[field-kit charter]",
            "  hw[hardware-industrial-design]",
            "  os[device-os / gunnchOS / Device Lab]",
            "  ai[gunnchAI3k]",
            "  games[four games]",
            "  conn[connectivity research]",
            "  profileDeferred[profile OWNER_DEFERRED]",
            "  portal --> field",
            "  field --> hw",
            "  field --> os",
            "  field --> ai",
            "  os --> games",
            "  os --> ai",
            "  field --> conn",
            "  profileDeferred -.-> portal",
            "```",
            "",
            "## Where do I contribute?",
            "",
            "- **Charter / evidence / work packets:** `gunnchos-7gc-ai-ran-field-kit`",
            "- **OS / Device Lab:** `gunnchos-device-os`",
            "- **Hardware:** `gunnchos-hardware-industrial-design`",
            "- **AI:** `gunnchAI3k`",
            "- **Games:** respective game repos",
            "- **Education / WAIKE:** `waike-research-ops`",
            "- **Public docs:** `gunnchos-research-portal`",
            "",
            "Every core README should link back to the Ecosystem Portal.",
            "",
        ]
    )
    text = "\n".join(lines)
    out_path.write_text(text, encoding="utf-8")
    return text


def check_charter(errors: list[str]) -> dict | None:
    for path in REQUIRED_CHARTER:
        if not path.is_file():
            fail(f"missing required file: {path.relative_to(ROOT)}", errors)
    if errors:
        return None
    data = load_yaml(REQUIRED_CHARTER[1])
    approval = data.get("approval") or {}
    for token in FORBIDDEN_TRUE_TOKENS:
        if approval.get(token) is True:
            fail(
                f"approval.{token} must remain false until Edmund merges final charter PR",
                errors,
            )
    if not approval.get("definition_content_complete_candidate"):
        fail("definition_content_complete_candidate should be true for WP-012 candidate", errors)
    mission = data.get("mission") or ""
    if "carrier-grade-targeted equitable compute ecosystem" not in mission:
        fail("mission language missing required defensible phrasing", errors)
    products = data.get("first_party_products") or []
    names = {p.get("name") for p in products}
    expected = {
        "Student 14.5",
        "Handheld Hybrid",
        "DS-XL Coder",
        "Edge I/O Rings",
        "First-party Dock",
    }
    if names != expected:
        fail(f"first_party_products mismatch: {names} != {expected}", errors)
    md = REQUIRED_CHARTER[0].read_text(encoding="utf-8").lower()
    for phrase in UNSUPPORTED_CLAIM_PHRASES:
        if phrase in md:
            fail(f"unsupported claim phrase in charter markdown: {phrase}", errors)
    return data


def check_artifacts(errors: list[str]) -> None:
    for path in REQUIRED_ARTIFACTS:
        if not path.is_file():
            fail(f"missing required artifact: {path.relative_to(ROOT)}", errors)
            continue
    reg_path = ROOT / "artifacts/wp012/PROJECT_CHARTER_COMPLETION_REGISTER.json"
    if reg_path.is_file():
        reg = json.loads(reg_path.read_text(encoding="utf-8"))
        tokens = reg.get("tokens") or {}
        if tokens.get("PRODUCT_CHARTER_DEFINITION_COMPLETE") is True:
            fail("register must not pre-set PRODUCT_CHARTER_DEFINITION_COMPLETE true", errors)
        if tokens.get("owner_approval_token") is True:
            fail("register must not pre-set owner_approval_token true", errors)
        contradictions = 0
        for req in reg.get("requirements") or []:
            rid = req.get("id")
            cls = req.get("classification")
            if cls not in VALID_CLASSES:
                fail(f"invalid classification for {rid}: {cls}", errors)
                contradictions += 1
                continue
            if rid == "PROFILE_FRONT_DOOR":
                if cls != "OWNER_DEFERRED" or req.get("blocking") is not False:
                    fail("PROFILE_FRONT_DOOR must be OWNER_DEFERRED with blocking=false", errors)
                    contradictions += 1
            if rid in DIGITAL_WORK_PENDING_IDS and cls != "DIGITAL_WORK_PENDING":
                fail(f"{rid} must be DIGITAL_WORK_PENDING until WP-011R passes", errors)
                contradictions += 1
            if rid in OWNER_RELEASE_ONLY_IDS and cls != "OWNER_RELEASE_DECISION_PENDING":
                fail(f"{rid} must remain OWNER_RELEASE_DECISION_PENDING", errors)
                contradictions += 1
            if cls == "OWNER_RELEASE_DECISION_PENDING" and rid not in OWNER_RELEASE_ONLY_IDS:
                # Allow only reserved Edmund-decision IDs in this class
                fail(
                    f"{rid} misclassified as OWNER_RELEASE_DECISION_PENDING "
                    "(reserve for Edmund decisions only)",
                    errors,
                )
                contradictions += 1
        tokens = reg.get("tokens") or {}
        reported = tokens.get("CHARTER_REGISTER_CLASSIFICATION_CONTRADICTIONS")
        if reported is not None and int(reported) != contradictions:
            # Auto-correct reported counter when writing integrity view
            if contradictions == 0 and int(reported) != 0:
                fail(
                    "CHARTER_REGISTER_CLASSIFICATION_CONTRADICTIONS must be 0 when register is clean",
                    errors,
                )
        if contradictions:
            fail(f"CHARTER_REGISTER_CLASSIFICATION_CONTRADICTIONS={contradictions}", errors)
    preview = ROOT / "artifacts/wp012/WP-001_INPUT_MANIFEST_PREVIEW.json"
    if preview.is_file():
        data = json.loads(preview.read_text(encoding="utf-8"))
        if data.get("status") != "PREVIEW_ONLY_DO_NOT_START":
            fail("WP-001 preview must remain PREVIEW_ONLY_DO_NOT_START", errors)


def check_catalog(errors: list[str], write: bool) -> None:
    yaml_path = ROOT / "artifacts/wp012/REPO_CATALOG.yaml"
    md_path = ROOT / "artifacts/wp012/REPO_CATALOG.md"
    if not yaml_path.is_file():
        return
    catalog = load_yaml(yaml_path)
    repos = catalog.get("repositories") or []
    if len(repos) < 10:
        fail(f"REPO_CATALOG.yaml expected core repos, found {len(repos)}", errors)
    required_fields = [
        "repo",
        "category",
        "purpose",
        "product_layer",
        "primary_audience",
        "owner",
        "source_of_truth_for",
        "depends_on",
        "consumed_by",
        "entrypoint",
        "claim_boundary",
        "current_state",
        "physical_pending",
        "external_pending",
    ]
    for r in repos:
        for field in required_fields:
            if field not in r:
                fail(f"catalog repo {r.get('repo')} missing field {field}", errors)
    generated = generate_repo_catalog_md(catalog, md_path if write else md_path)
    if not write:
        # still write — generation is part of integrity pipeline
        md_path.write_text(generated, encoding="utf-8")
    if not md_path.is_file():
        fail("REPO_CATALOG.md missing after generation", errors)


def check_historical_charter_label(errors: list[str]) -> None:
    hist = ROOT / "program/charters/GUNNCHOS3K_CARRIER_GRADE_6G_ECOSYSTEM.md"
    marker = ROOT / "program/charters/HISTORICAL_NOTE.md"
    if hist.is_file() and not marker.is_file():
        fail("program/charters/HISTORICAL_NOTE.md required to label prior ingest HISTORICAL", errors)


def check_portal(portal: Path, errors: list[str]) -> None:
    if not portal.is_dir():
        fail(f"portal path not found: {portal}", errors)
        return
    for name in PORTAL_REQUIRED:
        if not (portal / name).is_file():
            fail(f"portal missing {name}", errors)
    for name in PORTAL_AUDIENCES:
        if not (portal / "audiences" / name).is_file():
            fail(f"portal missing audiences/{name}", errors)
    readme = (portal / "README.md").read_text(encoding="utf-8")
    if "current spine" in readme.lower() and "historical" not in readme.lower():
        fail("portal README has competing spine claim without HISTORICAL label", errors)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate WP-012 docs integrity")
    parser.add_argument(
        "--portal",
        type=Path,
        default=None,
        help="Optional path to gunnchos-research-portal for sibling checks",
    )
    parser.add_argument(
        "--write-catalog",
        action="store_true",
        default=True,
        help="Generate REPO_CATALOG.md from YAML (default true)",
    )
    args = parser.parse_args()
    errors: list[str] = []

    if yaml is None:
        print("ERROR: PyYAML is required", file=sys.stderr)
        return 1

    check_charter(errors)
    check_artifacts(errors)
    check_catalog(errors, write=args.write_catalog)
    check_historical_charter_label(errors)
    if args.portal:
        check_portal(args.portal.resolve(), errors)

    if errors:
        print("DOCS_INTEGRITY_FAIL")
        for e in errors:
            print(f" - {e}")
        return 1
    print("DOCS_INTEGRITY_PASS")
    print(f" catalog_md={ROOT / 'artifacts/wp012/REPO_CATALOG.md'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
