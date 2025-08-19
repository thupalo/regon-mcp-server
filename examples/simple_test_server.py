#!/usr/bin/env python3
"""
Simple MCP Server Example to test basic functionality.
"""

import asyncio
import logging
from typing import Any, Dict, List

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize the MCP server
server = Server("simple-test")

@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available tools."""
    logger.debug("list_tools called")
    return [
        Tool(
            name="hello",
            description="Say hello to someone",
            inputSchema={
                "type": "object",
                "properties": {
                    "name": {
                        "type": "string",
                        "description": "Name to say hello to"
                    }
                },
                "required": ["name"]
            }
        )
    ]

@server.call_tool()
async def call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls."""
    logger.debug(f"call_tool called: {name} with {arguments}")
    
    if name == "hello":
        person_name = arguments.get("name", "World")
        content = f"Hello, {person_name}!"
    else:
        content = f"Unknown tool: {name}"
    
    return [TextContent(type="text", text=content)]

async def main():
    """Main server function."""
    try:
        logger.info("Starting Simple Test MCP Server...")
        
        # Run the server
        async with stdio_server() as (read_stream, write_stream):
            await server.run(
                read_stream,
                write_stream,
                server.create_initialization_options()
            )
    except Exception as e:
        logger.error(f"Server startup failed: {e}", exc_info=True)
        raise

if __name__ == "__main__":
    asyncio.run(main())
