# 🟣 PÚRPURA Design System

**Brand Identity & Visual Language**

---

## 🎨 Brand Concept

**PÚRPURA** (Portuguese for "purple") symbolizes:
- **Innovation** - Cutting-edge AI + climate science
- **Sustainability** - Environmental focus
- **Trust** - Institutional credibility
- **Brazilian Identity** - Tropicalized for Brazilian market

---

## Color Palette

### Primary Colors

```css
/* Purple Spectrum - Main Brand */
--purple-50:  #faf5ff;   /* Very light backgrounds */
--purple-100: #f3e8ff;   /* Hover states */
--purple-200: #e9d5ff;   /* Borders */
--purple-300: #d8b4fe;   /* Disabled states */
--purple-400: #c084fc;   /* Secondary elements */
--purple-500: #a855f7;   /* PRIMARY BRAND COLOR */
--purple-600: #9333ea;   /* Hover primary */
--purple-700: #7e22ce;   /* Active primary */
--purple-800: #6b21a8;   /* Dark mode primary */
--purple-900: #581c87;   /* Deep accents */
```

### Secondary Colors

```css
/* Climate Risk Gradient */
--green-500:  #10b981;   /* Low risk / safe */
--yellow-500: #f59e0b;   /* Moderate risk */
--orange-500: #f97316;   /* High risk */
--red-500:    #ef4444;   /* Critical risk */

/* Supporting Colors */
--blue-500:   #3b82f6;   /* Water / hydrology */
--teal-500:   #14b8a6;   /* Sustainability */
--slate-500:  #64748b;   /* Neutral UI elements */
```

### Neutrals

```css
/* Gray Scale */
--gray-50:  #f9fafb;
--gray-100: #f3f4f6;
--gray-200: #e5e7eb;
--gray-300: #d1d5db;
--gray-400: #9ca3af;
--gray-500: #6b7280;
--gray-600: #4b5563;
--gray-700: #374151;
--gray-800: #1f2937;
--gray-900: #111827;
```

---

## Typography

### Font Families

```css
/* Primary Font: Inter (sans-serif) */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Code/Monospace: JetBrains Mono */
@import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;500;600&display=swap');

--font-sans: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Courier New', monospace;
```

### Type Scale

```css
/* Headings */
--text-xs:   0.75rem;   /* 12px */
--text-sm:   0.875rem;  /* 14px */
--text-base: 1rem;      /* 16px */
--text-lg:   1.125rem;  /* 18px */
--text-xl:   1.25rem;   /* 20px */
--text-2xl:  1.5rem;    /* 24px */
--text-3xl:  1.875rem;  /* 30px */
--text-4xl:  2.25rem;   /* 36px */
--text-5xl:  3rem;      /* 48px */
```

### Font Weights

```css
--font-light:    300;
--font-normal:   400;
--font-medium:   500;
--font-semibold: 600;
--font-bold:     700;
--font-extrabold: 800;
```

---

## Spacing Scale

```css
/* Tailwind-compatible 8px base grid */
--space-0:  0;
--space-1:  0.25rem;  /* 4px */
--space-2:  0.5rem;   /* 8px */
--space-3:  0.75rem;  /* 12px */
--space-4:  1rem;     /* 16px */
--space-5:  1.25rem;  /* 20px */
--space-6:  1.5rem;   /* 24px */
--space-8:  2rem;     /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
--space-20: 5rem;     /* 80px */
--space-24: 6rem;     /* 96px */
```

---

## Components

### Buttons

```typescript
// Primary Button
<button className="
  bg-purple-600 hover:bg-purple-700
  text-white font-medium
  px-4 py-2 rounded-lg
  transition-colors duration-200
  focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2
">
  Calcular Risco
</button>

// Secondary Button
<button className="
  bg-white hover:bg-gray-50
  text-purple-600 font-medium
  border border-purple-300
  px-4 py-2 rounded-lg
  transition-colors duration-200
">
  Ver Detalhes
</button>

// Danger Button
<button className="
  bg-red-600 hover:bg-red-700
  text-white font-medium
  px-4 py-2 rounded-lg
">
  Excluir
</button>
```

### Cards

```typescript
<div className="
  bg-white rounded-xl shadow-sm
  border border-gray-200
  p-6
  hover:shadow-md transition-shadow
">
  {/* Card content */}
</div>
```

### Risk Badge

```typescript
const getRiskColor = (score: number) => {
  if (score < 0.3) return 'bg-green-100 text-green-800';
  if (score < 0.5) return 'bg-yellow-100 text-yellow-800';
  if (score < 0.7) return 'bg-orange-100 text-orange-800';
  return 'bg-red-100 text-red-800';
};

<span className={`
  ${getRiskColor(riskScore)}
  px-3 py-1 rounded-full text-sm font-medium
`}>
  {(riskScore * 100).toFixed(0)}% risco
</span>
```

---

## Iconography

**Icon Library:** [Lucide React](https://lucide.dev/)

```bash
npm install lucide-react
```

**Common Icons:**
- `MapPin` - Location markers
- `CloudRain` - Flood hazard
- `Droplet` - Water/drought
- `Thermometer` - Heat stress
- `AlertTriangle` - Warnings
- `TrendingUp` - Risk increase
- `Shield` - Low risk/protection
- `BarChart3` - Analytics
- `Map` - Geospatial view

---

## Layout

### Grid System

```typescript
// Main Layout
<div className="min-h-screen bg-gray-50">
  <nav className="bg-white border-b border-gray-200 sticky top-0 z-50">
    {/* Navigation */}
  </nav>

  <main className="container mx-auto px-4 py-8 max-w-7xl">
    {/* Page content */}
  </main>
</div>
```

### Responsive Breakpoints

```css
/* Tailwind breakpoints */
sm:  640px   /* Mobile landscape */
md:  768px   /* Tablets */
lg:  1024px  /* Desktop */
xl:  1280px  /* Large desktop */
2xl: 1536px  /* Extra large */
```

---

## Map Visualization

### Risk Heatmap Colors

```typescript
const getRiskHeatmapColor = (riskScore: number): string => {
  if (riskScore < 0.2) return '#10b981'; // green-500
  if (riskScore < 0.4) return '#84cc16'; // lime-500
  if (riskScore < 0.6) return '#f59e0b'; // yellow-500
  if (riskScore < 0.8) return '#f97316'; // orange-500
  return '#ef4444'; // red-500
};
```

### H3 Hexagon Styling

```typescript
// Leaflet GeoJSON style
{
  fillColor: getRiskHeatmapColor(feature.properties.risk_score),
  fillOpacity: 0.6,
  color: '#374151', // gray-700
  weight: 1,
  opacity: 0.8
}
```

---

## Data Visualization

### Chart Colors

```typescript
// For Recharts/Chart.js
const chartColors = {
  primary: '#a855f7',    // purple-500
  flood: '#3b82f6',      // blue-500
  drought: '#f59e0b',    // yellow-500
  heatStress: '#ef4444', // red-500
  grid: '#e5e7eb',       // gray-200
  text: '#374151',       // gray-700
};
```

### Risk Level Scale

```
0.0 - 0.3: Baixo (Verde)
0.3 - 0.5: Moderado (Amarelo)
0.5 - 0.7: Alto (Laranja)
0.7 - 1.0: Crítico (Vermelho)
```

---

## Animation & Motion

```css
/* Transitions */
--transition-fast:   150ms ease-in-out;
--transition-base:   200ms ease-in-out;
--transition-slow:   300ms ease-in-out;

/* Common animations */
.fade-in {
  animation: fadeIn 300ms ease-in;
}

@keyframes fadeIn {
  from { opacity: 0; }
  to { opacity: 1; }
}

.slide-in-up {
  animation: slideInUp 300ms ease-out;
}

@keyframes slideInUp {
  from {
    opacity: 0;
    transform: translateY(20px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}
```

---

## Portuguese (pt-BR) Copy

### Common Labels

```typescript
const ptBR = {
  // Navigation
  dashboard: 'Painel',
  municipalities: 'Municípios',
  documents: 'Documentos',
  reports: 'Relatórios',
  settings: 'Configurações',

  // Risk Assessment
  risk: 'Risco',
  lowRisk: 'Risco Baixo',
  moderateRisk: 'Risco Moderado',
  highRisk: 'Risco Alto',
  criticalRisk: 'Risco Crítico',

  // Hazards
  flood: 'Inundação',
  drought: 'Seca',
  heatStress: 'Estresse Térmico',
  landslide: 'Deslizamento',
  coastalInundation: 'Inundação Costeira',

  // Time periods
  current: 'Atual',
  projected2030: 'Projeção 2030',
  projected2050: 'Projeção 2050',

  // Actions
  calculate: 'Calcular',
  viewDetails: 'Ver Detalhes',
  download: 'Baixar',
  export: 'Exportar',
  upload: 'Enviar',

  // Common
  loading: 'Carregando...',
  error: 'Erro',
  success: 'Sucesso',
  municipality: 'Município',
  scenario: 'Cenário',
  confidence: 'Confiança',
};
```

---

## Accessibility

### WCAG 2.1 AA Compliance

- ✅ Color contrast ratio ≥ 4.5:1 for text
- ✅ Focus indicators on all interactive elements
- ✅ Semantic HTML (nav, main, section, article)
- ✅ ARIA labels for icon-only buttons
- ✅ Keyboard navigation support
- ✅ Screen reader friendly

### Example

```typescript
<button
  aria-label="Calcular risco climático para São Paulo"
  className="focus:ring-2 focus:ring-purple-500"
>
  <Calculator className="w-5 h-5" />
</button>
```

---

## Logo Concept

```
  🟣
PÚRPURA
Climate OS
```

**Logo Elements:**
- Purple hexagon (H3 cell reference)
- Clean sans-serif typography
- Optional: Climate icon integration (cloud, droplet, thermometer)

**Usage:**
- Primary: Full color logo on white
- Secondary: White logo on purple background
- Monochrome: Grayscale for documents

---

## Dark Mode (Future)

```css
/* Dark mode color overrides */
.dark {
  --bg-primary: #111827;    /* gray-900 */
  --bg-secondary: #1f2937;  /* gray-800 */
  --text-primary: #f9fafb;  /* gray-50 */
  --text-secondary: #d1d5db; /* gray-300 */
  --purple-primary: #c084fc; /* purple-400 for dark bg */
}
```

---

## Implementation Priority

### Phase 1 (Week 5-6):
1. ✅ Color system
2. ✅ Typography
3. ✅ Button components
4. ✅ Card components
5. ✅ Risk badges
6. ✅ Map colors

### Phase 2 (Week 7-8):
1. Chart components
2. Form inputs
3. Modals/dialogs
4. Navigation components

### Phase 3 (Week 9-10):
1. Dark mode
2. Animation refinements
3. Accessibility audit
4. Component documentation (Storybook)

---

**Last Updated:** 2025-10-21
**Status:** Ready for frontend implementation
