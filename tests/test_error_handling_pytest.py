"""
Pytest unit tests for the error handling module.

This module contains comprehensive unit tests for the error handling
functionality, including retry mechanisms, input validation, and sanitization.
"""

import asyncio
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from regon_mcp_server.error_handling import (
    RetryMechanism,
    sanitize_string,
    validate_input,
    ServerError,
    ValidationError,
    APIError,
    NetworkError,
    ConfigurationError
)


class TestRetryMechanism:
    """Test suite for the RetryMechanism class."""
    
    @pytest.mark.unit
    def test_retry_mechanism_initialization(self):
        """Test RetryMechanism initialization with default parameters."""
        retry = RetryMechanism()
        
        assert retry.max_retries == 3
        assert retry.delay == 1.0
        assert retry.backoff_factor == 2.0
    
    @pytest.mark.unit
    def test_retry_mechanism_custom_parameters(self):
        """Test RetryMechanism initialization with custom parameters."""
        retry = RetryMechanism(max_retries=5, delay=2.0, backoff_factor=1.5)
        
        assert retry.max_retries == 5
        assert retry.delay == 2.0
        assert retry.backoff_factor == 1.5
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_successful_operation_no_retry(self):
        """Test that successful operations don't trigger retries."""
        retry = RetryMechanism(max_retries=3, delay=0.1)
        
        async def successful_operation():
            return "success"
        
        result = await retry.async_retry(successful_operation)
        assert result == "success"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retry_mechanism_with_failures(self):
        """Test retry mechanism with temporary failures."""
        retry = RetryMechanism(max_retries=3, delay=0.1)
        
        call_count = 0
        
        async def failing_operation():
            nonlocal call_count
            call_count += 1
            if call_count < 3:
                raise Exception("Temporary failure")
            return "success"
        
        result = await retry.async_retry(failing_operation)
        assert result == "success"
        assert call_count == 3
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retry_mechanism_exhausted(self):
        """Test retry mechanism when all retries are exhausted."""
        retry = RetryMechanism(max_retries=2, delay=0.1)
        
        async def always_failing_operation():
            raise Exception("Persistent failure")
        
        with pytest.raises(Exception, match="Persistent failure"):
            await retry.async_retry(always_failing_operation)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retry_mechanism_backoff(self):
        """Test that retry delays follow backoff factor."""
        retry = RetryMechanism(max_retries=3, delay=0.1, backoff_factor=2.0)
        
        delays = []
        
        with patch('asyncio.sleep') as mock_sleep:
            mock_sleep.side_effect = lambda delay: delays.append(delay)
            
            async def failing_operation():
                raise Exception("Always fails")
            
            with pytest.raises(Exception):
                await retry.async_retry(failing_operation)
            
            # Check that delays follow backoff pattern
            expected_delays = [0.1, 0.2, 0.4]
            assert delays == expected_delays
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retry_mechanism_with_specific_exceptions(self):
        """Test retry mechanism with specific exception types."""
        retry = RetryMechanism(max_retries=2, delay=0.1)
        
        # Should retry on network-related exceptions
        async def network_error_operation():
            raise ConnectionError("Network error")
        
        with pytest.raises(ConnectionError):
            await retry.async_retry(network_error_operation)
        
        # Should not retry on validation errors (immediate failure)
        async def validation_error_operation():
            raise ValidationError("Invalid input")
        
        with pytest.raises(ValidationError):
            await retry.async_retry(validation_error_operation)


class TestInputValidation:
    """Test suite for input validation functions."""
    
    @pytest.mark.unit
    def test_validate_input_valid_nip(self, valid_nip):
        """Test validation of valid NIP numbers."""
        result = validate_input(valid_nip, 'nip')
        assert result == valid_nip
    
    @pytest.mark.unit
    def test_validate_input_invalid_nip(self, invalid_nip):
        """Test validation of invalid NIP numbers."""
        with pytest.raises(ValidationError):
            validate_input(invalid_nip, 'nip')
    
    @pytest.mark.unit
    def test_validate_input_valid_regon9(self, valid_regon9):
        """Test validation of valid 9-digit REGON numbers."""
        result = validate_input(valid_regon9, 'regon9')
        assert result == valid_regon9
    
    @pytest.mark.unit
    def test_validate_input_valid_regon14(self, valid_regon14):
        """Test validation of valid 14-digit REGON numbers."""
        result = validate_input(valid_regon14, 'regon14')
        assert result == valid_regon14
    
    @pytest.mark.unit
    def test_validate_input_valid_krs(self, valid_krs):
        """Test validation of valid KRS numbers."""
        result = validate_input(valid_krs, 'krs')
        assert result == valid_krs
    
    @pytest.mark.unit
    def test_validate_input_empty_string(self):
        """Test validation of empty strings."""
        with pytest.raises(ValidationError):
            validate_input("", 'nip')
    
    @pytest.mark.unit
    def test_validate_input_none_value(self):
        """Test validation of None values."""
        with pytest.raises(ValidationError):
            validate_input(None, 'nip')
    
    @pytest.mark.unit
    def test_validate_input_wrong_length(self):
        """Test validation of inputs with wrong length."""
        with pytest.raises(ValidationError):
            validate_input("123", 'nip')  # Too short
        
        with pytest.raises(ValidationError):
            validate_input("12345678901", 'nip')  # Too long
    
    @pytest.mark.unit
    def test_validate_input_non_numeric(self):
        """Test validation of non-numeric inputs."""
        with pytest.raises(ValidationError):
            validate_input("12345678ab", 'nip')


class TestStringSanitization:
    """Test suite for string sanitization functions."""
    
    @pytest.mark.unit
    def test_sanitize_string_basic(self):
        """Test basic string sanitization."""
        result = sanitize_string("Test String")
        assert result == "Test String"
    
    @pytest.mark.unit
    def test_sanitize_string_polish_characters(self):
        """Test sanitization of Polish characters."""
        polish_text = "Spółka z ograniczoną odpowiedzialnością"
        result = sanitize_string(polish_text)
        assert result == polish_text
    
    @pytest.mark.unit
    def test_sanitize_string_special_characters(self):
        """Test sanitization of special characters."""
        text_with_special = "Test & Company <script>alert('test')</script>"
        result = sanitize_string(text_with_special)
        # Should remove or escape dangerous content
        assert "<script>" not in result
        assert "alert" not in result
    
    @pytest.mark.unit
    def test_sanitize_string_whitespace(self):
        """Test sanitization of whitespace."""
        text_with_whitespace = "  Test   String  "
        result = sanitize_string(text_with_whitespace)
        assert result == "Test String"
    
    @pytest.mark.unit
    def test_sanitize_string_empty(self):
        """Test sanitization of empty strings."""
        result = sanitize_string("")
        assert result == ""
    
    @pytest.mark.unit
    def test_sanitize_string_none(self):
        """Test sanitization of None values."""
        result = sanitize_string(None)
        assert result == ""
    
    @pytest.mark.unit
    def test_sanitize_string_unicode(self):
        """Test sanitization of Unicode characters."""
        unicode_text = "Test 🏢 Company ąćęłńóśźż"
        result = sanitize_string(unicode_text)
        # Should preserve Unicode characters
        assert "🏢" in result
        assert "ąćęłńóśźż" in result


class TestCustomExceptions:
    """Test suite for custom exception classes."""
    
    @pytest.mark.unit
    def test_server_error_creation(self):
        """Test ServerError exception creation."""
        error = ServerError("Test error message")
        assert str(error) == "Test error message"
        assert isinstance(error, Exception)
    
    @pytest.mark.unit
    def test_validation_error_creation(self):
        """Test ValidationError exception creation."""
        error = ValidationError("Invalid input")
        assert str(error) == "Invalid input"
        assert isinstance(error, ServerError)
    
    @pytest.mark.unit
    def test_api_error_creation(self):
        """Test APIError exception creation."""
        error = APIError("API call failed")
        assert str(error) == "API call failed"
        assert isinstance(error, ServerError)
    
    @pytest.mark.unit
    def test_network_error_creation(self):
        """Test NetworkError exception creation."""
        error = NetworkError("Network operation failed")
        assert str(error) == "Network operation failed"
        assert isinstance(error, ServerError)
    
    @pytest.mark.unit
    def test_exception_hierarchy(self):
        """Test that all custom exceptions inherit from ServerError."""
        validation_error = ValidationError("test")
        api_error = APIError("test")
        network_error = NetworkError("test")
        
        assert isinstance(validation_error, ServerError)
        assert isinstance(api_error, ServerError)
        assert isinstance(network_error, ServerError)


class TestErrorHandlingIntegration:
    """Integration tests for error handling components."""
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retry_with_validation_error(self):
        """Test that validation errors are not retried."""
        retry = RetryMechanism(max_retries=3, delay=0.1)
        
        async def operation_with_validation_error():
            raise ValidationError("Invalid input format")
        
        # Should fail immediately without retries
        with pytest.raises(ValidationError):
            await retry.async_retry(operation_with_validation_error)
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_retry_with_api_error(self):
        """Test retry behavior with API errors."""
        retry = RetryMechanism(max_retries=2, delay=0.1)
        
        call_count = 0
        
        async def operation_with_api_error():
            nonlocal call_count
            call_count += 1
            raise APIError("API temporarily unavailable")
        
        # Should retry API errors
        with pytest.raises(APIError):
            await retry.async_retry(operation_with_api_error)
        
        assert call_count == 3  # Initial call + 2 retries
    
    @pytest.mark.unit
    def test_input_validation_with_sanitization(self):
        """Test input validation combined with sanitization."""
        # Test that sanitized input is validated
        dirty_nip = "  1234567890  "
        clean_nip = sanitize_string(dirty_nip)
        validated_nip = validate_input(clean_nip, 'nip')
        
        assert validated_nip == "1234567890"
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_comprehensive_error_handling_flow(self):
        """Test a comprehensive error handling flow."""
        retry = RetryMechanism(max_retries=2, delay=0.1)
        
        attempt_count = 0
        
        async def complex_operation(input_data):
            nonlocal attempt_count
            attempt_count += 1
            
            # Sanitize input
            clean_data = sanitize_string(input_data)
            
            # Validate input
            if not clean_data:
                raise ValidationError("Empty input after sanitization")
            
            # Simulate transient failure on first attempt
            if attempt_count == 1:
                raise APIError("Temporary API failure")
            
            return f"Processed: {clean_data}"
        
        # Test successful flow after retry
        result = await retry.async_retry(
            lambda: complex_operation("  Test Data  ")
        )
        
        assert result == "Processed: Test Data"
        assert attempt_count == 2
    
    @pytest.mark.unit
    @pytest.mark.asyncio
    async def test_error_handling_with_logging(self):
        """Test error handling with logging integration."""
        retry = RetryMechanism(max_retries=1, delay=0.1)
        
        with patch('regon_mcp_server.error_handling.logger') as mock_logger:
            async def failing_operation():
                raise ConnectionError("Network failure")
            
            with pytest.raises(ConnectionError):
                await retry.async_retry(failing_operation)
            
            # Verify that errors were logged
            assert mock_logger.warning.called or mock_logger.error.called
