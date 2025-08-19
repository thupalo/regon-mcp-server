#!/usr/bin/env python3
"""
Test Tool Configuration System

This script tests the tool configuration loading functionality
to ensure all JSON configurations work correctly.
"""

import os
import sys
import logging

# Configure UTF-8 encoding for proper Polish character handling
os.environ['PYTHONIOENCODING'] = 'utf-8'

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# Set up path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'regon_mcp_server'))

from regon_mcp_server.tool_config import get_config_loader, get_available_tool_configs

def test_config_discovery():
    """Test discovery of available configurations."""
    print("🔍 Testing configuration discovery...")
    
    configs = get_available_tool_configs()
    print(f"   Available configurations: {configs}")
    
    if len(configs) == 0:
        print("   ❌ No configurations found!")
        return False
    else:
        print(f"   ✅ Found {len(configs)} configurations")
        return True

def test_config_loading():
    """Test loading of each configuration."""
    print("\n📂 Testing configuration loading...")
    
    loader = get_config_loader()
    configs = loader.list_available_configs()
    
    results = {}
    
    for config_name in configs:
        try:
            print(f"\n   Testing config: {config_name}")
            
            # Get basic info without full load
            info = loader.get_config_info(config_name)
            if info:
                print(f"     Name: {info['name']}")
                print(f"     Language: {info['language']}")
                print(f"     Tools: {info['tool_count']}")
                print(f"     Description: {info['description']}")
            
            # Load the configuration
            config_data = loader.load_config(config_name)
            server_info = loader.get_server_info()
            tools = loader.get_all_tools()
            
            print(f"     ✅ Loaded successfully")
            print(f"     Server: {server_info.get('name', 'Unknown')}")
            print(f"     Language: {server_info.get('language', 'unknown')}")
            print(f"     Tools count: {len(tools)}")
            
            # Check first few tools
            for i, tool in enumerate(tools[:3]):
                print(f"       Tool {i+1}: {tool.get('name', 'unnamed')}")
                print(f"                 {tool.get('description', 'no description')[:60]}...")
            
            results[config_name] = True
            
        except Exception as e:
            print(f"     ❌ Failed to load: {e}")
            results[config_name] = False
    
    return results

def test_environment_variables():
    """Test environment variable configuration."""
    print("\n🌍 Testing environment variable support...")
    
    loader = get_config_loader()
    
    # Test default config (should be 'detailed')
    print("   Testing default config...")
    try:
        config_data = loader.load_config()
        server_info = loader.get_server_info()
        print(f"     ✅ Default config loaded: {server_info.get('name', 'Unknown')}")
        print(f"     Language: {server_info.get('language', 'unknown')}")
    except Exception as e:
        print(f"     ❌ Default config failed: {e}")
        return False
    
    # Test specific configs
    test_configs = ['default', 'polish', 'minimal']
    
    for config_name in test_configs:
        print(f"\n   Testing specific config: {config_name}")
        try:
            config_data = loader.load_config(config_name)
            server_info = loader.get_server_info()
            print(f"     ✅ Config '{config_name}' loaded: {server_info.get('name', 'Unknown')}")
            print(f"     Language: {server_info.get('language', 'unknown')}")
        except Exception as e:
            print(f"     ❌ Config '{config_name}' failed: {e}")
    
    return True

def test_tool_queries():
    """Test specific tool queries."""
    print("\n🔧 Testing tool queries...")
    
    loader = get_config_loader()
    
    # Load a config
    config_data = loader.load_config('default')
    
    # Test getting specific tools
    test_tools = ['regon_search_by_nip', 'regon_search_by_regon', 'regon_get_full_report']
    
    for tool_name in test_tools:
        tool_info = loader.get_tool_info(tool_name)
        if tool_info:
            print(f"   ✅ Tool '{tool_name}' found")
            print(f"     Description: {tool_info.get('description', 'no description')[:60]}...")
        else:
            print(f"   ❌ Tool '{tool_name}' not found")

def main():
    """Run all tests."""
    logging.basicConfig(level=logging.WARNING)  # Suppress INFO logs during testing
    
    print("🧪 RegonAPI MCP Server - Tool Configuration Test Suite")
    print("=" * 60)
    
    success = True
    
    # Test 1: Configuration discovery
    if not test_config_discovery():
        success = False
    
    # Test 2: Configuration loading
    results = test_config_loading()
    if not all(results.values()):
        success = False
        print(f"\n❌ Failed configurations: {[k for k, v in results.items() if not v]}")
    
    # Test 3: Environment variables
    if not test_environment_variables():
        success = False
    
    # Test 4: Tool queries
    test_tool_queries()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 All tests passed! Tool configuration system is working correctly.")
        print("\nAvailable configurations:")
        configs = get_available_tool_configs()
        for config in configs:
            loader = get_config_loader()
            info = loader.get_config_info(config)
            if info:
                print(f"  • {config}: {info['name']} ({info['language']}) - {info['tool_count']} tools")
        
        print("\nTo use a specific configuration:")
        print("  • Set environment variable: set TOOLS_CONFIG=polish")
        print("  • Or use command line: python server.py --tools-config polish")
    else:
        print("❌ Some tests failed. Please check the configuration files.")
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())
