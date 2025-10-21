"""
Climate Risk Assessment Router

Physical risk calculations using physrisk + Brazilian hazard data (Cemaden, INPE, IBGE).

Currently using mock data for MVP. Real API integrations coming soon.
"""

import logging
from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from ..models.risk import (
    MunicipalRisk,
    RiskScenario,
    HazardIndicator,
    HazardType,
)
from backend.data.municipalities import get_municipality_data, get_all_municipalities
from backend.services.physical_risk_calculator import get_risk_calculator
from backend.services.h3_risk_service import get_h3_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/municipality/{ibge_code}", response_model=MunicipalRisk)
async def get_municipal_risk(
    ibge_code: str,
    scenario: RiskScenario = RiskScenario.RCP45,
    include_h3_grid: bool = Query(
        False, description="Include H3 hexagonal grid risk data for visualization"
    ),
):
    """
    Get comprehensive climate risk assessment for a Brazilian municipality

    Returns hazard indicators, vulnerability metrics, overall risk score,
    and optionally H3 grid data for spatial visualization.

    **Parameters:**
    - **ibge_code**: IBGE 7-digit municipality code (e.g., 3550308 for São Paulo)
    - **scenario**: Climate scenario - RCP26 (low), RCP45 (moderate), RCP85 (high)
    - **include_h3_grid**: Include H3 hexagonal grid data (default: false)

    **Example:**
    ```
    GET /api/v1/risk/municipality/3550308?scenario=rcp45&include_h3_grid=true
    ```

    **Data Sources:**
    - Mock data (MVP): Realistic synthetic data based on historical patterns
    - Future: Cemaden (alerts), INPE (projections), physrisk-lib (modeling)
    """
    logger.info(
        f"GET municipal risk: ibge_code={ibge_code}, scenario={scenario.value}, "
        f"include_h3_grid={include_h3_grid}"
    )

    # 1. Buscar dados do município
    muni_data = get_municipality_data(ibge_code)
    if not muni_data:
        raise HTTPException(
            status_code=404,
            detail=f"Municipality with IBGE code {ibge_code} not found in database. "
            f"Currently supporting 10 priority municipalities.",
        )

    try:
        # 2. Calcular riscos com calculadora
        calculator = get_risk_calculator(use_mock=True)

        # 3. Construir hazard indicators
        hazards = calculator.build_hazard_indicators(ibge_code, scenario)

        if not hazards:
            raise HTTPException(
                status_code=500,
                detail="Failed to calculate hazard indicators. No hazard data available.",
            )

        # 4. Calcular vulnerabilidade
        vulnerability = calculator.calculate_vulnerability(ibge_code)

        # 5. Score geral de risco
        overall_risk = calculator.calculate_overall_risk_score(hazards, vulnerability)

        # 6. H3 grid (se solicitado)
        h3_grid_data = None
        if include_h3_grid:
            logger.info("Generating H3 grid...")
            h3_service = get_h3_service()

            # Obter scores de hazard para grid
            hazard_scores = calculator.calculate_municipality_risk(ibge_code, scenario, 2030)

            h3_grid_data = h3_service.generate_grid_from_hazard_data(
                center_lat=muni_data["lat"],
                center_lon=muni_data["lon"],
                hazard_scores=hazard_scores,
                radius_km=20,  # 20km de raio
                resolution=7,  # ~5km² por célula
            )

            # Log estatísticas do grid
            grid_stats = h3_service.get_grid_stats(h3_grid_data)
            logger.info(f"H3 grid generated: {grid_stats}")

        # 7. Gerar recomendações
        recommendations = calculator.generate_recommendations(hazards, vulnerability)

        # 8. Montar resposta
        return MunicipalRisk(
            ibge_code=ibge_code,
            municipality_name=muni_data["name"],
            scenario=scenario,
            overall_risk_score=overall_risk,
            hazards=hazards,
            vulnerability=vulnerability,
            h3_grid_data=h3_grid_data,
            recommendations=recommendations,
        )

    except ValueError as e:
        logger.error(f"ValueError calculating risk for {ibge_code}: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error calculating risk for {ibge_code}: {str(e)}",
            exc_info=True,
        )
        raise HTTPException(
            status_code=500,
            detail=f"Internal error calculating risk: {str(e)}",
        )


@router.get("/hazards/{ibge_code}", response_model=List[HazardIndicator])
async def get_hazard_indicators(
    ibge_code: str,
    scenario: RiskScenario = RiskScenario.RCP45,
    hazard_type: Optional[HazardType] = Query(
        None, description="Filter by specific hazard type"
    ),
):
    """
    Get detailed hazard indicators for a municipality

    Returns current and projected climate hazards (flood, drought, heat stress, etc.)

    **Parameters:**
    - **ibge_code**: IBGE 7-digit municipality code
    - **scenario**: Climate scenario (RCP26, RCP45, RCP85)
    - **hazard_type**: Optional filter (flood, drought, heat_stress, landslide, coastal_inundation)

    **Example:**
    ```
    GET /api/v1/risk/hazards/3550308?scenario=rcp45&hazard_type=flood
    ```

    **Data Sources:**
    - Mock data (MVP): Based on Cemaden historical alerts and INPE projections
    - Future: Real-time Cemaden API + INPE climate scenarios
    """
    logger.info(
        f"GET hazards: ibge_code={ibge_code}, scenario={scenario.value}, "
        f"hazard_type={hazard_type}"
    )

    # Validar município
    muni_data = get_municipality_data(ibge_code)
    if not muni_data:
        raise HTTPException(
            status_code=404,
            detail=f"Municipality {ibge_code} not found",
        )

    try:
        # Buscar hazard indicators
        calculator = get_risk_calculator(use_mock=True)
        hazards = calculator.build_hazard_indicators(ibge_code, scenario)

        # Filtrar por tipo se especificado
        if hazard_type:
            hazards = [h for h in hazards if h.hazard_type == hazard_type]

        if not hazards:
            raise HTTPException(
                status_code=404,
                detail=f"No hazard data available for {ibge_code}"
                + (f" with type {hazard_type.value}" if hazard_type else ""),
            )

        return hazards

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error getting hazards for {ibge_code}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


@router.post("/scenario-analysis", status_code=202)
async def run_scenario_analysis(
    ibge_codes: List[str] = Query(..., description="List of IBGE municipality codes"),
    scenarios: List[RiskScenario] = Query(
        default=[RiskScenario.RCP45, RiskScenario.RCP85],
        description="Climate scenarios to analyze",
    ),
    years: List[int] = Query(default=[2030, 2050], description="Projection years"),
):
    """
    Run multi-scenario climate risk analysis (async task)

    Compares risk across multiple municipalities, scenarios, and time horizons.
    Returns task ID for polling results.

    **Parameters:**
    - **ibge_codes**: List of municipality codes to analyze
    - **scenarios**: List of climate scenarios (default: RCP45, RCP85)
    - **years**: List of projection years (default: 2030, 2050)

    **Example:**
    ```
    POST /api/v1/risk/scenario-analysis
    ?ibge_codes=3550308&ibge_codes=3304557
    &scenarios=rcp45&scenarios=rcp85
    &years=2030&years=2050
    ```

    **Returns:**
    ```json
    {
        "task_id": "abc123-def456",
        "status": "processing",
        "estimated_completion_minutes": 2,
        "municipalities_count": 2,
        "scenarios_count": 2,
        "years_count": 2
    }
    ```

    **Future:** Implement async task queue (Celery/Redis) for long-running analyses
    """
    logger.info(
        f"POST scenario analysis: {len(ibge_codes)} municipalities, "
        f"{len(scenarios)} scenarios, {len(years)} years"
    )

    # Validar municípios
    invalid_codes = []
    for code in ibge_codes:
        if not get_municipality_data(code):
            invalid_codes.append(code)

    if invalid_codes:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid IBGE codes: {', '.join(invalid_codes)}",
        )

    # TODO: Implementar processamento assíncrono com Celery
    # from backend.tasks import run_scenario_analysis_task
    # task = run_scenario_analysis_task.delay(ibge_codes, scenarios, years)
    # task_id = task.id

    # Por ora, retornar resposta mock
    import uuid

    task_id = str(uuid.uuid4())

    return {
        "task_id": task_id,
        "status": "processing",
        "estimated_completion_minutes": len(ibge_codes) * len(scenarios) * 0.5,
        "municipalities_count": len(ibge_codes),
        "scenarios_count": len(scenarios),
        "years_count": len(years),
        "message": "Analysis task queued. Use task_id to poll results. "
        "(Note: Async processing not yet implemented - this is a mock response)",
    }


@router.get("/municipalities")
async def list_municipalities():
    """
    List all municipalities available in the database

    Returns basic info for all municipalities with risk data.

    **Example:**
    ```
    GET /api/v1/risk/municipalities
    ```

    **Returns:**
    ```json
    {
        "total": 10,
        "municipalities": [
            {
                "ibge_code": "3550308",
                "name": "São Paulo",
                "state": "SP",
                "population": 11451245
            },
            ...
        ]
    }
    ```
    """
    all_munis = get_all_municipalities()

    municipalities_list = [
        {
            "ibge_code": ibge_code,
            "name": data["name"],
            "state": data["state"],
            "state_name": data["state_name"],
            "population": data["population"],
            "lat": data["lat"],
            "lon": data["lon"],
        }
        for ibge_code, data in all_munis.items()
    ]

    # Ordenar por população (maior primeiro)
    municipalities_list.sort(key=lambda x: x["population"], reverse=True)

    return {
        "total": len(municipalities_list),
        "municipalities": municipalities_list,
    }


@router.get("/municipalities/{ibge_code}/info")
async def get_municipality_info(ibge_code: str):
    """
    Get detailed information about a municipality

    Returns demographic, geographic, and infrastructure data.

    **Example:**
    ```
    GET /api/v1/risk/municipalities/3550308/info
    ```
    """
    muni_data = get_municipality_data(ibge_code)
    if not muni_data:
        raise HTTPException(
            status_code=404,
            detail=f"Municipality {ibge_code} not found",
        )

    return {
        "ibge_code": ibge_code,
        **muni_data,
    }
