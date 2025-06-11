"""
Forecast View Widget - Displays 5-day weather forecast.
"""
from datetime import datetime
from typing import List

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QHBoxLayout, QVBoxLayout, QLabel,
    QFrame
)

from ...core.weather_service import ForecastData

class ForecastDayWidget(QFrame):
    """Widget displaying a single day's forecast."""
    
    def __init__(self):
        """Initialize the forecast day widget."""
        super().__init__()
        self.setFrameStyle(QFrame.StyledPanel)
        
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create labels
        self.date_label = QLabel()
        self.date_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.date_label)
        
        self.temp_label = QLabel()
        self.temp_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.temp_label)
        
        self.condition_label = QLabel()
        self.condition_label.setAlignment(Qt.AlignCenter)
        self.condition_label.setWordWrap(True)
        layout.addWidget(self.condition_label)
        
        self.precip_label = QLabel()
        self.precip_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.precip_label)
    
    def update_forecast(self, forecast: ForecastData, use_celsius: bool = True) -> None:
        """Update the display with forecast data.
        
        Args:
            forecast: ForecastData instance for this day
            use_celsius: Whether to display temperature in Celsius
        """
        # Format date
        self.date_label.setText(
            forecast.date.strftime("%A\n%b %d")
        )
        
        # Convert and display temperatures
        if use_celsius:
            min_temp = round(forecast.temp_min, 1)
            max_temp = round(forecast.temp_max, 1)
            unit = "°C"
        else:
            min_temp = round((forecast.temp_min * 9/5) + 32, 1)
            max_temp = round((forecast.temp_max * 9/5) + 32, 1)
            unit = "°F"
        
        self.temp_label.setText(
            f"{max_temp}{unit}\n{min_temp}{unit}"
        )
        
        # Display condition and precipitation
        self.condition_label.setText(forecast.condition.title())
        self.precip_label.setText(
            f"{int(forecast.precipitation_prob * 100)}% precip"
        )
        
        # TODO: Add weather icon display
        # self.icon_label.setPixmap(...)

class ForecastView(QWidget):
    """Widget for displaying 5-day weather forecast."""
    
    def __init__(self):
        """Initialize the forecast view widget."""
        super().__init__()
        
        layout = QHBoxLayout()
        self.setLayout(layout)
        
        # Create day widgets
        self.day_widgets = []
        for _ in range(5):
            day_widget = ForecastDayWidget()
            self.day_widgets.append(day_widget)
            layout.addWidget(day_widget)
        
        self._forecast_data = []
    
    def update_forecast(self, forecast_data: List[ForecastData]) -> None:
        """Update the display with new forecast data.
        
        Args:
            forecast_data: List of ForecastData instances for next 5 days
        """
        self._forecast_data = forecast_data
        # Use min() to handle case where API returns fewer than 5 days
        for i in range(min(len(forecast_data), 5)):
            self.day_widgets[i].update_forecast(forecast_data[i])
    
    def get_forecast_data(self) -> List[ForecastData]:
        """Return the current forecast data as a list."""
        return self._forecast_data

    def clear_forecast(self) -> None:
        """Clear all forecast information."""
        for widget in self.day_widgets:
            widget.date_label.setText("--")
            widget.temp_label.setText("--\n--")
            widget.condition_label.setText("No data")
            widget.precip_label.setText("--")
        self._forecast_data = []