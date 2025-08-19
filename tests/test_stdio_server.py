#!/usr/bin/env python3
"""
Stdio MCP Server Test Script
Tests the main stdio MCP server functionality.

Usage:
    .\.venv\Scripts\python.exe tests\test_stdio_server.py
"""

import subprocess
import sys
import json
import asyncio
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

async def test_server_functionality():
    """Test basic server functionality with a simple tool call."""
    print("🚀 Testing Stdio MCP Server")
    print("=" * 50)
    
    # Change to project root if we're in tests directory
    original_dir = os.getcwd()
    if 'tests' in os.getcwd():
        os.chdir('..')
    
    try:
        # Test 1: Test mode (default)
        print("\n📋 Test 1: Default test mode")
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", "--log-level", "WARNING"
            ], input='{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}\n', 
               text=True, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                # Parse JSON-RPC response
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get("result") and "tools" in response["result"]:
                                tools = response["result"]["tools"]
                                print(f"   ✅ Found {len(tools)} tools")
                                print(f"   📋 Available tools: {', '.join([t['name'] for t in tools[:3]])}...")
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                print(f"   ❌ Server failed with return code: {result.returncode}")
                print(f"   Error: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("   ❌ Server test timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 2: Production mode flag
        print("\n📋 Test 2: Production mode startup test")
        try:
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", "--production", "--log-level", "ERROR"
            ], input='{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}\n', 
               text=True, capture_output=True, timeout=10)
            
            if result.returncode == 0:
                print("   ✅ Production mode server starts successfully")
            else:
                print(f"   ⚠️  Production mode failed (may need API_KEY): {result.stderr[:100]}")
                
        except subprocess.TimeoutExpired:
            print("   ❌ Production mode test timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        # Test 3: Tool call test
        print("\n📋 Test 3: Tool call functionality")
        try:
            tool_call = {
                "jsonrpc": "2.0",
                "id": 1,
                "method": "tools/call",
                "params": {
                    "name": "regon_search_by_nip",
                    "arguments": {"nip": "7342867148"}
                }
            }
            
            result = subprocess.run([
                sys.executable, "regon_mcp_server/server.py", "--log-level", "ERROR"
            ], input=json.dumps(tool_call) + '\n', 
               text=True, capture_output=True, timeout=15)
            
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                for line in lines:
                    if line.strip():
                        try:
                            response = json.loads(line)
                            if response.get("result") and "content" in response["result"]:
                                content = response["result"]["content"]
                                if content and content[0].get("text"):
                                    result_data = json.loads(content[0]["text"])
                                    if isinstance(result_data, list) and len(result_data) > 0:
                                        company = result_data[0]
                                        print(f"   ✅ Tool call successful")
                                        print(f"   🏢 Company: {company.get('Nazwa', 'Unknown')}")
                                        print(f"   🆔 NIP: {company.get('Nip', 'Unknown')}")
                                        
                                        # Test Polish character encoding
                                        company_name = company.get('Nazwa', '')
                                        if any(char in company_name for char in 'ąćęłńóśźżĄĆĘŁŃÓŚŹŻ'):
                                            print(f"   ✅ Polish characters properly encoded")
                                        else:
                                            print(f"   ℹ️  No Polish characters in this company name")
                                        break
                            elif response.get("error"):
                                print(f"   ❌ Tool call error: {response['error']}")
                                break
                        except json.JSONDecodeError:
                            continue
            else:
                print(f"   ❌ Tool call failed: {result.stderr}")
                
        except subprocess.TimeoutExpired:
            print("   ❌ Tool call test timed out")
        except Exception as e:
            print(f"   ❌ Error: {e}")

        print("\n🎉 Stdio MCP Server test completed!")
        print("\n📋 Summary:")
        print("   - Test mode: Server startup and tool listing")
        print("   - Production mode: Startup test (may require API_KEY)")
        print("   - Tool functionality: NIP search with encoding test")
        
    finally:
        # Restore original directory
        os.chdir(original_dir)

def main():
    """Main entry point."""
    try:
        asyncio.run(test_server_functionality())
    except KeyboardInterrupt:
        print("\n🛑 Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")

if __name__ == "__main__":
    main()
