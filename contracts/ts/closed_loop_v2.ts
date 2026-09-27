/**
 * TS-compatible contract shapes for the 3k MLV Network Twin child of PR #2.
 * Canonical JSON Schemas live in ../. Do not infer fields.
 */

export type GeometryFidelity = "AUTHORED_PLANNING_LAYOUT" | "AS_BUILT_SURVEYED" | "MIXED";

export type EvidenceClass =
  | "SIMULATED"
  | "OPEN_DATA_BACKED"
  | "CONFIGURED_ASSUMPTION"
  | "CONTROLLED_DEVICE_MEASUREMENT"
  | "SDR_MEASURED"
  | "LAB_INSTRUMENT_MEASURED"
  | "RAN_TELEMETRY_MEASURED"
  | "FIELD_VALIDATED"
  | "MIXED";

export type SiteId =
  | "gary"
  | "ghana"
  | "guyana"
  | "geelong"
  | "germany"
  | "gaza"
  | "graham_land";

export type CampusSlug =
  | "gary"
  | "ghana"
  | "guyana"
  | "geelong"
  | "germany"
  | "gaza"
  | "graham-land"
  | "graham_land";

export interface CampusZoneRef {
  campus_slug: CampusSlug | string;
  phase: string;
  campus_requirement_id: string;
  digital_object: string;
  digital_route: string;
  geometry_fidelity: GeometryFidelity;
  space_id: string;
  kind: "ROOM" | "ZONE" | "PROGRAM" | "ABSTRACT_ZONE";
  service_intent_template: string;
  redacted?: boolean;
}

export interface CampusDesignBundleV1 {
  schema_name: "gunnchos.campus_design_bundle";
  schema_version: string;
  run_id: string;
  site_id: SiteId;
  campus_slug: CampusSlug;
  phase: string;
  geometry_fidelity: GeometryFidelity;
  source_manifest_sha256: string;
  projection_class: "network_design_planning";
  zones: CampusZoneRef[];
  evidence_class: EvidenceClass;
}

export interface ObjectiveVectorV1 {
  coverage: number;
  capacity: number;
  latency: number;
  jitter: number;
  packet_loss: number;
  spectral_efficiency: number;
  unmet_demand: number;
  jains_fairness: number;
  zone_service_gap: number;
  energy: number;
  service_continuity: number;
  recovery_time: number;
  edge_compute_utilization: number;
  planning_cost_proxy: number;
  installation_complexity_proxy: number;
  constraint_violations: number;
  uncertainty: number;
}

export interface CampusOptimizationResultV1 {
  schema_name: "gunnchos.campus_optimization_result";
  schema_version: string;
  run_id: string;
  site_id: string;
  campus_slug: string;
  phase: string;
  input_design_hash: string;
  input_twin_state_hash: string;
  geometry_fidelity: string;
  source_manifest_sha256: string;
  objectives: ObjectiveVectorV1;
  alternatives: Array<{
    alternative_id: string;
    label: string;
    planning_variables: Record<string, unknown>;
    objectives: ObjectiveVectorV1;
    pareto_member: boolean;
  }>;
  selected_alternative_id: string;
  evidence_class: EvidenceClass;
  readygary_used: boolean;
  ntn_used: boolean;
}

export interface TwinCalibrationBundleV1 {
  schema_name: "gunnchos.twin_calibration_bundle";
  schema_version: string;
  run_id: string;
  site_id: string;
  parent_model_version: string;
  new_model_version: string;
  prediction: Record<string, number>;
  measurement: Record<string, number>;
  residual: Record<string, number>;
  holdout_validation: {
    holdout_fraction: number;
    holdout_error: number;
    pass: boolean;
    n_train: number;
    n_holdout: number;
  };
}

export interface CampusMeasurementMappingV1 {
  schema_name: "gunnchos.campus_measurement_mapping";
  schema_version: string;
  campus_slug: string;
  phase: string;
  campus_requirement_id: string;
  space_id: string;
  coarse_grid_cell: string;
  measurement_point_id: string;
  campus_model_version: string;
  infrastructure_version: string;
  evidence_ref: string;
  contains_person_path: false;
  exact_minor_location: false;
}

export interface RanActuationRequestV1 {
  schema_name: "gunnchos.ran_actuation_request";
  dry_run: boolean;
  source_path: "server_control_plane" | "cli" | "authorized_testbed_agent";
}

export interface RanActuationReceiptV1 {
  schema_name: "gunnchos.ran_actuation_receipt";
  decision: "denied" | "dry_run_recorded" | "shadow_recorded" | "applied_testbed";
  real_actuation_enabled: boolean;
  e2_claimed: false;
  applied: boolean;
}

export const CURRENT_MLV_V2_SOURCE_MANIFEST_SHA256 =
  "520cbba99541b1505ebba899a2f34bfa905eadd7af8f5b5e8fa050c884067be1";

export const EXAMPLE_REQUIREMENT_IDS = [
  "GARY.FULL.HARDWARE_REPAIR_LAB",
  "GHANA.FULL.MENTOR_WORKSPACE",
  "GUYANA.FULL.CLIMATE_GIS_STUDIO",
  "GEELONG.FULL.DESIGN_BUILD_STUDIO",
  "GERMANY.FULL.INDUSTRY40_TWIN_LAB",
  "GAZA.RECOVERY.OFFLINE_LEARNING_STUDIO",
  "GRAHAM.FULL.NTN_LAB",
] as const;
