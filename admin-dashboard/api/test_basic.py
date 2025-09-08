#!/usr/bin/env python3
"""
Basic test to verify API components work
"""

import sys
import os
from pathlib import Path

def test_basic_setup():
    """Test basic setup without external dependencies"""
    print("🧪 Testing Daily Quote Admin API Basic Setup\n")
    
    # Test 1: Check if quote files exist
    print("1. Checking quote files...")
    quotes_path = Path("../../")
    quote_files = list(quotes_path.glob("quotes*.txt"))
    
    if quote_files:
        print(f"✅ Found {len(quote_files)} quote files:")
        for file in quote_files[:5]:  # Show first 5
            print(f"   - {file.name}")
        if len(quote_files) > 5:
            print(f"   ... and {len(quote_files) - 5} more")
    else:
        print("❌ No quote files found")
    
    # Test 2: Check Python version
    print(f"\n2. Python version: {sys.version}")
    if sys.version_info >= (3, 8):
        print("✅ Python version is compatible")
    else:
        print("❌ Python version too old (need 3.8+)")
    
    # Test 3: Test basic imports
    print("\n3. Testing basic imports...")
    try:
        import json
        import datetime
        print("✅ Standard library imports work")
    except ImportError as e:
        print(f"❌ Standard library import failed: {e}")
    
    # Test 4: Check if we can read a quote file
    print("\n4. Testing quote file reading...")
    if quote_files:
        try:
            with open(quote_files[0], 'r', encoding='utf-8') as f:
                lines = f.readlines()
            quotes = [line.strip() for line in lines if line.strip()]
            print(f"✅ Successfully read {len(quotes)} quotes from {quote_files[0].name}")
            if quotes:
                print(f"   Sample quote: {quotes[0][:50]}...")
        except Exception as e:
            print(f"❌ Error reading quote file: {e}")
    
    print("\n🎉 Basic setup test completed!")
    print("\nNext steps:")
    print("1. Install FastAPI: pip install fastapi uvicorn")
    print("2. Run API: python simple_main.py")
    print("3. Visit: http://localhost:8000/docs")

if __name__ == "__main__":
    test_basic_setup()
