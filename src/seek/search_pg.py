"""Seek PostgreSQL search — hybrid vector + FTS search."""

import os
import psycopg2
from typing import List, Tuple, Dict, Any

import numpy as np

from .config import expand, load_config
from .store_pg import search_vector_pg, search_fts_pg, hybrid_search_pg


def search_pg(query: str, top_k: int = 5, mode: str = "hybrid", label: str = None) -> List[Dict[str, Any]]:
    """Search across indexed content using PostgreSQL backend."""
    cfg = load_config()
    
    # Extract connection parameters from environment variables for PostgreSQL
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
    from pgvector.psycopg2 import register_vector
    register_vector(conn)
    
    # Embed the query
    from .indexer_pg import embed
    query_embedding = embed([query], cfg["model"])[0]
    
    # Perform search based on mode
    if mode == "vector":
        results = search_vector_pg(conn, query_embedding, top_k=top_k, label=label)
    elif mode == "fts":
        results = search_fts_pg(conn, query, top_k=top_k, label=label)
    elif mode == "hybrid":
        results = hybrid_search_pg(conn, query, query_embedding, top_k=top_k, label=label)
    else:
        raise ValueError(f"Unknown search mode: {mode}")
    
    conn.close()
    
    # Format results consistently
    formatted_results = []
    for score, data in results:
        formatted_results.append({
            "score": score,
            "source_path": data["source_path"],
            "label": data["label"],
            "chunk_text": data["chunk_text"],
            "line_start": data["line_start"],
            "line_end": data["line_end"]
        })
    
    return formatted_results


def status_pg() -> Dict[str, Any]:
    """Get index status using PostgreSQL backend."""
    cfg = load_config()
    
    # Extract connection parameters from environment variables for PostgreSQL
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
    
    with conn.cursor() as cursor:
        # Count total chunks
        cursor.execute("SELECT COUNT(*) FROM seek_chunks")
        total_chunks = cursor.fetchone()[0]
        
        # Count total sources
        cursor.execute("SELECT COUNT(DISTINCT source_path) FROM seek_chunks")
        total_sources = cursor.fetchone()[0]
        
        # Get database size
        cursor.execute("SELECT pg_size_pretty(pg_database_size(%s))", (db_name,))
        db_size = cursor.fetchone()[0]
        
        # Get labels
        cursor.execute("SELECT DISTINCT label FROM seek_chunks WHERE label IS NOT NULL")
        labels = [row[0] for row in cursor.fetchall()]
    
    conn.close()
    
    return {
        "db_type": "PostgreSQL",
        "db_name": db_name,
        "total_chunks": total_chunks,
        "total_sources": total_sources,
        "db_size": db_size,
        "labels": labels
    }


def reindex_pg(force: bool = False, label: str = None):
    """Rebuild index using PostgreSQL backend."""
    cfg = load_config()
    
    # Extract connection parameters from environment variables for PostgreSQL
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
    
    from .indexer_pg import index_file_pg
    
    # Clear existing index if force is True
    if force:
        print("Clearing existing PostgreSQL index...")
        with conn.cursor() as cursor:
            if label:
                cursor.execute("DELETE FROM seek_chunks WHERE label = %s", (label,))
                cursor.execute("DELETE FROM seek_file_meta WHERE source_path IN (SELECT DISTINCT source_path FROM seek_chunks WHERE label = %s)", (label,))
            else:
                cursor.execute("DELETE FROM seek_chunks")
                cursor.execute("DELETE FROM seek_file_meta")
        conn.commit()
        print("Existing index cleared.")
    
    # Index all configured paths
    paths = cfg.get("paths", [])
    sqlite_sources = cfg.get("sqliteSources", [])
    
    all_sources = paths + sqlite_sources
    
    if not all_sources:
        print("No paths configured for indexing. Check your config at ~/.config/seek/config.json")
        return
    
    for source in all_sources:
        expanded_source = expand(source)
        source_path = Path(expanded_source)
        
        if source_path.is_file():
            print(f"Indexing file: {expanded_source}")
            try:
                index_file_pg(conn, expanded_source, label or "default", cfg)
            except Exception as e:
                print(f"  Error indexing {expanded_source}: {e}")
        elif source_path.is_dir():
            print(f"Indexing directory: {expanded_source}")
            for ext in [".md", ".txt", ".py", ".js", ".ts", ".json", ".yaml", ".yml", ".toml", ".xml", ".html", ".css"]:
                for file_path in source_path.rglob(f"*{ext}"):
                    if file_path.is_file():
                        print(f"  Indexing: {file_path}")
                        try:
                            index_file_pg(conn, str(file_path), label or "directory", cfg)
                        except Exception as e:
                            print(f"    Error indexing {file_path}: {e}")
        else:
            print(f"Source does not exist: {expanded_source}")
    
    conn.close()
    print("Reindexing completed.")


def delete_source_pg(source_path: str):
    """Delete a source from the PostgreSQL index."""
    cfg = load_config()
    
    # Extract connection parameters from environment variables for PostgreSQL
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
    
    from .store_pg import delete_source_pg as delete_source_func
    delete_source_func(conn, expand(source_path))
    
    conn.close()
    print(f"Deleted source: {source_path}")