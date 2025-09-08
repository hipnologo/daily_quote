#!/usr/bin/env python3
"""
Test script to verify API setup
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("Testing imports...")
        
        # Test database setup
        from database import engine, SessionLocal, Base
        print("✅ Database modules imported successfully")
        
        # Test models
        from models import User, Quote, SentimentResult, VectorSpace, QuoteVector
        print("✅ Models imported successfully")
        
        # Test routers
        from routers import quotes, auth, sentiment, vectors, system, files
        print("✅ Routers imported successfully")
        
        # Test services
        from services.auth_service import AuthService
        from services.quote_service import QuoteService
        from services.sentiment_service import SentimentService
        from services.vector_service import VectorService
        from services.system_service import SystemService
        from services.file_service import FileService
        print("✅ Services imported successfully")
        
        # Test utils
        from utils.auth import get_password_hash, verify_password
        print("✅ Auth utilities imported successfully")
        
        print("\n🎉 All imports successful! API structure is ready.")
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_database_creation():
    """Test database table creation"""
    try:
        print("\nTesting database setup...")
        from database import engine, Base
        
        # Create tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database tables created successfully")
        
        return True
    except Exception as e:
        print(f"❌ Database error: {e}")
        return False

def main():
    """Main test function"""
    print("🧪 Testing Daily Quote Admin API Setup\n")
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    # Test database
    if not test_database_creation():
        success = False
    
    if success:
        print("\n✅ Setup test completed successfully!")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your settings")
        print("2. Run: python start.py (to create admin user)")
        print("3. Run: uvicorn main:app --reload (to start the API)")
        print("4. Visit: http://localhost:8000/docs (for API documentation)")
    else:
        print("\n❌ Setup test failed. Please check the errors above.")

if __name__ == "__main__":
    main()
