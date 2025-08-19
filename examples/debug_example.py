#!/usr/bin/env python3
"""
Debug version of the MCP client to investigate the parameter mapping issue.
"""

import asyncio
import json
import sys
from typing import Dict, Any


class DebugMCPClient:
    """Debug MCP client with detailed logging."""
    
    def __init__(self, server_script="regon_mcp_server/server.py"):
        self.server_script = server_script
        self.process = None
        self.id_counter = 0
    
    async def start_server(self):
        """Start the MCP server process."""
        print("[DEBUG] Starting MCP server process...")
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("[DEBUG] MCP Server process started")
    
    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            print("[DEBUG] Stopping MCP server...")
            self.process.terminate()
            await self.process.wait()
            print("[DEBUG] MCP Server stopped")
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server with debug output."""
        self.id_counter += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.id_counter,
            "method": method,
            "params": params or {}
        }
        
        print(f"[DEBUG] Sending request:")
        print(f"  Method: {method}")
        print(f"  Params: {json.dumps(params, indent=2) if params else '{}'}")
        print(f"  Full request: {json.dumps(request, indent=2)}")
        
        message = json.dumps(request) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
        # Read response
        line = await self.process.stdout.readline()
        if line:
            response = json.loads(line.decode().strip())
            print(f"[DEBUG] Received response:")
            print(f"  {json.dumps(response, indent=2)}")
            return response
        else:
            stderr = await self.process.stderr.read()
            stderr_text = stderr.decode() if stderr else "No stderr output"
            print(f"[DEBUG] No response received. Stderr: {stderr_text}")
            raise Exception(f"No response received. Stderr: {stderr_text}")
    
    async def initialize(self):
        """Initialize the MCP session."""
        print("[DEBUG] Initializing MCP session...")
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "regon-debug-client",
                "version": "1.0.0"
            }
        })
        
        # Send initialized notification (required after initialize)
        print("[DEBUG] Sending initialized notification...")
        initialized_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        message = json.dumps(initialized_msg) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
        print("[DEBUG] MCP session initialized")
        return response
    
    async def list_tools(self):
        """List available tools."""
        print("[DEBUG] Listing available tools...")
        response = await self.send_request("tools/list")
        return response
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a tool and return the text content."""
        print(f"[DEBUG] Calling tool: {tool_name}")
        print(f"[DEBUG] Arguments: {json.dumps(arguments, indent=2) if arguments else '{}'}")
        
        response = await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })
        
        if "result" in response and response["result"]:
            result = response["result"]
            # Handle the new MCP response format
            if "content" in result and result["content"]:
                return result["content"][0]["text"]
            else:
                return "No content in result"
        elif "error" in response:
            return f"Error: {response['error']}"
        else:
            return "No result returned"


async def test_direct_regon_api():
    """Test direct RegonAPI calls for comparison."""
    print("\n" + "="*60)
    print("TESTING DIRECT RegonAPI CALLS (for comparison)")
    print("="*60)
    
    try:
        from RegonAPI import RegonAPI
        import os
        from dotenv import load_dotenv
        
        load_dotenv()
        api_key = os.getenv("TEST_API_KEY") or os.getenv("API_KEY") or "abcde12345abcde12345"
        
        print(f"[DIRECT] Using API key: {api_key[:10]}...")
        
        # Initialize RegonAPI directly
        api = RegonAPI(
            bir_version="bir1.1",
            is_production=False,
            timeout=30,
            operation_timeout=30
        )
        
        print("[DIRECT] Authenticating...")
        api.authenticate(key=api_key)
        print("[DIRECT] Authentication successful")
        
        # Test service status
        print("[DIRECT] Getting service status...")
        status = api.get_service_status()
        print(f"[DIRECT] Service status: {status}")
        
        # Test data status
        print("[DIRECT] Getting data status...")
        data_status = api.get_data_status()
        print(f"[DIRECT] Data status: {data_status}")
        
        # Test search by NIP
        test_nip = "7342867148"
        print(f"[DIRECT] Searching by NIP: {test_nip}")
        results = api.searchData(nip=test_nip)
        print(f"[DIRECT] Search results: {len(results) if results else 0} entries found")
        if results:
            print(f"[DIRECT] First result keys: {list(results[0].keys())}")
        
    except Exception as e:
        print(f"[DIRECT] Error: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """Main debug function."""
    print("RegonAPI MCP Server - Debug Example")
    print("="*50)
    
    # First test direct API calls
    await test_direct_regon_api()
    
    print("\n" + "="*60)
    print("TESTING MCP SERVER COMMUNICATION")
    print("="*60)
    
    client = DebugMCPClient()
    
    try:
        # Start the server
        await client.start_server()
        
        # Initialize the session
        await client.initialize()
        
        # List available tools
        tools_response = await client.list_tools()
        print(f"\n[DEBUG] Available tools: {len(tools_response.get('result', {}).get('tools', []))} tools")
        
        # Test a simple tool call
        print("\n[DEBUG] Testing service status tool...")
        status = await client.call_tool("regon_get_service_status")
        print(f"[DEBUG] Service status result: {status}")
        
        # Test tool with parameters
        print("\n[DEBUG] Testing NIP search tool...")
        nip_result = await client.call_tool("regon_search_by_nip", {"nip": "7342867148"})
        print(f"[DEBUG] NIP search result: {nip_result}")
        
    except Exception as e:
        print(f"\n[DEBUG] Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Clean up
        await client.stop_server()
    
    print(f"\n[DEBUG] Debug session completed!")


if __name__ == "__main__":
    print("Starting RegonAPI MCP Server Debug Session...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[DEBUG] Debug session interrupted by user")
    except Exception as e:
        print(f"\n[DEBUG] Debug session failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
