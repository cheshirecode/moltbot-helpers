#!/usr/bin/env python3
"""seek — Local semantic search engine."""

import argparse
import os
import sys
import time

from .config import load_config, expand
from .store import init_db, upsert_chunks, delete_source, get_file_mtime
from .indexer import chunk_markdown, chunk_text, chunk_sqlite, embed, resolve_paths
from .search import hybrid_search


def cmd_index(args):
    cfg = load_config()
    conn = init_db(cfg["dbPath"])
    model_name = cfg["model"]
    chunk_size = cfg.get("chunkSize", 256)
    overlap = cfg.get("chunkOverlap", 32)
    total_chunks = 0
    total_files = 0

    # Index file paths
    if args.path:
        # Index specific path
        fp = expand(args.path)
        if not os.path.exists(fp):
            print(f"File not found: {fp}")
            return
        files = [(fp, "manual")]
    else:
        files = resolve_paths(cfg.get("paths", []))

    for filepath, label in files:
        # Check mtime to skip unchanged
        if not args.force:
            stored_mtime = get_file_mtime(conn, filepath)
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

        texts = [c[0] for c in chunks]
        embeddings = embed(texts, model_name)
        upsert_chunks(conn, filepath, label, chunks, embeddings)
        total_chunks += len(chunks)
        total_files += 1
        print(f"  {filepath} ({len(chunks)} chunks)")

    # Index SQLite sources
    for src in cfg.get("sqliteSources", []):
        db_path = expand(src["path"])
        label = src.get("label", "sqlite")
        tables = src.get("tables", [])
        source_key = f"sqlite:{db_path}"

        if not args.force:
            stored_mtime = get_file_mtime(conn, source_key)
            try:
                current_mtime = os.path.getmtime(db_path)
            except OSError:
                continue
            if stored_mtime and abs(current_mtime - stored_mtime) < 0.01:
                continue

        chunks = chunk_sqlite(db_path, tables)
        if not chunks:
            continue

        texts = [c[0] for c in chunks]
        embeddings = embed(texts, model_name)
        upsert_chunks(conn, source_key, label, chunks, embeddings)
        total_chunks += len(chunks)
        total_files += 1
        print(f"  {source_key} ({len(chunks)} chunks)")

    print(f"\nIndexed {total_files} sources, {total_chunks} chunks")
    conn.close()


def cmd_search(args):
    cfg = load_config()
    conn = init_db(cfg["dbPath"])
    query = " ".join(args.query)

    query_embedding = None
    if args.mode in ("semantic", "hybrid"):
        query_embedding = embed([query], cfg["model"])[0]

    results = hybrid_search(conn, query, query_embedding, top_k=args.top, mode=args.mode, label=args.label)

    if not results:
        print("No results found.")
    else:
        for r in results:
            path = r["source_path"]
            # Shorten home paths
            home = os.path.expanduser("~")
            if path.startswith(home):
                path = "~" + path[len(home):]
            ls = r["line_start"] or ""
            le = r["line_end"] or ""
            lines = f":{ls}-{le}" if ls else ""
            label = f" ({r['label']})" if r.get("label") else ""
            score = r.get("score", 0)
            print(f"[{score:.2f}] {path}{lines}{label}")
            # Show first 120 chars of chunk
            preview = r["chunk_text"][:120].replace("\n", " ").strip()
            if len(r["chunk_text"]) > 120:
                preview += "..."
            print(f"  {preview}")
            print()

    conn.close()


def cmd_status(args):
    cfg = load_config()
    db_path = expand(cfg["dbPath"])
    if not os.path.exists(db_path):
        print("No index database found.")
        return

    conn = init_db(cfg["dbPath"])
    total = conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0]
    sources = conn.execute("SELECT source_path, COUNT(*) as cnt, MAX(indexed_at) as last FROM chunks GROUP BY source_path ORDER BY last DESC").fetchall()
    db_size = os.path.getsize(db_path)

    print(f"Database: {db_path} ({db_size / 1024 / 1024:.1f} MB)")
    print(f"Total chunks: {total}")
    print(f"Sources: {len(sources)}")
    print()
    for s in sources:
        path = s["source_path"]
        home = os.path.expanduser("~")
        if path.startswith(home):
            path = "~" + path[len(home):]
        ts = time.strftime("%Y-%m-%d %H:%M", time.localtime(s["last"])) if s["last"] else "unknown"
        print(f"  {path}: {s['cnt']} chunks (indexed {ts})")
    conn.close()


def cmd_reindex(args):
    args.path = None
    args.force = True
    cmd_index(args)


def cmd_forget(args):
    cfg = load_config()
    conn = init_db(cfg["dbPath"])
    path = expand(args.path)
    delete_source(conn, path)
    # Also try unexpanded
    delete_source(conn, args.path)
    print(f"Removed: {args.path}")
    conn.close()


def main():
    parser = argparse.ArgumentParser(prog="seek", description="Local semantic search engine")
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
