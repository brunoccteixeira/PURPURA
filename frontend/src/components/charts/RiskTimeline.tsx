import type { HazardIndicator } from '../../types/risk';
import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
  ResponsiveContainer,
} from 'recharts';

interface RiskTimelineProps {
  hazards: HazardIndicator[];
}

export function RiskTimeline({ hazards }: RiskTimelineProps) {
  // Transform hazard data into timeline format
  const timelineData = [
    {
      year: 'Atual',
      flood: hazards.find((h) => h.hazard_type === 'flood')?.current_risk || 0,
      drought: hazards.find((h) => h.hazard_type === 'drought')?.current_risk || 0,
      heat_stress: hazards.find((h) => h.hazard_type === 'heat_stress')?.current_risk || 0,
    },
    {
      year: '2030',
      flood: hazards.find((h) => h.hazard_type === 'flood')?.projected_2030 || 0,
      drought: hazards.find((h) => h.hazard_type === 'drought')?.projected_2030 || 0,
      heat_stress: hazards.find((h) => h.hazard_type === 'heat_stress')?.projected_2030 || 0,
    },
    {
      year: '2050',
      flood: hazards.find((h) => h.hazard_type === 'flood')?.projected_2050 || 0,
      drought: hazards.find((h) => h.hazard_type === 'drought')?.projected_2050 || 0,
      heat_stress: hazards.find((h) => h.hazard_type === 'heat_stress')?.projected_2050 || 0,
    },
  ];

  const hazardLabels: Record<string, string> = {
    flood: 'Inundações',
    drought: 'Secas',
    heat_stress: 'Estresse Térmico',
  };

  const hazardColors: Record<string, string> = {
    flood: '#3b82f6', // blue
    drought: '#f59e0b', // amber
    heat_stress: '#ef4444', // red
  };

  return (
    <div className="card">
      <div className="mb-6">
        <h2 className="text-xl font-bold text-gray-900">Projeções de Risco ao Longo do Tempo</h2>
        <p className="text-sm text-gray-600 mt-1">
          Evolução dos principais riscos climáticos até 2050
        </p>
      </div>

      <ResponsiveContainer width="100%" height={350}>
        <LineChart data={timelineData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis
            dataKey="year"
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
            formatter={(value: number) => [`${(value * 100).toFixed(1)}%`, '']}
          />
          <Legend
            wrapperStyle={{ paddingTop: '20px' }}
            formatter={(value: string) => hazardLabels[value] || value}
          />
          <Line
            type="monotone"
            dataKey="flood"
            stroke={hazardColors.flood}
            strokeWidth={2}
            dot={{ fill: hazardColors.flood, r: 4 }}
            activeDot={{ r: 6 }}
            name="flood"
          />
          <Line
            type="monotone"
            dataKey="drought"
            stroke={hazardColors.drought}
            strokeWidth={2}
            dot={{ fill: hazardColors.drought, r: 4 }}
            activeDot={{ r: 6 }}
            name="drought"
          />
          <Line
            type="monotone"
            dataKey="heat_stress"
            stroke={hazardColors.heat_stress}
            strokeWidth={2}
            dot={{ fill: hazardColors.heat_stress, r: 4 }}
            activeDot={{ r: 6 }}
            name="heat_stress"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
