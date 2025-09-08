from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel

from database import get_database
from services.sentiment_service import SentimentService
from utils.auth import get_current_user

router = APIRouter()

class SentimentStats(BaseModel):
    total_analyzed: int
    positive_count: int
    negative_count: int
    neutral_count: int
    average_compound: float
    distribution: Dict[str, float]

class SentimentJobResponse(BaseModel):
    job_id: str
    status: str
    progress: float
    message: str

@router.get("/stats", response_model=SentimentStats)
async def get_sentiment_statistics(
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get sentiment analysis statistics"""
    service = SentimentService(db)
    return await service.get_statistics()

@router.post("/analyze", response_model=SentimentJobResponse)
async def start_sentiment_analysis(
    background_tasks: BackgroundTasks,
    language: Optional[str] = Query("en", regex="^(en|es|pt|it)$"),
    force_reanalyze: bool = Query(False),
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Start sentiment analysis for quotes"""
    service = SentimentService(db)
    job_id = await service.start_analysis(
        background_tasks, language, force_reanalyze
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "progress": 0.0,
        "message": "Sentiment analysis job started"
    }

@router.get("/jobs/{job_id}", response_model=SentimentJobResponse)
async def get_job_status(
    job_id: str,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get sentiment analysis job status"""
    service = SentimentService(db)
    job_status = await service.get_job_status(job_id)
    
    if not job_status:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job_status

@router.get("/distribution")
async def get_sentiment_distribution(
    language: Optional[str] = Query(None, regex="^(en|es|pt|it)$"),
    author: Optional[str] = None,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get sentiment distribution with optional filters"""
    service = SentimentService(db)
    return await service.get_distribution(language, author)

@router.get("/quotes/{sentiment_type}")
async def get_quotes_by_sentiment(
    sentiment_type: str = Query(..., regex="^(positive|negative|neutral)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    language: Optional[str] = Query(None, regex="^(en|es|pt|it)$"),
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get quotes filtered by sentiment type"""
    service = SentimentService(db)
    return await service.get_quotes_by_sentiment(
        sentiment_type, skip, limit, language
    )
