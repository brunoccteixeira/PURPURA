"""
Brazilian Municipalities Database

Initial dataset with 10 priority municipalities for MVP.
Data sources:
- IBGE (códigos, população Censo 2022)
- Geonames (coordenadas)
- Estimativas de infraestrutura crítica e população vulnerável
"""

from typing import Dict, Any, Optional

# Database de municípios prioritários (10 maiores cidades do Brasil)
MUNICIPALITIES: Dict[str, Dict[str, Any]] = {
    "3550308": {  # São Paulo - SP
        "name": "São Paulo",
        "state": "SP",
        "state_name": "São Paulo",
        "lat": -23.5505,
        "lon": -46.6333,
        "population": 11451245,  # Censo 2022
        "area_km2": 1521.11,
        "critical_infrastructure": 450,  # Hospitais, escolas, estações de tratamento
        "vulnerable_population_pct": 0.28,  # ~28% em áreas de risco
        "gdp_per_capita_brl": 52796,
        "urban_area_pct": 0.99,
        "green_area_per_capita_m2": 13.2,
    },
    "3304557": {  # Rio de Janeiro - RJ
        "name": "Rio de Janeiro",
        "state": "RJ",
        "state_name": "Rio de Janeiro",
        "lat": -22.9068,
        "lon": -43.1729,
        "population": 6211223,
        "area_km2": 1200.28,
        "critical_infrastructure": 320,
        "vulnerable_population_pct": 0.35,  # Favelas em encostas
        "gdp_per_capita_brl": 48275,
        "urban_area_pct": 0.98,
        "green_area_per_capita_m2": 54.8,
    },
    "2927408": {  # Salvador - BA
        "name": "Salvador",
        "state": "BA",
        "state_name": "Bahia",
        "lat": -12.9714,
        "lon": -38.5014,
        "population": 2886698,
        "area_km2": 692.82,
        "critical_infrastructure": 180,
        "vulnerable_population_pct": 0.32,
        "gdp_per_capita_brl": 22891,
        "urban_area_pct": 1.0,
        "green_area_per_capita_m2": 18.5,
    },
    "2304400": {  # Fortaleza - CE
        "name": "Fortaleza",
        "state": "CE",
        "state_name": "Ceará",
        "lat": -3.7172,
        "lon": -38.5433,
        "population": 2428678,
        "area_km2": 314.93,
        "critical_infrastructure": 150,
        "vulnerable_population_pct": 0.38,  # Áreas costeiras vulneráveis
        "gdp_per_capita_brl": 21065,
        "urban_area_pct": 0.97,
        "green_area_per_capita_m2": 12.1,
    },
    "5300108": {  # Brasília - DF
        "name": "Brasília",
        "state": "DF",
        "state_name": "Distrito Federal",
        "lat": -15.7939,
        "lon": -47.8828,
        "population": 2817068,
        "area_km2": 5760.78,
        "critical_infrastructure": 220,
        "vulnerable_population_pct": 0.18,
        "gdp_per_capita_brl": 79977,
        "urban_area_pct": 0.96,
        "green_area_per_capita_m2": 95.3,
    },
    "4106902": {  # Curitiba - PR
        "name": "Curitiba",
        "state": "PR",
        "state_name": "Paraná",
        "lat": -25.4284,
        "lon": -49.2733,
        "population": 1773718,
        "area_km2": 430.90,
        "critical_infrastructure": 200,
        "vulnerable_population_pct": 0.15,
        "gdp_per_capita_brl": 45327,
        "urban_area_pct": 0.98,
        "green_area_per_capita_m2": 64.5,
    },
    "1302603": {  # Manaus - AM
        "name": "Manaus",
        "state": "AM",
        "state_name": "Amazonas",
        "lat": -3.1190,
        "lon": -60.0217,
        "population": 2063547,
        "area_km2": 11401.06,
        "critical_infrastructure": 140,
        "vulnerable_population_pct": 0.42,  # Áreas de várzea
        "gdp_per_capita_brl": 29341,
        "urban_area_pct": 0.99,
        "green_area_per_capita_m2": 312.7,  # Floresta urbana
    },
    "2611606": {  # Recife - PE
        "name": "Recife",
        "state": "PE",
        "state_name": "Pernambuco",
        "lat": -8.0476,
        "lon": -34.8770,
        "population": 1488920,
        "area_km2": 218.50,
        "critical_infrastructure": 160,
        "vulnerable_population_pct": 0.44,  # Morros e áreas de mangue
        "gdp_per_capita_brl": 28237,
        "urban_area_pct": 1.0,
        "green_area_per_capita_m2": 9.8,
    },
    "4314902": {  # Porto Alegre - RS
        "name": "Porto Alegre",
        "state": "RS",
        "state_name": "Rio Grande do Sul",
        "lat": -30.0346,
        "lon": -51.2177,
        "population": 1332570,
        "area_km2": 496.68,
        "critical_infrastructure": 180,
        "vulnerable_population_pct": 0.22,
        "gdp_per_capita_brl": 48149,
        "urban_area_pct": 0.99,
        "green_area_per_capita_m2": 23.4,
    },
    "1501402": {  # Belém - PA
        "name": "Belém",
        "state": "PA",
        "state_name": "Pará",
        "lat": -1.4558,
        "lon": -48.5039,
        "population": 1303389,
        "area_km2": 1059.46,
        "critical_infrastructure": 120,
        "vulnerable_population_pct": 0.48,  # Áreas de baixada alagável
        "gdp_per_capita_brl": 20608,
        "urban_area_pct": 0.99,
        "green_area_per_capita_m2": 15.2,
    },
}


def get_municipality_data(ibge_code: str) -> Optional[Dict[str, Any]]:
    """
    Retorna dados de um município pelo código IBGE

    Args:
        ibge_code: Código IBGE de 7 dígitos (ex: "3550308")

    Returns:
        Dict com dados do município ou None se não encontrado
    """
    return MUNICIPALITIES.get(ibge_code)


def get_all_municipalities() -> Dict[str, Dict[str, Any]]:
    """
    Retorna todos os municípios disponíveis no database

    Returns:
        Dict com ibge_code como chave
    """
    return MUNICIPALITIES


def search_municipalities_by_name(name: str) -> list[Dict[str, Any]]:
    """
    Busca municípios por nome (case-insensitive, partial match)

    Args:
        name: Nome ou parte do nome do município

    Returns:
        Lista de municípios que correspondem à busca
    """
    name_lower = name.lower()
    results = []

    for ibge_code, data in MUNICIPALITIES.items():
        if name_lower in data["name"].lower():
            results.append({
                "ibge_code": ibge_code,
                **data
            })

    return results


def search_municipalities_by_state(state: str) -> list[Dict[str, Any]]:
    """
    Busca municípios por UF (ex: "SP", "RJ")

    Args:
        state: Sigla do estado (2 letras)

    Returns:
        Lista de municípios do estado
    """
    state_upper = state.upper()
    results = []

    for ibge_code, data in MUNICIPALITIES.items():
        if data["state"] == state_upper:
            results.append({
                "ibge_code": ibge_code,
                **data
            })

    return results


def get_municipality_stats() -> Dict[str, Any]:
    """
    Retorna estatísticas gerais do database de municípios

    Returns:
        Dict com estatísticas agregadas
    """
    total_population = sum(m["population"] for m in MUNICIPALITIES.values())
    avg_vulnerable_pct = sum(m["vulnerable_population_pct"] for m in MUNICIPALITIES.values()) / len(MUNICIPALITIES)

    states = set(m["state"] for m in MUNICIPALITIES.values())

    return {
        "total_municipalities": len(MUNICIPALITIES),
        "total_population": total_population,
        "average_vulnerable_population_pct": round(avg_vulnerable_pct, 3),
        "states_covered": sorted(states),
        "states_count": len(states),
    }


# Validação na importação
if __name__ == "__main__":
    print("✅ Municipalities Database")
    print(f"  Total: {len(MUNICIPALITIES)} municípios")

    stats = get_municipality_stats()
    print(f"  População total: {stats['total_population']:,}")
    print(f"  Estados: {', '.join(stats['states_covered'])}")
    print(f"  Média de população vulnerável: {stats['average_vulnerable_population_pct']:.1%}")

    # Teste de busca
    sp_results = search_municipalities_by_state("SP")
    print(f"\n  Municípios em SP: {len(sp_results)}")

    search_results = search_municipalities_by_name("são")
    print(f"  Busca por 'são': {len(search_results)} resultado(s)")
