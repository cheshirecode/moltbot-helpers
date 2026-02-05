#!/usr/bin/env python3
"""seek_pg — PostgreSQL semantic search engine."""

import os
import sys
import json
from pathlib import Path

# Import PostgreSQL versions of modules
from .config import load_config
from .search_pg import search_pg, status_pg, reindex_pg, delete_source_pg


USAGE = """\
seek_pg — PostgreSQL semantic search engine

Usage: seek_pg <command> [args]

Commands:
  search <query>      Hybrid semantic + FTS search
  status              Show index info
  reindex             Force full reindex
  reindex-force       Clear and rebuild index
  delete-source <path> Delete a source from index
  config              Show current config

Examples:
  seek_pg search "my query"
  seek_pg search "my query" --label project1
  seek_pg reindex
  seek_pg status
"""


def fmt_rows(rows):
    if not rows:
        return "(no results)"
    lines = []
    for row in rows:
        parts = []
        for k, v in row.items():
            if v is not None:
                parts.append(f"{k}: {v}")
        lines.append(" | ".join(parts))
    return "\n".join(lines)


def cmd_search(args):
    if not args:
        print("Usage: seek_pg search <query> [--label LABEL]")
        return

    query = " ".join(args)
    label = None
    
    # Check for --label argument
    if "--label" in args:
        label_idx = args.index("--label")
        if label_idx + 1 < len(args):
            label = args[label_idx + 1]
        # Remove label args from query
        query_parts = []
        i = 0
        while i < len(args):
            if args[i] == "--label":
                i += 2  # Skip label and its value
            else:
                query_parts.append(args[i])
                i += 1
        query = " ".join(query_parts)

    results = search_pg(query, top_k=10, mode="hybrid", label=label)
    print(fmt_rows(results))


def cmd_status():
    stats = status_pg()
    print(f"Database: PostgreSQL ({stats['db_name']})")
    print(f"Database size: {stats['db_size']}")
    print(f"Total chunks: {stats['total_chunks']}")
    print(f"Total sources: {stats['total_sources']}")
    print(f"Labels: {', '.join(stats['labels']) if stats['labels'] else 'None'}")


def cmd_reindex(args):
    force = args[0] == "force" if args else False
    label = None
    
    # Check for --label argument
    if "--label" in args:
        label_idx = args.index("--label")
        if label_idx + 1 < len(args):
            label = args[label_idx + 1]
    
    reindex_pg(force=force, label=label)


def cmd_delete_source(args):
    if not args:
        print("Usage: seek_pg delete-source <path>")
        return
    path = args[0]
    delete_source_pg(path)


def cmd_config():
    cfg = load_config()
    print(json.dumps(cfg, indent=2))


def main():
    args = sys.argv[1:]
    if not args:
        print(USAGE)
        return

    cmd = args[0]
    rest = args[1:]

    commands = {
        "search": lambda: cmd_search(rest),
        "status": lambda: cmd_status(),
        "reindex": lambda: cmd_reindex(rest),
        "reindex-force": lambda: cmd_reindex(["force"]),
        "delete-source": lambda: cmd_delete_source(rest),
        "config": lambda: cmd_config(),
    }

    if cmd in commands:
        commands[cmd]()
    else:
        print(f"Unknown command: {cmd}")
        print(USAGE)


if __name__ == "__main__":
    main()