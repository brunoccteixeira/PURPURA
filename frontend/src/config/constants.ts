/**
 * Application constants
 */

export const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const DEFAULT_SCENARIO: import('../types/risk').RiskScenario = 'rcp45';

export const SCENARIOS = [
  { value: 'rcp26', label: 'RCP 2.6 - Baixas Emissões', description: 'Cenário otimista' },
  { value: 'rcp45', label: 'RCP 4.5 - Emissões Moderadas', description: 'Cenário moderado' },
  { value: 'rcp85', label: 'RCP 8.5 - Altas Emissões', description: 'Cenário pessimista' },
] as const;

export const HAZARD_LABELS: Record<string, string> = {
  flood: 'Inundação',
  drought: 'Seca',
  heat_stress: 'Estresse Térmico',
  landslide: 'Deslizamento',
  coastal_inundation: 'Inundação Costeira',
};

export const RISK_LEVELS = [
  { min: 0, max: 0.3, label: 'Baixo', color: '#10b981' },
  { min: 0.3, max: 0.5, label: 'Moderado', color: '#f59e0b' },
  { min: 0.5, max: 0.7, label: 'Alto', color: '#f97316' },
  { min: 0.7, max: 1.0, label: 'Crítico', color: '#ef4444' },
] as const;

export const MUNICIPALITIES = [
  { ibge: '3550308', name: 'São Paulo', state: 'SP' },
  { ibge: '3304557', name: 'Rio de Janeiro', state: 'RJ' },
  { ibge: '2927408', name: 'Salvador', state: 'BA' },
  { ibge: '5300108', name: 'Brasília', state: 'DF' },
  { ibge: '4106902', name: 'Curitiba', state: 'PR' },
] as const;

export const MAP_CONFIG = {
  initialViewState: {
    latitude: -15.7801,
    longitude: -47.9292,
    zoom: 4,
    pitch: 45,
    bearing: 0,
  },
  h3Resolution: 7,
} as const;
