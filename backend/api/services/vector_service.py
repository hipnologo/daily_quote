from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import numpy as np
from fastapi import BackgroundTasks
import os
import sys

# Add backend path for vector operations
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..', 'backend'))

from models.quote import Quote
from models.vector import VectorSpace, QuoteVector

class VectorService:
    def __init__(self, db: Session):
        self.db = db
        self.jobs = {}  # In-memory job tracking
    
    async def list_vector_spaces(self) -> List[Dict[str, Any]]:
        """List all vector spaces"""
        spaces = self.db.query(VectorSpace).all()
        
        result = []
        for space in spaces:
            quote_count = self.db.query(QuoteVector).filter(
                QuoteVector.vector_space_id == space.id
            ).count()
            
            result.append({
                "id": space.id,
                "name": space.name,
                "algorithm": space.algorithm,
                "dimensions": space.dimensions,
                "quote_count": quote_count,
                "created_at": space.created_at.isoformat()
            })
        
        return result
    
    async def generate_vectors(self, background_tasks: BackgroundTasks,
                             algorithm: str = "tfidf", max_features: int = 5000,
                             language: str = "en") -> str:
        """Start vector generation job"""
        job_id = str(uuid.uuid4())
        
        self.jobs[job_id] = {
            "status": "running",
            "progress": 0.0,
            "message": "Starting vector generation...",
            "created_at": datetime.utcnow()
        }
        
        background_tasks.add_task(
            self._run_vector_generation, job_id, algorithm, max_features, language
        )
        
        return job_id
    
    async def _run_vector_generation(self, job_id: str, algorithm: str, 
                                   max_features: int, language: str):
        """Background task to generate vectors"""
        try:
            # Get quotes for the specified language
            quotes = self.db.query(Quote).filter(Quote.language == language).all()
            
            if not quotes:
                self.jobs[job_id] = {
                    "status": "failed",
                    "progress": 0.0,
                    "message": f"No quotes found for language: {language}",
                    "error": "No data to process"
                }
                return
            
            # Create vector space
            space_name = f"{algorithm}_{language}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
            
            if algorithm == "tfidf":
                vectors, dimensions = await self._generate_tfidf_vectors(
                    quotes, max_features, job_id
                )
            elif algorithm == "word2vec":
                vectors, dimensions = await self._generate_word2vec_vectors(
                    quotes, job_id
                )
            elif algorithm == "bert":
                vectors, dimensions = await self._generate_bert_vectors(
                    quotes, job_id
                )
            else:
                raise ValueError(f"Unsupported algorithm: {algorithm}")
            
            # Create vector space record
            vector_space = VectorSpace(
                name=space_name,
                algorithm=algorithm,
                dimensions=dimensions,
                parameters={"max_features": max_features, "language": language}
            )
            
            self.db.add(vector_space)
            self.db.commit()
            self.db.refresh(vector_space)
            
            # Save quote vectors
            for i, (quote, vector) in enumerate(zip(quotes, vectors)):
                quote_vector = QuoteVector(
                    quote_id=quote.id,
                    vector_space_id=vector_space.id,
                    vector=vector.tolist() if isinstance(vector, np.ndarray) else vector
                )
                self.db.add(quote_vector)
                
                if (i + 1) % 50 == 0:
                    self.db.commit()
                    progress = (i + 1) / len(quotes) * 90  # 90% for vector generation
                    self.jobs[job_id]["progress"] = progress
                    self.jobs[job_id]["message"] = f"Saved {i + 1}/{len(quotes)} vectors"
            
            self.db.commit()
            
            # Generate visualization coordinates (t-SNE)
            await self._generate_visualization_coords(vector_space.id, vectors, job_id)
            
            self.jobs[job_id] = {
                "status": "completed",
                "progress": 100.0,
                "message": f"Generated {len(vectors)} vectors using {algorithm}",
                "vector_space_id": vector_space.id,
                "completed_at": datetime.utcnow()
            }
            
        except Exception as e:
            self.jobs[job_id] = {
                "status": "failed",
                "progress": 0.0,
                "message": f"Vector generation failed: {str(e)}",
                "error": str(e)
            }
    
    async def _generate_tfidf_vectors(self, quotes: List[Quote], max_features: int, job_id: str):
        """Generate TF-IDF vectors"""
        try:
            from sklearn.feature_extraction.text import TfidfVectorizer
            from sklearn.preprocessing import normalize
            
            texts = [quote.text for quote in quotes]
            
            self.jobs[job_id]["message"] = "Fitting TF-IDF vectorizer..."
            self.jobs[job_id]["progress"] = 10.0
            
            vectorizer = TfidfVectorizer(
                max_features=max_features,
                stop_words='english',
                ngram_range=(1, 2),
                min_df=2
            )
            
            vectors = vectorizer.fit_transform(texts)
            vectors = normalize(vectors, norm='l2')
            
            return vectors.toarray(), vectors.shape[1]
            
        except ImportError:
            raise ValueError("scikit-learn not available for TF-IDF generation")
    
    async def _generate_word2vec_vectors(self, quotes: List[Quote], job_id: str):
        """Generate Word2Vec vectors (simplified implementation)"""
        # This is a placeholder - in production, you'd use gensim or similar
        # For now, return random vectors as demonstration
        dimensions = 300
        vectors = np.random.rand(len(quotes), dimensions)
        return vectors, dimensions
    
    async def _generate_bert_vectors(self, quotes: List[Quote], job_id: str):
        """Generate BERT vectors (simplified implementation)"""
        # This is a placeholder - in production, you'd use transformers library
        # For now, return random vectors as demonstration
        dimensions = 768
        vectors = np.random.rand(len(quotes), dimensions)
        return vectors, dimensions
    
    async def _generate_visualization_coords(self, vector_space_id: int, vectors, job_id: str):
        """Generate t-SNE coordinates for visualization"""
        try:
            from sklearn.manifold import TSNE
            
            self.jobs[job_id]["message"] = "Generating visualization coordinates..."
            self.jobs[job_id]["progress"] = 95.0
            
            if isinstance(vectors, np.ndarray):
                vector_array = vectors
            else:
                vector_array = np.array(vectors)
            
            # Use t-SNE for 2D visualization
            tsne = TSNE(n_components=2, random_state=42, perplexity=min(30, len(vectors)-1))
            coords_2d = tsne.fit_transform(vector_array)
            
            # Update quote vectors with visualization coordinates
            quote_vectors = self.db.query(QuoteVector).filter(
                QuoteVector.vector_space_id == vector_space_id
            ).all()
            
            for i, qv in enumerate(quote_vectors):
                qv.visualization_x = float(coords_2d[i, 0])
                qv.visualization_y = float(coords_2d[i, 1])
            
            self.db.commit()
            
        except ImportError:
            print("scikit-learn not available for t-SNE visualization")
        except Exception as e:
            print(f"Error generating visualization coordinates: {e}")
    
    async def find_similar_quotes(self, quote_id: int, limit: int = 10, 
                                threshold: float = 0.5, 
                                vector_space_id: Optional[int] = None):
        """Find quotes similar to the given quote"""
        # Get the target quote vector
        query = self.db.query(QuoteVector).filter(QuoteVector.quote_id == quote_id)
        
        if vector_space_id:
            query = query.filter(QuoteVector.vector_space_id == vector_space_id)
        else:
            # Use the most recent vector space
            latest_space = self.db.query(VectorSpace).order_by(
                VectorSpace.created_at.desc()
            ).first()
            if not latest_space:
                return []
            query = query.filter(QuoteVector.vector_space_id == latest_space.id)
        
        target_vector = query.first()
        if not target_vector:
            return []
        
        # Get all other vectors in the same space
        other_vectors = self.db.query(QuoteVector, Quote).join(Quote).filter(
            QuoteVector.vector_space_id == target_vector.vector_space_id,
            QuoteVector.quote_id != quote_id
        ).all()
        
        # Calculate similarities (cosine similarity)
        target_vec = np.array(target_vector.vector)
        similarities = []
        
        for qv, quote in other_vectors:
            other_vec = np.array(qv.vector)
            similarity = np.dot(target_vec, other_vec) / (
                np.linalg.norm(target_vec) * np.linalg.norm(other_vec)
            )
            
            if similarity >= threshold:
                similarities.append({
                    "quote_id": quote.id,
                    "quote_text": quote.text,
                    "author": quote.author,
                    "similarity_score": float(similarity)
                })
        
        # Sort by similarity and return top results
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        return similarities[:limit]
    
    async def get_clusters(self, vector_space_id: Optional[int] = None, 
                         n_clusters: int = 5):
        """Get quote clusters from vector analysis"""
        try:
            from sklearn.cluster import KMeans
            
            # Get vector space
            if vector_space_id:
                vector_space = self.db.query(VectorSpace).filter(
                    VectorSpace.id == vector_space_id
                ).first()
            else:
                vector_space = self.db.query(VectorSpace).order_by(
                    VectorSpace.created_at.desc()
                ).first()
            
            if not vector_space:
                return []
            
            # Get vectors and quotes
            vectors_data = self.db.query(QuoteVector, Quote).join(Quote).filter(
                QuoteVector.vector_space_id == vector_space.id
            ).all()
            
            if len(vectors_data) < n_clusters:
                return []
            
            vectors = np.array([qv.vector for qv, _ in vectors_data])
            
            # Perform clustering
            kmeans = KMeans(n_clusters=n_clusters, random_state=42)
            cluster_labels = kmeans.fit_predict(vectors)
            
            # Group quotes by cluster
            clusters = {}
            for i, (qv, quote) in enumerate(vectors_data):
                cluster_id = int(cluster_labels[i])
                if cluster_id not in clusters:
                    clusters[cluster_id] = []
                
                clusters[cluster_id].append({
                    "quote_id": quote.id,
                    "text": quote.text,
                    "author": quote.author,
                    "language": quote.language
                })
            
            return [{"cluster_id": k, "quotes": v} for k, v in clusters.items()]
            
        except ImportError:
            return []
