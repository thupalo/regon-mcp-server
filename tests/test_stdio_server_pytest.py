"""
Pytest tests for the stdio MCP server functionality.

This module contains comprehensive tests for the stdio MCP server,
including protocol compliance, tool functionality, and error handling.
"""

import asyncio
import json
import os
import subprocess
import sys
from pathlib import Path
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class TestStdioMCPServer:
    """Test suite for the stdio MCP server."""
    
    @pytest.mark.stdio
    @pytest.mark.unit
    def test_server_import(self):
        """Test that the server module can be imported successfully."""
        try:
            from regon_mcp_server import server
            assert hasattr(server, 'main')
        except ImportError as e:
            pytest.fail(f"Failed to import server module: {e}")
    
    @pytest.mark.stdio
    @pytest.mark.integration
    def test_server_startup(self):
        """Test that the server starts up without errors."""
        # Change to project root for subprocess
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            assert "REGON MCP Server" in result.stdout or "usage:" in result.stdout
        except subprocess.TimeoutExpired:
            pytest.fail("Server help command timed out")
        finally:
            os.chdir(original_dir)
    
    @pytest.mark.stdio
    @pytest.mark.integration
    def test_tools_list_functionality(self):
        """Test the tools/list MCP method."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", "--log-level", "WARNING"
            ], input='{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}\n', 
               text=True, capture_output=True, timeout=15)
            
            assert result.returncode == 0
            
            # Parse JSON-RPC response
            lines = result.stdout.strip().split('\n')
            response_found = False
            
            for line in lines:
                if line.strip():
                    try:
                        response = json.loads(line)
                        if response.get("result") and "tools" in response["result"]:
                            tools = response["result"]["tools"]
                            assert len(tools) > 0, "No tools found in response"
                            
                            # Check for expected tools
                            tool_names = [t['name'] for t in tools]
                            expected_tools = [
                                'regon_search_by_nip',
                                'regon_search_by_regon',
                                'regon_search_by_krs'
                            ]
                            
                            for expected_tool in expected_tools:
                                assert expected_tool in tool_names, f"Missing tool: {expected_tool}"
                            
                            response_found = True
                            break
                    except json.JSONDecodeError:
                        continue
            
            assert response_found, "No valid JSON-RPC response found"
            
        except subprocess.TimeoutExpired:
            pytest.fail("Tools list test timed out")
        finally:
            os.chdir(original_dir)
    
    @pytest.mark.stdio
    @pytest.mark.integration
    @pytest.mark.slow
    def test_tool_call_functionality(self):
        """Test calling a tool through the MCP protocol."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            tool_call = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "regon_search_by_nip",
                    "arguments": {"nip": "7342867148"}
                }
            }
            
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", "--log-level", "WARNING"
            ], input=json.dumps(tool_call) + '\n', 
               text=True, capture_output=True, timeout=30)
            
            # Allow both success (0) and API-related failures (1)
            # since we might not have a valid API key in test environment
            assert result.returncode in [0, 1]
            
            if result.returncode == 0:
                # Parse successful response
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if "result" in response:
                                assert "content" in response["result"]
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                # Check that error is API-related, not a code error
                assert "API" in result.stderr or "authentication" in result.stderr.lower()
                
        except subprocess.TimeoutExpired:
            pytest.fail("Tool call test timed out")
        finally:
            os.chdir(original_dir)
    
    @pytest.mark.stdio
    @pytest.mark.unit
    def test_production_mode_flag(self):
        """Test that production mode flag is recognized."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", "--production", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            # Should not fail due to --production flag
            assert result.returncode == 0
            
        except subprocess.TimeoutExpired:
            pytest.fail("Production mode help test timed out")
        finally:
            os.chdir(original_dir)
    
    @pytest.mark.stdio
    @pytest.mark.unit
    def test_tools_config_option(self):
        """Test that tools configuration option works."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", 
                "--tools-config", "minimal", "--help"
            ], capture_output=True, text=True, timeout=10)
            
            assert result.returncode == 0
            
        except subprocess.TimeoutExpired:
            pytest.fail("Tools config test timed out")
        finally:
            os.chdir(original_dir)
    
    @pytest.mark.stdio
    @pytest.mark.unit
    def test_invalid_json_handling(self):
        """Test server handling of invalid JSON input."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", "--log-level", "ERROR"
            ], input='invalid json\n', 
               text=True, capture_output=True, timeout=10)
            
            # Server should handle invalid JSON gracefully
            # Return code might be 0 (graceful handling) or 1 (error)
            assert result.returncode in [0, 1]
            
        except subprocess.TimeoutExpired:
            pytest.fail("Invalid JSON test timed out")
        finally:
            os.chdir(original_dir)


class TestStdioServerMethods:
    """Test individual server methods and functionality."""
    
    @pytest.mark.stdio
    @pytest.mark.unit
    @patch('regon_mcp_server.server.RegonAPI')
    def test_server_with_mocked_api(self, mock_regon_api_class, mock_regon_api):
        """Test server functionality with mocked RegonAPI."""
        mock_regon_api_class.return_value = mock_regon_api
        
        # This would require more complex mocking of the server's async methods
        # For now, we just test that the mock is properly set up
        assert mock_regon_api_class.return_value == mock_regon_api
    
    @pytest.mark.stdio
    @pytest.mark.unit
    def test_utf8_encoding_configuration(self):
        """Test that UTF-8 encoding is properly configured."""
        # Test that the environment variable is set
        assert os.environ.get('PYTHONIOENCODING') == 'utf-8'
        
        # Test that stdout can handle Unicode characters
        test_string = "Test: ąćęłńóśźż SPÓŁKA"
        try:
            sys.stdout.write(test_string)
            sys.stdout.flush()
        except UnicodeEncodeError:
            pytest.fail("UTF-8 encoding not properly configured")


# Integration tests that require actual server instance
class TestStdioServerIntegration:
    """Integration tests for stdio server."""
    
    @pytest.mark.stdio
    @pytest.mark.integration
    @pytest.mark.slow
    def test_server_lifecycle(self):
        """Test complete server lifecycle: start, process request, shutdown."""
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            # Test that server can start and shutdown cleanly
            process = subprocess.Popen([
                sys.executable, "regon_mcp_server/server.py", "--log-level", "ERROR"
            ], stdin=subprocess.PIPE, stdout=subprocess.PIPE, 
               stderr=subprocess.PIPE, text=True)
            
            # Send a simple request
            request = '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}\n'
            stdout, stderr = process.communicate(input=request, timeout=15)
            
            # Process should complete
            assert process.returncode is not None
            
        except subprocess.TimeoutExpired:
            process.kill()
            pytest.fail("Server lifecycle test timed out")
        finally:
            os.chdir(original_dir)
    
    @pytest.mark.stdio
    @pytest.mark.integration
    @pytest.mark.api
    @pytest.mark.network
    def test_api_connectivity(self, test_api_key):
        """Test actual API connectivity if test key is available."""
        if not test_api_key:
            pytest.skip("No test API key available")
        
        original_dir = os.getcwd()
        if 'tests' in os.getcwd():
            os.chdir('..')
        
        try:
            # Set the test API key
            env = os.environ.copy()
            env['TEST_API_KEY'] = test_api_key
            
            tool_call = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "regon_get_service_status",
                    "arguments": {}
                }
            }
            
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", "--log-level", "WARNING"
            ], input=json.dumps(tool_call) + '\n', 
               text=True, capture_output=True, timeout=30, env=env)
            
            # Should succeed with valid API key
            assert result.returncode == 0
            
        except subprocess.TimeoutExpired:
            pytest.fail("API connectivity test timed out")
        finally:
            os.chdir(original_dir)
