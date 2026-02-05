"""Seek PostgreSQL storage — chunks + FTS + vector search."""

import os
import psycopg2
import time
import numpy as np
from pgvector.psycopg2 import register_vector
from .config import expand


def init_db(db_path):
    # Extract connection parameters from db_path or use environment variables
    # For PostgreSQL version, we'll use environment variables
    db_host = os.environ.get("PT_DB_HOST", "localhost")
    db_port = int(os.environ.get("PT_DB_PORT", 5433))
    db_name = os.environ.get("PT_DB_NAME", "financial_analysis")
    db_user = os.environ.get("PT_DB_USER", "finance_user")
    db_password = os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
    
    conn = psycopg2.connect(
        host=db_host,
        port=db_port,
        database=db_name,
        user=db_user,
        password=db_password
    )
    
    # Register pgvector to handle vector data
    register_vector(conn)
    
    with conn.cursor() as cursor:
        # Create chunks table
        cursor.execute("""CREATE TABLE IF NOT EXISTS seek_chunks (
            id SERIAL PRIMARY KEY,
            source_path TEXT NOT NULL,
            label TEXT,
            chunk_text TEXT NOT NULL,
            line_start INTEGER,
            line_end INTEGER,
            embedding VECTOR(384),  -- Assuming 384-dim vectors from all-MiniLM-L6-v2
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Create file_meta table
        cursor.execute("""CREATE TABLE IF NOT EXISTS seek_file_meta (
            source_path TEXT PRIMARY KEY,
            mtime REAL,
            indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )""")
        
        # Create full-text search index
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_fts ON seek_chunks USING GIN(to_tsvector('english', chunk_text))")
        
        # Create index for source_path
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON seek_chunks(source_path)")
        
        # Create index for label
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_label ON seek_chunks(label)")
        
        # Create index for vector similarity (this will use pgvector's IVFFlat index)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON seek_chunks USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100)")
    
    conn.commit()
    return conn


def get_file_mtime(conn, source_path):
    with conn.cursor() as cursor:
        cursor.execute("SELECT mtime FROM seek_file_meta WHERE source_path = %s", (source_path,))
        row = cursor.fetchone()
        return row[0] if row else None


def upsert_chunks_pg(conn, source_path, label, chunks, embeddings):
    """Replace all chunks for a source_path with new ones using PostgreSQL.
    chunks: list of (chunk_text, line_start, line_end)
    embeddings: numpy array or list of numpy arrays
    """
    now = time.time()
    
    with conn.cursor() as cursor:
        # Delete existing chunks for this source_path
        cursor.execute("DELETE FROM seek_chunks WHERE source_path = %s", (source_path,))
        
        # Insert new chunks with embeddings
        for i, (text, ls, le) in enumerate(chunks):
            embedding_vec = embeddings[i].astype(np.float32) if embeddings is not None else None
            cursor.execute(
                """INSERT INTO seek_chunks (source_path, label, chunk_text, line_start, line_end, embedding, indexed_at) 
                   VALUES (%s, %s, %s, %s, %s, %s, CURRENT_TIMESTAMP)""",
                (source_path, label, text, ls, le, embedding_vec),
            )
        
        # Update file meta
        mtime = now
        if os.path.exists(expand(source_path)):
            mtime = os.path.getmtime(expand(source_path))
        
        cursor.execute(
            """INSERT INTO seek_file_meta (source_path, mtime, indexed_at) 
               VALUES (%s, %s, CURRENT_TIMESTAMP)
               ON CONFLICT (source_path) DO UPDATE SET
                   mtime = EXCLUDED.mtime,
                   indexed_at = EXCLUDED.indexed_at""",
            (source_path, mtime),
        )
    
    conn.commit()


def search_vector_pg(conn, query_embedding, top_k=5, label=None):
    """Vector similarity search using PostgreSQL/pgvector cosine similarity."""
    query_vec = query_embedding.astype(np.float32)
    
    with conn.cursor() as cursor:
        if label:
            cursor.execute(
                """SELECT id, source_path, label, chunk_text, line_start, line_end,
                          embedding <=> %s AS distance
                   FROM seek_chunks 
                   WHERE embedding IS NOT NULL AND label = %s
                   ORDER BY embedding <=> %s
                   LIMIT %s""",
                (query_vec, label, query_vec, top_k)
            )
        else:
            cursor.execute(
                """SELECT id, source_path, label, chunk_text, line_start, line_end,
                          embedding <=> %s AS distance
                   FROM seek_chunks 
                   WHERE embedding IS NOT NULL
                   ORDER BY embedding <=> %s
                   LIMIT %s""",
                (query_vec, query_vec, top_k)
            )
        
        rows = cursor.fetchall()
        
        # Convert distances to similarities (cosine similarity ranges from -1 to 1)
        # Distance is 1 - cosine_similarity, so similarity = 1 - distance
        results = []
        for row in rows:
            id_val, source_path, label_val, chunk_text, line_start, line_end, distance = row
            similarity = 1.0 - float(distance)  # Convert distance back to similarity
            results.append((
                similarity,
                {
                    'id': id_val,
                    'source_path': source_path,
                    'label': label_val,
                    'chunk_text': chunk_text,
                    'line_start': line_start,
                    'line_end': line_end
                }
            ))
        
        return results


def search_fts_pg(conn, query, top_k=5, label=None):
    """Full-text search using PostgreSQL's tsvector/tsquery."""
    with conn.cursor() as cursor:
        if label:
            cursor.execute(
                """SELECT id, source_path, label, chunk_text, line_start, line_end,
                          ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s)) AS score
                   FROM seek_chunks 
                   WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery('english', %s) 
                   AND label = %s
                   ORDER BY ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s)) DESC
                   LIMIT %s""",
                (query, query, label, query, top_k)
            )
        else:
            cursor.execute(
                """SELECT id, source_path, label, chunk_text, line_start, line_end,
                          ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s)) AS score
                   FROM seek_chunks 
                   WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery('english', %s)
                   ORDER BY ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s)) DESC
                   LIMIT %s""",
                (query, query, query, top_k)
            )
        
        rows = cursor.fetchall()
        
        results = []
        for row in rows:
            id_val, source_path, label_val, chunk_text, line_start, line_end, score = row
            results.append((
                float(score),
                {
                    'id': id_val,
                    'source_path': source_path,
                    'label': label_val,
                    'chunk_text': chunk_text,
                    'line_start': line_start,
                    'line_end': line_end
                }
            ))
        
        return results


def hybrid_search_pg(conn, query, query_embedding, top_k=5, label=None, weight_vector=0.7, weight_fts=0.3):
    """Hybrid search combining vector similarity and full-text search."""
    # Get vector search results
    vector_results = search_vector_pg(conn, query_embedding, top_k=top_k*2, label=label)
    
    # Get FTS results
    fts_results = search_fts_pg(conn, query, top_k=top_k*2, label=label)
    
    # Combine and rerank
    all_results = {}
    
    # Add vector results with weighted scores
    for score, data in vector_results:
        result_key = (data['id'], data['source_path'])
        all_results[result_key] = {
            'data': data,
            'vector_score': score,
            'fts_score': 0.0,
            'combined_score': score * weight_vector
        }
    
    # Add FTS results and update combined scores
    for score, data in fts_results:
        result_key = (data['id'], data['source_path'])
        if result_key in all_results:
            all_results[result_key]['fts_score'] = score
            # Recalculate combined score
            combined = (all_results[result_key]['vector_score'] * weight_vector + 
                       score * weight_fts)
            all_results[result_key]['combined_score'] = combined
        else:
            all_results[result_key] = {
                'data': data,
                'vector_score': 0.0,
                'fts_score': score,
                'combined_score': score * weight_fts
            }
    
    # Sort by combined score and return top-k
    sorted_results = sorted(all_results.values(), 
                           key=lambda x: x['combined_score'], 
                           reverse=True)[:top_k]
    
    return [(result['combined_score'], result['data']) for result in sorted_results]


def delete_source_pg(conn, source_path):
    """Delete all chunks for a source path."""
    with conn.cursor() as cursor:
        cursor.execute("DELETE FROM seek_chunks WHERE source_path = %s", (source_path,))
        cursor.execute("DELETE FROM seek_file_meta WHERE source_path = %s", (source_path,))
    
    conn.commit()