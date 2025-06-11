"""
Weather Service Module - Handles OpenWeatherMap API integration for current weather and forecasts.
Includes database integration for historical data storage.
"""
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import requests
from requests.exceptions import RequestException
from datetime import date

from src.database.session import SessionManager
from src.database.operations import DatabaseOperations

@dataclass
class WeatherData:
    """Container for weather information."""
    temperature: float
    feels_like: float
    humidity: int
    wind_speed: float
    condition: str
    icon: str
    timestamp: datetime
    location_name: str
    latitude: float
    longitude: float

@dataclass
class ForecastData:
    """Container for forecast information."""
    date: datetime
    temp_min: float
    temp_max: float
    condition: str
    icon: str
    precipitation_prob: float

class WeatherService:
    """Service for interacting with OpenWeatherMap API."""
    
    BASE_URL = "https://api.openweathermap.org/data/2.5"
    GEO_URL = "http://api.openweathermap.org/geo/1.0"
    
    def __init__(self, api_key: str):
        """Initialize the weather service.
        
        Args:
            api_key: OpenWeatherMap API key
        """
        self.api_key = api_key
        self.session = requests.Session()
        self.session_manager = SessionManager()
    
    def get_current_weather(self, lat: float, lon: float) -> WeatherData:
        """Fetch current weather for given coordinates."""
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Invalid coordinates")
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/weather",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            weather_data = WeatherData(
                temperature=data["main"]["temp"],
                feels_like=data["main"]["feels_like"],
                humidity=data["main"]["humidity"],
                wind_speed=data["wind"]["speed"],
                condition=data["weather"][0]["description"],
                icon=data["weather"][0]["icon"],
                timestamp=datetime.fromtimestamp(data["dt"]),
                location_name=data["name"],
                latitude=lat,
                longitude=lon
            )

            # Save to database using session scope
            with self.session_manager.session_scope() as session:
                db_ops = DatabaseOperations(session)
                db_ops.save_weather_data(
                    location_name=weather_data.location_name,
                    lat=weather_data.latitude,
                    lon=weather_data.longitude,
                    temperature=weather_data.temperature,
                    feels_like=weather_data.feels_like,
                    humidity=weather_data.humidity,
                    wind_speed=weather_data.wind_speed,
                    condition=weather_data.condition
                )

            return weather_data
            
        except RequestException as e:
            raise ConnectionError(f"Failed to fetch weather data: {str(e)}")
    
    def get_forecast(self, lat: float, lon: float) -> List[ForecastData]:
        """Fetch 5-day forecast for given coordinates."""
        if not (-90 <= lat <= 90 and -180 <= lon <= 180):
            raise ValueError("Invalid coordinates")
        
        try:
            response = self.session.get(
                f"{self.BASE_URL}/forecast",
                params={
                    "lat": lat,
                    "lon": lon,
                    "appid": self.api_key,
                    "units": "metric"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            # Group forecast data by day
            daily_forecasts: Dict[str, List[Dict]] = {}
            for item in data["list"]:
                date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                if date not in daily_forecasts:
                    daily_forecasts[date] = []
                daily_forecasts[date].append(item)
            
            # Create daily forecast summaries
            forecasts = []
            with self.session_manager.session_scope() as session:
                db_ops = DatabaseOperations(session)
                
                for date, items in list(daily_forecasts.items())[:5]:  # Limit to 5 days
                    temps = [item["main"]["temp"] for item in items]
                    most_common_weather = max(
                        [(item["weather"][0]["description"], item["weather"][0]["icon"]) 
                         for item in items],
                        key=lambda x: items.count(x)
                    )
                    
                    forecast_date = datetime.strptime(date, "%Y-%m-%d")
                    forecast_data = ForecastData(
                        date=forecast_date,
                        temp_min=min(temps),
                        temp_max=max(temps),
                        condition=most_common_weather[0],
                        icon=most_common_weather[1],
                        precipitation_prob=max(item.get("pop", 0) for item in items)
                    )
                    forecasts.append(forecast_data)

                    # Save forecast data to database
                    db_ops.save_weather_data(
                        location_name=data["city"]["name"],
                        lat=lat,
                        lon=lon,
                        temperature=(forecast_data.temp_min + forecast_data.temp_max) / 2,
                        feels_like=None,
                        humidity=None,
                        wind_speed=None,
                        condition=forecast_data.condition,
                        date_range_start=forecast_date.date(),
                        date_range_end=forecast_date.date()
                    )
            
            return forecasts
            
        except RequestException as e:
            raise ConnectionError(f"Failed to fetch forecast data: {str(e)}")

    def geocode_location(self, location: str) -> Optional[Tuple[float, float]]:
        """Convert location string to coordinates.
        
        Args:
            location: Location string (city name, zip code, etc.)
            
        Returns:
            Tuple of (latitude, longitude) if found, None otherwise
            
        Raises:
            ConnectionError: If API request fails
        """
        try:
            response = self.session.get(
                f"{self.GEO_URL}/direct",
                params={
                    "q": location,
                    "limit": 1,
                    "appid": self.api_key
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if data and len(data) > 0:
                coords = (data[0]["lat"], data[0]["lon"])
                # Save search to location history
                with self.session_manager.session_scope() as session:
                    db_ops = DatabaseOperations(session)
                    db_ops.add_location_history(
                        query=location,
                        resolved_name=data[0].get("name"),
                        lat=coords[0],
                        lon=coords[1]
                    )
                return coords
            return None
            
        except RequestException as e:
            raise ConnectionError(f"Failed to geocode location: {str(e)}")

    def close(self):
        """Close the requests session."""
        self.session.close()