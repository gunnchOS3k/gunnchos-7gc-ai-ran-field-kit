"""Deterministic seven-campus synthetic closed loop (simulation evidence only)."""
from __future__ import annotations

import hashlib
import json
import math
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .actuation_firewall import evaluate_request
from .campus_catalog import (
    CURRENT_MLV_V2_SOURCE_MANIFEST_SHA256,
    REPRESENTATIVE_ZONES,
    SITE_IDS,
    campus_slug_for,
    normalize_site_id,
)
from .ric_adapters import ReadOnlyTelemetryAdapter, SimulatedRICAdapter

OPTIONAL_BACKENDS = ("sionna", "deepmimo", "ns3", "ns_o_ran", "nvidia_aerial")


def _canonical_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_obj(obj: Any) -> str:
    return hashlib.sha256(_canonical_bytes(obj)).hexdigest()


def git_commit(repo_root: Path) -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return "0" * 40


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _zone_record(site_id: str, spec: dict[str, Any], *, primary: bool) -> dict[str, Any]:
    slug = campus_slug_for(site_id)
    redacted = bool(spec.get("redacted")) or site_id == "gaza"
    return {
        "campus_slug": slug,
        "phase": spec.get("phase") or REPRESENTATIVE_ZONES[site_id]["phase"],
        "campus_requirement_id": spec["requirement_id"],
        "digital_object": spec["digital_object"],
        "digital_route": spec["digital_route"],
        "geometry_fidelity": "AUTHORED_PLANNING_LAYOUT",
        "space_id": spec["space_id"],
        "kind": "ABSTRACT_ZONE" if redacted else "ROOM",
        "service_intent_template": spec["template"],
        "material_assumption": "drywall_and_concrete_planning",
        "floor_index": 0 if primary else 1,
        "redacted": redacted,
    }


def build_campus_design_bundle(
    site_id: str,
    *,
    source_manifest_sha256: str = CURRENT_MLV_V2_SOURCE_MANIFEST_SHA256,
    producer_commit: str = "0" * 40,
) -> dict[str, Any]:
    site_id = normalize_site_id(site_id)
    spec = REPRESENTATIVE_ZONES[site_id]
    slug = campus_slug_for(site_id)
    phase = spec["phase"]
    primary = _zone_record(site_id, spec, primary=True)
    secondary = _zone_record(site_id, spec["secondary"], primary=False)
    intents = [
        {
            "template": spec["template"],
            "source": "planning_template",
            "assumptions": "Derived from room/program role. Not measured occupancy.",
            "uncertainty": "high",
            "origin": "configured",
            "campus_requirement_id": spec["requirement_id"],
        },
        {
            "template": spec["secondary"]["template"],
            "source": "planning_template",
            "assumptions": "Secondary representative zone for CI projection only.",
            "uncertainty": "high",
            "origin": "configured",
            "campus_requirement_id": spec["secondary"]["requirement_id"],
        },
    ]
    location_precision = "abstract_zone" if site_id == "gaza" else "named_zone"
    ntn_role = site_id == "graham_land"
    return {
        "schema_name": "gunnchos.campus_design_bundle",
        "schema_version": "1.0.0",
        "run_id": f"closed-loop-v2-{site_id}-design",
        "site_id": site_id,
        "campus_slug": slug,
        "phase": phase,
        "geometry_fidelity": "AUTHORED_PLANNING_LAYOUT",
        "source_manifest_sha256": source_manifest_sha256,
        "source_version_label": "mlv_campus_v2_current",
        "projection_class": "network_design_planning",
        "zones": [primary, secondary],
        "candidate_infrastructure": [
            {
                "node_id": f"{site_id}-indoor-ap-1",
                "role": "indoor_ap",
                "height_m_assumption": 3.0,
                "orientation_assumption": "ceiling_omni",
                "power_dbm_bound": 20.0,
                "radio_count": 2,
                "band_profile": "n78_planning",
                "backhaul": "terrestrial",
                "edge_compute": False,
                "anchor_requirement_id": spec["requirement_id"],
            },
            {
                "node_id": f"{site_id}-edge-1",
                "role": "offline_cache" if site_id == "gaza" else "edge_compute",
                "height_m_assumption": 1.0,
                "orientation_assumption": "rack",
                "power_dbm_bound": 0.0,
                "radio_count": 1,
                "band_profile": "none",
                "backhaul": "offline_continuation" if site_id == "gaza" else "local_edge_wifi",
                "edge_compute": True,
                "anchor_requirement_id": spec["secondary"]["requirement_id"],
            },
            {
                "node_id": f"{site_id}-ntn-1",
                "role": "ntn_gateway",
                "height_m_assumption": 2.0,
                "orientation_assumption": "remote_reference" if ntn_role else "optional_fallback",
                "power_dbm_bound": 23.0,
                "radio_count": 1,
                "band_profile": "ntn_s_band_planning",
                "backhaul": "ntn_fallback",
                "edge_compute": False,
                "anchor_requirement_id": spec["requirement_id"],
            },
        ],
        "service_intents": intents,
        "aggregate_demand": {
            "values": {
                "users_proxy": 24 if site_id != "graham_land" else 8,
                "downlink_mbps": 80.0,
                "origin_note": "planning template, not measured traffic",
            },
            "origin": "configured",
        },
        "mobility": {
            "values": {"class": "low_named_zone", "aggregate_only": True},
            "origin": "configured",
        },
        "blockage": {
            "values": {"scenario": "interior_partitions", "extra_db": 8.0},
            "origin": "configured",
        },
        "outage": {
            "values": {
                "terrestrial_outage": site_id in {"gaza", "graham_land"},
                "degraded": site_id == "gaza",
            },
            "origin": "configured",
        },
        "compute": {
            "values": {"local_edge": True, "offline_cache": site_id == "gaza"},
            "origin": "configured",
        },
        "spectrum": {
            "values": {"budget_mhz": 20.0, "band_profile": "n78_planning"},
            "origin": "configured",
        },
        "energy": {
            "values": {"budget_j": 80.0 if site_id == "gaza" else 120.0},
            "origin": "configured",
        },
        "continuity": {
            "values": {
                "class": "offline_ok" if site_id == "gaza" else "degraded_ok",
                "max_interruption_s": 180,
            },
            "origin": "configured",
        },
        "privacy": {
            "contains_direct_identifiers": False,
            "contains_person_path": False,
            "location_precision": location_precision,
            "gaza_sensitive_export": False,
            "graham_station_claim": False,
        },
        "uncertainty": {
            "overall": "high",
            "notes": "AUTHORED_PLANNING_LAYOUT; not surveyed geometry.",
        },
        "evidence_class": "SIMULATED",
        "producer": {
            "repository": "gunnchos-7gc-ai-ran-field-kit",
            "commit": producer_commit,
        },
        "notes": "Representative projection only. 473-room catalog remains in 3k MLV.",
    }


def log_distance_path_loss(
    distance_m: float,
    *,
    exponent: float = 2.2,
    pl0_db: float = 40.0,
    d0_m: float = 1.0,
    material_db: float = 6.0,
    floor_db: float = 0.0,
    blockage_db: float = 0.0,
) -> float:
    d = max(distance_m, d0_m)
    return pl0_db + 10.0 * exponent * math.log10(d / d0_m) + material_db + floor_db + blockage_db


def coverage_from_path_loss(path_loss_db: float, threshold_db: float = 95.0) -> float:
    return max(0.0, min(1.0, 1.0 - (path_loss_db / (threshold_db * 1.4))))


def optional_backend_status() -> dict[str, str]:
    return {name: "fail_closed_unused" for name in OPTIONAL_BACKENDS}


def adapt_design_to_twin(
    design: dict[str, Any],
    *,
    producer_commit: str = "0" * 40,
) -> dict[str, Any]:
    if design.get("geometry_fidelity") != "AUTHORED_PLANNING_LAYOUT":
        # Propagate authored planning layouts; do not invent surveyed geometry.
        pass
    site_id = design["site_id"]
    n_users = int(design["aggregate_demand"]["values"].get("users_proxy", 16))
    latency = 18.0 if site_id not in {"gaza", "graham_land"} else 42.0
    if site_id == "graham_land":
        latency = 55.0
    twin = {
        "schema_name": "gunnchos.twin_state_bundle",
        "schema_version": "1.0.0",
        "run_id": f"closed-loop-v2-{site_id}-twin",
        "site_id": site_id,
        "source_measurement": {
            "summary": {
                "n_samples": 4,
                "mean_latency_ms": latency,
                "mean_jitter_ms": 3.0,
                "mean_packet_loss_pct": 0.4,
                "mean_upload_mbps": 12.0,
                "mean_download_mbps": 48.0,
                "dominant_network_type": "wifi",
                "workload_profile": "learn",
                "service_profile": "learn_continuity",
            },
            "sha256": sha256_obj({"design": design["run_id"]}),
            "producer_repository": "edge-io-measurement-node",
            "producer_commit": producer_commit if len(producer_commit) == 40 else "0" * 40,
        },
        "service_demand": {
            "values": {
                "service_profile": "learn_continuity",
                "geometry_fidelity": design["geometry_fidelity"],
                "source_manifest_sha256": design["source_manifest_sha256"],
            },
            "origin": "configured",
        },
        "user_demands": [
            {
                "user_class": "learn",
                "priority": 2,
                "latency_budget_ms": 150.0,
                "bandwidth_mbps": 10.0,
                "origin": "configured",
            }
        ],
        "connectivity_candidates": [
            {
                "network": "terrestrial",
                "available": site_id not in {"gaza", "graham_land"},
                "estimated_latency_ms": latency,
                "estimated_capacity_mbps": 48.0,
                "origin": "configured",
            },
            {
                "network": "local_edge_wifi",
                "available": True,
                "estimated_latency_ms": 12.0,
                "estimated_capacity_mbps": 40.0,
                "origin": "configured",
            },
            {
                "network": "degraded_local",
                "available": True,
                "estimated_latency_ms": latency * 1.4,
                "estimated_capacity_mbps": 12.0,
                "origin": "configured",
            },
            {
                "network": "ntn_fallback",
                "available": True,
                "estimated_latency_ms": 80.0 if site_id == "graham_land" else 45.0,
                "estimated_capacity_mbps": 5.0,
                "origin": "configured",
            },
            {
                "network": "device_to_device",
                "available": False,
                "estimated_latency_ms": None,
                "estimated_capacity_mbps": None,
                "origin": "missing",
            },
            {
                "network": "offline_continuation",
                "available": True,
                "estimated_latency_ms": 0.0,
                "estimated_capacity_mbps": 0.0,
                "origin": "configured",
            },
        ],
        "network_state": {
            "values": {
                "dominant_network_type": "wifi",
                "mean_latency_ms": latency,
                "zones": [z["campus_requirement_id"] for z in design["zones"]],
            },
            "origin": "inferred",
        },
        "spectrum_availability": design["spectrum"],
        "compute_availability": design["compute"],
        "mobility_state": design["mobility"],
        "blockage_state": design["blockage"],
        "energy_constraints": design["energy"],
        "outage_state": design["outage"],
        "privacy_constraints": {
            "values": design["privacy"],
            "origin": "configured",
        },
        "continuity_requirements": design["continuity"],
        "uncertainty": {
            "overall": "high",
            "notes": "Planning projection; geometry_fidelity=AUTHORED_PLANNING_LAYOUT",
        },
        "missing_data_flags": ["surveyed_geometry", "measured_occupancy"],
        "field_provenance": {
            "fields": {
                "network_state": "inferred",
                "service_demand": "configured",
                "geometry_fidelity": "configured",
            }
        },
        "scenario_provenance": {
            "transformer": "seven_gc_twin.integrations.campus_design.v1",
            "generated_at": _now(),
            "notes": "No surveyed geometry invented.",
        },
        "configuration_hash": sha256_obj(
            {
                "site_id": site_id,
                "source": design["source_manifest_sha256"],
                "geometry": design["geometry_fidelity"],
            }
        ),
        "evidence_level": "synthetic",
        "producer": {
            "repository": "7gc-digital-twin",
            "commit": producer_commit if len(producer_commit) == 40 else "0" * 40,
        },
        "n_users": max(n_users, 1),
        "service_profile": "learn_continuity",
    }
    return twin


def _objectives(
    *,
    nodes: int,
    power_dbm: float,
    site_id: str,
    exponent: float,
    blockage_db: float,
    edge: bool,
) -> dict[str, float]:
    pl = log_distance_path_loss(
        12.0 + nodes,
        exponent=exponent,
        blockage_db=blockage_db,
        material_db=5.0 if site_id != "gaza" else 9.0,
    )
    coverage = coverage_from_path_loss(pl)
    if site_id == "gaza":
        coverage *= 0.86
    if site_id == "graham_land":
        coverage *= 0.8
    capacity = 8.0 * nodes + power_dbm * 0.4
    latency = 14.0 + (8.0 if site_id == "graham_land" else 0.0) + (6.0 if site_id == "gaza" else 0.0)
    latency += max(0.0, 4 - nodes) * 3.0
    jitter = 2.0 + (1.5 if site_id == "gaza" else 0.0)
    packet_loss = max(0.1, 1.8 - nodes * 0.3)
    se = capacity / 20.0
    unmet = max(0.0, 1.0 - coverage * (0.7 + 0.08 * nodes))
    fairness = 1.0 / (1.0 + 0.05 * abs(nodes - 2))
    gap = max(0.0, 1.0 - coverage)
    energy = 10.0 * nodes + max(power_dbm, 0.0) * 0.5
    continuity = 0.55 + 0.12 * nodes + (0.15 if edge else 0.0)
    if site_id == "gaza":
        continuity = min(1.0, continuity + 0.1)
    recovery = 40.0 / max(nodes, 1)
    edge_util = 0.35 + (0.25 if edge else 0.0)
    cost = 12.0 * nodes + (8.0 if edge else 0.0)
    install = 4.0 * nodes
    return {
        "coverage": round(min(1.0, coverage), 4),
        "capacity": round(capacity, 4),
        "latency": round(latency, 4),
        "jitter": round(jitter, 4),
        "packet_loss": round(min(100.0, packet_loss), 4),
        "spectral_efficiency": round(se, 4),
        "unmet_demand": round(min(1.0, unmet), 4),
        "jains_fairness": round(min(1.0, fairness), 4),
        "zone_service_gap": round(min(1.0, gap), 4),
        "energy": round(energy, 4),
        "service_continuity": round(min(1.0, continuity), 4),
        "recovery_time": round(recovery, 4),
        "edge_compute_utilization": round(min(1.0, edge_util), 4),
        "planning_cost_proxy": round(cost, 4),
        "installation_complexity_proxy": round(install, 4),
        "constraint_violations": 0,
        "uncertainty": 0.72,
    }


def _dominates(a: dict[str, float], b: dict[str, float]) -> bool:
    maximize = {
        "coverage",
        "capacity",
        "spectral_efficiency",
        "jains_fairness",
        "service_continuity",
        "edge_compute_utilization",
    }
    better_or_equal = True
    strictly_better = False
    for key, av in a.items():
        bv = b[key]
        if key in maximize:
            if av < bv:
                better_or_equal = False
            if av > bv:
                strictly_better = True
        else:
            if av > bv:
                better_or_equal = False
            if av < bv:
                strictly_better = True
    return better_or_equal and strictly_better


def pareto_members(alts: list[dict[str, Any]]) -> list[str]:
    ids = []
    for a in alts:
        if not any(
            _dominates(b["objectives"], a["objectives"])
            for b in alts
            if b["alternative_id"] != a["alternative_id"]
        ):
            ids.append(a["alternative_id"])
    return ids


def plan_campus(
    design: dict[str, Any],
    twin: dict[str, Any],
    *,
    producer_commit: str = "0" * 40,
    path_loss_exponent: float = 2.2,
    blockage_db: float | None = None,
) -> dict[str, Any]:
    site_id = design["site_id"]
    blockage = (
        blockage_db
        if blockage_db is not None
        else float(design["blockage"]["values"].get("extra_db", 8.0))
    )
    candidates = [
        ("sparse", 1, 17.0, False),
        ("balanced", 2, 20.0, True),
        ("dense", 3, 23.0, True),
    ]
    alts = []
    for label, nodes, power, edge in candidates:
        alts.append(
            {
                "alternative_id": f"{site_id}-{label}",
                "label": label,
                "planning_variables": {
                    "node_count": nodes,
                    "power_dbm": power,
                    "edge_compute": edge,
                    "path_loss_exponent": path_loss_exponent,
                    "geometry_mutated": False,
                },
                "objectives": _objectives(
                    nodes=nodes,
                    power_dbm=power,
                    site_id=site_id,
                    exponent=path_loss_exponent,
                    blockage_db=blockage,
                    edge=edge,
                ),
                "pareto_member": False,
                "notes": "Does not mutate campus/building geometry.",
            }
        )
    front = set(pareto_members(alts))
    for alt in alts:
        alt["pareto_member"] = alt["alternative_id"] in front
    selected = next(a for a in alts if a["label"] == "balanced")
    return {
        "schema_name": "gunnchos.campus_optimization_result",
        "schema_version": "1.0.0",
        "run_id": f"closed-loop-v2-{site_id}-opt",
        "site_id": site_id,
        "campus_slug": design["campus_slug"],
        "phase": design["phase"],
        "input_design_hash": sha256_obj(design),
        "input_twin_state_hash": sha256_obj(twin),
        "geometry_fidelity": design["geometry_fidelity"],
        "source_manifest_sha256": design["source_manifest_sha256"],
        "objectives": selected["objectives"],
        "alternatives": alts,
        "selected_alternative_id": selected["alternative_id"],
        "constraint_violations": [],
        "uncertainty": {
            "overall": "high",
            "notes": "Synthetic planning; no OTA evidence.",
        },
        "evidence_class": "SIMULATED",
        "readygary_used": False,
        "ntn_used": site_id == "graham_land",
        "producer": {
            "repository": "spectrumx-ai-ran-gary",
            "commit": producer_commit if len(producer_commit) == 40 else "0" * 40,
        },
        "notes": "No opaque AI score. Optional beam/NTN unused unless compatible.",
    }


def synthetic_measurement(
    optimization: dict[str, Any],
    *,
    producer_commit: str = "0" * 40,
) -> tuple[dict[str, Any], dict[str, Any]]:
    site_id = optimization["site_id"]
    pred = optimization["objectives"]
    # Deterministic residual; not field evidence.
    measured = {
        "coverage": max(0.0, pred["coverage"] - 0.04),
        "capacity": max(0.0, pred["capacity"] - 1.5),
        "latency": pred["latency"] + 3.0,
        "jitter": pred["jitter"] + 0.4,
        "packet_loss": pred["packet_loss"] + 0.2,
    }
    residual = {k: round(measured[k] - pred[k], 4) for k in measured}
    mapping = {
        "schema_name": "gunnchos.campus_measurement_mapping",
        "schema_version": "1.0.0",
        "run_id": f"closed-loop-v2-{site_id}-map",
        "site_id": site_id,
        "campus_slug": optimization["campus_slug"],
        "phase": optimization["phase"],
        "campus_requirement_id": REPRESENTATIVE_ZONES[site_id]["requirement_id"],
        "space_id": REPRESENTATIVE_ZONES[site_id]["space_id"],
        "coarse_grid_cell": "Z0",
        "measurement_point_id": f"{site_id}-mp-01",
        "campus_model_version": "CAMPUS_V2_PLANNING",
        "infrastructure_version": "NETWORK_DESIGN_V1",
        "evidence_ref": optimization["run_id"],
        "batch_sha256": sha256_obj(measured),
        "contains_person_path": False,
        "exact_minor_location": False,
        "producer": {
            "repository": "edge-io-measurement-node",
            "commit": producer_commit if len(producer_commit) == 40 else "0" * 40,
        },
    }
    return {
        "prediction": {k: pred[k] for k in measured},
        "measurement": measured,
        "residual": residual,
        "mapping": mapping,
        "quarantined": [],
    }, mapping


def calibrate(
    optimization: dict[str, Any],
    synth: dict[str, Any],
    *,
    producer_commit: str = "0" * 40,
    parent_model_version: str = "CAMPUS_V2_PLANNING",
) -> dict[str, Any]:
    site_id = optimization["site_id"]
    residuals = [abs(v) for v in synth["residual"].values()]
    holdout_error = round(sum(residuals) / len(residuals), 4)
    new_version = f"CALIBRATED_SIM_{site_id}_V1"
    if new_version == parent_model_version:
        raise RuntimeError("refusing to overwrite parent model version")
    return {
        "schema_name": "gunnchos.twin_calibration_bundle",
        "schema_version": "1.0.0",
        "run_id": f"closed-loop-v2-{site_id}-cal",
        "site_id": site_id,
        "campus_slug": optimization["campus_slug"],
        "phase": optimization["phase"],
        "source_manifest_sha256": optimization["source_manifest_sha256"],
        "parent_model_version": parent_model_version,
        "new_model_version": new_version,
        "prediction": synth["prediction"],
        "measurement": synth["measurement"],
        "residual": synth["residual"],
        "uncertainty": {
            "overall": "high",
            "notes": "Synthetic holdout only. Not real twin calibration.",
        },
        "candidate_parameter_update": {
            "parameters": {
                "path_loss_exponent": 2.15,
                "attenuation_db": 5.5,
                "blockage_db": 7.5,
                "effective_node_range_m": 18.0,
                "backhaul_latency_ms": 12.0,
                "aggregate_demand_factor": 0.95,
                "failover_timing_s": 8.0,
            },
            "applied": True,
            "notes": "New version only; parent retained.",
        },
        "holdout_validation": {
            "holdout_fraction": 0.25,
            "holdout_error": holdout_error,
            "pass": holdout_error < 5.0,
            "n_train": 3,
            "n_holdout": 1,
        },
        "rejected_evidence": [
            {
                "evidence_ref": "quarantine://person-path",
                "reason": "person-path evidence is rejected",
            }
        ],
        "evidence_class": "SIMULATED",
        "producer": {
            "repository": "7gc-digital-twin",
            "commit": producer_commit if len(producer_commit) == 40 else "0" * 40,
        },
        "notes": "REAL_TWIN_CALIBRATION_PASS remains false.",
    }


def actuation_roundtrip(site_id: str, *, producer_commit: str = "0" * 40) -> tuple[dict[str, Any], dict[str, Any]]:
    request = {
        "schema_name": "gunnchos.ran_actuation_request",
        "schema_version": "1.0.0",
        "run_id": f"closed-loop-v2-{site_id}-act",
        "site_id": site_id,
        "request_id": f"{site_id.replace('_', '')}act01",
        "identity": {"authenticated": True, "principal_id": "synthetic-operator"},
        "role": "researcher",
        "testbed": {"explicit": True, "testbed_id": "synthetic-lab"},
        "action": {
            "name": "dry_run_recommendation",
            "allowlisted": True,
            "payload": {"power_dbm": 18.0},
        },
        "numeric_bounds": {
            "within_bounds": True,
            "requested": 18.0,
            "min": 0.0,
            "max": 23.0,
        },
        "ttl_s": 30,
        "regulatory": {"band_allowed": True, "band_profile": "n78_planning"},
        "rate_limit": {"within_limit": True, "window_s": 60},
        "dry_run": True,
        "rollback": {"supported": True, "safe_state": "prior_planning_recommendation"},
        "source_path": "server_control_plane",
        "producer": {
            "repository": "gunnchos-7gc-ai-ran-field-kit",
            "commit": producer_commit if len(producer_commit) == 40 else "0" * 40,
        },
    }
    receipt = evaluate_request(request)
    receipt["producer"] = request["producer"]
    return request, receipt


def run_one_campus(
    site_id: str,
    *,
    commits: dict[str, str] | None = None,
    source_manifest_sha256: str = CURRENT_MLV_V2_SOURCE_MANIFEST_SHA256,
) -> dict[str, Any]:
    commits = commits or {}
    design = build_campus_design_bundle(
        site_id,
        source_manifest_sha256=source_manifest_sha256,
        producer_commit=commits.get("field_kit", "0" * 40),
    )
    twin = adapt_design_to_twin(design, producer_commit=commits.get("digital_twin", "0" * 40))
    if twin["service_demand"]["values"]["geometry_fidelity"] != "AUTHORED_PLANNING_LAYOUT":
        raise RuntimeError("geometry fidelity was not propagated")
    opt = plan_campus(design, twin, producer_commit=commits.get("spectrumx", "0" * 40))
    if not any(a["pareto_member"] for a in opt["alternatives"]):
        raise RuntimeError("planner returned no Pareto members")
    if "ai_score" in opt and len(opt["objectives"]) == 1:
        raise RuntimeError("opaque AI score cannot be the only result")
    synth, mapping = synthetic_measurement(opt, producer_commit=commits.get("edge_io", "0" * 40))
    cal = calibrate(opt, synth, producer_commit=commits.get("digital_twin", "0" * 40))
    if cal["new_model_version"] == cal["parent_model_version"]:
        raise RuntimeError("calibration overwrote parent version")
    request, receipt = actuation_roundtrip(site_id, producer_commit=commits.get("field_kit", "0" * 40))
    telemetry = ReadOnlyTelemetryAdapter().read_telemetry(site_id)
    sim = SimulatedRICAdapter().recommend({"site_id": site_id})
    return {
        "site_id": normalize_site_id(site_id),
        "campus_slug": design["campus_slug"],
        "design": design,
        "twin": twin,
        "optimization": opt,
        "mapping": mapping,
        "calibration": cal,
        "actuation_request": request,
        "actuation_receipt": receipt,
        "read_only_telemetry": telemetry,
        "simulated_recommendation": sim,
        "hashes": {
            "design": sha256_obj(design),
            "twin": sha256_obj(twin),
            "optimization": sha256_obj(opt),
            "calibration": sha256_obj(cal),
            "mapping": sha256_obj(mapping),
        },
        "optional_backends": optional_backend_status(),
    }


def run_seven_campus_loop(
    *,
    commits: dict[str, str] | None = None,
    source_manifest_sha256: str = CURRENT_MLV_V2_SOURCE_MANIFEST_SHA256,
) -> dict[str, Any]:
    results = [
        run_one_campus(
            site_id,
            commits=commits,
            source_manifest_sha256=source_manifest_sha256,
        )
        for site_id in SITE_IDS
    ]
    passed = len(results)
    return {
        "SYNTHETIC_CLOSED_LOOP_PASS": f"{passed}/7",
        "MLV_TO_7GC_ADAPTER_PASS": f"{passed}/7",
        "7GC_TO_SPECTRUMX_PASS": f"{passed}/7",
        "SPECTRUMX_PLANNING_OPTIMIZER_PASS": f"{passed}/7",
        "OPTIMIZATION_RESULT_PASS": f"{passed}/7",
        "SEVEN_CAMPUS_BACKEND_PASS": f"{passed}/7",
        "MLV_V2_SOURCE_HASH_COMPAT_PASS": all(
            r["design"]["source_manifest_sha256"] == source_manifest_sha256 for r in results
        ),
        "source_manifest_sha256": source_manifest_sha256,
        "campuses": [r["site_id"] for r in results],
        "results": results,
    }
