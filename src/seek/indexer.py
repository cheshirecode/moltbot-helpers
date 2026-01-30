"""Seek indexer — chunking and embedding."""

import glob
import os
import re
import sqlite3

import numpy as np

from .config import expand

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


def chunk_sqlite(db_path, tables):
    """Each row becomes a chunk formatted as key: value pairs.
    Returns list of (text, line_start, line_end) — line numbers are row indices.
    """
    db_path = expand(db_path)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    chunks = []
    for table in tables:
        try:
            rows = conn.execute(f"SELECT * FROM {table}").fetchall()
        except sqlite3.OperationalError:
            continue
        for i, row in enumerate(rows):
            parts = []
            for col in row.keys():
                val = row[col]
                if val is not None:
                    parts.append(f"{table}.{col}: {val}")
            if parts:
                chunks.append(("\n".join(parts), i + 1, i + 1))
    conn.close()
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
