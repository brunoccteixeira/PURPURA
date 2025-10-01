"""
OS-Climate Transformer Adapter
Wraps osc-transformer-presteps and osc-transformer-based-extractor
"""
from typing import List, Dict, Any, Optional
from pathlib import Path
import json
import logging

logger = logging.getLogger(__name__)


class OSCTransformerExtractor:
    """
    Adapter for OS-Climate transformer-based extraction tools

    Workflow:
    1. PDF → JSON (osc-transformer-presteps)
    2. JSON → KPI detection (osc-transformer-based-extractor)
    3. Return structured results with confidence scores
    """

    def __init__(self, model_path: Optional[str] = None):
        """
        Initialize OS-Climate extractor

        Args:
            model_path: Path to fine-tuned BERT model (optional)
        """
        self.model_path = model_path
        self._init_extractors()

    def _init_extractors(self):
        """Initialize OS-Climate extraction tools"""
        try:
            # Import OS-Climate modules
            from osc_transformer_presteps.content_extraction.extraction_factory import PDFExtractor
            self.pdf_extractor = PDFExtractor()
            logger.info("✓ OS-Climate PDF extractor initialized")

            # KPI detector (will integrate next)
            # from osc_transformer_based_extractor import KPIDetector
            # self.kpi_detector = KPIDetector()

            self.mock_mode = False
        except ImportError as e:
            logger.warning(f"OS-Climate tools not fully installed: {e}")
            logger.warning("Falling back to mock mode")
            self.pdf_extractor = None
            self.mock_mode = True

    def extract_from_pdf(
        self,
        pdf_path: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract structured data from PDF using OS-Climate transformers

        Args:
            pdf_path: Path to PDF file
            schema: JSON schema for expected output

        Returns:
            Extracted data with confidence scores
        """
        logger.info(f"Extracting from PDF: {pdf_path}")

        # Step 1: PDF → JSON (using osc-transformer-presteps)
        pdf_json = self._pdf_to_json(pdf_path)

        # Step 2: KPI Detection (using osc-transformer-based-extractor)
        kpis = self._detect_kpis(pdf_json, schema)

        # Step 3: Format results
        return {
            "method": "transformer",
            "kpis": kpis,
            "raw_json": pdf_json,
            "model": "osc-bert-base" if not self.model_path else self.model_path,
        }

    def _pdf_to_json(self, pdf_path: str) -> Dict[str, Any]:
        """
        Convert PDF to structured JSON using osc-transformer-presteps

        Args:
            pdf_path: Path to PDF file

        Returns:
            Structured JSON representation of PDF
        """
        if self.mock_mode or not self.pdf_extractor:
            logger.warning("Mock mode: returning placeholder data")
            return {
                "pages": [
                    {
                        "page_number": 1,
                        "text": "Sample extracted text from page 1",
                        "tables": [],
                        "figures": []
                    }
                ],
                "metadata": {
                    "total_pages": 1,
                    "file_name": Path(pdf_path).name
                }
            }

        logger.info(f"Extracting PDF with OS-Climate: {pdf_path}")

        try:
            # Use OS-Climate PDF extractor
            # Convert string path to Path object if needed
            from pathlib import Path as PathlibPath
            path_obj = PathlibPath(pdf_path) if isinstance(pdf_path, str) else pdf_path
            extraction_result = self.pdf_extractor.extract(path_obj)

            # OS-Climate returns ExtractionResponse object
            # Structure: {page_num: {paragraph_id: {pdf_name, paragraph, page, ...}}}
            pages = []

            if hasattr(extraction_result, 'dictionary') and extraction_result.success:
                # Parse OS-Climate format
                page_dict = extraction_result.dictionary

                # Group paragraphs by page
                pages_text = {}
                for page_key, paragraphs in page_dict.items():
                    for para_id, para_data in paragraphs.items():
                        page_num = para_data.get('page', int(page_key)) + 1  # Convert to 1-indexed
                        text = para_data.get('paragraph', '')

                        if page_num not in pages_text:
                            pages_text[page_num] = []
                        pages_text[page_num].append(text)

                # Convert to page list
                for page_num in sorted(pages_text.keys()):
                    pages.append({
                        "page_number": page_num,
                        "text": "\n".join(pages_text[page_num]),
                        "tables": [],  # TODO: Extract tables if available
                        "figures": []  # TODO: Extract figures if available
                    })

            elif isinstance(extraction_result, dict) and "pages" in extraction_result:
                # Fallback format
                for page_data in extraction_result["pages"]:
                    pages.append({
                        "page_number": page_data.get("page_number", 0),
                        "text": page_data.get("text", ""),
                        "tables": page_data.get("tables", []),
                        "figures": page_data.get("figures", [])
                    })
            elif isinstance(extraction_result, str):
                # Simple text extraction
                pages.append({
                    "page_number": 1,
                    "text": extraction_result,
                    "tables": [],
                    "figures": []
                })

            return {
                "pages": pages,
                "metadata": {
                    "total_pages": len(pages),
                    "file_name": Path(pdf_path).name,
                    "extractor": "osc-transformer-presteps"
                }
            }

        except Exception as e:
            logger.error(f"PDF extraction failed: {e}")
            # Fallback to pypdf
            logger.info("Falling back to pypdf extraction")
            from pypdf import PdfReader

            reader = PdfReader(pdf_path)
            pages = []
            for i, page in enumerate(reader.pages):
                pages.append({
                    "page_number": i + 1,
                    "text": page.extract_text() or "",
                    "tables": [],
                    "figures": []
                })

            return {
                "pages": pages,
                "metadata": {
                    "total_pages": len(pages),
                    "file_name": Path(pdf_path).name,
                    "extractor": "pypdf (fallback)"
                }
            }

    def _detect_kpis(
        self,
        pdf_json: Dict[str, Any],
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Detect KPIs from JSON using BERT-based model

        Args:
            pdf_json: Structured JSON from PDF
            schema: Expected KPI schema

        Returns:
            Detected KPIs with confidence scores
        """
        # TODO: Implement actual osc-transformer-based-extractor integration
        logger.info("Detecting KPIs from JSON")

        # Mock KPI detection results
        return {
            "emissions_scope1": {
                "value": None,
                "confidence": 0.0,
                "source_page": None,
                "source_text": None,
                "method": "transformer"
            },
            "emissions_scope2": {
                "value": None,
                "confidence": 0.0,
                "source_page": None,
                "source_text": None,
                "method": "transformer"
            }
        }

    def extract_from_text(
        self,
        text: str,
        schema: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Extract KPIs from plain text

        Args:
            text: Input text
            schema: Expected KPI schema

        Returns:
            Extracted KPIs with confidence
        """
        # Convert text to mock JSON structure
        mock_json = {
            "pages": [{"page_number": 1, "text": text}],
            "metadata": {}
        }

        kpis = self._detect_kpis(mock_json, schema)

        return {
            "method": "transformer",
            "kpis": kpis,
            "model": "osc-bert-base"
        }


# Convenience function for quick extraction
def extract_with_transformers(
    pdf_path: str,
    schema: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Quick extraction using OS-Climate transformers

    Args:
        pdf_path: Path to PDF file
        schema: JSON schema for validation

    Returns:
        Extraction results
    """
    extractor = OSCTransformerExtractor()
    return extractor.extract_from_pdf(pdf_path, schema)
