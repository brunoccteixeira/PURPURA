/**
 * Risk Metric Cards Component
 */
import { TrendingUp, Droplet, Thermometer, CloudRain } from 'lucide-react'
import { formatRiskScore, getRiskLevel } from '../../lib/utils/format'
import { getRiskBadgeClass } from '../../lib/utils/colors'
import type { HazardIndicator } from '../../types/risk'

interface RiskCardsProps {
  overallRisk: number
  hazards: HazardIndicator[]
  isLoading?: boolean
}

export function RiskCards({ overallRisk, hazards, isLoading }: RiskCardsProps) {
  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {[...Array(4)].map((_, i) => (
          <div key={i} className="card animate-pulse">
            <div className="h-4 bg-gray-200 rounded w-1/2 mb-4" />
            <div className="h-8 bg-gray-200 rounded w-3/4" />
          </div>
        ))}
      </div>
    )
  }

  const getHazardIcon = (type: string) => {
    switch (type) {
      case 'flood':
        return <CloudRain className="w-5 h-5" />
      case 'drought':
        return <Droplet className="w-5 h-5" />
      case 'heat_stress':
        return <Thermometer className="w-5 h-5" />
      default:
        return <TrendingUp className="w-5 h-5" />
    }
  }

  const getHazardLabel = (type: string) => {
    const labels: Record<string, string> = {
      flood: 'Inundação',
      drought: 'Seca',
      heat_stress: 'Calor Extremo',
    }
    return labels[type] || type
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {/* Overall Risk */}
      <div className="card">
        <div className="flex items-center justify-between mb-2">
          <h3 className="text-sm font-medium text-gray-600">Risco Geral</h3>
          <TrendingUp className="w-5 h-5 text-purple-600" />
        </div>
        <div className="flex items-end gap-2">
          <div className="text-3xl font-bold text-gray-900">
            {formatRiskScore(overallRisk)}
          </div>
          <span className={`risk-badge ${getRiskBadgeClass(overallRisk)} mb-1`}>
            {getRiskLevel(overallRisk)}
          </span>
        </div>
        <p className="text-xs text-gray-500 mt-2">Projeção 2050</p>
      </div>

      {/* Individual Hazards */}
      {hazards.slice(0, 3).map((hazard) => (
        <div key={hazard.hazard_type} className="card">
          <div className="flex items-center justify-between mb-2">
            <h3 className="text-sm font-medium text-gray-600">
              {getHazardLabel(hazard.hazard_type)}
            </h3>
            <div className="text-gray-400">
              {getHazardIcon(hazard.hazard_type)}
            </div>
          </div>
          <div className="flex items-end gap-2">
            <div className="text-3xl font-bold text-gray-900">
              {formatRiskScore(hazard.projected_2050)}
            </div>
            <span className={`risk-badge ${getRiskBadgeClass(hazard.projected_2050)} mb-1`}>
              {getRiskLevel(hazard.projected_2050)}
            </span>
          </div>
          <div className="mt-3 flex items-center gap-2 text-xs">
            <span className="text-gray-500">Atual:</span>
            <span className="font-medium text-gray-700">
              {formatRiskScore(hazard.current_risk)}
            </span>
            <span className="text-gray-400">→</span>
            <span className="font-medium text-gray-900">
              {formatRiskScore(hazard.projected_2050)}
            </span>
          </div>
        </div>
      ))}
    </div>
  )
}
