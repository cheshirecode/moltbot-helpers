#!/usr/bin/env python3
"""seek_pg — PostgreSQL-powered local semantic search engine."""

import argparse
import os
import sys
import time

from .store import init_db, upsert_chunks, delete_source, get_file_mtime, hybrid_search


def cmd_index(args):
    init_db()  # Initialize database if needed
    from ..seek.indexer import chunk_markdown, chunk_text, chunk_sqlite, embed, resolve_paths
    
    model_name = os.environ.get("SEEK_MODEL", "all-MiniLM-L6-v2")  # Default model
    chunk_size = int(os.environ.get("SEEK_CHUNK_SIZE", 256))
    overlap = int(os.environ.get("SEEK_CHUNK_OVERLAP", 32))
    total_chunks = 0
    total_files = 0

    # Index file paths
    if args.path:
        # Index specific path
        fp = args.path  # No expansion needed for PostgreSQL version
        if not os.path.exists(fp):
            print(f"File not found: {fp}")
            return
        files = [(fp, "manual")]
    else:
        # For PostgreSQL version, we'll use command line paths or environment config
        # Since we're migrating away from config files, we'll use env vars
        paths_env = os.environ.get("SEEK_INDEX_PATHS", "")
        if paths_env:
            files = [(p.strip(), "auto") for p in paths_env.split(",") if p.strip()]
        else:
            print("No paths configured for indexing. Set SEEK_INDEX_PATHS environment variable.")
            return

    for filepath, label in files:
        # Check mtime to skip unchanged
        if not args.force:
            stored_mtime = get_file_mtime(filepath)
            try:
                current_mtime = os.path.getmtime(filepath)
            except OSError:
                continue
            if stored_mtime and abs(current_mtime - stored_mtime) < 0.01:
                continue

        if filepath.endswith(".md"):
            chunks = chunk_markdown(filepath, chunk_size, overlap)
        else:
            chunks = chunk_text(filepath, chunk_size, overlap)

        if not chunks:
            continue

        # Import embed function from original seek module
        from ..seek.indexer import embed
        texts = [c[0] for c in chunks]
        embeddings = embed(texts, model_name)
        upsert_chunks(filepath, label, chunks, embeddings)
        total_chunks += len(chunks)
        total_files += 1
        print(f"  {filepath} ({len(chunks)} chunks)")

    # Note: Skipping SQLite sources for PostgreSQL version since we're moving away from SQLite
    print(f"\nIndexed {total_files} sources, {total_chunks} chunks")


def cmd_search(args):
    query = " ".join(args.query)

    # Prepare query embedding
    query_embedding = None
    if args.mode in ("semantic", "hybrid"):
        from ..seek.indexer import embed
        query_embedding = embed([query], os.environ.get("SEEK_MODEL", "all-MiniLM-L6-v2"))[0]

    results = hybrid_search(query, query_embedding, top_k=args.top, mode=args.mode, label=args.label)

    if not results:
        print("No results found.")
    else:
        for score, r in results:
            path = r["source_path"]
            # Shorten home paths
            home = os.path.expanduser("~")
            if path.startswith(home):
                path = "~" + path[len(home):]
            ls = r.get("line_start") or ""
            le = r.get("line_end") or ""
            lines = f":{ls}-{le}" if ls else ""
            label = f" ({r.get('label', '')})" if r.get("label") else ""
            print(f"[{score:.2f}] {path}{lines}{label}")
            # Show first 120 chars of chunk
            preview = r["chunk_text"][:120].replace("\n", " ").strip()
            if len(r["chunk_text"]) > 120:
                preview += "..."
            print(f"  {preview}")
            print()


def cmd_status(args):
    import psycopg2
    
    conn = psycopg2.connect(
        host=os.environ.get("PT_DB_HOST", "localhost"),
        port=int(os.environ.get("PT_DB_PORT", 5433)),
        database=os.environ.get("PT_DB_NAME", "financial_analysis"),
        user=os.environ.get("PT_DB_USER", "finance_user"),
        password=os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
    )
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM seek_chunks;")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT source_path, COUNT(*) as cnt, MAX(indexed_at) as last FROM seek_chunks GROUP BY source_path ORDER BY last DESC;")
    sources = cursor.fetchall()
    
    # Get database size
    cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
    db_size = cursor.fetchone()[0]
    
    print(f"Database: PostgreSQL (financial_analysis)")
    print(f"Database size: {db_size}")
    print(f"Total chunks: {total}")
    print(f"Sources: {len(sources)}")
    print()
    for path, cnt, last in sources:
        home = os.path.expanduser("~")
        if path.startswith(home):
            path = "~" + path[len(home):]
        ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(last)) if last else "unknown"
        print(f"  {path}: {cnt} chunks (indexed {ts})")
    
    conn.close()


def cmd_reindex(args):
    args.path = None
    args.force = True
    cmd_index(args)


def cmd_forget(args):
    path = args.path
    delete_source(path)
    print(f"Removed: {path}")


def main():
    parser = argparse.ArgumentParser(prog="seek_pg", description="PostgreSQL-powered local semantic search engine")
    sub = parser.add_subparsers(dest="command")

    p_index = sub.add_parser("index", help="Index configured paths")
    p_index.add_argument("path", nargs="?", help="Specific path to index")
    p_index.add_argument("--force", action="store_true", help="Force reindex")

    p_search = sub.add_parser("search", help="Search indexed content")
    p_search.add_argument("query", nargs="+")
    p_search.add_argument("--mode", choices=["semantic", "exact", "hybrid"], default="hybrid")
    p_search.add_argument("--top", type=int, default=5)
    p_search.add_argument("--label", help="Filter by label")

    sub.add_parser("status", help="Show index status")
    sub.add_parser("reindex", help="Force reindex everything")

    p_forget = sub.add_parser("forget", help="Remove a path from index")
    p_forget.add_argument("path")

    args = parser.parse_args()

    if args.command == "index":
        cmd_index(args)
    elif args.command == "search":
        cmd_search(args)
    elif args.command == "status":
        cmd_status(args)
    elif args.command == "reindex":
        cmd_reindex(args)
    elif args.command == "forget":
        cmd_forget(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()