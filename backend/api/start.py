#!/usr/bin/env python3
"""
Startup script for Daily Quote Admin API
Creates initial admin user and starts the server
"""

import asyncio
import os
import sys
from sqlalchemy.orm import Session
from getpass import getpass

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import engine, SessionLocal, Base
from models.user import User, UserRole
from services.auth_service import AuthService

def create_tables():
    """Create database tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Database tables created successfully")

async def create_admin_user():
    """Create initial admin user if none exists"""
    db = SessionLocal()
    try:
        auth_service = AuthService(db)
        
        # Check if any admin users exist
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        
        if admin_exists:
            print(f"✅ Admin user already exists: {admin_exists.username}")
            return
        
        print("\n🔧 Creating initial admin user...")
        username = input("Enter admin username: ").strip()
        email = input("Enter admin email: ").strip()
        
        while True:
            password = getpass("Enter admin password: ").strip()
            confirm_password = getpass("Confirm password: ").strip()
            
            if password == confirm_password:
                if len(password) < 8:
                    print("❌ Password must be at least 8 characters long")
                    continue
                break
            else:
                print("❌ Passwords don't match. Please try again.")
        
        # Create admin user
        user_data = {
            "username": username,
            "email": email,
            "password": password,
            "role": UserRole.ADMIN
        }
        
        admin_user = await auth_service.create_user(user_data)
        print(f"✅ Admin user created successfully: {admin_user.username}")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")
    finally:
        db.close()

def check_environment():
    """Check if required environment variables are set"""
    required_vars = ["SECRET_KEY"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Warning: Missing environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease create a .env file based on .env.example")
        return False
    
    return True

def main():
    """Main startup function"""
    print("🚀 Starting Daily Quote Admin API...")
    
    # Check environment
    if not check_environment():
        print("❌ Environment check failed")
        return
    
    # Create database tables
    create_tables()
    
    # Create admin user
    asyncio.run(create_admin_user())
    
    print("\n✅ Setup complete!")
    print("\nTo start the API server:")
    print("  uvicorn main:app --reload --host 0.0.0.0 --port 8000")
    print("\nAPI Documentation will be available at:")
    print("  http://localhost:8000/api/docs")

if __name__ == "__main__":
    main()
