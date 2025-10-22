# 🟣 PÚRPURA Climate OS

**Climate risk assessment and IFRS S2 compliance platform for Brazilian municipalities, utilities, and enterprises**

Powered by [OS-Climate](https://os-climate.org) open-source tools + custom AI extraction pipeline.

---

## ✅ MVP Status: Ready for Testing!

**Week 5-6 Complete** — Physical Risk Dashboard is live!

🎯 **What's Working:**
- ✅ **Backend API**: Physical risk assessment for 10 Brazilian municipalities
- ✅ **Frontend Dashboard**: React + TypeScript with advanced visualizations
- ✅ **Data Integration**: INPE + Cemaden + INMET + Geographic Heuristics
- ✅ **5 Hazard Types**: Flood, Drought, Heat Stress, Landslide, Coastal Inundation
- ✅ **3 Climate Scenarios**: RCP 2.6, 4.5, 8.5
- ✅ **Temporal Projections**: Current → 2030 → 2050

📊 **Dashboard Features:**
- StatsOverview (6 key risk metrics)
- RiskChart (temporal evolution line chart)
- ScenarioComparison (RCP scenario bar chart)
- RiskCard grid (individual hazard cards)

🚀 **Quick Demo:** [See Quick Start below](#-quick-start) to run locally in 5 minutes!

---

## 🎯 Mission

Enable Brazilian organizations to:
- **Assess** physical climate risks (floods, droughts, heat stress)
- **Extract** climate data from sustainability reports (AI-powered)
- **Comply** with Lei 14.904/2024, IFRS S2, and TSB taxonomy
- **Report** actionable insights for climate adaptation

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Frontend (React + TypeScript)               │
│     📊 Municipal Dashboard ✅ │ 📄 Reports (Planned)         │
│   • Risk visualizations • Scenario comparison • Charts       │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API (FastAPI)
┌──────────────────────────┴──────────────────────────────────┐
│                  Backend (FastAPI + Python)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Extraction  │  │ Risk Engine  │  │  Compliance  │       │
│  │ (Hybrid) ✅ │  │ (physrisk) ✅│  │  (Planned)   │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
│  INPE • Cemaden • INMET • IBGE                              │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│             Data Layer (Trino + Iceberg + MinIO)             │
│  📦 Documents ✅ │ 📊 Extractions ✅ │ 🗺️ Geospatial ✅     │
└─────────────────────────────────────────────────────────────┘
```

### Tech Stack

**Backend:**
- FastAPI (async API framework)
- OS-Climate tools:
  - `osc-transformer-based-extractor` (BERT-based KPI extraction)
  - `physrisk-lib` (physical climate risk modeling)
- OpenAI GPT (hybrid extraction)
- ChromaDB (RAG vector store)
- H3 geospatial indexing

**Data Platform:**
- Trino (distributed SQL)
- Apache Iceberg (table format)
- MinIO (S3-compatible storage)
- PostgreSQL (metadata)

**Frontend:**
- React 18 + TypeScript
- Vite (build tool with HMR)
- Axios (HTTP client)
- Recharts (data visualizations)
- Tailwind CSS (utility-first styling)
- Lucide React (icons)

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Docker + Docker Compose
- 8GB RAM minimum

### 1. Clone & Setup

```bash
git clone https://github.com/brunoccteixeira/PURPURA.git
cd PURPURA

# Create Python environment
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your settings:
# - OPENAI_API_KEY (for LLM extraction)
# - Database credentials
# - Trino connection
```

### 3. Start Infrastructure

```bash
# Start MinIO, Hive, Trino
docker-compose up -d

# Wait for services to be healthy (~30 seconds)
docker-compose ps

# Create Iceberg tables
python scripts/create_iceberg_tables.py
```

### 4. Start API Server

```bash
cd backend
uvicorn api.main:app --reload --port 8000

# API docs available at http://localhost:8000/docs
```

### 5. Start Frontend

```bash
cd frontend
npm install
npm run dev

# Dashboard at http://localhost:3000
# Features:
# - 10 Brazilian municipalities (São Paulo, Rio, Fortaleza, etc.)
# - 5 hazard types (flood, drought, heat stress, landslide, coastal inundation)
# - 3 RCP scenarios (2.6, 4.5, 8.5)
# - Temporal projections (Current → 2030 → 2050)
# - Advanced visualizations (charts, stats, scenario comparison)
```

---

## 📖 Documentation

- **[CLAUDE.md](./CLAUDE.md)** — Developer guide for AI assistants
- **[docs/MVP_PLAN.md](./docs/MVP_PLAN.md)** — 12-week implementation roadmap
- **[docs/API.md](./docs/API.md)** — API reference
- **[docs/OS_CLIMATE_INTEGRATION.md](./docs/OS_CLIMATE_INTEGRATION.md)** — OS-Climate tools usage

---

## 🧪 Testing

```bash
# Run all tests
pytest

# With coverage
pytest --cov=backend --cov-report=html

# Specific test suite
pytest backend/tests/test_extraction.py
```

---

## 📊 Data Pipeline

### Ingest PDF → Extract → Store

```bash
# 1. Ingest PDF to chunks
python scripts/ingest_pdf.py data/sample.pdf \
  --out data/chunks.jsonl \
  --doc-id sample_001

# 2. Extract KPIs (hybrid: transformer + LLM)
python scripts/extract_from_chunks.py data/chunks.jsonl \
  --out data/extracted.jsonl \
  --method hybrid

# 3. Publish to Trino
python scripts/publish_jsonl_to_trino.py data/chunks.jsonl
python scripts/publish_jsonl_to_trino.py data/extracted.jsonl
```

### Query with Trino

```sql
-- View extracted KPIs
SELECT * FROM lake.ifrs.extract_results LIMIT 10;

-- Search by municipality
SELECT * FROM lake.ifrs.municipal_risks
WHERE ibge_code = '3550308';  -- São Paulo
```

---

## 🌍 OS-Climate Integration

PÚRPURA leverages these open-source components:

| Component | Purpose | Status |
|-----------|---------|--------|
| `osc-transformer-presteps` | PDF → JSON conversion | ✅ Integrated |
| `osc-transformer-based-extractor` | BERT KPI extraction | ✅ Integrated |
| `physrisk-lib` | Climate risk calculations | ✅ Integrated |
| `physrisk-ui` | Dashboard patterns | ✅ Integrated |
| H3 geospatial indexing | Municipal risk mapping | ✅ Integrated |

### Brazilian Data Sources

| Source | Purpose | Status |
|--------|---------|--------|
| **INPE** (PCBr API) | Climate projections (temperature, precipitation) | ✅ Integrated |
| **Cemaden** | Historical hazard frequency (floods, landslides) | ✅ Mock data ready |
| **INMET** (BDMEP) | Climate normals (1961-2023), station catalog | ✅ Mock data ready |
| **IBGE** | Municipality codes, population, coordinates | ✅ Integrated |

**License Compliance:**
All OS-Climate code is Apache 2.0 licensed. PÚRPURA maintains attribution and contributes improvements upstream.

---

## 🎨 Branding

- **Name:** PÚRPURA (purple in Portuguese, symbolizing innovation + sustainability)
- **Target:** Brazilian mid-market (municipalities 50-500k, regional utilities, SMEs)
- **Language:** 100% Portuguese (pt-BR)
- **Differentiator:** Partnership-first approach (Colab, Cemaden, TNC) + tropicalized models

---

## 🛣️ Roadmap

### Phase 1: Municipal MVP (Weeks 1-12) — **Current**
- [x] Data lakehouse infrastructure
- [x] LLM extraction pipeline (OpenAI)
- [x] FastAPI backend scaffold
- [x] Transformer-based extraction integration
- [x] Physical risk engine (physrisk + Brazilian data sources)
- [x] Municipal dashboard UI (React + TypeScript)
- [ ] 2 pilot deployments

### Phase 2: Enterprise TSB (Months 4-6)
- [ ] TSB taxonomy classifier
- [ ] IFRS S2 reporting module
- [ ] Enterprise dashboard
- [ ] 10-15 customer deployments

### Phase 3: Scale (Months 7-12)
- [ ] Agro module (AQUASENSE)
- [ ] Smart city monitoring (MONITOR)
- [ ] PIM-PAM tools (RMPT, CCS, PIA)
- [ ] 100+ municipalities, 20+ enterprises

---

## 📈 Success Metrics (Week 12 Target)

- ✅ 2 pilot customers deployed
- ✅ 10+ documents processed end-to-end
- ✅ <5min extraction time per document
- ✅ >85% pilot user satisfaction
- ✅ 1 Colab partnership MoU signed

---

## 🤝 Contributing

We welcome contributions! Please see [CONTRIBUTING.md](./CONTRIBUTING.md).

Key areas:
- Brazilian climate data sources integration (Cemaden, INPE, ANA)
- IFRS S2 / TSB schema validation
- Portuguese NLP improvements
- Municipal dashboard UX

---

## 📄 License

**PÚRPURA Climate OS** is licensed under the Apache License 2.0.

This project incorporates components from [OS-Climate](https://os-climate.org), also Apache 2.0 licensed.

---

## 🙏 Acknowledgments

- **OS-Climate** — Open-source climate tools foundation
- **Cemaden** — Brazilian climate monitoring data
- **Linux Foundation / FINOS** — Governance and community support

---

## 📞 Contact

- **Website:** [purpura.climate](https://purpura.climate) _(coming soon)_
- **GitHub:** [github.com/brunoccteixeira/PURPURA](https://github.com/brunoccteixeira/PURPURA)
- **Email:** bruno@purpura.climate

---

**Made with 🟣 in Brazil**
