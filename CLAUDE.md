# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**PÚRPURA × OS-Climate** — An MVP for IFRS S2 climate disclosure reporting using LLM+RAG, Trino/Iceberg data lakehouse, and visualization tools. The system extracts structured climate risk data (physical and transition risks) from PDF documents using LLM-based extraction with schema validation.

## Architecture

### Data Flow Pipeline

1. **Ingest**: PDFs → text extraction → chunking (token-aware with overlap)
2. **Extract**: LLM-based structured extraction (OpenAI JSON mode) against IFRS S2 schema
3. **Store**: Iceberg tables via Trino (Parquet format on MinIO S3)
4. **Query**: Trino SQL interface for analytics

### Stack Components

- **Storage**: MinIO (S3-compatible) at `s3a://purpura/`
- **Metastore**: Hive Metastore 3.1.3 backed by PostgreSQL
- **Query Engine**: Trino with Iceberg connector (`lake.ifrs` catalog/schema)
- **LLM**: OpenAI API (gpt-4o-mini default) with structured JSON output
- **Chunking**: Token-aware using tiktoken (cl100k_base encoding)

### Module Structure

```
src/
├── extract/          # LLM extraction logic
│   ├── llm_extractor.py         # Core extraction with OpenAI JSON mode
│   └── llm_extractor_adapter.py # Adapter layer
├── ingest/          # PDF processing
│   ├── pdf_ingestor.py  # pypdf-based extraction
│   └── chunker.py       # Token-aware text chunking
├── retrieval/       # RAG indexing (future)
├── utils/           # Shared utilities
│   └── trino_client.py  # Trino connection with sys.path sanitization
└── verify/          # Data validation

scripts/
├── ingest_pdf.py              # PDF → JSONL chunks
├── extract_from_chunks.py     # Chunks → extracted KPIs
├── create_iceberg_tables.py   # Schema setup
├── publish_jsonl_to_trino.py  # JSONL → Trino bulk insert
└── dry_run_extract.py         # Mock extraction for dev
```

## Common Commands

### Environment Setup

```bash
# Python virtual environment (3.11+)
source .venv/bin/activate  # or `python -m venv .venv` to create

# No requirements.txt yet; dependencies installed manually:
# pip install pypdf tiktoken openai trino jsonschema
```

### Infrastructure

```bash
# Start all services (MinIO, Hive Metastore, Trino)
docker-compose up -d

# Check service health
docker-compose ps

# Trino CLI access
docker exec -it trino trino

# View Trino logs
docker logs -f trino
```

### Data Pipeline Execution

```bash
# 1. Create Iceberg tables (run once or after schema changes)
python scripts/create_iceberg_tables.py

# 2. Ingest PDF to chunks
python scripts/ingest_pdf.py path/to/document.pdf \
  --out data/chunks.jsonl \
  --doc-id my_doc_001 \
  --max-tokens 800 \
  --overlap 120

# 3. Extract structured data from chunks
python scripts/extract_from_chunks.py data/chunks.jsonl \
  --out data/extracted.jsonl \
  --schema schemas/ifrs_s2_core.schema.json \
  --module src.extract.llm_extractor

# 4. Publish to Trino
python scripts/publish_jsonl_to_trino.py data/chunks.jsonl      # raw chunks
python scripts/publish_jsonl_to_trino.py data/extracted.jsonl  # extraction results
```

### Development & Testing

```bash
# Mock extraction (no API calls)
export LLM_MOCK=1
python scripts/dry_run_extract.py

# Run with OpenAI
export OPENAI_API_KEY=sk-...
export OPENAI_MODEL=gpt-4o-mini  # optional
export OPENAI_ORG_ID=org_xxx     # optional
export OPENAI_PROJECT_ID=proj_xxx # optional
python scripts/dry_run_extract.py

# Lint
ruff check .

# Validate JSON schemas
python -m json.tool schemas/ifrs_s2_core.schema.json
```

### Trino Environment Variables

Default connection params (override as needed):

```bash
export TRINO_HOST=localhost
export TRINO_PORT=8080
export TRINO_USER=bruno
export TRINO_CATALOG=lake
export TRINO_SCHEMA=ifrs
```

## Key Implementation Details

### LLM Extraction (`src/extract/llm_extractor.py`)

- Uses OpenAI JSON mode (`response_format={"type": "json_object"}`) for reliability
- Mock mode via `LLM_MOCK=1` environment variable returns deterministic responses
- Template-driven prompts with placeholders: `{{json_schema}}`, `{{evidence_chunks}}`, `{{task_description}}`
- Optional `jsonschema` validation; degrades gracefully if not installed
- Fallback JSON extraction from markdown code blocks if structured mode fails

### Chunking Strategy (`src/ingest/chunker.py`)

- Token-based with configurable overlap (default 800 tokens, 120 overlap)
- Uses tiktoken when available; falls back to `len(text)//4` heuristic
- Preserves word boundaries (splits on `\s+`)
- Returns list of `{"text": str, "token_len": int}` dicts

### Trino Client (`src/utils/trino_client.py`)

- **Critical**: `sys.path` sanitization prevents conflicts with local `trino/` directory
- Retry logic with exponential backoff (`wait_ready` function)
- Connection pooling not implemented; scripts create new connections per run

### Iceberg Tables (`scripts/create_iceberg_tables.py`)

Schema created in `lake.ifrs`:

1. **`raw_chunks`**: doc_id, chunk_id, source_path, created_at, token_len, char_len, text_sha256, text
2. **`extract_results`**: doc_id, chunk_id, result_json (VARCHAR), created_at

Both use PARQUET format. Warehouse location: `s3a://purpura/lake/ifrs/`

## Docker Infrastructure Notes

### MinIO

- Console: http://localhost:9001 (minio/minio123)
- API: http://localhost:9000
- Bucket `purpura` auto-created by `mc-init` service

### Trino

- Web UI: http://localhost:8080
- Iceberg connector configured via `trino/catalog/lake.properties`
- Java heap: 512m-1g (JAVA_TOOL_OPTIONS in docker-compose.yml)

### Hive Metastore

- Custom Dockerfile adds hadoop-aws and aws-java-sdk JARs for S3 support
- PostgreSQL backend (metastore-db service)
- Config: `hive/conf/hive-site.xml`

## CI/CD

GitHub Actions workflow (`.github/workflows/ci.yml`):
- JSON schema validation (`python -m json.tool`)
- Ruff linting

## Path Resolution Pattern

Scripts use this pattern to work from any CWD:

```python
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Then load resources relative to REPO_ROOT
schema_path = REPO_ROOT / "schemas/ifrs_s2_core.schema.json"
```

## Schema & Prompts

- **Schema**: `schemas/ifrs_s2_core.schema.json` — minimal IFRS S2 excerpt (document_meta + kpis object)
- **Prompt template**: `prompts/ifrs_s2_extractor_prompt.md` — simple placeholder-based template
- Task description hardcoded in `llm_extractor.py`: "Extract IFRS S2 KPIs for exposure to physical and transition risks"

## Troubleshooting

### Trino connection fails
1. Check services: `docker-compose ps` (all should be "Up (healthy)")
2. Wait for Hive Metastore: `wait_ready()` function handles this with 180s timeout
3. Verify sys.path sanitization if seeing import errors with trino module

### LLM extraction errors
- Set `LLM_MOCK=1` to bypass API during development
- Check `OPENAI_API_KEY` is set
- Review timeout setting: `LLM_TIMEOUT` env var (default 120s)
- Failed JSON parsing falls back to regex extraction from markdown blocks

### Docker volume issues
```bash
docker-compose down -v  # removes volumes (data loss!)
docker-compose up -d
python scripts/create_iceberg_tables.py  # recreate schema
```

## Future Architecture Considerations

- The system is designed for future integration with:
  - **COMPASS** (enterprise ESG/TSB reporting)
  - **AQUASENSE** (water demand forecasting)
  - **MONITOR** (smart city climate monitoring)
  - Retrieval/RAG indexing (currently placeholder in `src/retrieval/`)
  - Multi-tenant data isolation
  - Real-time streaming ingestion

See `Purpura_Climate_OS_Estrategia_Consolidada_v1.0.md` for product roadmap context.
