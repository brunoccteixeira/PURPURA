/**
 * API Client for PÚRPURA Backend
 */
import axios from 'axios';
import type { MunicipalRisk, RiskScenario } from './types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api/v1';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

/**
 * Get climate risk assessment for a municipality
 */
export async function getMunicipalRisk(
  ibgeCode: string,
  scenario: RiskScenario = 'rcp45'
): Promise<MunicipalRisk> {
  const response = await api.get<MunicipalRisk>(
    `/risk/municipality/${ibgeCode}`,
    { params: { scenario } }
  );
  return response.data;
}

/**
 * Get hazard indicators only (lightweight)
 */
export async function getHazardIndicators(
  ibgeCode: string,
  scenario: RiskScenario = 'rcp45'
) {
  const response = await api.get(`/risk/hazards/${ibgeCode}`, {
    params: { scenario },
  });
  return response.data;
}

/**
 * Run multi-scenario comparison
 */
export async function runScenarioAnalysis(
  ibgeCode: string,
  scenarios: RiskScenario[]
) {
  const response = await api.post('/risk/scenario-analysis', scenarios, {
    params: { ibge_code: ibgeCode },
  });
  return response.data;
}

/**
 * Health check
 */
export async function checkHealth() {
  const response = await api.get('/health', {
    baseURL: 'http://localhost:8000',
  });
  return response.data;
}

export default api;
