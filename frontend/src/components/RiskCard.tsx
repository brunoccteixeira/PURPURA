import { HazardIndicator, HAZARD_LABELS, getRiskColor, getRiskBgColor } from '../types';

interface RiskCardProps {
  hazard: HazardIndicator;
}

export default function RiskCard({ hazard }: RiskCardProps) {
  const label = HAZARD_LABELS[hazard.hazard_type];
  const currentRiskPct = Math.round(hazard.current_risk * 100);
  const projected2050Pct = Math.round(hazard.projected_2050 * 100);

  return (
    <div className="card">
      <div className="flex justify-between items-start mb-4">
        <h3 className="text-lg font-semibold text-gray-900 dark:text-white">
          {label}
        </h3>
        <span className="text-sm text-gray-500">
          Confiança: {Math.round(hazard.confidence * 100)}%
        </span>
      </div>

      <div className="space-y-3">
        {/* Current Risk */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">Risco Atual</span>
            <span className={`font-bold ${getRiskColor(hazard.current_risk)}`}>
              {currentRiskPct}%
            </span>
          </div>
          <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-2">
            <div
              className={`${getRiskBgColor(hazard.current_risk)} h-2 rounded-full transition-all`}
              style={{ width: `${currentRiskPct}%` }}
            />
          </div>
        </div>

        {/* 2030 Projection */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">Projeção 2030</span>
            <span className={`font-bold ${getRiskColor(hazard.projected_2030)}`}>
              {Math.round(hazard.projected_2030 * 100)}%
            </span>
          </div>
        </div>

        {/* 2050 Projection */}
        <div>
          <div className="flex justify-between text-sm mb-1">
            <span className="text-gray-600 dark:text-gray-400">Projeção 2050</span>
            <span className={`font-bold ${getRiskColor(hazard.projected_2050)}`}>
              {projected2050Pct}%
            </span>
          </div>
        </div>
      </div>

      <div className="mt-4 pt-4 border-t border-gray-200 dark:border-gray-700">
        <p className="text-xs text-gray-500">
          {hazard.data_source}
        </p>
      </div>
    </div>
  );
}
