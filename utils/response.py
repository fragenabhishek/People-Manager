"""
API response formatting module
Standardizes API responses across the application
"""
from typing import Any, Dict, Optional, Tuple
from flask import jsonify
from datetime import datetime


class APIResponse:
    """Standardized API response builder"""
    
    @staticmethod
    def success(
        data: Any = None,
        message: Optional[str] = None,
        status_code: int = 200
    ) -> Tuple[Dict, int]:
        """
        Create a successful API response
        
        Args:
            data: Response data
            message: Optional success message
            status_code: HTTP status code
            
        Returns:
            Tuple of (response dict, status code)
        """
        response = {
            'success': True,
            'timestamp': datetime.now().isoformat()
        }
        
        if data is not None:
            response['data'] = data
        
        if message:
            response['message'] = message
        
        return jsonify(response), status_code
    
    @staticmethod
    def error(
        message: str,
        status_code: int = 400,
        error_code: Optional[str] = None,
        details: Optional[Dict] = None
    ) -> Tuple[Dict, int]:
        """
        Create an error API response
        
        Args:
            message: Error message
            status_code: HTTP status code
            error_code: Optional error code for client handling
            details: Optional additional error details
            
        Returns:
            Tuple of (response dict, status code)
        """
        response = {
            'success': False,
            'error': message,
            'timestamp': datetime.now().isoformat()
        }
        
        if error_code:
            response['error_code'] = error_code
        
        if details:
            response['details'] = details
        
        return jsonify(response), status_code
    
    @staticmethod
    def created(data: Any, message: str = "Resource created successfully") -> Tuple[Dict, int]:
        """Create a 201 Created response"""
        return APIResponse.success(data, message, 201)
    
    @staticmethod
    def not_found(message: str = "Resource not found") -> Tuple[Dict, int]:
        """Create a 404 Not Found response"""
        return APIResponse.error(message, 404, "NOT_FOUND")
    
    @staticmethod
    def unauthorized(message: str = "Unauthorized") -> Tuple[Dict, int]:
        """Create a 401 Unauthorized response"""
        return APIResponse.error(message, 401, "UNAUTHORIZED")
    
    @staticmethod
    def forbidden(message: str = "Forbidden") -> Tuple[Dict, int]:
        """Create a 403 Forbidden response"""
        return APIResponse.error(message, 403, "FORBIDDEN")
    
    @staticmethod
    def validation_error(message: str) -> Tuple[Dict, int]:
        """Create a 400 validation error response"""
        return APIResponse.error(message, 400, "VALIDATION_ERROR")
    
    @staticmethod
    def server_error(message: str = "Internal server error") -> Tuple[Dict, int]:
        """Create a 500 server error response"""
        return APIResponse.error(message, 500, "SERVER_ERROR")


# Convenience functions
def success_response(data: Any = None, message: Optional[str] = None, status_code: int = 200):
    """Shorthand for success response"""
    return APIResponse.success(data, message, status_code)


def error_response(message: str, status_code: int = 400, error_code: Optional[str] = None):
    """Shorthand for error response"""
    return APIResponse.error(message, status_code, error_code)

