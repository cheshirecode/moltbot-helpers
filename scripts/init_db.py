#!/usr/bin/env python3
"""
Unified database initialization for moltbot-helpers.

Creates all required tables for:
- pt (project_tracker)
- fp (fp_* tables)
- seek (seek_* tables)

All tools share the same PostgreSQL database.
"""

import os
import sys
import psycopg2

# Shared connection settings
DB_HOST = os.environ.get("PT_DB_HOST", "localhost")
DB_PORT = int(os.environ.get("PT_DB_PORT", 5433))
DB_NAME = os.environ.get("PT_DB_NAME", "financial_analysis")
DB_USER = os.environ.get("PT_DB_USER", "finance_user")
DB_PASSWORD = os.environ.get("PT_DB_PASSWORD", "secure_finance_password")


def get_connection():
    """Establish connection to PostgreSQL."""
    try:
        conn = psycopg2.connect(
            host=DB_HOST,
            port=DB_PORT,
            database=DB_NAME,
            user=DB_USER,
            password=DB_PASSWORD
        )
        return conn
    except Exception as e:
        print(f"Error connecting to PostgreSQL: {e}")
        sys.exit(1)


def init_project_tracker(cur):
    """Initialize project_tracker table for pt tool."""
    print("Creating project_tracker table...")
    cur.execute("""
        CREATE TABLE IF NOT EXISTS project_tracker (
            id SERIAL PRIMARY KEY,
            project TEXT NOT NULL,
            category TEXT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT,
            status TEXT DEFAULT 'new',
            impact TEXT,
            tech_debt_level TEXT,
            created_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            tags JSONB DEFAULT '[]'::jsonb
        )
    """)
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pt_project ON project_tracker(project)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pt_status ON project_tracker(status)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_pt_tags ON project_tracker USING GIN(tags)")
    print("  ✓ project_tracker")


def init_family_planner(cur):
    """Initialize fp_* tables for fp tool."""
    print("Creating family planner tables...")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_people (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            relation TEXT,
            dob DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ fp_people")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_documents (
            id SERIAL PRIMARY KEY,
            person_id INTEGER REFERENCES fp_people(id),
            doc_type TEXT NOT NULL,
            doc_number TEXT,
            country TEXT,
            issued DATE,
            expires DATE,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ fp_documents")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_key_dates (
            id SERIAL PRIMARY KEY,
            label TEXT NOT NULL,
            date DATE,
            category TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ fp_key_dates")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_finances (
            id SERIAL PRIMARY KEY,
            category TEXT,
            asset_type TEXT,
            country TEXT,
            key TEXT NOT NULL,
            value TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ fp_finances")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_tasks (
            id SERIAL PRIMARY KEY,
            action TEXT NOT NULL,
            status TEXT DEFAULT 'OPEN',
            priority TEXT DEFAULT 'P2',
            due_date DATE,
            category TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ fp_tasks")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_facts (
            id SERIAL PRIMARY KEY,
            topic TEXT NOT NULL,
            key TEXT NOT NULL,
            value TEXT,
            source TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ fp_facts")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS fp_addresses (
            id SERIAL PRIMARY KEY,
            person_id INTEGER REFERENCES fp_people(id),
            address_type TEXT,
            street TEXT,
            city TEXT,
            state TEXT,
            postal_code TEXT,
            country TEXT,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    print("  ✓ fp_addresses")


def init_seek(cur):
    """Initialize seek_* tables for semantic search."""
    print("Creating seek tables...")
    
    cur.execute("""
        CREATE TABLE IF NOT EXISTS seek_file_meta (
            source_path TEXT PRIMARY KEY,
            label TEXT,
            mtime DOUBLE PRECISION,
            indexed_at DOUBLE PRECISION
        )
    """)
    print("  ✓ seek_file_meta")
    
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
    cur.execute("CREATE INDEX IF NOT EXISTS idx_seek_source ON seek_chunks(source_path)")
    cur.execute("CREATE INDEX IF NOT EXISTS idx_seek_label ON seek_chunks(label)")
    print("  ✓ seek_chunks")


def main():
    print(f"Connecting to PostgreSQL at {DB_HOST}:{DB_PORT}/{DB_NAME}...")
    conn = get_connection()
    cur = conn.cursor()
    
    print("\n=== Initializing moltbot-helpers database ===\n")
    
    init_project_tracker(cur)
    init_family_planner(cur)
    init_seek(cur)
    
    conn.commit()
    conn.close()
    
    print("\n=== Database initialization complete ===")
    print(f"\nConnection info:")
    print(f"  Host: {DB_HOST}")
    print(f"  Port: {DB_PORT}")
    print(f"  Database: {DB_NAME}")
    print(f"  User: {DB_USER}")


if __name__ == "__main__":
    main()
