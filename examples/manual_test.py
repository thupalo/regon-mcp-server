#!/usr/bin/env python3
"""
Manual test of MCP server with raw JSON-RPC messages.
"""

import asyncio
import json
import sys

async def test_mcp_server():
    """Test the MCP server with manual JSON-RPC messages."""
    
    # Start the server
    process = await asyncio.create_subprocess_exec(
        sys.executable, "simple_test_server.py",
        stdin=asyncio.subprocess.PIPE,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    try:
        # Send initialize message
        init_msg = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {},
                "clientInfo": {
                    "name": "manual-test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        print("Sending initialize message:")
        print(json.dumps(init_msg, indent=2))
        
        message = json.dumps(init_msg) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        # Read response
        line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        if line:
            response = json.loads(line.decode().strip())
            print("\nReceived initialize response:")
            print(json.dumps(response, indent=2))
        
        # Send initialized notification (required after initialize)
        initialized_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        print("\nSending initialized notification:")
        print(json.dumps(initialized_msg, indent=2))
        
        message = json.dumps(initialized_msg) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        # No response expected for notification
        await asyncio.sleep(0.1)  # Small delay to ensure processing
        
        # Send tools/list message
        list_msg = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/list",
            "params": {}
        }
        
        print("\nSending tools/list message:")
        print(json.dumps(list_msg, indent=2))
        
        message = json.dumps(list_msg) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        # Read response
        line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        if line:
            response = json.loads(line.decode().strip())
            print("\nReceived tools/list response:")
            print(json.dumps(response, indent=2))
        
        # Try alternative format without params
        list_msg2 = {
            "jsonrpc": "2.0",
            "id": 3,
            "method": "tools/list"
        }
        
        print("\nSending tools/list message (no params):")
        print(json.dumps(list_msg2, indent=2))
        
        message = json.dumps(list_msg2) + "\n"
        process.stdin.write(message.encode())
        await process.stdin.drain()
        
        # Read response
        line = await asyncio.wait_for(process.stdout.readline(), timeout=5.0)
        if line:
            response = json.loads(line.decode().strip())
            print("\nReceived tools/list response (no params):")
            print(json.dumps(response, indent=2))
            
    except asyncio.TimeoutError:
        print("Timeout waiting for response")
    except Exception as e:
        print(f"Error: {e}")
    finally:
        process.terminate()
        await process.wait()
        
        # Check stderr
        stderr = await process.stderr.read()
        if stderr:
            print(f"\nStderr output:")
            print(stderr.decode())

if __name__ == "__main__":
    asyncio.run(test_mcp_server())
