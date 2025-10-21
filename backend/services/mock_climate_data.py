"""
Mock Climate Data Service

Provides realistic synthetic climate risk data for municipalities
while real API integrations (Cemaden, INPE, physrisk-lib) are being developed.

Data is based on:
- Historical patterns from Cemaden alerts
- INPE climate projections (RCP scenarios)
- Regional climate characteristics
- Urban vulnerability assessments
"""

from typing import Dict, Any, List
from backend.api.models.risk import HazardType, RiskScenario


class MockClimateDataService:
    """
    Mock service for climate risk data

    Note: This is TEMPORARY. Replace with real API calls to:
    - Cemaden (current risks and alerts)
    - INPE (climate projections)
    - physrisk-lib (risk modeling)
    """

    # Mock hazard data por município (baseado em padrões reais)
    HAZARD_DATA: Dict[str, Dict[HazardType, Dict[str, Any]]] = {
        # São Paulo - Alta urbanização, enchentes, ilhas de calor
        "3550308": {
            HazardType.FLOOD: {
                "current": 0.45,
                "rcp26_2030": 0.48,
                "rcp26_2050": 0.52,
                "rcp45_2030": 0.55,
                "rcp45_2050": 0.65,
                "rcp85_2030": 0.60,
                "rcp85_2050": 0.75,
                "data_source": "MOCK - Baseado em histórico Cemaden 2015-2023",
                "confidence": 0.75,
                "notes": "Rios Tietê e Pinheiros frequentemente transbordam",
            },
            HazardType.HEAT_STRESS: {
                "current": 0.38,
                "rcp26_2030": 0.45,
                "rcp26_2050": 0.53,
                "rcp45_2030": 0.52,
                "rcp45_2050": 0.68,
                "rcp85_2030": 0.58,
                "rcp85_2050": 0.82,
                "data_source": "MOCK - Baseado em projeções INPE",
                "confidence": 0.70,
                "notes": "Ilha de calor urbana intensifica risco",
            },
            HazardType.DROUGHT: {
                "current": 0.25,
                "rcp26_2030": 0.28,
                "rcp26_2050": 0.32,
                "rcp45_2030": 0.35,
                "rcp45_2050": 0.45,
                "rcp85_2030": 0.42,
                "rcp85_2050": 0.58,
                "data_source": "MOCK - Sistema Cantareira",
                "confidence": 0.65,
                "notes": "Crise hídrica 2014-2015 como referência",
            },
        },

        # Rio de Janeiro - Deslizamentos, enchentes, calor extremo
        "3304557": {
            HazardType.FLOOD: {
                "current": 0.52,
                "rcp26_2030": 0.55,
                "rcp26_2050": 0.60,
                "rcp45_2030": 0.62,
                "rcp45_2050": 0.72,
                "rcp85_2030": 0.68,
                "rcp85_2050": 0.82,
                "data_source": "MOCK - Cemaden + histórico",
                "confidence": 0.80,
                "notes": "Eventos extremos de chuva (>100mm/h) frequentes",
            },
            HazardType.LANDSLIDE: {
                "current": 0.58,
                "rcp26_2030": 0.62,
                "rcp26_2050": 0.67,
                "rcp45_2030": 0.68,
                "rcp45_2050": 0.78,
                "rcp85_2030": 0.73,
                "rcp85_2050": 0.88,
                "data_source": "MOCK - GeoRio + Cemaden",
                "confidence": 0.85,
                "notes": "Favelas em encostas com alta vulnerabilidade",
            },
            HazardType.HEAT_STRESS: {
                "current": 0.42,
                "rcp26_2030": 0.48,
                "rcp26_2050": 0.55,
                "rcp45_2030": 0.58,
                "rcp45_2050": 0.70,
                "rcp85_2030": 0.65,
                "rcp85_2050": 0.85,
                "data_source": "MOCK - INPE",
                "confidence": 0.72,
                "notes": "Temperaturas >40°C projetadas para 2050",
            },
        },

        # Salvador - Inundações costeiras, calor
        "2927408": {
            HazardType.COASTAL_INUNDATION: {
                "current": 0.35,
                "rcp26_2030": 0.40,
                "rcp26_2050": 0.48,
                "rcp45_2030": 0.48,
                "rcp45_2050": 0.62,
                "rcp85_2030": 0.55,
                "rcp85_2050": 0.78,
                "data_source": "MOCK - IPCC + elevação do nível do mar",
                "confidence": 0.70,
                "notes": "Elevação de 30-60cm até 2050",
            },
            HazardType.FLOOD: {
                "current": 0.40,
                "rcp26_2030": 0.45,
                "rcp26_2050": 0.52,
                "rcp45_2030": 0.52,
                "rcp45_2050": 0.63,
                "rcp85_2030": 0.58,
                "rcp85_2050": 0.75,
                "data_source": "MOCK - Cemaden",
                "confidence": 0.68,
                "notes": "Sistema de drenagem insuficiente",
            },
            HazardType.HEAT_STRESS: {
                "current": 0.48,
                "rcp26_2030": 0.55,
                "rcp26_2050": 0.63,
                "rcp45_2030": 0.62,
                "rcp45_2050": 0.75,
                "rcp85_2030": 0.70,
                "rcp85_2050": 0.88,
                "data_source": "MOCK - INPE",
                "confidence": 0.75,
                "notes": "Nordeste com maior aquecimento projetado",
            },
        },

        # Fortaleza - Costa vulnerável, seca, calor
        "2304400": {
            HazardType.COASTAL_INUNDATION: {
                "current": 0.42,
                "rcp26_2030": 0.48,
                "rcp26_2050": 0.58,
                "rcp45_2030": 0.55,
                "rcp45_2050": 0.70,
                "rcp85_2030": 0.62,
                "rcp85_2050": 0.82,
                "data_source": "MOCK - Erosão costeira + nível do mar",
                "confidence": 0.73,
                "notes": "Praia do Futuro e Beira Mar vulneráveis",
            },
            HazardType.DROUGHT: {
                "current": 0.55,
                "rcp26_2030": 0.60,
                "rcp26_2050": 0.68,
                "rcp45_2030": 0.68,
                "rcp45_2050": 0.80,
                "rcp85_2030": 0.75,
                "rcp85_2050": 0.90,
                "data_source": "MOCK - Semiárido nordestino",
                "confidence": 0.82,
                "notes": "Secas plurianuais previstas",
            },
            HazardType.HEAT_STRESS: {
                "current": 0.52,
                "rcp26_2030": 0.60,
                "rcp26_2050": 0.70,
                "rcp45_2030": 0.68,
                "rcp45_2050": 0.82,
                "rcp85_2030": 0.75,
                "rcp85_2050": 0.92,
                "data_source": "MOCK - INPE",
                "confidence": 0.78,
                "notes": "Aumento de 3-5°C até 2050 (RCP 8.5)",
            },
        },

        # Brasília - Seca, queimadas
        "5300108": {
            HazardType.DROUGHT: {
                "current": 0.48,
                "rcp26_2030": 0.52,
                "rcp26_2050": 0.60,
                "rcp45_2030": 0.60,
                "rcp45_2050": 0.73,
                "rcp85_2030": 0.68,
                "rcp85_2050": 0.85,
                "data_source": "MOCK - Cerrado + sistema Descoberto",
                "confidence": 0.75,
                "notes": "Aquíferos em declínio",
            },
            HazardType.HEAT_STRESS: {
                "current": 0.35,
                "rcp26_2030": 0.42,
                "rcp26_2050": 0.52,
                "rcp45_2030": 0.50,
                "rcp45_2050": 0.65,
                "rcp85_2030": 0.58,
                "rcp85_2050": 0.78,
                "data_source": "MOCK - INPE",
                "confidence": 0.70,
                "notes": "Planalto Central com menor aquecimento que Nordeste",
            },
        },

        # Curitiba - Inundações, frio extremo (menor risco de calor)
        "4106902": {
            HazardType.FLOOD: {
                "current": 0.32,
                "rcp26_2030": 0.38,
                "rcp26_2050": 0.45,
                "rcp45_2030": 0.45,
                "rcp45_2050": 0.58,
                "rcp85_2030": 0.52,
                "rcp85_2050": 0.70,
                "data_source": "MOCK - Rio Iguaçu",
                "confidence": 0.72,
                "notes": "Bom sistema de drenagem reduz risco",
            },
            HazardType.HEAT_STRESS: {
                "current": 0.18,
                "rcp26_2030": 0.22,
                "rcp26_2050": 0.28,
                "rcp45_2030": 0.28,
                "rcp45_2050": 0.38,
                "rcp85_2030": 0.35,
                "rcp85_2050": 0.52,
                "data_source": "MOCK - INPE",
                "confidence": 0.68,
                "notes": "Clima subtropical - menor risco de calor extremo",
            },
        },

        # Manaus - Enchentes amazônicas, calor/umidade
        "1302603": {
            HazardType.FLOOD: {
                "current": 0.62,
                "rcp26_2030": 0.68,
                "rcp26_2050": 0.75,
                "rcp45_2030": 0.75,
                "rcp45_2050": 0.85,
                "rcp85_2030": 0.80,
                "rcp85_2050": 0.92,
                "data_source": "MOCK - Rio Negro + regime de chuvas",
                "confidence": 0.80,
                "notes": "Cheias históricas (2012, 2021)",
            },
            HazardType.HEAT_STRESS: {
                "current": 0.45,
                "rcp26_2030": 0.52,
                "rcp26_2050": 0.62,
                "rcp45_2030": 0.60,
                "rcp45_2050": 0.75,
                "rcp85_2030": 0.68,
                "rcp85_2050": 0.88,
                "data_source": "MOCK - INPE + desmatamento",
                "confidence": 0.77,
                "notes": "Desmatamento intensifica ilha de calor",
            },
        },

        # Recife - Inundações costeiras, deslizamentos
        "2611606": {
            HazardType.COASTAL_INUNDATION: {
                "current": 0.50,
                "rcp26_2030": 0.56,
                "rcp26_2050": 0.65,
                "rcp45_2030": 0.63,
                "rcp45_2050": 0.77,
                "rcp85_2030": 0.70,
                "rcp85_2050": 0.88,
                "data_source": "MOCK - Nível do mar + ressaca",
                "confidence": 0.78,
                "notes": "Boa Viagem altamente vulnerável",
            },
            HazardType.FLOOD: {
                "current": 0.58,
                "rcp26_2030": 0.63,
                "rcp26_2050": 0.70,
                "rcp45_2030": 0.70,
                "rcp45_2050": 0.82,
                "rcp85_2030": 0.77,
                "rcp85_2050": 0.90,
                "data_source": "MOCK - Cemaden",
                "confidence": 0.80,
                "notes": "Chuvas intensas causam alagamentos frequentes",
            },
            HazardType.LANDSLIDE: {
                "current": 0.48,
                "rcp26_2030": 0.53,
                "rcp26_2050": 0.60,
                "rcp45_2030": 0.60,
                "rcp45_2050": 0.72,
                "rcp85_2030": 0.67,
                "rcp85_2050": 0.82,
                "data_source": "MOCK - Morros + Cemaden",
                "confidence": 0.75,
                "notes": "Comunidades em morros vulneráveis",
            },
        },

        # Porto Alegre - Enchentes (Guaíba), tempestades
        "4314902": {
            HazardType.FLOOD: {
                "current": 0.42,
                "rcp26_2030": 0.48,
                "rcp26_2050": 0.56,
                "rcp45_2030": 0.56,
                "rcp45_2050": 0.68,
                "rcp85_2030": 0.63,
                "rcp85_2050": 0.80,
                "data_source": "MOCK - Lago Guaíba + chuvas",
                "confidence": 0.77,
                "notes": "Enchentes históricas do Guaíba",
            },
            HazardType.HEAT_STRESS: {
                "current": 0.22,
                "rcp26_2030": 0.28,
                "rcp26_2050": 0.35,
                "rcp45_2030": 0.35,
                "rcp45_2050": 0.48,
                "rcp85_2030": 0.42,
                "rcp85_2050": 0.62,
                "data_source": "MOCK - INPE",
                "confidence": 0.70,
                "notes": "Clima temperado - menor risco",
            },
        },

        # Belém - Enchentes, calor/umidade
        "1501402": {
            HazardType.FLOOD: {
                "current": 0.65,
                "rcp26_2030": 0.70,
                "rcp26_2050": 0.77,
                "rcp45_2030": 0.77,
                "rcp45_2050": 0.87,
                "rcp85_2030": 0.83,
                "rcp85_2050": 0.93,
                "data_source": "MOCK - Bacias + maré",
                "confidence": 0.82,
                "notes": "Baixadas alagáveis + maré alta",
            },
            HazardType.COASTAL_INUNDATION: {
                "current": 0.38,
                "rcp26_2030": 0.44,
                "rcp26_2050": 0.53,
                "rcp45_2030": 0.52,
                "rcp45_2050": 0.67,
                "rcp85_2030": 0.60,
                "rcp85_2050": 0.80,
                "data_source": "MOCK - Estuário + nível do mar",
                "confidence": 0.73,
                "notes": "Região estuarina vulnerável",
            },
            HazardType.HEAT_STRESS: {
                "current": 0.50,
                "rcp26_2030": 0.57,
                "rcp26_2050": 0.66,
                "rcp45_2030": 0.65,
                "rcp45_2050": 0.78,
                "rcp85_2030": 0.72,
                "rcp85_2050": 0.90,
                "data_source": "MOCK - INPE + umidade",
                "confidence": 0.75,
                "notes": "Calor + umidade = stress térmico alto",
            },
        },
    }

    @staticmethod
    def get_hazard_data(
        ibge_code: str,
        scenario: RiskScenario = RiskScenario.RCP45,
        year: int = 2030,
    ) -> Dict[HazardType, Dict[str, Any]]:
        """
        Retorna dados de hazards para um município em cenário/ano específico

        Args:
            ibge_code: Código IBGE do município
            scenario: Cenário climático (RCP26, RCP45, RCP85)
            year: Ano de projeção (2030 ou 2050)

        Returns:
            Dict com HazardType como chave e dados do hazard
        """
        if ibge_code not in MockClimateDataService.HAZARD_DATA:
            # Retorna dados padrão para municípios não catalogados
            return MockClimateDataService._get_default_hazard_data(scenario, year)

        raw_data = MockClimateDataService.HAZARD_DATA[ibge_code]
        result = {}

        # Determinar chave de projeção baseada em cenário e ano
        if year <= 2025:
            projection_key = "current"
        else:
            scenario_prefix = scenario.value.lower()  # rcp26, rcp45, rcp85
            year_suffix = 2030 if year <= 2040 else 2050
            projection_key = f"{scenario_prefix}_{year_suffix}"

        for hazard_type, hazard_data in raw_data.items():
            result[hazard_type] = {
                "risk_score": hazard_data.get(projection_key, 0.0),
                "data_source": hazard_data.get("data_source", "MOCK"),
                "confidence": hazard_data.get("confidence", 0.5),
                "notes": hazard_data.get("notes", ""),
                "scenario": scenario.value,
                "year": year,
            }

        return result

    @staticmethod
    def _get_default_hazard_data(
        scenario: RiskScenario, year: int
    ) -> Dict[HazardType, Dict[str, Any]]:
        """Dados padrão para municípios sem dados específicos"""
        base_risk = 0.3
        scenario_multiplier = {
            RiskScenario.RCP26: 1.1,
            RiskScenario.RCP45: 1.3,
            RiskScenario.RCP85: 1.6,
        }
        year_multiplier = 1.0 + ((year - 2024) / 100)  # +1% por ano

        risk_score = min(
            base_risk * scenario_multiplier[scenario] * year_multiplier, 0.95
        )

        return {
            HazardType.FLOOD: {
                "risk_score": risk_score,
                "data_source": "MOCK - Dados padrão",
                "confidence": 0.4,
                "notes": "Município sem dados específicos",
                "scenario": scenario.value,
                "year": year,
            }
        }

    @staticmethod
    def get_all_hazards_for_municipality(ibge_code: str) -> List[HazardType]:
        """Retorna lista de hazards disponíveis para um município"""
        if ibge_code not in MockClimateDataService.HAZARD_DATA:
            return [HazardType.FLOOD]  # Default

        return list(MockClimateDataService.HAZARD_DATA[ibge_code].keys())


# Alias para compatibilidade
get_mock_climate_data = MockClimateDataService.get_hazard_data
