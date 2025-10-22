import { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { runScenarioAnalysis } from '../api';
import { SCENARIO_LABELS, HAZARD_LABELS } from '../types';
import type { RiskScenario } from '../types';

interface ScenarioComparisonProps {
  ibgeCode: string;
}

export default function ScenarioComparison({ ibgeCode }: ScenarioComparisonProps) {
  const [loading, setLoading] = useState(false);
  const [comparisonData, setComparisonData] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  const loadComparison = async () => {
    try {
      setLoading(true);
      setError(null);
      const scenarios: RiskScenario[] = ['rcp26', 'rcp45', 'rcp85'];
      const data = await runScenarioAnalysis(ibgeCode, scenarios);
      setComparisonData(data);
    } catch (err) {
      setError('Erro ao carregar comparação de cenários');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (ibgeCode) {
      loadComparison();
    }
  }, [ibgeCode]);

  if (loading) {
    return (
      <div className="card">
        <div className="flex items-center justify-center py-12">
          <div className="text-gray-500">Carregando comparação...</div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card">
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg">
          {error}
        </div>
      </div>
    );
  }

  if (!comparisonData) {
    return null;
  }

  // Transform data for chart
  const chartData = comparisonData.results.map((result: any) => ({
    scenario: SCENARIO_LABELS[result.scenario as RiskScenario],
    'Risco Geral': (result.overall_risk_score * 100).toFixed(1),
    ...Object.fromEntries(
      result.hazards.slice(0, 3).map((h: any) => [
        HAZARD_LABELS[h.hazard_type as keyof typeof HAZARD_LABELS],
        (h.current_risk * 100).toFixed(1)
      ])
    )
  }));

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
        Comparação de Cenários Climáticos
      </h3>

      <p className="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Município: {comparisonData.municipality_name}
      </p>

      <ResponsiveContainer width="100%" height={400}>
        <BarChart data={chartData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-600" />
          <XAxis
            dataKey="scenario"
            className="text-gray-600 dark:text-gray-400"
            angle={-15}
            textAnchor="end"
            height={80}
          />
          <YAxis
            label={{ value: 'Risco (%)', angle: -90, position: 'insideLeft' }}
            className="text-gray-600 dark:text-gray-400"
            domain={[0, 100]}
          />
          <Tooltip
            contentStyle={{
              backgroundColor: 'rgba(255, 255, 255, 0.95)',
              border: '1px solid #ccc',
              borderRadius: '8px'
            }}
            formatter={(value: string) => `${value}%`}
          />
          <Legend />
          <Bar dataKey="Risco Geral" fill="#a855f7" />
          <Bar dataKey="Inundação" fill="#3b82f6" />
          <Bar dataKey="Seca" fill="#f59e0b" />
          <Bar dataKey="Estresse Térmico" fill="#ef4444" />
        </BarChart>
      </ResponsiveContainer>

      <div className="mt-6 grid grid-cols-1 md:grid-cols-3 gap-4">
        {comparisonData.results.map((result: any) => (
          <div key={result.scenario} className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg">
            <h4 className="font-semibold text-gray-900 dark:text-white mb-2">
              {SCENARIO_LABELS[result.scenario as RiskScenario]}
            </h4>
            <p className="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {(result.overall_risk_score * 100).toFixed(0)}%
            </p>
            <p className="text-sm text-gray-600 dark:text-gray-400">Risco Geral</p>
          </div>
        ))}
      </div>
    </div>
  );
}
