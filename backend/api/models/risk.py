"""Climate risk models"""
from pydantic import BaseModel
from enum import Enum
from typing import Dict, List, Optional


class RiskScenario(str, Enum):
    RCP26 = "rcp26"  # Low emissions
    RCP45 = "rcp45"  # Moderate emissions
    RCP85 = "rcp85"  # High emissions


class HazardType(str, Enum):
    FLOOD = "flood"
    DROUGHT = "drought"
    HEAT_STRESS = "heat_stress"
    LANDSLIDE = "landslide"
    COASTAL_INUNDATION = "coastal_inundation"


class HazardIndicator(BaseModel):
    """Climate hazard indicator"""
    hazard_type: HazardType
    current_risk: float  # 0.0 to 1.0
    projected_2030: float
    projected_2050: float
    data_source: str  # "Cemaden", "INPE", etc.
    confidence: float  # 0.0 to 1.0


class VulnerabilityIndicator(BaseModel):
    """Social/infrastructure vulnerability"""
    population_exposed: int
    critical_infrastructure_count: int
    vulnerable_population_pct: float
    adaptive_capacity_score: float  # 0.0 to 1.0


class MunicipalRisk(BaseModel):
    """Complete climate risk assessment for a municipality"""
    ibge_code: str
    municipality_name: str
    scenario: RiskScenario
    overall_risk_score: float  # 0.0 to 1.0
    hazards: List[HazardIndicator]
    vulnerability: VulnerabilityIndicator
    h3_grid_data: Optional[Dict[str, float]] = None  # H3 cell ID → risk score
    recommendations: List[str]

    class Config:
        json_schema_extra = {
            "example": {
                "ibge_code": "3550308",
                "municipality_name": "São Paulo",
                "scenario": "rcp45",
                "overall_risk_score": 0.65,
                "hazards": [
                    {
                        "hazard_type": "flood",
                        "current_risk": 0.4,
                        "projected_2030": 0.55,
                        "projected_2050": 0.7,
                        "data_source": "Cemaden",
                        "confidence": 0.85
                    }
                ],
                "vulnerability": {
                    "population_exposed": 500000,
                    "critical_infrastructure_count": 120,
                    "vulnerable_population_pct": 0.25,
                    "adaptive_capacity_score": 0.6
                },
                "recommendations": [
                    "Implementar sistema de drenagem em áreas críticas",
                    "Criar plano de evacuação para zonas de risco"
                ]
            }
        }
