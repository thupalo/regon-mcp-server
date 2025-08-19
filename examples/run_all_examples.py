#!/usr/bin/env python3
"""
Run All Examples Script for RegonAPI MCP Server

This script runs all available examples in sequence,
providing a comprehensive demonstration of the MCP server capabilities.
"""

import asyncio
import subprocess
import sys
import os
from datetime import datetime

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


def print_header(title: str, char: str = "="):
    """Print a formatted header."""
    width = 60
    print(f"\n{char * width}")
    print(f"{title:^{width}}")
    print(f"{char * width}\n")


def print_section(title: str):
    """Print a section header."""
    print(f"\n{'-' * 50}")
    print(f"📝 {title}")
    print(f"{'-' * 50}\n")


async def run_example(script_name: str, description: str) -> bool:
    """Run a single example script."""
    print_section(f"Running: {script_name}")
    print(f"[DESC] Description: {description}")
    print(f"⏰ Started at: {datetime.now().strftime('%H:%M:%S')}")
    
    try:
        # Run the example script
        process = await asyncio.create_subprocess_exec(
            sys.executable, script_name,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode == 0:
            print("✅ Example completed successfully!")
            if stdout:
                print("\n📤")
                # Safely decode with fallback
                try:
                    output_text = stdout.decode('utf-8')
                except UnicodeDecodeError:
                    output_text = stdout.decode('utf-8', errors='replace')
                print(output_text[:1000] + "..." if len(output_text) > 1000 else output_text)
            return True
        else:
            print(f"🔴 Example failed with return code: {process.returncode}")
            if stderr:
                print("\n❌")
                # Safely decode with fallback
                try:
                    error_text = stderr.decode('utf-8')
                except UnicodeDecodeError:
                    error_text = stderr.decode('utf-8', errors='replace')
                print(error_text)
            return False
            
    except Exception as e:
        print(f"❌ Error running example: {e}")
        return False


def check_prerequisites():
    """Check if all prerequisites are met."""
    print_section("Checking Prerequisites")
    
    # Check if we're in the examples directory
    if not os.path.basename(os.getcwd()) == "examples":
        print("🔴 Please run this script from the examples directory")
        return False
    
    # Check if parent server script exists
    server_script = "../regon_mcp_server/server.py"
    if not os.path.exists(server_script):
        print(f"🔴 Server script not found: {server_script}")
        return False
    
    # Check if .env file exists
    env_file = "../.env"
    if not os.path.exists(env_file):
        print(f"⚠️ Warning: .env file not found: {env_file}")
        print("   Examples will use default test API key")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major < 3 or (python_version.major == 3 and python_version.minor < 7):
        print(f"🔴 Python 3.7+ required, found: {python_version.major}.{python_version.minor}")
        return False
    
    print("✅ All prerequisites met!")
    return True


async def main():
    """Main function to run all examples."""
    print_header("RegonAPI MCP Server - All Examples Runner")
    print("This script will run all available examples in sequence.")
    print("Each example demonstrates different aspects of the MCP server.")
    
    if not check_prerequisites():
        print("\n🔴 Prerequisites not met. Please fix the issues above.")
        return
    
    # Define examples to run
    examples = [
        ("basic_usage_example.py", "Basic usage patterns - searching and reports"),
        ("bulk_search_example.py", "Bulk search operations for performance"),
        ("reports_example.py", "Comprehensive report generation"),
        ("monitoring_example.py", "Error handling and service monitoring"),
        ("advanced_example.py", "Advanced workflows and business intelligence")
    ]
    
    print(f"\n📝 Will run {len(examples)} examples:")
    for i, (script, desc) in enumerate(examples, 1):
        print(f"   {i}. {script} - {desc}")
    
    print("\n⏰ Starting examples execution...")
    start_time = datetime.now()
    
    results = []
    
    for i, (script_name, description) in enumerate(examples, 1):
        print_header(f"Example {i}/{len(examples)}: {script_name}", "=")
        
        success = await run_example(script_name, description)
        results.append((script_name, success))
        
        if success:
            print("✅ Example completed successfully!")
        else:
            print("🔴 Example failed!")
            
        # Add a pause between examples
        if i < len(examples):
            print("\n[WAIT] Pausing 2 seconds before next example...")
            await asyncio.sleep(2)
    
    # Summary
    end_time = datetime.now()
    duration = end_time - start_time
    
    print_header("Execution Summary")
    
    successful = sum(1 for _, success in results if success)
    failed = len(results) - successful
    
    print(f"📊 Results:")
    print(f"   * Total examples: {len(results)}")
    print(f"   * Successful: {successful}")
    print(f"   * Failed: {failed}")
    print(f"   * Success rate: {(successful/len(results)*100):.1f}%")
    
    print(f"\n⏰ Timing:")
    print(f"   * Started: {start_time.strftime('%H:%M:%S')}")
    print(f"   * Finished: {end_time.strftime('%H:%M:%S')}")
    print(f"   * Total duration: {duration.total_seconds():.1f} seconds")
    
    print(f"\n[RESULTS] Detailed Results:")
    for script_name, success in results:
        status = "🟢" if success else "🔴"
        print(f"   * {script_name}: {status}")
    
    if failed > 0:
        print(f"\n⚠️ {failed} example(s) failed. Please check the output above for details.")
        print("   Common issues:")
        print("   * Server startup problems")
        print("   * Network connectivity")
        print("   * API key configuration")
        print("   * Missing dependencies")
    else:
        print("\n🎉 All examples completed successfully!")
        print("   The RegonAPI MCP Server is working correctly.")
    
    print(f"\n📝 Next steps:")
    print("   * Review individual example code for learning")
    print("   * Modify examples with your own data")
    print("   * Integrate patterns into your applications")
    print("   * Check the examples/README.md for more details")


if __name__ == "__main__":
    print("RegonAPI MCP Server - All Examples Runner")
    print("=" * 50)
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[STOP] Execution interrupted by user")
        print("   You can run individual examples manually if needed.")
    except Exception as e:
        print(f"\n❌ Script failed: {e}")
        sys.exit(1)
