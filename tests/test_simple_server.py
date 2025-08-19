#!/usr/bin/env python3
"""
Simplified RegonAPI MCP Server WITHOUT fix_polish_encoding function
to test if PYTHONIOENCODING alone solves the encoding issues.
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from RegonAPI import RegonAPI
from RegonAPI.exceptions import ApiError

# Set PYTHONIOENCODING environment variable
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

# Global configuration
config = {'production_mode': False, 'log_level': 'INFO'}

def setup_logging(log_level: str):
    """Configure logging."""
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)
    logging.basicConfig(
        level=numeric_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def get_api_key(production_mode: bool) -> str:
    """Get appropriate API key."""
    if production_mode:
        api_key = os.getenv("API_KEY")
        if not api_key:
            test_key = os.getenv("TEST_API_KEY")
            if test_key:
                return test_key
            else:
                raise ValueError("Production mode requires API_KEY")
        return api_key
    else:
        return os.getenv("TEST_API_KEY", "abcde12345abcde12345")

def initialize_regon_api(production_mode: bool) -> RegonAPI:
    """Initialize RegonAPI instance."""
    global regon_api
    
    if regon_api is None:
        api_key = get_api_key(production_mode)
        regon_api = RegonAPI(
            bir_version="bir1.1",
            is_production=production_mode,
            timeout=30,
            operation_timeout=30
        )
        regon_api.authenticate(key=api_key)
        logger.info(f"RegonAPI initialized in {'production' if production_mode else 'test'} mode")
    
    return regon_api

# Initialize the MCP server
server = Server("regon-api-simple")

@server.list_tools()
async def handle_list_tools() -> List[Tool]:
    """List available tools."""
    return [
        Tool(
            name="regon_search_by_nip",
            description="Search for Polish companies by NIP (tax number)",
            inputSchema={
                "type": "object",
                "properties": {
                    "nip": {
                        "type": "string",
                        "description": "10-digit NIP number (e.g., '7342867148')"
                    }
                },
                "required": ["nip"]
            }
        ),
        Tool(
            name="regon_search_by_krs",
            description="Search for Polish companies by KRS (court register) number",
            inputSchema={
                "type": "object",
                "properties": {
                    "krs": {
                        "type": "string",
                        "description": "10-digit KRS number with leading zeros (e.g., '0000006865')"
                    }
                },
                "required": ["krs"]
            }
        ),
        Tool(
            name="regon_get_service_status",
            description="Check the status of the REGON service",
            inputSchema={
                "type": "object",
                "properties": {},
                "additionalProperties": False
            }
        )
    ]

@server.call_tool()
async def handle_call_tool(name: str, arguments: Dict[str, Any]) -> List[TextContent]:
    """Handle tool calls WITHOUT any encoding fixes."""
    try:
        api = initialize_regon_api(config['production_mode'])
        
        if name == "regon_search_by_nip":
            nip = arguments["nip"]
            logger.debug(f"Searching by NIP: {nip}")
            result = api.searchData(nip=nip)
            # NO ENCODING FIX - return raw result
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
            
        elif name == "regon_search_by_krs":
            krs = arguments["krs"]
            logger.debug(f"Searching by KRS: {krs}")
            result = api.searchData(krs=krs)
            # NO ENCODING FIX - return raw result
            return [TextContent(type="text", text=json.dumps(result, indent=2, ensure_ascii=False))]
            
        elif name == "regon_get_service_status":
            logger.debug("Getting service status")
            status_code, status_message = api.get_service_status()
            return [TextContent(type="text", text=f"Service Status Code: {status_code}, Status Message: {status_message}")]
            
        else:
            error_msg = f"Unknown tool: {name}"
            logger.error(error_msg)
            return [TextContent(type="text", text=error_msg)]
            
    except Exception as e:
        error_msg = f"Error in {name}: {str(e)}"
        logger.error(error_msg, exc_info=True)
        return [TextContent(type="text", text=error_msg)]

async def main():
    """Main entry point."""
    global logger, config
    
    logger = setup_logging('INFO')
    logger.info("Starting simplified RegonAPI MCP Server (NO encoding fixes)")
    
    try:
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
    regon_api: Optional[RegonAPI] = None
    logger = None
    asyncio.run(main())
