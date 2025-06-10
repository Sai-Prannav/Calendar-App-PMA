import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class WeatherService:
    def __init__(self):
        self.api_key = os.getenv('OPENWEATHER_API_KEY')
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.geocoding_url = "http://api.openweathermap.org/geo/1.0"
        
        if not self.api_key:
            raise ValueError("OpenWeather API key not found in environment variables")

    def _get_coordinates(self, location, location_type):
        """Convert location to coordinates using OpenWeather Geocoding API"""
        try:
            if location_type == 'coordinates':
                lat, lon = map(float, location.split(','))
                return lat, lon
            
            # For city names, landmarks, or zip codes
            params = {
                'appid': self.api_key,
                'limit': 1
            }
            
            if location_type == 'zip':
                params['zip'] = location
                geocoding_endpoint = f"{self.geocoding_url}/zip"
            else:  # city or landmark
                params['q'] = location
                geocoding_endpoint = f"{self.geocoding_url}/direct"
            
            response = requests.get(geocoding_endpoint, params=params)
            response.raise_for_status()
            
            data = response.json()
            if isinstance(data, list) and len(data) > 0:
                return data[0]['lat'], data[0]['lon']
            elif isinstance(data, dict) and 'lat' in data:
                return data['lat'], data['lon']
            else:
                raise ValueError(f"Location not found: {location}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching coordinates: {str(e)}")

    def get_current_weather(self, location, location_type):
        """Get current weather for a location"""
        try:
            lat, lon = self._get_coordinates(location, location_type)
            
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric'  # Use metric units (Celsius)
            }
            
            response = requests.get(f"{self.base_url}/weather", params=params)
            response.raise_for_status()
            
            weather_data = response.json()
            return {
                'temperature': weather_data['main']['temp'],
                'feels_like': weather_data['main']['feels_like'],
                'humidity': weather_data['main']['humidity'],
                'description': weather_data['weather'][0]['description'],
                'wind_speed': weather_data['wind']['speed'],
                'timestamp': datetime.fromtimestamp(weather_data['dt']).isoformat()
            }
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching weather data: {str(e)}")

    def get_forecast(self, location, location_type, days=5):
        """Get weather forecast for a location"""
        try:
            lat, lon = self._get_coordinates(location, location_type)
            
            params = {
                'lat': lat,
                'lon': lon,
                'appid': self.api_key,
                'units': 'metric',
                'cnt': days * 8  # API returns data in 3-hour intervals
            }
            
            response = requests.get(f"{self.base_url}/forecast", params=params)
            response.raise_for_status()
            
            forecast_data = response.json()
            daily_forecasts = []
            
            # Group 3-hour forecasts into daily forecasts
            current_date = None
            daily_temps = []
            
            for item in forecast_data['list']:
                date = datetime.fromtimestamp(item['dt']).date()
                
                if current_date is None:
                    current_date = date
                
                if date != current_date:
                    # Calculate daily summary
                    avg_temp = sum(t for t in daily_temps) / len(daily_temps)
                    daily_forecasts.append({
                        'date': current_date.isoformat(),
                        'average_temp': round(avg_temp, 2),
                        'min_temp': min(daily_temps),
                        'max_temp': max(daily_temps)
                    })
                    
                    current_date = date
                    daily_temps = []
                
                daily_temps.append(item['main']['temp'])
            
            # Add the last day if it has data
            if daily_temps:
                avg_temp = sum(t for t in daily_temps) / len(daily_temps)
                daily_forecasts.append({
                    'date': current_date.isoformat(),
                    'average_temp': round(avg_temp, 2),
                    'min_temp': min(daily_temps),
                    'max_temp': max(daily_temps)
                })
            
            return daily_forecasts
            
        except requests.exceptions.RequestException as e:
            raise Exception(f"Error fetching forecast data: {str(e)}")

    def validate_date_range(self, start_date, end_date):
        """Validate the given date range"""
        try:
            start = datetime.strptime(start_date, '%Y-%m-%d').date()
            end = datetime.strptime(end_date, '%Y-%m-%d').date()
            
            today = datetime.now().date()
            max_future = today + timedelta(days=5)
            max_past = today - timedelta(days=7)
            
            if start > end:
                raise ValueError("Start date must be before end date")
            
            if start < max_past:
                raise ValueError("Start date cannot be more than 7 days in the past")
                
            if end > max_future:
                raise ValueError("End date cannot be more than 5 days in the future")
                
            if (end - start).days > 5:
                raise ValueError("Date range cannot exceed 5 days")
                
            return True
            
        except ValueError as e:
            raise ValueError(f"Date validation error: {str(e)}")