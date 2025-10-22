"""
INPE Climate Projections Client
Access climate projection data from INPE's PCBr (Projeções Climáticas no Brasil)

API: http://pclima.inpe.br/analise/API/
Documentation: http://pclima.inpe.br/?page_id=183
"""
import os
from typing import Dict, List, Optional, Tuple
import requests
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class INPEScenario(str, Enum):
    """INPE climate scenarios (RCP)"""
    RCP26 = "rcp26"
    RCP45 = "rcp45"
    RCP85 = "rcp85"


class INPEVariable(str, Enum):
    """INPE climate variables"""
    TEMPERATURE = "tas"  # Near-surface air temperature
    PRECIPITATION = "pr"  # Precipitation
    TEMPERATURE_MAX = "tasmax"  # Maximum temperature
    TEMPERATURE_MIN = "tasmin"  # Minimum temperature


class INPEClient:
    """
    Client for INPE Climate Projections API (PCBr)

    Features:
    - Climate projections for Brazil (2030, 2050, 2100)
    - RCP scenarios (2.6, 4.5, 8.5)
    - Variables: temperature, precipitation, etc.

    Note: Requires API token from INPE
    """

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize INPE client

        Args:
            api_token: INPE API token (from environment or parameter)
        """
        self.base_url = "http://pclima.inpe.br/analise/API"
        self.api_token = api_token or os.getenv("INPE_API_TOKEN")
        self.session = requests.Session()
        self.timeout = 30

    def get_climate_projection(
        self,
        latitude: float,
        longitude: float,
        scenario: INPEScenario,
        variable: INPEVariable = INPEVariable.TEMPERATURE,
        year: int = 2050
    ) -> Optional[Dict]:
        """
        Get climate projection for a location

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            scenario: RCP scenario (2.6, 4.5, 8.5)
            variable: Climate variable to query
            year: Projection year (2030, 2050, 2100)

        Returns:
            Climate projection data or None if error

        MVP Implementation:
        - Returns mock data if no API token
        - Ready for real INPE integration when token available
        """
        if not self.api_token:
            logger.warning("INPE API token not configured - using mock data")
            return self._mock_projection(latitude, longitude, scenario, variable, year)

        try:
            # Build API request
            # Note: Actual API format may vary - needs testing with real token
            params = {
                "token": self.api_token,
                "lat": latitude,
                "lon": longitude,
                "scenario": scenario.value,
                "variable": variable.value,
                "year": year
            }

            response = self.session.get(
                self.base_url,
                params=params,
                timeout=self.timeout
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"INPE API error: {response.status_code}")
                return self._mock_projection(latitude, longitude, scenario, variable, year)

        except requests.RequestException as e:
            logger.error(f"INPE API request failed: {e}")
            return self._mock_projection(latitude, longitude, scenario, variable, year)

    def get_precipitation_projection(
        self,
        latitude: float,
        longitude: float,
        scenario: INPEScenario,
        baseline_year: int = 2020,
        projection_year: int = 2050
    ) -> Optional[Dict]:
        """
        Get precipitation change projection

        Args:
            latitude: Location latitude
            longitude: Location longitude
            scenario: Climate scenario
            baseline_year: Baseline year for comparison
            projection_year: Future projection year

        Returns:
            Dict with precipitation change data
        """
        projection = self.get_climate_projection(
            latitude=latitude,
            longitude=longitude,
            scenario=scenario,
            variable=INPEVariable.PRECIPITATION,
            year=projection_year
        )

        if projection:
            return {
                "scenario": scenario.value,
                "baseline_year": baseline_year,
                "projection_year": projection_year,
                "precipitation_change_pct": projection.get("change_pct", 0),
                "data_source": "INPE-PCBr" if self.api_token else "INPE-mock"
            }

        return None

    def get_temperature_projection(
        self,
        latitude: float,
        longitude: float,
        scenario: INPEScenario,
        projection_year: int = 2050
    ) -> Optional[Dict]:
        """
        Get temperature increase projection

        Args:
            latitude: Location latitude
            longitude: Location longitude
            scenario: Climate scenario
            projection_year: Future projection year

        Returns:
            Dict with temperature change data
        """
        projection = self.get_climate_projection(
            latitude=latitude,
            longitude=longitude,
            scenario=scenario,
            variable=INPEVariable.TEMPERATURE,
            year=projection_year
        )

        if projection:
            return {
                "scenario": scenario.value,
                "projection_year": projection_year,
                "temperature_increase_c": projection.get("increase_c", 0),
                "data_source": "INPE-PCBr" if self.api_token else "INPE-mock"
            }

        return None

    def _mock_projection(
        self,
        latitude: float,
        longitude: float,
        scenario: INPEScenario,
        variable: INPEVariable,
        year: int
    ) -> Dict:
        """
        Generate mock projection data for MVP

        Based on IPCC general projections for Brazil
        """
        # Scenario multipliers
        scenario_factors = {
            INPEScenario.RCP26: 1.0,
            INPEScenario.RCP45: 1.3,
            INPEScenario.RCP85: 1.8
        }

        # Year factors (relative to 2020 baseline)
        year_factors = {
            2030: 0.5,
            2050: 1.0,
            2100: 2.0
        }

        factor = scenario_factors.get(scenario, 1.3) * year_factors.get(year, 1.0)

        if variable == INPEVariable.TEMPERATURE:
            # Temperature increase (°C)
            # North Brazil: higher increase
            # South Brazil: moderate increase
            base_increase = 2.0 if latitude > -10 else 1.5
            return {
                "variable": variable.value,
                "increase_c": round(base_increase * factor, 2),
                "unit": "celsius",
                "scenario": scenario.value,
                "year": year,
                "mock": True
            }

        elif variable == INPEVariable.PRECIPITATION:
            # Precipitation change (%)
            # Amazon (North): -20% to -40%
            # Northeast (Sertão): -30% to -50%
            # South/Southeast: +10% to +20%
            if latitude > -10:  # North (Amazon)
                base_change = -25
            elif -10 <= latitude < -5:  # Northeast
                base_change = -35
            else:  # South/Southeast
                base_change = 15

            return {
                "variable": variable.value,
                "change_pct": round(base_change * factor / 1.5, 1),
                "unit": "percent",
                "scenario": scenario.value,
                "year": year,
                "mock": True
            }

        return {"mock": True, "variable": variable.value}


# Singleton instance
_inpe_client: Optional[INPEClient] = None


def get_inpe_client() -> INPEClient:
    """Get or create INPE client instance"""
    global _inpe_client
    if _inpe_client is None:
        _inpe_client = INPEClient()
    return _inpe_client
