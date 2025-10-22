"""
Cemaden Data Client
Access historical hazard data from Cemaden (Centro Nacional de Monitoramento e Alertas)

Future API: To be determined (currently no public REST API)
Data Portal: http://www2.cemaden.gov.br/mapainterativo
"""
import os
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class CemadenHazardType:
    """Cemaden monitored hazard types"""
    FLOOD = "inundacao"
    FLASH_FLOOD = "enxurrada"
    LANDSLIDE = "deslizamento"
    DROUGHT = "seca"


class CemadenClient:
    """
    Client for Cemaden hazard monitoring data

    MVP Implementation:
    - Uses mock historical data based on Brazilian regions
    - Prepared for future API integration when available

    Future Integration:
    - Cemaden Interactive Map API (when available)
    - Historical pluviometer data (2013-present)
    - Real-time alerts and warnings
    - Municipality-level hazard occurrences
    """

    def __init__(self):
        """Initialize Cemaden client"""
        self.data_portal = "http://www2.cemaden.gov.br/mapainterativo"
        self.has_api_access = False  # Set to True when API becomes available

        # Historical hazard occurrence data (mock - based on Cemaden reports)
        # Format: {ibge_code: {hazard_type: annual_occurrence_count}}
        self._historical_occurrences = self._load_mock_historical_data()

    def get_historical_hazard_frequency(
        self,
        ibge_code: str,
        hazard_type: str,
        years: int = 5
    ) -> Dict:
        """
        Get historical frequency of hazard occurrences

        Args:
            ibge_code: IBGE 7-digit municipality code
            hazard_type: Type of hazard (flood, landslide, drought)
            years: Number of years to analyze

        Returns:
            Dict with frequency statistics
        """
        if self.has_api_access:
            return self._query_api_historical(ibge_code, hazard_type, years)
        else:
            return self._get_mock_frequency(ibge_code, hazard_type, years)

    def get_current_alerts(self, ibge_code: str) -> List[Dict]:
        """
        Get current active alerts for municipality

        Args:
            ibge_code: IBGE municipality code

        Returns:
            List of active alert dictionaries

        MVP: Returns empty list (no API access)
        """
        if self.has_api_access:
            # TODO: Implement when API available
            pass

        logger.info(f"No current alerts available for {ibge_code} (API not configured)")
        return []

    def get_rainfall_data(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> Optional[List[Dict]]:
        """
        Get rainfall data from nearest pluviometer

        Args:
            latitude: Location latitude
            longitude: Location longitude
            start_date: Start date for data
            end_date: End date for data

        Returns:
            List of rainfall measurements

        MVP: Returns mock data
        Future: Real pluviometer data from Cemaden network
        """
        if self.has_api_access:
            # TODO: Query nearest pluviometer and download data
            pass

        return self._mock_rainfall_data(latitude, longitude, start_date, end_date)

    def _query_api_historical(
        self,
        ibge_code: str,
        hazard_type: str,
        years: int
    ) -> Dict:
        """Query real Cemaden API (future implementation)"""
        # TODO: Implement when API available
        # Expected format:
        # GET /api/v1/occurrences?ibge={code}&hazard={type}&years={n}
        pass

    def _get_mock_frequency(
        self,
        ibge_code: str,
        hazard_type: str,
        years: int
    ) -> Dict:
        """Get mock frequency data based on regional patterns"""
        occurrences = self._historical_occurrences.get(ibge_code, {})
        annual_count = occurrences.get(hazard_type, 0)

        return {
            "ibge_code": ibge_code,
            "hazard_type": hazard_type,
            "analysis_period_years": years,
            "total_occurrences": annual_count * years,
            "annual_average": annual_count,
            "data_source": "Cemaden-mock",
            "confidence": 0.5,  # Mock data has lower confidence
            "note": "MVP mock data based on Cemaden historical reports"
        }

    def _mock_rainfall_data(
        self,
        latitude: float,
        longitude: float,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict]:
        """Generate mock rainfall data"""
        # Simple regional rainfall patterns
        is_north = latitude > -10
        is_northeast = -10 <= latitude < -5
        is_south = latitude < -25

        # Base daily rainfall (mm)
        if is_north:
            base_rain = 8.0  # Higher rainfall (Amazon)
        elif is_northeast:
            base_rain = 2.0  # Low rainfall (Semi-arid)
        elif is_south:
            base_rain = 5.0  # Moderate rainfall
        else:
            base_rain = 4.0  # Southeast

        # Generate daily data
        data = []
        current_date = start_date

        while current_date <= end_date:
            # Add some variation
            import random
            daily_rain = max(0, base_rain * random.uniform(0.3, 2.5))

            data.append({
                "date": current_date.isoformat(),
                "rainfall_mm": round(daily_rain, 1),
                "station_id": f"mock_{latitude}_{longitude}",
                "mock": True
            })

            current_date += timedelta(days=1)

        return data

    def _load_mock_historical_data(self) -> Dict[str, Dict[str, int]]:
        """
        Load mock historical hazard occurrence data

        Based on actual Cemaden monitoring reports
        Returns annual average occurrences per municipality
        """
        return {
            # São Paulo - High urban flood and landslide risk
            "3550308": {
                CemadenHazardType.FLOOD: 12,
                CemadenHazardType.FLASH_FLOOD: 8,
                CemadenHazardType.LANDSLIDE: 15,
                CemadenHazardType.DROUGHT: 2
            },
            # Rio de Janeiro - Very high landslide risk
            "3304557": {
                CemadenHazardType.FLOOD: 10,
                CemadenHazardType.FLASH_FLOOD: 6,
                CemadenHazardType.LANDSLIDE: 20,
                CemadenHazardType.DROUGHT: 3
            },
            # Salvador - Coastal flooding
            "2927408": {
                CemadenHazardType.FLOOD: 8,
                CemadenHazardType.FLASH_FLOOD: 5,
                CemadenHazardType.LANDSLIDE: 7,
                CemadenHazardType.DROUGHT: 4
            },
            # Fortaleza - Drought and coastal
            "2304400": {
                CemadenHazardType.FLOOD: 6,
                CemadenHazardType.FLASH_FLOOD: 4,
                CemadenHazardType.LANDSLIDE: 2,
                CemadenHazardType.DROUGHT: 12
            },
            # Manaus - High flood risk (Amazon)
            "1302603": {
                CemadenHazardType.FLOOD: 18,
                CemadenHazardType.FLASH_FLOOD: 10,
                CemadenHazardType.LANDSLIDE: 3,
                CemadenHazardType.DROUGHT: 1
            },
            # Curitiba - Moderate risks
            "4106902": {
                CemadenHazardType.FLOOD: 7,
                CemadenHazardType.FLASH_FLOOD: 5,
                CemadenHazardType.LANDSLIDE: 6,
                CemadenHazardType.DROUGHT: 3
            },
            # Belo Horizonte - Flash floods and landslides
            "3106200": {
                CemadenHazardType.FLOOD: 9,
                CemadenHazardType.FLASH_FLOOD: 11,
                CemadenHazardType.LANDSLIDE: 12,
                CemadenHazardType.DROUGHT: 2
            },
            # Brasília - Drought risk
            "5300108": {
                CemadenHazardType.FLOOD: 5,
                CemadenHazardType.FLASH_FLOOD: 3,
                CemadenHazardType.LANDSLIDE: 1,
                CemadenHazardType.DROUGHT: 8
            },
            # Recife - High flood risk
            "2611606": {
                CemadenHazardType.FLOOD: 14,
                CemadenHazardType.FLASH_FLOOD: 9,
                CemadenHazardType.LANDSLIDE: 5,
                CemadenHazardType.DROUGHT: 6
            },
            # Porto Alegre - Flood risk
            "4314902": {
                CemadenHazardType.FLOOD: 11,
                CemadenHazardType.FLASH_FLOOD: 6,
                CemadenHazardType.LANDSLIDE: 4,
                CemadenHazardType.DROUGHT: 4
            },
        }

    def get_hazard_history_score(self, ibge_code: str, hazard_type: str) -> float:
        """
        Calculate normalized hazard history score (0.0-1.0)

        Based on historical occurrence frequency
        Higher score = more frequent occurrences
        """
        freq_data = self.get_historical_hazard_frequency(ibge_code, hazard_type, years=5)
        annual_avg = freq_data.get("annual_average", 0)

        # Normalize to 0-1 scale (max ~20 events/year)
        normalized = min(1.0, annual_avg / 20.0)

        return normalized


# Singleton instance
_cemaden_client: Optional[CemadenClient] = None


def get_cemaden_client() -> CemadenClient:
    """Get or create Cemaden client instance"""
    global _cemaden_client
    if _cemaden_client is None:
        _cemaden_client = CemadenClient()
    return _cemaden_client
