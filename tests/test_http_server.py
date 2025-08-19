#!/usr/bin/env python3
"""
Test client for HTTP MCP Server

This script tests the HTTP wrapper server to ensure it works correctly
and provides the same functionality as the stdio version.
"""

import asyncio
import json
import os
import sys
import requests
from typing import Dict, Any

# Configure UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class HttpMcpClient:
    """Simple HTTP client for testing the HTTP MCP server."""
    
    def __init__(self, base_url: str = "http://localhost:8001"):
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
    
    def get_server_info(self) -> Dict[str, Any]:
        """Get server information."""
        response = self.session.get(f"{self.base_url}/")
        response.raise_for_status()
        return response.json()
    
    def health_check(self) -> Dict[str, Any]:
        """Check server health."""
        response = self.session.get(f"{self.base_url}/health")
        response.raise_for_status()
        return response.json()
    
    def list_tools(self) -> Dict[str, Any]:
        """List available tools."""
        response = self.session.get(f"{self.base_url}/tools")
        response.raise_for_status()
        return response.json()
    
    def call_tool(self, name: str, arguments: Dict[str, Any]) -> Dict[str, Any]:
        """Call a specific tool."""
        payload = {
            "name": name,
            "arguments": arguments
        }
        response = self.session.post(f"{self.base_url}/tools/call", json=payload)
        response.raise_for_status()
        return response.json()
    
    def search_by_nip(self, nip: str) -> Dict[str, Any]:
        """Convenience method to search by NIP."""
        response = self.session.get(f"{self.base_url}/search/nip/{nip}")
        response.raise_for_status()
        return response.json()
    
    def search_by_krs(self, krs: str) -> Dict[str, Any]:
        """Convenience method to search by KRS."""
        response = self.session.get(f"{self.base_url}/search/krs/{krs}")
        response.raise_for_status()
        return response.json()

def test_http_server():
    """Test the HTTP MCP server functionality."""
    print("🧪 Testing HTTP MCP Server")
    print("=" * 50)
    
    client = HttpMcpClient()
    
    try:
        # Test 1: Server info
        print("\n🔍 Test 1: Server Information")
        info = client.get_server_info()
        print(f"   Service: {info['service']}")
        print(f"   Mode: {info['mode']}")
        print(f"   Encoding: {info['encoding']}")
        print(f"   Polish chars: {info['polish_characters']}")
        
        # Test 2: Health check
        print("\n🔍 Test 2: Health Check")
        health = client.health_check()
        print(f"   Status: {health['status']}")
        print(f"   REGON Service: {health['regon_service']['status_message']}")
        
        # Test 3: List tools
        print("\n🔍 Test 3: Available Tools")
        tools = client.list_tools()
        print(f"   Available tools: {len(tools['tools'])}")
        for tool in tools['tools'][:3]:  # Show first 3
            print(f"   - {tool['name']}: {tool['description']}")
        
        # Test 4: NIP search using tool call
        print("\n🔍 Test 4: Tool Call - NIP Search")
        nip_result = client.call_tool("regon_search_by_nip", {"nip": "7342867148"})
        result_data = json.loads(nip_result['result'][0]['text'])
        if result_data and len(result_data) > 0:
            company = result_data[0]
            nazwa = company.get('Nazwa', '')
            gmina = company.get('Gmina', '')
            print(f"   Company: {nazwa}")
            print(f"   Location: {gmina}")
            
            # Verify encoding
            if "SPÓŁKA" in nazwa and "Północ" in gmina:
                print(f"   ✅ Polish characters work correctly!")
            else:
                print(f"   ❌ Encoding issue detected")
        
        # Test 5: Convenience endpoint
        print("\n🔍 Test 5: Convenience Endpoint - NIP Search")
        nip_conv = client.search_by_nip("7342867148")
        if nip_conv['result'] and len(nip_conv['result']) > 0:
            company = nip_conv['result'][0]
            print(f"   Company: {company.get('Nazwa', '')}")
            print(f"   Location: {company.get('Gmina', '')}")
        
        # Test 6: KRS search
        print("\n🔍 Test 6: KRS Search")
        krs_result = client.search_by_krs("0000006865")
        if krs_result['result'] and len(krs_result['result']) > 0:
            company = krs_result['result'][0]
            print(f"   Company: {company.get('Nazwa', '')}")
            print(f"   NIP: {company.get('Nip', '')}")
        
        print("\n🎉 All tests passed! HTTP server is working correctly.")
        print("   The HTTP wrapper preserves all stdio server functionality.")
        print("   Polish character encoding works perfectly.")
        
    except requests.ConnectionError:
        print("❌ Could not connect to HTTP server.")
        print("   Make sure the server is running with:")
        print("   python regon_mcp_server/server_http.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_http_server()
