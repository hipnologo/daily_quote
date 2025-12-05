from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class SentimentResult(Base):
    __tablename__ = "sentiment_results"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    
    # VADER sentiment scores
    positive_score = Column(Float, nullable=False)
    negative_score = Column(Float, nullable=False)
    neutral_score = Column(Float, nullable=False)
    compound_score = Column(Float, nullable=False)
    
    # Analysis metadata
    analyzer_version = Column(String(50), default="VADER")
    processed_at = Column(DateTime(timezone=True), server_default=func.now())
    processing_time_ms = Column(Float, nullable=True)
    
    # Relationship
    quote = relationship("Quote", backref="sentiment_results")
    
    def __repr__(self):
        return f"<SentimentResult(quote_id={self.quote_id}, compound={self.compound_score})>"
    
    @property
    def sentiment_label(self):
        """Return sentiment label based on compound score"""
        if self.compound_score >= 0.05:
            return "positive"
        elif self.compound_score <= -0.05:
            return "negative"
        else:
            return "neutral"
