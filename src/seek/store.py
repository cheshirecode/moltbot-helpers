"""Seek SQLite storage — chunks + FTS5 + vector search."""

import os
import sqlite3
import time

import numpy as np

from .config import expand


def init_db(db_path):
    db_path = expand(db_path)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("""CREATE TABLE IF NOT EXISTS chunks (
        id INTEGER PRIMARY KEY,
        source_path TEXT NOT NULL,
        label TEXT,
        chunk_text TEXT NOT NULL,
        line_start INTEGER,
        line_end INTEGER,
        embedding BLOB,
        indexed_at REAL
    )""")
    conn.execute("""CREATE TABLE IF NOT EXISTS file_meta (
        source_path TEXT PRIMARY KEY,
        mtime REAL,
        indexed_at REAL
    )""")
    # FTS5 virtual table
    conn.execute("""CREATE VIRTUAL TABLE IF NOT EXISTS chunks_fts USING fts5(
        chunk_text, content=chunks, content_rowid=id
    )""")
    # Triggers to keep FTS in sync
    conn.execute("""CREATE TRIGGER IF NOT EXISTS chunks_ai AFTER INSERT ON chunks BEGIN
        INSERT INTO chunks_fts(rowid, chunk_text) VALUES (new.id, new.chunk_text);
    END""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS chunks_ad AFTER DELETE ON chunks BEGIN
        INSERT INTO chunks_fts(chunks_fts, rowid, chunk_text) VALUES('delete', old.id, old.chunk_text);
    END""")
    conn.execute("""CREATE TRIGGER IF NOT EXISTS chunks_au AFTER UPDATE ON chunks BEGIN
        INSERT INTO chunks_fts(chunks_fts, rowid, chunk_text) VALUES('delete', old.id, old.chunk_text);
        INSERT INTO chunks_fts(rowid, chunk_text) VALUES (new.id, new.chunk_text);
    END""")
    conn.execute("CREATE INDEX IF NOT EXISTS idx_chunks_source ON chunks(source_path)")
    conn.commit()
    return conn


def get_file_mtime(conn, source_path):
    row = conn.execute("SELECT mtime FROM file_meta WHERE source_path=?", (source_path,)).fetchone()
    return row["mtime"] if row else None


def upsert_chunks(conn, source_path, label, chunks, embeddings):
    """Replace all chunks for a source_path with new ones.
    chunks: list of (chunk_text, line_start, line_end)
    embeddings: numpy array or list of numpy arrays
    """
    now = time.time()
    conn.execute("DELETE FROM chunks WHERE source_path=?", (source_path,))
    for i, (text, ls, le) in enumerate(chunks):
        emb_blob = embeddings[i].astype(np.float32).tobytes() if embeddings is not None else None
        conn.execute(
            "INSERT INTO chunks (source_path, label, chunk_text, line_start, line_end, embedding, indexed_at) VALUES (?,?,?,?,?,?,?)",
            (source_path, label, text, ls, le, emb_blob, now),
        )
    # Update file meta
    mtime = now
    if os.path.exists(expand(source_path)):
        mtime = os.path.getmtime(expand(source_path))
    conn.execute(
        "INSERT OR REPLACE INTO file_meta (source_path, mtime, indexed_at) VALUES (?,?,?)",
        (source_path, mtime, now),
    )
    conn.commit()


def search_vector(conn, query_embedding, top_k=5, label=None):
    """Cosine similarity search over stored embeddings."""
    qvec = query_embedding.astype(np.float32)
    qnorm = np.linalg.norm(qvec)
    if qnorm == 0:
        return []

    where = "WHERE embedding IS NOT NULL"
    params = []
    if label:
        where += " AND label=?"
        params.append(label)

    rows = conn.execute(f"SELECT id, source_path, label, chunk_text, line_start, line_end, embedding FROM chunks {where}", params).fetchall()

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
    """FTS5 search."""
    # Escape special FTS chars
    safe_query = query.replace('"', '""')
    try:
        if label:
            rows = conn.execute(
                """SELECT c.id, c.source_path, c.label, c.chunk_text, c.line_start, c.line_end,
                          rank as score
                   FROM chunks_fts f JOIN chunks c ON f.rowid = c.id
                   WHERE chunks_fts MATCH ? AND c.label=?
                   ORDER BY rank LIMIT ?""",
                (safe_query, label, top_k),
            ).fetchall()
        else:
            rows = conn.execute(
                """SELECT c.id, c.source_path, c.label, c.chunk_text, c.line_start, c.line_end,
                          rank as score
                   FROM chunks_fts f JOIN chunks c ON f.rowid = c.id
                   WHERE chunks_fts MATCH ?
                   ORDER BY rank LIMIT ?""",
                (safe_query, top_k),
            ).fetchall()
    except sqlite3.OperationalError:
        # FTS query syntax error — try as phrase
        try:
            phrase = f'"{safe_query}"'
            if label:
                rows = conn.execute(
                    """SELECT c.id, c.source_path, c.label, c.chunk_text, c.line_start, c.line_end,
                              rank as score
                       FROM chunks_fts f JOIN chunks c ON f.rowid = c.id
                       WHERE chunks_fts MATCH ? AND c.label=?
                       ORDER BY rank LIMIT ?""",
                    (phrase, label, top_k),
                ).fetchall()
            else:
                rows = conn.execute(
                    """SELECT c.id, c.source_path, c.label, c.chunk_text, c.line_start, c.line_end,
                              rank as score
                       FROM chunks_fts f JOIN chunks c ON f.rowid = c.id
                       WHERE chunks_fts MATCH ?
                       ORDER BY rank LIMIT ?""",
                    (phrase, top_k),
                ).fetchall()
        except sqlite3.OperationalError:
            return []
    return [(abs(float(r["score"])) if r["score"] else 0.0, r) for r in rows]


def delete_source(conn, source_path):
    conn.execute("DELETE FROM chunks WHERE source_path=?", (source_path,))
    conn.execute("DELETE FROM file_meta WHERE source_path=?", (source_path,))
    conn.commit()
