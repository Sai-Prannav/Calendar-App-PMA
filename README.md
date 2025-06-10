# Weather Application

A comprehensive weather application that allows users to check current weather conditions, get forecasts, and maintain a history of weather queries. Built as part of the PM Accelerator program.

## Features

- Current weather information for any location
- 5-day weather forecast
- Multiple location input formats support (ZIP code, coordinates, city names, landmarks)
- Interactive map integration
- Weather query history with CRUD operations
- Data export in JSON and CSV formats
- Responsive design
- Developer information and PM Accelerator link

## Tech Stack

### Backend
- Python 3.8+
- Flask (Web framework)
- SQLite (Database)
- OpenWeather API
- Google Maps API
- YouTube API (optional)

### Frontend
- HTML5/CSS3
- JavaScript (ES6+)
- Bootstrap 5
- Axios (HTTP client)

## Prerequisites

- Python 3.8 or higher
- Node.js and npm (for frontend development tools)
- OpenWeather API key
- Google Maps API key (optional)
- YouTube API key (optional)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/weather-app.git
cd weather-app
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
# On Windows
venv\Scripts\activate
# On macOS/Linux
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the project root with your API keys:
```
OPENWEATHER_API_KEY=your_openweather_api_key
GOOGLE_MAPS_API_KEY=your_google_maps_api_key
YOUTUBE_API_KEY=your_youtube_api_key
```

## Running the Application

1. Start the Flask backend server:
```bash
# From the project root
python backend/main.py
```

2. Open `frontend/index.html` in your web browser or serve it using a local development server.

## API Endpoints

### Weather Operations
- `GET /api/weather/current` - Get current weather
- `GET /api/weather/forecast` - Get weather forecast
- `GET /api/weather` - Get weather query history
- `POST /api/weather` - Create new weather query
- `PUT /api/weather/:id` - Update weather query
- `DELETE /api/weather/:id` - Delete weather query

### Export Operations
- `GET /api/weather/export?format=json` - Export data as JSON
- `GET /api/weather/export?format=csv` - Export data as CSV

### Location Media
- `GET /api/location/media` - Get location media (maps, videos)

## Project Structure
```
weather-app/
├── backend/
│   ├── main.py                 # Flask application
│   ├── weather_service.py      # Weather API client
│   ├── database.py            # Database operations
│   ├── validators/
│   │   ├── location.py
│   │   └── date_range.py
│   └── error_handlers/
│       └── api_errors.py
├── frontend/
│   ├── index.html
│   ├── styles/
│   │   └── main.css
│   ├── js/
│   │   ├── app.js
│   │   ├── weather.js
│   │   ├── maps.js
│   │   └── export.js
│   └── assets/
│       └── weather-icons/
├── tests/
│   ├── test_weather_service.py
│   ├── test_validators.py
│   └── test_database.py
├── requirements.txt
└── README.md
```

## Development

1. The application uses SQLite for data persistence
2. All dates are stored in ISO format
3. Temperature is stored in Celsius
4. The frontend communicates with the backend via RESTful APIs
5. Error handling is implemented across all layers
6. Rate limiting is enabled on all endpoints

## Testing

Run the test suite:
```bash
python -m pytest tests/
```

## Error Handling

The application implements comprehensive error handling:
- Input validation
- API error handling
- Database error handling
- Rate limiting
- Fallback mechanisms for API failures

## Contributing

1. Fork the repository
2. Create your feature branch: `git checkout -b feature/YourFeature`
3. Commit your changes: `git commit -m 'Add YourFeature'`
4. Push to the branch: `git push origin feature/YourFeature`
5. Submit a pull request

## License

This project is part of the PM Accelerator program assessment.

## Author

[Your Name]