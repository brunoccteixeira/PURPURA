/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        // PÚRPURA brand colors
        primary: {
          50: '#faf5ff',
          100: '#f3e8ff',
          200: '#e9d5ff',
          300: '#d8b4fe',
          400: '#c084fc',
          500: '#a855f7',  // Main purple
          600: '#9333ea',
          700: '#7e22ce',
          800: '#6b21a8',
          900: '#581c87',
        },
        risk: {
          low: '#10b981',      // Green
          moderate: '#f59e0b', // Amber
          high: '#ef4444',     // Red
          extreme: '#7f1d1d',  // Dark red
        }
      },
    },
  },
  plugins: [],
}
