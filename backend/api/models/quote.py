from sqlalchemy import Column, Integer, String, Text, DateTime, Boolean, Float, Enum
from sqlalchemy.sql import func
from database import Base
import enum

class QuoteLanguage(enum.Enum):
    ENGLISH = "en"
    SPANISH = "es"
    PORTUGUESE = "pt"
    ITALIAN = "it"

class Quote(Base):
    __tablename__ = "quotes"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(Text, nullable=False)
    author = Column(String(200), nullable=False)
    language = Column(Enum(QuoteLanguage), default=QuoteLanguage.ENGLISH)
    category = Column(String(100), nullable=True)
    source = Column(String(200), nullable=True)
    verified = Column(Boolean, default=False)
    
    # Sentiment scores (populated by sentiment analysis)
    sentiment_positive = Column(Float, nullable=True)
    sentiment_negative = Column(Float, nullable=True)
    sentiment_neutral = Column(Float, nullable=True)
    sentiment_compound = Column(Float, nullable=True)
    
    # Metadata
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    file_source = Column(String(100), nullable=True)  # e.g., "quotes.txt"
    line_number = Column(Integer, nullable=True)
    
    def __repr__(self):
        return f"<Quote(id={self.id}, author='{self.author}', language='{self.language}')>"
    
    @property
    def sentiment_label(self):
        """Return sentiment label based on compound score"""
        if self.sentiment_compound is None:
            return "unknown"
        elif self.sentiment_compound >= 0.05:
            return "positive"
        elif self.sentiment_compound <= -0.05:
            return "negative"
        else:
            return "neutral"
