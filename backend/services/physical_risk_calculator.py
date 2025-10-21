"""
Physical Risk Calculator

Wrapper para physrisk-lib com integração de dados brasileiros.
Atualmente usa dados mock, mas preparado para integração real.

TODO: Integrar com:
- physrisk-lib para modelagem de risco
- Cemaden API para dados em tempo real
- INPE API para projeções climáticas
"""

import logging
from typing import Dict, Any, List, Optional
from backend.api.models.risk import (
    HazardType,
    RiskScenario,
    HazardIndicator,
    VulnerabilityIndicator,
)
from backend.services.mock_climate_data import MockClimateDataService
from backend.data.municipalities import get_municipality_data

logger = logging.getLogger(__name__)


class BrazilPhysicalRiskCalculator:
    """
    Calculador de risco físico climático para municípios brasileiros

    Arquitetura:
    1. Mock mode (atual): usa MockClimateDataService
    2. Hybrid mode (futuro): mock + physrisk-lib
    3. Full mode (produção): physrisk-lib + Cemaden + INPE
    """

    def __init__(self, use_mock: bool = True):
        """
        Inicializa calculador de risco

        Args:
            use_mock: Se True, usa dados mock. Se False, tenta usar physrisk-lib
        """
        self.use_mock = use_mock
        self.mock_service = MockClimateDataService()

        if not use_mock:
            try:
                # TODO: Inicializar physrisk-lib quando modo real for ativado
                # from physrisk import RiskCalculator
                # self.physrisk_api = RiskCalculator()
                logger.warning(
                    "physrisk-lib integration not yet implemented. Falling back to mock data."
                )
                self.use_mock = True
            except ImportError:
                logger.warning("physrisk-lib not available. Using mock data.")
                self.use_mock = True

    def calculate_municipality_risk(
        self,
        ibge_code: str,
        scenario: RiskScenario = RiskScenario.RCP45,
        year: int = 2030,
    ) -> Dict[str, Any]:
        """
        Calcula risco físico para um município

        Args:
            ibge_code: Código IBGE de 7 dígitos
            scenario: Cenário climático (RCP26, RCP45, RCP85)
            year: Ano de projeção (2030 ou 2050)

        Returns:
            Dict com scores de risco por hazard type

        Example:
            {
                "flood": {
                    "current": 0.45,
                    "projected_2030": 0.55,
                    "projected_2050": 0.65,
                    "data_source": "...",
                    "confidence": 0.75
                },
                ...
            }
        """
        logger.info(
            f"Calculating risk for {ibge_code} (scenario={scenario.value}, year={year})"
        )

        # Buscar dados do município
        muni_data = get_municipality_data(ibge_code)
        if not muni_data:
            raise ValueError(f"Municipality {ibge_code} not found in database")

        if self.use_mock:
            return self._calculate_with_mock(ibge_code, scenario, year, muni_data)
        else:
            return self._calculate_with_physrisk(ibge_code, scenario, year, muni_data)

    def _calculate_with_mock(
        self,
        ibge_code: str,
        scenario: RiskScenario,
        year: int,
        muni_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Cálculo usando dados mock"""
        # Obter dados de hazard do serviço mock
        hazard_data = self.mock_service.get_hazard_data(ibge_code, scenario, year)

        result = {}
        for hazard_type, data in hazard_data.items():
            # Buscar projeções para diferentes anos
            current_data = self.mock_service.get_hazard_data(
                ibge_code, scenario, 2024
            ).get(hazard_type, {})
            data_2030 = self.mock_service.get_hazard_data(
                ibge_code, scenario, 2030
            ).get(hazard_type, {})
            data_2050 = self.mock_service.get_hazard_data(
                ibge_code, scenario, 2050
            ).get(hazard_type, {})

            result[hazard_type.value] = {
                "current": current_data.get("risk_score", 0.0),
                "projected_2030": data_2030.get("risk_score", 0.0),
                "projected_2050": data_2050.get("risk_score", 0.0),
                "data_source": data.get("data_source", "MOCK"),
                "confidence": data.get("confidence", 0.5),
                "notes": data.get("notes", ""),
            }

        return result

    def _calculate_with_physrisk(
        self,
        ibge_code: str,
        scenario: RiskScenario,
        year: int,
        muni_data: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Cálculo usando physrisk-lib (TODO)"""
        # TODO: Implementar integração real com physrisk-lib
        #
        # from physrisk.api.v1 import PhysicalRisk
        # from physrisk.kernel.assets import RealEstateAsset
        #
        # risk_api = PhysicalRisk()
        # asset = RealEstateAsset(
        #     lat=muni_data["lat"],
        #     lon=muni_data["lon"],
        #     location=muni_data["name"]
        # )
        #
        # results = risk_api.get_asset_risk_measures(
        #     asset=asset,
        #     scenario=scenario.value,
        #     year=year
        # )
        #
        # return self._transform_physrisk_results(results)

        logger.warning("physrisk-lib not implemented yet, using mock data")
        return self._calculate_with_mock(ibge_code, scenario, year, muni_data)

    def build_hazard_indicators(
        self, ibge_code: str, scenario: RiskScenario = RiskScenario.RCP45
    ) -> List[HazardIndicator]:
        """
        Constrói lista de HazardIndicators para um município

        Args:
            ibge_code: Código IBGE
            scenario: Cenário climático

        Returns:
            Lista de HazardIndicator com dados de todos os hazards
        """
        hazard_scores = self.calculate_municipality_risk(ibge_code, scenario, 2030)

        indicators = []
        for hazard_type_str, data in hazard_scores.items():
            try:
                hazard_type = HazardType(hazard_type_str)
            except ValueError:
                logger.warning(f"Unknown hazard type: {hazard_type_str}")
                continue

            indicator = HazardIndicator(
                hazard_type=hazard_type,
                current_risk=data["current"],
                projected_2030=data["projected_2030"],
                projected_2050=data["projected_2050"],
                data_source=data["data_source"],
                confidence=data["confidence"],
            )
            indicators.append(indicator)

        return indicators

    def calculate_vulnerability(self, ibge_code: str) -> VulnerabilityIndicator:
        """
        Calcula indicador de vulnerabilidade para município

        Args:
            ibge_code: Código IBGE

        Returns:
            VulnerabilityIndicator com métricas de vulnerabilidade
        """
        muni_data = get_municipality_data(ibge_code)
        if not muni_data:
            raise ValueError(f"Municipality {ibge_code} not found")

        # Calcular população exposta (baseado em % vulnerável)
        population_exposed = int(
            muni_data["population"] * muni_data["vulnerable_population_pct"]
        )

        # Calcular adaptive capacity score (0.0-1.0)
        # Fatores: PIB per capita, área verde, infraestrutura
        gdp_score = min(muni_data["gdp_per_capita_brl"] / 80000, 1.0)  # Normalizado
        green_score = min(muni_data["green_area_per_capita_m2"] / 100, 1.0)
        infra_score = min(muni_data["critical_infrastructure"] / 500, 1.0)

        adaptive_capacity = (gdp_score + green_score + infra_score) / 3

        return VulnerabilityIndicator(
            population_exposed=population_exposed,
            critical_infrastructure_count=muni_data["critical_infrastructure"],
            vulnerable_population_pct=muni_data["vulnerable_population_pct"],
            adaptive_capacity_score=round(adaptive_capacity, 2),
        )

    def calculate_overall_risk_score(
        self, hazards: List[HazardIndicator], vulnerability: VulnerabilityIndicator
    ) -> float:
        """
        Calcula score geral de risco (0.0-1.0)

        Combina:
        - Média dos riscos de hazards projetados para 2030
        - Vulnerabilidade da população
        - Capacidade adaptativa

        Args:
            hazards: Lista de indicadores de hazard
            vulnerability: Indicador de vulnerabilidade

        Returns:
            Score de risco geral (0.0-1.0)
        """
        if not hazards:
            return 0.0

        # Média dos riscos projetados para 2030
        avg_hazard_risk = sum(h.projected_2030 for h in hazards) / len(hazards)

        # Fator de vulnerabilidade (0.0-1.0)
        vuln_factor = vulnerability.vulnerable_population_pct

        # Fator de capacidade adaptativa (inverso - menor capacidade = maior risco)
        adaptive_factor = 1.0 - vulnerability.adaptive_capacity_score

        # Score combinado (pesos: hazard=50%, vulnerabilidade=30%, capacidade=20%)
        overall_score = (
            avg_hazard_risk * 0.5 + vuln_factor * 0.3 + adaptive_factor * 0.2
        )

        return round(min(overall_score, 1.0), 3)

    def generate_recommendations(
        self, hazards: List[HazardIndicator], vulnerability: VulnerabilityIndicator
    ) -> List[str]:
        """
        Gera recomendações de adaptação baseadas em riscos identificados

        Args:
            hazards: Lista de hazard indicators
            vulnerability: Indicador de vulnerabilidade

        Returns:
            Lista de recomendações em português
        """
        recommendations = []

        # Recomendações baseadas em hazards específicos
        for hazard in hazards:
            if hazard.projected_2030 > 0.6:  # Alto risco
                if hazard.hazard_type == HazardType.FLOOD:
                    recommendations.append(
                        "📍 Risco de inundação alto: Implementar sistema de drenagem sustentável, "
                        "criar áreas de retenção (parques alagáveis), mapear zonas de risco"
                    )
                elif hazard.hazard_type == HazardType.HEAT_STRESS:
                    recommendations.append(
                        "🌡️ Risco de estresse térmico alto: Aumentar cobertura vegetal urbana, "
                        "criar corredores verdes, implementar tetos verdes em edifícios públicos"
                    )
                elif hazard.hazard_type == HazardType.DROUGHT:
                    recommendations.append(
                        "💧 Risco de seca alto: Diversificar fontes de abastecimento, "
                        "implementar reuso de água, conservar aquíferos, reduzir perdas na rede"
                    )
                elif hazard.hazard_type == HazardType.LANDSLIDE:
                    recommendations.append(
                        "⛰️ Risco de deslizamento alto: Relocar famílias de áreas de risco, "
                        "implementar contenções, sistema de alerta precoce, drenagem em encostas"
                    )
                elif hazard.hazard_type == HazardType.COASTAL_INUNDATION:
                    recommendations.append(
                        "🌊 Risco de inundação costeira alto: Construir barreiras naturais (manguezais, dunas), "
                        "restringir ocupação em áreas vulneráveis, plano de evacuação"
                    )

        # Recomendações baseadas em vulnerabilidade
        if vulnerability.vulnerable_population_pct > 0.3:
            recommendations.append(
                "👥 Alta população vulnerável: Priorizar ações em comunidades de baixa renda, "
                "criar abrigos emergenciais, programas de conscientização"
            )

        if vulnerability.adaptive_capacity_score < 0.5:
            recommendations.append(
                "🔧 Baixa capacidade adaptativa: Investir em infraestrutura resiliente, "
                "capacitação técnica, parcerias público-privadas para financiamento"
            )

        # Recomendações gerais (Lei 14.904)
        recommendations.append(
            "📋 Elaborar Plano Municipal de Adaptação às Mudanças Climáticas (Lei 14.904/2024)"
        )
        recommendations.append(
            "📊 Implementar sistema de monitoramento contínuo de riscos climáticos"
        )

        return recommendations


# Instância global (singleton pattern)
_calculator_instance: Optional[BrazilPhysicalRiskCalculator] = None


def get_risk_calculator(use_mock: bool = True) -> BrazilPhysicalRiskCalculator:
    """
    Retorna instância global do calculador de risco

    Args:
        use_mock: Se True, usa dados mock

    Returns:
        BrazilPhysicalRiskCalculator instance
    """
    global _calculator_instance
    if _calculator_instance is None:
        _calculator_instance = BrazilPhysicalRiskCalculator(use_mock=use_mock)
    return _calculator_instance
