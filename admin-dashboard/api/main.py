from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
import re
from pathlib import Path
from dotenv import load_dotenv

from database import engine, SessionLocal, Base
from routers import quotes, auth, sentiment, vectors, system, files
from models import User, Quote, SentimentResult, VectorSpace
from models.user import UserRole
from models.quote import QuoteLanguage
from utils.auth import get_password_hash

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

# Language mapping for quote files
LANGUAGE_MAP = {
    "quotes.txt": QuoteLanguage.ENGLISH,
    "quotes_es.txt": QuoteLanguage.SPANISH,
    "quotes_pt.txt": QuoteLanguage.PORTUGUESE,
    "quotes_it.txt": QuoteLanguage.ITALIAN,
    "quotes_new.txt": QuoteLanguage.ENGLISH,
}

def parse_quote_line(line: str):
    """Parse a quote line in format: Quote text — Author"""
    line = line.strip()
    if not line or line.startswith('#'):
        return None
    
    # Try different dash separators (em dash, en dash, hyphen, and various unicode dashes)
    # Unicode em-dash is \u2014, en-dash is \u2013
    separators = [
        ' \u2014 ',  # space + em dash + space (most common)
        ' \u2013 ',  # space + en dash + space
        '\u2014 ',   # em dash + space
        ' \u2014',   # space + em dash
        ' — ',       # literal em dash with spaces
        ' – ',       # literal en dash with spaces
        ' - ',       # hyphen with spaces
        ' ― ',       # horizontal bar
    ]
    
    for separator in separators:
        if separator in line:
            parts = line.rsplit(separator, 1)
            if len(parts) == 2:
                text, author = parts
                text = text.strip().strip('"').strip("'")
                author = author.strip()
                if text and author and len(text) > 10:  # Basic validation
                    return text, author
    
    return None

def init_default_admin():
    """Create default admin user if none exists"""
    db = SessionLocal()
    try:
        # Check if any admin user exists
        admin_exists = db.query(User).filter(User.role == UserRole.ADMIN).first()
        if not admin_exists:
            default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin")
            admin = User(
                username="admin",
                email="admin@dailyquote.local",
                hashed_password=get_password_hash(default_password),
                role=UserRole.ADMIN,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"✓ Default admin user created (username: admin)")
    except Exception as e:
        print(f"Warning: Could not create default admin: {e}")
    finally:
        db.close()

def init_quotes_from_files():
    """Load quotes from text files into database on startup"""
    db = SessionLocal()
    try:
        # Check if quotes already loaded
        existing_count = db.query(Quote).count()
        if existing_count > 0:
            print(f"✓ Database already has {existing_count} quotes, skipping import")
            return
        
        # Path to quote files - check /app first (Docker), then parent directories (local dev)
        quotes_paths = [
            Path("/app"),  # Docker mounted files
            Path(__file__).parent.parent.parent,  # Local development
        ]
        
        quotes_path = None
        for p in quotes_paths:
            if (p / "quotes.txt").exists():
                quotes_path = p
                break
        
        if not quotes_path:
            print("✗ No quote files found, skipping import")
            return
        
        print(f"  Loading quotes from: {quotes_path}")
        total_imported = 0
        
        for filename, language in LANGUAGE_MAP.items():
            file_path = quotes_path / filename
            if not file_path.exists():
                print(f"  Skipping {filename} (not found)")
                continue
            
            try:
                # Read file with UTF-8 and replace invalid characters
                with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
                    content = f.read()
                
                lines = content.split('\n')
                imported = 0
                for line_num, line in enumerate(lines, 1):
                    parsed = parse_quote_line(line)
                    if parsed:
                        text, author = parsed
                        # Skip if already exists
                        exists = db.query(Quote).filter(
                            Quote.text == text,
                            Quote.author == author
                        ).first()
                        if not exists:
                            quote = Quote(
                                text=text,
                                author=author,
                                language=language,
                                file_source=filename,
                                line_number=line_num,
                                verified=True
                            )
                            db.add(quote)
                            imported += 1
                
                db.commit()
                total_imported += imported
                print(f"  ✓ Imported {imported} quotes from {filename}")
                
            except Exception as e:
                print(f"  ✗ Error importing {filename}: {e}")
                db.rollback()
        
        print(f"✓ Total quotes imported: {total_imported}")
        
    except Exception as e:
        print(f"Warning: Could not import quotes: {e}")
    finally:
        db.close()

# Initialize default admin user
init_default_admin()

# Initialize quotes from files
init_quotes_from_files()

app = FastAPI(
    title="Daily Quote Admin API",
    description="Backend API for Daily Quote project administration",
    version="2.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "https://inspirartransforma.com"],  # React dev servers
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Dependency to get database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Include routers
app.include_router(quotes.router, prefix="/api/quotes", tags=["quotes"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(sentiment.router, prefix="/api/sentiment", tags=["sentiment"])
app.include_router(vectors.router, prefix="/api/vectors", tags=["vectors"])
app.include_router(system.router, prefix="/api/system", tags=["system"])
app.include_router(files.router, prefix="/api/files", tags=["files"])

@app.get("/")
async def root():
    return {"message": "Daily Quote Admin API v2.0", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "database": "connected"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
