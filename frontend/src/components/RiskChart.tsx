import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { HazardIndicator, HAZARD_LABELS } from '../types';

interface RiskChartProps {
  hazards: HazardIndicator[];
}

export default function RiskChart({ hazards }: RiskChartProps) {
  // Transform data for Recharts
  const data = [
    {
      period: 'Atual',
      ...Object.fromEntries(
        hazards.map(h => [HAZARD_LABELS[h.hazard_type], h.current_risk * 100])
      )
    },
    {
      period: '2030',
      ...Object.fromEntries(
        hazards.map(h => [HAZARD_LABELS[h.hazard_type], h.projected_2030 * 100])
      )
    },
    {
      period: '2050',
      ...Object.fromEntries(
        hazards.map(h => [HAZARD_LABELS[h.hazard_type], h.projected_2050 * 100])
      )
    },
  ];

  const colors = [
    '#3b82f6', // blue
    '#f59e0b', // amber
    '#10b981', // green
    '#ef4444', // red
    '#8b5cf6', // purple
  ];

  return (
    <div className="card">
      <h3 className="text-xl font-bold mb-4 text-gray-900 dark:text-white">
        Evolução Temporal dos Riscos
      </h3>
      <ResponsiveContainer width="100%" height={400}>
        <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" className="stroke-gray-300 dark:stroke-gray-600" />
          <XAxis
            dataKey="period"
            className="text-gray-600 dark:text-gray-400"
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
            formatter={(value: number) => `${value.toFixed(1)}%`}
          />
          <Legend />
          {hazards.map((hazard, idx) => (
            <Line
              key={hazard.hazard_type}
              type="monotone"
              dataKey={HAZARD_LABELS[hazard.hazard_type]}
              stroke={colors[idx % colors.length]}
              strokeWidth={2}
              dot={{ r: 4 }}
              activeDot={{ r: 6 }}
            />
          ))}
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
