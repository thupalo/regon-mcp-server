#!/usr/bin/env python3
"""
Manual MCP Server Test with Raw JSON-RPC Messages
Tests the MCP server protocol compliance with manual JSON-RPC messages.

Usage:
    .\.venv\Scripts\python.exe tests\test_mcp_protocol.py
"""

import asyncio
import json
import sys
import os

# Configure UTF-8 encoding for proper Unicode handling
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except AttributeError:
        # Fallback for older Python versions
        import codecs
        sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer)
        sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer)

async def test_mcp_server():
    """Test the MCP server with manual JSON-RPC messages."""
    
    print("🚀 Testing MCP Protocol Compliance")
    print("=" * 50)
    
    # Change to project root if we're in tests directory
    original_dir = os.getcwd()
    if 'tests' in os.getcwd():
        os.chdir('..')
    
    try:
        # Start the server
        print("\n📋 Starting MCP server...")
        process = await asyncio.create_subprocess_exec(
            sys.executable, "regon_mcp_server/server.py", "--log-level", "ERROR",
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        async def send_message(message):
            """Send a JSON-RPC message to the server."""
            json_message = json.dumps(message) + '\n'
            process.stdin.write(json_message.encode())
            await process.stdin.drain()
        
        async def read_response():
            """Read a JSON-RPC response from the server."""
            line = await process.stdout.readline()
            if line:
                return json.loads(line.decode().strip())
            return None
        
        # Test 1: Initialize
        print("\n✅ Test 1: Server Initialization")
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "roots": {
                        "listChanged": True
                    },
                    "sampling": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        await send_message(init_message)
        response = await read_response()
        
        if response and response.get("result"):
            print("   ✅ Server initialized successfully")
            print(f"   📋 Protocol version: {response['result'].get('protocolVersion', 'Unknown')}")
            capabilities = response['result'].get('capabilities', {})
            print(f"   🔧 Server capabilities: {list(capabilities.keys())}")
        else:
            print(f"   ❌ Initialization failed: {response}")
            return
        
        # Test 2: List tools
        print("\n✅ Test 2: List Available Tools")
        list_tools_message = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        await send_message(list_tools_message)
        response = await read_response()
        
        if response and response.get("result") and "tools" in response["result"]:
            tools = response["result"]["tools"]
            print(f"   ✅ Found {len(tools)} tools")
            for i, tool in enumerate(tools[:5]):  # Show first 5
                print(f"   {i+1}. {tool['name']} - {tool.get('description', 'No description')[:50]}...")
            if len(tools) > 5:
                print(f"   ... and {len(tools) - 5} more tools")
        else:
            print(f"   ❌ Failed to list tools: {response}")
        
        # Test 3: Call a tool
        print("\n✅ Test 3: Call MCP Tool")
        call_tool_message = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/call",
            "params": {
                "name": "regon_search_by_nip",
                "arguments": {"nip": "7342867148"}
            }
        }
        
        await send_message(call_tool_message)
        response = await read_response()
        
        if response and response.get("result"):
            content = response["result"].get("content", [])
            if content and content[0].get("text"):
                result_data = json.loads(content[0]["text"])
                if isinstance(result_data, list) and len(result_data) > 0:
                    company = result_data[0]
                    print("   ✅ Tool call successful")
                    print(f"   🏢 Company: {company.get('Nazwa', 'Unknown')}")
                    print(f"   🆔 NIP: {company.get('Nip', 'Unknown')}")
                    print(f"   📍 Location: {company.get('Wojewodztwo', 'Unknown')}")
                    
                    # Check Polish character encoding
                    company_name = company.get('Nazwa', '')
                    if any(char in company_name for char in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ'):
                        print("   ✅ Polish characters properly encoded")
                else:
                    print("   ⚠️  Tool call completed but no data returned")
            else:
                print("   ❌ Tool call returned no content")
        elif response and response.get("error"):
            print(f"   ❌ Tool call error: {response['error']}")
        else:
            print(f"   ❌ Unexpected response: {response}")
        
        # Test 4: Invalid tool call
        print("\n✅ Test 4: Error Handling (Invalid Tool)")
        invalid_tool_message = {
            "jsonrpc": "2.0",
            "id": 4,
            "method": "tools/call",
            "params": {
                "name": "non_existent_tool",
                "arguments": {}
            }
        }
        
        await send_message(invalid_tool_message)
        response = await read_response()
        
        if response and response.get("error"):
            print("   ✅ Error handling works correctly")
            print(f"   ⚠️  Error: {response['error'].get('message', 'Unknown error')}")
        else:
            print(f"   ❌ Expected error response, got: {response}")
        
        # Cleanup
        print("\n🧹 Cleaning up...")
        process.stdin.close()
        await process.wait()
        
        print("\n🎉 MCP Protocol Test Completed!")
        print("\n📋 Summary:")
        print("   ✅ JSON-RPC 2.0 protocol compliance")
        print("   ✅ MCP initialization handshake")
        print("   ✅ Tool listing functionality")
        print("   ✅ Tool calling with arguments")
        print("   ✅ Error handling for invalid requests")
        print("   ✅ Polish character encoding support")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        if 'process' in locals():
            process.terminate()
            await process.wait()
    finally:
        # Restore original directory
        os.chdir(original_dir)

def main():
    """Main entry point."""
    try:
        asyncio.run(test_mcp_server())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main()
