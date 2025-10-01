"""Extraction models"""
from pydantic import BaseModel
from enum import Enum
from typing import Dict, Any, List, Optional
from datetime import datetime


class ExtractionMethod(str, Enum):
    TRANSFORMER = "transformer"  # OS-Climate transformer-based
    LLM = "llm"  # OpenAI GPT
    HYBRID = "hybrid"  # Both methods with confidence voting


class ConfidenceScore(BaseModel):
    """Confidence metrics for extracted field"""
    value: float  # 0.0 to 1.0
    method: ExtractionMethod
    sources: List[str]  # Page numbers or chunk IDs


class ExtractedField(BaseModel):
    """Single extracted data field"""
    field_name: str
    value: Any
    confidence: ConfidenceScore
    validated: bool = False
    corrected_value: Optional[Any] = None


class ExtractionResult(BaseModel):
    """Complete extraction result for a document"""
    document_id: str
    extracted_at: datetime
    method: ExtractionMethod
    kpis: Dict[str, ExtractedField]
    document_meta: Dict[str, Any]
    schema_valid: bool
    schema_errors: Optional[List[str]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "document_id": "doc_abc123",
                "extracted_at": "2025-10-01T11:00:00Z",
                "method": "hybrid",
                "kpis": {
                    "emissions_scope1": {
                        "field_name": "emissions_scope1",
                        "value": 1250.5,
                        "confidence": {
                            "value": 0.95,
                            "method": "hybrid",
                            "sources": ["page_12", "page_15"]
                        },
                        "validated": True
                    }
                },
                "document_meta": {
                    "company": "Município XYZ",
                    "fiscal_year": "2024"
                },
                "schema_valid": True
            }
        }
