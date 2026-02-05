"""Seek PostgreSQL storage — chunks + FTS + vector search."""

import os
import psycopg2
import numpy as np
import json
from typing import Optional, List, Tuple, Any

import os

def expand(path):
    """Simple path expansion function."""
    return os.path.expanduser(path)


def get_connection():
    """Get PostgreSQL connection using environment variables."""
    import os
    conn = psycopg2.connect(
        host=os.environ.get("PT_DB_HOST", "localhost"),
        port=int(os.environ.get("PT_DB_PORT", 5433)),
        database=os.environ.get("PT_DB_NAME", "financial_analysis"),
        user=os.environ.get("PT_DB_USER", "finance_user"),
        password=os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
    )
    return conn


def init_db():
    """Initialize PostgreSQL tables for seek functionality."""
    conn = get_connection()
    cursor = conn.cursor()
    
    # Create chunks table with embedding support
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seek_chunks (
            id SERIAL PRIMARY KEY,
            source_path TEXT NOT NULL,
            label TEXT,
            chunk_text TEXT NOT NULL,
            line_start INTEGER,
            line_end INTEGER,
            embedding BYTEA,
            indexed_at DOUBLE PRECISION,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create file metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS seek_file_meta (
            source_path TEXT PRIMARY KEY,
            mtime DOUBLE PRECISION,
            indexed_at DOUBLE PRECISION,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    
    # Create indexes for performance
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_seek_chunks_source ON seek_chunks(source_path);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_seek_chunks_label ON seek_chunks(label);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_seek_file_meta_mtime ON seek_file_meta(mtime);")
    
    # Create full-text search index
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_seek_chunks_fts ON seek_chunks USING GIN(to_tsvector('english', chunk_text));")
    
    conn.commit()
    conn.close()
    return True


def get_file_mtime(source_path: str) -> Optional[float]:
    """Get the modification time for a file from the database."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT mtime FROM seek_file_meta WHERE source_path = %s;", (source_path,))
    result = cursor.fetchone()
    
    conn.close()
    return result[0] if result else None


def upsert_chunks(source_path: str, label: str, chunks: List[Tuple[str, int, int]], embeddings: Optional[List[np.ndarray]]) -> None:
    """Replace all chunks for a source_path with new ones."""
    import time
    
    now = time.time()
    conn = get_connection()
    cursor = conn.cursor()
    
    # Delete existing chunks for this source
    cursor.execute("DELETE FROM seek_chunks WHERE source_path = %s;", (source_path,))
    
    # Insert new chunks
    for i, (text, ls, le) in enumerate(chunks):
        emb_bytes = None
        if embeddings is not None and i < len(embeddings):
            emb_array = embeddings[i]
            if isinstance(emb_array, np.ndarray):
                emb_bytes = emb_array.astype(np.float32).tobytes()
        
        cursor.execute("""
            INSERT INTO seek_chunks (source_path, label, chunk_text, line_start, line_end, embedding, indexed_at)
            VALUES (%s, %s, %s, %s, %s, %s, %s);
        """, (source_path, label, text, ls, le, emb_bytes, now))
    
    # Update file metadata
    mtime = now
    expanded_path = expand(source_path)
    if os.path.exists(expanded_path):
        mtime = os.path.getmtime(expanded_path)
    
    cursor.execute("""
        INSERT INTO seek_file_meta (source_path, mtime, indexed_at)
        VALUES (%s, %s, %s)
        ON CONFLICT (source_path) DO UPDATE SET
            mtime = EXCLUDED.mtime,
            indexed_at = EXCLUDED.indexed_at;
    """, (source_path, mtime, now))
    
    conn.commit()
    conn.close()


def search_vector(query_embedding: np.ndarray, top_k: int = 5, label: Optional[str] = None) -> List[Tuple[float, Any]]:
    """Vector similarity search using PostgreSQL."""
    import math
    
    # Convert query embedding to bytes for database comparison
    qvec = query_embedding.astype(np.float32)
    qnorm = np.linalg.norm(qvec)
    if qnorm == 0:
        return []
    
    conn = get_connection()
    cursor = conn.cursor()
    
    # For PostgreSQL, we'll implement cosine similarity manually
    # First, get all embeddings from the database
    where_clause = "WHERE embedding IS NOT NULL"
    params = []
    if label:
        where_clause += " AND label = %s"
        params.append(label)
    
    cursor.execute(f"""
        SELECT id, source_path, label, chunk_text, line_start, line_end, embedding
        FROM seek_chunks {where_clause};
    """, params)
    
    rows = cursor.fetchall()
    scored = []
    
    for row in rows:
        emb_bytes = row[6]  # embedding column
        if emb_bytes:
            try:
                stored = np.frombuffer(emb_bytes, dtype=np.float32)
                snorm = np.linalg.norm(stored)
                if snorm == 0:
                    continue
                # Calculate cosine similarity
                sim = float(np.dot(qvec, stored) / (qnorm * snorm))
                # Create a dict-like object similar to sqlite Row
                row_obj = {
                    'id': row[0], 'source_path': row[1], 'label': row[2],
                    'chunk_text': row[3], 'line_start': row[4], 'line_end': row[5]
                }
                scored.append((sim, row_obj))
            except Exception:
                continue
    
    # Sort by similarity score descending
    scored.sort(key=lambda x: -x[0])
    
    conn.close()
    return scored[:top_k]


def search_fts(query: str, top_k: int = 5, label: Optional[str] = None) -> List[Tuple[float, Any]]:
    """Full-text search using PostgreSQL."""
    conn = get_connection()
    cursor = conn.cursor()
    
    where_clause = "WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery('english', %s)"
    params = [query]
    
    if label:
        where_clause += " AND label = %s"
        params.append(label)
    
    cursor.execute(f"""
        SELECT id, source_path, label, chunk_text, line_start, line_end,
               ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s)) as score
        FROM seek_chunks
        {where_clause}
        ORDER BY score DESC
        LIMIT %s;
    """, params + [query, top_k])
    
    rows = cursor.fetchall()
    results = []
    
    for row in rows:
        row_obj = {
            'id': row[0], 'source_path': row[1], 'label': row[2],
            'chunk_text': row[3], 'line_start': row[4], 'line_end': row[5],
            'score': row[6]
        }
        results.append((float(row[6]), row_obj))
    
    conn.close()
    return results


def hybrid_search(query: str, query_embedding: Optional[np.ndarray], top_k: int = 5, mode: str = "hybrid", label: Optional[str] = None) -> List[Any]:
    """Hybrid search combining FTS and vector search."""
    fts_results = []
    vector_results = []
    
    if mode in ("hybrid", "exact"):
        fts_results = search_fts(query, top_k * 2, label)  # Get more results for hybrid
    
    if mode in ("hybrid", "semantic") and query_embedding is not None:
        vector_results = search_vector(query_embedding, top_k * 2, label)
    
    if mode == "exact":
        return fts_results[:top_k]
    elif mode == "semantic":
        return vector_results[:top_k]
    else:  # hybrid
        # Combine and rank results
        all_results = {}
        
        # Add FTS results with score adjustment
        for score, row in fts_results:
            key = row['id']
            all_results[key] = {
                'row': row,
                'fts_score': score,
                'vector_score': 0.0
            }
        
        # Add vector results with score adjustment
        for score, row in vector_results:
            key = row['id']
            if key in all_results:
                all_results[key]['vector_score'] = score
            else:
                all_results[key] = {
                    'row': row,
                    'fts_score': 0.0,
                    'vector_score': score
                }
        
        # Rank by combined score (equal weight for FTS and vector)
        ranked = []
        for key, data in all_results.items():
            combined_score = (data['fts_score'] * 0.5) + (data['vector_score'] * 0.5)
            ranked.append((combined_score, data['row']))
        
        # Sort by combined score descending
        ranked.sort(key=lambda x: -x[0])
        return ranked[:top_k]


def delete_source(source_path: str) -> None:
    """Delete all chunks for a given source path."""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute("DELETE FROM seek_chunks WHERE source_path = %s;", (source_path,))
    cursor.execute("DELETE FROM seek_file_meta WHERE source_path = %s;", (source_path,))
    
    conn.commit()
    conn.close()