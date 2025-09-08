from fastapi import APIRouter, Depends, HTTPException, Query, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List, Optional, Dict
from pydantic import BaseModel

from database import get_database
from services.vector_service import VectorService
from utils.auth import get_current_user

router = APIRouter()

class VectorSpaceResponse(BaseModel):
    id: int
    name: str
    algorithm: str
    dimensions: int
    quote_count: int
    created_at: str

class SimilarityResult(BaseModel):
    quote_id: int
    quote_text: str
    author: str
    similarity_score: float

@router.get("/spaces", response_model=List[VectorSpaceResponse])
async def list_vector_spaces(
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """List all vector spaces"""
    service = VectorService(db)
    return await service.list_vector_spaces()

@router.post("/generate")
async def generate_vectors(
    background_tasks: BackgroundTasks,
    algorithm: str = Query("tfidf", regex="^(tfidf|word2vec|bert)$"),
    max_features: int = Query(5000, ge=100, le=10000),
    language: str = Query("en", regex="^(en|es|pt|it)$"),
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Generate vectors for quotes"""
    service = VectorService(db)
    job_id = await service.generate_vectors(
        background_tasks, algorithm, max_features, language
    )
    
    return {
        "job_id": job_id,
        "status": "started",
        "message": "Vector generation started"
    }

@router.get("/similarity/{quote_id}")
async def find_similar_quotes(
    quote_id: int,
    limit: int = Query(10, ge=1, le=50),
    threshold: float = Query(0.5, ge=0.0, le=1.0),
    vector_space_id: Optional[int] = None,
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Find quotes similar to the given quote"""
    service = VectorService(db)
    similar_quotes = await service.find_similar_quotes(
        quote_id, limit, threshold, vector_space_id
    )
    
    return {"similar_quotes": similar_quotes}

@router.get("/clusters")
async def get_quote_clusters(
    vector_space_id: Optional[int] = None,
    n_clusters: int = Query(5, ge=2, le=20),
    db: Session = Depends(get_database),
    current_user = Depends(get_current_user)
):
    """Get quote clusters from vector analysis"""
    service = VectorService(db)
    clusters = await service.get_clusters(vector_space_id, n_clusters)
    
    return {"clusters": clusters}
