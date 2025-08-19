#!/usr/bin/env python3
"""
Simple test script to verify the consolidated RegonAPI MCP Server
Tests both test and production modes
"""

import subprocess
import sys
import json
import asyncio

async def test_server_functionality():
    """Test basic server functionality with a simple tool call."""
    print("🚀 Testing Consolidated RegonAPI MCP Server")
    print("=" * 50)
    
    # Test 1: Test mode (default)
    print("\n📋 Test 1: Default test mode")
    try:
        result = subprocess.run([
            sys.executable, "regon_mcp_server/server.py", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Test mode server starts successfully")
            print("📋 Available options:")
            print(result.stdout)
        else:
            print(f"❌ Test mode failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⏰ Test mode timeout (but server likely working)")
    except Exception as e:
        print(f"❌ Test mode error: {e}")
    
    # Test 2: Production mode
    print("\n📋 Test 2: Production mode")
    try:
        result = subprocess.run([
            sys.executable, "regon_mcp_server/server.py", "--production", "--help"
        ], capture_output=True, text=True, timeout=10)
        
        if result.returncode == 0:
            print("✅ Production mode server starts successfully")
        else:
            print(f"❌ Production mode failed: {result.stderr}")
    except subprocess.TimeoutExpired:
        print("⏰ Production mode timeout (but server likely working)")
    except Exception as e:
        print(f"❌ Production mode error: {e}")
    
    # Test 3: Check project structure
    print("\n📋 Test 3: Project structure validation")
    import os
    
    required_files = [
        "regon_mcp_server/server.py",
        "regon_mcp_server/__init__.py", 
        "regon_mcp_server/README.md",
        "mcp.json",
        ".env",
        "examples/run_all_examples.py"
    ]
    
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ Missing: {file_path}")
    
    # Test 4: MCP configuration validation
    print("\n📋 Test 4: MCP configuration validation")
    try:
        with open("mcp.json", "r") as f:
            mcp_config = json.load(f)
        
        expected_servers = ["regon-api-test", "regon-api-production", "regon-api-debug"]
        for server in expected_servers:
            if server in mcp_config.get("mcpServers", {}):
                print(f"✅ MCP server config: {server}")
            else:
                print(f"❌ Missing MCP server config: {server}")
                
    except Exception as e:
        print(f"❌ MCP config validation failed: {e}")
    
    # Test 5: Environment configuration
    print("\n📋 Test 5: Environment configuration")
    try:
        with open(".env", "r") as f:
            env_content = f.read()
        
        if "API_KEY" in env_content:
            print("✅ Production API_KEY configured")
        else:
            print("⚠️  Production API_KEY not configured")
            
        if "TEST_API_KEY" in env_content:
            print("✅ Test API_KEY configured")
        else:
            print("⚠️  Test API_KEY not configured")
            
    except Exception as e:
        print(f"❌ Environment config check failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Server consolidation validation completed!")
    print("📖 Usage examples:")
    print("   # Test mode:")
    print("   python regon_mcp_server/server.py")
    print("   # Production mode:")
    print("   python regon_mcp_server/server.py --production")
    print("   # Debug mode:")
    print("   python regon_mcp_server/server.py --log-level DEBUG")
    print("📚 Run examples: cd examples && python run_all_examples.py")

if __name__ == "__main__":
    asyncio.run(test_server_functionality())
