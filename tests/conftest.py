"""
Pytest configuration and shared fixtures for REGON MCP Server tests.

This module provides common test fixtures, utilities, and configuration
for all test modules in the project.
"""

import asyncio
import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Optional
from unittest.mock import AsyncMock, MagicMock

import pytest
from dotenv import load_dotenv

# Configure UTF-8 encoding for proper Unicode handling
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add the project root to Python path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Load environment variables for testing
load_dotenv()

# Mock RegonAPI module since it might not be available in test environment
class MockRegonAPI:
    """Mock RegonAPI for testing purposes."""
    
    def __init__(self, *args, **kwargs):
        self.session = MagicMock()
        self.is_authenticated = False
        
    async def authenticate(self):
        """Mock authentication."""
        self.is_authenticated = True
        return True
        
    async def search_by_nip(self, nip):
        """Mock NIP search."""
        return {
            "nip": nip,
            "name": "Test Company",
            "regon": "123456789",
            "status": "AKTYWNY"
        }
        
    async def search_by_regon(self, regon):
        """Mock REGON search."""
        return {
            "regon": regon,
            "name": "Test Company",
            "nip": "1234567890",
            "status": "AKTYWNY"
        }
        
    async def search_by_krs(self, krs):
        """Mock KRS search."""
        return {
            "krs": krs,
            "name": "Test Company",
            "regon": "123456789",
            "nip": "1234567890",
            "status": "AKTYWNY"
        }
        
    async def get_full_report(self, regon):
        """Mock full report."""
        return {
            "regon": regon,
            "name": "Test Company Full Report",
            "address": "Test Address 123",
            "postal_code": "00-000",
            "city": "Test City"
        }

# Add the mock to sys.modules so imports work
sys.modules['RegonAPI'] = type('MockModule', (), {'RegonAPI': MockRegonAPI})()

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older Python versions
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root directory path."""
    return project_root


@pytest.fixture(scope="session")
def test_api_key():
    """Return the test API key for REGON API."""
    return os.getenv('TEST_API_KEY', 'abcde12345abcde12345')


@pytest.fixture(scope="session")
def production_api_key():
    """Return the production API key if available."""
    return os.getenv('API_KEY')


@pytest.fixture
def mock_regon_api():
    """Mock RegonAPI for testing without actual API calls."""
    mock_api = MagicMock()
    
    # Mock successful search response
    mock_api.search_by_nip.return_value = [{
        'Regon': '123456789',
        'Nip': '1234567890',
        'StatusNip': '',
        'Nazwa': 'Test Company Sp. z o.o.',
        'Wojewodztwo': 'MAZOWIECKIE',
        'Powiat': 'warszawski',
        'Gmina': 'Warszawa',
        'Miejscowosc': 'Warszawa',
        'KodPocztowy': '00-001',
        'Ulica': 'ul. Testowa',
        'NrNieruchomosci': '1',
        'NrLokalu': '1',
        'Typ': 'P',
        'SilosID': '6',
        'DataZakonczeniaDzialalnosci': '',
        'MiejscowoscPoczty': 'Warszawa'
    }]
    
    # Mock empty search response
    mock_api.search_by_regon.return_value = []
    
    # Mock service status
    mock_api.get_service_status.return_value = 1
    
    # Mock data status
    mock_api.get_data_status.return_value = "2025-08-21"
    
    return mock_api


@pytest.fixture
def sample_mcp_request():
    """Return a sample MCP request for testing."""
    return {
        "jsonrpc": "2.0",
        "id": "test-id-123",
        "method": "tools/call",
        "params": {
            "name": "regon_search_by_nip",
            "arguments": {
                "nip": "1234567890"
            }
        }
    }


@pytest.fixture
def sample_mcp_response():
    """Return a sample MCP response for testing."""
    return {
        "jsonrpc": "2.0",
        "id": "test-id-123",
        "result": {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps([{
                        'Regon': '123456789',
                        'Nip': '1234567890',
                        'Nazwa': 'Test Company Sp. z o.o.'
                    }], ensure_ascii=False, indent=2)
                }
            ]
        }
    }


@pytest.fixture
def tools_config():
    """Return the default tools configuration."""
    return {
        "regon_search_by_nip": {
            "name": "regon_search_by_nip",
            "description": "Search for business entity by NIP (Tax Identification Number)",
            "inputSchema": {
                "type": "object",
                "properties": {
                    "nip": {
                        "type": "string",
                        "description": "10-digit NIP number"
                    }
                },
                "required": ["nip"]
            }
        }
    }


@pytest.fixture
async def mock_stdio_transport():
    """Create a mock stdio transport for testing."""
    class MockTransport:
        def __init__(self):
            self.written_data = []
            self.closed = False
        
        def write(self, data):
            self.written_data.append(data)
        
        def close(self):
            self.closed = True
    
    return MockTransport()


@pytest.fixture
def temp_config_file(tmp_path):
    """Create a temporary configuration file for testing."""
    config_data = {
        "regon_search_by_nip": {
            "name": "regon_search_by_nip",
            "description": "Test tool description"
        }
    }
    
    config_file = tmp_path / "test_config.json"
    config_file.write_text(json.dumps(config_data, indent=2))
    return str(config_file)


@pytest.fixture
def env_vars(monkeypatch):
    """Fixture to set environment variables for testing."""
    def _set_env_vars(**kwargs):
        for key, value in kwargs.items():
            monkeypatch.setenv(key, value)
    return _set_env_vars


class AsyncContextManagerMock:
    """Mock async context manager for testing."""
    
    def __init__(self, return_value=None):
        self.return_value = return_value
    
    async def __aenter__(self):
        return self.return_value
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass


@pytest.fixture
def async_context_mock():
    """Create an async context manager mock."""
    return AsyncContextManagerMock


# Test data fixtures
@pytest.fixture
def valid_nip():
    """Return a valid NIP number for testing."""
    return "1234567890"


@pytest.fixture
def valid_regon9():
    """Return a valid 9-digit REGON number for testing."""
    return "123456789"


@pytest.fixture
def valid_regon14():
    """Return a valid 14-digit REGON number for testing."""
    return "12345678901234"


@pytest.fixture
def valid_krs():
    """Return a valid KRS number for testing."""
    return "0000123456"


@pytest.fixture
def invalid_nip():
    """Return an invalid NIP number for testing."""
    return "invalid_nip"


# Pytest markers for test categorization
pytest_plugins = []


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "unit: Unit tests that don't require external dependencies"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests that may require external services"
    )
    config.addinivalue_line(
        "markers", "http: Tests for HTTP server functionality"
    )
    config.addinivalue_line(
        "markers", "stdio: Tests for stdio MCP server functionality"
    )
    config.addinivalue_line(
        "markers", "slow: Tests that take longer to run"
    )
    config.addinivalue_line(
        "markers", "network: Tests that require network access"
    )
    config.addinivalue_line(
        "markers", "api: Tests that require REGON API access"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on test names and paths."""
    for item in items:
        # Add markers based on test file names
        if "test_http" in item.fspath.basename:
            item.add_marker(pytest.mark.http)
        elif "test_stdio" in item.fspath.basename:
            item.add_marker(pytest.mark.stdio)
        elif "test_mcp" in item.fspath.basename:
            item.add_marker(pytest.mark.stdio)
        
        # Add markers based on test function names
        if "integration" in item.name:
            item.add_marker(pytest.mark.integration)
        elif "api" in item.name:
            item.add_marker(pytest.mark.api)
            item.add_marker(pytest.mark.network)
        elif "slow" in item.name:
            item.add_marker(pytest.mark.slow)
        else:
            item.add_marker(pytest.mark.unit)


# Event loop configuration for async tests
@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()
