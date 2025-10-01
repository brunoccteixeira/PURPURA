"""Document models"""
from pydantic import BaseModel
from enum import Enum
from datetime import datetime
from typing import Optional


class DocumentStatus(str, Enum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    EXTRACTED = "extracted"
    VALIDATED = "validated"
    FAILED = "failed"


class Document(BaseModel):
    id: str
    filename: str
    status: DocumentStatus
    upload_date: datetime
    size_bytes: int
    company_name: Optional[str] = None
    fiscal_year: Optional[str] = None
    document_type: Optional[str] = None  # "sustainability_report", "risk_assessment", etc.
    extraction_progress: Optional[float] = None  # 0.0 to 1.0
    error_message: Optional[str] = None

    class Config:
        json_schema_extra = {
            "example": {
                "id": "doc_abc123",
                "filename": "relatorio_sustentabilidade_2024.pdf",
                "status": "extracted",
                "upload_date": "2025-10-01T10:00:00Z",
                "size_bytes": 2048576,
                "company_name": "Município de São Paulo",
                "fiscal_year": "2024",
                "document_type": "sustainability_report",
                "extraction_progress": 1.0,
            }
        }
