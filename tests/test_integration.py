#!/usr/bin/env python3
"""
Final Integration Test for Tool Configuration System

This script validates that the tool configuration system works correctly
with both stdio and HTTP servers.
"""

import os
import sys
import subprocess
import time
import json
import logging

# Configure UTF-8 encoding for proper Polish character handling
os.environ['PYTHONIOENCODING'] = 'utf-8'

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

def test_server_import():
    """Test that the servers can import tool configuration."""
    print("🧪 Testing server imports...")
    
    try:
        # Test stdio server
        sys.path.insert(0, 'regon_mcp_server')
        from regon_mcp_server import server
        from regon_mcp_server import server_http
        from regon_mcp_server.tool_config import get_config_loader
        
        print("   ✅ Server modules imported successfully")
        return True
    except Exception as e:
        print(f"   ❌ Import failed: {e}")
        return False

def test_configuration_loading():
    """Test configuration loading in server context."""
    print("\n🔧 Testing configuration loading...")
    
    try:
        from regon_mcp_server.tool_config import get_config_loader
        from regon_mcp_server import server
        
        # Test different configurations
        configs = ['default', 'polish', 'minimal']
        
        for config_name in configs:
            print(f"   Testing {config_name} configuration...")
            
            # Set the configuration
            server.config['tools_config'] = config_name
            
            # Initialize tool config
            server.initialize_tool_config()
            
            if server.tool_config_loader:
                tools = server.tool_config_loader.get_all_tools()
                server_info = server.tool_config_loader.get_server_info()
                print(f"     ✅ {config_name}: {len(tools)} tools, language: {server_info.get('language', 'unknown')}")
            else:
                print(f"     ⚠️ {config_name}: Using fallback tools")
        
        return True
    except Exception as e:
        print(f"   ❌ Configuration loading failed: {e}")
        return False

def test_argument_parsing():
    """Test command line argument parsing."""
    print("\n⚙️ Testing argument parsing...")
    
    try:
        from regon_mcp_server import server
        
        # Mock command line arguments
        original_argv = sys.argv
        
        # Test stdio server args
        sys.argv = ['server.py', '--tools-config', 'polish', '--log-level', 'DEBUG']
        args = server.parse_arguments()
        
        if args.tools_config == 'polish' and args.log_level == 'DEBUG':
            print("   ✅ Stdio server argument parsing works")
        else:
            print("   ❌ Stdio server argument parsing failed")
            return False
        
        # Test HTTP server args
        from regon_mcp_server import server_http
        sys.argv = ['server_http.py', '--tools-config', 'minimal', '--port', '8080']
        args = server_http.parse_arguments()
        
        if args.tools_config == 'minimal' and args.port == 8080:
            print("   ✅ HTTP server argument parsing works")
        else:
            print("   ❌ HTTP server argument parsing failed")
            return False
        
        # Restore original argv
        sys.argv = original_argv
        return True
        
    except Exception as e:
        print(f"   ❌ Argument parsing failed: {e}")
        sys.argv = original_argv
        return False

def test_environment_variables():
    """Test environment variable support."""
    print("\n🌍 Testing environment variable integration...")
    
    try:
        # Set environment variable
        original_tools_config = os.environ.get('TOOLS_CONFIG')
        os.environ['TOOLS_CONFIG'] = 'polish'
        
        from regon_mcp_server import server
        
        # Test argument parsing with env var
        original_argv = sys.argv
        sys.argv = ['server.py']
        args = server.parse_arguments()
        
        if args.tools_config == 'polish':
            print("   ✅ Environment variable TOOLS_CONFIG works")
            success = True
        else:
            print("   ❌ Environment variable TOOLS_CONFIG failed")
            success = False
        
        # Restore
        sys.argv = original_argv
        if original_tools_config:
            os.environ['TOOLS_CONFIG'] = original_tools_config
        else:
            del os.environ['TOOLS_CONFIG']
        
        return success
        
    except Exception as e:
        print(f"   ❌ Environment variable test failed: {e}")
        return False

def display_configuration_summary():
    """Display a summary of available configurations."""
    print("\n📋 Configuration Summary")
    print("=" * 50)
    
    try:
        from regon_mcp_server.tool_config import get_config_loader
        
        loader = get_config_loader()
        configs = loader.list_available_configs()
        
        for config_name in configs:
            info = loader.get_config_info(config_name)
            if info:
                print(f"🔧 {config_name.upper()}")
                print(f"   Name: {info['name']}")
                print(f"   Language: {info['language']}")
                print(f"   Tools: {info['tool_count']}")
                print(f"   Description: {info['description'][:60]}...")
                print()
        
        print("Usage Examples:")
        print("   python regon_mcp_server/server.py --tools-config polish")
        print("   python regon_mcp_server/server_http.py --tools-config minimal --port 8080")
        print("   set TOOLS_CONFIG=polish && python regon_mcp_server/server.py")
        
    except Exception as e:
        print(f"❌ Failed to display summary: {e}")

def main():
    """Run the integration test suite."""
    logging.basicConfig(level=logging.WARNING)  # Suppress INFO logs
    
    print("🚀 RegonAPI MCP Server - Tool Configuration Integration Test")
    print("=" * 70)
    
    success = True
    
    # Test 1: Import validation
    if not test_server_import():
        success = False
    
    # Test 2: Configuration loading
    if not test_configuration_loading():
        success = False
    
    # Test 3: Argument parsing
    if not test_argument_parsing():
        success = False
    
    # Test 4: Environment variables
    if not test_environment_variables():
        success = False
    
    # Display summary
    display_configuration_summary()
    
    print("=" * 70)
    if success:
        print("🎉 All integration tests passed!")
        print("✅ Tool configuration system is fully integrated and functional")
        print("\nNext steps:")
        print("  1. Test with actual MCP clients (VS Code, Claude Desktop, etc.)")
        print("  2. Verify UTF-8 encoding with Polish characters")
        print("  3. Test HTTP server endpoints with different configurations")
        print("  4. Validate API responses in both English and Polish")
    else:
        print("❌ Some integration tests failed")
        print("Please check the error messages above and fix any issues")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
