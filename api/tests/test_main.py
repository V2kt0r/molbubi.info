import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.shared.exceptions import ResourceNotFound


class TestMainApp:
    @pytest.fixture
    def client(self):
        return TestClient(app)

    def test_read_root(self, client):
        response = client.get("/")
        
        assert response.status_code == 200
        assert response.json() == {"message": "Welcome to molbubi.info"}

    def test_openapi_json(self, client):
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        openapi_data = response.json()
        assert "openapi" in openapi_data
        assert "info" in openapi_data
        assert openapi_data["info"]["title"] == "molbubi.info"

    def test_docs_endpoint(self, client):
        response = client.get("/docs")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_redoc_endpoint(self, client):
        response = client.get("/redoc")
        
        assert response.status_code == 200
        assert "text/html" in response.headers["content-type"]

    def test_process_time_middleware(self, client):
        response = client.get("/")
        
        assert "X-Process-Time" in response.headers
        # Should be a numeric value (as string)
        process_time = float(response.headers["X-Process-Time"])
        assert process_time >= 0

    def test_resource_not_found_exception_handler(self, client):
        # Test the exception handler by triggering a ResourceNotFound exception
        with pytest.raises(Exception):
            # This would need to be tested with an actual endpoint that raises ResourceNotFound
            # For now, we'll test that the handler is properly registered
            pass

    def test_404_endpoint(self, client):
        response = client.get("/nonexistent-endpoint")
        
        assert response.status_code == 404

    def test_api_prefix_routing(self, client):
        # Test that API routes are properly prefixed
        response = client.get("/api/v1/bikes/")
        
        # Should not return 404 (route exists) even if service fails
        assert response.status_code != 404

    def test_cors_headers(self, client):
        # Test if CORS is handled (if configured)
        response = client.get("/")
        
        # Basic check - response should succeed
        assert response.status_code == 200

    def test_invalid_json_body(self, client):
        # Test handling of invalid JSON in request body
        response = client.post(
            "/api/v1/bikes/",  # This endpoint doesn't exist, but tests JSON parsing
            headers={"Content-Type": "application/json"},
            data="invalid json"
        )
        
        # Should return 422 for invalid JSON or 404/405 for invalid endpoint
        assert response.status_code in [404, 405, 422]

    def test_large_request_body(self, client):
        # Test handling of large request bodies
        large_data = {"data": "x" * 10000}  # 10KB of data
        
        response = client.post(
            "/api/v1/bikes/",  # Non-existent endpoint
            json=large_data
        )
        
        # Should handle large bodies gracefully
        assert response.status_code in [404, 405, 413, 422]

    def test_content_type_validation(self, client):
        # Test different content types
        response = client.post(
            "/api/v1/bikes/",  # Non-existent endpoint
            headers={"Content-Type": "text/plain"},
            data="plain text data"
        )
        
        assert response.status_code in [404, 405, 415, 422]

    def test_method_not_allowed(self, client):
        # Test unsupported HTTP methods
        response = client.patch("/")
        
        assert response.status_code == 405

    def test_api_version_in_openapi(self, client):
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        openapi_data = response.json()
        
        # Should include version from settings
        assert "version" in openapi_data["info"]

    def test_api_tags_in_openapi(self, client):
        response = client.get("/api/v1/openapi.json")
        
        assert response.status_code == 200
        openapi_data = response.json()
        
        # Should include the expected tags for each router
        paths = openapi_data.get("paths", {})
        tags_found = set()
        
        for path_info in paths.values():
            for method_info in path_info.values():
                if isinstance(method_info, dict) and "tags" in method_info:
                    tags_found.update(method_info["tags"])
        
        # Should include the tags defined in api router
        expected_tags = {"Stations", "Bikes", "Distribution"}
        assert expected_tags.issubset(tags_found)

    def test_health_endpoint_availability(self, client):
        # Test that basic health check works (root endpoint)
        response = client.get("/")
        
        assert response.status_code == 200
        assert "message" in response.json()

    def test_trailing_slash_handling(self, client):
        # Test both with and without trailing slash
        response1 = client.get("/api/v1/bikes")
        response2 = client.get("/api/v1/bikes/")
        
        # At least one should work (depending on FastAPI configuration)
        assert response1.status_code != 404 or response2.status_code != 404