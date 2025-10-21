"""
PÚRPURA Physical Risk Calculator
Simplified wrapper around physrisk-lib + Brazilian climate data sources
"""
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
import logging
import os

logger = logging.getLogger(__name__)

# Import Brazilian API clients
try:
    from backend.integrations.inpe_client import INPEClient
    from backend.integrations.ana_client import ANAClient
    APIS_AVAILABLE = True
except ImportError:
    logger.warning("Brazilian API clients not available - using mock mode only")
    APIS_AVAILABLE = False


class RiskScenario(str, Enum):
    """Climate scenarios (IPCC SSP/RCP)"""
    SSP126 = "ssp126"  # Low emissions (replaces RCP2.6)
    SSP245 = "ssp245"  # Moderate emissions (replaces RCP4.5)
    SSP585 = "ssp585"  # High emissions (replaces RCP8.5)


class HazardType(str, Enum):
    """Physical climate hazards"""
    FLOOD = "flood"
    DROUGHT = "drought"
    HEAT_STRESS = "heat_stress"
    LANDSLIDE = "landslide"
    COASTAL_INUNDATION = "coastal_inundation"


@dataclass
class HazardResult:
    """Result of hazard calculation"""
    hazard_type: HazardType
    current_risk: float  # 0.0 to 1.0
    projected_2030: float
    projected_2050: float
    confidence: float  # 0.0 to 1.0
    data_source: str
    raw_value: Optional[float] = None
    unit: Optional[str] = None


@dataclass
class LocationRisk:
    """Complete risk assessment for a location"""
    latitude: float
    longitude: float
    ibge_code: Optional[str]
    municipality_name: Optional[str]
    scenario: RiskScenario
    hazards: List[HazardResult]
    overall_risk_score: float


class BrazilianClimateData:
    """
    Adapter for Brazilian climate data sources
    Integrates with:
    - INPE: Climate projections and temperature data
    - ANA: Hydrological data and flood risk
    - Cemaden: TODO - no public API available yet
    """

    def __init__(self, use_real_apis: bool = True):
        """
        Initialize Brazilian data adapter

        Args:
            use_real_apis: Whether to use real APIs (with fallback to mock)
        """
        self.use_real_apis = use_real_apis and APIS_AVAILABLE

        # Initialize API clients
        if self.use_real_apis:
            try:
                self.inpe_client = INPEClient()
                self.ana_client = ANAClient()
                logger.info("✅ Brazilian API clients initialized (INPE + ANA)")
            except Exception as e:
                logger.warning(f"Failed to initialize API clients: {e}. Falling back to mock mode.")
                self.use_real_apis = False
        else:
            logger.info("BrazilianClimateData initialized (mock mode)")

    def get_flood_risk(
        self,
        latitude: float,
        longitude: float,
        scenario: RiskScenario,
        year: int
    ) -> HazardResult:
        """
        Get flood risk from ANA hydrological data

        Uses:
        1. ANA telemetric stations for recent rainfall
        2. Climate projections to adjust future risk
        """
        if self.use_real_apis:
            try:
                # Find nearest ANA station
                station = self.ana_client.find_nearest_station(latitude, longitude)

                if station:
                    # Get current flood risk from rainfall data
                    current_risk = self.ana_client.get_flood_risk_from_rainfall(
                        station.code, days=30
                    )

                    # Apply climate change multipliers based on scenario
                    scenario_multipliers = {
                        RiskScenario.SSP126: {2030: 1.1, 2050: 1.2},
                        RiskScenario.SSP245: {2030: 1.2, 2050: 1.5},
                        RiskScenario.SSP585: {2030: 1.3, 2050: 1.8},
                    }

                    multiplier_2030 = scenario_multipliers.get(scenario, {}).get(2030, 1.2)
                    multiplier_2050 = scenario_multipliers.get(scenario, {}).get(2050, 1.5)

                    logger.info(f"✅ Flood risk from ANA station {station.code}: {current_risk}")

                    return HazardResult(
                        hazard_type=HazardType.FLOOD,
                        current_risk=current_risk,
                        projected_2030=min(current_risk * multiplier_2030, 1.0),
                        projected_2050=min(current_risk * multiplier_2050, 1.0),
                        confidence=0.7,
                        data_source=f"ANA_{station.code}",
                        unit="risk_score"
                    )
            except Exception as e:
                logger.warning(f"ANA API failed: {e}. Using mock data.")

        # Fallback to mock data
        base_risk = 0.3 if latitude > -24 else 0.4

        return HazardResult(
            hazard_type=HazardType.FLOOD,
            current_risk=base_risk,
            projected_2030=base_risk * 1.2,
            projected_2050=base_risk * 1.5,
            confidence=0.6,
            data_source="mock_ana",
            unit="probability"
        )

    def get_drought_risk(
        self,
        latitude: float,
        longitude: float,
        scenario: RiskScenario,
        year: int
    ) -> HazardResult:
        """
        Get drought risk from INPE climate projections

        Uses INPE precipitation projections to estimate drought risk
        """
        if self.use_real_apis:
            try:
                # Map scenario names (SSP -> RCP for INPE)
                scenario_map = {
                    RiskScenario.SSP126: 'rcp26',
                    RiskScenario.SSP245: 'rcp45',
                    RiskScenario.SSP585: 'rcp85',
                }
                rcp_scenario = scenario_map.get(scenario, 'rcp45')

                # Get drought risk from INPE
                current_risk = self.inpe_client.get_drought_risk_projection(
                    latitude, longitude, rcp_scenario, 2024
                )
                risk_2030 = self.inpe_client.get_drought_risk_projection(
                    latitude, longitude, rcp_scenario, 2030
                )
                risk_2050 = self.inpe_client.get_drought_risk_projection(
                    latitude, longitude, rcp_scenario, 2050
                )

                logger.info(f"✅ Drought risk from INPE: {current_risk} → {risk_2050}")

                return HazardResult(
                    hazard_type=HazardType.DROUGHT,
                    current_risk=current_risk,
                    projected_2030=risk_2030,
                    projected_2050=risk_2050,
                    confidence=0.75,
                    data_source="INPE",
                    unit="risk_score"
                )
            except Exception as e:
                logger.warning(f"INPE API failed: {e}. Using mock data.")

        # Fallback to mock data
        base_risk = 0.5 if latitude > -10 else 0.2

        return HazardResult(
            hazard_type=HazardType.DROUGHT,
            current_risk=base_risk,
            projected_2030=base_risk * 1.3,
            projected_2050=base_risk * 1.6,
            confidence=0.7,
            data_source="mock_inpe",
            unit="severity_index"
        )

    def get_heat_stress_risk(
        self,
        latitude: float,
        longitude: float,
        scenario: RiskScenario,
        year: int
    ) -> HazardResult:
        """
        Get heat stress risk from INPE temperature projections

        Uses INPE climate models to project temperature increases
        """
        if self.use_real_apis:
            try:
                # Map scenario names (SSP -> RCP for INPE)
                scenario_map = {
                    RiskScenario.SSP126: 'rcp26',
                    RiskScenario.SSP245: 'rcp45',
                    RiskScenario.SSP585: 'rcp85',
                }
                rcp_scenario = scenario_map.get(scenario, 'rcp45')

                # Get heat stress risk from INPE
                current_risk = self.inpe_client.get_heat_stress_projection(
                    latitude, longitude, rcp_scenario, 2024
                )
                risk_2030 = self.inpe_client.get_heat_stress_projection(
                    latitude, longitude, rcp_scenario, 2030
                )
                risk_2050 = self.inpe_client.get_heat_stress_projection(
                    latitude, longitude, rcp_scenario, 2050
                )

                logger.info(f"✅ Heat stress risk from INPE: {current_risk} → {risk_2050}")

                return HazardResult(
                    hazard_type=HazardType.HEAT_STRESS,
                    current_risk=current_risk,
                    projected_2030=risk_2030,
                    projected_2050=risk_2050,
                    confidence=0.85,
                    data_source="INPE",
                    unit="risk_score"
                )
            except Exception as e:
                logger.warning(f"INPE API failed: {e}. Using mock data.")

        # Fallback to mock data
        base_risk = 0.6 if latitude > -15 else 0.3

        return HazardResult(
            hazard_type=HazardType.HEAT_STRESS,
            current_risk=base_risk,
            projected_2030=base_risk * 1.4,
            projected_2050=base_risk * 2.0,
            confidence=0.8,
            data_source="mock_inpe",
            raw_value=35.5,
            unit="degrees_celsius"
        )


class RiskCalculator:
    """
    Main risk calculator combining physrisk-lib + Brazilian data
    """

    def __init__(self, use_brazilian_data: bool = True):
        """
        Initialize risk calculator

        Args:
            use_brazilian_data: Use Brazilian data sources (Cemaden, INPE, ANA)
        """
        self.use_brazilian_data = use_brazilian_data

        if use_brazilian_data:
            self.brazilian_data = BrazilianClimateData()
            logger.info("✓ Brazilian climate data adapter initialized")
        else:
            self.brazilian_data = None
            logger.info("Using physrisk-lib default data only")

        # TODO: Initialize physrisk-lib model when needed
        self.physrisk_model = None

    def calculate_location_risk(
        self,
        latitude: float,
        longitude: float,
        scenario: RiskScenario = RiskScenario.SSP245,
        ibge_code: Optional[str] = None,
        municipality_name: Optional[str] = None
    ) -> LocationRisk:
        """
        Calculate comprehensive climate risk for a location

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            scenario: Climate scenario (SSP1-2.6, SSP2-4.5, SSP5-8.5)
            ibge_code: IBGE municipality code (7 digits)
            municipality_name: Municipality name

        Returns:
            LocationRisk with hazard assessments
        """
        logger.info(f"Calculating risk for ({latitude}, {longitude})")

        hazards = []

        if self.brazilian_data:
            # Use Brazilian data sources
            hazards.append(self.brazilian_data.get_flood_risk(
                latitude, longitude, scenario, 2050
            ))
            hazards.append(self.brazilian_data.get_drought_risk(
                latitude, longitude, scenario, 2050
            ))
            hazards.append(self.brazilian_data.get_heat_stress_risk(
                latitude, longitude, scenario, 2050
            ))
        else:
            # TODO: Use physrisk-lib for global data
            pass

        # Calculate overall risk score (weighted average)
        if hazards:
            weights = {
                HazardType.FLOOD: 0.4,
                HazardType.DROUGHT: 0.3,
                HazardType.HEAT_STRESS: 0.2,
                HazardType.LANDSLIDE: 0.05,
                HazardType.COASTAL_INUNDATION: 0.05
            }

            total_weight = 0.0
            weighted_sum = 0.0

            for hazard in hazards:
                weight = weights.get(hazard.hazard_type, 0.1)
                weighted_sum += hazard.projected_2050 * weight
                total_weight += weight

            overall_risk = weighted_sum / total_weight if total_weight > 0 else 0.0
        else:
            overall_risk = 0.0

        return LocationRisk(
            latitude=latitude,
            longitude=longitude,
            ibge_code=ibge_code,
            municipality_name=municipality_name,
            scenario=scenario,
            hazards=hazards,
            overall_risk_score=overall_risk
        )

    def calculate_municipality_risk(
        self,
        ibge_code: str,
        scenario: RiskScenario = RiskScenario.SSP245
    ) -> LocationRisk:
        """
        Calculate risk for a Brazilian municipality

        Args:
            ibge_code: IBGE 7-digit municipality code
            scenario: Climate scenario

        Returns:
            LocationRisk for municipality centroid
        """
        # TODO: Query IBGE API for municipality centroid
        # For now, using hardcoded coordinates for major cities

        city_coords = {
            "3550308": (-23.5505, -46.6333, "São Paulo"),
            "3304557": (-22.9068, -43.1729, "Rio de Janeiro"),
            "2927408": (-12.9714, -38.5014, "Salvador"),
            "5300108": (-15.7801, -47.9292, "Brasília"),
            "4106902": (-25.4284, -49.2733, "Curitiba"),
        }

        if ibge_code in city_coords:
            lat, lng, name = city_coords[ibge_code]
        else:
            logger.warning(f"IBGE code {ibge_code} not in hardcoded list")
            # Default to São Paulo
            lat, lng, name = -23.5505, -46.6333, f"Municipality {ibge_code}"

        return self.calculate_location_risk(
            latitude=lat,
            longitude=lng,
            scenario=scenario,
            ibge_code=ibge_code,
            municipality_name=name
        )


# Convenience functions
def calculate_municipal_risk(
    ibge_code: str,
    scenario: RiskScenario = RiskScenario.SSP245
) -> LocationRisk:
    """Quick municipal risk calculation"""
    calculator = RiskCalculator(use_brazilian_data=True)
    return calculator.calculate_municipality_risk(ibge_code, scenario)


def calculate_location_risk(
    latitude: float,
    longitude: float,
    scenario: RiskScenario = RiskScenario.SSP245
) -> LocationRisk:
    """Quick location risk calculation"""
    calculator = RiskCalculator(use_brazilian_data=True)
    return calculator.calculate_location_risk(latitude, longitude, scenario)
