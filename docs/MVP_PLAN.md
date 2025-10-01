# PÚRPURA MVP Implementation Plan (12 Weeks)

**Goal:** Deploy 2 pilots (1 municipality 100-500k + 1 regional utility) with climate risk dashboard

**Stack:** FastAPI + React + OS-Climate tools + Trino/Iceberg

---

## Week 1-2: Enhanced Data Extraction

### Objectives
- Integrate OS-Climate transformer-based extraction
- Build hybrid extraction pipeline (transformer + LLM)
- Add confidence scoring and validation

### Tasks
- [ ] Install and test `osc-transformer-presteps` on sample PDFs
- [ ] Install and test `osc-transformer-based-extractor` for KPI detection
- [ ] Build unified extraction service combining both methods
- [ ] Add confidence scoring to extraction results
- [ ] Update Trino schema for extraction metadata
- [ ] Migrate existing `src/extract/llm_extractor.py` to `backend/extraction/llm/`
- [ ] Create `backend/extraction/transformers/osc_adapter.py`
- [ ] Create `backend/extraction/hybrid.py` orchestrator

### Deliverables
- Working hybrid extraction pipeline
- Extraction confidence metrics
- Updated database schema

---

## Week 3-4: Physical Risk & API

### Objectives
- Integrate physrisk library for climate risk calculations
- Build H3 geospatial indexing service
- Complete FastAPI backend with all endpoints

### Tasks
- [ ] Install `physrisk-lib` and run example calculations
- [ ] Adapt physrisk for Brazilian climate data (Cemaden API integration)
- [ ] Build H3 geospatial indexing service
- [ ] Implement authentication (JWT + multi-tenant)
- [ ] Complete all API endpoints (documents, extraction, risk, compliance)
- [ ] Add database connection layer (PostgreSQL + Trino)
- [ ] Create MinIO client service for file storage
- [ ] Write API integration tests

### Deliverables
- Functional REST API (all endpoints)
- Municipal risk calculation engine
- H3 grid risk mapping

---

## Week 5-6: Frontend Foundation

### Objectives
- Scaffold React application
- Apply PÚRPURA branding
- Build core UI components

### Tasks
- [ ] Initialize React + TypeScript app with Vite
- [ ] Set up Tailwind CSS + design system
- [ ] Create PÚRPURA branding (colors, logo, typography)
- [ ] Implement Portuguese (pt-BR) i18n
- [ ] Build document upload + management UI
- [ ] Build extraction results viewer (JSON tree with confidence scores)
- [ ] Create API client service (TanStack Query)
- [ ] Set up routing (React Router)

### Deliverables
- Branded React application
- Document management interface
- Extraction results viewer

---

## Week 7-8: Municipal Dashboard

### Objectives
- Build interactive risk dashboard for municipalities
- Integrate maps and visualizations
- Complete Lei 14.904 report generator

### Tasks
- [ ] Integrate Leaflet/Mapbox for municipality maps
- [ ] Build risk heatmap visualization (H3 grid overlay)
- [ ] Implement climate hazard charts (Cemaden data viz)
- [ ] Create vulnerability indicators dashboard
- [ ] Build scenario modeling UI (El Niño/La Niña impacts)
- [ ] Implement Lei 14.904 report generator UI
- [ ] Add PDF export functionality
- [ ] Create settings/configuration panel

### Deliverables
- Interactive municipal risk dashboard
- Climate hazard visualizations
- Lei 14.904 compliance reports

---

## Week 9-10: RAG & Validation

### Objectives
- Implement semantic search for evidence retrieval
- Add data validation and quality metrics
- Build verification workflows

### Tasks
- [ ] Implement vector store (ChromaDB)
- [ ] Create embedding pipeline (OpenAI or sentence-transformers)
- [ ] Build semantic search for evidence retrieval
- [ ] Implement schema validation (IFRS S2, TSB, Lei 14.904)
- [ ] Create data quality dashboard
- [ ] Build human-in-the-loop validation UI
- [ ] Add cross-reference validation with IBGE data
- [ ] Implement audit logging

### Deliverables
- RAG-powered evidence search
- Data validation framework
- Quality metrics dashboard

---

## Week 11-12: Testing & Pilot Deployment

### Objectives
- Achieve >70% test coverage
- Process sample datasets
- Deploy to production
- Prepare pilot materials

### Tasks
- [ ] Write unit tests (backend: pytest, frontend: Jest)
- [ ] Write integration tests (API + Trino)
- [ ] Write E2E tests (Playwright critical flows)
- [ ] Process 5 municipal + 2 utility sample reports
- [ ] Deploy to cloud VM (DigitalOcean/AWS)
- [ ] Configure monitoring (Prometheus + Grafana)
- [ ] Create user documentation (Portuguese)
- [ ] Prepare training materials (video walkthroughs)
- [ ] Set up support infrastructure (issue tracking, email)
- [ ] Conduct pilot onboarding sessions

### Deliverables
- Fully tested application (>70% coverage)
- Production deployment
- Pilot customer onboarding complete
- User documentation and training

---

## Success Criteria (Week 12)

- ✅ 2 pilot deployments live
- ✅ 10+ documents processed end-to-end
- ✅ <5min average extraction time per document
- ✅ >85% pilot user satisfaction (survey)
- ✅ 1 Colab partnership MoU signed
- ✅ Seed fundraising deck ready

---

## Risk Mitigation

| Risk | Probability | Mitigation |
|------|------------|------------|
| OS-Climate tools not Brazil-ready | Medium | Keep LLM fallback; adapt data sources |
| Physrisk learning curve too steep | Medium | Start with simple scenarios; reference docs |
| Frontend complexity delays delivery | High | Use minimal UI; focus on core workflows |
| Pilot customers not ready | Medium | Use Colab for distribution; have backup pilots |
| API performance issues | Low | Implement caching (Redis); async processing |
| Data quality problems | High | Human-in-the-loop validation UI; confidence scores |

---

## Team & Resources

### Required Skills
- **Backend:** Python, FastAPI, SQL, ML/NLP
- **Frontend:** React, TypeScript, data visualization
- **DevOps:** Docker, cloud deployment, monitoring
- **Domain:** Climate science, IFRS S2, Brazilian regulation

### Budget (MVP)
- Development: Volunteer/founding team
- Infrastructure: ~R$ 1.500/month (cloud VM + APIs)
- Total: <R$ 20.000 for 12 weeks

---

## Post-MVP (Weeks 13-16)

### Pilot Phase Activities
- Weekly check-ins with pilot customers
- Bug fixes and UX improvements
- Data quality refinement
- Performance optimization
- Prepare for Seed fundraising (R$ 1-2M)

### Scaling Preparation
- Kubernetes migration planning
- Multi-region deployment design
- SaaS pricing model finalization
- Marketing and sales materials

---

**Last Updated:** 2025-10-01
**Status:** In Progress (Week 1)
