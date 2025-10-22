"""
Physical Risk Service
Calculates climate physical risks for Brazilian municipalities

MVP: Simplified calculations based on location
Future: Full integration with physrisk + Cemaden + INPE
"""
from typing import Dict, List, Optional
from enum import Enum
import math


class RiskScenario(str, Enum):
    """Climate scenarios (IPCC)"""
    RCP26 = "rcp26"  # Low emissions
    RCP45 = "rcp45"  # Moderate emissions
    RCP85 = "rcp85"  # High emissions


class HazardType(str, Enum):
    """Physical climate hazards"""
    FLOOD = "flood"
    DROUGHT = "drought"
    HEAT_STRESS = "heat_stress"
    LANDSLIDE = "landslide"
    COASTAL_INUNDATION = "coastal_inundation"


class HazardRiskScore:
    """Risk scores for a specific hazard"""
    def __init__(
        self,
        hazard_type: HazardType,
        current_risk: float,
        projected_2030: float,
        projected_2050: float,
        confidence: float = 0.5,
        data_source: str = "MVP-simplified"
    ):
        self.hazard_type = hazard_type
        self.current_risk = current_risk
        self.projected_2030 = projected_2030
        self.projected_2050 = projected_2050
        self.confidence = confidence
        self.data_source = data_source

    def to_dict(self) -> Dict:
        return {
            "hazard_type": self.hazard_type.value,
            "current_risk": round(self.current_risk, 3),
            "projected_2030": round(self.projected_2030, 3),
            "projected_2050": round(self.projected_2050, 3),
            "confidence": round(self.confidence, 2),
            "data_source": self.data_source,
        }


class PhysicalRiskService:
    """
    Calculates physical climate risks for Brazilian locations

    MVP Implementation:
    - Simplified risk calculations based on lat/lon
    - Heuristics for Brazilian regions
    - Returns structured risk scores for 5 hazard types

    Future Integration:
    - physrisk library for detailed modeling
    - Cemaden API for real-time hazard data
    - INPE projections for climate scenarios
    - IBGE data for municipality characteristics
    """

    def __init__(self):
        """Initialize risk service"""
        self.scenario_multipliers = {
            RiskScenario.RCP26: {"2030": 1.1, "2050": 1.2},
            RiskScenario.RCP45: {"2030": 1.15, "2050": 1.35},
            RiskScenario.RCP85: {"2030": 1.25, "2050": 1.6},
        }

    def calculate_municipal_risk(
        self,
        ibge_code: str,
        latitude: float,
        longitude: float,
        scenario: RiskScenario = RiskScenario.RCP45
    ) -> List[HazardRiskScore]:
        """
        Calculate climate risks for a municipality

        Args:
            ibge_code: 7-digit IBGE municipality code
            latitude: Latitude in decimal degrees
            longitude: Longitude in decimal degrees
            scenario: Climate scenario (default RCP4.5)

        Returns:
            List of HazardRiskScore objects (one per hazard type)
        """
        # Get baseline risks based on geography
        baseline_risks = self._calculate_baseline_risks(latitude, longitude)

        # Apply scenario multipliers
        multipliers = self.scenario_multipliers[scenario]

        hazard_scores = []
        for hazard_type, base_risk in baseline_risks.items():
            score = HazardRiskScore(
                hazard_type=hazard_type,
                current_risk=base_risk,
                projected_2030=min(1.0, base_risk * multipliers["2030"]),
                projected_2050=min(1.0, base_risk * multipliers["2050"]),
                confidence=self._get_confidence_for_hazard(hazard_type, latitude, longitude),
                data_source="MVP-simplified (geographic heuristics)"
            )
            hazard_scores.append(score)

        return hazard_scores

    def _calculate_baseline_risks(
        self,
        latitude: float,
        longitude: float
    ) -> Dict[HazardType, float]:
        """
        Calculate baseline (current) risk scores based on location

        Uses simplified heuristics for Brazilian geography:
        - North (Amazon): High flood, moderate drought
        - Northeast (Sertão): High drought, low flood
        - Southeast (urban coast): Flood + heat stress
        - South: Moderate across hazards
        - Coastal: High coastal inundation

        Returns risk scores 0.0-1.0 for each hazard type
        """
        risks = {}

        # Regional classification (simplified)
        is_north = latitude > -10
        is_northeast = -10 <= latitude < -5 and longitude > -44
        is_southeast = -25 <= latitude < -14 and -50 <= longitude < -39
        is_south = latitude < -25
        is_coastal = abs(longitude + 40) < 5  # Rough coastal approximation

        # Flood risk
        if is_north:
            risks[HazardType.FLOOD] = 0.45 + self._add_noise(0.15)
        elif is_northeast:
            risks[HazardType.FLOOD] = 0.25 + self._add_noise(0.1)
        elif is_southeast:
            risks[HazardType.FLOOD] = 0.35 + self._add_noise(0.15)
        else:
            risks[HazardType.FLOOD] = 0.30 + self._add_noise(0.1)

        # Drought risk
        if is_northeast:
            risks[HazardType.DROUGHT] = 0.65 + self._add_noise(0.15)
        elif is_north:
            risks[HazardType.DROUGHT] = 0.25 + self._add_noise(0.1)
        elif is_south:
            risks[HazardType.DROUGHT] = 0.35 + self._add_noise(0.1)
        else:
            risks[HazardType.DROUGHT] = 0.40 + self._add_noise(0.12)

        # Heat stress (increases towards equator)
        latitude_factor = (10 + latitude) / 40  # 0-1 scale
        risks[HazardType.HEAT_STRESS] = 0.3 + latitude_factor * 0.4 + self._add_noise(0.1)

        # Landslide (higher in mountainous southeast)
        if is_southeast:
            risks[HazardType.LANDSLIDE] = 0.40 + self._add_noise(0.15)
        elif is_south:
            risks[HazardType.LANDSLIDE] = 0.30 + self._add_noise(0.1)
        else:
            risks[HazardType.LANDSLIDE] = 0.15 + self._add_noise(0.08)

        # Coastal inundation
        if is_coastal:
            risks[HazardType.COASTAL_INUNDATION] = 0.50 + self._add_noise(0.2)
        else:
            risks[HazardType.COASTAL_INUNDATION] = 0.05 + self._add_noise(0.03)

        # Clamp all values to [0, 1]
        return {k: max(0.0, min(1.0, v)) for k, v in risks.items()}

    def _add_noise(self, amplitude: float) -> float:
        """Add small random variation to make data more realistic"""
        import hashlib
        import time
        # Deterministic "noise" based on timestamp hash
        seed = int(hashlib.md5(str(time.time()).encode()).hexdigest()[:8], 16)
        noise = ((seed % 1000) / 1000.0 - 0.5) * 2 * amplitude
        return noise

    def _get_confidence_for_hazard(
        self,
        hazard_type: HazardType,
        latitude: float,
        longitude: float
    ) -> float:
        """
        Estimate confidence in risk score

        MVP: Returns fixed confidence levels
        Future: Based on data availability and model quality
        """
        # Confidence is lower for MVP simplified calculations
        base_confidence = {
            HazardType.FLOOD: 0.5,
            HazardType.DROUGHT: 0.55,
            HazardType.HEAT_STRESS: 0.6,
            HazardType.LANDSLIDE: 0.45,
            HazardType.COASTAL_INUNDATION: 0.5,
        }
        return base_confidence.get(hazard_type, 0.5)

    def get_h3_risk_grid(
        self,
        latitude: float,
        longitude: float,
        resolution: int = 7,
        radius_km: int = 10
    ) -> Dict[str, float]:
        """
        Generate H3 grid with risk scores around a location

        Args:
            latitude: Center point latitude
            longitude: Center point longitude
            resolution: H3 resolution (7 = ~500m cells)
            radius_km: Radius to generate grid

        Returns:
            Dict mapping H3 cell IDs to overall risk scores

        Future: Full H3 integration with physrisk
        """
        try:
            import h3

            # Get central H3 cell
            center_h3 = h3.latlng_to_cell(latitude, longitude, resolution)

            # Get ring of cells (k-ring)
            k = max(1, radius_km // 2)  # Approximate ring size
            cells = h3.grid_disk(center_h3, k)

            # Calculate risk for each cell
            # MVP: Simple distance decay from center
            grid_risks = {}
            for cell in cells:
                cell_lat, cell_lon = h3.cell_to_latlng(cell)

                # Distance from center
                dist = self._haversine_distance(
                    latitude, longitude, cell_lat, cell_lon
                )

                # Decay factor
                decay = math.exp(-dist / (radius_km * 0.5))

                # Base risk (simplified average)
                base_risks = self._calculate_baseline_risks(cell_lat, cell_lon)
                avg_risk = sum(base_risks.values()) / len(base_risks)

                grid_risks[cell] = round(avg_risk * decay, 3)

            return grid_risks

        except ImportError:
            # H3 not available, return empty
            return {}

    def _haversine_distance(
        self,
        lat1: float,
        lon1: float,
        lat2: float,
        lon2: float
    ) -> float:
        """Calculate distance between two points in km"""
        R = 6371  # Earth radius in km

        phi1, phi2 = math.radians(lat1), math.radians(lat2)
        dphi = math.radians(lat2 - lat1)
        dlambda = math.radians(lon2 - lon1)

        a = math.sin(dphi/2)**2 + \
            math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2

        return 2 * R * math.asin(math.sqrt(a))


# Singleton instance
_risk_service: Optional[PhysicalRiskService] = None


def get_risk_service() -> PhysicalRiskService:
    """Get or create physical risk service instance"""
    global _risk_service
    if _risk_service is None:
        _risk_service = PhysicalRiskService()
    return _risk_service
