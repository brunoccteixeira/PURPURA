/**
 * Risk API endpoints
 */
import { useQuery } from '@tanstack/react-query';
import apiClient from './client';
import type { MunicipalRisk, H3GridData, LocationRisk, RiskScenario } from '../../types/risk';

/**
 * Fetch municipal risk assessment
 */
export const useMunicipalRisk = (ibgeCode: string, scenario: RiskScenario = 'rcp45') => {
  return useQuery<MunicipalRisk>({
    queryKey: ['municipal-risk', ibgeCode, scenario],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/risk/municipality/${ibgeCode}`, {
        params: { scenario },
      });
      return data;
    },
    enabled: !!ibgeCode,
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

/**
 * Fetch H3 grid for municipality
 */
export const useH3Grid = (
  ibgeCode: string,
  options: {
    resolution?: number;
    rings?: number;
    format?: 'geojson' | 'heatmap';
    scenario?: RiskScenario;
  } = {}
) => {
  const {
    resolution = 7,
    rings = 2,
    format = 'heatmap',
    scenario = 'rcp45',
  } = options;

  return useQuery<H3GridData>({
    queryKey: ['h3-grid', ibgeCode, resolution, rings, format, scenario],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/risk/h3-grid/${ibgeCode}`, {
        params: { resolution, rings, format, scenario },
      });
      return data;
    },
    enabled: !!ibgeCode,
    staleTime: 1000 * 60 * 10, // 10 minutes (grids don't change often)
  });
};

/**
 * Fetch hazard indicators
 */
export const useHazardIndicators = (ibgeCode: string, scenario: RiskScenario = 'rcp45') => {
  return useQuery({
    queryKey: ['hazards', ibgeCode, scenario],
    queryFn: async () => {
      const { data } = await apiClient.get(`/api/v1/risk/hazards/${ibgeCode}`, {
        params: { scenario },
      });
      return data;
    },
    enabled: !!ibgeCode,
    staleTime: 1000 * 60 * 5,
  });
};

/**
 * Fetch location risk for arbitrary coordinates
 */
export const useLocationRisk = (
  lat: number | null,
  lng: number | null,
  scenario: RiskScenario = 'rcp45'
) => {
  return useQuery<LocationRisk>({
    queryKey: ['location-risk', lat, lng, scenario],
    queryFn: async () => {
      const { data} = await apiClient.get(`/api/v1/risk/location`, {
        params: { lat, lng, scenario },
      });
      return data;
    },
    enabled: lat !== null && lng !== null,
    staleTime: 1000 * 60 * 5,
  });
};

/**
 * Run scenario analysis (compare multiple scenarios)
 */
export const useScenarioAnalysis = (ibgeCode: string, scenarios: RiskScenario[]) => {
  return useQuery({
    queryKey: ['scenario-analysis', ibgeCode, scenarios],
    queryFn: async () => {
      const { data } = await apiClient.post(`/api/v1/risk/scenario-analysis`, null, {
        params: { ibge_code: ibgeCode, scenarios: scenarios.join(',') },
      });
      return data;
    },
    enabled: !!ibgeCode && scenarios.length > 0,
    staleTime: 1000 * 60 * 5,
  });
};
