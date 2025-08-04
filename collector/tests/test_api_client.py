"""
Comprehensive tests for API client covering all edge cases.
"""
import json
import pytest
import responses
from requests.exceptions import (
    RequestException, Timeout, ConnectionError, HTTPError, 
    TooManyRedirects, InvalidURL
)
from unittest.mock import patch

from app.api.client import ApiClient


class TestApiClient:
    """Test cases for ApiClient class."""

    def test_init_default_params(self, mock_settings):
        """Test ApiClient initialization with default parameters."""
        client = ApiClient()
        assert client.api_url == mock_settings.API_URL
        assert client.timeout == 10

    def test_init_custom_params(self):
        """Test ApiClient initialization with custom parameters."""
        custom_url = "https://custom-api.example.com"
        custom_timeout = 30
        client = ApiClient(api_url=custom_url, timeout=custom_timeout)
        assert client.api_url == custom_url
        assert client.timeout == custom_timeout

    @responses.activate
    def test_fetch_bike_data_success(self, valid_nextbike_data, caplog_info):
        """Test successful API data fetching."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json=valid_nextbike_data,
            status=200
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result == valid_nextbike_data
        assert len(responses.calls) == 1
        assert responses.calls[0].request.url == "https://test-api.example.com/"

    @responses.activate
    def test_fetch_bike_data_empty_response(self, caplog_error):
        """Test handling of empty response."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json={},
            status=200
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result == {}

    @responses.activate
    def test_fetch_bike_data_invalid_json(self, caplog_error):
        """Test handling of invalid JSON response."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            body="Invalid JSON content",
            status=200
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None
        assert "Error fetching data from Nextbike API" in caplog_error.text

    @responses.activate
    def test_fetch_bike_data_http_error_400(self, caplog_error):
        """Test handling of HTTP 400 Bad Request."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json={"error": "Bad Request"},
            status=400
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None
        assert "Error fetching data from Nextbike API" in caplog_error.text

    @responses.activate
    def test_fetch_bike_data_http_error_401(self, caplog_error):
        """Test handling of HTTP 401 Unauthorized."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json={"error": "Unauthorized"},
            status=401
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None
        assert "Error fetching data from Nextbike API" in caplog_error.text

    @responses.activate
    def test_fetch_bike_data_http_error_403(self, caplog_error):
        """Test handling of HTTP 403 Forbidden."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json={"error": "Forbidden"},
            status=403
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None
        assert "Error fetching data from Nextbike API" in caplog_error.text

    @responses.activate
    def test_fetch_bike_data_http_error_404(self, caplog_error):
        """Test handling of HTTP 404 Not Found."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json={"error": "Not Found"},
            status=404
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None
        assert "Error fetching data from Nextbike API" in caplog_error.text

    @responses.activate
    def test_fetch_bike_data_http_error_500(self, caplog_error):
        """Test handling of HTTP 500 Internal Server Error."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json={"error": "Internal Server Error"},
            status=500
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None
        assert "Error fetching data from Nextbike API" in caplog_error.text

    @responses.activate
    def test_fetch_bike_data_http_error_502(self, caplog_error):
        """Test handling of HTTP 502 Bad Gateway."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json={"error": "Bad Gateway"},
            status=502
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None
        assert "Error fetching data from Nextbike API" in caplog_error.text

    @responses.activate
    def test_fetch_bike_data_http_error_503(self, caplog_error):
        """Test handling of HTTP 503 Service Unavailable."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json={"error": "Service Unavailable"},
            status=503
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None
        assert "Error fetching data from Nextbike API" in caplog_error.text

    def test_fetch_bike_data_timeout(self, caplog_error):
        """Test handling of request timeout."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = Timeout("Request timed out")
            
            client = ApiClient(api_url="https://test-api.example.com", timeout=1)
            result = client.fetch_bike_data()
            
            assert result is None
            assert "Error fetching data from Nextbike API" in caplog_error.text
            mock_get.assert_called_once_with(
                "https://test-api.example.com", 
                timeout=1
            )

    def test_fetch_bike_data_connection_error(self, caplog_error):
        """Test handling of connection error."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = ConnectionError("Connection failed")
            
            client = ApiClient(api_url="https://test-api.example.com")
            result = client.fetch_bike_data()
            
            assert result is None
            assert "Error fetching data from Nextbike API" in caplog_error.text

    def test_fetch_bike_data_too_many_redirects(self, caplog_error):
        """Test handling of too many redirects error."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = TooManyRedirects("Too many redirects")
            
            client = ApiClient(api_url="https://test-api.example.com")
            result = client.fetch_bike_data()
            
            assert result is None
            assert "Error fetching data from Nextbike API" in caplog_error.text

    def test_fetch_bike_data_invalid_url(self, caplog_error):
        """Test handling of invalid URL error."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = InvalidURL("Invalid URL")
            
            client = ApiClient(api_url="invalid-url")
            result = client.fetch_bike_data()
            
            assert result is None
            assert "Error fetching data from Nextbike API" in caplog_error.text

    def test_fetch_bike_data_generic_request_exception(self, caplog_error):
        """Test handling of generic RequestException."""
        with patch('requests.get') as mock_get:
            mock_get.side_effect = RequestException("Generic request error")
            
            client = ApiClient(api_url="https://test-api.example.com")
            result = client.fetch_bike_data()
            
            assert result is None
            assert "Error fetching data from Nextbike API" in caplog_error.text

    @responses.activate
    def test_fetch_bike_data_unicode_content(self):
        """Test handling of unicode content in response."""
        unicode_data = {
            "countries": [
                {
                    "cities": [
                        {
                            "places": [
                                {
                                    "uid": 12345,
                                    "lat": 47.5,
                                    "lng": 19.0,
                                    "name": "Állomás étkezde",  # Unicode characters
                                    "spot": False,
                                    "bike_list": []
                                }
                            ]
                        }
                    ]
                }
            ]
        }
        
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json=unicode_data,
            status=200
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result == unicode_data
        assert result["countries"][0]["cities"][0]["places"][0]["name"] == "Állomás étkezde"

    @responses.activate
    def test_fetch_bike_data_large_response(self, large_nextbike_data):
        """Test handling of large API response."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json=large_nextbike_data,
            status=200
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result == large_nextbike_data
        assert len(result["countries"][0]["cities"][0]["places"]) == 100

    @responses.activate
    def test_fetch_bike_data_custom_timeout_used(self):
        """Test that custom timeout is properly used in request."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            json={"test": "data"},
            status=200
        )
        
        custom_timeout = 15
        client = ApiClient(api_url="https://test-api.example.com", timeout=custom_timeout)
        
        with patch('requests.get') as mock_get:
            mock_get.return_value.raise_for_status.return_value = None
            mock_get.return_value.json.return_value = {"test": "data"}
            
            client.fetch_bike_data()
            
            mock_get.assert_called_once_with(
                "https://test-api.example.com",
                timeout=custom_timeout
            )

    @responses.activate
    def test_fetch_bike_data_empty_body(self, caplog_error):
        """Test handling of empty response body."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            body="",
            status=200
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None
        assert "Error fetching data from Nextbike API" in caplog_error.text

    @responses.activate
    def test_fetch_bike_data_null_response(self):
        """Test handling of null JSON response."""
        responses.add(
            responses.GET,
            "https://test-api.example.com",
            body="null",
            status=200
        )
        
        client = ApiClient(api_url="https://test-api.example.com")
        result = client.fetch_bike_data()
        
        assert result is None