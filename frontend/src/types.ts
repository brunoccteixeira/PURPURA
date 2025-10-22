/**
 * Type definitions for PÚRPURA Climate Risk Assessment
 */

export type RiskScenario = 'rcp26' | 'rcp45' | 'rcp85';

export type HazardType =
  | 'flood'
  | 'drought'
  | 'heat_stress'
  | 'landslide'
  | 'coastal_inundation';

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

export interface Municipality {
  ibge_code: string;
  name: string;
  state: string;
}

export const HAZARD_LABELS: Record<HazardType, string> = {
  flood: 'Inundação',
  drought: 'Seca',
  heat_stress: 'Estresse Térmico',
  landslide: 'Deslizamento',
  coastal_inundation: 'Inundação Costeira',
};

export const SCENARIO_LABELS: Record<RiskScenario, string> = {
  rcp26: 'RCP 2.6 (Baixas Emissões)',
  rcp45: 'RCP 4.5 (Emissões Moderadas)',
  rcp85: 'RCP 8.5 (Altas Emissões)',
};

export function getRiskLevel(score: number): 'low' | 'moderate' | 'high' | 'extreme' {
  if (score < 0.25) return 'low';
  if (score < 0.50) return 'moderate';
  if (score < 0.75) return 'high';
  return 'extreme';
}

export function getRiskColor(score: number): string {
  const level = getRiskLevel(score);
  const colors = {
    low: 'text-risk-low',
    moderate: 'text-risk-moderate',
    high: 'text-risk-high',
    extreme: 'text-risk-extreme',
  };
  return colors[level];
}

export function getRiskBgColor(score: number): string {
  const level = getRiskLevel(score);
  const colors = {
    low: 'bg-risk-low',
    moderate: 'bg-risk-moderate',
    high: 'bg-risk-high',
    extreme: 'bg-risk-extreme',
  };
  return colors[level];
}
