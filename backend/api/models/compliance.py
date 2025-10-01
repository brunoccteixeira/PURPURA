"""Compliance and reporting models"""
from pydantic import BaseModel
from enum import Enum
from typing import Dict, List, Any, Optional
from datetime import datetime


class ReportType(str, Enum):
    LEI14904 = "lei14904"  # Brazilian municipal climate adaptation
    IFRS_S1 = "ifrs_s1"  # Sustainability-related disclosures
    IFRS_S2 = "ifrs_s2"  # Climate-related disclosures
    TSB = "tsb"  # Brazilian Sustainable Taxonomy


class ComplianceStatus(str, Enum):
    COMPLIANT = "compliant"
    PARTIAL = "partial"
    NON_COMPLIANT = "non_compliant"
    INSUFFICIENT_DATA = "insufficient_data"


class ComplianceRequirement(BaseModel):
    """Single compliance requirement"""
    requirement_id: str
    description: str
    status: ComplianceStatus
    evidence: Optional[List[str]] = None  # Document IDs or data sources
    gap_analysis: Optional[str] = None


class ComplianceReport(BaseModel):
    """Complete compliance report"""
    report_id: str
    report_type: ReportType
    entity_id: str  # IBGE code for municipalities, CNPJ for companies
    entity_name: str
    generated_at: datetime
    reporting_period: str  # "2024", "Q1 2024", etc.
    overall_status: ComplianceStatus
    requirements: List[ComplianceRequirement]
    recommendations: List[str]
    data_sources: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "report_id": "rpt_lei14904_3550308_2024",
                "report_type": "lei14904",
                "entity_id": "3550308",
                "entity_name": "São Paulo",
                "generated_at": "2025-10-01T12:00:00Z",
                "reporting_period": "2024",
                "overall_status": "partial",
                "requirements": [
                    {
                        "requirement_id": "lei14904_art3_i",
                        "description": "Diagnóstico de vulnerabilidades climáticas",
                        "status": "compliant",
                        "evidence": ["doc_abc123", "cemaden_data_2024"]
                    },
                    {
                        "requirement_id": "lei14904_art3_ii",
                        "description": "Plano de adaptação climática",
                        "status": "non_compliant",
                        "gap_analysis": "Plano não foi elaborado ou submetido"
                    }
                ],
                "recommendations": [
                    "Elaborar plano de adaptação climática municipal",
                    "Realizar consulta pública sobre vulnerabilidades"
                ],
                "data_sources": ["Cemaden", "IBGE", "Upload: relatorio_2024.pdf"]
            }
        }
