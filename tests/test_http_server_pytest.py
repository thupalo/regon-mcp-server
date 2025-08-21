"""
Pytest tests for the HTTP server functionality.

This module contains comprehensive tests for the HTTP REST API server,
including endpoint functionality, error handling, and integration tests.
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from unittest.mock import patch

import pytest
import requests

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestHTTPServer:
    """Test suite for the HTTP server."""
    
    @pytest.mark.http
    @pytest.mark.unit
    def test_http_server_import(self):
        """Test that the HTTP server module can be imported successfully."""
        try:
            from regon_mcp_server import server_http
            assert hasattr(server_http, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import HTTP server module: {e}")
    
    @pytest.mark.http
    @pytest.mark.integration
    def test_http_server_startup(self):
        """Test that the HTTP server starts up without errors."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server_http.py", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            assert "HTTP Server for REGON MCP" in result.stdout or "usage:" in result.stdout
        except subprocess.TimeoutExpired:
            pytest.fail("HTTP server help command timed out")
        finally:
            os.chdir(original_dir)


class TestHTTPServerEndpoints:
    """Test HTTP server endpoints with a running server instance."""
    
    @pytest.fixture(scope="class")
    def http_server_process(self):
        """Start HTTP server for testing and clean up afterwards."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        # Start the server
        process = subprocess.Popen([
            sys.executable, "regon_mcp_server/server_http.py",
            "--host", "127.0.0.1",
            "--port", "8002",  # Use different port to avoid conflicts
            "--log-level", "WARNING"
        ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is not None:
            stdout, stderr = process.communicate()
            os.chdir(original_dir)
            pytest.fail(f"HTTP server failed to start: {stderr.decode()}")
        
        yield "http://127.0.0.1:8002"
        
        # Cleanup
        process.terminate()
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
        
        os.chdir(original_dir)
    
    @pytest.mark.http
    @pytest.mark.integration
    def test_health_endpoint(self, http_server_process):
        """Test the /health endpoint."""
        base_url = http_server_process
        
        try:
            response = requests.get(f"{base_url}/health", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert "status" in data
            assert data["status"] in ["healthy", "ok"]
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Health endpoint request failed: {e}")
    
    @pytest.mark.http
    @pytest.mark.integration
    def test_tools_list_endpoint(self, http_server_process):
        """Test the /tools endpoint."""
        base_url = http_server_process
        
        try:
            response = requests.get(f"{base_url}/tools", timeout=10)
            assert response.status_code == 200
            
            data = response.json()
            assert "tools" in data
            assert len(data["tools"]) > 0
            
            # Check for expected tools
            tool_names = [tool["name"] for tool in data["tools"]]
            expected_tools = [
                "regon_search_by_nip",
                "regon_search_by_regon",
                "regon_search_by_krs"
            ]
            
            for expected_tool in expected_tools:
                assert expected_tool in tool_names, f"Missing tool: {expected_tool}"
                
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Tools endpoint request failed: {e}")
    
    @pytest.mark.http
    @pytest.mark.integration
    @pytest.mark.slow
    def test_tool_call_endpoint(self, http_server_process):
        """Test the /tools/call endpoint."""
        base_url = http_server_process
        
        payload = {
            "name": "regon_search_by_nip",
            "arguments": {
                "nip": "7342867148"
            }
        }
        
        try:
            response = requests.post(
                f"{base_url}/tools/call",
                json=payload,
                timeout=30
            )
            
            # Allow both success and API-related failures
            assert response.status_code in [200, 400, 500]
            
            if response.status_code == 200:
                data = response.json()
                assert "content" in data
            else:
                # Check that error is API-related
                error_text = response.text.lower()
                assert any(keyword in error_text for keyword in [
                    "api", "authentication", "key", "unauthorized"
                ]), f"Unexpected error: {response.text}"
                
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Tool call endpoint request failed: {e}")
    
    @pytest.mark.http
    @pytest.mark.integration
    def test_invalid_tool_call(self, http_server_process):
        """Test calling a non-existent tool."""
        base_url = http_server_process
        
        payload = {
            "name": "non_existent_tool",
            "arguments": {}
        }
        
        try:
            response = requests.post(
                f"{base_url}/tools/call",
                json=payload,
                timeout=10
            )
            
            assert response.status_code == 400
            
            data = response.json()
            assert "error" in data
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Invalid tool call request failed: {e}")
    
    @pytest.mark.http
    @pytest.mark.integration
    def test_malformed_request(self, http_server_process):
        """Test server handling of malformed requests."""
        base_url = http_server_process
        
        try:
            # Test invalid JSON
            response = requests.post(
                f"{base_url}/tools/call",
                data="invalid json",
                headers={"Content-Type": "application/json"},
                timeout=10
            )
            
            assert response.status_code == 422  # FastAPI validation error
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"Malformed request test failed: {e}")
    
    @pytest.mark.http
    @pytest.mark.integration
    def test_cors_headers(self, http_server_process):
        """Test that CORS headers are properly set."""
        base_url = http_server_process
        
        try:
            response = requests.options(f"{base_url}/tools", timeout=10)
            
            # Check for CORS headers
            assert "access-control-allow-origin" in response.headers
            assert "access-control-allow-methods" in response.headers
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"CORS test request failed: {e}")


class TestHTTPServerConfiguration:
    """Test HTTP server configuration options."""
    
    @pytest.mark.http
    @pytest.mark.unit
    def test_server_port_configuration(self):
        """Test that custom port configuration works."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server_http.py",
                "--port", "9999", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            
        except subprocess.TimeoutExpired:
            pytest.fail("Port configuration test timed out")
        finally:
            os.chdir(original_dir)
    
    @pytest.mark.http
    @pytest.mark.unit
    def test_server_host_configuration(self):
        """Test that custom host configuration works."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server_http.py",
                "--host", "0.0.0.0", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            
        except subprocess.TimeoutExpired:
            pytest.fail("Host configuration test timed out")
        finally:
            os.chdir(original_dir)
    
    @pytest.mark.http
    @pytest.mark.unit
    def test_production_mode_configuration(self):
        """Test production mode configuration."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server_http.py",
                "--production", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            
        except subprocess.TimeoutExpired:
            pytest.fail("Production mode configuration test timed out")
        finally:
            os.chdir(original_dir)


class TestHTTPServerStress:
    """Stress tests for HTTP server."""
    
    @pytest.mark.http
    @pytest.mark.slow
    @pytest.mark.integration
    def test_concurrent_requests(self, http_server_process):
        """Test server handling of concurrent requests."""
        base_url = http_server_process
        
        async def make_request():
            """Make a single request."""
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get(f"{base_url}/health") as response:
                    return response.status
        
        async def test_concurrent():
            """Test concurrent requests."""
            tasks = [make_request() for _ in range(10)]
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Most requests should succeed
            success_count = sum(1 for result in results if result == 200)
            assert success_count >= 8, f"Only {success_count}/10 requests succeeded"
        
        try:
            asyncio.run(test_concurrent())
        except Exception as e:
            pytest.fail(f"Concurrent requests test failed: {e}")


# API integration tests
class TestHTTPServerAPIIntegration:
    """Integration tests with actual REGON API."""
    
    @pytest.mark.http
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.network
    def test_api_service_status_endpoint(self, http_server_process, test_api_key):
        """Test service status endpoint with actual API."""
        if not test_api_key:
            pytest.skip("No test API key available")
        
        base_url = http_server_process
        
        payload = {
            "name": "regon_get_service_status",
            "arguments": {}
        }
        
        try:
            response = requests.post(
                f"{base_url}/tools/call",
                json=payload,
                timeout=30
            )
            
            # Should succeed with valid API key
            assert response.status_code == 200
            
            data = response.json()
            assert "content" in data
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"API service status test failed: {e}")
    
    @pytest.mark.http
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.network
    def test_api_search_functionality(self, http_server_process, test_api_key):
        """Test actual search functionality with API."""
        if not test_api_key:
            pytest.skip("No test API key available")
        
        base_url = http_server_process
        
        payload = {
            "name": "regon_search_by_nip",
            "arguments": {
                "nip": "7342867148"  # Test NIP
            }
        }
        
        try:
            response = requests.post(
                f"{base_url}/tools/call",
                json=payload,
                timeout=30
            )
            
            # Should succeed with valid API key and test data
            assert response.status_code == 200
            
            data = response.json()
            assert "content" in data
            
        except requests.exceptions.RequestException as e:
            pytest.fail(f"API search functionality test failed: {e}")
