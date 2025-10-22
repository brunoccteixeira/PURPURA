import { useState } from 'react';
import { getMunicipalRisk } from './api';
import type { MunicipalRisk, RiskScenario } from './types';
import RiskCard from './components/RiskCard';
import { SCENARIO_LABELS, getRiskColor } from './types';

// Available municipalities
const MUNICIPALITIES = [
  { ibge_code: '3550308', name: 'São Paulo', state: 'SP' },
  { ibge_code: '3304557', name: 'Rio de Janeiro', state: 'RJ' },
  { ibge_code: '3106200', name: 'Belo Horizonte', state: 'MG' },
  { ibge_code: '2927408', name: 'Salvador', state: 'BA' },
  { ibge_code: '5300108', name: 'Brasília', state: 'DF' },
  { ibge_code: '2304400', name: 'Fortaleza', state: 'CE' },
  { ibge_code: '1302603', name: 'Manaus', state: 'AM' },
  { ibge_code: '4106902', name: 'Curitiba', state: 'PR' },
  { ibge_code: '2611606', name: 'Recife', state: 'PE' },
  { ibge_code: '4314902', name: 'Porto Alegre', state: 'RS' },
];

function App() {
  const [selectedMunicipality, setSelectedMunicipality] = useState('3550308');
  const [scenario, setScenario] = useState<RiskScenario>('rcp45');
  const [riskData, setRiskData] = useState<MunicipalRisk | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadRiskData = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await getMunicipalRisk(selectedMunicipality, scenario);
      setRiskData(data);
    } catch (err) {
      setError('Erro ao carregar dados. Verifique se o backend está rodando.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const currentMuni = MUNICIPALITIES.find(m => m.ibge_code === selectedMunicipality);

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-primary-600 text-white py-6 shadow-lg">
        <div className="container mx-auto px-4">
          <h1 className="text-3xl font-bold">🟣 PÚRPURA Climate OS</h1>
          <p className="text-primary-100 mt-1">
            Avaliação de Riscos Climáticos Físicos - Brasil
          </p>
        </div>
      </header>

      {/* Main Content */}
      <main className="container mx-auto px-4 py-8">
        {/* Controls */}
        <div className="card mb-8">
          <h2 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
            Selecione o Município e Cenário
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            {/* Municipality Select */}
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                Município
              </label>
              <select
                value={selectedMunicipality}
                onChange={(e) => setSelectedMunicipality(e.target.value)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {MUNICIPALITIES.map((muni) => (
                  <option key={muni.ibge_code} value={muni.ibge_code}>
                    {muni.name} - {muni.state}
                  </option>
                ))}
              </select>
            </div>

            {/* Scenario Select */}
            <div>
              <label className="block text-sm font-medium mb-2 text-gray-700 dark:text-gray-300">
                Cenário Climático
              </label>
              <select
                value={scenario}
                onChange={(e) => setScenario(e.target.value as RiskScenario)}
                className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
              >
                {Object.entries(SCENARIO_LABELS).map(([key, label]) => (
                  <option key={key} value={key}>
                    {label}
                  </option>
                ))}
              </select>
            </div>

            {/* Load Button */}
            <div className="flex items-end">
              <button
                onClick={loadRiskData}
                disabled={loading}
                className="btn-primary w-full disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {loading ? 'Carregando...' : 'Carregar Dados'}
              </button>
            </div>
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 text-red-800 dark:text-red-200 px-4 py-3 rounded-lg mb-6">
            {error}
          </div>
        )}

        {/* Risk Dashboard */}
        {riskData && (
          <div className="space-y-6">
            {/* Overview */}
            <div className="card">
              <h2 className="text-2xl font-bold mb-2 text-gray-900 dark:text-white">
                {riskData.municipality_name}
              </h2>
              <p className="text-gray-600 dark:text-gray-400 mb-4">
                Código IBGE: {riskData.ibge_code} | Cenário: {SCENARIO_LABELS[riskData.scenario]}
              </p>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Risco Geral</p>
                  <p className={`text-3xl font-bold ${getRiskColor(riskData.overall_risk_score)}`}>
                    {Math.round(riskData.overall_risk_score * 100)}%
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">População Exposta</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {riskData.vulnerability.population_exposed.toLocaleString('pt-BR')}
                  </p>
                </div>
                <div>
                  <p className="text-sm text-gray-600 dark:text-gray-400">Capacidade Adaptativa</p>
                  <p className="text-3xl font-bold text-gray-900 dark:text-white">
                    {Math.round(riskData.vulnerability.adaptive_capacity_score * 100)}%
                  </p>
                </div>
              </div>
            </div>

            {/* Hazard Cards */}
            <div>
              <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
                Riscos por Tipo de Ameaça Climática
              </h3>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {riskData.hazards.map((hazard) => (
                  <RiskCard key={hazard.hazard_type} hazard={hazard} />
                ))}
              </div>
            </div>

            {/* Recommendations */}
            {riskData.recommendations.length > 0 && (
              <div className="card">
                <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
                  Recomendações
                </h3>
                <ul className="space-y-2">
                  {riskData.recommendations.map((rec, idx) => (
                    <li key={idx} className="flex items-start">
                      <span className="text-primary-500 mr-2">•</span>
                      <span className="text-gray-700 dark:text-gray-300">{rec}</span>
                    </li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}

        {/* Initial State */}
        {!riskData && !loading && !error && (
          <div className="card text-center py-12">
            <p className="text-gray-500 dark:text-gray-400 text-lg">
              Selecione um município e cenário climático para visualizar os riscos.
            </p>
          </div>
        )}
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 text-gray-300 py-6 mt-12">
        <div className="container mx-auto px-4 text-center">
          <p>🟣 PÚRPURA Climate OS - MVP</p>
          <p className="text-sm text-gray-500 mt-1">
            Dados: INPE + Cemaden + INMET + Heurísticas
          </p>
        </div>
      </footer>
    </div>
  );
}

export default App;
