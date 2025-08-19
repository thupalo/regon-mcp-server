#!/usr/bin/env python3
"""
Error Handling and Monitoring Example for RegonAPI MCP Server

This example demonstrates error handling, service monitoring,
and debugging capabilities of the MCP server.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class MCPClient:
    """Simple MCP client for testing the RegonAPI server."""
    
    def __init__(self, server_script="../regon_mcp_server/server.py"):
        self.server_script = server_script
        self.process = None
        self.id_counter = 0
    
    async def start_server(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("🚀 MCP Server started")
    
    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("⏹️  MCP Server stopped")
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        self.id_counter += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.id_counter,
            "method": method,
            "params": params or {}
        }
        
        message = json.dumps(request) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
        # Read response
        line = await self.process.stdout.readline()
        if line:
            return json.loads(line.decode().strip())
        else:
            stderr = await self.process.stderr.read()
            raise Exception(f"No response received. Stderr: {stderr.decode()}")
    
    async def initialize(self):
        """Initialize the MCP session."""
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "regon-monitoring-example-client",
                "version": "1.0.0"
            }
        })
        
        # Send initialized notification (required after initialize)
        initialized_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        message = json.dumps(initialized_msg) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
        print("✅ Initialized MCP session")
        return response
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a tool and return the text content."""
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


async def main():
    """
    Demonstrate error handling and monitoring capabilities of the RegonAPI MCP Server.
    
    This example shows how to monitor service status, handle errors,
    and debug issues with the MCP server.
    """
    
    print("RegonAPI MCP Server - Error Handling & Monitoring Example")
    print("=" * 65)
    print("Demonstrating service monitoring and error handling")
    print("=" * 65)
    
    client = MCPClient()
    
    try:
        # Start the server
        await client.start_server()
        
        # Initialize the session
        await client.initialize()
        
        print("\n🔍 Service Health Check")
        print("=" * 25)
        
        # Check service status
        print("📊 Checking service status...")
        status = await client.call_tool("regon_get_service_status")
        print(f"Service Status: {status}")
        
        # Check data status
        print("\n📊 Checking data status...")
        data_status = await client.call_tool("regon_get_data_status")
        print(f"Data Status: {data_status}")
        
        # Get available operations
        print("\n📊 Getting available operations...")
        operations = await client.call_tool("regon_get_available_operations")
        print(f"Available Operations: {operations}")
        
        print("\n🔍 Error Handling Tests")
        print("=" * 25)
        
        # Test 1: Invalid NIP format
        print("\n❌ Test 1: Invalid NIP format")
        print("-" * 30)
        invalid_nip = "123abc"
        result = await client.call_tool("regon_search_by_nip", {"nip": invalid_nip})
        print(f"Result: {result}")
        
        # Check if this generated an error code
        error_info = await client.call_tool("regon_get_last_error_code")
        print(f"Last Error Code: {error_info}")
        
        # Test 2: Invalid REGON format
        print("\n❌ Test 2: Invalid REGON format")
        print("-" * 32)
        invalid_regon = "123"
        result = await client.call_tool("regon_search_by_regon", {"regon": invalid_regon})
        print(f"Result: {result}")
        
        # Check error code again
        error_info = await client.call_tool("regon_get_last_error_code")
        print(f"Last Error Code: {error_info}")
        
        # Test 3: Invalid KRS format
        print("\n❌ Test 3: Invalid KRS format")
        print("-" * 30)
        invalid_krs = "abc123"
        result = await client.call_tool("regon_search_by_krs", {"krs": invalid_krs})
        print(f"Result: {result}")
        
        # Test 4: Invalid report name
        print("\n❌ Test 4: Invalid report name")
        print("-" * 31)
        result = await client.call_tool("regon_get_full_report", {
            "regon": "492707333",
            "report_name": "NonExistentReport",
            "strict": True
        })
        print(f"Result: {result}")
        
        # Test 5: Empty bulk search
        print("\n❌ Test 5: Empty bulk search")
        print("-" * 30)
        result = await client.call_tool("regon_search_multiple_nips", {"nips": []})
        print(f"Result: {result}")
        
        # Test 6: Non-existent entity
        print("\n❌ Test 6: Non-existent entity")
        print("-" * 32)
        fake_nip = "9999999999"
        result = await client.call_tool("regon_search_by_nip", {"nip": fake_nip})
        print(f"Result: {result}")
        
        print("\n🔍 Valid Operations After Errors")
        print("=" * 35)
        
        # Show that the service still works after errors
        print("✅ Testing valid operation after errors...")
        valid_nip = "7342867148"  # CD Projekt
        result = await client.call_tool("regon_search_by_nip", {"nip": valid_nip})
        print(f"Valid search result: {result}")
        
        print("\n🔍 Service Monitoring Best Practices")
        print("=" * 40)
        
        print("💡 Recommended monitoring workflow:")
        print("   1. Check service status before operations")
        
        # Demonstrate monitoring workflow
        status = await client.call_tool("regon_get_service_status")
        if "Available" in status or "1" in status:
            print("   ✅ Service is available")
            
            print("   2. Check data freshness")
            data_status = await client.call_tool("regon_get_data_status")
            print(f"   📊 Data last updated: {data_status}")
            
            print("   3. Perform operations")
            print("   ✅ Safe to perform RegonAPI operations")
            
            print("   4. Check for errors after operations")
            error_info = await client.call_tool("regon_get_last_error_code")
            print(f"   🔍 Error check: {error_info}")
        else:
            print("   ❌ Service is not available")
            print("   ⏸️  Should retry later or alert administrators")
        
        print("\n🔍 Error Code Reference")
        print("=" * 25)
        print("Common RegonAPI error codes:")
        print("   * 0: No errors")
        print("   * 1: CAPTCHA required")
        print("   * 2: Too many identifiers")
        print("   * 4: Entity not found")
        print("   * 5: Insufficient privileges")
        print("   * 7: Session expired")
        
        print("\n🔍 Production Monitoring Tips")
        print("=" * 32)
        print("For production environments:")
        print("   * Monitor service status regularly")
        print("   * Implement retry logic for network errors")
        print("   * Log error codes for debugging")
        print("   * Check data freshness for critical applications")
        print("   * Implement rate limiting to avoid API limits")
        print("   * Use bulk operations when possible")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        
        # Even in case of client errors, we can try to get server status
        try:
            error_info = await client.call_tool("regon_get_last_error_code")
            print(f"Server error info: {error_info}")
        except:
            print("Could not retrieve server error information")
    
    finally:
        # Clean up
        await client.stop_server()
    
    print(f"\n✅ Error handling and monitoring example completed!")
    print("\n" + "=" * 50)
    print("💡 Key takeaways:")
    print("   * Always check service status before operations")
    print("   * Handle errors gracefully in your applications")
    print("   * Use error codes for debugging and monitoring")
    print("   * Implement proper retry logic for production use")


if __name__ == "__main__":
    print("Starting RegonAPI MCP Server Error Handling Example...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        sys.exit(1)
