"""
API Services Module - Handles integrations with YouTube and Google Maps APIs.
Includes rate limiting and error handling.
"""
from dataclasses import dataclass
from datetime import datetime
import time
from typing import Dict, List, Optional
import requests
from requests.exceptions import RequestException

@dataclass
class YouTubeVideo:
    """Container for YouTube video information."""
    video_id: str
    title: str
    thumbnail_url: str
    published_at: datetime

@dataclass
class LocationMedia:
    """Container for location-related media."""
    videos: List[YouTubeVideo]
    static_map_url: str

class RateLimiter:
    """Simple rate limiter using token bucket algorithm."""
    def __init__(self, requests_per_minute: int):
        self.requests_per_minute = requests_per_minute
        self.time_between_requests = 60.0 / requests_per_minute
        self.last_request_time = 0.0

    def wait_if_needed(self):
        """Wait if necessary to maintain rate limit."""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.time_between_requests:
            time.sleep(self.time_between_requests - time_since_last)
        self.last_request_time = time.time()

class APIServices:
    """Service for handling external API integrations."""
    
    YOUTUBE_BASE_URL = "https://www.googleapis.com/youtube/v3"
    MAPS_STATIC_URL = "https://maps.googleapis.com/maps/api/staticmap"
    
    def __init__(self, youtube_api_key: str, maps_api_key: Optional[str] = None):
        """Initialize API services.
        
        Args:
            youtube_api_key: YouTube Data API key
            maps_api_key: Google Maps API key
        """
        self.youtube_api_key = youtube_api_key
        self.maps_api_key = maps_api_key
        self.session = requests.Session()
        
        # Initialize rate limiters (YouTube has quota of 10,000 units per day)
        self.youtube_limiter = RateLimiter(requests_per_minute=30)
        self.maps_limiter = RateLimiter(requests_per_minute=60)

    def get_location_media(self, location: str, max_videos: int = 3) -> LocationMedia:
        """Fetch media content for a location.
        
        Args:
            location: Location name to search for
            max_videos: Maximum number of videos to return
            
        Returns:
            LocationMedia object containing videos and map
            
        Raises:
            ConnectionError: If API requests fail
        """
        try:
            # Get location videos
            self.youtube_limiter.wait_if_needed()
            videos_response = self.session.get(
                f"{self.YOUTUBE_BASE_URL}/search",
                params={
                    "part": "snippet",
                    "q": f"{location} travel",
                    "type": "video",
                    "maxResults": max_videos,
                    "key": self.youtube_api_key,
                    "order": "viewCount"
                }
            )
            videos_response.raise_for_status()
            videos_data = videos_response.json()
            
            videos = [
                YouTubeVideo(
                    video_id=item["id"]["videoId"],
                    title=item["snippet"]["title"],
                    thumbnail_url=item["snippet"]["thumbnails"]["medium"]["url"],
                    published_at=datetime.strptime(
                        item["snippet"]["publishedAt"],
                        "%Y-%m-%dT%H:%M:%SZ"
                    )
                )
                for item in videos_data.get("items", [])
            ]
            
            # Get static map if API key is available
            static_map_url = None
            if self.maps_api_key:
                self.maps_limiter.wait_if_needed()
                static_map_url = (
                    f"{self.MAPS_STATIC_URL}"
                    f"?center={location}"
                    f"&zoom=12"
                    f"&size=400x300"
                    f"&key={self.maps_api_key}"
                )
            
            return LocationMedia(videos=videos, static_map_url=static_map_url)
            
        except RequestException as e:
            raise ConnectionError(f"Failed to fetch location media: {str(e)}")
            
    def close(self):
        """Close the HTTP session."""
        self.session.close()