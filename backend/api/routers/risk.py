"""
Climate Risk Assessment Router
Physical risk calculations using physrisk + Brazilian hazard data
"""
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List
import sys
from pathlib import Path

# Add backend to path for imports
backend_root = Path(__file__).resolve().parents[2]
if str(backend_root) not in sys.path:
    sys.path.insert(0, str(backend_root))

from risk.calculator import (
    RiskCalculator,
    RiskScenario as CalcRiskScenario,
    HazardType as CalcHazardType
)
from risk.h3_service import H3RiskMapper, get_geojson_for_municipality
from ..models.risk import MunicipalRisk, RiskScenario, HazardIndicator, VulnerabilityIndicator

router = APIRouter()

# Initialize risk calculator
risk_calculator = RiskCalculator(use_brazilian_data=True)


def map_scenario_to_calc(scenario: RiskScenario) -> CalcRiskScenario:
    """Map API RiskScenario to calculator RiskScenario"""
    mapping = {
        RiskScenario.RCP26: CalcRiskScenario.SSP126,
        RiskScenario.RCP45: CalcRiskScenario.SSP245,
        RiskScenario.RCP85: CalcRiskScenario.SSP585,
    }
    return mapping.get(scenario, CalcRiskScenario.SSP245)


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
    try:
        # Map scenario
        calc_scenario = map_scenario_to_calc(scenario)

        # Calculate risk
        location_risk = risk_calculator.calculate_municipality_risk(
            ibge_code=ibge_code,
            scenario=calc_scenario
        )

        # Convert to API model
        hazards = [
            HazardIndicator(
                hazard_type=h.hazard_type.value,
                current_risk=h.current_risk,
                projected_2030=h.projected_2030,
                projected_2050=h.projected_2050,
                data_source=h.data_source,
                confidence=h.confidence
            )
            for h in location_risk.hazards
        ]

        # Mock vulnerability data (TODO: implement real vulnerability assessment)
        vulnerability = VulnerabilityIndicator(
            population_exposed=100000,  # TODO: Query from IBGE
            critical_infrastructure_count=50,  # TODO: Query from OpenStreetMap
            vulnerable_population_pct=0.25,  # TODO: Calculate from IBGE census
            adaptive_capacity_score=0.6  # TODO: Calculate from municipality indicators
        )

        # Generate recommendations
        recommendations = []
        for hazard in location_risk.hazards:
            if hazard.projected_2050 > 0.5:
                if hazard.hazard_type.value == "flood":
                    recommendations.append(
                        "Implementar sistema de drenagem em áreas críticas"
                    )
                elif hazard.hazard_type.value == "drought":
                    recommendations.append(
                        "Desenvolver plano de gestão de recursos hídricos"
                    )
                elif hazard.hazard_type.value == "heat_stress":
                    recommendations.append(
                        "Criar programa de adaptação ao calor extremo"
                    )

        return MunicipalRisk(
            ibge_code=ibge_code,
            municipality_name=location_risk.municipality_name or f"Município {ibge_code}",
            scenario=scenario,
            overall_risk_score=location_risk.overall_risk_score,
            hazards=hazards,
            vulnerability=vulnerability,
            h3_grid_data=None,  # Can be fetched separately via /h3-grid endpoint
            recommendations=recommendations
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating municipal risk: {str(e)}"
        )


@router.get("/hazards/{ibge_code}")
async def get_hazard_indicators(
    ibge_code: str,
    scenario: RiskScenario = RiskScenario.RCP45
):
    """
    Get current and projected climate hazards for a municipality

    - **ibge_code**: IBGE 7-digit municipality code
    - **scenario**: Climate scenario
    """
    try:
        calc_scenario = map_scenario_to_calc(scenario)

        location_risk = risk_calculator.calculate_municipality_risk(
            ibge_code=ibge_code,
            scenario=calc_scenario
        )

        # Format hazards for response
        hazards = {}
        for h in location_risk.hazards:
            hazards[h.hazard_type.value] = {
                "current": h.current_risk,
                "projected_2030": h.projected_2030,
                "projected_2050": h.projected_2050,
                "confidence": h.confidence,
                "data_source": h.data_source
            }

        return {
            "ibge_code": ibge_code,
            "municipality_name": location_risk.municipality_name,
            "scenario": scenario.value,
            "hazards": hazards
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error retrieving hazard indicators: {str(e)}"
        )


@router.post("/scenario-analysis")
async def run_scenario_analysis(
    ibge_code: str,
    scenarios: List[RiskScenario]
):
    """
    Run multi-scenario risk analysis

    - **ibge_code**: IBGE 7-digit municipality code
    - **scenarios**: List of climate scenarios to analyze
    """
    try:
        results = []

        for scenario in scenarios:
            calc_scenario = map_scenario_to_calc(scenario)

            location_risk = risk_calculator.calculate_municipality_risk(
                ibge_code=ibge_code,
                scenario=calc_scenario
            )

            results.append({
                "scenario": scenario.value,
                "overall_risk": location_risk.overall_risk_score,
                "hazards": {
                    h.hazard_type.value: h.projected_2050
                    for h in location_risk.hazards
                }
            })

        return {
            "ibge_code": ibge_code,
            "municipality_name": location_risk.municipality_name,
            "scenarios": results
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error running scenario analysis: {str(e)}"
        )


@router.get("/h3-grid/{ibge_code}")
async def get_h3_risk_grid(
    ibge_code: str,
    scenario: RiskScenario = RiskScenario.RCP45,
    resolution: int = Query(7, ge=5, le=9),
    rings: int = Query(2, ge=1, le=5),
    format: str = Query("geojson", regex="^(geojson|heatmap)$")
):
    """
    Get H3 hexagonal risk grid for a municipality

    - **ibge_code**: IBGE 7-digit municipality code
    - **scenario**: Climate scenario
    - **resolution**: H3 resolution (5-9, default 7 for municipalities)
    - **rings**: Number of hexagonal rings around center (1-5)
    - **format**: Response format (geojson or heatmap)
    """
    try:
        calc_scenario = map_scenario_to_calc(scenario)

        if format == "geojson":
            # Return GeoJSON for web mapping
            geojson = get_geojson_for_municipality(
                ibge_code=ibge_code,
                resolution=resolution,
                rings=rings
            )
            return geojson
        else:
            # Return heatmap format (h3_index → risk_score)
            mapper = H3RiskMapper(resolution=resolution, scenario=calc_scenario)
            cells = mapper.create_municipality_grid(ibge_code, rings)
            heatmap = mapper.get_risk_heatmap_data(cells)

            return {
                "ibge_code": ibge_code,
                "resolution": resolution,
                "scenario": scenario.value,
                "heatmap": heatmap
            }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error generating H3 grid: {str(e)}"
        )


@router.get("/location")
async def get_location_risk(
    lat: float = Query(..., ge=-90, le=90),
    lng: float = Query(..., ge=-180, le=180),
    scenario: RiskScenario = RiskScenario.RCP45
):
    """
    Get climate risk for arbitrary lat/lng coordinates

    - **lat**: Latitude in decimal degrees
    - **lng**: Longitude in decimal degrees
    - **scenario**: Climate scenario
    """
    try:
        calc_scenario = map_scenario_to_calc(scenario)

        location_risk = risk_calculator.calculate_location_risk(
            latitude=lat,
            longitude=lng,
            scenario=calc_scenario
        )

        return {
            "latitude": lat,
            "longitude": lng,
            "scenario": scenario.value,
            "overall_risk": location_risk.overall_risk_score,
            "hazards": {
                h.hazard_type.value: {
                    "current": h.current_risk,
                    "projected_2030": h.projected_2030,
                    "projected_2050": h.projected_2050,
                    "confidence": h.confidence
                }
                for h in location_risk.hazards
            }
        }

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error calculating location risk: {str(e)}"
        )
