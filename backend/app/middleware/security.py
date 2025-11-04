"""
Security middleware for input validation and sanitization
"""

import json
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response
from typing import Callable

from app.utils.validation import InputValidator


class SecurityMiddleware(BaseHTTPMiddleware):
    """
    Middleware to validate and sanitize all incoming requests
    """
    
    def __init__(self, app, skip_paths: list = None):
        super().__init__(app)
        self.skip_paths = skip_paths or ['/docs', '/redoc', '/openapi.json', '/static', '/webhook']
        
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        # Skip validation for certain paths
        if any(request.url.path.startswith(path) for path in self.skip_paths):
            return await call_next(request)
        
        try:
            # Validate query parameters
            if request.query_params:
                for key, value in request.query_params.items():
                    InputValidator.sanitize_string(key, 100)
                    InputValidator.sanitize_string(value, 1000)
                    InputValidator.validate_sql_input(value)
            
            # Validate JSON body for POST/PUT requests
            if request.method in ["POST", "PUT", "PATCH"]:
                await self._validate_request_body(request)
            
            # Continue processing
            response = await call_next(request)
            
            # Add security headers
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            response.headers["X-XSS-Protection"] = "1; mode=block"
            
            return response
            
        except ValueError as e:
            raise HTTPException(status_code=400, detail=f"Invalid input: {str(e)}")
        except Exception as e:
            # Log the error in production
            import traceback
            print(f"Security middleware caught exception: {str(e)}")
            print(f"Traceback: {traceback.format_exc()}")
            raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
    
    async def _validate_request_body(self, request: Request):
        """
        Validate request body content
        """
        try:
            # Read body
            body = await request.body()
            if not body:
                return
            
            # Check content type
            content_type = request.headers.get("content-type", "")
            
            if "application/json" in content_type:
                try:
                    json_data = json.loads(body)
                    # Validate JSON data
                    if isinstance(json_data, dict):
                        InputValidator.sanitize_dict(json_data)
                    elif isinstance(json_data, str):
                        InputValidator.sanitize_string(json_data)
                except json.JSONDecodeError:
                    raise ValueError("Invalid JSON format")
                    
            elif "multipart/form-data" in content_type or "application/x-www-form-urlencoded" in content_type:
                # For form data, validation is handled by FastAPI/Pydantic models
                pass
            
        except Exception as e:
            raise ValueError(f"Request body validation failed: {str(e)}")