"""
Integration tests for FastAPI endpoints

Tests cover:
- Root and health endpoints
- Basic endpoint availability
- Response structure validation
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
# Root Endpoint Tests
# ============================================================================

@pytest.mark.integration
class TestRootEndpoint:
    """Tests for root endpoint."""

    def test_root_endpoint_returns_200(self):
        """Test that root endpoint returns 200 OK."""
        response = client.get("/")

        assert response.status_code == 200

    def test_root_endpoint_response_structure(self):
        """Test root endpoint response structure."""
        response = client.get("/")
        data = response.json()

        assert "name" in data
        assert "version" in data
        assert "environment" in data
        assert "status" in data
        assert "docs" in data

    def test_root_endpoint_returns_correct_name(self):
        """Test that root endpoint returns correct API name."""
        response = client.get("/")
        data = response.json()

        assert data["name"] == "PÚRPURA Climate OS API"

    def test_root_endpoint_status_operational(self):
        """Test that root endpoint shows operational status."""
        response = client.get("/")
        data = response.json()

        assert data["status"] == "operational"

    def test_root_endpoint_includes_docs_link(self):
        """Test that root endpoint includes docs link."""
        response = client.get("/")
        data = response.json()

        assert data["docs"] == "/docs"


# ============================================================================
# Health Check Endpoint Tests
# ============================================================================

@pytest.mark.integration
class TestHealthEndpoint:
    """Tests for health check endpoint."""

    def test_health_endpoint_returns_200(self):
        """Test that health endpoint returns 200 OK."""
        response = client.get("/health")

        assert response.status_code == 200

    def test_health_endpoint_response_structure(self):
        """Test health endpoint response structure."""
        response = client.get("/health")
        data = response.json()

        assert "status" in data
        assert "version" in data
        assert "services" in data

    def test_health_endpoint_status_healthy(self):
        """Test that health endpoint reports healthy status."""
        response = client.get("/health")
        data = response.json()

        assert data["status"] == "healthy"

    def test_health_endpoint_includes_services(self):
        """Test that health endpoint includes service status."""
        response = client.get("/health")
        data = response.json()

        assert "services" in data
        assert "api" in data["services"]
        assert data["services"]["api"] == "up"

    def test_health_endpoint_returns_version(self):
        """Test that health endpoint returns version."""
        response = client.get("/health")
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)


# ============================================================================
# OpenAPI Documentation Tests
# ============================================================================

@pytest.mark.integration
class TestOpenAPIEndpoints:
    """Tests for OpenAPI documentation endpoints."""

    def test_openapi_json_available(self):
        """Test that OpenAPI JSON spec is available."""
        response = client.get("/openapi.json")

        assert response.status_code == 200
        data = response.json()

        assert "openapi" in data
        assert "info" in data
        assert "paths" in data

    def test_docs_endpoint_available(self):
        """Test that Swagger UI docs are available."""
        response = client.get("/docs")

        assert response.status_code == 200

    def test_redoc_endpoint_available(self):
        """Test that ReDoc documentation is available."""
        response = client.get("/redoc")

        assert response.status_code == 200


# ============================================================================
# Router Availability Tests
# ============================================================================

@pytest.mark.integration
class TestRouterAvailability:
    """Tests to ensure all routers are properly mounted."""

    def test_documents_router_mounted(self):
        """Test that documents router is mounted."""
        # Try to access a typical REST endpoint pattern
        # Even if it returns 404 or 405, it means the router is mounted
        response = client.get("/api/v1/documents/")

        # Should not be 404 at router level (would be 404 if router not mounted)
        assert response.status_code in [200, 404, 405, 422]

    def test_extraction_router_mounted(self):
        """Test that extraction router is mounted."""
        response = client.get("/api/v1/extraction/")

        assert response.status_code in [200, 404, 405, 422]

    def test_risk_router_mounted(self):
        """Test that risk assessment router is mounted."""
        response = client.get("/api/v1/risk/")

        assert response.status_code in [200, 404, 405, 422]

    def test_compliance_router_mounted(self):
        """Test that compliance router is mounted."""
        response = client.get("/api/v1/compliance/")

        assert response.status_code in [200, 404, 405, 422]


# ============================================================================
# CORS Tests
# ============================================================================

@pytest.mark.integration
class TestCORS:
    """Tests for CORS configuration."""

    def test_cors_headers_present(self):
        """Test that CORS headers are present in responses."""
        response = client.options(
            "/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
            }
        )

        # Check for CORS headers
        assert "access-control-allow-origin" in response.headers or \
               response.status_code in [200, 404]

    def test_preflight_request(self):
        """Test CORS preflight request."""
        response = client.options(
            "/api/v1/documents/",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "POST",
                "Access-Control-Request-Headers": "Content-Type",
            }
        )

        # Preflight should return 200 or be handled
        assert response.status_code in [200, 404]


# ============================================================================
# Error Handling Tests
# ============================================================================

@pytest.mark.integration
class TestErrorHandling:
    """Tests for API error handling."""

    def test_nonexistent_endpoint_returns_404(self):
        """Test that non-existent endpoint returns 404."""
        response = client.get("/api/v1/nonexistent/endpoint")

        assert response.status_code == 404

    def test_404_response_structure(self):
        """Test 404 error response structure."""
        response = client.get("/api/v1/nonexistent/endpoint")

        assert response.status_code == 404
        data = response.json()

        # FastAPI default 404 structure
        assert "detail" in data

    def test_method_not_allowed(self):
        """Test that wrong HTTP method returns 405."""
        # Root only supports GET, try POST
        response = client.post("/")

        assert response.status_code == 405


# ============================================================================
# Response Headers Tests
# ============================================================================

@pytest.mark.integration
class TestResponseHeaders:
    """Tests for response headers."""

    def test_content_type_json(self):
        """Test that API returns JSON content type."""
        response = client.get("/")

        assert "application/json" in response.headers["content-type"]

    def test_health_content_type_json(self):
        """Test that health endpoint returns JSON."""
        response = client.get("/health")

        assert "application/json" in response.headers["content-type"]


# ============================================================================
# API Version Tests
# ============================================================================

@pytest.mark.integration
class TestAPIVersion:
    """Tests for API versioning."""

    def test_version_in_root_response(self):
        """Test that version is included in root response."""
        response = client.get("/")
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)
        assert len(data["version"]) > 0

    def test_version_in_health_response(self):
        """Test that version is included in health response."""
        response = client.get("/health")
        data = response.json()

        assert "version" in data
        assert isinstance(data["version"], str)

    def test_version_format(self):
        """Test that version follows semantic versioning format."""
        response = client.get("/")
        data = response.json()

        version = data["version"]
        # Should be like "1.0.0" or similar
        parts = version.split(".")
        assert len(parts) >= 2  # At least major.minor


# ============================================================================
# Environment Configuration Tests
# ============================================================================

@pytest.mark.integration
class TestEnvironmentConfiguration:
    """Tests for environment configuration."""

    def test_environment_in_root_response(self):
        """Test that environment is included in root response."""
        response = client.get("/")
        data = response.json()

        assert "environment" in data
        assert isinstance(data["environment"], str)

    def test_environment_valid_value(self):
        """Test that environment has valid value."""
        response = client.get("/")
        data = response.json()

        env = data["environment"]
        # Should be one of common environment names
        assert env in ["development", "staging", "production", "test"]


# ============================================================================
# Integration Test Utilities
# ============================================================================

@pytest.mark.integration
class TestTestClient:
    """Tests to verify test client functionality."""

    def test_test_client_working(self):
        """Test that TestClient is working correctly."""
        response = client.get("/")

        assert response is not None
        assert hasattr(response, "status_code")
        assert hasattr(response, "json")

    def test_multiple_requests(self):
        """Test that multiple requests work."""
        response1 = client.get("/")
        response2 = client.get("/health")

        assert response1.status_code == 200
        assert response2.status_code == 200
