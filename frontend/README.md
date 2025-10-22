# PÚRPURA Frontend

**React + TypeScript dashboard for municipal climate risk assessment**

## ✅ Status: MVP Completed (Week 5-6)

Interactive dashboard for visualizing physical climate risks across Brazilian municipalities.

## 🚀 Quick Start

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

The dashboard will be available at **http://localhost:3000**

## 🎯 Features

### Core Functionality
- **10 Brazilian Municipalities**: São Paulo, Rio de Janeiro, Belo Horizonte, Salvador, Brasília, Fortaleza, Manaus, Curitiba, Recife, Porto Alegre
- **5 Hazard Types**:
  - Inundação (Flood)
  - Seca (Drought)
  - Estresse Térmico (Heat Stress)
  - Deslizamento (Landslide)
  - Inundação Costeira (Coastal Inundation)
- **3 RCP Scenarios**: 2.6 (optimistic), 4.5 (moderate), 8.5 (pessimistic)
- **Temporal Projections**: Current → 2030 → 2050

### Visualizations

1. **StatsOverview** - 6 key metrics dashboard
   - Risk level assessment
   - 2050 projection increase percentage
   - Highest risk identification
   - Population exposure (vulnerable %)
   - Critical infrastructure count
   - Adaptive capacity score

2. **RiskChart** - Temporal evolution line chart
   - All 5 hazards on single interactive chart
   - Shows progression: Current → 2030 → 2050
   - Color-coded by hazard type
   - Interactive tooltips

3. **ScenarioComparison** - Climate scenario bar chart
   - Compares RCP 2.6, 4.5, and 8.5 side-by-side
   - Auto-loads on municipality selection
   - Shows overall risk + top hazards

4. **RiskCard** - Individual hazard visualization
   - Progress bars with color-coded severity
   - Green (low) → Amber (moderate) → Red (high) → Dark Red (extreme)
   - Data source attribution
   - Confidence scores

## 🏗️ Project Structure

```
frontend/
├── src/
│   ├── components/          # React components
│   │   ├── RiskCard.tsx    # Individual hazard visualization
│   │   ├── RiskChart.tsx   # Temporal evolution chart
│   │   ├── ScenarioComparison.tsx  # RCP scenario comparison
│   │   └── StatsOverview.tsx       # Key metrics dashboard
│   ├── api.ts              # API client (Axios)
│   ├── types.ts            # TypeScript interfaces
│   ├── App.tsx             # Main dashboard component
│   ├── index.css           # Tailwind CSS base
│   └── main.tsx            # React entry point
├── public/                 # Static assets
├── index.html              # HTML template
├── package.json            # Dependencies
├── tailwind.config.js      # Tailwind configuration
├── tsconfig.json           # TypeScript configuration
└── vite.config.ts          # Vite build configuration
```

## 🎨 Tech Stack

| Technology | Purpose | Version |
|------------|---------|---------|
| **React** | UI framework | 18.3.1 |
| **TypeScript** | Type safety | 5.6.2 |
| **Vite** | Build tool | 6.4.1 |
| **Tailwind CSS** | Styling | 3.4.17 |
| **Recharts** | Data visualization | 2.15.0 |
| **Axios** | HTTP client | 1.7.9 |
| **Lucide React** | Icon library | 0.468.0 |

## 🎨 Design System

### Colors (PÚRPURA Brand)

```javascript
{
  primary: {
    500: '#a855f7',  // Main purple
    600: '#9333ea',  // Darker purple
  },
  risk: {
    low: '#10b981',      // Green
    moderate: '#f59e0b', // Amber
    high: '#ef4444',     // Red
    extreme: '#7f1d1d',  // Dark red
  }
}
```

### Typography
- Font: System font stack (sans-serif)
- Language: 100% Portuguese (pt-BR)

## 🔌 API Integration

The frontend connects to the PÚRPURA backend API at `http://localhost:8000/api/v1`

**Endpoints used:**
- `GET /risk/municipality/{ibge_code}?scenario={rcp}` - Get municipal risk assessment
- `POST /risk/scenario-analysis?ibge_code={code}` - Compare multiple scenarios

**Proxy configuration** (vite.config.ts):
```typescript
server: {
  proxy: {
    '/api': 'http://localhost:8000'
  }
}
```

## 📊 Data Flow

1. User selects municipality + scenario
2. Frontend calls `/risk/municipality/{ibge_code}`
3. Backend returns risk assessment with:
   - Overall risk score
   - 5 hazard indicators (current + 2030 + 2050)
   - Data source attribution (INPE + Cemaden + INMET + Heuristics)
   - Confidence scores
4. Components render visualizations:
   - StatsOverview calculates key metrics
   - RiskChart plots temporal evolution
   - RiskCards display individual hazards
   - ScenarioComparison auto-loads multi-scenario data

## 🧪 Testing

Currently the project uses manual testing. Future improvements:

```bash
# Planned test commands
npm test          # Run unit tests (Vitest)
npm run test:e2e  # Run E2E tests (Playwright)
```

## 🚀 Deployment

### Production Build

```bash
npm run build
# Output: dist/ directory

# Preview production build locally
npm run preview
```

### Environment Variables

Create `.env` file (if needed):
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

## 📝 Development Notes

### Key Features
- ✅ Responsive design (mobile-friendly)
- ✅ Dark mode support (via Tailwind)
- ✅ Error handling with user-friendly messages
- ✅ Loading states during API calls
- ✅ Color-coded risk severity levels
- ✅ Portuguese localization
- ✅ Interactive charts with tooltips

### Performance
- Vite HMR (Hot Module Replacement) for fast development
- Code splitting ready for production
- Optimized bundle size with Rollup

### Code Quality
- TypeScript for type safety
- ESLint for code linting
- Component-based architecture
- Separation of concerns (API, types, components)

## 🤝 Contributing

Key areas for improvement:
- [ ] Add unit tests (Vitest)
- [ ] Add E2E tests (Playwright)
- [ ] Implement map visualization (Leaflet)
- [ ] Add PDF export functionality
- [ ] Improve accessibility (ARIA labels)
- [ ] Add internationalization (i18next)
- [ ] Optimize performance (React.memo, useMemo)

## 📄 License

Apache License 2.0 (same as parent project)

---

**Made with 🟣 in Brazil**
