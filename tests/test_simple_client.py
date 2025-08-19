#!/usr/bin/env python3
"""
Test client for simplified server without encoding fixes
"""

import asyncio
import json
import os
import sys

# Set PYTHONIOENCODING environment variable
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

class SimpleTestClient:
    """Simple test client for the simplified MCP server."""
    
    def __init__(self, server_script="test_simple_server.py"):
        current_dir = os.path.dirname(os.path.abspath(__file__))
        self.server_script = os.path.join(current_dir, server_script)
        self.process = None
        self.id_counter = 0
    
    async def start_server(self):
        """Start the simplified MCP server."""
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("[STARTED] Simplified MCP Server started")
    
    async def stop_server(self):
        """Stop the server."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("[STOPPED] Simplified MCP Server stopped")
    
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
                print(f"Raw response: {response_line}")
                return None
        return None
    
    async def initialize(self):
        """Initialize the MCP session."""
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "simple-test-client", "version": "1.0.0"}
        })
        
        # Send initialized notification
        initialized_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        message = json.dumps(initialized_msg) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
        print("[OK] Initialized simplified MCP session")
        return response
    
    async def call_tool(self, name: str, arguments: dict):
        """Call a tool."""
        return await self.send_request("tools/call", {
            "name": name,
            "arguments": arguments
        })

async def test_simplified_server():
    """Test the simplified server without encoding fixes."""
    print("Testing Simplified RegonAPI MCP Server (NO encoding fixes)")
    print("=" * 60)
    
    client = SimpleTestClient()
    
    try:
        await client.start_server()
        await client.initialize()
        
        # Test NIP search
        print("\n[SEARCH] Testing NIP search: 7342867148")
        print("-" * 40)
        
        response = await client.call_tool("regon_search_by_nip", {"nip": "7342867148"})
        
        print(f"Full response: {response}")
        
        if response and "result" in response:
            result = response["result"]
            print(f"Result type: {type(result)}")
            print(f"Result content: {result}")
            
            if isinstance(result, dict) and "content" in result:
                content = result["content"]
                if isinstance(content, list) and len(content) > 0:
                    result_text = content[0].get("text", "")
                    print("Raw server response:")
                    print(result_text)
                    
                    # Parse the JSON to analyze the data
                    try:
                        data = json.loads(result_text)
                        if data and len(data) > 0:
                            company = data[0]
                            nazwa = company.get('Nazwa', '')
                            gmina = company.get('Gmina', '')
                            
                            print(f"\nExtracted data analysis:")
                            print(f"  Nazwa: '{nazwa}'")
                            print(f"  Gmina: '{gmina}'")
                            
                            # Check if characters are correct
                            expected_nazwa = "CD PROJEKT SPÓŁKA AKCYJNA"
                            expected_gmina = "Praga-Północ"
                            
                            print(f"\nEncoding verification:")
                            print(f"  Nazwa matches expected: {nazwa == expected_nazwa}")
                            print(f"  Gmina matches expected: {gmina == expected_gmina}")
                            
                            if nazwa == expected_nazwa and gmina == expected_gmina:
                                print("  ✅ ENCODING IS CORRECT!")
                            else:
                                print("  ❌ Encoding issues detected")
                                print(f"     Expected Nazwa: '{expected_nazwa}'")
                                print(f"     Actual Nazwa:   '{nazwa}'")
                                print(f"     Expected Gmina: '{expected_gmina}'")
                                print(f"     Actual Gmina:   '{gmina}'")
                                
                    except json.JSONDecodeError as e:
                        print(f"Failed to parse JSON response: {e}")
                else:
                    print("No content in result")
            else:
                print("Unexpected result format")
                
        else:
            print("No valid response received")
            if response:
                print(f"Response: {response}")
        
    except Exception as e:
        print(f"Test failed: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await client.stop_server()
    
    print("\n" + "=" * 60)
    print("Simplified server test completed!")

if __name__ == "__main__":
    asyncio.run(test_simplified_server())
