"""
H3 Geospatial Indexing Service
Maps climate risks to hexagonal grids for visualization
"""
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import h3
import logging

from .calculator import RiskCalculator, RiskScenario, HazardType

logger = logging.getLogger(__name__)


@dataclass
class H3Cell:
    """H3 hexagonal cell with risk data"""
    h3_index: str
    resolution: int
    center_lat: float
    center_lng: float
    risk_score: float
    hazard_breakdown: Dict[str, float]
    area_km2: float


class H3RiskMapper:
    """
    Maps climate risks to H3 hexagonal grid system

    H3 Resolutions (for reference):
    - Res 5: ~252 km² per cell (regional/state level)
    - Res 6: ~36 km² per cell (large municipality)
    - Res 7: ~5.2 km² per cell (municipality/district)
    - Res 8: ~0.74 km² per cell (neighborhood)
    - Res 9: ~0.11 km² per cell (block level)
    """

    def __init__(
        self,
        resolution: int = 7,
        scenario: RiskScenario = RiskScenario.SSP245
    ):
        """
        Initialize H3 risk mapper

        Args:
            resolution: H3 resolution (5-9, default 7 for municipalities)
            scenario: Climate scenario
        """
        if resolution < 5 or resolution > 9:
            raise ValueError("Resolution must be between 5 and 9")

        self.resolution = resolution
        self.scenario = scenario
        self.risk_calculator = RiskCalculator(use_brazilian_data=True)

        logger.info(f"H3RiskMapper initialized (resolution={resolution}, scenario={scenario})")

    def latlng_to_h3(self, latitude: float, longitude: float) -> str:
        """Convert lat/lng to H3 index"""
        return h3.latlng_to_cell(latitude, longitude, self.resolution)

    def h3_to_latlng(self, h3_index: str) -> Tuple[float, float]:
        """Convert H3 index to lat/lng (center of cell)"""
        lat, lng = h3.cell_to_latlng(h3_index)
        return lat, lng

    def get_cell_area(self, h3_index: str) -> float:
        """Get cell area in km²"""
        return h3.cell_area(h3_index, unit='km^2')

    def calculate_cell_risk(self, h3_index: str) -> H3Cell:
        """
        Calculate climate risk for a single H3 cell

        Args:
            h3_index: H3 hexagon index

        Returns:
            H3Cell with risk data
        """
        # Get cell center
        lat, lng = self.h3_to_latlng(h3_index)

        # Calculate risk
        location_risk = self.risk_calculator.calculate_location_risk(
            latitude=lat,
            longitude=lng,
            scenario=self.scenario
        )

        # Extract hazard breakdown
        hazard_breakdown = {
            hazard.hazard_type.value: hazard.projected_2050
            for hazard in location_risk.hazards
        }

        return H3Cell(
            h3_index=h3_index,
            resolution=self.resolution,
            center_lat=lat,
            center_lng=lng,
            risk_score=location_risk.overall_risk_score,
            hazard_breakdown=hazard_breakdown,
            area_km2=self.get_cell_area(h3_index)
        )

    def create_risk_grid(
        self,
        center_lat: float,
        center_lng: float,
        rings: int = 3
    ) -> List[H3Cell]:
        """
        Create hexagonal risk grid around a center point

        Args:
            center_lat: Center latitude
            center_lng: Center longitude
            rings: Number of hexagonal rings around center (default 3)

        Returns:
            List of H3Cell with risk data
        """
        logger.info(f"Creating risk grid: center=({center_lat},{center_lng}), rings={rings}")

        # Get center cell
        center_cell = self.latlng_to_h3(center_lat, center_lng)

        # Get all cells in grid (center + rings)
        h3_indices = h3.grid_disk(center_cell, rings)

        logger.info(f"Grid contains {len(h3_indices)} cells")

        # Calculate risk for each cell
        cells = []
        for i, h3_idx in enumerate(h3_indices):
            cell = self.calculate_cell_risk(h3_idx)
            cells.append(cell)

            if (i + 1) % 10 == 0:
                logger.debug(f"Processed {i + 1}/{len(h3_indices)} cells")

        logger.info(f"✓ Risk grid created with {len(cells)} cells")
        return cells

    def create_municipality_grid(
        self,
        ibge_code: str,
        rings: int = 2
    ) -> List[H3Cell]:
        """
        Create risk grid for a municipality

        Args:
            ibge_code: IBGE 7-digit municipality code
            rings: Number of rings (default 2)

        Returns:
            List of H3Cell
        """
        # TODO: Query IBGE API for actual municipality boundaries
        # For now, using centroid from calculator

        risk = self.risk_calculator.calculate_municipality_risk(ibge_code, self.scenario)

        return self.create_risk_grid(
            center_lat=risk.latitude,
            center_lng=risk.longitude,
            rings=rings
        )

    def create_bounding_box_grid(
        self,
        min_lat: float,
        min_lng: float,
        max_lat: float,
        max_lng: float
    ) -> List[H3Cell]:
        """
        Create risk grid for a bounding box

        Args:
            min_lat, min_lng: Southwest corner
            max_lat, max_lng: Northeast corner

        Returns:
            List of H3Cell covering the bounding box
        """
        logger.info(f"Creating grid for bbox: ({min_lat},{min_lng}) to ({max_lat},{max_lng})")

        # Get all H3 cells in bounding box
        h3_indices = h3.polygon_to_cells(
            [
                [min_lat, min_lng],
                [max_lat, min_lng],
                [max_lat, max_lng],
                [min_lat, max_lng],
                [min_lat, min_lng]  # Close polygon
            ],
            self.resolution
        )

        logger.info(f"Bounding box contains {len(h3_indices)} cells")

        # Calculate risk for each cell
        cells = [self.calculate_cell_risk(idx) for idx in h3_indices]

        logger.info(f"✓ Bounding box grid created with {len(cells)} cells")
        return cells

    def get_risk_heatmap_data(
        self,
        cells: List[H3Cell],
        hazard_type: Optional[HazardType] = None
    ) -> Dict[str, float]:
        """
        Convert H3 cells to heatmap format (h3_index → risk_score)

        Args:
            cells: List of H3Cell
            hazard_type: Specific hazard to map (None = overall risk)

        Returns:
            Dict mapping h3_index to risk score
        """
        heatmap = {}

        for cell in cells:
            if hazard_type:
                # Use specific hazard risk
                risk = cell.hazard_breakdown.get(hazard_type.value, 0.0)
            else:
                # Use overall risk
                risk = cell.risk_score

            heatmap[cell.h3_index] = risk

        return heatmap

    def get_geojson_features(self, cells: List[H3Cell]) -> List[Dict]:
        """
        Convert H3 cells to GeoJSON features for mapping

        Args:
            cells: List of H3Cell

        Returns:
            List of GeoJSON Feature objects
        """
        features = []

        for cell in cells:
            # Get cell boundary as polygon
            boundary = h3.cell_to_boundary(cell.h3_index)

            # Convert to GeoJSON format [lng, lat]
            coordinates = [[lng, lat] for lat, lng in boundary]
            coordinates.append(coordinates[0])  # Close polygon

            feature = {
                "type": "Feature",
                "geometry": {
                    "type": "Polygon",
                    "coordinates": [coordinates]
                },
                "properties": {
                    "h3_index": cell.h3_index,
                    "resolution": cell.resolution,
                    "risk_score": cell.risk_score,
                    "area_km2": cell.area_km2,
                    **cell.hazard_breakdown
                }
            }

            features.append(feature)

        return features


# Convenience functions
def create_municipal_risk_grid(
    ibge_code: str,
    resolution: int = 7,
    rings: int = 2,
    scenario: RiskScenario = RiskScenario.SSP245
) -> List[H3Cell]:
    """Quick municipal risk grid creation"""
    mapper = H3RiskMapper(resolution=resolution, scenario=scenario)
    return mapper.create_municipality_grid(ibge_code, rings)


def get_geojson_for_municipality(
    ibge_code: str,
    resolution: int = 7,
    rings: int = 2
) -> Dict:
    """Get GeoJSON FeatureCollection for municipality risk grid"""
    cells = create_municipal_risk_grid(ibge_code, resolution, rings)

    mapper = H3RiskMapper(resolution=resolution)
    features = mapper.get_geojson_features(cells)

    return {
        "type": "FeatureCollection",
        "features": features,
        "properties": {
            "ibge_code": ibge_code,
            "resolution": resolution,
            "cell_count": len(features)
        }
    }
