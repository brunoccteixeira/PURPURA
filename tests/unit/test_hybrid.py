"""
Unit tests for backend/extraction/hybrid.py

Tests cover:
- ConfidenceVoting agreement checking
- ConfidenceVoting KPI merging
- HybridExtractor initialization
- HybridExtractor extraction modes (TRANSFORMER, LLM, HYBRID)
"""

import sys
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch

import pytest

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.extraction.hybrid import (
    ConfidenceVoting,
    ExtractionMethod,
    HybridExtractor,
    extract_hybrid,
)


# ============================================================================
# ConfidenceVoting Agreement Tests
# ============================================================================

@pytest.mark.unit
class TestConfidenceVotingAgreement:
    """Tests for ConfidenceVoting._check_agreement method."""

    def test_exact_match_integers(self):
        """Test exact match for integers."""
        assert ConfidenceVoting._check_agreement(42, 42) is True
        assert ConfidenceVoting._check_agreement(0, 0) is True

    def test_exact_match_strings(self):
        """Test exact match for strings."""
        assert ConfidenceVoting._check_agreement("test", "test") is True
        assert ConfidenceVoting._check_agreement("hello", "hello") is True

    def test_case_insensitive_string_match(self):
        """Test case-insensitive string comparison."""
        assert ConfidenceVoting._check_agreement("Test", "test") is True
        assert ConfidenceVoting._check_agreement("HELLO", "hello") is True
        assert ConfidenceVoting._check_agreement("MixedCase", "mixedcase") is True

    def test_whitespace_trimming_strings(self):
        """Test that strings are trimmed before comparison."""
        assert ConfidenceVoting._check_agreement("  test  ", "test") is True
        assert ConfidenceVoting._check_agreement("hello ", " hello") is True

    def test_numerical_tolerance_within_10_percent(self):
        """Test numerical agreement within 10% tolerance."""
        # 100 and 105 differ by 5%, should agree
        assert ConfidenceVoting._check_agreement(100, 105) is True
        assert ConfidenceVoting._check_agreement(100, 109) is True  # 9% difference

    def test_numerical_tolerance_exceeds_10_percent(self):
        """Test numerical disagreement exceeding 10% tolerance."""
        # 100 and 115 differ by 15%, should disagree
        assert ConfidenceVoting._check_agreement(100, 115) is False
        assert ConfidenceVoting._check_agreement(100, 90) is False  # 10% difference (boundary)

    def test_numerical_tolerance_with_floats(self):
        """Test numerical tolerance with float values."""
        assert ConfidenceVoting._check_agreement(100.0, 105.5) is True
        assert ConfidenceVoting._check_agreement(1.0, 1.05) is True
        assert ConfidenceVoting._check_agreement(0.5, 0.55) is False  # 10% of max

    def test_numerical_tolerance_with_zero(self):
        """Test numerical comparison when one value is zero."""
        # Special case: absolute difference < tolerance
        assert ConfidenceVoting._check_agreement(0, 0.05) is True
        assert ConfidenceVoting._check_agreement(0, 0.15) is False

    def test_custom_tolerance(self):
        """Test agreement with custom tolerance."""
        # 20% tolerance
        assert ConfidenceVoting._check_agreement(100, 115, tolerance=0.2) is True
        assert ConfidenceVoting._check_agreement(100, 125, tolerance=0.2) is False

    def test_different_types_disagree(self):
        """Test that different types disagree."""
        assert ConfidenceVoting._check_agreement(100, "100") is False
        assert ConfidenceVoting._check_agreement("42", 42) is False
        assert ConfidenceVoting._check_agreement(True, "True") is False

    def test_none_values(self):
        """Test agreement with None values."""
        assert ConfidenceVoting._check_agreement(None, None) is True
        assert ConfidenceVoting._check_agreement(None, 100) is False
        assert ConfidenceVoting._check_agreement("test", None) is False

    def test_boolean_values(self):
        """Test agreement with boolean values."""
        assert ConfidenceVoting._check_agreement(True, True) is True
        assert ConfidenceVoting._check_agreement(False, False) is True
        assert ConfidenceVoting._check_agreement(True, False) is False


# ============================================================================
# ConfidenceVoting Merge KPIs Tests
# ============================================================================

@pytest.mark.unit
class TestConfidenceVotingMerge:
    """Tests for ConfidenceVoting.merge_kpis method."""

    def test_merge_both_none(self):
        """Test merging when both methods return None."""
        transformer_kpis = {
            "scope1": {"value": None, "confidence": 0.0}
        }
        llm_kpis = {
            "scope1": {"value": None, "confidence": 0.0}
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        assert result["scope1"]["value"] is None
        assert result["scope1"]["confidence"] == 0.0
        assert result["scope1"]["agreement"] is False
        assert result["scope1"]["sources"] == []

    def test_merge_only_transformer_has_value(self):
        """Test merging when only transformer found value."""
        transformer_kpis = {
            "scope1": {"value": 1000, "confidence": 0.9}
        }
        llm_kpis = {
            "scope1": {"value": None, "confidence": 0.0}
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        assert result["scope1"]["value"] == 1000
        assert result["scope1"]["confidence"] == 0.9 * 0.8  # Penalized
        assert result["scope1"]["method"] == "transformer"
        assert result["scope1"]["agreement"] is False
        assert result["scope1"]["sources"] == ["transformer"]

    def test_merge_only_llm_has_value(self):
        """Test merging when only LLM found value."""
        transformer_kpis = {
            "scope1": {"value": None, "confidence": 0.0}
        }
        llm_kpis = {
            "scope1": {"value": 2000, "confidence": 0.85}
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        assert result["scope1"]["value"] == 2000
        assert result["scope1"]["confidence"] == 0.85 * 0.8  # Penalized
        assert result["scope1"]["method"] == "llm"
        assert result["scope1"]["agreement"] is False
        assert result["scope1"]["sources"] == ["llm"]

    def test_merge_both_agree_boosts_confidence(self):
        """Test that agreement boosts confidence."""
        transformer_kpis = {
            "scope1": {"value": 1000, "confidence": 0.8}
        }
        llm_kpis = {
            "scope1": {"value": 1000, "confidence": 0.7}
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        # Average is 0.75, boosted by 1.2 = 0.9
        expected_conf = min((0.8 + 0.7) / 2 * 1.2, 1.0)

        assert result["scope1"]["value"] == 1000
        assert result["scope1"]["confidence"] == expected_conf
        assert result["scope1"]["method"] == "hybrid"
        assert result["scope1"]["agreement"] is True
        assert set(result["scope1"]["sources"]) == {"transformer", "llm"}

    def test_merge_both_agree_caps_confidence_at_1(self):
        """Test that confidence is capped at 1.0."""
        transformer_kpis = {
            "scope1": {"value": 1000, "confidence": 0.95}
        }
        llm_kpis = {
            "scope1": {"value": 1000, "confidence": 0.95}
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        # Would be 0.95 * 1.2 = 1.14, but capped at 1.0
        assert result["scope1"]["confidence"] == 1.0

    def test_merge_both_disagree_uses_higher_confidence_transformer(self):
        """Test that higher confidence wins when disagreeing (transformer)."""
        transformer_kpis = {
            "scope1": {"value": 1000, "confidence": 0.9}
        }
        llm_kpis = {
            "scope1": {"value": 2000, "confidence": 0.7}
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        assert result["scope1"]["value"] == 1000
        assert result["scope1"]["confidence"] == 0.9
        assert result["scope1"]["method"] == "transformer"
        assert result["scope1"]["agreement"] is False
        assert "conflict" in result["scope1"]
        assert result["scope1"]["conflict"]["llm_value"] == 2000

    def test_merge_both_disagree_uses_higher_confidence_llm(self):
        """Test that higher confidence wins when disagreeing (LLM)."""
        transformer_kpis = {
            "scope1": {"value": 1000, "confidence": 0.6}
        }
        llm_kpis = {
            "scope1": {"value": 2000, "confidence": 0.9}
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        assert result["scope1"]["value"] == 2000
        assert result["scope1"]["confidence"] == 0.9
        assert result["scope1"]["method"] == "llm"
        assert result["scope1"]["agreement"] is False
        assert "conflict" in result["scope1"]
        assert result["scope1"]["conflict"]["transformer_value"] == 1000

    def test_merge_multiple_kpis(self):
        """Test merging multiple KPIs with different scenarios."""
        transformer_kpis = {
            "scope1": {"value": 1000, "confidence": 0.9},
            "scope2": {"value": None, "confidence": 0.0},
            "scope3": {"value": 3000, "confidence": 0.8}
        }
        llm_kpis = {
            "scope1": {"value": 1000, "confidence": 0.85},  # Agree
            "scope2": {"value": 2000, "confidence": 0.7},   # Only LLM
            "scope3": {"value": 4000, "confidence": 0.6}    # Disagree
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        # Scope1: Agreement
        assert result["scope1"]["agreement"] is True
        assert result["scope1"]["method"] == "hybrid"

        # Scope2: Only LLM
        assert result["scope2"]["value"] == 2000
        assert result["scope2"]["method"] == "llm"

        # Scope3: Disagree, transformer wins
        assert result["scope3"]["value"] == 3000
        assert result["scope3"]["method"] == "transformer"

    def test_merge_keys_only_in_transformer(self):
        """Test merging when KPI only exists in transformer results."""
        transformer_kpis = {
            "unique_transformer_kpi": {"value": 500, "confidence": 0.8}
        }
        llm_kpis = {}

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        assert result["unique_transformer_kpi"]["value"] == 500
        assert result["unique_transformer_kpi"]["confidence"] == 0.8 * 0.8

    def test_merge_keys_only_in_llm(self):
        """Test merging when KPI only exists in LLM results."""
        transformer_kpis = {}
        llm_kpis = {
            "unique_llm_kpi": {"value": "climate risk", "confidence": 0.75}
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        assert result["unique_llm_kpi"]["value"] == "climate risk"
        assert result["unique_llm_kpi"]["confidence"] == 0.75 * 0.8

    def test_merge_preserves_both_values_on_agreement(self):
        """Test that both values are preserved when they agree."""
        transformer_kpis = {
            "target_year": {"value": 2030, "confidence": 0.9}
        }
        llm_kpis = {
            "target_year": {"value": 2030, "confidence": 0.85}
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        assert "transformer_value" in result["target_year"]
        assert "llm_value" in result["target_year"]
        assert result["target_year"]["transformer_value"] == 2030
        assert result["target_year"]["llm_value"] == 2030

    def test_merge_empty_dicts(self):
        """Test merging empty KPI dictionaries."""
        result = ConfidenceVoting.merge_kpis({}, {})
        assert result == {}

    def test_merge_llm_result_not_dict(self):
        """Test merging when LLM result is not a dict (edge case)."""
        transformer_kpis = {
            "scope1": {"value": 1000, "confidence": 0.9}
        }
        llm_kpis = {
            "scope1": "invalid_format"  # Not a dict
        }

        result = ConfidenceVoting.merge_kpis(transformer_kpis, llm_kpis)

        # Should handle gracefully
        assert "scope1" in result


# ============================================================================
# HybridExtractor Tests
# ============================================================================

@pytest.mark.unit
class TestHybridExtractor:
    """Tests for HybridExtractor class."""

    def test_init_default(self):
        """Test HybridExtractor initialization with defaults."""
        with patch("backend.extraction.hybrid.OSCTransformerExtractor"):
            with patch("backend.extraction.hybrid.LLMClient"):
                extractor = HybridExtractor()

                assert extractor.use_transformer is True
                assert extractor.use_llm is True

    def test_init_transformer_only(self):
        """Test initialization with transformer only."""
        with patch("backend.extraction.hybrid.OSCTransformerExtractor"):
            extractor = HybridExtractor(use_transformer=True, use_llm=False)

            assert extractor.use_transformer is True
            assert extractor.use_llm is False
            assert hasattr(extractor, "transformer_extractor")

    def test_init_llm_only(self):
        """Test initialization with LLM only."""
        with patch("backend.extraction.hybrid.LLMClient") as mock_llm:
            extractor = HybridExtractor(use_transformer=False, use_llm=True)

            assert extractor.use_transformer is False
            assert extractor.use_llm is True
            assert hasattr(extractor, "llm_client")

    def test_init_custom_llm_client(self):
        """Test initialization with custom LLM client."""
        custom_client = Mock()

        with patch("backend.extraction.hybrid.OSCTransformerExtractor"):
            extractor = HybridExtractor(llm_client=custom_client)

            assert extractor.llm_client is custom_client

    @patch("backend.extraction.hybrid.OSCTransformerExtractor")
    @patch("backend.extraction.hybrid.LLMClient")
    def test_extract_transformer_mode(self, mock_llm_cls, mock_transformer_cls):
        """Test extraction in TRANSFORMER mode."""
        # Setup mocks
        mock_transformer = Mock()
        mock_transformer.extract_from_pdf.return_value = {
            "kpis": {"scope1": {"value": 1000, "confidence": 0.9}}
        }
        mock_transformer_cls.return_value = mock_transformer

        extractor = HybridExtractor()
        result = extractor.extract(
            pdf_path="/path/to/test.pdf",
            method=ExtractionMethod.TRANSFORMER,
            document_meta={"doc_id": "test_001"}
        )

        # Should call transformer
        mock_transformer.extract_from_pdf.assert_called_once()

        # Should return transformer results
        assert "kpis" in result
        assert result["document_meta"]["doc_id"] == "test_001"

    @patch("backend.extraction.hybrid.OSCTransformerExtractor")
    @patch("backend.extraction.hybrid.LLMClient")
    @patch("backend.extraction.hybrid.llm_extract")
    def test_extract_llm_mode(self, mock_llm_extract, mock_llm_cls, mock_transformer_cls):
        """Test extraction in LLM mode."""
        # Setup mocks
        mock_llm_extract.return_value = {
            "kpis": {"scope1": {"value": 2000, "confidence": 0.85}},
            "document_meta": {"doc_id": "test_001"},
            "extracted_at": "2023-01-01T00:00:00"
        }

        extractor = HybridExtractor()
        result = extractor.extract(
            document_meta={"doc_id": "test_001"},
            evidence_chunks=[{"text": "test", "page": 1}],
            template="{{task_description}}",
            schema={"type": "object"},
            method=ExtractionMethod.LLM
        )

        # Should call LLM extract
        mock_llm_extract.assert_called_once()

        # Should return LLM results
        assert "kpis" in result

    @patch("backend.extraction.hybrid.OSCTransformerExtractor")
    @patch("backend.extraction.hybrid.LLMClient")
    @patch("backend.extraction.hybrid.llm_extract")
    def test_extract_hybrid_mode(self, mock_llm_extract, mock_llm_cls, mock_transformer_cls):
        """Test extraction in HYBRID mode with both methods."""
        # Setup transformer mock
        mock_transformer = Mock()
        mock_transformer.extract_from_pdf.return_value = {
            "kpis": {
                "scope1": {"value": 1000, "confidence": 0.9},
                "scope2": {"value": 500, "confidence": 0.8}
            }
        }
        mock_transformer_cls.return_value = mock_transformer

        # Setup LLM mock
        mock_llm_extract.return_value = {
            "kpis": {
                "scope1": {"value": 1000, "confidence": 0.85},  # Agrees
                "scope3": {"value": 300, "confidence": 0.7}     # Unique to LLM
            },
            "extracted_at": "2023-01-01T00:00:00"
        }

        extractor = HybridExtractor()
        result = extractor.extract(
            pdf_path="/path/to/test.pdf",
            document_meta={"doc_id": "test_001"},
            evidence_chunks=[{"text": "test", "page": 1}],
            template="{{task_description}}",
            schema={"type": "object"},
            method=ExtractionMethod.HYBRID
        )

        # Should call both methods
        mock_transformer.extract_from_pdf.assert_called_once()
        mock_llm_extract.assert_called_once()

        # Should return hybrid results
        assert result["method"] == "hybrid"
        assert "kpis" in result
        assert "transformer_results" in result
        assert "llm_results" in result

        # Check merged KPIs
        assert "scope1" in result["kpis"]  # From both
        assert "scope2" in result["kpis"]  # From transformer
        assert "scope3" in result["kpis"]  # From LLM

    @patch("backend.extraction.hybrid.OSCTransformerExtractor")
    @patch("backend.extraction.hybrid.LLMClient")
    def test_extract_no_results(self, mock_llm_cls, mock_transformer_cls):
        """Test extraction when no results are available."""
        extractor = HybridExtractor()
        result = extractor.extract(
            document_meta={"doc_id": "test_001"},
            method=ExtractionMethod.HYBRID
        )

        # Should return fallback structure
        assert "error" in result
        assert result["kpis"] == {}
        assert result["document_meta"]["doc_id"] == "test_001"

    @patch("backend.extraction.hybrid.OSCTransformerExtractor")
    @patch("backend.extraction.hybrid.LLMClient")
    def test_extract_with_text_input(self, mock_llm_cls, mock_transformer_cls):
        """Test extraction with text input instead of PDF."""
        mock_transformer = Mock()
        mock_transformer.extract_from_text.return_value = {
            "kpis": {"scope1": {"value": 1000, "confidence": 0.9}}
        }
        mock_transformer_cls.return_value = mock_transformer

        extractor = HybridExtractor()
        result = extractor.extract(
            text="Climate risk text data",
            method=ExtractionMethod.TRANSFORMER
        )

        # Should call extract_from_text instead of extract_from_pdf
        mock_transformer.extract_from_text.assert_called_once_with(
            "Climate risk text data", None
        )


# ============================================================================
# Convenience Function Tests
# ============================================================================

@pytest.mark.unit
class TestExtractHybrid:
    """Tests for extract_hybrid convenience function."""

    @patch("backend.extraction.hybrid.HybridExtractor")
    def test_extract_hybrid_convenience(self, mock_extractor_cls):
        """Test extract_hybrid convenience function."""
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {
            "kpis": {},
            "method": "hybrid"
        }
        mock_extractor_cls.return_value = mock_extractor

        schema = {"type": "object"}
        result = extract_hybrid("/path/to/test.pdf", schema)

        # Should create extractor and call extract
        mock_extractor_cls.assert_called_once()
        mock_extractor.extract.assert_called_once_with(
            pdf_path="/path/to/test.pdf",
            schema=schema,
            method=ExtractionMethod.HYBRID
        )

        assert result["method"] == "hybrid"

    @patch("backend.extraction.hybrid.HybridExtractor")
    def test_extract_hybrid_with_method(self, mock_extractor_cls):
        """Test extract_hybrid with specific method."""
        mock_extractor = Mock()
        mock_extractor.extract.return_value = {"kpis": {}}
        mock_extractor_cls.return_value = mock_extractor

        schema = {"type": "object"}
        extract_hybrid(
            "/path/to/test.pdf",
            schema,
            method=ExtractionMethod.TRANSFORMER
        )

        # Should pass method to extract
        call_args = mock_extractor.extract.call_args
        assert call_args[1]["method"] == ExtractionMethod.TRANSFORMER
