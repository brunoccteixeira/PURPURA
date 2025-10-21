"""
H3 Geospatial Risk Service

Generates H3 hexagonal grids with risk scores for spatial visualization.

H3 Resolution Reference:
- Resolution 5: ~252 km² per cell (regional)
- Resolution 6: ~36 km² per cell (city-wide)
- Resolution 7: ~5 km² per cell (district-level) ✓ RECOMMENDED
- Resolution 8: ~0.7 km² per cell (neighborhood)
- Resolution 9: ~0.1 km² per cell (block-level)
"""

import logging
from typing import Dict, Tuple, Optional, List
import math

logger = logging.getLogger(__name__)

try:
    import h3
    H3_AVAILABLE = True
except ImportError:
    logger.warning("h3-py not installed. Grid generation will be disabled.")
    H3_AVAILABLE = False


class H3RiskGridService:
    """
    Service for generating H3 hexagonal risk grids

    Features:
    - Generate grids covering municipality area
    - Calculate per-cell risk scores
    - Support multiple resolution levels
    - Distance-based risk decay (optional)
    """

    # H3 Resolution levels
    RESOLUTION_REGIONAL = 5  # ~252 km²
    RESOLUTION_CITY = 6      # ~36 km²
    RESOLUTION_DISTRICT = 7  # ~5 km² (default)
    RESOLUTION_NEIGHBORHOOD = 8  # ~0.7 km²
    RESOLUTION_BLOCK = 9     # ~0.1 km²

    def __init__(self):
        """Initialize H3 risk grid service"""
        if not H3_AVAILABLE:
            raise ImportError(
                "h3-py is required for grid generation. Install with: pip install h3"
            )

    def generate_municipality_grid(
        self,
        center_lat: float,
        center_lon: float,
        radius_km: float = 20,
        resolution: int = RESOLUTION_DISTRICT,
        base_risk_score: float = 0.5,
    ) -> Dict[str, float]:
        """
        Generate H3 grid covering municipality area

        Args:
            center_lat: Latitude do centro do município
            center_lon: Longitude do centro do município
            radius_km: Raio de cobertura em km (default: 20km)
            resolution: Resolução H3 (5-9, default: 7 para ~5km²)
            base_risk_score: Score base de risco (0.0-1.0)

        Returns:
            Dict mapping H3 cell ID → risk score
            Example: {"87a8a45a9ffffff": 0.65, "87a8a45abffffff": 0.43, ...}
        """
        logger.info(
            f"Generating H3 grid: center=({center_lat}, {center_lon}), "
            f"radius={radius_km}km, resolution={resolution}"
        )

        # 1. Célula central
        center_h3 = h3.latlng_to_cell(center_lat, center_lon, resolution)

        # 2. Calcular quantos rings necessários para cobrir raio
        # Cada ring adiciona ~1.5x o tamanho anterior
        k_rings_needed = self._calculate_k_rings(radius_km, resolution)
        logger.debug(f"Using k={k_rings_needed} rings to cover {radius_km}km radius")

        # 3. Gerar células no raio especificado
        all_cells = h3.grid_disk(center_h3, k_rings_needed)

        # 4. Filtrar células fora do raio real (círculo inscrito)
        cells_in_radius = self._filter_cells_by_radius(
            all_cells, center_lat, center_lon, radius_km
        )

        logger.info(f"Generated {len(cells_in_radius)} H3 cells")

        # 5. Calcular risco para cada célula
        grid_risks = {}
        for cell_id in cells_in_radius:
            cell_lat, cell_lon = h3.cell_to_latlng(cell_id)

            # Calcular risco baseado em distância do centro
            risk_score = self._calculate_cell_risk(
                cell_lat=cell_lat,
                cell_lon=cell_lon,
                center_lat=center_lat,
                center_lon=center_lon,
                base_risk=base_risk_score,
                max_distance_km=radius_km,
            )

            grid_risks[cell_id] = round(risk_score, 3)

        return grid_risks

    def generate_grid_from_hazard_data(
        self,
        center_lat: float,
        center_lon: float,
        hazard_scores: Dict[str, Dict],
        radius_km: float = 20,
        resolution: int = RESOLUTION_DISTRICT,
    ) -> Dict[str, float]:
        """
        Generate grid with risk scores from actual hazard data

        Args:
            center_lat: Centro do município
            center_lon: Centro do município
            hazard_scores: Dict de scores de hazard (output do calculator)
            radius_km: Raio de cobertura
            resolution: Resolução H3

        Returns:
            Dict H3 cell ID → aggregated risk score
        """
        # Calcular score médio de todos os hazards
        all_scores = []
        for hazard_data in hazard_scores.values():
            if "projected_2030" in hazard_data:
                all_scores.append(hazard_data["projected_2030"])

        base_risk = sum(all_scores) / len(all_scores) if all_scores else 0.5

        # Gerar grid com score base
        return self.generate_municipality_grid(
            center_lat=center_lat,
            center_lon=center_lon,
            radius_km=radius_km,
            resolution=resolution,
            base_risk_score=base_risk,
        )

    def _calculate_k_rings(self, radius_km: float, resolution: int) -> int:
        """
        Calcula quantos k-rings necessários para cobrir raio em km

        Args:
            radius_km: Raio desejado em km
            resolution: Resolução H3

        Returns:
            Número de k-rings necessários
        """
        # Tamanho médio de célula por resolução (edge length em km)
        edge_lengths = {
            5: 8.544,    # ~252 km² per cell
            6: 3.229,    # ~36 km²
            7: 1.220,    # ~5 km²
            8: 0.461,    # ~0.7 km²
            9: 0.174,    # ~0.1 km²
        }

        edge_length = edge_lengths.get(resolution, 1.0)

        # Cada k-ring adiciona aproximadamente edge_length*2 ao raio
        k_needed = math.ceil(radius_km / (edge_length * 2))

        return max(k_needed, 1)  # Mínimo 1 ring

    def _filter_cells_by_radius(
        self,
        cells: set,
        center_lat: float,
        center_lon: float,
        radius_km: float,
    ) -> List[str]:
        """
        Filtra células que estão dentro do raio especificado

        Args:
            cells: Set de H3 cell IDs
            center_lat: Latitude do centro
            center_lon: Longitude do centro
            radius_km: Raio em km

        Returns:
            Lista de cell IDs dentro do raio
        """
        filtered = []

        for cell_id in cells:
            cell_lat, cell_lon = h3.cell_to_latlng(cell_id)
            distance = self._haversine_distance(
                center_lat, center_lon, cell_lat, cell_lon
            )

            if distance <= radius_km:
                filtered.append(cell_id)

        return filtered

    def _calculate_cell_risk(
        self,
        cell_lat: float,
        cell_lon: float,
        center_lat: float,
        center_lon: float,
        base_risk: float,
        max_distance_km: float,
    ) -> float:
        """
        Calcula score de risco para uma célula H3

        Strategy:
        - Células perto do centro têm risco = base_risk
        - Risco decai gradualmente com distância (decay factor = 0.3)
        - TODO: Substituir por cálculo real baseado em hazards pontuais

        Args:
            cell_lat: Latitude da célula
            cell_lon: Longitude da célula
            center_lat: Latitude do centro
            center_lon: Longitude do centro
            base_risk: Score base de risco (0.0-1.0)
            max_distance_km: Distância máxima do grid

        Returns:
            Risk score (0.0-1.0)
        """
        # Calcular distância do centro
        distance = self._haversine_distance(
            center_lat, center_lon, cell_lat, cell_lon
        )

        # Fator de decaimento baseado em distância (0.0-1.0)
        # Distância 0 = fator 1.0 (sem decay)
        # Distância max = fator 0.0 (máximo decay)
        distance_factor = 1.0 - (distance / max_distance_km)

        # Aplicar decay suave (30% de redução no máximo)
        decay_coefficient = 0.3
        risk_with_decay = base_risk * (1.0 - decay_coefficient * (1.0 - distance_factor))

        # TODO: Substituir por cálculo real
        # risk_score = physrisk.calculate_point_risk(cell_lat, cell_lon, hazard_type)

        return max(min(risk_with_decay, 1.0), 0.0)

    def _haversine_distance(
        self, lat1: float, lon1: float, lat2: float, lon2: float
    ) -> float:
        """
        Calcula distância Haversine entre dois pontos (km)

        Args:
            lat1, lon1: Primeiro ponto
            lat2, lon2: Segundo ponto

        Returns:
            Distância em quilômetros
        """
        R = 6371  # Raio da Terra em km

        # Converter para radianos
        lat1_rad = math.radians(lat1)
        lat2_rad = math.radians(lat2)
        delta_lat = math.radians(lat2 - lat1)
        delta_lon = math.radians(lon2 - lon1)

        # Fórmula de Haversine
        a = (
            math.sin(delta_lat / 2) ** 2
            + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2
        )
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return R * c

    def get_grid_stats(self, grid: Dict[str, float]) -> Dict[str, any]:
        """
        Retorna estatísticas do grid gerado

        Args:
            grid: Dict de H3 cell ID → risk score

        Returns:
            Dict com estatísticas (min, max, avg, count)
        """
        if not grid:
            return {
                "cell_count": 0,
                "min_risk": 0.0,
                "max_risk": 0.0,
                "avg_risk": 0.0,
            }

        risk_scores = list(grid.values())

        return {
            "cell_count": len(grid),
            "min_risk": round(min(risk_scores), 3),
            "max_risk": round(max(risk_scores), 3),
            "avg_risk": round(sum(risk_scores) / len(risk_scores), 3),
            "high_risk_cells": sum(1 for score in risk_scores if score > 0.7),
            "medium_risk_cells": sum(
                1 for score in risk_scores if 0.4 <= score <= 0.7
            ),
            "low_risk_cells": sum(1 for score in risk_scores if score < 0.4),
        }

    def get_cells_by_risk_level(
        self, grid: Dict[str, float], risk_threshold: float = 0.7
    ) -> List[str]:
        """
        Retorna células acima de um threshold de risco

        Args:
            grid: Dict de H3 cell ID → risk score
            risk_threshold: Threshold de risco (default: 0.7 = alto risco)

        Returns:
            Lista de H3 cell IDs com risco >= threshold
        """
        return [cell_id for cell_id, score in grid.items() if score >= risk_threshold]


# Instância global
_h3_service_instance: Optional[H3RiskGridService] = None


def get_h3_service() -> H3RiskGridService:
    """
    Retorna instância global do serviço H3

    Returns:
        H3RiskGridService instance
    """
    global _h3_service_instance
    if _h3_service_instance is None:
        _h3_service_instance = H3RiskGridService()
    return _h3_service_instance
