#!/usr/bin/env python3
"""
Basic MCP Client Example for RegonAPI MCP Server

This example demonstrates basic usage of the RegonAPI MCP Server,
equivalent to the original RegonAPI bir11_examples.py

Based on: https://github.com/rolzwy7/RegonAPI/blob/main/examples/bir11_examples.py
"""

import asyncio
import json
import sys
import os
from typing import Dict, Any

# Configure UTF-8 output for Windows console redirection
if sys.platform.startswith('win'):
    # Set environment variable to ensure UTF-8 encoding
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    
    # Reconfigure stdout to use UTF-8 encoding
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    elif hasattr(sys.stdout, 'buffer'):
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')


class MCPClient:
    """Simple MCP client for testing the RegonAPI server."""
    
    def __init__(self, server_script=None):
        if server_script is None:
            # Try to find the server script relative to this file
            current_dir = os.path.dirname(os.path.abspath(__file__))
            server_script = os.path.join(current_dir, "..", "regon_mcp_server", "server.py")
        self.server_script = server_script
        self.process = None
        self.id_counter = 0
    
    async def start_server(self):
        """Start the MCP server process."""
        self.process = await asyncio.create_subprocess_exec(
            sys.executable, self.server_script,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        print("🚀 MCP Server started")
    
    async def stop_server(self):
        """Stop the MCP server process."""
        if self.process:
            self.process.terminate()
            await self.process.wait()
            print("⏹️ MCP Server stopped")
    
    async def send_request(self, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Send a JSON-RPC request to the server."""
        self.id_counter += 1
        request = {
            "jsonrpc": "2.0",
            "id": self.id_counter,
            "method": method,
            "params": params or {}
        }
        
        message = json.dumps(request) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
        # Read response
        line = await self.process.stdout.readline()
        if line:
            return json.loads(line.decode().strip())
        else:
            stderr = await self.process.stderr.read()
            raise Exception(f"No response received. Stderr: {stderr.decode()}")
    
    async def initialize(self):
        """Initialize the MCP session."""
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "regon-example-client",
                "version": "1.0.0"
            }
        })
        
        # Send initialized notification (required after initialize)
        initialized_msg = {
            "jsonrpc": "2.0",
            "method": "notifications/initialized"
        }
        
        message = json.dumps(initialized_msg) + "\n"
        self.process.stdin.write(message.encode())
        await self.process.stdin.drain()
        
        print("✅ Initialized MCP session")
        return response
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a tool and return the text content."""
        response = await self.send_request("tools/call", {
            "name": tool_name,
            "arguments": arguments or {}
        })
        
        if "result" in response and response["result"]:
            result = response["result"]
            # Handle the new MCP response format
            if "content" in result and result["content"]:
                return result["content"][0]["text"]
            else:
                return "No content in result"
        elif "error" in response:
            return f"Error: {response['error']}"
        else:
            return "No result returned"


async def main():
    """
    Main example function demonstrating RegonAPI MCP Server usage.
    
    This example replicates the functionality from the original RegonAPI examples
    but using the MCP server instead of direct API calls.
    """
    
    print("RegonAPI MCP Server - Basic Usage Example")
    print("=" * 50)
    print("Based on: RegonAPI/examples/bir11_examples.py")
    print("=" * 50)
    
    # Test data (same as original examples)
    TEST_API_KEY = "abcde12345abcde12345"
    CD_PROJEKT_NIP = "7342867148"
    CD_PROJEKT_KRS = "0000006865"
    CD_PROJEKT_REGON9 = "492707333"
    
    # Available reports (same as original examples)
    REPORTS = [
        "BIR11OsFizycznaDaneOgolne",
        "BIR11OsFizycznaDzialalnoscCeidg",
        "BIR11OsFizycznaDzialalnoscRolnicza",
        "BIR11OsFizycznaDzialalnoscPozostala",
        "BIR11OsFizycznaDzialalnoscSkreslonaDo20141108",
        "BIR11OsFizycznaPkd",
        "BIR11OsFizycznaListaJednLokalnych",
        "BIR11JednLokalnaOsFizycznej",
        "BIR11JednLokalnaOsFizycznejPkd",
        "BIR11OsPrawna",
        "BIR11OsPrawnaPkd",
        "BIR11OsPrawnaListaJednLokalnych",
        "BIR11JednLokalnaOsPrawnej",
        "BIR11JednLokalnaOsPrawnejPkd",
        "BIR11OsPrawnaSpCywilnaWspolnicy",
        "BIR11TypPodmiotu"
    ]
    
    client = MCPClient()
    
    try:
        # Start the server
        await client.start_server()
        
        # Initialize the session
        await client.initialize()
        
        print("\n🔍 Testing Service Status...")
        # Get service status
        status = await client.call_tool("regon_get_service_status")
        print(f"Service Status:\n{status}")
        
        print("\n📊 Testing Data Status...")
        # Get data status
        data_status = await client.call_tool("regon_get_data_status")
        print(f"Data Status:\n{data_status}")
        
        print(f"\n🔍 Search by NIP: {CD_PROJEKT_NIP}")
        print("-" * 40)
        # Search by NIP (equivalent to: api.searchData(nip=CD_PROJEKT_NIP))
        result = await client.call_tool("regon_search_by_nip", {"nip": CD_PROJEKT_NIP})
        print(result)
        
        print(f"\n🔍 Search by KRS: {CD_PROJEKT_KRS}")
        print("-" * 40)
        # Search by KRS (equivalent to: api.searchData(krs=CD_PROJEKT_KRS))
        result = await client.call_tool("regon_search_by_krs", {"krs": CD_PROJEKT_KRS})
        print(result)
        
        print(f"\n🔍 Search by REGON: {CD_PROJEKT_REGON9}")
        print("-" * 40)
        # Search by REGON (equivalent to: api.searchData(regon=CD_PROJEKT_REGON9))
        result = await client.call_tool("regon_search_by_regon", {"regon": CD_PROJEKT_REGON9})
        print(result)
        
        print(f"\n📋 Getting reports for REGON: {CD_PROJEKT_REGON9}")
        print("-" * 50)
        
        # Get a few sample reports (equivalent to: api.dataDownloadFullReport(CD_PROJEKT_REGON9, report_name))
        sample_reports = [
            "BIR11OsPrawna",  # Basic legal entity data
            "BIR11OsPrawnaPkd",  # Legal entity PKD codes
            "BIR11TypPodmiotu"  # Entity type
        ]
        
        for report_name in sample_reports:
            print(f"\n📄 Report: {report_name}")
            print("-" * 30)
            result = await client.call_tool("regon_get_full_report", {
                "regon": CD_PROJEKT_REGON9,
                "report_name": report_name
            })
            print(result)
        
        print(f"\n🔍 Testing bulk search with multiple NIPs...")
        print("-" * 45)
        # Test multiple NIPs search
        result = await client.call_tool("regon_search_multiple_nips", {
            "nips": [CD_PROJEKT_NIP, "1234567890"]  # Add a dummy NIP for comparison
        })
        print(result)
        
        print(f"\n⚙️ Getting available operations...")
        print("-" * 35)
        # Get available operations
        operations = await client.call_tool("regon_get_available_operations")
        print(operations)
        
        print(f"\n❌ Getting last error code...")
        print("-" * 30)
        # Get last error code
        error_info = await client.call_tool("regon_get_last_error_code")
        print(error_info)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Clean up
        await client.stop_server()
    
    print(f"\n✅ Example completed!")
    print("\n" + "=" * 50)
    print("💡 This example demonstrates basic MCP server usage.")
    print("   For more examples, see other files in this examples/ folder.")


if __name__ == "__main__":
    print("Starting RegonAPI MCP Server Basic Example...")
    
    # Also write output to a UTF-8 encoded file
    output_file = "basic_example_output_utf8.txt"
    
    # Redirect stdout to capture output
    import io
    from contextlib import redirect_stdout
    
    # Create a StringIO object to capture output
    captured_output = io.StringIO()
    
    try:
        with redirect_stdout(captured_output):
            asyncio.run(main())
        
        # Get the captured output
        output_content = captured_output.getvalue()
        
        # Write to file with UTF-8 encoding
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(output_content)
        
        print(f"[UTF8] Output also saved to {output_file} with proper UTF-8 encoding")
        
    except KeyboardInterrupt:
        print("\n[STOP] Example interrupted by user")
    except Exception as e:
        print(f"\n🔴 Example failed: {e}")
        sys.exit(1)
