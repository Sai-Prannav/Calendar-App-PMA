"""
Integration tests for API Services
"""
import os
from datetime import datetime
from unittest.mock import Mock, patch

import pytest
from requests.exceptions import RequestException

from src.core.api_services import APIServices, LocationMedia, YouTubeVideo

@pytest.fixture(params=[
    {"maps_api_key": "test_maps_key"},
    {"maps_api_key": None}
])
def api_services(request):
    """Create test instance of APIServices with and without maps API key."""
    return APIServices(
        youtube_api_key="test_youtube_key",
        maps_api_key=request.param["maps_api_key"]
    )

def test_get_location_media_success(api_services):
    """Test successful location media retrieval."""
    # Mock YouTube API response
    youtube_response = {
        "items": [
            {
                "id": {"videoId": "test123"},
                "snippet": {
                    "title": "Test Video",
                    "thumbnails": {"medium": {"url": "http://example.com/thumb.jpg"}},
                    "publishedAt": "2024-01-01T12:00:00Z"
                }
            }
        ]
    }
    
    with patch.object(api_services.session, 'get') as mock_get:
        # Setup mock responses
        mock_get.return_value = Mock(
            status_code=200,
            json=lambda: youtube_response
        )
        
        # Test the method
        result = api_services.get_location_media("Test City")
        
        assert isinstance(result, LocationMedia)
        assert len(result.videos) == 1
        assert isinstance(result.videos[0], YouTubeVideo)
        assert result.videos[0].video_id == "test123"
        
        # Check map URL based on whether API key is provided
        if api_services.maps_api_key:
            assert result.static_map_url is not None
            assert "maps.googleapis.com" in result.static_map_url
            assert "Test City" in result.static_map_url
        else:
            assert result.static_map_url is None

def test_get_location_media_api_error(api_services):
    """Test handling of API errors."""
    with patch.object(api_services.session, 'get') as mock_get:
        mock_get.side_effect = RequestException("API Error")
        
        with pytest.raises(ConnectionError) as exc_info:
            api_services.get_location_media("Test City")
        
        assert "Failed to fetch location media" in str(exc_info.value)

def test_rate_limiting(api_services):
    """Test that rate limiting is applied."""
    with patch.object(api_services.youtube_limiter, 'wait_if_needed') as mock_wait:
        with patch.object(api_services.session, 'get') as mock_get:
            mock_get.return_value = Mock(
                status_code=200,
                json=lambda: {"items": []}
            )
            
            api_services.get_location_media("Test City")
            
            # Verify rate limiter was called
            mock_wait.assert_called_once()

def test_cleanup(api_services):
    """Test proper cleanup of resources."""
    with patch.object(api_services.session, 'close') as mock_close:
        api_services.close()
        mock_close.assert_called_once()