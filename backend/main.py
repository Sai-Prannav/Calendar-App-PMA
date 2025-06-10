from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from datetime import datetime
import os
from dotenv import load_dotenv
import json
import csv
import io

# Import local modules
from database import init_db, get_all_queries, insert_query, update_query, delete_query
from weather_service import WeatherService
from validators.location import LocationValidator
from validators.date_range import DateRangeValidator
from error_handlers.api_errors import register_error_handlers, ValidationError, NotFoundError, ExternalAPIError

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)
CORS(app)

# Setup rate limiting
limiter = Limiter(
    get_remote_address,
    app=app,
    default_limits=["200 per day", "50 per hour"]
)

# Register error handlers
register_error_handlers(app)

# Initialize services
weather_service = WeatherService()

# Initialize database
init_db()

@app.route('/api/weather/current', methods=['GET'])
@limiter.limit("30 per minute")
def get_current_weather():
    """Get current weather for a location"""
    location = request.args.get('location')
    if not location:
        raise ValidationError("Location parameter is required")

    # Validate location
    is_valid, message, location_type = LocationValidator.validate(location)
    if not is_valid:
        raise ValidationError(message)

    # Get weather data
    try:
        weather_data = weather_service.get_current_weather(location, location_type)
        return jsonify({
            'status': 'success',
            'data': weather_data
        })
    except Exception as e:
        raise ExternalAPIError(str(e), 'OpenWeather')

@app.route('/api/weather/forecast', methods=['GET'])
@limiter.limit("30 per minute")
def get_weather_forecast():
    """Get weather forecast for a location"""
    location = request.args.get('location')
    days = int(request.args.get('days', 5))
    
    if not location:
        raise ValidationError("Location parameter is required")
    if days not in range(1, 6):
        raise ValidationError("Days parameter must be between 1 and 5")

    # Validate location
    is_valid, message, location_type = LocationValidator.validate(location)
    if not is_valid:
        raise ValidationError(message)

    # Get forecast data
    try:
        forecast_data = weather_service.get_forecast(location, location_type, days)
        return jsonify({
            'status': 'success',
            'data': forecast_data
        })
    except Exception as e:
        raise ExternalAPIError(str(e), 'OpenWeather')

@app.route('/api/weather', methods=['GET'])
@limiter.limit("30 per minute")
def get_weather_queries():
    """Get all weather queries"""
    queries = get_all_queries()
    return jsonify({
        'status': 'success',
        'data': queries
    })

@app.route('/api/weather', methods=['POST'])
@limiter.limit("10 per minute")
def create_weather_query():
    """Create a new weather query"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['location', 'date_range_start', 'date_range_end']
    for field in required_fields:
        if field not in data:
            raise ValidationError(f"Missing required field: {field}")

    # Validate location
    is_valid, message, location_type = LocationValidator.validate(data['location'])
    if not is_valid:
        raise ValidationError(message)

    # Validate date range
    is_valid, message, date_range = DateRangeValidator.validate(
        data['date_range_start'],
        data['date_range_end']
    )
    if not is_valid:
        raise ValidationError(message)

    # Get weather data and insert query
    try:
        weather_data = weather_service.get_current_weather(data['location'], location_type)
        query_id = insert_query(
            data['location'],
            location_type,
            data['date_range_start'],
            data['date_range_end'],
            weather_data['temperature'],
            weather_data['description']
        )
        
        return jsonify({
            'status': 'success',
            'message': 'Weather query created successfully',
            'id': query_id
        }), 201
    
    except Exception as e:
        raise ExternalAPIError(str(e), 'OpenWeather')

@app.route('/api/weather/<int:query_id>', methods=['PUT'])
@limiter.limit("10 per minute")
def update_weather_query(query_id):
    """Update an existing weather query"""
    data = request.get_json()
    success = update_query(
        query_id,
        data.get('temperature'),
        data.get('weather_conditions')
    )

    if not success:
        raise NotFoundError('Weather query not found')

    return jsonify({
        'status': 'success',
        'message': 'Weather query updated successfully'
    })

@app.route('/api/weather/<int:query_id>', methods=['DELETE'])
@limiter.limit("10 per minute")
def delete_weather_query(query_id):
    """Delete a weather query"""
    success = delete_query(query_id)
    if not success:
        raise NotFoundError('Weather query not found')

    return jsonify({
        'status': 'success',
        'message': 'Weather query deleted successfully'
    })

@app.route('/api/weather/export', methods=['GET'])
@limiter.limit("10 per minute")
def export_weather_data():
    """Export weather data in various formats"""
    format_type = request.args.get('format', 'json')
    queries = get_all_queries()
    
    if format_type == 'json':
        return jsonify(queries)
        
    elif format_type == 'csv':
        output = io.StringIO()
        writer = csv.writer(output)
        
        # Write headers
        writer.writerow(['ID', 'Location', 'Type', 'Start Date', 'End Date', 
                        'Temperature', 'Conditions', 'Created At', 'Updated At'])
        
        # Write data
        for query in queries:
            writer.writerow(query)
            
        output.seek(0)
        return send_file(
            io.BytesIO(output.getvalue().encode('utf-8')),
            mimetype='text/csv',
            as_attachment=True,
            download_name='weather_data.csv'
        )
        
    else:
        raise ValidationError('Unsupported export format')

@app.route('/api/location/media', methods=['GET'])
@limiter.limit("10 per minute")
def get_location_media():
    """Get media (maps, videos) for a location"""
    location = request.args.get('location')
    if not location:
        raise ValidationError("Location parameter is required")

    # Validate location
    is_valid, message, location_type = LocationValidator.validate(location)
    if not is_valid:
        raise ValidationError(message)

    # Format location for display
    formatted_location = LocationValidator.format_for_display(location, location_type)
    
    return jsonify({
        'status': 'success',
        'data': {
            'location': formatted_location,
            'maps_url': f"https://www.google.com/maps/search/?api=1&query={location}",
            # Additional media endpoints would be integrated here
        }
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)