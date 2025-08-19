#!/usr/bin/env python3
"""
Test script for the consolidated RegonAPI MCP Server

This script tests both test and production modes of the new server.
"""

import asyncio
import json
import subprocess
import sys
import time

async def test_server_mode(mode_name, command_args):
    """Test a specific server mode."""
    print(f"\n{'='*60}")
    print(f"Testing {mode_name} mode")
    print(f"Command: {sys.executable} {' '.join(command_args)}")
    print(f"{'='*60}")
    
    try:
        # Start the server process (use current Python executable)
        process = await asyncio.create_subprocess_exec(
            sys.executable, *command_args,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        # Send initialization message
        init_message = {
            "jsonrpc": "2.0",
            "id": 1,
            "method": "initialize",
            "params": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "clientInfo": {
                    "name": "test-client",
                    "version": "1.0.0"
                }
            }
        }
        
        # Send message
        message_str = json.dumps(init_message) + "\n"
        process.stdin.write(message_str.encode())
        await process.stdin.drain()
        
        # Send notifications/initialized
        initialized_notification = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        notification_str = json.dumps(initialized_notification) + "\n"
        process.stdin.write(notification_str.encode())
        await process.stdin.drain()
        
        # Send a test tool call
        test_call = {
            "jsonrpc": "2.0",
            "id": 2,
            "method": "tools/call",
            "params": {
                "name": "regon_get_service_status",
                "arguments": {}
            }
        }
        
        call_str = json.dumps(test_call) + "\n"
        process.stdin.write(call_str.encode())
        await process.stdin.drain()
        
        # Read response with timeout
        try:
            stdout_data, stderr_data = await asyncio.wait_for(
                process.communicate(), timeout=10.0
            )
            
            if stdout_data:
                print(f"✅ {mode_name} mode started successfully")
                # Try to parse the response
                lines = stdout_data.decode().strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if 'result' in response:
                                print(f"✅ Service call successful: {response['result']}")
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                print(f"❌ No response from {mode_name} mode")
                
            if stderr_data:
                stderr_text = stderr_data.decode()
                if "ERROR" in stderr_text:
                    print(f"❌ Errors in {mode_name} mode:")
                    print(stderr_text)
                else:
                    print(f"ℹ️  Server logs for {mode_name} mode:")
                    print(stderr_text[:500] + "..." if len(stderr_text) > 500 else stderr_text)
        
        except asyncio.TimeoutError:
            print(f"⏰ {mode_name} mode timeout - server may be running but not responding")
            process.terminate()
            
    except Exception as e:
        print(f"❌ Failed to test {mode_name} mode: {e}")

async def main():
    """Main test function."""
    print("Testing Consolidated RegonAPI MCP Server")
    print("=" * 60)
    
    # Test different modes
    test_modes = [
        ("Test (Default)", ["regon_mcp_server/server.py"]),
        ("Test with Debug", ["regon_mcp_server/server.py", "--log-level", "DEBUG"]),
        ("Production", ["regon_mcp_server/server.py", "--production"]),
        ("Production with Warning logs", ["regon_mcp_server/server.py", "--production", "--log-level", "WARNING"])
    ]
    
    for mode_name, command_args in test_modes:
        await test_server_mode(mode_name, command_args)
        # Small delay between tests
        await asyncio.sleep(1)
    
    print(f"\n{'='*60}")
    print("Server consolidation testing completed!")
    print("Check the logs above to verify all modes are working correctly.")
    print(f"{'='*60}")

if __name__ == "__main__":
    asyncio.run(main())
