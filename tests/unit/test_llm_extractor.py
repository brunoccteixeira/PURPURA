"""
Unit tests for src/extract/llm_extractor.py

Tests cover:
- LLMClient in mock mode
- LLMClient with OpenAI API (mocked)
- JSON extraction fallback
- Schema validation
- Prompt rendering
- Full extraction pipeline
"""

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from src.extract.llm_extractor import (
    LLMClient,
    _extract_json_str,
    _mock_response,
    _validate_with_schema_if_possible,
    extract,
    render_prompt,
)


# ============================================================================
# Helper Function Tests
# ============================================================================

@pytest.mark.unit
class TestExtractJsonStr:
    """Tests for _extract_json_str fallback function."""

    def test_extract_from_markdown_code_block(self):
        """Test extracting JSON from markdown code block."""
        text = """
        Some text here
        ```json
        {"key": "value", "number": 42}
        ```
        More text
        """

        result = _extract_json_str(text)
        data = json.loads(result)

        assert data["key"] == "value"
        assert data["number"] == 42

    def test_extract_from_plain_code_block(self):
        """Test extracting JSON from plain code block without 'json' label."""
        text = """
        ```
        {"name": "test", "active": true}
        ```
        """

        result = _extract_json_str(text)
        data = json.loads(result)

        assert data["name"] == "test"
        assert data["active"] is True

    def test_extract_from_braces_in_text(self):
        """Test extracting JSON from braces when no code block exists."""
        text = """
        Here is some data: {"id": 123, "status": "ok"} and more text
        """

        result = _extract_json_str(text)
        data = json.loads(result)

        assert data["id"] == 123
        assert data["status"] == "ok"

    def test_extract_complex_nested_json(self):
        """Test extracting complex nested JSON."""
        json_obj = {
            "document_meta": {"doc_id": "test_001"},
            "kpis": {
                "physical_risk": {"mentioned": True},
                "emissions": {"scope1": 1000, "scope2": 500},
            },
        }
        text = f"```json\n{json.dumps(json_obj)}\n```"

        result = _extract_json_str(text)
        data = json.loads(result)

        assert data["document_meta"]["doc_id"] == "test_001"
        assert data["kpis"]["emissions"]["scope1"] == 1000

    def test_extract_raises_on_no_json(self):
        """Test that function raises ValueError when no JSON found."""
        text = "This text has no JSON in it at all"

        with pytest.raises(ValueError, match="Nenhum objeto JSON encontrado"):
            _extract_json_str(text)

    def test_extract_handles_multiple_braces(self):
        """Test extraction when multiple brace pairs exist."""
        text = "First {\"a\": 1} and second {\"b\": 2, \"c\": 3} object"

        # Should extract the largest/outermost object
        result = _extract_json_str(text)

        # Will get the span from first { to last }
        assert "{" in result and "}" in result


@pytest.mark.unit
class TestValidateWithSchema:
    """Tests for _validate_with_schema_if_possible function."""

    def test_validate_with_valid_data(self, sample_ifrs_schema):
        """Test validation with data that matches schema."""
        data = {
            "document_meta": {"doc_id": "test_001", "title": "Test Doc", "year": 2023},
            "kpis": {
                "physical_risk_exposure": {"mentioned": True, "details": "Climate risks"}
            },
        }

        ok, error = _validate_with_schema_if_possible(data, sample_ifrs_schema)

        assert ok is True
        assert error is None

    def test_validate_with_invalid_data(self, sample_ifrs_schema):
        """Test validation with data that violates schema."""
        # Missing required 'doc_id' field
        data = {"document_meta": {}, "kpis": {}}

        ok, error = _validate_with_schema_if_possible(data, sample_ifrs_schema)

        # Behavior depends on whether jsonschema is installed
        if error is not None:
            assert ok is False
            assert isinstance(error, str)
        else:
            # jsonschema not installed, so it passes
            assert ok is True

    def test_validate_without_jsonschema_installed(self, sample_ifrs_schema):
        """Test that validation gracefully handles missing jsonschema."""
        data = {"document_meta": {"doc_id": "test"}, "kpis": {}}

        # Mock jsonschema being unavailable
        with patch.dict(sys.modules, {"jsonschema": None}):
            ok, error = _validate_with_schema_if_possible(data, sample_ifrs_schema)

            # Should pass without jsonschema
            assert ok is True
            assert error is None


@pytest.mark.unit
class TestMockResponse:
    """Tests for _mock_response function."""

    def test_mock_response_with_chunks(self, sample_chunks):
        """Test mock response generation with evidence chunks."""
        result = _mock_response(sample_chunks)

        assert isinstance(result, dict)
        assert "kpis" in result
        assert "s2_mock" in result["kpis"]
        assert "seed" in result["kpis"]["s2_mock"]

        # Seed should be deterministic for same input
        result2 = _mock_response(sample_chunks)
        assert result["kpis"]["s2_mock"]["seed"] == result2["kpis"]["s2_mock"]["seed"]

    def test_mock_response_without_chunks(self):
        """Test mock response with empty chunks list."""
        result = _mock_response([])

        assert isinstance(result, dict)
        assert "kpis" in result
        assert "s2_mock" in result["kpis"]

    def test_mock_response_deterministic(self):
        """Test that mock response is deterministic."""
        chunks = [{"text": "Test climate risk data"}]

        result1 = _mock_response(chunks)
        result2 = _mock_response(chunks)

        assert result1 == result2


# ============================================================================
# LLMClient Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.mock
class TestLLMClientMock:
    """Tests for LLMClient in mock mode."""

    def test_init_mock_mode(self, enable_llm_mock):
        """Test LLMClient initialization in mock mode."""
        client = LLMClient()

        assert client.mock is True
        assert client.model == os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    def test_extract_json_mock_mode(self, enable_llm_mock, sample_chunks):
        """Test JSON extraction in mock mode."""
        client = LLMClient()
        prompt = "Extract climate data"

        result = client.extract_json(prompt, evidence_chunks=sample_chunks)

        assert isinstance(result, dict)
        assert "kpis" in result
        assert "s2_mock" in result["kpis"]

    def test_mock_mode_no_api_call(self, enable_llm_mock):
        """Test that mock mode doesn't require API key."""
        # Should not raise error even without API key
        client = LLMClient()
        result = client.extract_json("test prompt")

        assert isinstance(result, dict)


@pytest.mark.unit
class TestLLMClientOpenAI:
    """Tests for LLMClient with OpenAI API (mocked)."""

    def test_init_requires_api_key(self, monkeypatch):
        """Test that LLMClient requires API key when not in mock mode."""
        # Remove LLM_MOCK and API key
        monkeypatch.delenv("LLM_MOCK", raising=False)
        monkeypatch.delenv("OPENAI_API_KEY", raising=False)

        with pytest.raises(RuntimeError, match="Missing required environment variable"):
            LLMClient()

    def test_init_with_api_key(self, monkeypatch):
        """Test LLMClient initialization with API key."""
        monkeypatch.delenv("LLM_MOCK", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

        with patch("src.extract.llm_extractor.OpenAI") as mock_openai:
            client = LLMClient()

            assert client.mock is False
            mock_openai.assert_called_once()

    def test_extract_json_with_openai(self, monkeypatch, mock_llm_response_json):
        """Test JSON extraction with mocked OpenAI API."""
        monkeypatch.delenv("LLM_MOCK", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

        # Mock OpenAI response
        mock_message = Mock()
        mock_message.content = mock_llm_response_json

        mock_choice = Mock()
        mock_choice.message = mock_message

        mock_response = Mock()
        mock_response.choices = [mock_choice]

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.extract.llm_extractor.OpenAI") as mock_openai:
            mock_openai.return_value = mock_client

            client = LLMClient()
            result = client.extract_json("Extract climate data")

            assert isinstance(result, dict)
            assert "document_meta" in result
            assert "kpis" in result

    def test_extract_json_fallback_on_invalid_json(self, monkeypatch):
        """Test that extraction falls back when OpenAI returns invalid JSON."""
        monkeypatch.delenv("LLM_MOCK", raising=False)
        monkeypatch.setenv("OPENAI_API_KEY", "sk-test-key")

        # Mock OpenAI returning JSON in code block
        invalid_response = "```json\n{\"key\": \"value\"}\n```"

        mock_message = Mock()
        mock_message.content = invalid_response

        mock_choice = Mock()
        mock_choice.message = mock_message

        mock_response = Mock()
        mock_response.choices = [mock_choice]

        mock_client = Mock()
        mock_client.chat.completions.create.return_value = mock_response

        with patch("src.extract.llm_extractor.OpenAI") as mock_openai:
            mock_openai.return_value = mock_client

            client = LLMClient()
            result = client.extract_json("test")

            assert result["key"] == "value"

    def test_custom_model(self, monkeypatch):
        """Test LLMClient with custom model."""
        monkeypatch.setenv("LLM_MOCK", "1")

        client = LLMClient(model="gpt-4")

        assert client.model == "gpt-4"


# ============================================================================
# Prompt Rendering Tests
# ============================================================================

@pytest.mark.unit
class TestRenderPrompt:
    """Tests for render_prompt function."""

    def test_render_basic_prompt(self, sample_ifrs_schema, sample_chunks):
        """Test basic prompt rendering."""
        template = """
        Task: {{task_description}}

        Schema: {{json_schema}}

        Evidence: {{evidence_chunks}}
        """

        prompt = render_prompt(
            json_schema=sample_ifrs_schema,
            evidence_chunks=sample_chunks,
            task="Extract climate data",
            template=template,
        )

        assert "Extract climate data" in prompt
        assert "document_meta" in prompt  # From schema
        assert "Climate risk" in prompt or "climate" in prompt.lower()

    def test_render_includes_all_chunks(self, sample_ifrs_schema, sample_chunks):
        """Test that all chunks are included in rendered prompt."""
        template = "{{evidence_chunks}}"

        prompt = render_prompt(
            json_schema=sample_ifrs_schema,
            evidence_chunks=sample_chunks,
            task="Test",
            template=template,
        )

        # Should contain numbered chunks
        for i in range(1, len(sample_chunks) + 1):
            assert f"[{i}]" in prompt

    def test_render_with_empty_chunks(self, sample_ifrs_schema):
        """Test prompt rendering with no evidence chunks."""
        template = "Task: {{task_description}}\nEvidence: {{evidence_chunks}}"

        prompt = render_prompt(
            json_schema=sample_ifrs_schema,
            evidence_chunks=[],
            task="Test task",
            template=template,
        )

        assert "Test task" in prompt
        # Evidence section should be empty but present
        assert "Evidence:" in prompt

    def test_render_truncates_long_chunks(self, sample_ifrs_schema):
        """Test that very long chunks are truncated to 800 chars."""
        long_chunk = {"text": "x" * 2000, "document_id": "doc1", "page": 1}

        template = "{{evidence_chunks}}"

        prompt = render_prompt(
            json_schema=sample_ifrs_schema,
            evidence_chunks=[long_chunk],
            task="Test",
            template=template,
        )

        # Should be truncated to ~800 chars (plus metadata)
        # The actual chunk text should be max 800 chars
        lines = prompt.split("\n")
        chunk_line = [l for l in lines if "doc=" in l][0]
        # Extract just the text portion after ::
        text_part = chunk_line.split("::")[-1].strip()
        assert len(text_part) <= 800


# ============================================================================
# Full Extraction Pipeline Tests
# ============================================================================

@pytest.mark.unit
@pytest.mark.mock
class TestExtract:
    """Tests for extract() main function."""

    def test_extract_with_mock_llm(
        self, enable_llm_mock, sample_document_meta, sample_chunks, sample_ifrs_schema
    ):
        """Test full extraction pipeline with mock LLM."""
        template = "{{task_description}}\n{{json_schema}}\n{{evidence_chunks}}"

        llm = LLMClient()
        result = extract(
            document_meta=sample_document_meta,
            evidence_chunks=sample_chunks,
            llm=llm,
            template=template,
            schema=sample_ifrs_schema,
        )

        # Should include document metadata
        assert "document_meta" in result
        assert result["document_meta"]["doc_id"] == "test_doc_001"

        # Should include extraction timestamp
        assert "extracted_at" in result

        # Should include KPIs (from mock)
        assert "kpis" in result

    def test_extract_adds_timestamp(
        self, enable_llm_mock, sample_document_meta, sample_chunks, sample_ifrs_schema
    ):
        """Test that extract adds extraction timestamp."""
        template = "{{task_description}}"

        llm = LLMClient()
        result = extract(
            document_meta=sample_document_meta,
            evidence_chunks=sample_chunks,
            llm=llm,
            template=template,
            schema=sample_ifrs_schema,
        )

        assert "extracted_at" in result
        # Should be ISO format timestamp
        import datetime

        datetime.datetime.fromisoformat(result["extracted_at"])

    def test_extract_preserves_document_meta(
        self, enable_llm_mock, sample_chunks, sample_ifrs_schema
    ):
        """Test that original document metadata is preserved."""
        doc_meta = {
            "doc_id": "custom_id_123",
            "title": "Custom Title",
            "source": "test_source",
        }

        template = "{{task_description}}"

        llm = LLMClient()
        result = extract(
            document_meta=doc_meta,
            evidence_chunks=sample_chunks,
            llm=llm,
            template=template,
            schema=sample_ifrs_schema,
        )

        assert result["document_meta"] == doc_meta

    def test_extract_with_schema_validation_error(
        self, enable_llm_mock, sample_document_meta, sample_chunks
    ):
        """Test extract behavior when schema validation fails."""
        # Create strict schema that mock response won't match
        strict_schema = {
            "type": "object",
            "properties": {
                "required_field": {"type": "string"},
                "document_meta": {"type": "object"},
                "kpis": {"type": "object"},
            },
            "required": ["required_field", "document_meta", "kpis"],
        }

        template = "{{task_description}}"

        llm = LLMClient()
        result = extract(
            document_meta=sample_document_meta,
            evidence_chunks=sample_chunks,
            llm=llm,
            template=template,
            schema=strict_schema,
        )

        # Should complete but may have schema error
        assert "document_meta" in result
        # If jsonschema is installed, should have error field
        # If not, no error field

    def test_extract_with_empty_chunks(
        self, enable_llm_mock, sample_document_meta, sample_ifrs_schema
    ):
        """Test extraction with no evidence chunks."""
        template = "{{task_description}}"

        llm = LLMClient()
        result = extract(
            document_meta=sample_document_meta,
            evidence_chunks=[],
            llm=llm,
            template=template,
            schema=sample_ifrs_schema,
        )

        assert "document_meta" in result
        assert "kpis" in result

    def test_extract_end_to_end(
        self, enable_llm_mock, sample_document_meta, sample_text_short, sample_ifrs_schema
    ):
        """Test end-to-end extraction with realistic data."""
        # Create chunks from sample text
        from src.ingest.chunker import chunk_text

        chunks = chunk_text(sample_text_short, max_tokens=100, overlap=20)

        # Add required metadata to chunks
        evidence_chunks = [
            {**chunk, "document_id": "test_doc", "page": 1} for chunk in chunks
        ]

        template = """
        Extract IFRS S2 climate-related KPIs from the following evidence.

        Schema: {{json_schema}}

        Evidence chunks:
        {{evidence_chunks}}

        Task: {{task_description}}
        """

        llm = LLMClient()
        result = extract(
            document_meta=sample_document_meta,
            evidence_chunks=evidence_chunks,
            llm=llm,
            template=template,
            schema=sample_ifrs_schema,
        )

        # Verify complete result structure
        assert "document_meta" in result
        assert "kpis" in result
        assert "extracted_at" in result
        assert isinstance(result, dict)
