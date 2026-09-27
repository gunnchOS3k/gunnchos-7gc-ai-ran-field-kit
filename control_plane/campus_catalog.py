"""Representative campus projection catalog.

This is not an independent 473-room source of truth. It references
current MLV Campus V2 requirement IDs and the current source-manifest
hash as a version identifier only.
"""
from __future__ import annotations

# Current 3k MLV Campus V2 source-manifest digest. Treat as the current
# source-version identifier, not a permanent global constant.
CURRENT_MLV_V2_SOURCE_MANIFEST_SHA256 = (
    "520cbba99541b1505ebba899a2f34bfa905eadd7af8f5b5e8fa050c884067be1"
)

SITE_IDS = (
    "gary",
    "ghana",
    "guyana",
    "geelong",
    "germany",
    "gaza",
    "graham_land",
)

MLV_SLUG_TO_SITE = {
    "gary": "gary",
    "ghana": "ghana",
    "guyana": "guyana",
    "geelong": "geelong",
    "germany": "germany",
    "gaza": "gaza",
    "graham-land": "graham_land",
    "graham_land": "graham_land",
}

SITE_TO_MLV_SLUG = {
    "gary": "gary",
    "ghana": "ghana",
    "guyana": "guyana",
    "geelong": "geelong",
    "germany": "germany",
    "gaza": "gaza",
    "graham_land": "graham-land",
}

# Representative zones only. Full room authority remains in 3k MLV PR #2.
REPRESENTATIVE_ZONES = {
    "gary": {
        "phase": "FULL",
        "requirement_id": "GARY.FULL.HARDWARE_REPAIR_LAB",
        "digital_object": "gary.full.hardware_repair_lab",
        "digital_route": "#/mlv/campus/gary/full/hardware-repair-lab",
        "space_id": "hardware_repair_lab",
        "name": "Hardware / repair lab",
        "template": "repair_lab",
        "secondary": {
            "requirement_id": "GARY.PILOT.FLEXIBLE_CLASSROOM",
            "digital_object": "gary.pilot.flexible_classroom",
            "digital_route": "#/mlv/campus/gary/pilot/flexible-classroom",
            "space_id": "flexible_classroom",
            "name": "Flexible classroom",
            "template": "classroom",
            "phase": "PILOT",
        },
    },
    "ghana": {
        "phase": "FULL",
        "requirement_id": "GHANA.FULL.MENTOR_WORKSPACE",
        "digital_object": "ghana.full.mentor_workspace",
        "digital_route": "#/mlv/campus/ghana/full/mentor-workspace",
        "space_id": "mentor_workspace",
        "name": "Mentor / visiting instructor workspace",
        "template": "hybrid_lecture",
        "secondary": {
            "requirement_id": "GHANA.PILOT.FLEXIBLE_CLASSROOM",
            "digital_object": "ghana.pilot.flexible_classroom",
            "digital_route": "#/mlv/campus/ghana/pilot/flexible-classroom",
            "space_id": "flexible_classroom",
            "name": "Flexible classroom",
            "template": "classroom",
            "phase": "PILOT",
        },
    },
    "guyana": {
        "phase": "FULL",
        "requirement_id": "GUYANA.FULL.CLIMATE_GIS_STUDIO",
        "digital_object": "guyana.full.climate_gis_studio",
        "digital_route": "#/mlv/campus/guyana/full/climate-gis-studio",
        "space_id": "climate_gis_studio",
        "name": "Climate / GIS + digital twin studio",
        "template": "gis_climate",
        "secondary": {
            "requirement_id": "GUYANA.PILOT.FLEXIBLE_CLASSROOM",
            "digital_object": "guyana.pilot.flexible_classroom",
            "digital_route": "#/mlv/campus/guyana/pilot/flexible-classroom",
            "space_id": "flexible_classroom",
            "name": "Flexible classroom",
            "template": "classroom",
            "phase": "PILOT",
        },
    },
    "geelong": {
        "phase": "FULL",
        "requirement_id": "GEELONG.FULL.DESIGN_BUILD_STUDIO",
        "digital_object": "geelong.full.design_build_studio",
        "digital_route": "#/mlv/campus/geelong/full/design-build-studio",
        "space_id": "design_build_studio",
        "name": "Design / build + prototyping studio",
        "template": "media_collaboration",
        "secondary": {
            "requirement_id": "GEELONG.PILOT.FLEXIBLE_CLASSROOM",
            "digital_object": "geelong.pilot.flexible_classroom",
            "digital_route": "#/mlv/campus/geelong/pilot/flexible-classroom",
            "space_id": "flexible_classroom",
            "name": "Flexible classroom",
            "template": "classroom",
            "phase": "PILOT",
        },
    },
    "germany": {
        "phase": "FULL",
        "requirement_id": "GERMANY.FULL.INDUSTRY40_TWIN_LAB",
        "digital_object": "germany.full.industry40_twin_lab",
        "digital_route": "#/mlv/campus/germany/full/industry40-twin-lab",
        "space_id": "industry40_twin_lab",
        "name": "Industry 4.0 + digital twin lab",
        "template": "industry40",
        "secondary": {
            "requirement_id": "GERMANY.PILOT.FLEXIBLE_CLASSROOM",
            "digital_object": "germany.pilot.flexible_classroom",
            "digital_route": "#/mlv/campus/germany/pilot/flexible-classroom",
            "space_id": "flexible_classroom",
            "name": "Flexible classroom",
            "template": "classroom",
            "phase": "PILOT",
        },
    },
    "gaza": {
        "phase": "FULL_RECOVERY_EDUCATION_HUB",
        "requirement_id": "GAZA.RECOVERY.OFFLINE_LEARNING_STUDIO",
        "digital_object": "gaza.recovery.offline_learning_studio",
        "digital_route": "#/mlv/campus/gaza/recovery/offline-learning-studio",
        "space_id": "offline_learning_studio",
        "name": "Offline learning studio",
        "template": "offline_recovery",
        "redacted": True,
        "secondary": {
            "requirement_id": "GAZA.RECOVERY_NETWORK.SAFE_TEMPORARY_LEARNING_CIRCLE",
            "digital_object": "gaza.recovery.abstract_learning_zone",
            "digital_route": "#/mlv/campus/gaza/recovery/abstract-learning-zone",
            "space_id": "abstract_learning_zone",
            "name": "Abstract recovery learning zone",
            "template": "offline_recovery",
            "phase": "RECOVERY_NETWORK",
            "redacted": True,
        },
    },
    "graham_land": {
        "phase": "NON_ANTARCTIC_POLAR_EDUCATION_HUB",
        "requirement_id": "GRAHAM.FULL.NTN_LAB",
        "digital_object": "graham-land.full.ntn_lab",
        "digital_route": "#/mlv/campus/graham-land/full/ntn-lab",
        "space_id": "ntn_lab",
        "name": "Networking / NTN lab",
        "template": "ntn_remote_sensing",
        "remote_only": True,
        "secondary": {
            "requirement_id": "GRAHAM.REMOTE.FLEXIBLE_VIRTUAL_CLASSROOM",
            "digital_object": "graham-land.remote.flexible_virtual_classroom",
            "digital_route": "#/mlv/campus/graham-land/remote/flexible-virtual-classroom",
            "space_id": "flexible_virtual_classroom",
            "name": "Flexible / virtual classroom",
            "template": "hybrid_lecture",
            "phase": "REMOTE_LEARNING_LAB",
        },
    },
}


def normalize_site_id(value: str) -> str:
    key = value.strip().lower().replace(" ", "_")
    if key not in MLV_SLUG_TO_SITE:
        raise ValueError(f"Unknown campus identity: {value}")
    return MLV_SLUG_TO_SITE[key]


def campus_slug_for(site_id: str) -> str:
    return SITE_TO_MLV_SLUG[normalize_site_id(site_id)]
