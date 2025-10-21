/**
 * Formatting utilities
 */

/**
 * Format risk score as percentage
 */
export const formatRiskScore = (score: number): string => {
  return `${(score * 100).toFixed(0)}%`;
};

/**
 * Format number with thousands separator (Brazilian format)
 */
export const formatNumber = (num: number): string => {
  return new Intl.NumberFormat('pt-BR').format(num);
};

/**
 * Format percentage
 */
export const formatPercentage = (value: number): string => {
  return `${(value * 100).toFixed(1)}%`;
};

/**
 * Format confidence score
 */
export const formatConfidence = (confidence: number): string => {
  if (confidence >= 0.8) return 'Alta';
  if (confidence >= 0.6) return 'Média';
  return 'Baixa';
};

/**
 * Get hazard label in Portuguese
 */
export const getHazardLabel = (hazardType: string): string => {
  const labels: Record<string, string> = {
    flood: 'Inundação',
    drought: 'Seca',
    heat_stress: 'Estresse Térmico',
    landslide: 'Deslizamento',
    coastal_inundation: 'Inundação Costeira',
  };
  return labels[hazardType] || hazardType;
};

/**
 * Get scenario label in Portuguese
 */
export const getScenarioLabel = (scenario: string): string => {
  const labels: Record<string, string> = {
    rcp26: 'RCP 2.6 - Baixas Emissões',
    rcp45: 'RCP 4.5 - Emissões Moderadas',
    rcp85: 'RCP 8.5 - Altas Emissões',
    ssp126: 'SSP1-2.6 - Sustentabilidade',
    ssp245: 'SSP2-4.5 - Meio do Caminho',
    ssp585: 'SSP5-8.5 - Combustíveis Fósseis',
  };
  return labels[scenario] || scenario.toUpperCase();
};

/**
 * Truncate text with ellipsis
 */
export const truncate = (text: string, maxLength: number): string => {
  if (text.length <= maxLength) return text;
  return text.slice(0, maxLength - 3) + '...';
};

/**
 * Format area in square kilometers
 */
export const formatArea = (areaKm2: number): string => {
  if (areaKm2 < 1) {
    return `${(areaKm2 * 1000000).toFixed(0)} m²`;
  }
  return `${areaKm2.toFixed(2)} km²`;
};
