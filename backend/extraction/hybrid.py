"""
Hybrid Extraction Orchestrator
Combines OS-Climate transformers + OpenAI LLM with confidence voting
"""
from typing import Dict, Any, List, Optional, Literal
from enum import Enum
import logging
from pathlib import Path

from .transformers.osc_adapter import OSCTransformerExtractor
from .llm.openai_extractor import LLMClient, extract as llm_extract

logger = logging.getLogger(__name__)


class ExtractionMethod(str, Enum):
    TRANSFORMER = "transformer"
    LLM = "llm"
    HYBRID = "hybrid"


class ConfidenceVoting:
    """
    Confidence-based voting for hybrid extraction results

    Strategy:
    - If both methods agree: Use higher confidence value
    - If they disagree: Use method with higher confidence
    - Weight transformer slightly higher for numerical data
    - Weight LLM higher for text/descriptive fields
    """

    @staticmethod
    def merge_kpis(
        transformer_kpis: Dict[str, Any],
        llm_kpis: Dict[str, Any],
        weights: Optional[Dict[str, float]] = None
    ) -> Dict[str, Any]:
        """
        Merge KPIs from both methods using confidence voting

        Args:
            transformer_kpis: Results from BERT transformer
            llm_kpis: Results from OpenAI LLM
            weights: Optional method weights per field type

        Returns:
            Merged KPIs with confidence scores
        """
        merged = {}

        # Get all unique KPI keys
        all_keys = set(transformer_kpis.keys()) | set(llm_kpis.keys())

        for key in all_keys:
            trans_result = transformer_kpis.get(key, {})
            llm_result = llm_kpis.get(key, {})

            # Extract values and confidences
            trans_value = trans_result.get("value")
            trans_conf = trans_result.get("confidence", 0.0)

            llm_value = llm_result.get("value")
            llm_conf = llm_result.get("confidence", 0.0) if isinstance(llm_result, dict) else 0.0

            # Voting logic
            if trans_value is None and llm_value is None:
                # Neither method found the value
                merged[key] = {
                    "value": None,
                    "confidence": 0.0,
                    "method": "hybrid",
                    "agreement": False,
                    "sources": []
                }
            elif trans_value is None:
                # Only LLM found value
                merged[key] = {
                    "value": llm_value,
                    "confidence": llm_conf * 0.8,  # Penalize single-method
                    "method": "llm",
                    "agreement": False,
                    "sources": ["llm"]
                }
            elif llm_value is None:
                # Only transformer found value
                merged[key] = {
                    "value": trans_value,
                    "confidence": trans_conf * 0.8,  # Penalize single-method
                    "method": "transformer",
                    "agreement": False,
                    "sources": ["transformer"]
                }
            else:
                # Both found values - check agreement
                agreement = ConfidenceVoting._check_agreement(trans_value, llm_value)

                if agreement:
                    # Values agree - boost confidence
                    avg_conf = (trans_conf + llm_conf) / 2
                    merged[key] = {
                        "value": trans_value if trans_conf >= llm_conf else llm_value,
                        "confidence": min(avg_conf * 1.2, 1.0),  # Boost for agreement
                        "method": "hybrid",
                        "agreement": True,
                        "sources": ["transformer", "llm"],
                        "transformer_value": trans_value,
                        "llm_value": llm_value
                    }
                else:
                    # Values disagree - use higher confidence
                    if trans_conf > llm_conf:
                        merged[key] = {
                            "value": trans_value,
                            "confidence": trans_conf,
                            "method": "transformer",
                            "agreement": False,
                            "sources": ["transformer", "llm"],
                            "conflict": {"llm_value": llm_value, "llm_confidence": llm_conf}
                        }
                    else:
                        merged[key] = {
                            "value": llm_value,
                            "confidence": llm_conf,
                            "method": "llm",
                            "agreement": False,
                            "sources": ["transformer", "llm"],
                            "conflict": {"transformer_value": trans_value, "transformer_confidence": trans_conf}
                        }

        return merged

    @staticmethod
    def _check_agreement(value1: Any, value2: Any, tolerance: float = 0.1) -> bool:
        """
        Check if two values agree within tolerance

        Args:
            value1: First value
            value2: Second value
            tolerance: Tolerance for numerical comparison (10% default)

        Returns:
            True if values agree
        """
        # Exact match
        if value1 == value2:
            return True

        # Numerical comparison with tolerance
        if isinstance(value1, (int, float)) and isinstance(value2, (int, float)):
            if value1 == 0 or value2 == 0:
                return abs(value1 - value2) < tolerance
            relative_diff = abs(value1 - value2) / max(abs(value1), abs(value2))
            return relative_diff < tolerance

        # String comparison (case-insensitive)
        if isinstance(value1, str) and isinstance(value2, str):
            return value1.lower().strip() == value2.lower().strip()

        return False


class HybridExtractor:
    """
    Hybrid extraction pipeline combining transformer and LLM methods
    """

    def __init__(
        self,
        use_transformer: bool = True,
        use_llm: bool = True,
        llm_client: Optional[LLMClient] = None
    ):
        """
        Initialize hybrid extractor

        Args:
            use_transformer: Enable transformer-based extraction
            use_llm: Enable LLM-based extraction
            llm_client: Optional pre-configured LLM client
        """
        self.use_transformer = use_transformer
        self.use_llm = use_llm

        if use_transformer:
            self.transformer_extractor = OSCTransformerExtractor()

        if use_llm:
            self.llm_client = llm_client or LLMClient()

    def extract(
        self,
        pdf_path: Optional[str] = None,
        text: Optional[str] = None,
        document_meta: Optional[Dict[str, Any]] = None,
        evidence_chunks: Optional[List[Dict[str, Any]]] = None,
        template: Optional[str] = None,
        schema: Optional[Dict[str, Any]] = None,
        method: ExtractionMethod = ExtractionMethod.HYBRID
    ) -> Dict[str, Any]:
        """
        Extract structured data using hybrid approach

        Args:
            pdf_path: Path to PDF (for transformer)
            text: Text input (for LLM)
            document_meta: Document metadata
            evidence_chunks: Pre-chunked evidence for LLM
            template: Prompt template for LLM
            schema: JSON schema for validation
            method: Extraction method to use

        Returns:
            Extraction results with confidence scores
        """
        logger.info(f"Starting hybrid extraction (method={method})")

        transformer_results = None
        llm_results = None

        # Run transformer extraction
        if method in [ExtractionMethod.TRANSFORMER, ExtractionMethod.HYBRID] and self.use_transformer:
            if pdf_path:
                logger.info("Running transformer extraction...")
                transformer_results = self.transformer_extractor.extract_from_pdf(pdf_path, schema)
            elif text:
                transformer_results = self.transformer_extractor.extract_from_text(text, schema)

        # Run LLM extraction
        if method in [ExtractionMethod.LLM, ExtractionMethod.HYBRID] and self.use_llm:
            if evidence_chunks and document_meta and template and schema:
                logger.info("Running LLM extraction...")
                llm_results = llm_extract(
                    document_meta,
                    evidence_chunks,
                    self.llm_client,
                    template,
                    schema
                )

        # Merge results if hybrid
        if method == ExtractionMethod.HYBRID and transformer_results and llm_results:
            logger.info("Merging results from both methods...")
            merged_kpis = ConfidenceVoting.merge_kpis(
                transformer_results.get("kpis", {}),
                llm_results.get("kpis", {})
            )

            return {
                "method": "hybrid",
                "kpis": merged_kpis,
                "document_meta": document_meta or {},
                "transformer_results": transformer_results,
                "llm_results": llm_results,
                "extracted_at": llm_results.get("extracted_at") if llm_results else None
            }

        # Return single method results
        if transformer_results and not llm_results:
            return {**transformer_results, "document_meta": document_meta or {}}

        if llm_results and not transformer_results:
            return llm_results

        # Fallback
        return {
            "method": str(method),
            "kpis": {},
            "document_meta": document_meta or {},
            "error": "No extraction results available"
        }


# Convenience function
def extract_hybrid(
    pdf_path: str,
    schema: Dict[str, Any],
    method: ExtractionMethod = ExtractionMethod.HYBRID
) -> Dict[str, Any]:
    """
    Quick hybrid extraction from PDF

    Args:
        pdf_path: Path to PDF file
        schema: JSON schema
        method: Extraction method

    Returns:
        Extraction results
    """
    extractor = HybridExtractor()
    return extractor.extract(pdf_path=pdf_path, schema=schema, method=method)
