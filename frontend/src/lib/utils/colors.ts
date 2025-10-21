/**
 * Color utilities for risk visualization
 */

/**
 * Get risk level color based on score (0-1)
 */
export const getRiskColor = (score: number): string => {
  if (score < 0.3) return '#10b981'; // green-500
  if (score < 0.5) return '#f59e0b'; // yellow-500
  if (score < 0.7) return '#f97316'; // orange-500
  return '#ef4444'; // red-500
};

/**
 * Get risk level label
 */
export const getRiskLevel = (score: number): string => {
  if (score < 0.3) return 'Baixo';
  if (score < 0.5) return 'Moderado';
  if (score < 0.7) return 'Alto';
  return 'Crítico';
};

/**
 * Get Tailwind CSS class for risk badge
 */
export const getRiskBadgeClass = (score: number): string => {
  if (score < 0.3) return 'risk-low';
  if (score < 0.5) return 'risk-moderate';
  if (score < 0.7) return 'risk-high';
  return 'risk-critical';
};

/**
 * Convert risk score to RGB array for deck.gl
 */
export const getRiskColorRGB = (score: number): [number, number, number] => {
  if (score < 0.3) return [16, 185, 129];  // green
  if (score < 0.5) return [245, 158, 11];  // yellow
  if (score < 0.7) return [249, 115, 22];  // orange
  return [239, 68, 68];                     // red
};

/**
 * Get color with opacity for deck.gl
 */
export const getRiskColorRGBA = (
  score: number,
  alpha: number = 200
): [number, number, number, number] => {
  return [...getRiskColorRGB(score), alpha];
};

/**
 * Interpolate between two colors
 */
export const interpolateColor = (
  color1: [number, number, number],
  color2: [number, number, number],
  factor: number
): [number, number, number] => {
  return [
    Math.round(color1[0] + (color2[0] - color1[0]) * factor),
    Math.round(color1[1] + (color2[1] - color1[1]) * factor),
    Math.round(color1[2] + (color2[2] - color1[2]) * factor),
  ];
};

/**
 * Get color gradient for continuous scale
 */
export const getGradientColor = (value: number, min: number, max: number): string => {
  const normalized = (value - min) / (max - min);
  const score = Math.max(0, Math.min(1, normalized));
  return getRiskColor(score);
};
