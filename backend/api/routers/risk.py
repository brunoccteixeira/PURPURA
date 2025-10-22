"""
Climate Risk Assessment Router
Physical risk calculations using physrisk + Brazilian hazard data
"""
from fastapi import APIRouter, HTTPException
from typing import Optional, Dict
from pathlib import Path
import sys

# Add repo root to path for imports
REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.api.models.risk import (
    MunicipalRisk,
    RiskScenario,
    HazardIndicator,
    VulnerabilityIndicator,
    HazardType
)
from backend.services.physical_risk import (
    get_risk_service,
    RiskScenario as ServiceRiskScenario
)
from backend.services.ibge_data import get_ibge_service

router = APIRouter()


@router.get("/municipality/{ibge_code}", response_model=MunicipalRisk)
async def get_municipal_risk(
    ibge_code: str,
    scenario: RiskScenario = RiskScenario.RCP45
):
    """
    Get climate risk assessment for a Brazilian municipality

    - **ibge_code**: IBGE 7-digit municipality code
    - **scenario**: Climate scenario (RCP 2.6, 4.5, 8.5)
    """
    # Get municipality data
    ibge_service = get_ibge_service()
    muni = ibge_service.get_municipality(ibge_code)

    if not muni:
        raise HTTPException(
            status_code=404,
            detail=f"Municipality {ibge_code} not found in database"
        )

    # Calculate physical risks
    risk_service = get_risk_service()

    # Map API scenario to service scenario
    service_scenario = ServiceRiskScenario(scenario.value)

    hazard_scores = risk_service.calculate_municipal_risk(
        ibge_code=ibge_code,
        latitude=muni.latitude,
        longitude=muni.longitude,
        scenario=service_scenario
    )

    # Convert to API model
    hazards = [
        HazardIndicator(
            hazard_type=HazardType(score.hazard_type.value),
            current_risk=score.current_risk,
            projected_2030=score.projected_2030,
            projected_2050=score.projected_2050,
            data_source=score.data_source,
            confidence=score.confidence
        )
        for score in hazard_scores
    ]

    # Calculate overall risk score (average of current risks)
    overall_risk = sum(h.current_risk for h in hazards) / len(hazards)

    # Generate H3 grid (optional)
    h3_grid = risk_service.get_h3_risk_grid(
        latitude=muni.latitude,
        longitude=muni.longitude,
        resolution=7,
        radius_km=10
    )

    # Mock vulnerability data (TODO: real calculation)
    vulnerability = VulnerabilityIndicator(
        population_exposed=int((muni.population or 100000) * overall_risk * 0.3),
        critical_infrastructure_count=int(50 * overall_risk),
        vulnerable_population_pct=0.20 + overall_risk * 0.15,
        adaptive_capacity_score=max(0.3, 0.7 - overall_risk * 0.4)
    )

    # Generate recommendations
    recommendations = _generate_recommendations(hazards, muni.name)

    return MunicipalRisk(
        ibge_code=ibge_code,
        municipality_name=muni.name,
        scenario=scenario,
        overall_risk_score=overall_risk,
        hazards=hazards,
        vulnerability=vulnerability,
        h3_grid_data=h3_grid if h3_grid else None,
        recommendations=recommendations
    )


@router.get("/hazards/{ibge_code}")
async def get_hazard_indicators(ibge_code: str, scenario: RiskScenario = RiskScenario.RCP45):
    """
    Get current and projected climate hazards for a municipality

    - **ibge_code**: IBGE 7-digit municipality code
    - **scenario**: Climate scenario (default RCP4.5)

    Returns simplified hazard-only data (no full risk assessment)
    """
    # Get municipality data
    ibge_service = get_ibge_service()
    muni = ibge_service.get_municipality(ibge_code)

    if not muni:
        raise HTTPException(
            status_code=404,
            detail=f"Municipality {ibge_code} not found in database"
        )

    # Calculate risks
    risk_service = get_risk_service()
    service_scenario = ServiceRiskScenario(scenario.value)

    hazard_scores = risk_service.calculate_municipal_risk(
        ibge_code=ibge_code,
        latitude=muni.latitude,
        longitude=muni.longitude,
        scenario=service_scenario
    )

    # Format response
    hazards = {
        score.hazard_type.value: {
            "current": score.current_risk,
            "projected_2030": score.projected_2030,
            "projected_2050": score.projected_2050,
            "confidence": score.confidence,
            "data_source": score.data_source,
        }
        for score in hazard_scores
    }

    return {
        "ibge_code": ibge_code,
        "municipality_name": muni.name,
        "scenario": scenario.value,
        "hazards": hazards,
    }


@router.post("/scenario-analysis")
async def run_scenario_analysis(
    ibge_code: str,
    scenarios: list[RiskScenario]
):
    """
    Run multi-scenario risk analysis

    - **ibge_code**: IBGE 7-digit municipality code
    - **scenarios**: List of climate scenarios to analyze
    """
    # Get municipality data
    ibge_service = get_ibge_service()
    muni = ibge_service.get_municipality(ibge_code)

    if not muni:
        raise HTTPException(
            status_code=404,
            detail=f"Municipality {ibge_code} not found in database"
        )

    # Run analysis for each scenario
    risk_service = get_risk_service()
    results = []

    for scenario in scenarios:
        service_scenario = ServiceRiskScenario(scenario.value)

        hazard_scores = risk_service.calculate_municipal_risk(
            ibge_code=ibge_code,
            latitude=muni.latitude,
            longitude=muni.longitude,
            scenario=service_scenario
        )

        # Calculate overall risk
        overall_risk = sum(s.current_risk for s in hazard_scores) / len(hazard_scores)

        results.append({
            "scenario": scenario.value,
            "overall_risk_score": round(overall_risk, 3),
            "hazards": [
                {
                    "hazard_type": s.hazard_type.value,
                    "current_risk": s.current_risk,
                    "projected_2030": s.projected_2030,
                    "projected_2050": s.projected_2050,
                }
                for s in hazard_scores
            ]
        })

    return {
        "ibge_code": ibge_code,
        "municipality_name": muni.name,
        "scenarios_analyzed": [s.value for s in scenarios],
        "results": results,
    }


# Helper functions

def _generate_recommendations(
    hazards: list[HazardIndicator],
    municipality_name: str
) -> list[str]:
    """Generate climate adaptation recommendations based on hazard scores"""
    recommendations = []

    # Check each hazard and add relevant recommendations
    for hazard in hazards:
        if hazard.current_risk > 0.5:
            if hazard.hazard_type == HazardType.FLOOD:
                recommendations.append(
                    f"Priorizar sistemas de drenagem e contenção de enchentes em {municipality_name}"
                )
            elif hazard.hazard_type == HazardType.DROUGHT:
                recommendations.append(
                    f"Implementar programa de reuso de água e gestão de recursos hídricos"
                )
            elif hazard.hazard_type == HazardType.HEAT_STRESS:
                recommendations.append(
                    f"Desenvolver plano de aumento de áreas verdes e sombreamento urbano"
                )
            elif hazard.hazard_type == HazardType.LANDSLIDE:
                recommendations.append(
                    f"Mapear áreas de risco e implementar sistema de monitoramento de encostas"
                )
            elif hazard.hazard_type == HazardType.COASTAL_INUNDATION:
                recommendations.append(
                    f"Estabelecer zonas de proteção costeira e plano de evacuação"
                )

        # Check for high projected increase
        if hazard.projected_2050 > hazard.current_risk * 1.4:
            recommendations.append(
                f"Planejamento de longo prazo para {hazard.hazard_type.value}: "
                f"risco pode aumentar {int((hazard.projected_2050/hazard.current_risk - 1)*100)}% até 2050"
            )

    # Add general recommendations
    if not recommendations:
        recommendations.append(
            f"Manter monitoramento contínuo dos indicadores climáticos em {municipality_name}"
        )

    recommendations.append(
        "Desenvolver Plano Municipal de Adaptação Climática (Lei 14.904/2025)"
    )

    return recommendations[:5]  # Limit to top 5 recommendations
