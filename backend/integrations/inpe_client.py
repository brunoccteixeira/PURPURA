"""
INPE (Instituto Nacional de Pesquisas Espaciais) Climate Projections API Client

API Documentation: http://pclima.inpe.br/analise/API/
Platform: Projeções Climáticas no Brasil
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx
from dataclasses import dataclass

from .cache import cache_response, get_cache
from .retry import retry_with_backoff, RetryConfig, CircuitBreaker

logger = logging.getLogger(__name__)


@dataclass
class ClimateProjection:
    """Climate projection data"""
    latitude: float
    longitude: float
    variable: str  # 'temperature', 'precipitation', etc.
    scenario: str  # 'rcp26', 'rcp45', 'rcp85'
    time_period: str  # '2030', '2050', '2070', '2100'
    value: float
    unit: str
    model: str
    data_source: str = "INPE"


class INPEClient:
    """
    Client for INPE Climate Projections API

    Provides access to climate change projections for Brazil including:
    - Temperature increases
    - Precipitation changes
    - Extreme events (heat waves, droughts)
    - Multi-model ensembles
    """

    BASE_URL = "http://pclima.inpe.br/analise/API"
    TIMEOUT = 30.0
    CACHE_TTL = 3600  # 1 hour cache for climate projections

    # Scenario mapping: our internal names -> INPE names
    SCENARIO_MAP = {
        'rcp26': 'RCP2.6',
        'rcp45': 'RCP4.5',
        'rcp85': 'RCP8.5',
    }

    # Variable mapping
    VARIABLE_MAP = {
        'temperature': 'tas',  # near-surface air temperature
        'precipitation': 'pr',  # precipitation
        'tmax': 'tasmax',  # maximum temperature
        'tmin': 'tasmin',  # minimum temperature
    }

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize INPE client

        Args:
            api_key: Optional API key (if required in the future)
        """
        self.api_key = api_key or os.getenv('INPE_API_KEY')

        # Use connection pooling for better performance
        limits = httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10,
            keepalive_expiry=30.0
        )

        self.client = httpx.Client(
            timeout=self.TIMEOUT,
            limits=limits,
            http2=True  # Enable HTTP/2 for better performance
        )

        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0
        )

        logger.info("INPE Client initialized with connection pooling and circuit breaker")

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'client'):
            self.client.close()

    async def get_climate_projection(
        self,
        latitude: float,
        longitude: float,
        variable: str = 'temperature',
        scenario: str = 'rcp45',
        time_period: str = '2050'
    ) -> Optional[ClimateProjection]:
        """
        Get climate projection for a specific location

        Args:
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            variable: Climate variable ('temperature', 'precipitation', etc.)
            scenario: Climate scenario ('rcp26', 'rcp45', 'rcp85')
            time_period: Time period ('2030', '2050', '2070', '2100')

        Returns:
            ClimateProjection object or None if unavailable
        """
        try:
            # Map to INPE variable names
            inpe_variable = self.VARIABLE_MAP.get(variable, variable)
            inpe_scenario = self.SCENARIO_MAP.get(scenario, scenario)

            # Build API request (placeholder structure - needs refinement based on actual API)
            params = {
                'lat': latitude,
                'lon': longitude,
                'variable': inpe_variable,
                'scenario': inpe_scenario,
                'period': time_period,
            }

            logger.info(f"Requesting INPE projection: {params}")

            # TODO: Make actual API request when endpoint is accessible
            # response = self.client.get(f"{self.BASE_URL}/projection", params=params)
            # response.raise_for_status()
            # data = response.json()

            # For now, return mock data with realistic values based on IPCC reports
            return self._get_mock_projection(
                latitude, longitude, variable, scenario, time_period
            )

        except Exception as e:
            logger.error(f"Error fetching INPE projection: {e}")
            return None

    def _get_mock_projection(
        self,
        latitude: float,
        longitude: float,
        variable: str,
        scenario: str,
        time_period: str
    ) -> ClimateProjection:
        """
        Generate mock projection data based on IPCC AR6 Brazil projections

        Realistic estimates for Brazil:
        - Temperature: +1.5°C to +5°C by 2100 depending on scenario
        - Precipitation: -20% to +20% changes regionally
        """
        # Base scenario multipliers (compared to current)
        scenario_multipliers = {
            'rcp26': {'2030': 0.3, '2050': 0.5, '2070': 0.6, '2100': 0.7},
            'rcp45': {'2030': 0.4, '2050': 0.7, '2070': 1.0, '2100': 1.3},
            'rcp85': {'2030': 0.5, '2050': 1.2, '2070': 2.0, '2100': 3.0},
        }

        multiplier = scenario_multipliers.get(scenario, {}).get(time_period, 1.0)

        if variable == 'temperature':
            # Temperature increase in °C
            value = 1.5 * multiplier
            unit = '°C'
        elif variable == 'precipitation':
            # Precipitation change in %
            # Brazil varies: Amazon may get wetter, Northeast drier
            # Simplified: slight decrease on average
            value = -5 * multiplier if latitude < -10 else -10 * multiplier
            unit = '%'
        else:
            value = 0.0
            unit = 'unknown'

        return ClimateProjection(
            latitude=latitude,
            longitude=longitude,
            variable=variable,
            scenario=scenario,
            time_period=time_period,
            value=round(value, 2),
            unit=unit,
            model='INPE-Eta_HadGEM2-ES',  # Common model used in Brazil
            data_source='INPE (mock)'
        )

    @cache_response(ttl=3600, key_prefix="inpe_heat", source="INPE")
    def get_heat_stress_projection(
        self,
        latitude: float,
        longitude: float,
        scenario: str = 'rcp45',
        year: int = 2050
    ) -> float:
        """
        Get heat stress risk projection (0-1 scale)

        Based on projected temperature increases and frequency of extreme heat days

        NOTE: Cached for 1 hour
        """
        projection = self._get_mock_projection(
            latitude, longitude, 'temperature', scenario, str(year)
        )

        if not projection:
            return 0.3  # fallback

        # Convert temperature increase to risk score
        # +1°C = 0.2 risk, +2°C = 0.4, +3°C = 0.6, +4°C = 0.8, +5°C = 1.0
        temp_increase = projection.value
        risk = min(temp_increase / 5.0, 1.0)

        return round(risk, 3)

    @cache_response(ttl=3600, key_prefix="inpe_drought", source="INPE")
    def get_drought_risk_projection(
        self,
        latitude: float,
        longitude: float,
        scenario: str = 'rcp45',
        year: int = 2050
    ) -> float:
        """
        Get drought risk projection (0-1 scale)

        Based on projected precipitation changes

        NOTE: Cached for 1 hour
        """
        projection = self._get_mock_projection(
            latitude, longitude, 'precipitation', scenario, str(year)
        )

        if not projection:
            return 0.2  # fallback

        # Convert precipitation change to drought risk
        # -10% = 0.3 risk, -20% = 0.5, -30% = 0.7, -40% = 0.9
        precip_change = projection.value

        if precip_change >= 0:
            risk = 0.1  # low risk if precipitation increases
        else:
            risk = min(abs(precip_change) / 40.0, 1.0)

        return round(risk, 3)

    @retry_with_backoff(
        RetryConfig(max_attempts=2, initial_delay=0.5, retriable_exceptions=(Exception,)),
        log_attempts=False
    )
    def health_check(self) -> Dict[str, Any]:
        """
        Check if INPE API is accessible

        Returns:
            Dictionary with status information
        """
        try:
            # Try to ping the main portal
            response = self.client.get("http://pclima.inpe.br", timeout=5.0)

            # Get cache stats
            cache_stats = get_cache().stats()

            return {
                'service': 'INPE',
                'status': 'available' if response.status_code == 200 else 'degraded',
                'response_time_ms': round(response.elapsed.total_seconds() * 1000, 2),
                'circuit_breaker_state': self.circuit_breaker.state,
                'cache_stats': cache_stats,
                'timestamp': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.warning(f"INPE health check failed: {e}")
            return {
                'service': 'INPE',
                'status': 'unavailable',
                'error': str(e),
                'circuit_breaker_state': self.circuit_breaker.state,
                'timestamp': datetime.utcnow().isoformat(),
            }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    client = INPEClient()

    # Test São Paulo
    lat, lon = -23.5505, -46.6333

    print(f"\n🌡️ Climate projections for São Paulo ({lat}, {lon}):")

    for scenario in ['rcp26', 'rcp45', 'rcp85']:
        for year in ['2030', '2050']:
            temp_proj = client._get_mock_projection(lat, lon, 'temperature', scenario, year)
            print(f"  {scenario.upper()} {year}: +{temp_proj.value}{temp_proj.unit}")

    print(f"\n🔥 Heat stress risk 2050 (RCP4.5): {client.get_heat_stress_projection(lat, lon)}")
    print(f"☀️ Drought risk 2050 (RCP4.5): {client.get_drought_risk_projection(lat, lon)}")

    print(f"\n✅ Health check: {client.health_check()}")
