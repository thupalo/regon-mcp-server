#!/usr/bin/env python3
"""
Error Handling and Recovery Module for REGON MCP Server

This module provides comprehensive error handling, recovery mechanisms,
and hardening utilities to make the server bullet-proof against exceptions.
"""

import logging
import traceback
import functools
import asyncio
import sys
import json
from typing import Any, Dict, List, Optional, Callable, Union
from mcp.types import TextContent

# Configure module logger
logger = logging.getLogger(__name__)

class ServerError(Exception):
    """Base exception for server errors."""
    def __init__(self, message: str, error_code: str = "UNKNOWN_ERROR", details: Optional[Dict] = None):
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

class ConfigurationError(ServerError):
    """Configuration-related errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "CONFIGURATION_ERROR", details)

class APIError(ServerError):
    """REGON API-related errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "API_ERROR", details)

class ValidationError(ServerError):
    """Input validation errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "VALIDATION_ERROR", details)

class NetworkError(ServerError):
    """Network-related errors."""
    def __init__(self, message: str, details: Optional[Dict] = None):
        super().__init__(message, "NETWORK_ERROR", details)

def safe_execute(func: Callable) -> Callable:
    """
    Decorator for safe function execution with comprehensive error handling.
    
    Args:
        func: Function to wrap with error handling
        
    Returns:
        Wrapped function with error handling
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Return safe default based on function name
            if func.__name__.startswith('get_') or func.__name__.startswith('load_'):
                return None
            elif func.__name__.startswith('list_') or func.__name__.startswith('find_'):
                return []
            elif func.__name__.startswith('is_') or func.__name__.startswith('has_'):
                return False
            else:
                raise ServerError(error_msg, "EXECUTION_ERROR", {"function": func.__name__, "original_error": str(e)})
                
    return wrapper

def safe_async_execute(func: Callable) -> Callable:
    """
    Decorator for safe async function execution with comprehensive error handling.
    
    Args:
        func: Async function to wrap with error handling
        
    Returns:
        Wrapped async function with error handling
    """
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except asyncio.CancelledError:
            logger.warning(f"Function {func.__name__} was cancelled")
            raise
        except Exception as e:
            error_msg = f"Error in {func.__name__}: {str(e)}"
            logger.error(error_msg, exc_info=True)
            
            # Return safe default for async functions
            if func.__name__.startswith('handle_'):
                return [TextContent(type="text", text=f"❌ Error: {error_msg}")]
            elif func.__name__.startswith('get_') or func.__name__.startswith('load_'):
                return None
            elif func.__name__.startswith('list_') or func.__name__.startswith('find_'):
                return []
            else:
                raise ServerError(error_msg, "ASYNC_EXECUTION_ERROR", {"function": func.__name__, "original_error": str(e)})
                
    return wrapper

def safe_json_parse(data: str, default: Any = None) -> Any:
    """
    Safely parse JSON data with error handling.
    
    Args:
        data: JSON string to parse
        default: Default value if parsing fails
        
    Returns:
        Parsed JSON data or default value
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError) as e:
        logger.warning(f"JSON parsing failed: {e}")
        return default

def safe_dict_get(dictionary: Dict, key: str, default: Any = None) -> Any:
    """
    Safely get value from dictionary with nested key support.
    
    Args:
        dictionary: Dictionary to search
        key: Key to look for (supports dot notation for nested keys)
        default: Default value if key not found
        
    Returns:
        Value from dictionary or default
    """
    try:
        if '.' in key:
            keys = key.split('.')
            value = dictionary
            for k in keys:
                value = value[k]
            return value
        else:
            return dictionary.get(key, default)
    except (KeyError, TypeError, AttributeError):
        return default

def validate_input(data: Dict, required_fields: List[str], field_types: Optional[Dict[str, type]] = None) -> Dict[str, Any]:
    """
    Validate input data with type checking.
    
    Args:
        data: Input data to validate
        required_fields: List of required field names
        field_types: Optional type validation for fields
        
    Returns:
        Validated data
        
    Raises:
        ValidationError: If validation fails
    """
    if not isinstance(data, dict):
        raise ValidationError("Input must be a dictionary")
    
    # Check required fields
    missing_fields = [field for field in required_fields if field not in data]
    if missing_fields:
        raise ValidationError(f"Missing required fields: {missing_fields}")
    
    # Type validation
    if field_types:
        for field, expected_type in field_types.items():
            if field in data and not isinstance(data[field], expected_type):
                raise ValidationError(f"Field '{field}' must be of type {expected_type.__name__}")
    
    return data

def sanitize_string(value: str, max_length: int = 1000) -> str:
    """
    Sanitize string input to prevent injection attacks and limit length.
    
    Args:
        value: String to sanitize
        max_length: Maximum allowed length
        
    Returns:
        Sanitized string
    """
    if not isinstance(value, str):
        value = str(value)
    
    # Remove potentially dangerous characters
    sanitized = value.replace('\x00', '').replace('\r', '').replace('\n', ' ')
    
    # Limit length
    if len(sanitized) > max_length:
        sanitized = sanitized[:max_length] + "..."
        logger.warning(f"String truncated to {max_length} characters")
    
    return sanitized

def create_error_response(error: Exception, context: str = "") -> List[TextContent]:
    """
    Create a standardized error response for MCP tools.
    
    Args:
        error: Exception that occurred
        context: Additional context about the error
        
    Returns:
        List of TextContent with error information
    """
    if isinstance(error, ServerError):
        error_msg = f"❌ {error.error_code}: {error.message}"
        if error.details:
            error_msg += f"\nDetails: {json.dumps(error.details, indent=2)}"
    else:
        error_msg = f"❌ Unexpected error: {str(error)}"
    
    if context:
        error_msg = f"{context}\n{error_msg}"
    
    logger.error(f"Error response created: {error_msg}")
    return [TextContent(type="text", text=error_msg)]

def setup_error_handling():
    """
    Set up global error handling and logging configuration.
    """
    # Configure root logger to catch all errors
    root_logger = logging.getLogger()
    
    # Add handler for uncaught exceptions
    def handle_exception(exc_type, exc_value, exc_traceback):
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
        
        logger.critical("Uncaught exception", exc_info=(exc_type, exc_value, exc_traceback))
    
    sys.excepthook = handle_exception
    
    # Handle asyncio exceptions
    def handle_async_exception(loop, context):
        exception = context.get('exception')
        if exception:
            logger.critical(f"Async exception: {exception}", exc_info=exception)
        else:
            logger.critical(f"Async error: {context}")
    
    # Set the exception handler for the current event loop
    try:
        loop = asyncio.get_running_loop()
        loop.set_exception_handler(handle_async_exception)
    except RuntimeError:
        # No running loop, set for future loops
        pass

class RetryMechanism:
    """
    Retry mechanism for functions that might fail temporarily.
    """
    
    def __init__(self, max_retries: int = 3, delay: float = 1.0, backoff_factor: float = 2.0):
        self.max_retries = max_retries
        self.delay = delay
        self.backoff_factor = backoff_factor
    
    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < self.max_retries:
                        wait_time = self.delay * (self.backoff_factor ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait_time}s...")
                        import time
                        time.sleep(wait_time)
                    else:
                        logger.error(f"All {self.max_retries + 1} attempts failed for {func.__name__}")
                        break
            
            raise last_exception
        
        return wrapper
    
    def async_retry(self, func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(self.max_retries + 1):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    
                    if attempt < self.max_retries:
                        wait_time = self.delay * (self.backoff_factor ** attempt)
                        logger.warning(f"Attempt {attempt + 1} failed for {func.__name__}: {e}. Retrying in {wait_time}s...")
                        await asyncio.sleep(wait_time)
                    else:
                        logger.error(f"All {self.max_retries + 1} attempts failed for {func.__name__}")
                        break
            
            raise last_exception
        
        return wrapper

# Pre-configured retry decorators
retry_on_failure = RetryMechanism(max_retries=2, delay=0.5)
retry_on_network_failure = RetryMechanism(max_retries=3, delay=1.0, backoff_factor=1.5)

class HealthChecker:
    """
    Health checking utility for server components.
    """
    
    def __init__(self):
        self.checks = {}
    
    def register_check(self, name: str, check_func: Callable) -> None:
        """Register a health check function."""
        self.checks[name] = check_func
    
    def run_checks(self) -> Dict[str, Any]:
        """Run all registered health checks."""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                result = check_func()
                results[name] = {"status": "healthy", "result": result}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
                logger.warning(f"Health check '{name}' failed: {e}")
        
        return results
    
    async def run_async_checks(self) -> Dict[str, Any]:
        """Run all registered health checks asynchronously."""
        results = {}
        
        for name, check_func in self.checks.items():
            try:
                if asyncio.iscoroutinefunction(check_func):
                    result = await check_func()
                else:
                    result = check_func()
                results[name] = {"status": "healthy", "result": result}
            except Exception as e:
                results[name] = {"status": "unhealthy", "error": str(e)}
                logger.warning(f"Health check '{name}' failed: {e}")
        
        return results

# Global health checker instance
health_checker = HealthChecker()

def format_error_for_user(error: Exception) -> str:
    """
    Format error message for end users (remove technical details).
    
    Args:
        error: Exception to format
        
    Returns:
        User-friendly error message
    """
    if isinstance(error, ServerError):
        return f"❌ {error.message}"
    elif "RegonAPI" in str(error) or "API" in str(error):
        return "❌ Problem connecting to REGON database. Please try again later."
    elif "network" in str(error).lower() or "connection" in str(error).lower():
        return "❌ Network connection problem. Please check your internet connection."
    elif "timeout" in str(error).lower():
        return "❌ Request timed out. Please try again."
    else:
        return "❌ An unexpected error occurred. Please contact support if this persists."
