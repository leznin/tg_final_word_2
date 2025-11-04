"""
Input validation and sanitization utilities
"""

import re
import html
from typing import Any, Dict, Optional


class InputValidator:
    """Utility class for validating and sanitizing user input"""
    
    # Common SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|EXECUTE)\b)",
        r"(--|;|\/\*|\*\/)",
        r"(\b(UNION|OR|AND)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)",
        r"(\b(OR|AND)\b.*=.*)",
        r"('|\").*('|\")",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"on\w+\s*=",
        r"<iframe[^>]*>.*?</iframe>",
        r"<object[^>]*>.*?</object>",
        r"<embed[^>]*>.*?</embed>",
    ]

    @classmethod
    def sanitize_string(cls, value: str, max_length: int = 1000) -> str:
        """
        Sanitize string input to prevent XSS and injection attacks
        """
        if not isinstance(value, str):
            return str(value)
        
        # Limit length
        value = value[:max_length]
        
        # HTML escape
        value = html.escape(value)
        
        # Remove null bytes
        value = value.replace('\x00', '')
        
        # Check for XSS patterns
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potential XSS attack detected")
        
        return value.strip()

    @classmethod
    def validate_sql_input(cls, value: str) -> str:
        """
        Validate input for SQL injection attempts
        """
        if not isinstance(value, str):
            return str(value)
        
        # Check for SQL injection patterns
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value, re.IGNORECASE):
                raise ValueError("Potential SQL injection detected")
        
        return value

    @classmethod
    def validate_email(cls, email: str) -> str:
        """
        Validate email format
        """
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise ValueError("Invalid email format")
        return email.lower().strip()

    @classmethod
    def validate_integer(cls, value: Any, min_val: int = 0, max_val: int = 999999999) -> int:
        """
        Validate integer input
        """
        try:
            int_val = int(value)
            if int_val < min_val or int_val > max_val:
                raise ValueError(f"Integer must be between {min_val} and {max_val}")
            return int_val
        except (ValueError, TypeError):
            raise ValueError("Invalid integer format")

    @classmethod
    def sanitize_dict(cls, data: Dict[str, Any], max_string_length: int = 1000) -> Dict[str, Any]:
        """
        Recursively sanitize dictionary data
        """
        if not isinstance(data, dict):
            return data
        
        sanitized = {}
        for key, value in data.items():
            # Sanitize key
            safe_key = cls.sanitize_string(str(key), 100)
            
            # Sanitize value based on type
            if isinstance(value, str):
                sanitized[safe_key] = cls.sanitize_string(value, max_string_length)
            elif isinstance(value, dict):
                sanitized[safe_key] = cls.sanitize_dict(value, max_string_length)
            elif isinstance(value, list):
                sanitized[safe_key] = [
                    cls.sanitize_string(str(item), max_string_length) if isinstance(item, str) else item
                    for item in value[:100]  # Limit list size
                ]
            else:
                sanitized[safe_key] = value
        
        return sanitized