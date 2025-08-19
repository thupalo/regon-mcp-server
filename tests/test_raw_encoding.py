#!/usr/bin/env python3
"""
Test script to check raw RegonAPI output without any encoding fixes
to determine if the issue is in Python I/O handling or the API data itself.
"""

import os
import sys
from dotenv import load_dotenv
from RegonAPI import RegonAPI

# Set PYTHONIOENCODING before any output
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Configure UTF-8 encoding for Windows console output
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

load_dotenv()

def test_raw_api_output():
    """Test raw RegonAPI output to see actual encoding issues."""
    
    print("Testing raw RegonAPI output...")
    print("=" * 50)
    
    try:
        # Initialize RegonAPI
        api_key = os.getenv("TEST_API_KEY", "abcde12345abcde12345")
        
        regon_api = RegonAPI(
            bir_version="bir1.1",
            is_production=False,
            timeout=30,
            operation_timeout=30
        )
        
        regon_api.authenticate(key=api_key)
        
        # Test search by NIP (CD Projekt)
        print("\n1. Testing search by NIP: 7342867148")
        result = regon_api.searchData(nip="7342867148")
        
        print("Raw result type:", type(result))
        print("Raw result:", result)
        
        if result and len(result) > 0:
            company = result[0]
            nazwa = company.get('Nazwa', '')
            gmina = company.get('Gmina', '')
            
            print(f"\nAnalyzing 'Nazwa' field:")
            print(f"  Value: '{nazwa}'")
            print(f"  Type: {type(nazwa)}")
            print(f"  Length: {len(nazwa)}")
            print(f"  Bytes: {nazwa.encode('utf-8') if isinstance(nazwa, str) else 'N/A'}")
            print(f"  Repr: {repr(nazwa)}")
            
            print(f"\nAnalyzing 'Gmina' field:")
            print(f"  Value: '{gmina}'")
            print(f"  Type: {type(gmina)}")
            print(f"  Length: {len(gmina)}")
            print(f"  Bytes: {gmina.encode('utf-8') if isinstance(gmina, str) else 'N/A'}")
            print(f"  Repr: {repr(gmina)}")
            
            # Check for specific characters
            print(f"\nCharacter analysis for 'Nazwa':")
            for i, char in enumerate(nazwa):
                if ord(char) > 127:  # Non-ASCII characters
                    print(f"  Position {i}: '{char}' (U+{ord(char):04X})")
                    
            print(f"\nCharacter analysis for 'Gmina':")
            for i, char in enumerate(gmina):
                if ord(char) > 127:  # Non-ASCII characters
                    print(f"  Position {i}: '{char}' (U+{ord(char):04X})")
            
        print("\n" + "=" * 50)
        print("Raw API test completed!")
        
    except Exception as e:
        print(f"Error during raw API test: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_raw_api_output()
