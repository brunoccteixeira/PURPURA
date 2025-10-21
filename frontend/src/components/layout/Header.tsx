/**
 * Header Component
 */
import { Link } from 'react-router-dom'
import { MapPin } from 'lucide-react'

export function Header() {
  return (
    <header className="bg-white border-b border-gray-200 sticky top-0 z-50 shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link to="/" className="flex items-center gap-2 hover:opacity-80 transition-opacity">
            <div className="w-8 h-8 bg-purple-600 rounded-lg flex items-center justify-center text-white font-bold">
              🟣
            </div>
            <div>
              <div className="font-bold text-gray-900">PÚRPURA</div>
              <div className="text-xs text-gray-600">Climate OS</div>
            </div>
          </Link>

          {/* Navigation */}
          <nav className="flex items-center gap-6">
            <Link
              to="/dashboard"
              className="text-gray-700 hover:text-purple-600 font-medium transition-colors flex items-center gap-2"
            >
              <MapPin className="w-4 h-4" />
              Dashboard
            </Link>
          </nav>
        </div>
      </div>
    </header>
  )
}
