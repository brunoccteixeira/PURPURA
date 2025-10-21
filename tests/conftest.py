"""
Shared pytest fixtures for PURPURA tests.

This module provides reusable fixtures for:
- Sample data (PDFs, schemas, text chunks)
- Mock responses (LLM, Trino)
- Test clients (FastAPI, Trino)
- Environment setup
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, List
from unittest.mock import MagicMock, Mock

import pytest

# Add project root to sys.path for imports
REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ============================================================================
# Path Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def repo_root() -> Path:
    """Absolute path to repository root."""
    return REPO_ROOT


@pytest.fixture(scope="session")
def tests_dir(repo_root: Path) -> Path:
    """Absolute path to tests directory."""
    return repo_root / "tests"


@pytest.fixture(scope="session")
def fixtures_dir(tests_dir: Path) -> Path:
    """Absolute path to test fixtures directory."""
    return tests_dir / "fixtures"


# ============================================================================
# Schema Fixtures
# ============================================================================

@pytest.fixture
def sample_ifrs_schema() -> Dict:
    """Minimal IFRS S2 JSON schema for testing."""
    return {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "object",
        "properties": {
            "document_meta": {
                "type": "object",
                "properties": {
                    "doc_id": {"type": "string"},
                    "title": {"type": "string"},
                    "year": {"type": "integer"}
                },
                "required": ["doc_id"]
            },
            "kpis": {
                "type": "object",
                "properties": {
                    "physical_risk_exposure": {
                        "type": "object",
                        "properties": {
                            "mentioned": {"type": "boolean"},
                            "details": {"type": "string"}
                        }
                    },
                    "transition_risk_exposure": {
                        "type": "object",
                        "properties": {
                            "mentioned": {"type": "boolean"},
                            "details": {"type": "string"}
                        }
                    },
                    "ghg_emissions": {
                        "type": "object",
                        "properties": {
                            "scope1": {"type": "number"},
                            "scope2": {"type": "number"},
                            "scope3": {"type": "number"},
                            "unit": {"type": "string"}
                        }
                    }
                }
            }
        },
        "required": ["document_meta", "kpis"]
    }


@pytest.fixture
def sample_schema_path(fixtures_dir: Path, sample_ifrs_schema: Dict) -> Path:
    """Path to a sample schema file (creates if doesn't exist)."""
    schema_path = fixtures_dir / "sample_schemas" / "test_ifrs_s2.schema.json"
    schema_path.parent.mkdir(parents=True, exist_ok=True)

    if not schema_path.exists():
        with open(schema_path, "w") as f:
            json.dump(sample_ifrs_schema, f, indent=2)

    return schema_path


# ============================================================================
# Text and Chunk Fixtures
# ============================================================================

@pytest.fixture
def sample_text_short() -> str:
    """Short sample text for testing (< 100 tokens)."""
    return """
    IFRS S2 Climate-Related Disclosures

    Our organization has identified significant physical risks related to climate change,
    including increased frequency of extreme weather events and rising sea levels.

    We have set a target to reduce GHG emissions by 50% by 2030 from a 2020 baseline.
    """


@pytest.fixture
def sample_text_long() -> str:
    """Longer sample text for chunking tests (~500 tokens)."""
    return """
    Climate-Related Financial Disclosures - Annual Report 2023

    Executive Summary

    This report provides comprehensive information about our climate-related risks and opportunities
    in accordance with IFRS S2 standards. Our analysis covers both physical and transition risks
    that could materially impact our financial position over the short, medium, and long term.

    Physical Risk Assessment

    We have identified the following physical climate risks:
    - Acute risks: Increased frequency and severity of extreme weather events including hurricanes,
      floods, and wildfires that could disrupt operations at our coastal facilities.
    - Chronic risks: Rising sea levels threatening our manufacturing plants in low-lying areas,
      and prolonged droughts affecting water availability for our production processes.

    Our scenario analysis indicates that under a high-warming scenario (RCP 8.5), potential
    financial impacts could reach $500 million by 2050, primarily from asset damage and
    operational disruptions.

    Transition Risk Assessment

    Key transition risks include:
    - Policy and legal: Implementation of carbon pricing mechanisms could increase operational
      costs by an estimated $50 million annually by 2030.
    - Technology: Shift to low-carbon technologies requires capital investments of approximately
      $200 million over the next five years.
    - Market: Changing consumer preferences toward sustainable products necessitates product
      portfolio transformation.
    - Reputation: Failure to meet climate commitments could result in stakeholder backlash and
      reduced market valuation.

    Greenhouse Gas Emissions

    Our 2023 emissions inventory:
    - Scope 1 (direct emissions): 125,000 tCO2e
    - Scope 2 (indirect emissions from energy): 78,000 tCO2e
    - Scope 3 (value chain emissions): 450,000 tCO2e

    We have committed to achieve net-zero emissions by 2050, with intermediate targets of:
    - 30% reduction by 2025 (from 2020 baseline)
    - 50% reduction by 2030
    - 75% reduction by 2040

    Climate Opportunities

    We have identified several climate-related opportunities:
    - Resource efficiency: Energy efficiency programs expected to save $30 million annually
    - Products and services: Growing market for sustainable product lines
    - Resilience: Investments in climate adaptation increasing operational resilience
    """


@pytest.fixture
def sample_chunks() -> List[Dict]:
    """Sample text chunks with metadata."""
    return [
        {
            "text": "Climate risk assessment shows physical risks from extreme weather.",
            "token_len": 12,
            "chunk_id": 0
        },
        {
            "text": "Transition risks include carbon pricing and technology shifts.",
            "token_len": 10,
            "chunk_id": 1
        },
        {
            "text": "GHG emissions: Scope 1 is 125,000 tCO2e, Scope 2 is 78,000 tCO2e.",
            "token_len": 20,
            "chunk_id": 2
        }
    ]


# ============================================================================
# Mock LLM Response Fixtures
# ============================================================================

@pytest.fixture
def mock_llm_response() -> Dict:
    """Mock LLM extraction response in expected format."""
    return {
        "document_meta": {
            "doc_id": "test_doc_001",
            "title": "Climate Risk Report 2023",
            "year": 2023
        },
        "kpis": {
            "physical_risk_exposure": {
                "mentioned": True,
                "details": "Extreme weather events and sea level rise"
            },
            "transition_risk_exposure": {
                "mentioned": True,
                "details": "Carbon pricing and technology transition"
            },
            "ghg_emissions": {
                "scope1": 125000.0,
                "scope2": 78000.0,
                "scope3": 450000.0,
                "unit": "tCO2e"
            }
        }
    }


@pytest.fixture
def mock_llm_response_json(mock_llm_response: Dict) -> str:
    """Mock LLM response as JSON string."""
    return json.dumps(mock_llm_response, indent=2)


# ============================================================================
# Environment Fixtures
# ============================================================================

@pytest.fixture
def mock_env_vars(monkeypatch):
    """Set up mock environment variables for testing."""
    env_vars = {
        "LLM_MOCK": "1",
        "OPENAI_API_KEY": "sk-test-mock-key",
        "OPENAI_MODEL": "gpt-4o-mini",
        "TRINO_HOST": "localhost",
        "TRINO_PORT": "8080",
        "TRINO_USER": "test_user",
        "TRINO_CATALOG": "lake",
        "TRINO_SCHEMA": "ifrs"
    }

    for key, value in env_vars.items():
        monkeypatch.setenv(key, value)

    return env_vars


@pytest.fixture
def enable_llm_mock(monkeypatch):
    """Force LLM mock mode for tests."""
    monkeypatch.setenv("LLM_MOCK", "1")


# ============================================================================
# Mock Client Fixtures
# ============================================================================

@pytest.fixture
def mock_trino_connection():
    """Mock Trino connection for testing."""
    mock_conn = MagicMock()
    mock_cursor = MagicMock()

    # Configure cursor behavior
    mock_cursor.execute.return_value = None
    mock_cursor.fetchall.return_value = []
    mock_cursor.fetchone.return_value = None

    mock_conn.cursor.return_value = mock_cursor
    return mock_conn


@pytest.fixture
def mock_openai_client():
    """Mock OpenAI client for testing."""
    mock_client = MagicMock()
    mock_response = MagicMock()

    # Configure response structure
    mock_message = MagicMock()
    mock_message.content = json.dumps({
        "document_meta": {"doc_id": "mock_001"},
        "kpis": {"physical_risk_exposure": {"mentioned": True}}
    })

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_response.choices = [mock_choice]
    mock_client.chat.completions.create.return_value = mock_response

    return mock_client


# ============================================================================
# FastAPI Test Client Fixture
# ============================================================================

@pytest.fixture
def api_client():
    """FastAPI test client for integration tests."""
    from fastapi.testclient import TestClient
    from backend.api.main import app

    return TestClient(app)


# ============================================================================
# Sample PDF Fixtures
# ============================================================================

@pytest.fixture
def sample_pdf_path(fixtures_dir: Path) -> Path:
    """
    Path to a minimal sample PDF for testing.

    Note: This fixture returns the expected path. The actual PDF file
    should be created separately using a PDF library or placed manually.
    """
    pdf_path = fixtures_dir / "sample_pdfs" / "test_climate_report.pdf"
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    return pdf_path


# ============================================================================
# Document Metadata Fixtures
# ============================================================================

@pytest.fixture
def sample_document_meta() -> Dict:
    """Sample document metadata."""
    return {
        "doc_id": "test_doc_001",
        "title": "Test Climate Report",
        "year": 2023,
        "source": "test_source",
        "created_at": "2023-01-01T00:00:00Z"
    }


# ============================================================================
# Cleanup Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def cleanup_test_files():
    """Automatically clean up temporary test files after each test."""
    yield
    # Cleanup logic can be added here if needed
    pass
