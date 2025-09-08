from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import os
from dotenv import load_dotenv

from database import engine, SessionLocal, Base
from routers import quotes, auth, sentiment, vectors, system, files
from models import User, Quote, SentimentResult, VectorSpace

# Load environment variables
load_dotenv()

# Create database tables
Base.metadata.create_all(bind=engine)

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
    allow_origins=["http://localhost:3000", "http://localhost:5173"],  # React dev servers
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
