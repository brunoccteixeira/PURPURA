"""
Integration tests for Physical Risk API endpoints

Tests cover:
- GET /municipality/{ibge_code}
- GET /hazards/{ibge_code}
- POST /scenario-analysis
- GET /municipalities
- GET /municipalities/{ibge_code}/info
"""

import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add repo root to path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from backend.api.main import app


# Create test client
client = TestClient(app)


# ============================================================================
# Municipality Risk Endpoint Tests
# ============================================================================

@pytest.mark.integration
class TestMunicipalityRiskEndpoint:
    """Tests for GET /api/v1/risk/municipality/{ibge_code}"""

    def test_get_risk_sao_paulo_success(self):
        """Test successful risk assessment for São Paulo"""
        response = client.get("/api/v1/risk/municipality/3550308")

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "ibge_code" in data
        assert data["ibge_code"] == "3550308"
        assert data["municipality_name"] == "São Paulo"
        assert "scenario" in data
        assert "overall_risk_score" in data
        assert "hazards" in data
        assert "vulnerability" in data
        assert "recommendations" in data

        # Verify risk score range
        assert 0.0 <= data["overall_risk_score"] <= 1.0

        # Verify hazards array
        assert isinstance(data["hazards"], list)
        assert len(data["hazards"]) > 0

        # Verify vulnerability indicators
        vuln = data["vulnerability"]
        assert "population_exposed" in vuln
        assert "critical_infrastructure_count" in vuln
        assert "vulnerable_population_pct" in vuln
        assert "adaptive_capacity_score" in vuln

    def test_get_risk_with_rcp85_scenario(self):
        """Test risk assessment with RCP 8.5 (high emissions) scenario"""
        response = client.get("/api/v1/risk/municipality/3550308?scenario=rcp85")

        assert response.status_code == 200
        data = response.json()
        assert data["scenario"] == "rcp85"

    def test_get_risk_with_h3_grid(self):
        """Test risk assessment with H3 hexagonal grid data"""
        response = client.get(
            "/api/v1/risk/municipality/3550308?include_h3_grid=true"
        )

        assert response.status_code == 200
        data = response.json()

        # Verify H3 grid is included
        assert "h3_grid_data" in data
        assert data["h3_grid_data"] is not None
        assert isinstance(data["h3_grid_data"], dict)

        # Verify H3 cell IDs format (should be hexadecimal strings)
        for cell_id, risk_score in data["h3_grid_data"].items():
            assert isinstance(cell_id, str)
            assert len(cell_id) == 15  # H3 cell IDs are 15 chars
            assert isinstance(risk_score, (int, float))
            assert 0.0 <= risk_score <= 1.0

    def test_get_risk_without_h3_grid(self):
        """Test that H3 grid is not included by default"""
        response = client.get("/api/v1/risk/municipality/3550308")

        assert response.status_code == 200
        data = response.json()
        assert data["h3_grid_data"] is None

    def test_get_risk_rio_de_janeiro(self):
        """Test risk assessment for Rio de Janeiro"""
        response = client.get("/api/v1/risk/municipality/3304557")

        assert response.status_code == 200
        data = response.json()
        assert data["municipality_name"] == "Rio de Janeiro"

    def test_get_risk_invalid_ibge_code(self):
        """Test error handling for invalid IBGE code"""
        response = client.get("/api/v1/risk/municipality/9999999")

        assert response.status_code == 404
        data = response.json()
        assert "detail" in data
        assert "not found" in data["detail"].lower()

    def test_get_risk_malformed_ibge_code(self):
        """Test error handling for malformed IBGE code"""
        response = client.get("/api/v1/risk/municipality/invalid")

        assert response.status_code == 404


# ============================================================================
# Hazards Endpoint Tests
# ============================================================================

@pytest.mark.integration
class TestHazardsEndpoint:
    """Tests for GET /api/v1/risk/hazards/{ibge_code}"""

    def test_get_hazards_sao_paulo(self):
        """Test hazard indicators for São Paulo"""
        response = client.get("/api/v1/risk/hazards/3550308")

        assert response.status_code == 200
        data = response.json()

        # Verify response is array of hazard indicators
        assert isinstance(data, list)
        assert len(data) > 0

        # Verify hazard structure
        hazard = data[0]
        assert "hazard_type" in hazard
        assert "current_risk" in hazard
        assert "projected_2030" in hazard
        assert "projected_2050" in hazard
        assert "data_source" in hazard
        assert "confidence" in hazard

        # Verify risk progression (2050 >= 2030 >= current)
        assert hazard["projected_2050"] >= hazard["projected_2030"]

    def test_get_hazards_filter_by_type_flood(self):
        """Test filtering hazards by type (flood)"""
        response = client.get(
            "/api/v1/risk/hazards/3550308?hazard_type=flood"
        )

        assert response.status_code == 200
        data = response.json()

        # All returned hazards should be flood type
        for hazard in data:
            assert hazard["hazard_type"] == "flood"

    def test_get_hazards_filter_by_type_heat_stress(self):
        """Test filtering hazards by type (heat_stress)"""
        response = client.get(
            "/api/v1/risk/hazards/3550308?hazard_type=heat_stress"
        )

        assert response.status_code == 200
        data = response.json()

        for hazard in data:
            assert hazard["hazard_type"] == "heat_stress"

    def test_get_hazards_with_scenario(self):
        """Test hazards with specific climate scenario"""
        response = client.get(
            "/api/v1/risk/hazards/3550308?scenario=rcp85"
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0

    def test_get_hazards_invalid_municipality(self):
        """Test error for invalid municipality"""
        response = client.get("/api/v1/risk/hazards/9999999")

        assert response.status_code == 404


# ============================================================================
# Scenario Analysis Endpoint Tests
# ============================================================================

@pytest.mark.integration
class TestScenarioAnalysisEndpoint:
    """Tests for POST /api/v1/risk/scenario-analysis"""

    def test_scenario_analysis_single_municipality(self):
        """Test scenario analysis for single municipality"""
        response = client.post(
            "/api/v1/risk/scenario-analysis"
            "?ibge_codes=3550308"
            "&scenarios=rcp45&scenarios=rcp85"
            "&years=2030&years=2050"
        )

        assert response.status_code == 202
        data = response.json()

        # Verify response structure
        assert "task_id" in data
        assert "status" in data
        assert data["status"] == "processing"
        assert "municipalities_count" in data
        assert data["municipalities_count"] == 1
        assert "scenarios_count" in data
        assert data["scenarios_count"] == 2

    def test_scenario_analysis_multiple_municipalities(self):
        """Test scenario analysis for multiple municipalities"""
        response = client.post(
            "/api/v1/risk/scenario-analysis"
            "?ibge_codes=3550308&ibge_codes=3304557&ibge_codes=4106902"
            "&scenarios=rcp45&scenarios=rcp85"
        )

        assert response.status_code == 202
        data = response.json()
        assert data["municipalities_count"] == 3

    def test_scenario_analysis_invalid_municipality(self):
        """Test error handling for invalid municipality in batch"""
        response = client.post(
            "/api/v1/risk/scenario-analysis"
            "?ibge_codes=3550308&ibge_codes=9999999"
        )

        assert response.status_code == 400
        data = response.json()
        assert "invalid" in data["detail"].lower()

    def test_scenario_analysis_defaults(self):
        """Test scenario analysis with default parameters"""
        response = client.post(
            "/api/v1/risk/scenario-analysis?ibge_codes=3550308"
        )

        assert response.status_code == 202
        data = response.json()

        # Should use default scenarios (RCP45, RCP85) and years (2030, 2050)
        assert data["scenarios_count"] == 2
        assert data["years_count"] == 2


# ============================================================================
# Municipalities List Endpoint Tests
# ============================================================================

@pytest.mark.integration
class TestMunicipalitiesListEndpoint:
    """Tests for GET /api/v1/risk/municipalities"""

    def test_list_municipalities(self):
        """Test listing all available municipalities"""
        response = client.get("/api/v1/risk/municipalities")

        assert response.status_code == 200
        data = response.json()

        # Verify structure
        assert "total" in data
        assert "municipalities" in data
        assert isinstance(data["municipalities"], list)

        # Verify we have the expected municipalities (10 for MVP)
        assert data["total"] == 10

        # Verify municipality structure
        muni = data["municipalities"][0]
        assert "ibge_code" in muni
        assert "name" in muni
        assert "state" in muni
        assert "population" in muni
        assert "lat" in muni
        assert "lon" in muni

        # Verify São Paulo is in the list
        sp_codes = [m["ibge_code"] for m in data["municipalities"]]
        assert "3550308" in sp_codes

    def test_municipalities_sorted_by_population(self):
        """Test that municipalities are sorted by population (largest first)"""
        response = client.get("/api/v1/risk/municipalities")

        assert response.status_code == 200
        data = response.json()

        munis = data["municipalities"]

        # Verify population is descending
        for i in range(len(munis) - 1):
            assert munis[i]["population"] >= munis[i + 1]["population"]


# ============================================================================
# Municipality Info Endpoint Tests
# ============================================================================

@pytest.mark.integration
class TestMunicipalityInfoEndpoint:
    """Tests for GET /api/v1/risk/municipalities/{ibge_code}/info"""

    def test_get_municipality_info_sao_paulo(self):
        """Test getting detailed municipality info"""
        response = client.get("/api/v1/risk/municipalities/3550308/info")

        assert response.status_code == 200
        data = response.json()

        # Verify all expected fields
        assert data["ibge_code"] == "3550308"
        assert data["name"] == "São Paulo"
        assert data["state"] == "SP"
        assert data["state_name"] == "São Paulo"
        assert "population" in data
        assert "area_km2" in data
        assert "critical_infrastructure" in data
        assert "vulnerable_population_pct" in data
        assert "gdp_per_capita_brl" in data
        assert "lat" in data
        assert "lon" in data

    def test_get_municipality_info_all_cities(self):
        """Test info endpoint for all 10 municipalities"""
        ibge_codes = [
            "3550308",  # São Paulo
            "3304557",  # Rio de Janeiro
            "2927408",  # Salvador
            "2304400",  # Fortaleza
            "5300108",  # Brasília
            "4106902",  # Curitiba
            "1302603",  # Manaus
            "2611606",  # Recife
            "4314902",  # Porto Alegre
            "1501402",  # Belém
        ]

        for ibge_code in ibge_codes:
            response = client.get(f"/api/v1/risk/municipalities/{ibge_code}/info")
            assert response.status_code == 200

    def test_get_municipality_info_invalid(self):
        """Test error for invalid municipality"""
        response = client.get("/api/v1/risk/municipalities/9999999/info")

        assert response.status_code == 404


# ============================================================================
# Data Validation Tests
# ============================================================================

@pytest.mark.integration
class TestDataValidation:
    """Tests for data consistency and validation"""

    def test_risk_scores_valid_range(self):
        """Test that all risk scores are in valid range (0.0-1.0)"""
        response = client.get("/api/v1/risk/municipality/3550308")

        assert response.status_code == 200
        data = response.json()

        # Overall risk
        assert 0.0 <= data["overall_risk_score"] <= 1.0

        # Hazard risks
        for hazard in data["hazards"]:
            assert 0.0 <= hazard["current_risk"] <= 1.0
            assert 0.0 <= hazard["projected_2030"] <= 1.0
            assert 0.0 <= hazard["projected_2050"] <= 1.0
            assert 0.0 <= hazard["confidence"] <= 1.0

        # Vulnerability
        vuln = data["vulnerability"]
        assert 0.0 <= vuln["vulnerable_population_pct"] <= 1.0
        assert 0.0 <= vuln["adaptive_capacity_score"] <= 1.0

    def test_recommendations_not_empty(self):
        """Test that recommendations are provided"""
        response = client.get("/api/v1/risk/municipality/3550308")

        assert response.status_code == 200
        data = response.json()

        assert "recommendations" in data
        assert isinstance(data["recommendations"], list)
        assert len(data["recommendations"]) > 0

    def test_h3_grid_cells_valid_format(self):
        """Test that H3 cell IDs are valid format"""
        response = client.get(
            "/api/v1/risk/municipality/3550308?include_h3_grid=true"
        )

        assert response.status_code == 200
        data = response.json()

        grid = data["h3_grid_data"]
        assert len(grid) > 0  # Should have cells

        # Verify at least 10 cells generated
        assert len(grid) >= 10

        # All cell IDs should be 15-character hex strings
        for cell_id in grid.keys():
            assert len(cell_id) == 15
            # Should be valid hex
            int(cell_id, 16)  # Raises if not valid hex


# ============================================================================
# Performance Tests
# ============================================================================

@pytest.mark.integration
class TestPerformance:
    """Basic performance tests"""

    def test_response_time_without_grid(self):
        """Test response time is reasonable without H3 grid"""
        import time

        start = time.time()
        response = client.get("/api/v1/risk/municipality/3550308")
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 2.0  # Should complete in under 2 seconds

    def test_response_time_with_grid(self):
        """Test response time with H3 grid generation"""
        import time

        start = time.time()
        response = client.get(
            "/api/v1/risk/municipality/3550308?include_h3_grid=true"
        )
        elapsed = time.time() - start

        assert response.status_code == 200
        assert elapsed < 5.0  # Grid generation should still be fast
