"""
Input validation utilities for the weather application.
"""
import re
from typing import Union, Optional, Tuple

def validate_coordinates(lat: Union[str, float], lon: Union[str, float]) -> Tuple[float, float]:
    """Validate and convert latitude and longitude values.
    
    Args:
        lat: Latitude value as string or float
        lon: Longitude value as string or float
        
    Returns:
        Tuple of (latitude, longitude) as floats
        
    Raises:
        ValueError: If coordinates are invalid
    """
    try:
        lat_float = float(lat)
        lon_float = float(lon)
    except ValueError:
        raise ValueError("Coordinates must be numeric values")
    
    if not (-90 <= lat_float <= 90):
        raise ValueError("Latitude must be between -90 and 90 degrees")
    if not (-180 <= lon_float <= 180):
        raise ValueError("Longitude must be between -180 and 180 degrees")
    
    return (lat_float, lon_float)

def validate_zip_code(zip_code: str) -> bool:
    """Validate a US ZIP code format.
    
    Args:
        zip_code: ZIP code to validate
        
    Returns:
        True if valid, False otherwise
    """
    zip_pattern = r'^\d{5}(?:-\d{4})?$'
    return bool(re.match(zip_pattern, zip_code))

def validate_city_name(city: str) -> bool:
    """Validate city name format.
    
    Args:
        city: City name to validate
        
    Returns:
        True if valid, False otherwise
    """
    # Basic validation - allow letters, spaces, and common punctuation
    city_pattern = r'^[A-Za-z\s\.\-\']+$'
    return bool(re.match(city_pattern, city))

def parse_location_input(text: str) -> Optional[Tuple[str, str]]:
    """Parse location input to determine its type.
    
    Args:
        text: Location input text
        
    Returns:
        Tuple of (type, value) where type is 'coordinates', 'zip', or 'city',
        or None if input format is invalid
    """
    text = text.strip()
    
    # Check for coordinates (decimal format)
    coord_pattern = r'^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$'
    if match := re.match(coord_pattern, text):
        try:
            validate_coordinates(*match.groups())
            return ('coordinates', text)
        except ValueError:
            pass
    
    # Check for ZIP code
    if validate_zip_code(text):
        return ('zip', text)
    
    # Check for city name
    if validate_city_name(text):
        return ('city', text)
    
    return None