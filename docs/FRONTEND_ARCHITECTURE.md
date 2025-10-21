# 🟣 PÚRPURA Frontend Architecture Plan

## Modern Geospatial Dashboard with OS-Climate Integration

**Date:** 2025-10-21
**Objective:** Build world-class climate risk dashboard using best-in-class tools

---

## 🎯 Technology Stack

### Core Framework
- **React 18** + **TypeScript** + **Vite** ✅ (installed)
- **Tailwind CSS** ✅ (configured)
- **React Router** ✅ (installed)

### Geospatial Visualization
- **deck.gl** (WebGL-powered maps) - PRIMARY
  - `@deck.gl/react` - React bindings
  - `@deck.gl/geo-layers` - H3HexagonLayer
  - `@deck.gl/core` - Core rendering
- **h3-js** - H3 geospatial indexing
- **MapLibre GL JS** - Base map tiles

### Data Visualization
- **Recharts** (React charts) - Recommended by OS-Climate
- **Victory** (Alternative for complex charts)
- **React-ECharts** (For advanced visualizations)

### State Management & API
- **@tanstack/react-query** ✅ (installed)
- **axios** ✅ (installed)
- **zustand** (Lightweight state management)

### UI Components
- **Lucide React** ✅ (icons)
- **Headless UI** (Accessible components)
- **Radix UI** (Primitive components)

---

## 🌍 Integration Strategy

### 1. OS-Climate Integration

**physrisk-ui Learnings:**
- Uses React + Create React App
- Likely uses Recharts (industry standard)
- Connects to physrisk-api backend
- Focus on scenario comparison

**What We'll Adopt:**
- ✅ React component architecture
- ✅ Recharts for charts
- ✅ Scenario selection UI patterns
- ✅ Risk indicator displays

**What We'll Improve:**
- 🟣 Modern deck.gl instead of older map libs
- 🟣 Tailwind CSS instead of Material-UI
- 🟣 TanStack Query for better caching
- 🟣 Our own API (physrisk + Brazilian data)

---

### 2. deck.gl H3 Visualization

**Why deck.gl?**
- ✅ Industry standard (Uber, CARTO)
- ✅ WebGL performance (thousands of hexagons)
- ✅ Native H3HexagonLayer support
- ✅ Beautiful out-of-the-box

**Implementation:**
```typescript
import DeckGL from '@deck.gl/react';
import { H3HexagonLayer } from '@deck.gl/geo-layers';

const h3Layer = new H3HexagonLayer({
  id: 'h3-risk-layer',
  data: riskGridData, // From our API
  pickable: true,
  wireframe: false,
  filled: true,
  extruded: true,
  getHexagon: d => d.h3_index,
  getFillColor: d => getRiskColor(d.risk_score),
  getElevation: d => d.risk_score * 1000,
  elevationScale: 100,
});
```

**Data Flow:**
```
Backend API (/h3-grid/{ibge_code})
  → TanStack Query cache
  → H3HexagonLayer data prop
  → deck.gl renders WebGL
```

---

### 3. CARTO Integration (Future)

**Current Status:**
- CARTO for React being deprecated
- Recommended: CARTO + deck.gl directly
- CARTO supports H3 and Quadbins

**Our Approach:**
- **Phase 1:** Use deck.gl with our own data ✅
- **Phase 2:** Add CARTO basemaps (optional)
- **Phase 3:** Consider CARTO warehouse if scaling

**Benefits:**
- Professional basemaps
- SQL API for big data
- H3 native support
- Cloud-native geospatial

---

### 4. LGND.io Integration (Future)

**Potential Use Cases:**
- Geographic embeddings for similarity search
- "Find municipalities similar to São Paulo"
- AI-powered spatial analysis
- Earth data enrichment

**Integration Points:**
- Embeddings API for municipality clustering
- Spatial feature extraction
- Enhanced risk predictions

**Timeline:** Phase 2 (after MVP)

---

### 5. Clay (madewithclay.org) Integration (Future)

**Potential Use Cases:**
- Deforestation detection for Brazil
- Environmental monitoring
- Vector embeddings for climate data
- Public datasets integration

**Integration Points:**
- Layer overlay for environmental data
- AI-powered insights
- Real-time monitoring integration

**Timeline:** Phase 3 (scaling)

---

## 📐 Dashboard Architecture

### Page Structure

```
/
├── Dashboard (/)
│   ├── MunicipalitySelector
│   ├── RiskOverview
│   ├── MapView (deck.gl)
│   └── HazardCharts (Recharts)
│
├── Map (/map)
│   ├── FullScreenMap
│   ├── H3GridLayer
│   ├── LayerControls
│   └── LocationSearch
│
├── Municipality (/municipality/:ibge_code)
│   ├── MunicipalHeader
│   ├── RiskScoreCard
│   ├── HazardBreakdown
│   ├── ScenarioComparison
│   ├── Timeline (2030, 2050)
│   └── Recommendations
│
├── Documents (/documents)
│   ├── DocumentList
│   ├── Upload
│   └── ExtractionResults
│
└── About (/about)
    ├── Methodology
    ├── DataSources
    └── Contact
```

### Component Hierarchy

```
App
└── Layout
    ├── Header (Navigation)
    ├── Main (Routes)
    │   ├── DashboardPage
    │   │   ├── MapView
    │   │   │   ├── DeckGLMap
    │   │   │   │   └── H3HexagonLayer
    │   │   │   └── MapControls
    │   │   ├── RiskMetrics
    │   │   │   ├── OverallRiskCard
    │   │   │   └── HazardCards
    │   │   └── ChartsSection
    │   │       ├── TimelineChart
    │   │       └── ScenarioChart
    │   └── ...
    └── Footer
```

---

## 🎨 UI/UX Design Principles

### Color System (from design system)
```typescript
const riskColors = {
  low: '#10b981',      // green-500
  moderate: '#f59e0b', // yellow-500
  high: '#f97316',     // orange-500
  critical: '#ef4444', // red-500
};

const brandColor = '#a855f7'; // purple-500
```

### Map Styling
```typescript
const getH3FillColor = (riskScore: number): [number, number, number] => {
  if (riskScore < 0.3) return [16, 185, 129];  // green
  if (riskScore < 0.5) return [245, 158, 11];  // yellow
  if (riskScore < 0.7) return [249, 115, 22];  // orange
  return [239, 68, 68];                         // red
};
```

### Responsive Design
- Desktop: Split view (map + metrics)
- Tablet: Stacked with collapsible map
- Mobile: Tabs (map, metrics, charts)

---

## 🔌 API Integration

### API Client Structure

```typescript
// src/lib/api/client.ts
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: { 'Content-Type': 'application/json' },
});

// src/lib/api/queries/risk.ts
import { useQuery } from '@tanstack/react-query';

export const useMunicipalRisk = (ibgeCode: string, scenario: string) => {
  return useQuery({
    queryKey: ['municipal-risk', ibgeCode, scenario],
    queryFn: () =>
      apiClient.get(`/api/v1/risk/municipality/${ibgeCode}`, {
        params: { scenario }
      }).then(res => res.data),
    staleTime: 1000 * 60 * 5, // 5 minutes
  });
};

export const useH3Grid = (ibgeCode: string, resolution: number) => {
  return useQuery({
    queryKey: ['h3-grid', ibgeCode, resolution],
    queryFn: () =>
      apiClient.get(`/api/v1/risk/h3-grid/${ibgeCode}`, {
        params: { resolution, format: 'heatmap' }
      }).then(res => res.data),
  });
};
```

---

## 📊 Data Flow

```
User Interaction
  ↓
React Component
  ↓
TanStack Query Hook
  ↓
Axios API Call (with cache)
  ↓
Backend REST API (/api/v1/risk/...)
  ↓
RiskCalculator + H3Service
  ↓
Response (JSON)
  ↓
TanStack Query Cache
  ↓
React Component Re-render
  ↓
deck.gl / Recharts Visualization
```

---

## 🚀 Implementation Phases

### Phase 1: Core Dashboard (Week 5-6)
- [x] Project setup (Vite, Tailwind, Router)
- [ ] Install deck.gl + h3-js
- [ ] API client + TanStack Query
- [ ] Basic layout + navigation
- [ ] DeckGL map component
- [ ] H3HexagonLayer integration
- [ ] Municipality selector
- [ ] Risk metrics display

### Phase 2: Rich Visualizations (Week 7-8)
- [ ] Recharts timeline charts
- [ ] Scenario comparison
- [ ] Hazard breakdown charts
- [ ] Interactive tooltips
- [ ] Legend component
- [ ] Layer controls

### Phase 3: Advanced Features (Week 9-10)
- [ ] Document upload UI
- [ ] Extraction results viewer
- [ ] Export functionality
- [ ] Print-friendly reports
- [ ] Accessibility audit
- [ ] i18n (pt-BR)

### Phase 4: Integrations (Future)
- [ ] CARTO basemaps
- [ ] LGND.io embeddings
- [ ] Clay environmental data
- [ ] Real-time updates

---

## 🎯 Success Metrics

**Performance:**
- First Contentful Paint: <1.5s
- Time to Interactive: <3s
- H3 grid render: <500ms (1000 cells)

**UX:**
- Intuitive navigation
- Mobile responsive
- Accessible (WCAG 2.1 AA)
- Portuguese labels

**Technical:**
- Type-safe (TypeScript)
- Test coverage >70%
- Clean component architecture
- Reusable design system

---

## 📚 Resources

### Documentation Links
- **deck.gl:** https://deck.gl/docs
- **H3HexagonLayer:** https://deck.gl/docs/api-reference/geo-layers/h3-hexagon-layer
- **TanStack Query:** https://tanstack.com/query/latest
- **Recharts:** https://recharts.org/
- **Tailwind CSS:** https://tailwindcss.com/

### Inspiration
- **OS-Climate physrisk-ui:** https://github.com/os-climate/physrisk-ui
- **CARTO demos:** https://carto.com/developers/deck-gl/
- **deck.gl examples:** https://deck.gl/examples

---

## 🔮 Future Enhancements

### Advanced Analytics
- Machine learning predictions
- Similarity clustering (LGND.io)
- Trend analysis
- Anomaly detection

### Real-time Features
- Live weather data
- Alert notifications
- WebSocket updates
- Streaming data

### Collaboration
- Multi-user dashboards
- Shared reports
- Comments/annotations
- Export templates

---

**Status:** Ready for implementation
**Next:** Install deck.gl and build map component
**Owner:** PÚRPURA Team

🟣 **Powered by OS-Climate + Modern Web Stack**
