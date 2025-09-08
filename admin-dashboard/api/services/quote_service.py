from sqlalchemy.orm import Session
from sqlalchemy import func, or_
from typing import List, Optional, Dict, Any
from models.quote import Quote, QuoteLanguage
from difflib import SequenceMatcher
import re

class QuoteService:
    def __init__(self, db: Session):
        self.db = db
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive quote statistics"""
        total = self.db.query(Quote).count()
        
        # By language
        lang_stats = self.db.query(
            Quote.language, func.count(Quote.id)
        ).group_by(Quote.language).all()
        
        # By sentiment
        sentiment_stats = {
            "positive": self.db.query(Quote).filter(Quote.sentiment_compound >= 0.05).count(),
            "negative": self.db.query(Quote).filter(Quote.sentiment_compound <= -0.05).count(),
            "neutral": self.db.query(Quote).filter(
                Quote.sentiment_compound > -0.05, Quote.sentiment_compound < 0.05
            ).count(),
            "unknown": self.db.query(Quote).filter(Quote.sentiment_compound.is_(None)).count()
        }
        
        verified = self.db.query(Quote).filter(Quote.verified == True).count()
        
        return {
            "total_quotes": total,
            "by_language": {lang.value: count for lang, count in lang_stats},
            "by_sentiment": sentiment_stats,
            "verified_count": verified,
            "recent_additions": 0  # TODO: implement recent count
        }
    
    async def list_quotes(
        self, skip: int = 0, limit: int = 100, 
        language: Optional[QuoteLanguage] = None,
        sentiment: Optional[str] = None,
        author: Optional[str] = None,
        verified: Optional[bool] = None,
        search: Optional[str] = None
    ) -> List[Quote]:
        """List quotes with filtering"""
        query = self.db.query(Quote)
        
        if language:
            query = query.filter(Quote.language == language)
        
        if sentiment:
            if sentiment == "positive":
                query = query.filter(Quote.sentiment_compound >= 0.05)
            elif sentiment == "negative":
                query = query.filter(Quote.sentiment_compound <= -0.05)
            elif sentiment == "neutral":
                query = query.filter(
                    Quote.sentiment_compound > -0.05, 
                    Quote.sentiment_compound < 0.05
                )
        
        if author:
            query = query.filter(Quote.author.ilike(f"%{author}%"))
        
        if verified is not None:
            query = query.filter(Quote.verified == verified)
        
        if search:
            query = query.filter(
                or_(
                    Quote.text.ilike(f"%{search}%"),
                    Quote.author.ilike(f"%{search}%")
                )
            )
        
        return query.offset(skip).limit(limit).all()
    
    async def get_quote(self, quote_id: int) -> Optional[Quote]:
        """Get quote by ID"""
        return self.db.query(Quote).filter(Quote.id == quote_id).first()
    
    async def create_quote(self, quote_data: Dict[str, Any]) -> Quote:
        """Create new quote"""
        quote = Quote(**quote_data)
        self.db.add(quote)
        self.db.commit()
        self.db.refresh(quote)
        return quote
    
    async def update_quote(self, quote_id: int, update_data: Dict[str, Any]) -> Optional[Quote]:
        """Update existing quote"""
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            return None
        
        for field, value in update_data.items():
            setattr(quote, field, value)
        
        self.db.commit()
        self.db.refresh(quote)
        return quote
    
    async def delete_quote(self, quote_id: int) -> bool:
        """Delete quote"""
        quote = self.db.query(Quote).filter(Quote.id == quote_id).first()
        if not quote:
            return False
        
        self.db.delete(quote)
        self.db.commit()
        return True
    
    async def bulk_import(self, content: str, language: QuoteLanguage, source: str = None) -> Dict[str, int]:
        """Bulk import quotes from text content"""
        lines = content.strip().split('\n')
        imported = 0
        skipped = 0
        errors = 0
        
        for line_num, line in enumerate(lines, 1):
            try:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                
                # Parse quote format: "Quote text" — Author
                match = re.match(r'^"(.+)"\s*[—–-]\s*(.+)$', line)
                if match:
                    text, author = match.groups()
                    
                    # Check for duplicates
                    existing = self.db.query(Quote).filter(
                        Quote.text == text.strip(),
                        Quote.author == author.strip()
                    ).first()
                    
                    if existing:
                        skipped += 1
                        continue
                    
                    quote = Quote(
                        text=text.strip(),
                        author=author.strip(),
                        language=language,
                        source=source,
                        file_source=source,
                        line_number=line_num
                    )
                    self.db.add(quote)
                    imported += 1
                else:
                    errors += 1
            
            except Exception:
                errors += 1
        
        self.db.commit()
        return {"imported": imported, "skipped": skipped, "errors": errors}
    
    async def find_duplicates(self, threshold: float = 0.8) -> List[Dict]:
        """Find potential duplicate quotes"""
        quotes = self.db.query(Quote).all()
        duplicates = []
        
        for i, quote1 in enumerate(quotes):
            for quote2 in quotes[i+1:]:
                similarity = SequenceMatcher(None, quote1.text, quote2.text).ratio()
                if similarity >= threshold:
                    duplicates.append({
                        "quote1": {"id": quote1.id, "text": quote1.text, "author": quote1.author},
                        "quote2": {"id": quote2.id, "text": quote2.text, "author": quote2.author},
                        "similarity": similarity
                    })
        
        return duplicates
    
    async def merge_duplicates(self, primary_id: int, duplicate_ids: List[int]) -> bool:
        """Merge duplicate quotes into primary quote"""
        primary = self.db.query(Quote).filter(Quote.id == primary_id).first()
        if not primary:
            return False
        
        # Delete duplicates
        self.db.query(Quote).filter(Quote.id.in_(duplicate_ids)).delete()
        self.db.commit()
        return True
