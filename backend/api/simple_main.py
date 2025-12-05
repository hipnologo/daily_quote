#!/usr/bin/env python3
"""
Simplified Daily Quote Admin API for testing
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import os
import sys
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

app = FastAPI(
    title="Daily Quote Admin API",
    description="Admin dashboard API for Daily Quote management",
    version="2.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base path for quote files
QUOTES_BASE_PATH = Path("../../")

@app.get("/")
async def root():
    return {"message": "Daily Quote Admin API v2.0", "status": "running"}

@app.get("/api/health")
async def health_check():
    return {
        "status": "healthy",
        "version": "2.0.0",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/api/quotes/stats")
async def get_quote_stats():
    """Get quote statistics"""
    try:
        total_quotes = 0
        languages = set()
        authors = set()
        categories = set()
        
        # Count quotes from all files
        patterns = ["quotes.txt", "quotes_*.txt"]
        for pattern in patterns:
            for file_path in QUOTES_BASE_PATH.glob(pattern):
                if file_path.is_file():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            lines = [line.strip() for line in f if line.strip()]
                            total_quotes += len(lines)
                            
                        # Extract language from filename
                        if file_path.name == "quotes.txt":
                            languages.add("en")
                        elif "_" in file_path.name:
                            lang = file_path.name.split("_")[1].split(".")[0]
                            languages.add(lang)
                    except Exception as e:
                        print(f"Error reading {file_path}: {e}")
        
        return {
            "total_quotes": total_quotes,
            "languages": len(languages),
            "authors": max(10, total_quotes // 50),  # Estimate authors
            "categories": max(5, total_quotes // 100)  # Estimate categories
        }
    except Exception as e:
        return {
            "total_quotes": 0,
            "languages": 0,
            "authors": 0,
            "categories": 0
        }

@app.get("/api/quotes/files")
async def list_quote_files():
    """List all quote files"""
    files = []
    patterns = ["quotes.txt", "quotes_*.txt"]
    
    for pattern in patterns:
        for file_path in QUOTES_BASE_PATH.glob(pattern):
            if file_path.is_file():
                try:
                    stat = file_path.stat()
                    with open(file_path, 'r', encoding='utf-8') as f:
                        lines = sum(1 for line in f if line.strip())
                    
                    files.append({
                        "filename": file_path.name,
                        "path": str(file_path),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                        "lines": lines
                    })
                except Exception as e:
                    print(f"Error reading {file_path}: {e}")
                    continue
    
    return {"files": sorted(files, key=lambda x: x["filename"])}

@app.get("/api/quotes/files/{filename}")
async def read_quote_file(filename: str):
    """Read content of a quote file"""
    file_path = QUOTES_BASE_PATH / filename
    
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        quotes = [line.strip() for line in lines if line.strip()]
        
        return {
            "filename": filename,
            "quote_count": len(quotes),
            "quotes": quotes[:10],  # First 10 quotes for preview
            "total_lines": len(lines)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error reading file: {str(e)}")

@app.get("/api/system/info")
async def system_info():
    """Get basic system information"""
    try:
        import psutil
        
        return {
            "cpu_usage": psutil.cpu_percent(interval=1),
            "memory_usage": psutil.virtual_memory().percent,
            "disk_usage": psutil.disk_usage('/').percent if os.name != 'nt' else psutil.disk_usage('C:').percent,
            "python_version": sys.version,
            "platform": sys.platform
        }
    except ImportError:
        return {
            "python_version": sys.version,
            "platform": sys.platform,
            "note": "psutil not available for detailed system info"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
