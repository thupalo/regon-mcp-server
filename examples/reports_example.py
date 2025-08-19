#!/usr/bin/env python3
"""
Reports Example for RegonAPI MCP Server

This example demonstrates how to fetch different types of reports
for business entities using the MCP server.

Based on the report functionality from the original RegonAPI examples.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


class MCPClient:
    """Simple MCP client for testing the RegonAPI server."""
    
    def __init__(self, server_script="../regon_mcp_server/server.py"):
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
            print("⏹️  MCP Server stopped")
    
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
                "name": "regon-reports-example-client",
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
    Demonstrate report generation capabilities of the RegonAPI MCP Server.
    
    This example shows how to fetch different types of reports for business entities,
    similar to the original RegonAPI examples but using the MCP server.
    """
    
    print("RegonAPI MCP Server - Reports Example")
    print("=" * 40)
    print("Demonstrating different types of business reports")
    print("=" * 40)
    
    # Test entities
    CD_PROJEKT_REGON9 = "492707333"  # Legal entity
    
    # Report categories with descriptions
    report_categories = {
        "Legal Entity Reports": [
            ("BIR11OsPrawna", "Basic legal entity data"),
            ("BIR11OsPrawnaPkd", "Legal entity PKD codes (activity classification)"),
            ("BIR11OsPrawnaListaJednLokalnych", "List of local units"),
            ("BIR11TypPodmiotu", "Entity type information")
        ],
        "Local Units Reports": [
            ("BIR11JednLokalnaOsPrawnej", "Local unit of legal entity"),
            ("BIR11JednLokalnaOsPrawnejPkd", "Local unit PKD codes")
        ],
        "Partnership Reports": [
            ("BIR11OsPrawnaSpCywilnaWspolnicy", "Civil partnership participants")
        ]
    }
    
    # Natural person reports (for reference, though we're using a legal entity example)
    natural_person_reports = {
        "Natural Person Reports": [
            ("BIR11OsFizycznaDaneOgolne", "General natural person data"),
            ("BIR11OsFizycznaDzialalnoscCeidg", "CEIDG activity data"),
            ("BIR11OsFizycznaDzialalnoscRolnicza", "Agricultural activity"),
            ("BIR11OsFizycznaDzialalnoscPozostala", "Other activities"),
            ("BIR11OsFizycznaDzialalnoscSkreslonaDo20141108", "Deleted activities (until 2014-11-08)"),
            ("BIR11OsFizycznaPkd", "Natural person PKD codes"),
            ("BIR11OsFizycznaListaJednLokalnych", "List of local units"),
            ("BIR11JednLokalnaOsFizycznej", "Local unit of natural person"),
            ("BIR11JednLokalnaOsFizycznejPkd", "Local unit PKD codes")
        ]
    }
    
    client = MCPClient()
    
    try:
        # Start the server
        await client.start_server()
        
        # Initialize the session
        await client.initialize()
        
        print(f"\n🏢 Entity: CD Projekt (REGON: {CD_PROJEKT_REGON9})")
        print("=" * 50)
        
        # First, let's search for the entity to see what we're working with
        print("📋 Basic entity information:")
        search_result = await client.call_tool("regon_search_by_regon", {"regon": CD_PROJEKT_REGON9})
        print(search_result)
        
        # Now fetch different types of reports
        for category, reports in report_categories.items():
            print(f"\n📊 {category}")
            print("=" * (len(category) + 4))
            
            for report_name, description in reports:
                print(f"\n📄 Report: {report_name}")
                print(f"   Description: {description}")
                print("-" * 60)
                
                try:
                    result = await client.call_tool("regon_get_full_report", {
                        "regon": CD_PROJEKT_REGON9,
                        "report_name": report_name,
                        "strict": True
                    })
                    print(result)
                except Exception as e:
                    print(f"❌ Error fetching report: {e}")
        
        print(f"\n💡 Available Natural Person Reports")
        print("=" * 40)
        print("Note: These reports are for natural persons (individuals), not legal entities")
        print("They would be used with REGON numbers of individual entrepreneurs")
        
        for category, reports in natural_person_reports.items():
            print(f"\n📊 {category}")
            print("-" * (len(category) + 4))
            
            for report_name, description in reports[:3]:  # Show only first 3 for brevity
                print(f"   * {report_name}: {description}")
        
        print(f"\n🔍 Testing Report Validation")
        print("=" * 30)
        print("Testing with invalid report name...")
        
        try:
            result = await client.call_tool("regon_get_full_report", {
                "regon": CD_PROJEKT_REGON9,
                "report_name": "InvalidReportName",
                "strict": True
            })
            print(result)
        except Exception as e:
            print(f"✅ Correctly caught validation error: {e}")
        
        print(f"\n🔍 Testing with Non-strict Mode")
        print("=" * 32)
        print("Testing with strict=False...")
        
        result = await client.call_tool("regon_get_full_report", {
            "regon": CD_PROJEKT_REGON9,
            "report_name": "SomeCustomReport",
            "strict": False
        })
        print(result)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Clean up
        await client.stop_server()
    
    print(f"\n✅ Reports example completed!")
    print("\n" + "=" * 50)
    print("💡 Key takeaways:")
    print("   * Different report types provide different data")
    print("   * Legal entities and natural persons have different reports")
    print("   * Use strict=True for validation (recommended)")
    print("   * Reports contain detailed business information")
    print("   * PKD reports show activity classifications")


if __name__ == "__main__":
    print("Starting RegonAPI MCP Server Reports Example...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        sys.exit(1)
