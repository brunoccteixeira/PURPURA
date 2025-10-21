import { useState } from 'react';
import type { RiskScenario } from '../../types/risk';
import { useMunicipalRisk } from '../../lib/api/risk';
import { formatRiskScore, getRiskLevel } from '../../lib/utils/format';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface ScenarioComparisonProps {
  ibgeCode: string;
}

export function ScenarioComparison({ ibgeCode }: ScenarioComparisonProps) {
  const [selectedYear, setSelectedYear] = useState<'2030' | '2050'>('2050');

  // Fetch data for all three scenarios
  const { data: rcp26 } = useMunicipalRisk(ibgeCode, 'rcp26');
  const { data: rcp45 } = useMunicipalRisk(ibgeCode, 'rcp45');
  const { data: rcp85 } = useMunicipalRisk(ibgeCode, 'rcp85');

  // Transform data for chart
  const getComparisonData = () => {
    const scenarios = [
      { name: 'RCP 2.6\n(Otimista)', data: rcp26, color: '#10b981' },
      { name: 'RCP 4.5\n(Moderado)', data: rcp45, color: '#f59e0b' },
      { name: 'RCP 8.5\n(Pessimista)', data: rcp85, color: '#ef4444' },
    ];

    const hazardTypes = ['flood', 'drought', 'heat_stress'];
    const hazardLabels: Record<string, string> = {
      flood: 'Inundações',
      drought: 'Secas',
      heat_stress: 'Estresse Térmico',
    };

    return hazardTypes.map((hazardType) => {
      const dataPoint: any = {
        name: hazardLabels[hazardType],
        hazard: hazardType,
      };

      scenarios.forEach((scenario) => {
        const hazard = scenario.data?.hazards.find((h) => h.hazard_type === hazardType);
        const value = selectedYear === '2050' ? hazard?.projected_2050 : hazard?.projected_2030;
        dataPoint[scenario.name] = value || 0;
      });

      return dataPoint;
    });
  };

  const comparisonData = getComparisonData();

  const scenarioDescriptions: Record<RiskScenario, string> = {
    rcp26: 'Baixas emissões - Ação climática agressiva',
    rcp45: 'Emissões moderadas - Cenário intermediário',
    rcp85: 'Altas emissões - Business as usual',
  };

  return (
    <div className="card">
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h2 className="text-xl font-bold text-gray-900">Comparação de Cenários Climáticos</h2>
            <p className="text-sm text-gray-600 mt-1">
              Análise de diferentes trajetórias de emissões (RCP)
            </p>
          </div>

          <div className="flex gap-2">
            <button
              onClick={() => setSelectedYear('2030')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedYear === '2030'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              2030
            </button>
            <button
              onClick={() => setSelectedYear('2050')}
              className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
                selectedYear === '2050'
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              2050
            </button>
          </div>
        </div>

        {/* Scenario descriptions */}
        <div className="grid grid-cols-3 gap-3 mb-6">
          <div className="bg-green-50 border border-green-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 bg-green-500 rounded-full"></div>
              <span className="font-semibold text-sm text-green-900">RCP 2.6</span>
            </div>
            <p className="text-xs text-green-700">{scenarioDescriptions.rcp26}</p>
          </div>

          <div className="bg-amber-50 border border-amber-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 bg-amber-500 rounded-full"></div>
              <span className="font-semibold text-sm text-amber-900">RCP 4.5</span>
            </div>
            <p className="text-xs text-amber-700">{scenarioDescriptions.rcp45}</p>
          </div>

          <div className="bg-red-50 border border-red-200 rounded-lg p-3">
            <div className="flex items-center gap-2 mb-1">
              <div className="w-3 h-3 bg-red-500 rounded-full"></div>
              <span className="font-semibold text-sm text-red-900">RCP 8.5</span>
            </div>
            <p className="text-xs text-red-700">{scenarioDescriptions.rcp85}</p>
          </div>
        </div>
      </div>

      <ResponsiveContainer width="100%" height={350}>
        <BarChart data={comparisonData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="name"
            stroke="#6b7280"
            style={{ fontSize: '0.875rem' }}
          />
          <YAxis
            stroke="#6b7280"
            style={{ fontSize: '0.875rem' }}
            domain={[0, 1]}
            tickFormatter={(value) => `${(value * 100).toFixed(0)}%`}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: '#ffffff',
              border: '1px solid #e5e7eb',
              borderRadius: '0.5rem',
              boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)',
            }}
            labelStyle={{ color: '#111827', fontWeight: 600 }}
            formatter={(value: number) => `${(value * 100).toFixed(1)}%`}
          />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value: string) => value.replace('\n', ' ')}
          />
          <Bar dataKey="RCP 2.6\n(Otimista)" fill="#10b981" radius={[4, 4, 0, 0]} />
          <Bar dataKey="RCP 4.5\n(Moderado)" fill="#f59e0b" radius={[4, 4, 0, 0]} />
          <Bar dataKey="RCP 8.5\n(Pessimista)" fill="#ef4444" radius={[4, 4, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>

      {/* Overall risk comparison cards */}
      <div className="grid grid-cols-3 gap-4 mt-6 pt-6 border-t border-gray-200">
        {[
          { scenario: 'rcp26' as RiskScenario, data: rcp26, color: 'green' },
          { scenario: 'rcp45' as RiskScenario, data: rcp45, color: 'amber' },
          { scenario: 'rcp85' as RiskScenario, data: rcp85, color: 'red' },
        ].map(({ scenario, data, color }) => (
          <div key={scenario} className="text-center">
            <div className="text-2xl font-bold text-gray-900">
              {data ? formatRiskScore(data.overall_risk_score) : '—'}
            </div>
            <div className={`text-xs font-medium text-${color}-700 mt-1`}>
              Risco Geral {selectedYear}
            </div>
            <div className={`text-xs text-${color}-600 mt-0.5`}>
              {data ? getRiskLevel(data.overall_risk_score) : '—'}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
