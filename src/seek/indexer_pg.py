"""Seek PostgreSQL indexer — embed, chunk, upsert."""

import os
import hashlib
import tiktoken
from pathlib import Path
from typing import List, Tuple

import numpy as np

from .config import expand
from .store_pg import upsert_chunks_pg


enc = tiktoken.get_encoding("cl100k_base")


def chunk_markdown(path: str, chunk_size: int, overlap: int) -> List[Tuple[str, int, int]]:
    """Split markdown into overlapping chunks of specified token length."""
    path = expand(path)
    with open(path, encoding="utf-8") as f:
        lines = f.readlines()

    # Join lines back together, but preserve line breaks for context
    text = "".join(lines)
    
    # Split into sentences to use as base units
    sentences = []
    current_sentence = ""
    for line in lines:
        if line.strip() == "":
            if current_sentence.strip():
                sentences.append(current_sentence)
                current_sentence = ""
        else:
            current_sentence += line
    
    if current_sentence.strip():
        sentences.append(current_sentence)

    # Tokenize the full text to understand token boundaries
    tokens = enc.encode(text)
    
    chunks = []
    start_idx = 0
    
    while start_idx < len(tokens):
        end_idx = start_idx + chunk_size
        
        # If this is the last chunk, include all remaining tokens
        if end_idx >= len(tokens):
            end_idx = len(tokens)
        
        # Decode this chunk back to text
        chunk_tokens = tokens[start_idx:end_idx]
        chunk_text = enc.decode(chunk_tokens)
        
        # Find the approximate line numbers for this chunk
        # This is a rough approximation - in practice you might want more sophisticated alignment
        start_char = len(enc.decode(tokens[:start_idx]))
        end_char = len(enc.decode(tokens[:end_idx]))
        
        # Find line numbers by counting newlines up to these character positions
        start_line = text[:start_char].count('\n') + 1
        end_line = text[:end_char].count('\n') + 1
        
        chunks.append((chunk_text, start_line, end_line))
        
        # Move to the next chunk with overlap
        if end_idx >= len(tokens):
            break
            
        # Calculate overlap in tokens
        overlap_tokens = int(overlap)
        start_idx = end_idx - overlap_tokens
        
        # Ensure we don't go backwards
        if start_idx <= start_idx:
            start_idx = end_idx  # Move to next position without overlap if overlap would cause issues

    return chunks


def embed(texts: List[str], model: str) -> np.ndarray:
    """Get embeddings for a list of texts."""
    if model == "debug":
        # Return random embeddings for debugging
        return np.random.rand(len(texts), 384).astype(np.float32)
    
    try:
        import sentence_transformers
    except ImportError:
        raise ImportError(
            "sentence-transformers required for embeddings. Install with: pip install sentence-transformers"
        )
    
    # Use a local SentenceTransformer model
    model_path = os.environ.get("SENTENCE_TRANSFORMER_MODEL", "all-MiniLM-L6-v2")
    
    # Check if it's a local path
    if Path(model_path).exists():
        model_instance = sentence_transformers.SentenceTransformer(model_path)
    else:
        # Download from HuggingFace
        model_instance = sentence_transformers.SentenceTransformer(model_path)
    
    embeddings = model_instance.encode(texts, convert_to_numpy=True, show_progress_bar=False)
    return embeddings.astype(np.float32)


def index_file_pg(conn, path: str, label: str, cfg: dict):
    """Index a file using PostgreSQL backend."""
    path = expand(path)
    chunks = chunk_markdown(path, cfg.get("chunkSize", 256), cfg.get("chunkOverlap", 32))
    
    if not chunks:
        print(f"  No chunks to index for {path}")
        return
    
    texts = [c[0] for c in chunks]
    embeddings = embed(texts, cfg["model"])
    
    print(f"  Uploading {len(chunks)} chunks to PostgreSQL database")
    upsert_chunks_pg(conn, path, label, chunks, embeddings)
    
    print(f"  Indexed {path} -> {label}")