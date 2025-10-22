"""
INMET Data Client
Access meteorological data from INMET (Instituto Nacional de Meteorologia)

Official API: https://portal.inmet.gov.br/manual/manual-de-uso-da-api-estações
BDMEP: https://bdmep.inmet.gov.br/ (historical data since 1961)
Historical Portal: https://portal.inmet.gov.br/dadoshistoricos

Token request: cadastro.act@inmet.gov.br
"""
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import requests
import logging

logger = logging.getLogger(__name__)


class INMETStation:
    """INMET Weather Station"""
    def __init__(
        self,
        code: str,
        name: str,
        latitude: float,
        longitude: float,
        altitude: Optional[float] = None,
        state: Optional[str] = None
    ):
        self.code = code
        self.name = name
        self.latitude = latitude
        self.longitude = longitude
        self.altitude = altitude
        self.state = state


class INMETClient:
    """
    Client for INMET meteorological data

    Features:
    - Real-time data from automatic weather stations
    - Historical data from BDMEP (1961-present)
    - Variables: temperature, precipitation, humidity, wind, pressure
    - Nationwide coverage (600+ stations)

    MVP Implementation:
    - Mock historical data based on Brazilian climate patterns
    - Prepared for INMET API token integration
    - Station catalog for major cities
    """

    def __init__(self, api_token: Optional[str] = None):
        """
        Initialize INMET client

        Args:
            api_token: INMET API token (from environment or parameter)
                      Request at: cadastro.act@inmet.gov.br
        """
        self.api_token = api_token or os.getenv("INMET_TOKEN")
        self.api_base = "https://apitempo.inmet.gov.br"
        self.bdmep_base = "https://bdmep.inmet.gov.br"
        self.session = requests.Session()
        self.timeout = 30

        # Load station catalog
        self._stations = self._load_station_catalog()

    def get_station_by_location(
        self,
        latitude: float,
        longitude: float,
        max_distance_km: float = 50.0
    ) -> Optional[INMETStation]:
        """
        Find nearest weather station to a location

        Args:
            latitude: Target latitude
            longitude: Target longitude
            max_distance_km: Maximum search radius in km

        Returns:
            Nearest INMETStation or None if none found within radius
        """
        import math

        def haversine_distance(lat1, lon1, lat2, lon2):
            R = 6371  # Earth radius in km
            phi1, phi2 = math.radians(lat1), math.radians(lat2)
            dphi = math.radians(lat2 - lat1)
            dlambda = math.radians(lon2 - lon1)
            a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
            return 2 * R * math.asin(math.sqrt(a))

        nearest = None
        min_distance = float('inf')

        for station in self._stations.values():
            dist = haversine_distance(latitude, longitude, station.latitude, station.longitude)
            if dist < min_distance and dist <= max_distance_km:
                min_distance = dist
                nearest = station

        return nearest

    def get_historical_climate_summary(
        self,
        station_code: str,
        start_year: int = 2000,
        end_year: int = 2023
    ) -> Optional[Dict]:
        """
        Get historical climate summary for a station

        Args:
            station_code: INMET station code (e.g., "A101", "83377")
            start_year: Start year for analysis
            end_year: End year for analysis

        Returns:
            Dict with climate statistics (temperature, precipitation)

        MVP: Returns mock data based on station location
        Future: Query BDMEP API for real historical data
        """
        if not self.api_token:
            logger.info(f"INMET token not configured - using mock historical data for {station_code}")
            return self._mock_historical_summary(station_code, start_year, end_year)

        try:
            # TODO: Implement real BDMEP query when API available
            # Expected endpoint: /bdmep/station/{code}/summary?start={year}&end={year}
            logger.warning("BDMEP API integration not yet implemented - using mock data")
            return self._mock_historical_summary(station_code, start_year, end_year)

        except Exception as e:
            logger.error(f"BDMEP query failed: {e}")
            return self._mock_historical_summary(station_code, start_year, end_year)

    def get_current_conditions(
        self,
        station_code: str
    ) -> Optional[Dict]:
        """
        Get current weather conditions from a station

        Args:
            station_code: INMET station code

        Returns:
            Dict with current meteorological observations

        MVP: Returns mock data
        Future: Real-time API integration
        """
        if not self.api_token:
            logger.info("INMET token not configured - using mock current conditions")
            return self._mock_current_conditions(station_code)

        try:
            # INMET API endpoint for current conditions
            # https://apitempo.inmet.gov.br/estacao/{code}/atual
            headers = {"Authorization": f"Bearer {self.api_token}"}
            url = f"{self.api_base}/estacao/{station_code}/atual"

            response = self.session.get(url, headers=headers, timeout=self.timeout)

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"INMET API error: {response.status_code}")
                return self._mock_current_conditions(station_code)

        except requests.RequestException as e:
            logger.error(f"INMET API request failed: {e}")
            return self._mock_current_conditions(station_code)

    def get_extreme_events_history(
        self,
        station_code: str,
        event_type: str = "precipitation",
        years: int = 10
    ) -> List[Dict]:
        """
        Get history of extreme weather events

        Args:
            station_code: INMET station code
            event_type: Type of extreme event (precipitation, temperature, wind)
            years: Number of years to analyze

        Returns:
            List of extreme event records

        Useful for validating hazard risk models
        """
        if not self.api_token:
            return self._mock_extreme_events(station_code, event_type, years)

        # TODO: Query BDMEP for extreme events
        return self._mock_extreme_events(station_code, event_type, years)

    def _load_station_catalog(self) -> Dict[str, INMETStation]:
        """
        Load catalog of INMET weather stations

        MVP: Sample stations for major cities
        Future: Complete catalog from INMET API
        """
        return {
            # São Paulo
            "A701": INMETStation("A701", "São Paulo - Mirante", -23.4969, -46.6197, 792, "SP"),

            # Rio de Janeiro
            "A652": INMETStation("A652", "Rio de Janeiro - Forte de Copacabana", -22.9868, -43.1897, 24, "RJ"),

            # Belo Horizonte
            "A522": INMETStation("A522", "Belo Horizonte", -19.9320, -43.9438, 915, "MG"),

            # Salvador
            "A410": INMETStation("A410", "Salvador", -12.9091, -38.3310, 51, "BA"),

            # Brasília
            "A001": INMETStation("A001", "Brasília", -15.7894, -47.9258, 1160, "DF"),

            # Fortaleza
            "A307": INMETStation("A307", "Fortaleza", -3.7765, -38.5324, 26, "CE"),

            # Manaus
            "A101": INMETStation("A101", "Manaus", -3.1028, -59.9631, 67, "AM"),

            # Curitiba
            "A807": INMETStation("A807", "Curitiba", -25.4483, -49.2307, 923, "PR"),

            # Recife
            "A301": INMETStation("A301", "Recife", -8.0522, -34.9521, 10, "PE"),

            # Porto Alegre
            "A801": INMETStation("A801", "Porto Alegre", -30.0534, -51.1749, 46, "RS"),
        }

    def _mock_historical_summary(
        self,
        station_code: str,
        start_year: int,
        end_year: int
    ) -> Dict:
        """Generate mock historical climate summary based on Brazilian regions"""
        station = self._stations.get(station_code)
        if not station:
            return {
                "station_code": station_code,
                "error": "Station not found",
                "mock": True
            }

        lat = station.latitude

        # Regional climate patterns (based on historical INMET data)
        if lat > -10:  # North (Amazon)
            temp_avg = 26.5
            temp_range = 2.0
            precip_annual = 2300  # mm/year
        elif -10 <= lat < -5:  # Northeast
            temp_avg = 27.0
            temp_range = 3.0
            precip_annual = 800  # Semi-arid
        elif -25 <= lat < -14:  # Southeast
            temp_avg = 22.0
            temp_range = 5.0
            precip_annual = 1400
        else:  # South
            temp_avg = 18.0
            temp_range = 8.0
            precip_annual = 1600

        return {
            "station_code": station_code,
            "station_name": station.name,
            "period": f"{start_year}-{end_year}",
            "years_analyzed": end_year - start_year + 1,
            "temperature": {
                "mean_annual_c": round(temp_avg, 1),
                "mean_max_c": round(temp_avg + temp_range/2, 1),
                "mean_min_c": round(temp_avg - temp_range/2, 1),
                "absolute_max_c": round(temp_avg + temp_range, 1),
                "absolute_min_c": round(temp_avg - temp_range, 1),
            },
            "precipitation": {
                "mean_annual_mm": precip_annual,
                "wettest_month_mm": round(precip_annual / 4),  # Concentrated in rainy season
                "driest_month_mm": round(precip_annual / 24),
                "rainy_days_per_year": int(precip_annual / 10),
            },
            "humidity": {
                "mean_relative_pct": 75 if lat > -10 else 65,
            },
            "data_source": "INMET-mock",
            "mock": True,
            "note": "MVP mock data based on INMET climate normals for Brazilian regions"
        }

    def _mock_current_conditions(self, station_code: str) -> Dict:
        """Generate mock current weather conditions"""
        station = self._stations.get(station_code)
        if not station:
            return {"error": "Station not found", "mock": True}

        import random
        from datetime import datetime, timezone

        # Time-based temperature variation
        hour = datetime.now().hour
        temp_variation = -3 if (hour < 6 or hour > 20) else 0

        lat = station.latitude
        base_temp = 26.5 if lat > -10 else (27.0 if -10 <= lat < -5 else 22.0)

        return {
            "station_code": station_code,
            "station_name": station.name,
            "observation_time": datetime.now(timezone.utc).isoformat(),
            "temperature_c": round(base_temp + temp_variation + random.uniform(-2, 2), 1),
            "humidity_pct": round(75 + random.uniform(-15, 15)),
            "pressure_hpa": round(1013 + random.uniform(-10, 10), 1),
            "wind_speed_ms": round(random.uniform(1, 8), 1),
            "wind_direction_deg": random.randint(0, 359),
            "precipitation_mm": round(random.uniform(0, 5), 1) if random.random() > 0.7 else 0,
            "data_source": "INMET-mock",
            "mock": True
        }

    def _mock_extreme_events(
        self,
        station_code: str,
        event_type: str,
        years: int
    ) -> List[Dict]:
        """Generate mock extreme events history"""
        station = self._stations.get(station_code)
        if not station:
            return []

        lat = station.latitude
        events = []

        # Number of extreme events varies by region
        if event_type == "precipitation":
            # More extreme rainfall in Amazon and Southeast
            event_count = 15 if lat > -10 else (10 if -25 <= lat < -14 else 5)

            for i in range(min(event_count, years * 2)):
                year = 2023 - (i // 2)
                month = 1 if lat > -10 else (12 if lat < -25 else 3)  # Rainy season
                events.append({
                    "date": f"{year}-{month:02d}-{15+i%15:02d}",
                    "type": "extreme_precipitation",
                    "value_mm": round(80 + i * 10, 1),
                    "duration_hours": 12 + i % 12,
                    "severity": "high" if i < 3 else "moderate"
                })

        return events


# Singleton instance
_inmet_client: Optional[INMETClient] = None


def get_inmet_client() -> INMETClient:
    """Get or create INMET client instance"""
    global _inmet_client
    if _inmet_client is None:
        _inmet_client = INMETClient()
    return _inmet_client
