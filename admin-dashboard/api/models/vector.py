from sqlalchemy import Column, Integer, String, Float, DateTime, Text, ForeignKey, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class VectorSpace(Base):
    __tablename__ = "vector_spaces"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    algorithm = Column(String(50), nullable=False)  # 'tfidf', 'word2vec', 'bert'
    dimensions = Column(Integer, nullable=False)
    parameters = Column(JSON, nullable=True)  # Store algorithm parameters
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    quote_count = Column(Integer, default=0)
    
    def __repr__(self):
        return f"<VectorSpace(name='{self.name}', algorithm='{self.algorithm}', dimensions={self.dimensions})>"

class QuoteVector(Base):
    __tablename__ = "quote_vectors"

    id = Column(Integer, primary_key=True, index=True)
    quote_id = Column(Integer, ForeignKey("quotes.id"), nullable=False)
    vector_space_id = Column(Integer, ForeignKey("vector_spaces.id"), nullable=False)
    
    # Vector embedding (stored as JSON array)
    embedding = Column(JSON, nullable=False)
    
    # Reduced dimensions for visualization (2D/3D)
    x_coord = Column(Float, nullable=True)
    y_coord = Column(Float, nullable=True)
    z_coord = Column(Float, nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    quote = relationship("Quote", backref="vectors")
    vector_space = relationship("VectorSpace", backref="quote_vectors")
    
    def __repr__(self):
        return f"<QuoteVector(quote_id={self.quote_id}, space_id={self.vector_space_id})>"
