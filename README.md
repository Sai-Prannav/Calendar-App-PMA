# Weather App

A PyQt5-based weather application that displays current weather conditions and 5-day forecasts, with optional location media features and multiple export options.

## Core Features

- Location input supporting multiple formats:
  - City names
  - ZIP codes
  - Coordinates (decimal or degrees)
- Current weather display with:
  - Temperature (°C/°F toggle)
  - Feels like temperature
  - Humidity
  - Wind speed
  - Weather condition
- 5-day forecast with:
  - Daily temperature ranges
  - Weather conditions
  - Precipitation probability
- Data export options:
  - JSON export
  - CSV export
  - PDF report generation
- Input validation and error handling
- Clean, modern user interface
- Rate limiting and error handling for APIs

## Optional Features

The following features require additional API keys:
- Location media integration:
  - YouTube travel videos (requires YouTube Data API)
  - Google Maps static view (requires Google Maps API)
  - Loading indicators for API calls
- "About" dialog with placeholder company information.

## Setup

1. Make sure you have Python 3.8+ installed
2. Clone this repository
3. Create and activate a virtual environment (recommended):
```bash
# On Windows
python -m venv venv
venv\Scripts\activate

# On macOS/Linux
python3 -m venv venv
source venv/bin/activate
```
4. Install the required dependencies:
```bash
# For users: Basic installation
pip install .

# For developers: Install with development dependencies
pip install -e ".[dev]"
```
4. Get API keys:
   
   Required:
   - [OpenWeatherMap API](https://openweathermap.org/api) - Core weather functionality
   
   Optional:
   - [YouTube Data API](https://console.cloud.google.com/apis/library/youtube.googleapis.com) - For location videos
   - [Google Maps API](https://console.cloud.google.com/apis/library/maps-backend.googleapis.com) - For location maps

5. Create a `.env` file from the template:
```bash
cp .env.template .env
```
6. Configure your `.env` file:

   Minimal setup (required):
   ```
   OPENWEATHERMAP_API_KEY=your_api_key_here
   ```
   
   Optional features:
   ```
   YOUTUBE_API_KEY=your_youtube_api_key_here     # For travel videos
   GOOGLE_MAPS_API_KEY=your_maps_api_key_here    # For location maps
   ```

## Running the Application

From the project root directory:

```bash
python src/main.py
```

## Running Tests

The project uses pytest with custom markers for different test categories:

```bash
# Run all tests
pytest

# Run specific test categories
pytest -m "not slow"        # Skip slow tests
pytest -m "not integration" # Skip integration tests
pytest -m "ui"             # Run only UI tests

# Run with coverage report
pytest --cov=src --cov-report=html
```

### Test Categories
- `integration`: Tests that interact with external APIs
- `ui`: Tests for PyQt5 interface components
- `slow`: Tests that take longer to execute

## Troubleshooting

Common issues and solutions:

1. PyQt5 Installation Issues:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install python3-pyqt5
   
   # On Windows
   pip install --upgrade pip setuptools wheel
   pip install PyQt5
   ```

2. Environment Variables Not Loading:
   - Ensure `.env` file exists in project root
   - Verify file permissions
   - Check for proper line endings (no spaces after values)

3. Test Import Errors:
   - Verify you've installed development dependencies: `pip install -e ".[dev]"`
   - Check that PYTHONPATH includes the project root
   - Ensure pytest.ini is in project root

4. API Connection Issues:
   - Verify API keys in `.env` file
   - Check internet connection
   - Confirm API service status

## Project Structure

```
weather_app/
├── src/                    # Source code
│   ├── main.py            # Application entry point
│   ├── ui/                # User interface components
│   ├── core/              # Core functionality and API services
│   ├── database/          # Database operations
│   └── utils/             # Utility functions and export handlers
├── tests/                 # Unit and integration tests
├── requirements.txt       # Dependencies
└── .env                   # Configuration (create from .env.template)
```

## Export Functionality

The application supports three export formats:

1. JSON Export
   - Complete weather data in structured format
   - Includes current conditions and forecast
   - Ideal for data processing and API integration

2. CSV Export
   - Tabular format for spreadsheet applications
   - Separate sections for current weather and forecast
   - Easy to import into Excel or other tools

3. PDF Export
   - Professional report format
   - Includes weather data visualization
   - Suitable for sharing and printing

## API Rate Limits

The application implements rate limiting to respect API quotas:

Required APIs:
- OpenWeatherMap API: As per your API plan

Optional APIs (only if configured):
- YouTube Data API: 30 requests per minute
- Google Maps API: 60 requests per minute

## Contributing

1. Follow PEP 8 style guide
2. Add type hints to new code
3. Include docstrings for modules, classes, and functions
4. Write unit tests for new features
5. Implement integration tests for API features
6. Test changes before submitting

## License

MIT License