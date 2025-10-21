/**
 * Municipality Selector Component
 */
import { MUNICIPALITIES } from '../../config/constants'

interface MunicipalitySelectorProps {
  value: string
  onChange: (ibgeCode: string) => void
}

export function MunicipalitySelector({ value, onChange }: MunicipalitySelectorProps) {
  return (
    <div className="w-full max-w-xs">
      <label htmlFor="municipality" className="block text-sm font-medium text-gray-700 mb-2">
        Selecione o Município
      </label>
      <select
        id="municipality"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-purple-500 focus:border-purple-500 bg-white"
      >
        {MUNICIPALITIES.map((city) => (
          <option key={city.ibge} value={city.ibge}>
            {city.name} - {city.state}
          </option>
        ))}
      </select>
    </div>
  )
}
