"""
Main Window Module - Primary application interface using PyQt5.
"""
import os
from typing import Optional, List
import webbrowser
from pathlib import Path

from PyQt5.QtCore import Qt, QSize, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QMessageBox, QFileDialog,
    QMenu, QProgressBar, QDialog, QTextEdit
)
from PyQt5.QtGui import QIcon

import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from src.core.api_services import APIServices, LocationMedia
from src.utils.export import DataExporter
from src.database.session import SessionManager
from src.database.operations import DatabaseOperations

from src.ui.widgets.location_input import LocationInput
from src.ui.widgets.weather_display import WeatherDisplay
from src.ui.widgets.forecast_view import ForecastView
from src.core.weather_service import WeatherService, WeatherData, ForecastData

class MainWindow(QMainWindow):
    """Main application window."""
    
    # Custom worker thread signal
    class APIWorker(QThread):
        finished = pyqtSignal(object)
        error = pyqtSignal(str)
        
        def __init__(self, func, *args):
            super().__init__()
            self.func = func
            self.args = args
            
        def run(self):
            try:
                result = self.func(*self.args)
                self.finished.emit(result)
            except Exception as e:
                self.error.emit(str(e))
    
    def __init__(self, weather_service: WeatherService, api_services: APIServices):
        """Initialize the main window.
        
        Args:
            weather_service: Instance of WeatherService for API interactions
            api_services: Instance of APIServices for additional API features
        """
        super().__init__()
        
        self.weather_service = weather_service
        self.api_services = api_services
        self.session_manager = SessionManager()
        self.setWindowTitle("Weather App by Sai Prannav")
        self.setMinimumSize(QSize(800, 600))
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create UI components
        self._setup_header(layout)
        self._setup_weather_display(layout)
        self._setup_forecast(layout)
        self._setup_media_display(layout)
        self._setup_footer(layout)
        
        # Initialize empty state
        self.current_weather: Optional[WeatherData] = None
        self.current_location: Optional[tuple[float, float]] = None
        self.current_location_name: Optional[str] = None
        self.location_media: Optional[LocationMedia] = None
    
    def _setup_header(self, parent_layout: QVBoxLayout) -> None:
        """Set up the header section with location input."""
        header_layout = QHBoxLayout()
        
        # Location input
        self.location_input = LocationInput(self.weather_service)
        self.location_input.location_selected.connect(self._update_weather)
        header_layout.addWidget(self.location_input)
        
        # Export button
        export_btn = QPushButton("Export")
        export_btn.setFixedWidth(60)
        export_menu = QMenu(export_btn)
        export_menu.addAction("Export to JSON", self._export_json)
        export_menu.addAction("Export to CSV", self._export_csv)
        export_menu.addAction("Export to PDF", self._export_pdf)
        export_btn.setMenu(export_menu)
        header_layout.addWidget(export_btn)
        
        parent_layout.addLayout(header_layout)
    
    def _setup_weather_display(self, parent_layout: QVBoxLayout) -> None:
        """Set up the current weather display section."""
        self.weather_display = WeatherDisplay()
        parent_layout.addWidget(self.weather_display)
    
    def _setup_forecast(self, parent_layout: QVBoxLayout) -> None:
        """Set up the forecast display section."""
        forecast_label = QLabel("5-Day Forecast")
        forecast_label.setAlignment(Qt.AlignCenter)
        parent_layout.addWidget(forecast_label)
        
        self.forecast_view = ForecastView()
        parent_layout.addWidget(self.forecast_view)
    
    def _setup_media_display(self, parent_layout: QVBoxLayout) -> None:
        """Set up the media display section."""
        self.media_container = QWidget()
        media_layout = QVBoxLayout(self.media_container)
        
        # Loading indicator
        self.loading_bar = QProgressBar()
        self.loading_bar.setTextVisible(False)
        self.loading_bar.hide()
        media_layout.addWidget(self.loading_bar)
        
        # Media content
        self.media_content = QLabel("Select a location to view related media")
        self.media_content.setAlignment(Qt.AlignCenter)
        media_layout.addWidget(self.media_content)
        
        parent_layout.addWidget(self.media_container)

    def _setup_footer(self, parent_layout: QVBoxLayout) -> None:
        """Set up the footer section."""
        footer_layout = QHBoxLayout()
        
        # Company info button
        company_btn = QPushButton("Info About PM Accelerator")
        company_btn.clicked.connect(self._show_about_dialog)
        footer_layout.addWidget(company_btn)
        
        parent_layout.addLayout(footer_layout)

    def _show_about_dialog(self):
        info_text = (
            "The Product Manager Accelerator Program is designed to support PM professionals through every stage of their careers. From students looking for entry-level jobs to Directors looking to take on a leadership role, our program has helped over hundreds of students fulfill their career aspirations."
            "Our Product Manager Accelerator community are ambitious and committed. Through our program they have learnt, honed and developed new PM and leadership skills, giving them a strong foundation for their future endeavors."
        )
        QMessageBox.information(self, "About PM Accelerator", info_text)

    def _update_weather(self, lat: float, lon: float) -> None:
        """Update weather display with data for given coordinates.
        
        Args:
            lat: Latitude
            lon: Longitude
        """
        try:
            self.loading_bar.show()
            self.loading_bar.setRange(0, 0)  # Indeterminate mode
            
            # Start weather data fetch in background
            self.weather_worker = self.APIWorker(
                self.weather_service.get_current_weather,
                lat, lon
            )
            self.weather_worker.finished.connect(self._handle_weather_result)
            self.weather_worker.error.connect(self._handle_api_error)
            self.weather_worker.start()
            
            # Start forecast fetch in background
            self.forecast_worker = self.APIWorker(
                self.weather_service.get_forecast,
                lat, lon
            )
            self.forecast_worker.finished.connect(self._handle_forecast_result)
            self.forecast_worker.error.connect(self._handle_api_error)
            self.forecast_worker.start()
            
            # Store location
            self.current_location = (lat, lon)
            self.current_location_name = self.location_input.text()
            
            # Fetch location media
            self.media_worker = self.APIWorker(
                self.api_services.get_location_media,
                self.current_location_name
            )
            self.media_worker.finished.connect(self._handle_media_result)
            self.media_worker.error.connect(self._handle_api_error)
            self.media_worker.start()
            
        except Exception as e:
            self._handle_api_error(str(e))
            
    def _handle_weather_result(self, weather_data: WeatherData) -> None:
        """Handle weather data result."""
        self.current_weather = weather_data
        self.weather_display.update_display(weather_data, self.current_location_name)
        self._check_loading_complete()
        
    def _handle_forecast_result(self, forecast_data: List[ForecastData]) -> None:
        """Handle forecast data result."""
        self.forecast_view.update_forecast(forecast_data)
        self._check_loading_complete()
        
    def _handle_media_result(self, media_data: LocationMedia) -> None:
        """Handle media data result."""
        self.location_media = media_data
        self._update_media_display()
        self._check_loading_complete()
        
    def _handle_api_error(self, error_msg: str) -> None:
        """Handle API error."""
        self.loading_bar.hide()
        QMessageBox.warning(self, "Error", f"Failed to fetch data: {error_msg}")
        
    def _check_loading_complete(self) -> None:
        """Check if all API calls are complete."""
        if hasattr(self, 'current_weather') and \
           hasattr(self, 'forecast_view') and \
           hasattr(self, 'location_media'):
            self.loading_bar.hide()
            
    def _update_media_display(self) -> None:
        """Update the media display with location content."""
        if not self.location_media:
            return
            
        content = "<h3>Location Media</h3>"
        
        # Add static map if available
        if self.location_media.static_map_url:
            content += f'<img src="{self.location_media.static_map_url}" width="400"/><br/><br/>'
        else:
            content += "<p><i>Map view not available - Google Maps API key not configured</i></p><br/>"
        
        # Add videos
        if self.location_media.videos:
            content += "<h4>Related Videos:</h4>"
            for video in self.location_media.videos:
                content += f"""
                    <p><a href="https://youtube.com/watch?v={video.video_id}">{video.title}</a></p>
                    <img src="{video.thumbnail_url}" width="200"/>
                    <br/>
                """
        else:
            content += "<p><i>No related videos found</i></p>"
            
        self.media_content.setText(content)
        self.media_content.setOpenExternalLinks(True)
    
    def _export_json(self) -> None:
        """Export weather data to JSON."""
        if not self.current_weather:
            QMessageBox.warning(self, "Error", "No weather data to export")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to JSON", "", "JSON Files (*.json)"
        )
        if filepath:
            try:
                DataExporter.export_to_json(
                    self.current_weather,
                    self.forecast_view.get_forecast_data(),
                    self.current_location_name,
                    filepath
                )
                QMessageBox.information(
                    self, "Success", "Data exported successfully"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to export data: {str(e)}"
                )

    def _export_csv(self) -> None:
        """Export weather data to CSV."""
        if not self.current_weather:
            QMessageBox.warning(self, "Error", "No weather data to export")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to CSV", "", "CSV Files (*.csv)"
        )
        if filepath:
            try:
                DataExporter.export_to_csv(
                    self.current_weather,
                    self.forecast_view.get_forecast_data(),
                    self.current_location_name,
                    filepath
                )
                QMessageBox.information(
                    self, "Success", "Data exported successfully"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to export data: {str(e)}"
                )

    def _export_pdf(self) -> None:
        """Export weather data to PDF."""
        if not self.current_weather:
            QMessageBox.warning(self, "Error", "No weather data to export")
            return
            
        filepath, _ = QFileDialog.getSaveFileName(
            self, "Export to PDF", "", "PDF Files (*.pdf)"
        )
        if filepath:
            try:
                DataExporter.export_to_pdf(
                    self.current_weather,
                    self.forecast_view.get_forecast_data(),
                    self.current_location_name,
                    filepath
                )
                QMessageBox.information(
                    self, "Success", "Data exported successfully"
                )
            except Exception as e:
                QMessageBox.warning(
                    self, "Error", f"Failed to export data: {str(e)}"
                )

    def closeEvent(self, event) -> None:
        """Handle application shutdown."""
        # Clean up any resources
        self.weather_service.session.close()
        self.api_services.close()
        super().closeEvent(event)

    def get_db(self) -> DatabaseOperations:
        """Get a database operations instance with a new session."""
        session = self.session_manager.get_session()
        return DatabaseOperations(session)

    def save_weather_data(self, weather_data: WeatherData) -> None:
        """Save weather data to the database."""
        with self.session_manager.session_scope() as session:
            db = DatabaseOperations(session)
            db.save_weather_data(
                location_name=weather_data.location_name,
                lat=weather_data.latitude,
                lon=weather_data.longitude,
                temperature=weather_data.temperature,
                feels_like=weather_data.feels_like,
                humidity=weather_data.humidity,
                wind_speed=weather_data.wind_speed,
                condition=weather_data.condition
            )