#!/usr/bin/env python3
"""
Advanced MCP Client Example for RegonAPI MCP Server

This example demonstrates more advanced usage patterns including
async operations, error handling, and complex business logic workflows.
"""

import asyncio
import json
import os
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
from datetime import datetime

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
    os.environ['PYTHONIOENCODING'] = 'utf-8'


@dataclass
class BusinessEntity:
    """Data class to represent a business entity."""
    name: str
    nip: str
    regon: str
    krs: Optional[str] = None
    entity_type: Optional[str] = None
    address: Optional[str] = None


class AdvancedMCPClient:
    """Advanced MCP client with enhanced functionality."""
    
    def __init__(self, server_script="../regon_mcp_server/server.py"):
        self.server_script = server_script
        self.process = None
        self.id_counter = 0
        self.session_initialized = False
    
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
        if self.session_initialized:
            return
            
        response = await self.send_request("initialize", {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {
                "name": "regon-advanced-example-client",
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
        
        self.session_initialized = True
        print("✅ Initialized MCP session")
        return response
    
    async def call_tool(self, tool_name: str, arguments: Dict[str, Any] = None) -> str:
        """Call a tool and return the text content."""
        if not self.session_initialized:
            await self.initialize()
            
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
    
    async def is_service_available(self) -> bool:
        """Check if the RegonAPI service is available."""
        try:
            status = await self.call_tool("regon_get_service_status")
            return "Available" in status or "1" in status
        except Exception:
            return False
    
    async def search_entity_comprehensive(self, identifier: str, identifier_type: str) -> Optional[BusinessEntity]:
        """Perform a comprehensive search for a business entity."""
        try:
            if identifier_type == "nip":
                result = await self.call_tool("regon_search_by_nip", {"nip": identifier})
            elif identifier_type == "regon":
                result = await self.call_tool("regon_search_by_regon", {"regon": identifier})
            elif identifier_type == "krs":
                result = await self.call_tool("regon_search_by_krs", {"krs": identifier})
            else:
                return None
            
            if "No results found" in result or "Error:" in result:
                return None
            
            # Parse result to extract basic entity information
            # This is a simplified parser - in practice you'd want more robust parsing
            lines = result.split('\n')
            entity_data = {}
            
            for line in lines:
                if ':' in line:
                    key, value = line.split(':', 1)
                    entity_data[key.strip()] = value.strip()
            
            # Create BusinessEntity object
            return BusinessEntity(
                name=entity_data.get('Nazwa', 'Unknown'),
                nip=entity_data.get('Nip', ''),
                regon=entity_data.get('Regon', ''),
                krs=entity_data.get('Krs', None),
                entity_type=entity_data.get('Typ', None),
                address=entity_data.get('Adres', None)
            )
            
        except Exception as e:
            print(f"Error searching for {identifier}: {e}")
            return None
    
    async def get_entity_reports(self, regon: str, report_types: List[str]) -> Dict[str, str]:
        """Get multiple reports for an entity."""
        reports = {}
        
        for report_type in report_types:
            try:
                result = await self.call_tool("regon_get_full_report", {
                    "regon": regon,
                    "report_name": report_type,
                    "strict": True
                })
                
                if "No report data" not in result and "Error:" not in result:
                    reports[report_type] = result
                else:
                    reports[report_type] = f"No data available: {result}"
                    
            except Exception as e:
                reports[report_type] = f"Error: {e}"
        
        return reports


async def main():
    """
    Advanced example demonstrating complex business workflows.
    
    This example shows how to build more sophisticated applications
    using the RegonAPI MCP Server with proper error handling and
    business logic.
    """
    
    print("RegonAPI MCP Server - Advanced Usage Example")
    print("=" * 50)
    print("Demonstrating advanced patterns and workflows")
    print("=" * 50)
    
    # Sample companies for analysis
    companies = [
        ("7342867148", "nip", "CD Projekt"),       # Gaming company
        ("5260255203", "nip", "PKO Bank Polski"),  # Bank
        ("0000006865", "krs", "CD Projekt KRS"),   # Same company by KRS
        ("492707333", "regon", "CD Projekt REGON") # Same company by REGON
    ]
    
    client = AdvancedMCPClient()
    
    try:
        # Start the server
        await client.start_server()
        
        # Initialize the session
        await client.initialize()
        
        print("\n🔍 Service Health Check")
        print("=" * 25)
        
        if await client.is_service_available():
            print("✅ RegonAPI service is available")
        else:
            print("❌ RegonAPI service is unavailable")
            return
        
        print("\n🏢 Company Analysis Workflow")
        print("=" * 32)
        
        entities = []
        
        # Step 1: Search for all companies
        print("📋 Step 1: Searching for companies...")
        for identifier, id_type, name in companies:
            print(f"   🔍 Searching for {name} ({id_type}: {identifier})")
            
            entity = await client.search_entity_comprehensive(identifier, id_type)
            if entity:
                entities.append(entity)
                print(f"   ✅ Found: {entity.name}")
            else:
                print(f"   ❌ Not found: {name}")
        
        print(f"\n📊 Found {len(entities)} entities")
        
        # Step 2: Analyze each entity
        print("\n📋 Step 2: Detailed entity analysis...")
        
        for i, entity in enumerate(entities, 1):
            print(f"\n🏢 Entity {i}: {entity.name}")
            print("-" * (len(entity.name) + 15))
            print(f"   NIP: {entity.nip}")
            print(f"   REGON: {entity.regon}")
            print(f"   KRS: {entity.krs or 'N/A'}")
            print(f"   Type: {entity.entity_type or 'Unknown'}")
            
            # Get basic reports
            if entity.regon:
                print(f"\n   📄 Fetching reports for {entity.name}...")
                
                basic_reports = ["BIR11OsPrawna", "BIR11TypPodmiotu"]
                reports = await client.get_entity_reports(entity.regon, basic_reports)
                
                for report_name, report_data in reports.items():
                    print(f"\n   📋 Report: {report_name}")
                    if len(report_data) > 200:  # Truncate long reports
                        print(f"   {report_data[:200]}...")
                    else:
                        print(f"   {report_data}")
        
        print("\n🔍 Cross-Reference Analysis")
        print("=" * 30)
        
        # Step 3: Find duplicate entities (same company with different identifiers)
        print("🔗 Checking for duplicate entities...")
        
        regon_groups = {}
        for entity in entities:
            if entity.regon in regon_groups:
                regon_groups[entity.regon].append(entity)
            else:
                regon_groups[entity.regon] = [entity]
        
        for regon, group in regon_groups.items():
            if len(group) > 1:
                print(f"\n🔗 Found duplicate entity (REGON: {regon}):")
                for entity in group:
                    print(f"   * {entity.name} (NIP: {entity.nip}, KRS: {entity.krs})")
        
        print("\n🔍 Bulk Operations Demo")
        print("=" * 25)
        
        # Step 4: Demonstrate bulk operations
        all_nips = [entity.nip for entity in entities if entity.nip]
        if all_nips:
            print(f"📋 Performing bulk search for {len(all_nips)} NIPs...")
            bulk_result = await client.call_tool("regon_search_multiple_nips", {"nips": all_nips})
            print("✅ Bulk search completed")
            
            # Count results
            result_count = bulk_result.count("--- Result")
            print(f"📊 Bulk search returned {result_count} results")
        
        print("\n🔍 Performance Monitoring")
        print("=" * 27)
        
        # Step 5: Performance and monitoring
        start_time = datetime.now()
        
        # Perform a series of operations to test performance
        test_operations = [
            ("regon_get_service_status", {}),
            ("regon_get_data_status", {}),
            ("regon_get_last_error_code", {}),
            ("regon_search_by_nip", {"nip": "7342867148"}),
        ]
        
        for tool_name, args in test_operations:
            op_start = datetime.now()
            result = await client.call_tool(tool_name, args)
            op_time = (datetime.now() - op_start).total_seconds()
            print(f"   ⏱️  {tool_name}: {op_time:.2f}s")
        
        total_time = (datetime.now() - start_time).total_seconds()
        print(f"\n📊 Total analysis time: {total_time:.2f} seconds")
        
        print("\n🔍 Business Intelligence Summary")
        print("=" * 35)
        
        # Step 6: Generate business intelligence summary
        unique_entities = len(set(entity.regon for entity in entities))
        legal_entities = sum(1 for entity in entities if entity.krs)
        
        print(f"📊 Analysis Summary:")
        print(f"   * Total entities analyzed: {len(entities)}")
        print(f"   * Unique entities: {unique_entities}")
        print(f"   * Legal entities (with KRS): {legal_entities}")
        print(f"   * Individual entrepreneurs: {len(entities) - legal_entities}")
        
        print(f"\n💡 Recommendations:")
        if unique_entities < len(entities):
            print(f"   * Found duplicate entities - consider data deduplication")
        print(f"   * Use bulk operations for better performance")
        print(f"   * Monitor service status before critical operations")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
    
    finally:
        # Clean up
        await client.stop_server()
    
    print(f"\n✅ Advanced example completed!")
    print("\n" + "=" * 50)
    print("💡 This example demonstrates:")
    print("   * Complex business workflows")
    print("   * Error handling and resilience")
    print("   * Performance monitoring")
    print("   * Data analysis and cross-referencing")
    print("   * Business intelligence generation")


if __name__ == "__main__":
    print("Starting RegonAPI MCP Server Advanced Example...")
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⏹️  Example interrupted by user")
    except Exception as e:
        print(f"\n❌ Example failed: {e}")
        sys.exit(1)
