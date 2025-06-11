"""
Dialog for editing weather records.
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QDialogButtonBox, QSpinBox,
    QDoubleSpinBox
)

from ...database import WeatherRecord

class WeatherEditDialog(QDialog):
    """Dialog for editing weather record data."""

    def __init__(self, record: WeatherRecord, parent=None):
        """Initialize the dialog with weather record data."""
        super().__init__(parent)
        self.record = record
        self.setWindowTitle("Edit Weather Record")
        self.setup_ui()

    def setup_ui(self) -> None:
        """Set up the dialog's user interface."""
        layout = QVBoxLayout()
        self.setLayout(layout)

        # Temperature
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature (°C):"))
        self.temp_input = QDoubleSpinBox()
        self.temp_input.setRange(-100, 100)
        self.temp_input.setDecimals(1)
        # Use dict access if record is a dict, else attribute access
        get = self.record.get if isinstance(self.record, dict) else lambda k: getattr(self.record, k)
        self.temp_input.setValue(get('temperature') if get('temperature') is not None else 0.0)
        temp_layout.addWidget(self.temp_input)
        layout.addLayout(temp_layout)

        # Feels Like
        feels_layout = QHBoxLayout()
        feels_layout.addWidget(QLabel("Feels Like (°C):"))
        self.feels_input = QDoubleSpinBox()
        self.feels_input.setRange(-100, 100)
        self.feels_input.setDecimals(1)
        self.feels_input.setValue(get('feels_like') if get('feels_like') is not None else 0.0)
        feels_layout.addWidget(self.feels_input)
        layout.addLayout(feels_layout)

        # Humidity
        humidity_layout = QHBoxLayout()
        humidity_layout.addWidget(QLabel("Humidity (%):"))
        self.humidity_input = QSpinBox()
        self.humidity_input.setRange(0, 100)
        self.humidity_input.setValue(get('humidity') if get('humidity') is not None else 0)
        humidity_layout.addWidget(self.humidity_input)
        layout.addLayout(humidity_layout)

        # Wind Speed
        wind_layout = QHBoxLayout()
        wind_layout.addWidget(QLabel("Wind Speed (m/s):"))
        self.wind_input = QDoubleSpinBox()
        self.wind_input.setRange(0, 200)
        self.wind_input.setDecimals(1)
        self.wind_input.setValue(get('wind_speed') if get('wind_speed') is not None else 0.0)
        wind_layout.addWidget(self.wind_input)
        layout.addLayout(wind_layout)

        # Condition
        condition_layout = QHBoxLayout()
        condition_layout.addWidget(QLabel("Condition:"))
        self.condition_input = QLineEdit(get('condition') if get('condition') is not None else "")
        condition_layout.addWidget(self.condition_input)
        layout.addLayout(condition_layout)

        # Dialog buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)

    def get_updated_data(self) -> dict:
        """Get the updated weather record data.
        
        Returns:
            Dictionary containing updated weather record values
        """
        return {
            'temperature': self.temp_input.value(),
            'feels_like': self.feels_input.value(),
            'humidity': self.humidity_input.value(),
            'wind_speed': self.wind_input.value(),
            'condition': self.condition_input.text()
        }