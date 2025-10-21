/**
 * Type definitions for risk assessment
 */

export type RiskScenario = 'rcp26' | 'rcp45' | 'rcp85';

export type HazardType = 'flood' | 'drought' | 'heat_stress' | 'landslide' | 'coastal_inundation';

export interface HazardIndicator {
  hazard_type: HazardType;
  current_risk: number;
  projected_2030: number;
  projected_2050: number;
  data_source: string;
  confidence: number;
}

export interface VulnerabilityIndicator {
  population_exposed: number;
  critical_infrastructure_count: number;
  vulnerable_population_pct: number;
  adaptive_capacity_score: number;
}

export interface MunicipalRisk {
  ibge_code: string;
  municipality_name: string;
  scenario: RiskScenario;
  overall_risk_score: number;
  hazards: HazardIndicator[];
  vulnerability: VulnerabilityIndicator;
  h3_grid_data?: Record<string, number>;
  recommendations: string[];
}

export interface H3Cell {
  h3_index: string;
  resolution: number;
  risk_score: number;
  flood?: number;
  drought?: number;
  heat_stress?: number;
}

export interface H3GridData {
  ibge_code: string;
  resolution: number;
  scenario: string;
  heatmap: Record<string, number>;
}

export interface LocationRisk {
  latitude: number;
  longitude: number;
  scenario: string;
  overall_risk: number;
  hazards: Record<string, {
    current: number;
    projected_2030: number;
    projected_2050: number;
    confidence: number;
  }>;
}
