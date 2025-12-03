from sqlalchemy.orm import Session
from sqlalchemy import func, select
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import asyncio
from fastapi import BackgroundTasks
import os
import sys

# Add backend path for sentiment analysis
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from models.quote import Quote, QuoteLanguage
from models.sentiment import SentimentResult

# Map language strings to QuoteLanguage enum
LANGUAGE_STRING_MAP = {
    "en": QuoteLanguage.ENGLISH,
    "es": QuoteLanguage.SPANISH,
    "pt": QuoteLanguage.PORTUGUESE,
    "it": QuoteLanguage.ITALIAN,
}

class SentimentService:
    # Class-level job tracking (shared across all instances)
    jobs: Dict[str, Dict[str, Any]] = {}
    
    def __init__(self, db: Session):
        self.db = db
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get sentiment analysis statistics"""
        total_analyzed = self.db.query(SentimentResult).count()
        
        if total_analyzed == 0:
            return {
                "total_analyzed": 0,
                "positive_count": 0,
                "negative_count": 0,
                "neutral_count": 0,
                "average_compound": 0.0,
                "distribution": {"positive": 0.0, "negative": 0.0, "neutral": 0.0}
            }
        
        # Get sentiment counts by calculating from compound_score
        positive_count = self.db.query(SentimentResult).filter(
            SentimentResult.compound_score >= 0.05
        ).count()
        negative_count = self.db.query(SentimentResult).filter(
            SentimentResult.compound_score <= -0.05
        ).count()
        neutral_count = total_analyzed - positive_count - negative_count
        
        # Get average compound score
        avg_compound = self.db.query(func.avg(SentimentResult.compound_score)).scalar() or 0.0
        
        # Calculate distribution
        distribution = {
            "positive": positive_count / total_analyzed * 100,
            "negative": negative_count / total_analyzed * 100,
            "neutral": neutral_count / total_analyzed * 100
        }
        
        return {
            "total_analyzed": total_analyzed,
            "positive_count": positive_count,
            "negative_count": negative_count,
            "neutral_count": neutral_count,
            "average_compound": round(avg_compound, 3),
            "distribution": distribution
        }
    
    async def start_analysis(self, background_tasks: BackgroundTasks, 
                           language: str = "en", force_reanalyze: bool = False) -> str:
        """Start sentiment analysis job"""
        job_id = str(uuid.uuid4())
        
        SentimentService.jobs[job_id] = {
            "status": "running",
            "progress": 0.0,
            "message": "Starting sentiment analysis...",
            "created_at": datetime.utcnow()
        }
        
        background_tasks.add_task(
            self._run_sentiment_analysis, job_id, language, force_reanalyze
        )
        
        return job_id
    
    async def _run_sentiment_analysis(self, job_id: str, language: str, force_reanalyze: bool):
        """Background task to run sentiment analysis"""
        try:
            # Get quotes that need analysis
            query = self.db.query(Quote)
            
            # Filter by language if not "all"
            if language != "all":
                lang_enum = LANGUAGE_STRING_MAP.get(language)
                if lang_enum:
                    query = query.filter(Quote.language == lang_enum)
            
            if not force_reanalyze:
                # Only analyze quotes without sentiment results
                analyzed_quote_ids = select(SentimentResult.quote_id)
                query = query.filter(~Quote.id.in_(analyzed_quote_ids))
            
            quotes = query.all()
            total_quotes = len(quotes)
            
            if total_quotes == 0:
                SentimentService.jobs[job_id] = {
                    "status": "completed",
                    "progress": 100.0,
                    "message": "No quotes to analyze",
                    "completed_at": datetime.utcnow()
                }
                return
            
            # Import sentiment analysis (lazy import to avoid startup issues)
            try:
                from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
                analyzer = SentimentIntensityAnalyzer()
            except ImportError:
                SentimentService.jobs[job_id] = {
                    "status": "failed",
                    "progress": 0.0,
                    "message": "VADER sentiment analyzer not available",
                    "error": "Missing vaderSentiment dependency"
                }
                return
            
            # Process quotes
            for i, quote in enumerate(quotes):
                try:
                    # Analyze sentiment
                    scores = analyzer.polarity_scores(quote.text)
                    
                    # Delete existing result if force reanalyze
                    if force_reanalyze:
                        existing = self.db.query(SentimentResult).filter(
                            SentimentResult.quote_id == quote.id
                        ).first()
                        if existing:
                            self.db.delete(existing)
                    
                    # Create new sentiment result
                    sentiment_result = SentimentResult(
                        quote_id=quote.id,
                        positive_score=scores['pos'],
                        negative_score=scores['neg'],
                        neutral_score=scores['neu'],
                        compound_score=scores['compound']
                    )
                    
                    self.db.add(sentiment_result)
                    
                    # Update progress
                    progress = (i + 1) / total_quotes * 100
                    SentimentService.jobs[job_id]["progress"] = progress
                    SentimentService.jobs[job_id]["message"] = f"Analyzed {i + 1}/{total_quotes} quotes"
                    
                    # Commit every 10 quotes
                    if (i + 1) % 10 == 0:
                        self.db.commit()
                
                except Exception as e:
                    print(f"Error analyzing quote {quote.id}: {e}")
                    continue
            
            # Final commit
            self.db.commit()
            
            SentimentService.jobs[job_id] = {
                "status": "completed",
                "progress": 100.0,
                "message": f"Successfully analyzed {total_quotes} quotes",
                "completed_at": datetime.utcnow()
            }
            
        except Exception as e:
            SentimentService.jobs[job_id] = {
                "status": "failed",
                "progress": 0.0,
                "message": f"Analysis failed: {str(e)}",
                "error": str(e)
            }
    
    async def get_job_status(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get job status"""
        return SentimentService.jobs.get(job_id)
    
    async def get_distribution(self, language: Optional[str] = None, 
                             author: Optional[str] = None) -> Dict[str, Any]:
        """Get sentiment distribution with filters"""
        query = self.db.query(SentimentResult).join(Quote)
        
        if language:
            lang_enum = LANGUAGE_STRING_MAP.get(language)
            if lang_enum:
                query = query.filter(Quote.language == lang_enum)
        if author:
            query = query.filter(Quote.author.ilike(f"%{author}%"))
        
        total = query.count()
        
        if total == 0:
            return {"distribution": {}, "total": 0, "counts": {}}
        
        # Count by sentiment using compound_score thresholds
        positive_count = query.filter(SentimentResult.compound_score >= 0.05).count()
        negative_count = query.filter(SentimentResult.compound_score <= -0.05).count()
        neutral_count = total - positive_count - negative_count
        
        sentiment_counts = {
            "positive": positive_count, 
            "negative": negative_count, 
            "neutral": neutral_count
        }
        
        distribution = {
            label: count / total * 100 
            for label, count in sentiment_counts.items()
        }
        
        return {
            "distribution": distribution,
            "total": total,
            "counts": sentiment_counts
        }
    
    async def get_quotes_by_sentiment(self, sentiment_type: str, skip: int = 0, 
                                    limit: int = 50, language: Optional[str] = None):
        """Get quotes filtered by sentiment type"""
        query = self.db.query(Quote, SentimentResult).join(SentimentResult)
        
        # Filter by sentiment type using compound_score thresholds
        if sentiment_type == "positive":
            query = query.filter(SentimentResult.compound_score >= 0.05)
        elif sentiment_type == "negative":
            query = query.filter(SentimentResult.compound_score <= -0.05)
        else:  # neutral
            query = query.filter(
                SentimentResult.compound_score > -0.05,
                SentimentResult.compound_score < 0.05
            )
        
        if language:
            lang_enum = LANGUAGE_STRING_MAP.get(language)
            if lang_enum:
                query = query.filter(Quote.language == lang_enum)
        
        results = query.offset(skip).limit(limit).all()
        
        quotes = []
        for quote, sentiment in results:
            quotes.append({
                "id": quote.id,
                "text": quote.text,
                "author": quote.author,
                "language": quote.language,
                "sentiment_scores": {
                    "positive": sentiment.positive_score,
                    "negative": sentiment.negative_score,
                    "neutral": sentiment.neutral_score,
                    "compound": sentiment.compound_score
                }
            })
        
        return {"quotes": quotes, "total": len(quotes)}
