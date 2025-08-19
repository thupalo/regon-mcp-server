#!/usr/bin/env python3
"""
HTTP MCP Server Test Script (Virtual Environment Compatible)
Tests the HTTP wrapper of the REGON MCP server.
"""

import requests
import json
import time
import sys

def test_http_server():
    """Test HTTP MCP server endpoints."""
    base_url = "http://localhost:8001"
    
    print("🚀 Testing HTTP MCP Server...")
    print(f"📡 Base URL: {base_url}")
    print()
    
    # Test 1: Server info
    try:
        print("✅ Test 1: Server Information")
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Server: {data.get('name', 'Unknown')}")
            print(f"   Version: {data.get('version', 'Unknown')}")
            print(f"   Mode: {data.get('mode', 'Unknown')}")
            print("   ✅ PASSED")
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: Connection error - {e}")
        print("\n💡 Make sure HTTP server is running:")
        print("   .\\venv\\Scripts\\python.exe regon_mcp_server\\server_http.py --port 8001")
        return False
    
    print()
    
    # Test 2: Health check
    try:
        print("✅ Test 2: Health Check")
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status', 'Unknown')}")
            print(f"   Service: {data.get('regon_service', 'Unknown')}")
            print("   ✅ PASSED")
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: {e}")
    
    print()
    
    # Test 3: List tools
    try:
        print("✅ Test 3: List MCP Tools")
        response = requests.get(f"{base_url}/tools", timeout=5)
        if response.status_code == 200:
            data = response.json()
            tools = data.get('tools', [])
            print(f"   Found {len(tools)} tools:")
            for tool in tools[:3]:  # Show first 3
                print(f"     - {tool.get('name', 'Unknown')}")
            if len(tools) > 3:
                print(f"     ... and {len(tools) - 3} more")
            print("   ✅ PASSED")
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: {e}")
    
    print()
    
    # Test 4: Search by NIP (convenience endpoint)
    try:
        print("✅ Test 4: Search by NIP (convenience endpoint)")
        test_nip = "7342867148"  # Known test NIP
        response = requests.get(f"{base_url}/search/nip/{test_nip}", timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success') and data.get('result'):
                company = data['result'][0]
                print(f"   Company: {company.get('Nazwa', 'Unknown')}")
                print(f"   NIP: {company.get('Nip', 'Unknown')}")
                print(f"   REGON: {company.get('Regon', 'Unknown')}")
                print("   ✅ PASSED")
            else:
                print(f"   ⚠️  No results found for NIP {test_nip}")
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
            print(f"   Response: {response.text[:200]}...")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: {e}")
    
    print()
    
    # Test 5: Call tool directly
    try:
        print("✅ Test 5: Call MCP Tool Directly")
        tool_request = {
            "name": "regon_search_by_nip",
            "arguments": {"nip": "7342867148"}
        }
        response = requests.post(f"{base_url}/tools/call", 
                               json=tool_request, 
                               timeout=10)
        if response.status_code == 200:
            data = response.json()
            if data.get('success'):
                result_text = data.get('result', [''])[0]
                if 'Nazwa' in result_text:
                    print("   Tool call successful - company data received")
                    print("   ✅ PASSED")
                else:
                    print("   ⚠️  Tool call completed but no company data")
            else:
                print(f"   ❌ FAILED: {data.get('error', 'Unknown error')}")
        else:
            print(f"   ❌ FAILED: HTTP {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ FAILED: {e}")
    
    print()
    print("🎉 HTTP MCP Server test completed!")
    print()
    print("📚 Available endpoints:")
    print("   GET  /              - Server information")
    print("   GET  /health        - Health check")
    print("   GET  /tools         - List MCP tools")
    print("   POST /tools/call    - Call MCP tool")
    print("   GET  /search/nip/{nip}     - Search by NIP")
    print("   GET  /search/krs/{krs}     - Search by KRS")
    print("   GET  /search/regon/{regon} - Search by REGON")
    print("   GET  /docs          - API documentation")
    
    return True

if __name__ == "__main__":
    test_http_server()
