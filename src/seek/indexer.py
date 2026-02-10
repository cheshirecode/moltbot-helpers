"""Seek indexer — chunking and embedding."""

import glob
import os
import re

import numpy as np
import psycopg2
from psycopg2.extras import RealDictCursor

from .config import expand

# Database connection settings (for PostgreSQL table chunking)
DB_HOST = os.environ.get("SEEK_DB_HOST", os.environ.get("PT_DB_HOST", "localhost"))
DB_PORT = os.environ.get("SEEK_DB_PORT", os.environ.get("PT_DB_PORT", "5433"))
DB_NAME = os.environ.get("SEEK_DB_NAME", os.environ.get("PT_DB_NAME", "financial_analysis"))
DB_USER = os.environ.get("SEEK_DB_USER", os.environ.get("PT_DB_USER", "finance_user"))
DB_PASS = os.environ.get("SEEK_DB_PASS", os.environ.get("PT_DB_PASS", "secure_finance_password"))

# Lazy model cache
_model = None
_model_name = None


def _get_model(model_name):
    global _model, _model_name
    if _model is not None and _model_name == model_name:
        return _model
    try:
        from sentence_transformers import SentenceTransformer
        _model = SentenceTransformer(model_name)
        _model_name = model_name
        return _model
    except ImportError:
        raise RuntimeError("sentence-transformers not installed. Install with: uv pip install sentence-transformers")


def embed(texts, model_name="all-MiniLM-L6-v2"):
    """Encode texts into embeddings. Returns numpy array (N, dim)."""
    if not texts:
        return np.array([])
    model = _get_model(model_name)
    return model.encode(texts, show_progress_bar=False, convert_to_numpy=True)


def chunk_markdown(filepath, chunk_size=256, overlap=32):
    """Split markdown by headers, then paragraphs, then sentences.
    Returns list of (text, line_start, line_end).
    """
    filepath = expand(filepath)
    with open(filepath, "r", errors="replace") as f:
        lines = f.readlines()

    chunks = []
    # Split into sections by headers
    sections = []
    current_start = 0
    current_lines = []

    for i, line in enumerate(lines):
        if re.match(r"^#{1,6}\s", line) and current_lines:
            sections.append((current_start, i - 1, current_lines))
            current_lines = [line]
            current_start = i
        else:
            current_lines.append(line)
    if current_lines:
        sections.append((current_start, len(lines) - 1, current_lines))

    for sec_start, sec_end, sec_lines in sections:
        text = "".join(sec_lines).strip()
        if not text:
            continue
        words = text.split()
        if len(words) <= chunk_size:
            chunks.append((text, sec_start + 1, sec_end + 1))
        else:
            # Split into overlapping word chunks
            for j in range(0, len(words), chunk_size - overlap):
                chunk_words = words[j : j + chunk_size]
                if not chunk_words:
                    break
                chunk_text = " ".join(chunk_words)
                # Approximate line numbers
                ratio_start = j / len(words)
                ratio_end = min((j + len(chunk_words)) / len(words), 1.0)
                ls = sec_start + int(ratio_start * (sec_end - sec_start)) + 1
                le = sec_start + int(ratio_end * (sec_end - sec_start)) + 1
                chunks.append((chunk_text, ls, le))

    return chunks


def chunk_text(filepath, chunk_size=256, overlap=32):
    """Fixed-size token chunks for non-markdown files."""
    filepath = expand(filepath)
    with open(filepath, "r", errors="replace") as f:
        content = f.read()
    words = content.split()
    total_lines = content.count("\n") + 1
    chunks = []
    for j in range(0, len(words), chunk_size - overlap):
        chunk_words = words[j : j + chunk_size]
        if not chunk_words:
            break
        text = " ".join(chunk_words)
        ratio_s = j / max(len(words), 1)
        ratio_e = min((j + len(chunk_words)) / max(len(words), 1), 1.0)
        ls = max(1, int(ratio_s * total_lines))
        le = max(1, int(ratio_e * total_lines))
        chunks.append((text, ls, le))
    return chunks


def chunk_postgres_table(table_name, columns=None):
    """Each row becomes a chunk formatted as key: value pairs.
    Returns list of (text, line_start, line_end) — line numbers are row indices.
    """
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )
    cur = conn.cursor(cursor_factory=RealDictCursor)
    chunks = []
    
    try:
        if columns:
            cols = ", ".join(columns)
            cur.execute(f"SELECT {cols} FROM {table_name}")
        else:
            cur.execute(f"SELECT * FROM {table_name}")
        rows = cur.fetchall()
        
        for i, row in enumerate(rows):
            parts = []
            for col, val in row.items():
                if val is not None:
                    parts.append(f"{table_name}.{col}: {val}")
            if parts:
                chunks.append(("\n".join(parts), i + 1, i + 1))
    except psycopg2.Error as e:
        print(f"Error reading table {table_name}: {e}")
    finally:
        conn.close()
    
    return chunks


# Keep for backwards compatibility, but use PostgreSQL
def chunk_sqlite(db_path, tables):
    """Deprecated: Use chunk_postgres_table instead.
    This function now indexes from PostgreSQL tables if they exist.
    """
    chunks = []
    for table in tables:
        # Try PostgreSQL tables with common prefixes
        for prefix in ["", "fp_", "seek_", "project_"]:
            try:
                table_chunks = chunk_postgres_table(f"{prefix}{table}")
                if table_chunks:
                    chunks.extend(table_chunks)
                    break
            except:
                continue
    return chunks


def resolve_paths(path_configs):
    """Resolve glob patterns from config. Returns list of (filepath, label)."""
    results = []
    for pc in path_configs:
        pattern = expand(pc["glob"])
        label = pc.get("label", "default")
        for fp in glob.glob(pattern, recursive=True):
            if os.path.isfile(fp):
                results.append((fp, label))
    return results
