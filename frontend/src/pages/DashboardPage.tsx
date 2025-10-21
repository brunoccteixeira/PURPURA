/**
 * Dashboard Page - Main application page
 */
import { useState } from 'react'
import { MunicipalitySelector } from '../components/ui/MunicipalitySelector'
import { RiskCards } from '../components/risk/RiskCards'
import { VulnerabilityIndicators } from '../components/risk/VulnerabilityIndicators'
import { RiskTimeline } from '../components/charts/RiskTimeline'
import { ScenarioComparison } from '../components/charts/ScenarioComparison'
import { H3RiskMap } from '../components/map/H3RiskMap'
import { ChartSkeleton } from '../components/ui/LoadingSkeleton'
import { useMunicipalRisk, useH3Grid } from '../lib/api/risk'
import { AlertCircle, Info } from 'lucide-react'

export function DashboardPage() {
  const [selectedCity, setSelectedCity] = useState('3550308') // São Paulo
  const [scenario] = useState<'rcp45'>('rcp45')

  // Fetch data
  const { data: riskData, isLoading: isLoadingRisk, error: riskError } = useMunicipalRisk(
    selectedCity,
    scenario
  )

  const { data: gridData, isLoading: isLoadingGrid } = useH3Grid(
    selectedCity,
    { resolution: 7, rings: 2, format: 'heatmap', scenario }
  )

  return (
    <div className="container mx-auto px-4 py-6 space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Dashboard de Risco Climático
          </h1>
          <p className="text-gray-600 mt-1">
            Avaliação de riscos físicos para municípios brasileiros
          </p>
        </div>
        <MunicipalitySelector value={selectedCity} onChange={setSelectedCity} />
      </div>

      {/* Info Banner */}
      <div className="bg-purple-50 border border-purple-200 rounded-lg p-4 flex items-start gap-3">
        <Info className="w-5 h-5 text-purple-600 flex-shrink-0 mt-0.5" />
        <div className="text-sm">
          <p className="text-purple-900 font-medium">
            Dados em modo demonstração
          </p>
          <p className="text-purple-700 mt-1">
            Os riscos mostrados são baseados em modelos simulados.
            A integração com APIs reais (Cemaden, INPE, ANA) será implementada na próxima fase.
          </p>
        </div>
      </div>

      {/* Error State */}
      {riskError && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-red-600 flex-shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="text-red-900 font-medium">Erro ao carregar dados</p>
            <p className="text-red-700 mt-1">
              Verifique se o backend está rodando em http://localhost:8000
            </p>
          </div>
        </div>
      )}

      {/* Risk Cards */}
      <RiskCards
        overallRisk={riskData?.overall_risk_score || 0}
        hazards={riskData?.hazards || []}
        isLoading={isLoadingRisk}
      />

      {/* Timeline Chart */}
      {isLoadingRisk ? (
        <ChartSkeleton />
      ) : riskData?.hazards ? (
        <RiskTimeline hazards={riskData.hazards} />
      ) : null}

      {/* Scenario Comparison */}
      {isLoadingRisk ? (
        <ChartSkeleton />
      ) : (
        <ScenarioComparison ibgeCode={selectedCity} />
      )}

      {/* Vulnerability Indicators */}
      {isLoadingRisk ? (
        <ChartSkeleton />
      ) : riskData?.vulnerability ? (
        <VulnerabilityIndicators vulnerability={riskData.vulnerability} />
      ) : null}

      {/* Map Section */}
      <div className="card p-0 overflow-hidden">
        <div className="bg-gradient-to-r from-purple-600 to-purple-700 px-6 py-4">
          <h2 className="text-xl font-bold text-white">
            Mapa de Risco Climático - {riskData?.municipality_name || 'Carregando...'}
          </h2>
          <p className="text-purple-100 text-sm mt-1">
            Grade hexagonal H3 com visualização 3D de riscos
          </p>
        </div>

        <div className="h-[600px] relative">
          {isLoadingGrid ? (
            <div className="absolute inset-0 flex items-center justify-center bg-gray-50">
              <div className="text-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-purple-600 mx-auto" />
                <p className="mt-3 text-sm text-gray-600">Carregando grade hexagonal...</p>
              </div>
            </div>
          ) : (
            <H3RiskMap
              gridData={gridData || null}
              initialViewState={{
                latitude: riskData?.municipality_name === 'São Paulo' ? -23.5505 : -15.7801,
                longitude: riskData?.municipality_name === 'São Paulo' ? -46.6333 : -47.9292,
                zoom: 10,
                pitch: 45,
                bearing: 0,
              }}
              onHexClick={(h3Index, riskScore) => {
                console.log('Clicked hex:', h3Index, 'Risk:', riskScore)
              }}
            />
          )}
        </div>
      </div>

      {/* Recommendations */}
      {riskData?.recommendations && riskData.recommendations.length > 0 && (
        <div className="card">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">
            Recomendações
          </h3>
          <ul className="space-y-2">
            {riskData.recommendations.map((rec, index) => (
              <li key={index} className="flex items-start gap-3">
                <span className="flex-shrink-0 w-6 h-6 bg-purple-100 text-purple-600 rounded-full flex items-center justify-center text-sm font-medium">
                  {index + 1}
                </span>
                <span className="text-gray-700">{rec}</span>
              </li>
            ))}
          </ul>
        </div>
      )}

      {/* Municipality Info */}
      {riskData && (
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="card">
            <h4 className="text-sm font-medium text-gray-600 mb-1">Município</h4>
            <p className="text-lg font-semibold text-gray-900">{riskData.municipality_name}</p>
            <p className="text-xs text-gray-500 mt-1">IBGE: {riskData.ibge_code}</p>
          </div>

          <div className="card">
            <h4 className="text-sm font-medium text-gray-600 mb-1">Cenário Climático</h4>
            <p className="text-lg font-semibold text-gray-900">RCP 4.5</p>
            <p className="text-xs text-gray-500 mt-1">Emissões Moderadas</p>
          </div>

          <div className="card">
            <h4 className="text-sm font-medium text-gray-600 mb-1">População Exposta</h4>
            <p className="text-lg font-semibold text-gray-900">
              {riskData.vulnerability?.population_exposed.toLocaleString('pt-BR') || 'N/A'}
            </p>
            <p className="text-xs text-gray-500 mt-1">Estimativa</p>
          </div>
        </div>
      )}
    </div>
  )
}
