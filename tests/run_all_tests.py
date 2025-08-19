#!/usr/bin/env python3
"""
Run All Tests Script
Comprehensive test suite for both stdio and HTTP MCP servers.

Usage:
    .\.venv\Scripts\python.exe tests\run_all_tests.py
    .\.venv\Scripts\python.exe tests\run_all_tests.py --port 8000
    .\.venv\Scripts\python.exe tests\run_all_tests.py -p 9000
"""

import asyncio
import subprocess
import sys
import os
import time
import requests
import argparse
from pathlib import Path

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

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Run all REGON MCP Server tests',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tests/run_all_tests.py                       # Test with default port 8001
  python tests/run_all_tests.py --port 8000           # Test HTTP server on port 8000
  python tests/run_all_tests.py -p 9000               # Test HTTP server on port 9000
        """
    )
    
    parser.add_argument(
        '--port', '-p',
        type=int,
        default=8001,
        help='HTTP server port to test (default: 8001)'
    )
    
    return parser.parse_args()

def print_header(title):
    """Print a formatted test section header."""
    print("\n" + "=" * 60)
    print(f"🧪 {title}")
    print("=" * 60)

def print_section(title):
    """Print a formatted test subsection."""
    print(f"\n📋 {title}")
    print("-" * 40)

async def test_stdio_server():
    """Test the stdio MCP server."""
    print_section("Stdio MCP Server Tests")
    
    # Change to project root if needed
    original_dir = os.getcwd()
    if 'tests' in os.getcwd():
        os.chdir('..')
    
    try:
        # Run stdio server test
        result = subprocess.run([
            sys.executable, "tests/test_stdio_server.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Stdio server tests PASSED")
            return True
        else:
            print("❌ Stdio server tests FAILED")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ Stdio server test error: {e}")
        return False
    finally:
        os.chdir(original_dir)

async def test_mcp_protocol():
    """Test MCP protocol compliance."""
    print_section("MCP Protocol Compliance Tests")
    
    original_dir = os.getcwd()
    if 'tests' in os.getcwd():
        os.chdir('..')
    
    try:
        result = subprocess.run([
            sys.executable, "tests/test_mcp_protocol.py"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ MCP protocol tests PASSED")
            return True
        else:
            print("❌ MCP protocol tests FAILED")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ MCP protocol test error: {e}")
        return False
    finally:
        os.chdir(original_dir)

async def test_http_server(port=8001):
    """Test the HTTP MCP server."""
    print_section("HTTP MCP Server Tests")
    
    original_dir = os.getcwd()
    if 'tests' in os.getcwd():
        os.chdir('..')
    
    try:
        # Check if HTTP server is already running
        try:
            response = requests.get(f"http://localhost:{port}/health", timeout=2)
            server_running = response.status_code == 200
        except:
            server_running = False
        
        if not server_running:
            print(f"⚠️  HTTP server not running on port {port}. Please start it manually:")
            print(f"   .\\venv\\Scripts\\python.exe regon_mcp_server\\server_http.py --port {port}")
            print("\nThen run HTTP tests separately:")
            print(f"   .\\venv\\Scripts\\python.exe tests\\test_http_server.py --port {port}")
            return False
        
        # Run HTTP server test
        result = subprocess.run([
            sys.executable, "tests/test_http_server.py", "--port", str(port)
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ HTTP server tests PASSED")
            return True
        else:
            print("❌ HTTP server tests FAILED")
            print(result.stderr)
            return False
    except Exception as e:
        print(f"❌ HTTP server test error: {e}")
        return False
    finally:
        os.chdir(original_dir)

def check_environment():
    """Check if the environment is properly set up."""
    print_section("Environment Check")
    
    # Check if we're in the right directory
    if not os.path.exists("regon_mcp_server"):
        print("❌ Not in project root directory")
        return False
    
    # Check if virtual environment is active or available
    venv_python = Path(".venv/Scripts/python.exe")
    if not venv_python.exists():
        print("❌ Virtual environment not found at .venv/Scripts/python.exe")
        return False
    
    # Check if required modules are installed
    try:
        import mcp
        import fastapi
        import uvicorn
        import requests
        print("✅ All required modules are installed")
    except ImportError as e:
        print(f"❌ Missing required module: {e}")
        return False
    
    print("✅ Environment check PASSED")
    return True

async def main():
    """Run all tests."""
    # Parse command line arguments
    args = parse_arguments()
    
    print_header("REGON MCP Server Test Suite")
    print(f"🌐 HTTP Server Port: {args.port}")
    
    # Change to project root if needed
    original_dir = os.getcwd()
    if 'tests' in os.getcwd():
        os.chdir('..')
    
    try:
        # Environment check
        if not check_environment():
            print("\n❌ Environment check failed. Please fix issues before running tests.")
            return
        
        # Track test results
        results = {
            "stdio_server": False,
            "mcp_protocol": False,
            "http_server": False
        }
        
        # Run stdio server tests
        print_header("Testing Stdio MCP Server")
        results["stdio_server"] = await test_stdio_server()
        
        # Run MCP protocol tests
        print_header("Testing MCP Protocol Compliance")
        results["mcp_protocol"] = await test_mcp_protocol()
        
        # Run HTTP server tests
        print_header("Testing HTTP MCP Server")
        results["http_server"] = await test_http_server(port=args.port)
        
        # Summary
        print_header("Test Results Summary")
        total_tests = len(results)
        passed_tests = sum(results.values())
        
        for test_name, passed in results.items():
            status = "✅ PASSED" if passed else "❌ FAILED"
            print(f"{test_name.replace('_', ' ').title()}: {status}")
        
        print(f"\nOverall: {passed_tests}/{total_tests} test suites passed")
        
        if passed_tests == total_tests:
            print("\n🎉 All tests PASSED! Your REGON MCP server is working correctly.")
        else:
            print(f"\n⚠️  {total_tests - passed_tests} test suite(s) failed. Please check the output above.")
        
        # Instructions for failed tests
        if not results["http_server"]:
            print("\n💡 HTTP Server Test Instructions:")
            print(f"   1. Start HTTP server: .\\venv\\Scripts\\python.exe regon_mcp_server\\server_http.py --port {args.port}")
            print(f"   2. Run HTTP tests: .\\venv\\Scripts\\python.exe tests\\test_http_server.py --port {args.port}")
        
    except Exception as e:
        print(f"\n❌ Test suite error: {e}")
    finally:
        os.chdir(original_dir)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n🛑 Test suite interrupted by user")
    except Exception as e:
        print(f"\n❌ Test suite failed: {e}")
