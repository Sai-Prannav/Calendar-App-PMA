"""
Tests for the Weather Service module.
"""
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
import requests

from src.core.weather_service import WeatherService, WeatherData, ForecastData

@pytest.fixture
def weather_service():
    """Create a WeatherService instance with test API key."""
    return WeatherService("test_api_key")

@pytest.fixture
def mock_weather_response():
    """Mock response for current weather API call."""
    return {
        "main": {
            "temp": 20.5,
            "feels_like": 21.0,
            "humidity": 65
        },
        "wind": {
            "speed": 5.2
        },
        "weather": [{
            "description": "clear sky",
            "icon": "01d"
        }],
        "dt": 1623345600,  # 2021-06-10 12:00:00
        "name": "Test City"  # Added for test compatibility
    }

@pytest.fixture
def mock_forecast_response():
    """Mock response for forecast API call."""
    return {
        "city": {"name": "Test City"},  # Added for test compatibility
        "list": [
            {
                "dt": 1623345600,  # 2021-06-10 12:00:00
                "main": {
                    "temp": 20.5
                },
                "weather": [{
                    "description": "clear sky",
                    "icon": "01d"
                }],
                "pop": 0.2
            },
            {
                "dt": 1623432000,  # 2021-06-11 12:00:00
                "main": {
                    "temp": 22.5
                },
                "weather": [{
                    "description": "clear sky",
                    "icon": "01d"
                }],
                "pop": 0.1
            }
        ]
    }

def test_init_weather_service():
    """Test WeatherService initialization."""
    service = WeatherService("test_key")
    assert service.api_key == "test_key"
    assert isinstance(service.session, requests.Session)

def test_get_current_weather_success(weather_service, mock_weather_response):
    """Test successful current weather retrieval."""
    with patch.object(requests.Session, 'get') as mock_get:
        mock_get.return_value.json.return_value = mock_weather_response
        mock_get.return_value.raise_for_status = Mock()
        
        weather = weather_service.get_current_weather(40.7128, -74.0060)
        
        assert isinstance(weather, WeatherData)
        assert weather.temperature == 20.5
        assert weather.feels_like == 21.0
        assert weather.humidity == 65
        assert weather.wind_speed == 5.2
        assert weather.condition == "clear sky"
        assert weather.icon == "01d"
        assert isinstance(weather.timestamp, datetime)

def test_get_current_weather_invalid_coordinates(weather_service):
    """Test current weather retrieval with invalid coordinates."""
    with pytest.raises(ValueError):
        weather_service.get_current_weather(91, 0)  # Invalid latitude
    with pytest.raises(ValueError):
        weather_service.get_current_weather(0, 181)  # Invalid longitude

def test_get_current_weather_api_error(weather_service):
    """Test current weather retrieval with API error."""
    with patch.object(requests.Session, 'get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        with pytest.raises(ConnectionError):
            weather_service.get_current_weather(40.7128, -74.0060)

def test_get_forecast_success(weather_service, mock_forecast_response):
    """Test successful forecast retrieval."""
    with patch.object(requests.Session, 'get') as mock_get:
        mock_get.return_value.json.return_value = mock_forecast_response
        mock_get.return_value.raise_for_status = Mock()
        
        forecast = weather_service.get_forecast(40.7128, -74.0060)
        
        assert isinstance(forecast, list)
        assert len(forecast) > 0
        assert isinstance(forecast[0], ForecastData)
        assert forecast[0].temp_max == 20.5
        assert forecast[0].condition == "clear sky"
        assert forecast[0].precipitation_prob == 0.2

def test_geocode_location_success(weather_service):
    """Test successful location geocoding."""
    mock_response = [{"lat": 40.7128, "lon": -74.0060}]
    
    with patch.object(requests.Session, 'get') as mock_get:
        mock_get.return_value.json.return_value = mock_response
        mock_get.return_value.raise_for_status = Mock()
        
        coordinates = weather_service.geocode_location("New York")
        
        assert coordinates == (40.7128, -74.0060)

def test_geocode_location_not_found(weather_service):
    """Test geocoding with location not found."""
    with patch.object(requests.Session, 'get') as mock_get:
        mock_get.return_value.json.return_value = []
        mock_get.return_value.raise_for_status = Mock()
        
        coordinates = weather_service.geocode_location("NonexistentCity")
        
        assert coordinates is None

def test_geocode_location_api_error(weather_service):
    """Test geocoding with API error."""
    with patch.object(requests.Session, 'get') as mock_get:
        mock_get.side_effect = requests.exceptions.RequestException("API Error")
        
        with pytest.raises(ConnectionError):
            weather_service.geocode_location("New York")