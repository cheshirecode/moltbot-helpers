"""Seek PostgreSQL storage — chunks + full-text search + vector search."""

import os
import time

import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor

from .config import expand

# Database connection settings
DB_HOST = os.environ.get("SEEK_DB_HOST", os.environ.get("PT_DB_HOST", "localhost"))
DB_PORT = os.environ.get("SEEK_DB_PORT", os.environ.get("PT_DB_PORT", "5433"))
DB_NAME = os.environ.get("SEEK_DB_NAME", os.environ.get("PT_DB_NAME", "financial_analysis"))
DB_USER = os.environ.get("SEEK_DB_USER", os.environ.get("PT_DB_USER", "finance_user"))
DB_PASS = os.environ.get("SEEK_DB_PASS", os.environ.get("PT_DB_PASS", "secure_finance_password"))


def init_db(db_path=None):
    """Initialize PostgreSQL database tables for seek."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor()
    
    # Chunks table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seek_chunks (
            id SERIAL PRIMARY KEY,
            source_path TEXT NOT NULL,
            label TEXT,
            chunk_text TEXT NOT NULL,
            line_start INTEGER,
            line_end INTEGER,
            embedding BYTEA,
            indexed_at DOUBLE PRECISION
        )
    """)
    
    # File meta table
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seek_file_meta (
            source_path TEXT PRIMARY KEY,
            mtime DOUBLE PRECISION,
            indexed_at DOUBLE PRECISION
        )
    """)
    
    # Create indexes
    cur.execute("CREATE INDEX IF NOT EXISTS idx_seek_chunks_source ON seek_chunks(source_path)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_seek_chunks_label ON seek_chunks(label)")
    
    # Create GIN index for full-text search
    cur.execute("""
        CREATE INDEX IF NOT EXISTS idx_seek_chunks_fts 
        ON seek_chunks USING gin(to_tsvector('english', chunk_text))
    """)
    
    conn.commit()
    return conn


def get_db():
    """Get a database connection."""
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    return conn


def get_file_mtime(conn, source_path):
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("SELECT mtime FROM seek_file_meta WHERE source_path=%s", (source_path,))
    row = cur.fetchone()
    return row["mtime"] if row else None


def upsert_chunks(conn, source_path, label, chunks, embeddings):
    """Replace all chunks for a source_path with new ones.
    chunks: list of (chunk_text, line_start, line_end)
    embeddings: numpy array or list of numpy arrays
    """
    cur = conn.cursor()
    now = time.time()
    
    # Delete existing chunks for this source
    cur.execute("DELETE FROM seek_chunks WHERE source_path=%s", (source_path,))
    
    # Insert new chunks
    for i, (text, ls, le) in enumerate(chunks):
        emb_blob = embeddings[i].astype(np.float32).tobytes() if embeddings is not None else None
        cur.execute(
            """INSERT INTO seek_chunks (source_path, label, chunk_text, line_start, line_end, embedding, indexed_at) 
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (source_path, label, text, ls, le, emb_blob, now),
        )
    
    # Update file meta
    mtime = now
    expanded_path = expand(source_path)
    if os.path.exists(expanded_path):
        mtime = os.path.getmtime(expanded_path)
    
    cur.execute(
        """INSERT INTO seek_file_meta (source_path, mtime, indexed_at) VALUES (%s, %s, %s)
           ON CONFLICT (source_path) DO UPDATE SET mtime=%s, indexed_at=%s""",
        (source_path, mtime, now, mtime, now),
    )
    conn.commit()


def search_vector(conn, query_embedding, top_k=5, label=None):
    """Cosine similarity search over stored embeddings."""
    qvec = query_embedding.astype(np.float32)
    qnorm = np.linalg.norm(qvec)
    if qnorm == 0:
        return []

    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    where = "WHERE embedding IS NOT NULL"
    params = []
    if label:
        where += " AND label=%s"
        params.append(label)

    cur.execute(
        f"SELECT id, source_path, label, chunk_text, line_start, line_end, embedding FROM seek_chunks {where}",
        params
    )
    rows = cur.fetchall()

    scored = []
    for row in rows:
        stored = np.frombuffer(row["embedding"], dtype=np.float32)
        snorm = np.linalg.norm(stored)
        if snorm == 0:
            continue
        sim = float(np.dot(qvec, stored) / (qnorm * snorm))
        scored.append((sim, row))

    scored.sort(key=lambda x: -x[0])
    return scored[:top_k]


def search_fts(conn, query, top_k=5, label=None):
    """Full-text search using PostgreSQL tsquery."""
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Convert query to tsquery format
    # Simple approach: split by spaces and AND them together
    terms = query.strip().split()
    if not terms:
        return []
    
    # Create tsquery with OR between terms for more flexible matching
    tsquery = " | ".join(terms)
    
    try:
        if label:
            cur.execute(
                """SELECT id, source_path, label, chunk_text, line_start, line_end,
                          ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s)) as score
                   FROM seek_chunks
                   WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery('english', %s) AND label=%s
                   ORDER BY score DESC LIMIT %s""",
                (query, query, label, top_k),
            )
        else:
            cur.execute(
                """SELECT id, source_path, label, chunk_text, line_start, line_end,
                          ts_rank(to_tsvector('english', chunk_text), plainto_tsquery('english', %s)) as score
                   FROM seek_chunks
                   WHERE to_tsvector('english', chunk_text) @@ plainto_tsquery('english', %s)
                   ORDER BY score DESC LIMIT %s""",
                (query, query, top_k),
            )
        rows = cur.fetchall()
    except psycopg2.Error:
        # Fallback to ILIKE search if FTS fails
        pattern = f"%{query}%"
        if label:
            cur.execute(
                """SELECT id, source_path, label, chunk_text, line_start, line_end, 0.5 as score
                   FROM seek_chunks
                   WHERE chunk_text ILIKE %s AND label=%s
                   LIMIT %s""",
                (pattern, label, top_k),
            )
        else:
            cur.execute(
                """SELECT id, source_path, label, chunk_text, line_start, line_end, 0.5 as score
                   FROM seek_chunks
                   WHERE chunk_text ILIKE %s
                   LIMIT %s""",
                (pattern, top_k),
            )
        rows = cur.fetchall()
    
    return [(float(r["score"]) if r["score"] else 0.0, r) for r in rows]


def delete_source(conn, source_path):
    cur = conn.cursor()
    cur.execute("DELETE FROM seek_chunks WHERE source_path=%s", (source_path,))
    cur.execute("DELETE FROM seek_file_meta WHERE source_path=%s", (source_path,))
    conn.commit()
