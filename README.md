# 🟣 PÚRPURA Climate OS

**Climate risk assessment and IFRS S2 compliance platform for Brazilian organizations, utilities and municipalities**

Powered by [OS-Climate](https://os-climate.org) open-source tools + custom AI extraction pipeline.

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
│                    Frontend (React + TS)                     │
│  📊 Municipal Dashboard │ 📄 Document Manager │ 📈 Reports   │
└──────────────────────────┬──────────────────────────────────┘
                           │ REST API
┌──────────────────────────┴──────────────────────────────────┐
│                  Backend (FastAPI + Python)                  │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────┐       │
│  │ Extraction  │  │ Risk Engine  │  │  Compliance  │       │
│  │ (Hybrid)    │  │ (physrisk)   │  │  (Lei 14904) │       │
│  └─────────────┘  └──────────────┘  └──────────────┘       │
└──────────────────────────┬──────────────────────────────────┘
                           │
┌──────────────────────────┴──────────────────────────────────┐
│             Data Layer (Trino + Iceberg + MinIO)             │
│  📦 Documents │ 📊 Extractions │ 🗺️ Geospatial (H3)         │
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
- TanStack Query (API state)
- Recharts/D3 (visualizations)
- Leaflet (maps)
- Tailwind CSS

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

### 5. Start Frontend (Coming Soon)

```bash
cd frontend
npm install
npm run dev

# Dashboard at http://localhost:3000
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
| `physrisk-lib` | Climate risk calculations | 🚧 In Progress |
| `physrisk-ui` | Dashboard patterns | 📋 Planned |
| H3 geospatial indexing | Municipal risk mapping | 📋 Planned |

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
- [ ] Transformer-based extraction integration
- [ ] Physical risk engine (physrisk)
- [ ] Municipal dashboard UI
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
