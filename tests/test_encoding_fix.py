#!/usr/bin/env python3
"""
Test client for verifying the updated main server works with proper UTF-8 encoding
"""

import asyncio
import json
import os
import sys

# Configure UTF-8 encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class EncodingTestClient:
    """Test client for encoding verification."""
    
    def __init__(self):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.server_script = os.path.join(current_dir, "regon_mcp_server", "server.py")
        self.process = None
        self.id_counter = 0
    
    async def start_server(self):
        """Start the main MCP server."""
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("[STARTED] Main MCP Server")
    
    async def stop_server(self):
        """Stop the server."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("[STOPPED] Main MCP Server")
    
    async def send_request(self, method: str, params: dict = None):
        """Send a JSON-RPC request."""
        self.id_counter += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.id_counter,
            "method": method
        }
        if params:
            request["params"] = params
        
        message = json.dumps(request) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
        # Read response
        response_line = await self.process.stdout.readline()
        if response_line:
            try:
                return json.loads(response_line.decode())
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {e}")
                return None
        return None
    
    async def initialize(self):
        """Initialize the MCP session."""
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "encoding-test-client", "version": "1.0.0"}
        })
        
        # Send initialized notification
        initialized_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        message = json.dumps(initialized_msg) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
        print("[OK] MCP session initialized")
        return response
    
    async def call_tool(self, name: str, arguments: dict):
        """Call a tool."""
        return await self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })

async def test_encoding():
    """Test the encoding in the updated server."""
    print("Testing Main Server Polish Character Encoding")
    print("=" * 50)
    
    client = EncodingTestClient()
    
    try:
        await client.start_server()
        await client.initialize()
        
        # Test NIP search
        print("\n[TEST] Searching by NIP: 7342867148")
        
        response = await client.call_tool("regon_search_by_nip", {"nip": "7342867148"})
        
        if response and "result" in response:
            result = response["result"]
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    result_text = content[0].get("text", "")
                    
                    try:
                        data = json.loads(result_text)
                        if data and len(data) > 0:
                            company = data[0]
                            nazwa = company.get('Nazwa', '')
                            gmina = company.get('Gmina', '')
                            
                            print(f"\nResults:")
                            print(f"  Company: {nazwa}")
                            print(f"  Location: {gmina}")
                            
                            # Verify encoding
                            expected_nazwa = "CD PROJEKT SPÓŁKA AKCYJNA"
                            expected_gmina = "Praga-Północ"
                            
                            nazwa_ok = nazwa == expected_nazwa
                            gmina_ok = gmina == expected_gmina
                            
                            print(f"\nEncoding Check:")
                            print(f"  ✅ Nazwa: {'PASS' if nazwa_ok else 'FAIL'}")
                            print(f"  ✅ Gmina: {'PASS' if gmina_ok else 'FAIL'}")
                            
                            if nazwa_ok and gmina_ok:
                                print(f"\n🎉 SUCCESS! Polish encoding works perfectly!")
                                print(f"   The fix_polish_encoding() function was indeed obsolete.")
                                print(f"   PYTHONIOENCODING + UTF-8 configuration is the correct solution.")
                            else:
                                print(f"\n❌ Encoding issue detected")
                        else:
                            print("No data returned")
                    except json.JSONDecodeError as e:
                        print(f"JSON parse error: {e}")
                else:
                    print("No content found")
            else:
                print("Unexpected response format")
        else:
            print("No response received")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.stop_server()
    
    print("\n" + "=" * 50)
    print("Encoding test completed!")

if __name__ == "__main__":
    asyncio.run(test_encoding())
