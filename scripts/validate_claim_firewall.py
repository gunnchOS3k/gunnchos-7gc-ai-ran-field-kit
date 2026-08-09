#!/usr/bin/env python3
"""Release claim firewall — Cont VII.

Fails CI when product claims exceed evidence:
- assertive forbidden phrases in program prose
- RC / content-complete tokens while launch blockers remain
- FULL_* tokens while digitally executable SCHEMA/STUB backlog remains
- hardware release-complete while placeholder EDA remains
- firmware-complete while production main is smoke-only
- global-data / carrier / 6G claims that exceed standards truth
- final-umbrella / digital-totality claims while Cont VII backlog remains
- Cont VI SCHEMA_ONLY=221 treated as stale — Cont VII backlog is authoritative

Inspects field-kit matrices and, when present, sibling product repos.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]
SIBLING = ROOT.parent
FP = ROOT / "program" / "full_product"
GRAPH = FP / "requirement_graph.yaml"
GAME_MATRIX = FP / "game_release_matrix.yaml"
HW_MATRIX = FP / "hardware_release_matrix.yaml"
SOFT_MATRIX = FP / "software_integration_matrix.yaml"
AI_MATRIX = FP / "ai_capability_matrix.yaml"
BACKLOG_VIII = FP / "continuation_viii" / "DIGITAL_BACKLOG.json"
BACKLOG_VII = FP / "continuation_vii" / "DIGITAL_BACKLOG.json"
BACKLOG_VI = FP / "continuation_vi" / "DIGITALLY_EXECUTABLE_BACKLOG_COUNTS.json"
CONN_MATRIX = FP / "connectivity_carrier_matrix.yaml"
MASTER_STATUS = FP / "reports" / "FULL_PRODUCT_MASTER_STATUS.md"


def active_backlog_path() -> Path:
    """Prefer Cont VIII backlog when present; Cont VII freeze is reference only."""
    if BACKLOG_VIII.exists():
        return BACKLOG_VIII
    if BACKLOG_VII.exists():
        return BACKLOG_VII
    return BACKLOG_VI


# Backward-compatible alias resolved at import; digitally_executable_remaining re-resolves.
BACKLOG = active_backlog_path()

SCAN_DIRS = [
    ROOT / "program" / "nonphysical",
    ROOT / "program" / "physical",
    ROOT / "program" / "reports",
    ROOT / "program" / "credentials",
    ROOT / "device_designs",
    ROOT / "gate2",
    ROOT / "gate3",
    ROOT / "gate4",
    ROOT / "gate5",
    ROOT / "gate6",
    ROOT / "gate7",
    ROOT / "gate8",
    ROOT / "standards",
]

FORBIDDEN = [
    r"\bis carrier-grade deployed\b",
    r"\bis 6G certified\b",
    r"\bis IMT-2030 compliant\b",
    r"\bwe achieved production manufacturing\b",
    r"\bcarrier accepted\b",
    r"\bis FCC/CE certified\b",
    r"\bpilot validated\b",
    r"\bis field proven\b",
    r"\breal battery measurement (complete|pass|accepted)\b",
    r"\breal thermal measurement (complete|pass|accepted)\b",
    r"\bphysical ring validated\b",
    r"\bsecure boot physically validated\b",
    r"\b(earned|achieved|declared|granted)\s+GATE_8_PASS\b",
    r"\bgate\s*8\s*:\s*PASS\b",
]

ALLOW_LINE = re.compile(
    r"(?i)(not |never |forbidden|pending|do not|without claiming|must not|reject|"
    r"criterion|title:|blocked until|NOT_CLAIM|prohibited|token_pass:|"
    r"tokens:|GATE_8_PASS forbidden|pass_axis|PREMATURE_REVOKE|REVOKED|"
    r"not claimed|not earned|not honestly|\*\*not\*\*|: false|:false|"
    r"explicitly \*\*not\*\*|forbidden_claims|may claim|only if|criteria|"
    r"\bno\b.*claimed|not honestly earned)"
)

FULL_TOKEN_RE = re.compile(r"\bFULL_[A-Z0-9_]+\b")
PLACEHOLDER_RE = re.compile(
    r"(?i)(TODO_PINOUT|PLACEHOLDER|FIXME_EDA|STUB_NET|NOT_YET_ROUTED|COMING_SOON)"
)
SMOKE_MAIN_RE = re.compile(r"(?i)(printk\s*\(|while\s*\(\s*1\s*\)\s*\{[^}]{0,80}k_msleep)")


def load_yaml(path: Path) -> Any:
    if not path.exists():
        return {}
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


def load_json(path: Path) -> Any:
    if not path.exists():
        return {}
    return json.loads(path.read_text(encoding="utf-8"))


def scan_prose(hits: list[str]) -> None:
    pat = re.compile("|".join(f"({p})" for p in FORBIDDEN), re.I)
    for d in SCAN_DIRS:
        if not d.exists():
            continue
        for path in d.rglob("*"):
            if path.suffix.lower() not in {".md", ".yaml", ".yml", ".json", ".txt"}:
                continue
            if "claim_firewall" in path.name or "prohibited_claim" in path.name:
                continue
            text = path.read_text(encoding="utf-8", errors="ignore")
            for i, line in enumerate(text.splitlines(), 1):
                if not pat.search(line):
                    continue
                if ALLOW_LINE.search(line):
                    continue
                hits.append(f"{path}:{i}:{line.strip()[:160]}")


def anime_blocks_token() -> int:
    path = SIBLING / "anime-aggressors" / "content" / "missing_assets.json"
    if not path.exists():
        games = (load_yaml(GAME_MATRIX).get("games") or {}).get("anime_aggressors") or {}
        return int(games.get("blocks_token_assets_remaining") or 0)
    data = json.loads(path.read_text(encoding="utf-8"))
    items = data.get("items") or data.get("assets") or []
    return sum(1 for x in items if isinstance(x, dict) and x.get("blocks_token") is True)


def check_game_tokens(hits: list[str]) -> None:
    games = (load_yaml(GAME_MATRIX).get("games") or {})
    bt = anime_blocks_token()
    anime = games.get("anime_aggressors") or {}
    tokens = anime.get("tokens") or {}
    if bt > 0:
        if anime.get("content_complete") is True:
            hits.append(
                f"anime: content_complete=true while {bt} blocks_token launch blockers remain"
            )
        if anime.get("rc_digital") is True:
            hits.append(f"anime: rc_digital=true while {bt} blocks_token launch blockers remain")
        for tok in (
            "ANIME_BETA_CONTENT_COMPLETE_DIGITAL",
            "ANIME_DIGITAL_RC_READY",
        ):
            val = tokens.get(tok)
            if val and val not in {"PREMATURE_REVOKE", "REVOKED"}:
                hits.append(
                    f"anime: tokens.{tok}={val!r} while {bt} blocks_token remain "
                    "(must be PREMATURE_REVOKE)"
                )

    # Generic: any game with rc_digital/content_complete true must not carry launch blockers
    for key, entry in games.items():
        if not isinstance(entry, dict):
            continue
        remaining = int(entry.get("blocks_token_assets_remaining") or 0)
        if remaining <= 0:
            continue
        if entry.get("rc_digital") is True:
            hits.append(f"{key}: rc_digital=true while blocks_token_assets_remaining={remaining}")
        if entry.get("content_complete") is True:
            hits.append(
                f"{key}: content_complete=true while blocks_token_assets_remaining={remaining}"
            )


def digitally_executable_remaining() -> dict[str, int]:
    backlog = active_backlog_path()
    if backlog.exists():
        data = load_json(backlog)
        return {
            "SCHEMA_ONLY": int(data.get("DIGITALLY_EXECUTABLE_SCHEMA_ONLY") or 0),
            "STUB_ONLY": int(data.get("DIGITALLY_EXECUTABLE_STUB_ONLY") or 0),
            "SIMULATION_ONLY": int(data.get("DIGITALLY_EXECUTABLE_SIMULATION_ONLY") or 0),
            "MOCK_ONLY": int(data.get("DIGITALLY_EXECUTABLE_MOCK_ONLY") or 0),
        }
    graph = load_yaml(GRAPH)
    counts = {"SCHEMA_ONLY": 0, "STUB_ONLY": 0, "SIMULATION_ONLY": 0, "MOCK_ONLY": 0}
    for n in graph.get("nodes") or []:
        st = n.get("full_product_status")
        if st in counts:
            counts[st] += 1
        if st == "MOCK_ONLY":
            counts["MOCK_ONLY"] += 1
    return counts


def check_cont_vii_umbrella(hits: list[str]) -> None:
    """Cont VII/VIII: final umbrella / digital totality forbidden while backlog remains."""
    remaining = digitally_executable_remaining()
    soft = (
        remaining["SCHEMA_ONLY"]
        + remaining["STUB_ONLY"]
        + remaining.get("SIMULATION_ONLY", 0)
        + remaining.get("MOCK_ONLY", 0)
    )
    surfaces: list[tuple[str, str]] = []
    for path in (
        SOFT_MATRIX,
        AI_MATRIX,
        HW_MATRIX,
        GAME_MATRIX,
        FP / "evidence_registry.yaml",
        MASTER_STATUS,
        FP / "continuation_vii" / "DIGITAL_BACKLOG.json",
        FP / "continuation_viii" / "DIGITAL_BACKLOG.json",
        FP / "continuation_viii" / "READINESS_SCORECARD.json",
    ):
        if path.exists():
            surfaces.append((str(path), path.read_text(encoding="utf-8", errors="ignore")))
    assertive_umbrella = re.compile(
        r"(?i)(true\s+final\s+umbrella|final_umbrella\s*[:=]\s*true|"
        r"digital\s+totality\s+(complete|achieved|earned)|"
        r"FULL_PRODUCT_DIGITAL_TOTALITY\s*[:=]\s*true|"
        r"DIGITAL_PRE_EVT_RELEASE_READY\s*[:=]\s*true|"
        r"umbrella\s+opened\b.*\b(true|complete|earned))"
    )
    for path, text in surfaces:
        for i, line in enumerate(text.splitlines(), 1):
            if not assertive_umbrella.search(line):
                continue
            if ALLOW_LINE.search(line):
                continue
            if soft > 0:
                hits.append(
                    f"{path}:{i}: final-umbrella/digital-totality claim while Cont VIII "
                    f"digitally executable backlog remains "
                    f"(SCHEMA_ONLY={remaining['SCHEMA_ONLY']} "
                    f"STUB_ONLY={remaining['STUB_ONLY']} "
                    f"MOCK_ONLY={remaining.get('MOCK_ONLY', 0)})"
                )
            else:
                # Even at zero, require explicit Edmund acceptance language elsewhere;
                # bare "umbrella opened" without accepted-mains caveat is rejected.
                if "accepted main" not in line.lower() and "edmund" not in line.lower():
                    hits.append(
                        f"{path}:{i}: final umbrella assertion requires accepted-mains "
                        "digital backlog=0 and Edmund acceptance"
                    )


def check_stale_cont_vi_schema_copy(hits: list[str]) -> None:
    """Reject Cont VII artifacts that copy Cont VI SCHEMA_ONLY=221 as current truth."""
    cont_vii = FP / "continuation_vii"
    if not cont_vii.exists():
        return
    for path in cont_vii.glob("*.json"):
        data = load_json(path)
        # Current status_counts must not silently equal the stale Cont VI snapshot
        # without an explicit stale-reference key.
        sc = data.get("status_counts") if isinstance(data, dict) else None
        if isinstance(sc, dict) and int(sc.get("SCHEMA_ONLY") or -1) == 221:
            if "stale" not in path.name.lower() and "previous_cont_vi_stale" not in json.dumps(data):
                hits.append(
                    f"{path}: status_counts.SCHEMA_ONLY=221 looks like stale Cont VI copy; "
                    "Cont VII must re-prove"
                )


def check_full_tokens(hits: list[str]) -> None:
    remaining = digitally_executable_remaining()
    soft_remaining = (
        remaining["SCHEMA_ONLY"]
        + remaining["STUB_ONLY"]
        + remaining.get("SIMULATION_ONLY", 0)
        + remaining.get("MOCK_ONLY", 0)
    )
    surfaces: list[tuple[str, str]] = [
        (str(SOFT_MATRIX), SOFT_MATRIX.read_text(encoding="utf-8") if SOFT_MATRIX.exists() else ""),
        (str(AI_MATRIX), AI_MATRIX.read_text(encoding="utf-8") if AI_MATRIX.exists() else ""),
        (str(HW_MATRIX), HW_MATRIX.read_text(encoding="utf-8") if HW_MATRIX.exists() else ""),
        (str(GAME_MATRIX), GAME_MATRIX.read_text(encoding="utf-8") if GAME_MATRIX.exists() else ""),
        (
            str(FP / "evidence_registry.yaml"),
            (FP / "evidence_registry.yaml").read_text(encoding="utf-8")
            if (FP / "evidence_registry.yaml").exists()
            else "",
        ),
    ]
    # Also scan sibling docs for FULL_* assertive claims when siblings present.
    # Cont VIII: when digitally executable backlog is already zero on accepted mains,
    # sibling-local FULL_* product tokens are sibling evidence — field-kit still must
    # not assert DIGITAL_PRE_EVT / umbrella tokens (checked on field-kit surfaces).
    # While backlog remains, sibling FULL_* claims are rejected (Cont VII doctrine).
    if soft_remaining > 0:
        for repo in (
            "gunnchos-device-os",
            "gunnchAI3k",
            "gunnchos-hardware-industrial-design",
            "edge-io-measurement-node",
            "anime-aggressors",
            "pedestrian-pursuit",
            "archive-of-life-artifact-world",
            "beatlink-party",
        ):
            base = SIBLING / repo
            if not base.exists():
                continue
            for rel in ("README.md", "docs", "program", "evidence"):
                path = base / rel
                if path.is_file() and path.suffix.lower() in {".md", ".yaml", ".yml", ".json"}:
                    surfaces.append((str(path), path.read_text(encoding="utf-8", errors="ignore")))
                elif path.is_dir():
                    for f in list(path.rglob("*.md"))[:40] + list(path.rglob("*.json"))[:40]:
                        surfaces.append((str(f), f.read_text(encoding="utf-8", errors="ignore")))
    else:
        # Digital backlog exhausted: still reject field-kit DIGITAL_PRE_EVT / umbrella.
        scorecard = FP / "continuation_viii" / "READINESS_SCORECARD.json"
        if scorecard.exists():
            sc = load_json(scorecard)
            if sc.get("digital_pre_evt_release_ready") is True:
                hits.append(
                    "READINESS_SCORECARD.digital_pre_evt_release_ready=true forbidden "
                    "without Edmund acceptance pack"
                )

    forbidden_full = {
        "FULL_GUNNCHOS_PLATFORM_DIGITAL_COMPLETE",
        "FULL_GUNNCHAI3K_PLATFORM_DIGITAL_COMPLETE",
        "FULL_HARDWARE_DESIGN_RELEASE_COMPLETE",
        "FULL_PHYSICAL_VALIDATION_COMPLETE",
        "FULL_EXTERNAL_VALIDATION_COMPLETE",
        "FULL_CERTIFICATION_COMPLETE",
        "FULL_DEPLOYMENT_COMPLETE",
        "FULL_OPERATIONAL_PRODUCT",
        "FULL_RING_FIRMWARE_DIGITAL_COMPLETE",
    }
    assertive = re.compile(
        r"(?i)(token_earned\s*[:=]\s*true|"
        r"[\"']?(PASS|COMPLETE|EARNED|YES)[\"']?\s*$|"
        r":\s*true\b|"
        r"\b(earned|achieved|declared|granted)\b|"
        r"\bis complete\b|\bstatus:\s*complete\b)"
    )
    for path, text in surfaces:
        if not text:
            continue
        for i, line in enumerate(text.splitlines(), 1):
            toks = [t for t in FULL_TOKEN_RE.findall(line) if t in forbidden_full]
            if not toks:
                continue
            if ALLOW_LINE.search(line):
                continue
            # JSON false / list membership without assertion
            if re.search(r":\s*false\b", line) or line.strip().endswith(","):
                continue
            if not assertive.search(line):
                continue
            tok = toks[0]
            hits.append(
                f"{path}:{i}: {tok} asserted while digitally executable "
                f"SCHEMA/STUB backlog remains "
                f"(SCHEMA_ONLY={remaining['SCHEMA_ONLY']} "
                f"STUB_ONLY={remaining['STUB_ONLY']})"
                if soft_remaining > 0
                else f"{path}:{i}: {tok} asserted — FULL_* requires digital totality + Edmund"
            )


def check_hardware_placeholders(hits: list[str]) -> None:
    hw = load_yaml(HW_MATRIX)
    if hw.get("full_complete_claimed") is True:
        hits.append("hardware_release_matrix: full_complete_claimed=true forbidden under Cont VII")
    token = str(hw.get("token") or "")
    if "COMPLETE" in token and "CANDIDATE" not in token:
        hits.append(f"hardware_release_matrix: token={token!r} looks release-complete")

    hw_repo = SIBLING / "gunnchos-hardware-industrial-design"
    if not hw_repo.exists():
        return
    docs = hw_repo / "docs"
    assertive_claim = False
    if docs.exists():
        for f in docs.rglob("*.md"):
            for line in f.read_text(encoding="utf-8", errors="ignore").splitlines():
                if "FULL_HARDWARE_DESIGN_RELEASE_COMPLETE" not in line:
                    continue
                if ALLOW_LINE.search(line):
                    continue
                if re.search(r"(?i)(earned|achieved|claimed|complete:\s*true|: true)", line):
                    assertive_claim = True
                    break
            if assertive_claim:
                break
    if not assertive_claim:
        return
    placeholder_hits = []
    for pattern in ("**/*.kicad_sch", "**/*.kicad_pcb", "**/*BOM*.csv"):
        for f in hw_repo.glob(pattern):
            if not f.is_file():
                continue
            try:
                body = f.read_text(encoding="utf-8", errors="ignore")
            except Exception:
                continue
            if PLACEHOLDER_RE.search(body):
                placeholder_hits.append(str(f.relative_to(hw_repo)))
            if len(placeholder_hits) >= 10:
                break
    if placeholder_hits:
        hits.append(
            "hardware: FULL_HARDWARE_DESIGN_RELEASE_COMPLETE asserted while placeholder "
            f"EDA remains ({', '.join(placeholder_hits[:5])})"
        )


def check_firmware_smoke(hits: list[str]) -> None:
    edge = SIBLING / "edge-io-measurement-node"
    if not edge.exists():
        soft = load_yaml(SOFT_MATRIX)
        edge_entry = (soft.get("repos") or {}).get("edge-io-measurement-node") or {}
        note = str(edge_entry.get("note") or "")
        token_docs = str(edge_entry.get("token") or "")
        if "COMPLETE" in token_docs and "smoke" in note.lower():
            hits.append(
                "edge-io: firmware complete token while software_integration_matrix notes smoke-only"
            )
        return

    # Detect smoke-only main loops
    smoke_files = []
    for f in list(edge.rglob("main.c"))[:30] + list(edge.rglob("*.c"))[:80]:
        try:
            body = f.read_text(encoding="utf-8", errors="ignore")
        except Exception:
            continue
        if "printk" in body and ("k_msleep" in body or "k_sleep" in body):
            if not re.search(r"(?i)(iqs7222|npm1300|se050|bmi270|dw3000)", body):
                smoke_files.append(str(f.relative_to(edge)))
    claim_blob = ""
    for rel in ("README.md", "docs", "program"):
        path = edge / rel
        if path.is_file():
            claim_blob += path.read_text(encoding="utf-8", errors="ignore")
        elif path.is_dir():
            for f in list(path.rglob("*.md"))[:30]:
                claim_blob += f.read_text(encoding="utf-8", errors="ignore")
    claims_complete = bool(
        re.search(r"(?i)(FULL_RING_FIRMWARE|firmware complete|production main complete)", claim_blob)
        and not re.search(r"(?i)(not |never |forbidden|smoke-only|incomplete)", claim_blob)
    )
    if claims_complete and smoke_files:
        hits.append(
            "edge-io: firmware-complete claim while smoke-only main remains "
            f"({', '.join(smoke_files[:5])})"
        )


def check_global_and_carrier(hits: list[str]) -> None:
    conn = load_yaml(CONN_MATRIX)
    forbidden = set(conn.get("forbidden_claims") or [])
    text_surfaces = []
    for path in (CONN_MATRIX, AI_MATRIX, SOFT_MATRIX, FP / "deployment_support_matrix.yaml"):
        if path.exists():
            text_surfaces.append(path.read_text(encoding="utf-8", errors="ignore"))
    archive = SIBLING / "archive-of-life-artifact-world"
    if archive.exists():
        for f in list((archive / "docs").rglob("*.md"))[:40] if (archive / "docs").exists() else []:
            text_surfaces.append(f.read_text(encoding="utf-8", errors="ignore"))
    blob = "\n".join(text_surfaces)
    for claim in (
        "6G_certified",
        "final_IMT2030_compliant",
        "commercial_6G_carrier_accepted",
        "GATE_8_PASS",
        "global-complete",
        "all species ever discovered",
    ):
        for line in blob.splitlines():
            if claim.lower() not in line.lower():
                continue
            if ALLOW_LINE.search(line) or "forbidden_claims" in line:
                continue
            if line.strip().startswith("-") and not re.search(
                r"(?i)(is|achieved|earned|certified|complete|accepted)\b", line
            ):
                continue
            if re.search(
                rf"(?i)\b(is|achieved|earned|declared)\b.*{re.escape(claim)}|"
                rf"{re.escape(claim)}.*(earned|achieved|true|yes|pass)\b",
                line,
            ):
                hits.append(f"carrier/global claim exceeds truth: {line.strip()[:140]}")
                break


def main() -> int:
    hits: list[str] = []
    scan_prose(hits)
    check_game_tokens(hits)
    check_full_tokens(hits)
    check_hardware_placeholders(hits)
    check_firmware_smoke(hits)
    check_global_and_carrier(hits)
    check_cont_vii_umbrella(hits)
    check_stale_cont_vi_schema_copy(hits)

    if hits:
        print("CLAIM_FIREWALL_FAIL")
        for h in hits[:80]:
            print(h)
        if len(hits) > 80:
            print(f"... and {len(hits) - 80} more")
        return 1
    print("CLAIM_FIREWALL_PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
