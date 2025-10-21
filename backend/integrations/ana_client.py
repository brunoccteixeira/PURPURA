"""
ANA (Agência Nacional de Águas e Saneamento Básico) API Client

API Documentation:
- New Service: https://www.ana.gov.br/hidrowebservice/swagger-ui.html
- Legacy Service: http://telemetriaws1.ana.gov.br/ServiceANA.asmx
- Portal: https://dadosabertos.ana.gov.br/
"""

import os
import logging
from typing import Optional, Dict, Any, List
from datetime import datetime, timedelta
import httpx
from dataclasses import dataclass
import xml.etree.ElementTree as ET

from .cache import cache_response, get_cache
from .retry import retry_with_backoff, RetryConfig, CircuitBreaker

logger = logging.getLogger(__name__)


@dataclass
class TelemetricStation:
    """Telemetric station data"""
    code: str
    name: str
    latitude: float
    longitude: float
    river: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    basin: Optional[str] = None


@dataclass
class HydrologicalData:
    """Hydrological measurement data"""
    station_code: str
    timestamp: datetime
    variable: str  # 'rainfall', 'river_level', 'flow'
    value: float
    unit: str
    data_source: str = "ANA"


class ANAClient:
    """
    Client for ANA (Agência Nacional de Águas) APIs

    Provides access to:
    - Telemetric station data (rainfall, river levels, flow)
    - Historical hydrological series
    - Real-time water monitoring
    - Reservoir levels
    """

    # Legacy SOAP Web Service (active until June 2026)
    LEGACY_BASE_URL = "http://telemetriaws1.ana.gov.br/ServiceANA.asmx"

    # New REST API (OAuth required)
    REST_BASE_URL = "https://www.ana.gov.br/hidrowebservice"

    TIMEOUT = 30.0

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize ANA client

        Args:
            api_token: OAuth token for new REST API (optional)
        """
        self.api_token = api_token or os.getenv('ANA_API_TOKEN')

        # Use connection pooling
        limits = httpx.Limits(
            max_keepalive_connections=5,
            max_connections=10,
            keepalive_expiry=30.0
        )

        self.client = httpx.Client(
            timeout=self.TIMEOUT,
            limits=limits,
            http2=True
        )

        # Initialize circuit breaker
        self.circuit_breaker = CircuitBreaker(
            failure_threshold=3,
            recovery_timeout=60.0
        )

        logger.info("ANA Client initialized with connection pooling and circuit breaker")

    def __del__(self):
        """Cleanup"""
        if hasattr(self, 'client'):
            self.client.close()

    def get_telemetric_stations(
        self,
        state: Optional[str] = None,
        basin: Optional[str] = None
    ) -> List[TelemetricStation]:
        """
        Get list of telemetric stations

        Args:
            state: Filter by state (e.g., 'SP', 'RJ')
            basin: Filter by hydrographic basin

        Returns:
            List of TelemetricStation objects
        """
        try:
            # Use legacy SOAP service
            url = f"{self.LEGACY_BASE_URL}/ListaEstacoesTelemetricas"

            params = {}
            if state:
                params['estado'] = state

            logger.info(f"Requesting ANA telemetric stations: {params}")

            # TODO: Make actual API request
            # response = self.client.get(url, params=params)
            # response.raise_for_status()
            # stations = self._parse_stations_xml(response.text)

            # For now, return mock stations for major Brazilian cities
            return self._get_mock_stations(state)

        except Exception as e:
            logger.error(f"Error fetching ANA stations: {e}")
            return []

    def _get_mock_stations(self, state: Optional[str] = None) -> List[TelemetricStation]:
        """Generate mock telemetric stations for testing"""
        all_stations = [
            TelemetricStation(
                code='58001000',
                name='São Paulo - Tietê',
                latitude=-23.5505,
                longitude=-46.6333,
                river='Tietê',
                city='São Paulo',
                state='SP',
                basin='Alto Tietê'
            ),
            TelemetricStation(
                code='60491000',
                name='Brasília - Paranoá',
                latitude=-15.7801,
                longitude=-47.9292,
                river='Paranoá',
                city='Brasília',
                state='DF',
                basin='Paranoá'
            ),
            TelemetricStation(
                code='62755000',
                name='Rio de Janeiro - Guandu',
                latitude=-22.9068,
                longitude=-43.1729,
                river='Guandu',
                city='Rio de Janeiro',
                state='RJ',
                basin='Guandu'
            ),
        ]

        if state:
            return [s for s in all_stations if s.state == state]

        return all_stations

    def get_rainfall_data(
        self,
        station_code: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> List[HydrologicalData]:
        """
        Get rainfall data from a telemetric station

        Args:
            station_code: Station code
            start_date: Start date (defaults to 7 days ago)
            end_date: End date (defaults to today)

        Returns:
            List of HydrologicalData objects
        """
        if not start_date:
            start_date = datetime.now() - timedelta(days=7)
        if not end_date:
            end_date = datetime.now()

        try:
            logger.info(f"Requesting rainfall data for station {station_code}")

            # TODO: Make actual API request
            # Use HidroSerieHistorica from legacy API or new REST endpoint

            # For now, return mock data
            return self._get_mock_rainfall_data(station_code, start_date, end_date)

        except Exception as e:
            logger.error(f"Error fetching rainfall data: {e}")
            return []

    def _get_mock_rainfall_data(
        self,
        station_code: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[HydrologicalData]:
        """Generate mock rainfall data"""
        data = []

        # Generate daily rainfall (mm)
        current_date = start_date
        while current_date <= end_date:
            # Simulate realistic rainfall patterns
            import random
            rainfall_mm = random.uniform(0, 50) if random.random() > 0.3 else 0

            data.append(HydrologicalData(
                station_code=station_code,
                timestamp=current_date,
                variable='rainfall',
                value=round(rainfall_mm, 1),
                unit='mm',
                data_source='ANA (mock)'
            ))

            current_date += timedelta(days=1)

        return data

    @cache_response(ttl=600, key_prefix="ana_flood", source="ANA")  # 10 min cache for rainfall
    def get_flood_risk_from_rainfall(
        self,
        station_code: str,
        days: int = 7
    ) -> float:
        """
        Calculate flood risk based on recent rainfall accumulation

        Args:
            station_code: Station code
            days: Number of days to analyze

        Returns:
            Flood risk score (0-1)

        NOTE: Cached for 10 minutes
        """
        try:
            end_date = datetime.now()
            start_date = end_date - timedelta(days=days)

            rainfall_data = self.get_rainfall_data(station_code, start_date, end_date)

            if not rainfall_data:
                return 0.3  # default moderate risk

            # Calculate accumulated rainfall
            total_rainfall = sum(d.value for d in rainfall_data)

            # Flood risk thresholds (accumulated mm over period)
            # These are simplified - real thresholds vary by region
            if total_rainfall < 100:
                risk = 0.2  # low risk
            elif total_rainfall < 200:
                risk = 0.4  # moderate risk
            elif total_rainfall < 300:
                risk = 0.6  # high risk
            else:
                risk = 0.8  # critical risk

            logger.info(f"Station {station_code}: {total_rainfall}mm over {days} days = {risk} flood risk")

            return round(risk, 3)

        except Exception as e:
            logger.error(f"Error calculating flood risk: {e}")
            return 0.3

    def get_river_level(self, station_code: str) -> Optional[float]:
        """
        Get current river level

        Args:
            station_code: Station code

        Returns:
            River level in meters or None
        """
        try:
            # TODO: Call real-time telemetry endpoint
            # return self._fetch_latest_telemetry(station_code, 'river_level')

            # Mock: random river level between 1-5 meters
            import random
            return round(random.uniform(1.5, 4.5), 2)

        except Exception as e:
            logger.error(f"Error fetching river level: {e}")
            return None

    def find_nearest_station(
        self,
        latitude: float,
        longitude: float,
        max_distance_km: float = 50
    ) -> Optional[TelemetricStation]:
        """
        Find nearest telemetric station to a location

        Args:
            latitude: Latitude
            longitude: Longitude
            max_distance_km: Maximum search distance in km

        Returns:
            Nearest TelemetricStation or None
        """
        stations = self.get_telemetric_stations()

        if not stations:
            return None

        # Calculate distances using haversine formula
        def haversine_distance(lat1, lon1, lat2, lon2):
            """Calculate distance in km"""
            from math import radians, sin, cos, sqrt, atan2

            R = 6371  # Earth radius in km

            lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
            dlat = lat2 - lat1
            dlon = lon2 - lon1

            a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
            c = 2 * atan2(sqrt(a), sqrt(1-a))

            return R * c

        # Find nearest
        nearest = None
        min_distance = float('inf')

        for station in stations:
            distance = haversine_distance(
                latitude, longitude,
                station.latitude, station.longitude
            )

            if distance < min_distance and distance <= max_distance_km:
                min_distance = distance
                nearest = station

        if nearest:
            logger.info(f"Nearest station: {nearest.name} ({min_distance:.1f} km away)")

        return nearest

    def health_check(self) -> Dict[str, Any]:
        """
        Check if ANA API is accessible

        Returns:
            Dictionary with status information
        """
        try:
            # Try to access legacy SOAP service
            response = self.client.get(f"{self.LEGACY_BASE_URL}?op=ListaEstacoesTelemetricas", timeout=5.0)

            return {
                'service': 'ANA',
                'status': 'available' if response.status_code == 200 else 'degraded',
                'endpoint': 'legacy_soap',
                'response_time_ms': response.elapsed.total_seconds() * 1000,
                'timestamp': datetime.utcnow().isoformat(),
            }
        except Exception as e:
            logger.warning(f"ANA health check failed: {e}")
            return {
                'service': 'ANA',
                'status': 'unavailable',
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat(),
            }


# Example usage
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    client = ANAClient()

    print("\n💧 ANA Telemetric Stations:")
    stations = client.get_telemetric_stations(state='SP')
    for station in stations:
        print(f"  {station.code} - {station.name} ({station.city}/{station.state})")

    print("\n🌧️ Rainfall data (last 7 days):")
    if stations:
        rainfall = client.get_rainfall_data(stations[0].code)
        total = sum(d.value for d in rainfall)
        print(f"  Station {stations[0].code}: {total:.1f}mm accumulated")

    print("\n🌊 Flood risk assessment:")
    if stations:
        risk = client.get_flood_risk_from_rainfall(stations[0].code)
        print(f"  Station {stations[0].code}: {risk} flood risk")

    print("\n🔍 Find nearest station to São Paulo center:")
    nearest = client.find_nearest_station(-23.5505, -46.6333)
    if nearest:
        print(f"  {nearest.name} - {nearest.river}")

    print(f"\n✅ Health check: {client.health_check()}")
