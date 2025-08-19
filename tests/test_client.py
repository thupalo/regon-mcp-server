#!/usr/bin/env python3
"""
Simple MCP client example for testing the RegonAPI MCP Server
"""

import asyncio
import json
import sys
import subprocess
from typing import Dict, Any

async def test_mcp_server():
    """Test the MCP server by sending sample requests."""
    
    server_script = "regon_mcp_server.py"
    
    print("Starting MCP server test...")
    print("=" * 50)
    
    # Start the server process
    try:
        process = await asyncio.create_subprocess_exec(
            sys.executable, server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        print("Server started successfully")
        
        # Send initialization request
        init_request = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialization request...")
        await send_request(process, init_request)
        response = await read_response(process)
        print(f"Initialization response: {response}")
        
        # List available tools
        tools_request = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\nRequesting tools list...")
        await send_request(process, tools_request)
        response = await read_response(process)
        if "result" in response and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"Found {len(tools)} tools:")
            for tool in tools:
                print(f"  - {tool['name']}: {tool['description']}")
        
        # Test search by NIP
        search_request = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "regon_search_by_nip",
                "arguments": {
                    "nip": "7342867148"  # CD Projekt NIP
                }
            }
        }
        
        print("\nTesting search by NIP...")
        await send_request(process, search_request)
        response = await read_response(process)
        if "result" in response:
            content = response["result"][0]["text"]
            print(f"Search result:\n{content}")
        else:
            print(f"Search failed: {response}")
        
        # Test service status
        status_request = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call", 
            "params": {
                "name": "regon_get_service_status",
                "arguments": {}
            }
        }
        
        print("\nTesting service status...")
        await send_request(process, status_request)
        response = await read_response(process)
        if "result" in response:
            content = response["result"][0]["text"]
            print(f"Service status:\n{content}")
        
        # Terminate the server
        process.terminate()
        await process.wait()
        print("\nServer terminated successfully")
        
    except Exception as e:
        print(f"Error: {e}")
        if 'process' in locals():
            process.terminate()

async def send_request(process: asyncio.subprocess.Process, request: Dict[str, Any]):
    """Send a JSON-RPC request to the server."""
    message = json.dumps(request) + "\n"
    process.stdin.write(message.encode())
    await process.stdin.drain()

async def read_response(process: asyncio.subprocess.Process) -> Dict[str, Any]:
    """Read a JSON-RPC response from the server."""
    line = await process.stdout.readline()
    if line:
        return json.loads(line.decode().strip())
    else:
        stderr = await process.stderr.read()
        raise Exception(f"No response received. Stderr: {stderr.decode()}")

if __name__ == "__main__":
    print("RegonAPI MCP Server Client Test")
    print("=" * 40)
    
    try:
        asyncio.run(test_mcp_server())
        print("\n✅ MCP server test completed!")
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)
