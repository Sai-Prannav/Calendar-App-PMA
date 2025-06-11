"""
Location Input Widget - Handles location input with validation and auto-completion.
"""
import re
from typing import Optional, Tuple

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QLineEdit, QPushButton,
    QCompleter, QMessageBox
)

from ...core.weather_service import WeatherService

class LocationInput(QWidget):
    """Widget for location input with validation and detection."""
    
    # Signal emitted when valid location is selected (lat, lon)
    location_selected = pyqtSignal(float, float)
    
    def __init__(self, weather_service: WeatherService):
        """Initialize the location input widget.
        
        Args:
            weather_service: WeatherService instance for geocoding
        """
        super().__init__()
        self.weather_service = weather_service
        
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        
        self._setup_input()
        self._setup_buttons()
    
    def _setup_input(self) -> None:
        """Set up the location input field."""
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Enter city, ZIP code, or coordinates")
        self.input_field.returnPressed.connect(self._handle_input)
        
        # Add to layout
        self.layout().addWidget(self.input_field)
    
    def _setup_buttons(self) -> None:
        """Set up the search and location detection buttons."""
        # Search button
        search_btn = QPushButton("🔍")
        search_btn.setFixedWidth(40)
        search_btn.clicked.connect(self._handle_input)
        self.layout().addWidget(search_btn)
        
        # Current location button
        location_btn = QPushButton("📍")
        location_btn.setFixedWidth(40)
        location_btn.setToolTip("Use current location")
        location_btn.clicked.connect(self._detect_location)
        self.layout().addWidget(location_btn)
    
    def _handle_input(self) -> None:
        """Process the location input and emit coordinates if valid."""
        text = self.input_field.text().strip()
        if not text:
            return
        
        # Try parsing as coordinates first
        coords = self._parse_coordinates(text)
        if coords:
            self.location_selected.emit(coords[0], coords[1])
            return
        
        # If not coordinates, try geocoding
        try:
            coords = self.weather_service.geocode_location(text)
            if coords:
                self.location_selected.emit(coords[0], coords[1])
            else:
                QMessageBox.warning(
                    self,
                    "Location Not Found",
                    f"Could not find location: {text}"
                )
        except ConnectionError as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to geocode location: {str(e)}"
            )
    
    def _parse_coordinates(self, text: str) -> Optional[Tuple[float, float]]:
        """Try to parse text as coordinates.
        
        Supports formats:
        - Decimal: "51.5074, -0.1278"
        - Degrees: "51°30'26\"N 0°7'39\"W"
        
        Args:
            text: Input text to parse
            
        Returns:
            Tuple of (latitude, longitude) if valid, None otherwise
        """
        # Try decimal format
        decimal_pattern = r'^(-?\d+\.?\d*),\s*(-?\d+\.?\d*)$'
        if match := re.match(decimal_pattern, text):
            lat, lon = map(float, match.groups())
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return (lat, lon)
        
        # Try degrees format
        degrees_pattern = (
            r'^(\d+)°(\d+)\'(\d+)"([NS])\s*'
            r'(\d+)°(\d+)\'(\d+)"([EW])$'
        )
        if match := re.match(degrees_pattern, text):
            lat_d, lat_m, lat_s, lat_dir, lon_d, lon_m, lon_s, lon_dir = match.groups()
            
            # Convert to decimal degrees
            lat = (int(lat_d) + int(lat_m)/60 + int(lat_s)/3600)
            lon = (int(lon_d) + int(lon_m)/60 + int(lon_s)/3600)
            
            # Apply direction
            if lat_dir == 'S':
                lat = -lat
            if lon_dir == 'W':
                lon = -lon
            
            if -90 <= lat <= 90 and -180 <= lon <= 180:
                return (lat, lon)
        
        return None
    
    def _detect_location(self) -> None:
        """Attempt to detect current location using browser geolocation.
        
        Note: This is a placeholder. In a real implementation, you would:
        1. Use a proper geolocation service or device GPS
        2. Handle permissions appropriately
        3. Implement proper error handling
        """
        # For demonstration, using New York coordinates
        self.location_selected.emit(40.7128, -74.0060)
        QMessageBox.information(
            self,
            "Location Detection",
            "Note: Currently using demo location (New York)\n"
            "Real location detection would be implemented in production."
        )
    
    def text(self) -> str:
        """Return the current location text.
        
        Returns:
            str: The current text in the location input field
        """
        return self.input_field.text().strip()