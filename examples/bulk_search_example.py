#!/usr/bin/env python3
"""
Bulk Search Example for RegonAPI MCP Server

This example demonstrates how to perform bulk searches for multiple entities
using the MCP server's bulk search capabilities.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List

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
                "name": "regon-bulk-example-client",
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
    Demonstrate bulk search capabilities of the RegonAPI MCP Server.
    
    This example shows how to search for multiple entities at once,
    which is more efficient than individual searches.
    """
    
    print("RegonAPI MCP Server - Bulk Search Example")
    print("=" * 45)
    print("Demonstrating bulk search capabilities")
    print("=" * 45)
    
    # Sample data for bulk searches
    sample_nips = [
        "7342867148",  # CD Projekt
        "5260255203",  # PKO Bank Polski
        "5213018952",  # Bank Pekao
        "7831686635"   # mBank
    ]
    
    sample_regons9 = [
        "492707333",   # CD Projekt
        "017206916",   # PKO Bank Polski  
        "017179322",   # Bank Pekao
        "017187973"    # mBank
    ]
    
    sample_krs = [
        "0000006865",  # CD Projekt
        "0000026438",  # PKO Bank Polski
        "0000026317",  # Bank Pekao
        "0000025237"   # mBank
    ]
    
    client = MCPClient()
    
    try:
        # Start the server
        await client.start_server()
        
        # Initialize the session
        await client.initialize()
        
        print("\n🔍 Bulk Search by Multiple NIPs")
        print("=" * 35)
        print(f"Searching for NIPs: {', '.join(sample_nips)}")
        
        result = await client.call_tool("regon_search_multiple_nips", {
            "nips": sample_nips
        })
        print(result)
        
        print("\n🔍 Bulk Search by Multiple 9-digit REGONs")
        print("=" * 45)
        print(f"Searching for REGONs: {', '.join(sample_regons9)}")
        
        result = await client.call_tool("regon_search_multiple_regons9", {
            "regons9": sample_regons9
        })
        print(result)
        
        print("\n🔍 Bulk Search by Multiple KRS Numbers")
        print("=" * 40)
        print(f"Searching for KRS: {', '.join(sample_krs)}")
        
        result = await client.call_tool("regon_search_multiple_krs", {
            "krss": sample_krs
        })
        print(result)
        
        print("\n🔍 Mixed Individual Searches for Comparison")
        print("=" * 45)
        print("Performing individual searches for the same entities...")
        
        for i, nip in enumerate(sample_nips[:2]):  # Just first 2 for brevity
            print(f"\n📄 Individual search for NIP: {nip}")
            result = await client.call_tool("regon_search_by_nip", {"nip": nip})
            print(result)
        
        print("\n💡 Performance Comparison")
        print("=" * 25)
        print("✅ Bulk searches are more efficient when searching multiple entities")
        print("✅ Single API call vs multiple calls")
        print("✅ Reduced server load and faster response times")
        print("✅ Better for batch processing scenarios")
        
        print("\n🔍 Testing with Invalid Data")
        print("=" * 30)
        print("Testing bulk search with some invalid NIPs...")
        
        mixed_nips = [
            "7342867148",  # Valid CD Projekt NIP
            "1234567890",  # Invalid NIP
            "5260255203",  # Valid PKO Bank NIP
            "9999999999"   # Invalid NIP
        ]
        
        result = await client.call_tool("regon_search_multiple_nips", {
            "nips": mixed_nips
        })
        print(result)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Clean up
        await client.stop_server()
    
    print(f"\n✅ Bulk search example completed!")
    print("\n" + "=" * 50)
    print("💡 Key takeaways:")
    print("   * Use bulk search tools for multiple entities")
    print("   * More efficient than individual searches")
    print("   * Handles mixed valid/invalid data gracefully")


if __name__ == "__main__":
    print("Starting RegonAPI MCP Server Bulk Search Example...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        sys.exit(1)
