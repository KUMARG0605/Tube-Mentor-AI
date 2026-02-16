"""FAISS-based vector store for video embeddings and similarity search."""

import faiss
import numpy as np
import pickle
from pathlib import Path
from typing import List, Tuple, Optional, Dict
from app.services.embeddings import generate_embedding, EMBEDDING_DIMENSION


INDEX_DIR = Path(__file__).parent.parent / "outputs" / "faiss_index"
INDEX_FILE = INDEX_DIR / "video_index.faiss"
METADATA_FILE = INDEX_DIR / "video_metadata.pkl"


class VideoVectorStore:
    """Vector database for video embeddings using FAISS IndexFlatIP."""
    
    def __init__(self):
        """Initialize vector store, loading existing index or creating new one."""
        INDEX_DIR.mkdir(parents=True, exist_ok=True)
        
        if INDEX_FILE.exists() and METADATA_FILE.exists():
            self._load_index()
        else:
            self.index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
            self.video_ids: List[str] = []
            self.metadata: Dict[str, dict] = {}
    
    def _load_index(self):
        """Load index and metadata from disk."""
        self.index = faiss.read_index(str(INDEX_FILE))
        with open(METADATA_FILE, 'rb') as f:
            data = pickle.load(f)
            self.video_ids = data['video_ids']
            self.metadata = data['metadata']
    
    def _save_index(self):
        """Save index and metadata to disk."""
        faiss.write_index(self.index, str(INDEX_FILE))
        with open(METADATA_FILE, 'wb') as f:
            pickle.dump({
                'video_ids': self.video_ids,
                'metadata': self.metadata,
            }, f)
    
    def add_video(
        self,
        video_id: str,
        title: str,
        embedding: Optional[np.ndarray] = None,
        description: str = "",
        summary: str = "",
        transcript: str = "",
        thumbnail_url: str = "",
        channel_name: str = "",
    ) -> bool:
        """Add a video to the vector store. Returns False if already exists."""
        if video_id in self.metadata:
            return False
        
        if embedding is None:
            from app.services.embeddings import create_video_text
            text = create_video_text(title, description, summary, transcript)
            embedding = generate_embedding(text)
        
        if embedding.ndim == 1:
            embedding = embedding.reshape(1, -1)
        
        self.index.add(embedding.astype('float32'))
        
        self.video_ids.append(video_id)
        self.metadata[video_id] = {
            'title': title,
            'description': description[:500] if description else "",
            'summary': summary[:500] if summary else "",
            'thumbnail_url': thumbnail_url,
            'channel_name': channel_name,
        }
        
        self._save_index()
        return True
    
    def search_similar(
        self,
        query: str = None,
        video_id: str = None,
        embedding: np.ndarray = None,
        k: int = 5,
        exclude_video_ids: List[str] = None,
    ) -> List[Tuple[str, float, dict]]:
        """Find videos similar to query text, video, or embedding."""
        if self.index.ntotal == 0:
            return []
        
        if embedding is not None:
            query_embedding = embedding
        elif query is not None:
            query_embedding = generate_embedding(query)
        elif video_id is not None:
            if video_id not in self.video_ids:
                raise ValueError(f"Video {video_id} not in index")
            idx = self.video_ids.index(video_id)
            query_embedding = self.index.reconstruct(idx)
        else:
            raise ValueError("Must provide query, video_id, or embedding")
        
        if query_embedding.ndim == 1:
            query_embedding = query_embedding.reshape(1, -1)
        
        search_k = min(k + len(exclude_video_ids or []) + 1, self.index.ntotal)
        distances, indices = self.index.search(query_embedding.astype('float32'), search_k)
        
        results = []
        exclude_set = set(exclude_video_ids or [])
        
        for dist, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue
            
            vid = self.video_ids[idx]
            if vid in exclude_set:
                continue
            
            results.append((vid, float(dist), self.metadata.get(vid, {})))
            
            if len(results) >= k:
                break
        
        return results
    
    def get_video_count(self) -> int:
        """Return the number of videos in the index."""
        return len(self.video_ids)
    
    def has_video(self, video_id: str) -> bool:
        """Check if a video is in the index."""
        return video_id in self.metadata
    
    def get_video_metadata(self, video_id: str) -> Optional[dict]:
        """Get metadata for a specific video."""
        return self.metadata.get(video_id)
    
    def remove_video(self, video_id: str) -> bool:
        """Remove a video from the index. Rebuilds entire index."""
        if video_id not in self.video_ids:
            return False
        
        idx = self.video_ids.index(video_id)
        self.video_ids.pop(idx)
        del self.metadata[video_id]
        
        if self.video_ids:
            all_embeddings = []
            for i in range(self.index.ntotal):
                if i != idx:
                    all_embeddings.append(self.index.reconstruct(i))
            
            self.index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
            if all_embeddings:
                self.index.add(np.array(all_embeddings).astype('float32'))
        else:
            self.index = faiss.IndexFlatIP(EMBEDDING_DIMENSION)
        
        self._save_index()
        return True


_vector_store: Optional[VideoVectorStore] = None


def get_vector_store() -> VideoVectorStore:
    """Get or create the singleton vector store instance."""
    global _vector_store
    if _vector_store is None:
        _vector_store = VideoVectorStore()
    return _vector_store
