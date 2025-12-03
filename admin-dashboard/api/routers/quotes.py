from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from database import get_database
from models.quote import Quote, QuoteLanguage
from services.quote_service import QuoteService
from utils.auth import get_current_user

router = APIRouter()

# Pydantic models for request/response
class QuoteCreate(BaseModel):
    text: str
    author: str
    language: QuoteLanguage = QuoteLanguage.ENGLISH
    category: Optional[str] = None
    source: Optional[str] = None

class QuoteUpdate(BaseModel):
    text: Optional[str] = None
    author: Optional[str] = None
    category: Optional[str] = None
    verified: Optional[bool] = None

class QuoteResponse(BaseModel):
    id: int
    text: str
    author: str
    language: str
    category: Optional[str]
    source: Optional[str]
    verified: bool
    sentiment_label: Optional[str]
    created_at: datetime
    
    class Config:
        from_attributes = True

class QuoteStats(BaseModel):
    total_quotes: int
    by_language: dict
    by_sentiment: dict
    verified_count: int
    recent_additions: int

@router.get("/stats", response_model=QuoteStats)
async def get_quote_statistics(
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get comprehensive quote statistics"""
    service = QuoteService(db)
    return await service.get_statistics()

@router.get("/top-authors")
async def get_top_authors(
    limit: int = Query(10, ge=1, le=50),
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get top authors by quote count"""
    service = QuoteService(db)
    authors = await service.get_top_authors(limit)
    return {"authors": authors}

@router.get("/categories")
async def get_categories(
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get all categories with counts"""
    service = QuoteService(db)
    categories = await service.get_categories()
    return {"categories": categories}

@router.get("/", response_model=List[QuoteResponse])
async def list_quotes(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    language: Optional[QuoteLanguage] = None,
    sentiment: Optional[str] = Query(None, regex="^(positive|negative|neutral)$"),
    author: Optional[str] = None,
    verified: Optional[bool] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """List quotes with filtering and pagination"""
    service = QuoteService(db)
    return await service.list_quotes(
        skip=skip, 
        limit=limit,
        language=language,
        sentiment=sentiment,
        author=author,
        verified=verified,
        search=search
    )

@router.get("/{quote_id}", response_model=QuoteResponse)
async def get_quote(
    quote_id: int,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get a specific quote by ID"""
    service = QuoteService(db)
    quote = await service.get_quote(quote_id)
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    return quote

@router.post("/", response_model=QuoteResponse, status_code=status.HTTP_201_CREATED)
async def create_quote(
    quote_data: QuoteCreate,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Create a new quote"""
    service = QuoteService(db)
    return await service.create_quote(quote_data.dict())

@router.put("/{quote_id}", response_model=QuoteResponse)
async def update_quote(
    quote_id: int,
    quote_data: QuoteUpdate,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Update an existing quote"""
    service = QuoteService(db)
    quote = await service.update_quote(quote_id, quote_data.dict(exclude_unset=True))
    if not quote:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )
    return quote

@router.delete("/{quote_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_quote(
    quote_id: int,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Delete a quote"""
    service = QuoteService(db)
    success = await service.delete_quote(quote_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Quote not found"
        )

@router.post("/bulk-import")
async def bulk_import_quotes(
    file_content: str,
    language: QuoteLanguage = QuoteLanguage.ENGLISH,
    source: Optional[str] = None,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Bulk import quotes from text content"""
    service = QuoteService(db)
    result = await service.bulk_import(file_content, language, source)
    return {
        "imported": result["imported"],
        "skipped": result["skipped"],
        "errors": result["errors"]
    }

@router.get("/duplicates/find")
async def find_duplicates(
    threshold: float = Query(0.8, ge=0.1, le=1.0),
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Find potential duplicate quotes"""
    service = QuoteService(db)
    duplicates = await service.find_duplicates(threshold)
    return {"duplicates": duplicates}

@router.post("/duplicates/merge")
async def merge_duplicates(
    primary_id: int,
    duplicate_ids: List[int],
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Merge duplicate quotes into primary quote"""
    service = QuoteService(db)
    result = await service.merge_duplicates(primary_id, duplicate_ids)
    return {"merged": result}
