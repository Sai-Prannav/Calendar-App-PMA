"""
Weather Application - Main entry point
"""
import os
import sys
from dotenv import load_dotenv
from PyQt5.QtWidgets import QApplication, QMessageBox

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from src.core.weather_service import WeatherService
from src.core.api_services import APIServices
from src.ui.main_window import MainWindow
from src.database.models import init_db
from src.database.session import SessionManager

def main():
    """Application entry point."""
    # Load environment variables
    load_dotenv()
    
    # Validate required API keys
    openweather_key = os.getenv('OPENWEATHERMAP_API_KEY')
    youtube_key = os.getenv('YOUTUBE_API_KEY')
    maps_key = os.getenv('GOOGLE_MAPS_API_KEY')
    
    missing_keys = []
    if not openweather_key:
        missing_keys.append("OPENWEATHERMAP_API_KEY")
    if not youtube_key:
        missing_keys.append("YOUTUBE_API_KEY")
    if not maps_key:
        missing_keys.append("GOOGLE_MAPS_API_KEY")
        
    if missing_keys:
        print("Error: The following API keys are not set:")
        for key in missing_keys:
            print(f"- {key}")
        print("\nPlease add them to your .env file:")
        print("OPENWEATHERMAP_API_KEY=your_key_here")
        print("YOUTUBE_API_KEY=your_key_here")
        print("GOOGLE_MAPS_API_KEY=your_key_here")
        sys.exit(1)
    
    # Initialize application
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for consistent look
    
    try:
        # Initialize database
        db_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'weather_app.db')
        engine, Session = init_db(db_path)
        session_manager = SessionManager(db_path)
        
        # Create services
        weather_service = WeatherService(openweather_key)
        api_services = APIServices(youtube_key, maps_key)
        
        # Create and show main window
        window = MainWindow(weather_service, api_services)
        window.show()
        
        # Start event loop
        sys.exit(app.exec_())
        
    except Exception as e:
        QMessageBox.critical(
            None,
            "Application Error",
            f"An error occurred while starting the application:\n{str(e)}"
        )
        sys.exit(1)

if __name__ == '__main__':
    main()