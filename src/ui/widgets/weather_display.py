"""
Weather Display Widget - Shows current weather conditions.
"""
from datetime import date, datetime, timedelta
from typing import List, Optional

from ..dialogs import WeatherEditDialog

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QDateEdit, QTableWidget,
    QTableWidgetItem, QHeaderView, QMessageBox
)

from ...database import db
from ...database.operations import DatabaseOperations
from ...database.session import SessionManager
from ...core.weather_service import WeatherData

class WeatherDisplay(QWidget):
    """Widget for displaying current weather conditions."""
    
    def __init__(self):
        """Initialize the weather display widget."""
        super().__init__()
        
        self.use_celsius = True  # Temperature unit flag
        self._current_temp: Optional[float] = None
        self._current_location = None
        self.session_manager = SessionManager()  # Initialize session manager
        
        # Set up the UI
        layout = QVBoxLayout()
        self.setLayout(layout)
        
        # Create frames
        self._setup_main_display(layout)
        self._setup_details(layout)
        self._setup_date_range(layout)
        self._setup_history_table(layout)
        
        # Initial empty state
        self.clear_display()

    def _setup_main_display(self, parent_layout: QVBoxLayout) -> None:
        """Set up the main weather display section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        # Temperature and unit toggle
        temp_layout = QHBoxLayout()
        self.temp_label = QLabel()
        self.temp_label.setStyleSheet("font-size: 48px;")
        temp_layout.addWidget(self.temp_label)
        
        unit_toggle = QPushButton("°C/°F")
        unit_toggle.clicked.connect(self._toggle_unit)
        temp_layout.addWidget(unit_toggle)
        temp_layout.addStretch()
        layout.addLayout(temp_layout)
        
        # Condition and icon
        self.condition_label = QLabel()
        self.condition_label.setStyleSheet("font-size: 24px;")
        layout.addWidget(self.condition_label)
        
        parent_layout.addWidget(frame)
    
    def _setup_details(self, parent_layout: QVBoxLayout) -> None:
        """Set up the weather details section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout()
        frame.setLayout(layout)
        
        # Feels like temperature
        feels_layout = QHBoxLayout()
        feels_layout.addWidget(QLabel("Feels like:"))
        self.feels_like_label = QLabel()
        feels_layout.addWidget(self.feels_like_label)
        feels_layout.addStretch()
        layout.addLayout(feels_layout)
        
        # Humidity
        humidity_layout = QHBoxLayout()
        humidity_layout.addWidget(QLabel("Humidity:"))
        self.humidity_label = QLabel()
        humidity_layout.addWidget(self.humidity_label)
        humidity_layout.addStretch()
        layout.addLayout(humidity_layout)
        
        # Wind speed
        wind_layout = QHBoxLayout()
        wind_layout.addWidget(QLabel("Wind speed:"))
        self.wind_label = QLabel()
        wind_layout.addWidget(self.wind_label)
        wind_layout.addStretch()
        layout.addLayout(wind_layout)
        
        parent_layout.addWidget(frame)
    
    def _setup_date_range(self, parent_layout: QVBoxLayout) -> None:
        """Set up the date range selection section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout()
        frame.setLayout(layout)

        # Date range controls
        date_layout = QHBoxLayout()
        date_layout.addWidget(QLabel("Date Range:"))
        
        self.start_date = QDateEdit()
        self.start_date.setDate(date.today() - timedelta(days=7))
        self.start_date.setCalendarPopup(True)
        date_layout.addWidget(self.start_date)
        
        date_layout.addWidget(QLabel("to"))
        
        self.end_date = QDateEdit()
        self.end_date.setDate(date.today())
        self.end_date.setCalendarPopup(True)
        date_layout.addWidget(self.end_date)
        
        refresh_btn = QPushButton("Refresh History")
        refresh_btn.clicked.connect(self._load_history)
        date_layout.addWidget(refresh_btn)
        
        layout.addLayout(date_layout)
        parent_layout.addWidget(frame)

    def _setup_history_table(self, parent_layout: QVBoxLayout) -> None:
        """Set up the historical weather data table."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout()
        frame.setLayout(layout)

        # History table
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(7)
        self.history_table.setHorizontalHeaderLabels([
            "Date", "Temperature", "Feels Like", "Humidity",
            "Wind Speed", "Condition", "Actions"
        ])
        header = self.history_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeToContents)
        layout.addWidget(self.history_table)

        parent_layout.addWidget(frame)

    def _load_history(self) -> None:
        """Load historical weather data for selected date range."""
        if not self._current_location:
            self.history_table.setRowCount(0)
            return

        start = self.start_date.date().toPyDate()
        end = self.end_date.date().toPyDate()

        if start > end:
            QMessageBox.warning(
                self,
                "Invalid Date Range",
                "Start date must be before or equal to end date."
            )
            return

        try:
            with self.session_manager.session_scope() as session:
                db_ops = DatabaseOperations(session)
                history = db_ops.get_weather_history(
                    location_name=self._current_location,
                    start_date=start,
                    end_date=end
                )
                self._display_history(history)
        except Exception as e:
            QMessageBox.warning(
                self,
                "Database Error",
                f"Failed to load weather history: {str(e)}"
            )

    def _display_history(self, records: List) -> None:
        """Display historical weather records in the table."""
        self.history_table.setRowCount(len(records))
        if not records:
            return
        for row, record in enumerate(records):
            # Copy record data to a plain dict to avoid DetachedInstanceError
            record_data = {
                'id': record.id,
                'timestamp': record.timestamp,
                'temperature': record.temperature,
                'feels_like': record.feels_like,
                'humidity': record.humidity,
                'wind_speed': record.wind_speed,
                'condition': record.condition,
                'location_name': record.location_name,
                'latitude': record.latitude,
                'longitude': record.longitude,
                'date_range_start': getattr(record, 'date_range_start', None),
                'date_range_end': getattr(record, 'date_range_end', None),
            }
            # Date
            self.history_table.setItem(
                row, 0,
                QTableWidgetItem(record.timestamp.strftime("%Y-%m-%d %H:%M"))
            )
            
            # Temperature
            temp = self._convert_temp(record.temperature)
            self.history_table.setItem(
                row, 1,
                QTableWidgetItem(f"{temp}°{'C' if self.use_celsius else 'F'}")
            )
            
            # Feels Like
            feels_like = self._convert_temp(record.feels_like) if record.feels_like else "--"
            self.history_table.setItem(
                row, 2,
                QTableWidgetItem(f"{feels_like}°{'C' if self.use_celsius else 'F'}" if feels_like != "--" else "--")
            )
            
            # Humidity
            self.history_table.setItem(
                row, 3,
                QTableWidgetItem(f"{record.humidity}%" if record.humidity else "--")
            )
            
            # Wind Speed
            self.history_table.setItem(
                row, 4,
                QTableWidgetItem(f"{record.wind_speed} m/s" if record.wind_speed else "--")
            )
            
            # Condition
            self.history_table.setItem(
                row, 5,
                QTableWidgetItem(record.condition)
            )
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout()
            actions_layout.setContentsMargins(0, 0, 0, 0)
            
            edit_btn = QPushButton("Edit")
            edit_btn.clicked.connect(lambda checked, r=record_data: self._edit_record(r))
            actions_layout.addWidget(edit_btn)
            
            delete_btn = QPushButton("Delete")
            delete_btn.clicked.connect(lambda checked, r=record_data: self._delete_record(r))
            actions_layout.addWidget(delete_btn)
            
            actions_widget.setLayout(actions_layout)
            self.history_table.setCellWidget(row, 6, actions_widget)

    def _edit_record(self, record) -> None:
        """Open dialog to edit a weather record."""
        dialog = WeatherEditDialog(record, self)
        if dialog.exec_():
            updated_data = dialog.get_updated_data()
            try:
                with self.session_manager.session_scope() as session:
                    db_ops = DatabaseOperations(session)
                    if db_ops.update_weather_record(record.id, **updated_data):
                        self._load_history()
                    else:
                        raise Exception("Failed to update record")
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Update Failed",
                    f"Failed to update the weather record: {str(e)}"
                )

    def _delete_record(self, record) -> None:
        """Delete a weather record after confirmation."""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            "Are you sure you want to delete this record?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with self.session_manager.session_scope() as session:
                    db_ops = DatabaseOperations(session)
                    if db_ops.delete_weather_record(record['id']):
                        self._load_history()
                    else:
                        raise Exception("Failed to delete record")
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Delete Failed",
                    f"Failed to delete the weather record: {str(e)}"
                )

    def update_display(self, weather: WeatherData, location_name: str) -> None:
        """Update the display with new weather data.
        
        Args:
            weather: WeatherData instance containing current conditions
            location_name: Name of the location
        """
        self._current_temp = weather.temperature
        self._current_location = location_name
        
        # Update temperature display
        self._update_temperature_display()
        
        # Update location and other fields
        self.condition_label.setText(f"{location_name} - {weather.condition.title()}")
        self.feels_like_label.setText(
            f"{self._convert_temp(weather.feels_like)}°"
            f"{'C' if self.use_celsius else 'F'}"
        )
        self.humidity_label.setText(f"{weather.humidity}%")
        self.wind_label.setText(f"{weather.wind_speed} m/s")
        
        # TODO: Add weather icon display
        # self.icon_label.setPixmap(...)
        
        self._load_history()  # Refresh table after weather update
    
    def clear_display(self) -> None:
        """Clear all weather information from the display."""
        self._current_temp = None
        self.temp_label.setText("--")
        self.condition_label.setText("No data")
        self.feels_like_label.setText("--")
        self.humidity_label.setText("--")
        self.wind_label.setText("--")
    
    def _toggle_unit(self) -> None:
        """Toggle between Celsius and Fahrenheit."""
        self.use_celsius = not self.use_celsius
        self._update_temperature_display()
    
    def _update_temperature_display(self) -> None:
        """Update temperature display with current unit setting."""
        if self._current_temp is not None:
            temp = self._convert_temp(self._current_temp)
            self.temp_label.setText(
                f"{temp}°{'C' if self.use_celsius else 'F'}"
            )
    
    def _convert_temp(self, celsius: float) -> float:
        """Convert temperature based on current unit setting.
        
        Args:
            celsius: Temperature in Celsius
            
        Returns:
            Temperature in current display unit
        """
        if self.use_celsius:
            return round(celsius, 1)
        return round((celsius * 9/5) + 32, 1)