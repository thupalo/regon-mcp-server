#!/usr/bin/env python3
"""
Test script for RegonAPI MCP Server
This script tests basic functionality without running the full MCP server.
"""

import os
import sys
import logging
from dotenv import load_dotenv

# Add current directory to path
sys.path.insert(0, os.path.dirname(__file__))

from RegonAPI import RegonAPI
from RegonAPI.exceptions import ApiAuthenticationError

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_regon_api():
    """Test RegonAPI initialization and basic functionality."""
    
    # Load environment variables
    load_dotenv()
    
    # Get API key
    api_key = os.getenv("TEST_API_KEY") or os.getenv("API_KEY")
    if not api_key:
        logger.error("No API key found. Please set TEST_API_KEY or API_KEY in .env file")
        return False
    
    logger.info(f"Using API key: {api_key[:10]}...")
    
    try:
        # Initialize RegonAPI
        logger.info("Initializing RegonAPI...")
        api = RegonAPI(
            bir_version="bir1.1",
            is_production=False,  # Use test environment
            timeout=30,
            operation_timeout=30
        )
        
        # Authenticate
        logger.info("Authenticating...")
        api.authenticate(key=api_key)
        logger.info("Authentication successful!")
        
        # Test service status
        logger.info("Testing service status...")
        status_code, status_message = api.get_service_status()
        logger.info(f"Service Status: {status_code} - {status_message}")
        
        # Test data status
        logger.info("Testing data status...")
        data_status = api.get_data_status()
        logger.info(f"Data Status: {data_status}")
        
        # Test operations list
        logger.info("Getting available operations...")
        operations = api.get_operations()
        logger.info(f"Available operations: {len(operations)} operations found")
        
        # Test search (using test company CD Projekt)
        logger.info("Testing search by NIP...")
        test_nip = "7342867148"  # CD Projekt NIP
        results = api.searchData(nip=test_nip)
        if results:
            logger.info(f"Search successful! Found {len(results)} result(s)")
            for i, result in enumerate(results, 1):
                logger.info(f"Result {i}: {result.get('Nazwa', 'N/A')} (REGON: {result.get('Regon', 'N/A')})")
        else:
            logger.info("No results found for test search")
        
        logger.info("All tests passed successfully!")
        return True
        
    except ApiAuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        return False
    except Exception as e:
        logger.error(f"Test failed: {e}")
        return False

if __name__ == "__main__":
    print("RegonAPI MCP Server Test")
    print("=" * 40)
    
    success = test_regon_api()
    
    if success:
        print("\n✅ All tests passed! The MCP server should work correctly.")
        print("\nTo run the MCP server:")
        print("python regon_mcp_server.py")
    else:
        print("\n❌ Tests failed! Please check your configuration.")
        sys.exit(1)
