from typing import Dict, Any, Optional
from flask import jsonify
from werkzeug.exceptions import HTTPException

class APIError(Exception):
    """Base exception class for API errors"""
    def __init__(self, message: str, status_code: int = 500, details: Optional[Dict[str, Any]] = None):
        super().__init__()
        self.message = message
        self.status_code = status_code
        self.details = details or {}

class ValidationError(APIError):
    """Exception for validation errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=400, details=details)

class NotFoundError(APIError):
    """Exception for resource not found errors"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, status_code=404, details=details)

class ExternalAPIError(APIError):
    """Exception for external API errors"""
    def __init__(self, message: str, service: str, details: Optional[Dict[str, Any]] = None):
        error_details = {'service': service}
        if details:
            error_details.update(details)
        super().__init__(message, status_code=502, details=error_details)

def handle_api_error(error: APIError):
    """Handler for API errors"""
    response = {
        'status': 'error',
        'message': error.message
    }
    if error.details:
        response['details'] = error.details
    return jsonify(response), error.status_code

def handle_http_error(error: HTTPException):
    """Handler for HTTP errors"""
    response = {
        'status': 'error',
        'message': error.description,
        'code': error.code
    }
    return jsonify(response), error.code

def handle_validation_error(error: ValidationError):
    """Handler for validation errors"""
    response = {
        'status': 'error',
        'message': 'Validation error',
        'errors': error.message
    }
    if error.details:
        response['details'] = error.details
    return jsonify(response), 400

def handle_generic_error(error: Exception):
    """Handler for unexpected errors"""
    response = {
        'status': 'error',
        'message': 'An unexpected error occurred',
        'type': error.__class__.__name__
    }
    return jsonify(response), 500

def register_error_handlers(app):
    """Register error handlers with Flask app"""
    app.register_error_handler(APIError, handle_api_error)
    app.register_error_handler(ValidationError, handle_validation_error)
    app.register_error_handler(HTTPException, handle_http_error)
    app.register_error_handler(Exception, handle_generic_error)

def format_error_response(message: str, status_code: int = 400, details: Optional[Dict[str, Any]] = None) -> Dict:
    """Format an error response"""
    response = {
        'status': 'error',
        'message': message,
        'code': status_code
    }
    if details:
        response['details'] = details
    return response