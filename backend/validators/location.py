import re
from typing import Tuple, Optional, Dict, Any
import json

class LocationValidator:
    # Regular expression patterns for different location formats
    PATTERNS = {
        'zip': r'^\d{5}(-\d{4})?$',  # US ZIP code with optional +4
        'coordinates': r'^(-?\d+(\.\d+)?),\s*(-?\d+(\.\d+)?)$',  # lat,lon format
        'city': r'^[A-Za-z\s]{2,},\s*[A-Za-z]{2,}$',  # City, Country format
        'landmark': r'^[A-Za-z0-9\s\-\'\.]{2,}$'  # Common landmark names
    }

    @classmethod
    def validate(cls, location: str) -> Tuple[bool, str, Optional[str]]:
        """
        Validate location input and determine its type.
        
        Args:
            location: The location string to validate
            
        Returns:
            Tuple containing:
            - Boolean indicating if location is valid
            - String message describing the validation result
            - String indicating the location type if valid, None if invalid
        """
        if not location or not isinstance(location, str):
            return False, "Location must be a non-empty string", None

        location = location.strip()
        if len(location) < 2:
            return False, "Location must be at least 2 characters long", None

        # Check each pattern to determine location type
        for location_type, pattern in cls.PATTERNS.items():
            if re.match(pattern, location):
                return True, "Valid location format", location_type

        # If no pattern matches but input looks reasonable, assume landmark
        if cls._is_reasonable_landmark(location):
            return True, "Assumed landmark location", "landmark"

        return False, "Invalid location format", None

    @classmethod
    def _is_reasonable_landmark(cls, location: str) -> bool:
        """
        Check if the location string could reasonably be a landmark.
        
        Args:
            location: The location string to check
            
        Returns:
            Boolean indicating if the string could be a landmark
        """
        # Basic checks for reasonable landmark names
        if len(location) > 100:  # Too long for a typical landmark
            return False
            
        if re.search(r'[^\w\s\-\'\.,:()]', location):  # Contains unusual characters
            return False
            
        words = location.split()
        if len(words) > 10:  # Too many words for typical landmark
            return False
            
        return True

    @classmethod
    def normalize_location(cls, location: str, location_type: str) -> str:
        """
        Normalize location string based on its type.
        
        Args:
            location: The location string to normalize
            location_type: The type of location (zip, coordinates, city, landmark)
            
        Returns:
            Normalized location string
        """
        location = location.strip()
        
        if location_type == 'coordinates':
            # Standardize coordinate format
            try:
                lat, lon = map(float, re.findall(r'-?\d+\.?\d*', location))
                return f"{lat:.6f},{lon:.6f}"
            except ValueError:
                return location
                
        elif location_type == 'city':
            # Capitalize city and country names
            parts = location.split(',')
            return ','.join(part.strip().title() for part in parts)
            
        elif location_type == 'zip':
            # Remove any spaces in ZIP code
            return location.replace(' ', '')
            
        elif location_type == 'landmark':
            # Capitalize significant words
            return ' '.join(word.capitalize() if len(word) > 3 else word
                          for word in location.split())
        
        return location

    @classmethod
    def format_for_display(cls, location: str, location_type: str) -> Dict[str, Any]:
        """
        Format location information for display.
        
        Args:
            location: The location string
            location_type: The type of location
            
        Returns:
            Dictionary containing formatted location information
        """
        normalized = cls.normalize_location(location, location_type)
        
        result = {
            'original': location,
            'normalized': normalized,
            'type': location_type,
            'display_name': normalized
        }
        
        if location_type == 'coordinates':
            try:
                lat, lon = map(float, normalized.split(','))
                result.update({
                    'latitude': lat,
                    'longitude': lon,
                    'display_name': f"({lat:.4f}, {lon:.4f})"
                })
            except ValueError:
                pass
                
        return result