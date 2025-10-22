import { MunicipalRisk, getRiskLevel } from '../types';

interface StatsOverviewProps {
  riskData: MunicipalRisk;
}

export default function StatsOverview({ riskData }: StatsOverviewProps) {
  const riskLevel = getRiskLevel(riskData.overall_risk_score);
  const riskLevelLabels = {
    low: 'Baixo',
    moderate: 'Moderado',
    high: 'Alto',
    extreme: 'Extremo',
  };

  // Calculate change from current to 2050
  const avgCurrentRisk = riskData.hazards.reduce((sum, h) => sum + h.current_risk, 0) / riskData.hazards.length;
  const avg2050Risk = riskData.hazards.reduce((sum, h) => sum + h.projected_2050, 0) / riskData.hazards.length;
  const riskIncrease = ((avg2050Risk - avgCurrentRisk) / avgCurrentRisk * 100);

  // Find highest risk hazard
  const highestRiskHazard = riskData.hazards.reduce((max, h) =>
    h.current_risk > max.current_risk ? h : max
  );

  const stats = [
    {
      label: 'Nível de Risco',
      value: riskLevelLabels[riskLevel],
      subtext: `${Math.round(riskData.overall_risk_score * 100)}% de score geral`,
      icon: '⚠️',
      color: riskLevel === 'high' || riskLevel === 'extreme' ? 'text-red-600' :
             riskLevel === 'moderate' ? 'text-amber-600' : 'text-green-600',
    },
    {
      label: 'Projeção 2050',
      value: riskIncrease > 0 ? `+${riskIncrease.toFixed(0)}%` : `${riskIncrease.toFixed(0)}%`,
      subtext: 'Aumento médio até 2050',
      icon: '📈',
      color: riskIncrease > 30 ? 'text-red-600' : 'text-amber-600',
    },
    {
      label: 'Maior Risco',
      value: highestRiskHazard.hazard_type === 'flood' ? 'Inundação' :
             highestRiskHazard.hazard_type === 'drought' ? 'Seca' :
             highestRiskHazard.hazard_type === 'heat_stress' ? 'Calor' :
             highestRiskHazard.hazard_type === 'landslide' ? 'Deslizamento' : 'Costeira',
      subtext: `${Math.round(highestRiskHazard.current_risk * 100)}% de risco atual`,
      icon: '🎯',
      color: 'text-primary-600',
    },
    {
      label: 'População em Risco',
      value: (riskData.vulnerability.population_exposed / 1000).toFixed(0) + 'k',
      subtext: `${Math.round(riskData.vulnerability.vulnerable_population_pct * 100)}% vulnerável`,
      icon: '👥',
      color: 'text-blue-600',
    },
    {
      label: 'Infraestrutura Crítica',
      value: riskData.vulnerability.critical_infrastructure_count.toString(),
      subtext: 'Estruturas expostas',
      icon: '🏢',
      color: 'text-purple-600',
    },
    {
      label: 'Capacidade Adaptativa',
      value: Math.round(riskData.vulnerability.adaptive_capacity_score * 100) + '%',
      subtext: 'Resiliência municipal',
      icon: '💪',
      color: riskData.vulnerability.adaptive_capacity_score > 0.6 ? 'text-green-600' : 'text-amber-600',
    },
  ];

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-6 text-gray-900 dark:text-white">
        Visão Geral - {riskData.municipality_name}
      </h3>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {stats.map((stat, idx) => (
          <div key={idx} className="relative">
            <div className="flex items-start space-x-3">
              <div className="text-3xl">{stat.icon}</div>
              <div className="flex-1">
                <p className="text-sm text-gray-600 dark:text-gray-400 mb-1">
                  {stat.label}
                </p>
                <p className={`text-2xl font-bold ${stat.color}`}>
                  {stat.value}
                </p>
                <p className="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  {stat.subtext}
                </p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-6 pt-6 border-t border-gray-200 dark:border-gray-700">
        <p className="text-sm text-gray-600 dark:text-gray-400">
          <span className="font-semibold">Fonte de Dados:</span> INPE + Cemaden + INMET + Heurísticas Geográficas
        </p>
      </div>
    </div>
  );
}
