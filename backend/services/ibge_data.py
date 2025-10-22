"""
IBGE Municipality Data Service
Provides Brazilian municipality information

MVP: Sample data for major cities
Future: Full IBGE API integration
"""
from typing import Dict, Optional, NamedTuple


class MunicipalityInfo(NamedTuple):
    """Municipality information"""
    ibge_code: str
    name: str
    state: str
    latitude: float
    longitude: float
    population: Optional[int] = None


class IBGEDataService:
    """
    Service for Brazilian municipality data

    MVP: Hardcoded data for major cities
    Future: IBGE API integration + local database
    """

    def __init__(self):
        # Sample municipalities (MVP data)
        self._municipalities: Dict[str, MunicipalityInfo] = {
            # São Paulo
            "3550308": MunicipalityInfo(
                ibge_code="3550308",
                name="São Paulo",
                state="SP",
                latitude=-23.5505,
                longitude=-46.6333,
                population=12300000
            ),
            # Rio de Janeiro
            "3304557": MunicipalityInfo(
                ibge_code="3304557",
                name="Rio de Janeiro",
                state="RJ",
                latitude=-22.9068,
                longitude=-43.1729,
                population=6700000
            ),
            # Belo Horizonte
            "3106200": MunicipalityInfo(
                ibge_code="3106200",
                name="Belo Horizonte",
                state="MG",
                latitude=-19.9167,
                longitude=-43.9345,
                population=2500000
            ),
            # Salvador
            "2927408": MunicipalityInfo(
                ibge_code="2927408",
                name="Salvador",
                state="BA",
                latitude=-12.9714,
                longitude=-38.5014,
                population=2900000
            ),
            # Brasília
            "5300108": MunicipalityInfo(
                ibge_code="5300108",
                name="Brasília",
                state="DF",
                latitude=-15.7975,
                longitude=-47.8919,
                population=3000000
            ),
            # Fortaleza
            "2304400": MunicipalityInfo(
                ibge_code="2304400",
                name="Fortaleza",
                state="CE",
                latitude=-3.7319,
                longitude=-38.5267,
                population=2700000
            ),
            # Manaus
            "1302603": MunicipalityInfo(
                ibge_code="1302603",
                name="Manaus",
                state="AM",
                latitude=-3.1190,
                longitude=-60.0217,
                population=2200000
            ),
            # Curitiba
            "4106902": MunicipalityInfo(
                ibge_code="4106902",
                name="Curitiba",
                state="PR",
                latitude=-25.4284,
                longitude=-49.2733,
                population=1900000
            ),
            # Recife
            "2611606": MunicipalityInfo(
                ibge_code="2611606",
                name="Recife",
                state="PE",
                latitude=-8.0476,
                longitude=-34.8770,
                population=1650000
            ),
            # Porto Alegre
            "4314902": MunicipalityInfo(
                ibge_code="4314902",
                name="Porto Alegre",
                state="RS",
                latitude=-30.0346,
                longitude=-51.2177,
                population=1490000
            ),
        }

    def get_municipality(self, ibge_code: str) -> Optional[MunicipalityInfo]:
        """
        Get municipality information by IBGE code

        Args:
            ibge_code: 7-digit IBGE municipality code

        Returns:
            MunicipalityInfo or None if not found
        """
        return self._municipalities.get(ibge_code)

    def get_coordinates(self, ibge_code: str) -> Optional[tuple[float, float]]:
        """
        Get municipality coordinates

        Args:
            ibge_code: 7-digit IBGE code

        Returns:
            Tuple of (latitude, longitude) or None
        """
        muni = self.get_municipality(ibge_code)
        if muni:
            return (muni.latitude, muni.longitude)
        return None

    def search_by_name(self, name: str) -> list[MunicipalityInfo]:
        """
        Search municipalities by name (case-insensitive)

        Args:
            name: Municipality name or partial name

        Returns:
            List of matching municipalities
        """
        name_lower = name.lower()
        return [
            muni for muni in self._municipalities.values()
            if name_lower in muni.name.lower()
        ]

    def get_all_municipalities(self) -> list[MunicipalityInfo]:
        """Get all available municipalities"""
        return list(self._municipalities.values())


# Singleton instance
_ibge_service: Optional[IBGEDataService] = None


def get_ibge_service() -> IBGEDataService:
    """Get or create IBGE data service instance"""
    global _ibge_service
    if _ibge_service is None:
        _ibge_service = IBGEDataService()
    return _ibge_service
