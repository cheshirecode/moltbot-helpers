"""
PostgreSQL Memory Manager for OpenClaw

This module provides enhanced memory management capabilities that integrate
with the semantic search system to improve recall and context using PostgreSQL.
"""
import os
import json
import psycopg2
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class MemoryManager:
    """
    Enhanced memory system that integrates semantic search capabilities
    to improve recall and context using PostgreSQL.
    """
    
    def __init__(self, memory_dir: str = None, db_host: str = None, db_port: int = None, db_name: str = None, db_user: str = None, db_password: str = None):
        """Initialize the memory manager with PostgreSQL connection."""
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory")
        
        # PostgreSQL connection parameters
        self.db_host = db_host or os.environ.get("PT_DB_HOST", "localhost")
        self.db_port = db_port or int(os.environ.get("PT_DB_PORT", 5433))
        self.db_name = db_name or os.environ.get("PT_DB_NAME", "financial_analysis")
        self.db_user = db_user or os.environ.get("PT_DB_USER", "finance_user")
        self.db_password = db_password or os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
        
        # Ensure memory directory exists
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize database for memory metadata
        self._init_db()
    
    def get_connection(self):
        """Get a PostgreSQL database connection."""
        conn = psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )
        return conn
    
    def _init_db(self):
        """Initialize the memory metadata database."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create table for memory metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_metadata (
                id SERIAL PRIMARY KEY,
                memory_id VARCHAR(255) UNIQUE NOT NULL,
                title TEXT,
                content_preview TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                importance REAL DEFAULT 0.5  -- 0.0 to 1.0 scale
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mem_timestamp ON memory_metadata(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mem_tags ON memory_metadata(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_mem_importance ON memory_metadata(importance)")
        
        conn.commit()
        conn.close()
    
    def store_memory(self, title: str, content: str, tags: List[str] = None, importance: float = 0.5) -> str:
        """
        Store a memory with semantic indexing.
        
        Args:
            title: Title of the memory
            content: Content of the memory
            tags: List of tags for categorization
            importance: Importance rating (0.0 to 1.0)
        
        Returns:
            Memory ID for reference
        """
        from seek.cli import cmd_index
        import tempfile
        
        # Generate a unique memory ID
        memory_id = f"mem_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{hash(title) % 10000}"
        
        # Create memory file
        memory_file = os.path.join(self.memory_dir, f"{memory_id}.md")
        
        with open(memory_file, 'w') as f:
            f.write(f"# {title}\n\n")
            f.write(f"**Timestamp:** {datetime.now().isoformat()}\n\n")
            f.write(f"**Tags:** {', '.join(tags) if tags else 'none'}\n\n")
            f.write(f"**Importance:** {importance}\n\n")
            f.write(content)
        
        # Store metadata in PostgreSQL database
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memory_metadata (memory_id, title, content_preview, tags, importance)
            VALUES (%s, %s, %s, %s, %s)
            ON CONFLICT (memory_id) DO UPDATE SET
                title = EXCLUDED.title,
                content_preview = EXCLUDED.content_preview,
                tags = EXCLUDED.tags,
                importance = EXCLUDED.importance,
                timestamp = CURRENT_TIMESTAMP
        """, (
            memory_id,
            title,
            content[:200] + "..." if len(content) > 200 else content,  # Preview of first 200 chars
            ','.join(tags) if tags else '',
            importance
        ))
        
        conn.commit()
        conn.close()
        
        # Index the memory file with seek for semantic search
        try:
            from seek.config import load_config
            cfg = load_config()
            conn = psycopg2.connect(
                host=os.environ.get("PT_DB_HOST", "localhost"),
                port=int(os.environ.get("PT_DB_PORT", 5433)),
                database=os.environ.get("PT_DB_NAME", "financial_analysis"),
                user=os.environ.get("PT_DB_USER", "finance_user"),
                password=os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
            )
            
            # Import necessary functions from seek modules
            from seek.indexer import chunk_markdown, embed, upsert_chunks_pg
            from seek.store import init_db
            
            # Re-initialize the DB connection properly
            conn = init_db(cfg["dbPath"])
            
            # Chunk and embed the memory file
            chunks = chunk_markdown(memory_file, cfg.get("chunkSize", 256), cfg.get("chunkOverlap", 32))
            
            if chunks:
                texts = [c[0] for c in chunks]
                embeddings = embed(texts, cfg["model"])
                upsert_chunks_pg(conn, memory_file, "openclaw-memory", chunks, embeddings)
            
            conn.close()
        except Exception as e:
            print(f"Warning: Could not index memory with seek: {e}")
        
        return memory_id
    
    def search_memories(self, query: str, limit: int = 10, min_importance: float = 0.0) -> List[Dict[str, Any]]:
        """
        Search memories using semantic search capabilities.
        
        Args:
            query: Search query
            limit: Maximum number of results
            min_importance: Minimum importance threshold
        
        Returns:
            List of matching memories with relevance scores
        """
        # First, try semantic search through the seek system
        try:
            from seek_pg.search import hybrid_search
            from seek_pg.config import load_config
            from seek_pg.store import init_db
            
            cfg = load_config()
            conn = init_db(cfg["dbPath"])
            
            # Embed the query
            from seek_pg.indexer import embed
            query_embedding = embed([query], cfg["model"])[0]
            
            # Search for relevant content in the seek database
            results = hybrid_search(conn, query, query_embedding, top_k=limit, mode="hybrid")
            
            # Filter results to only include memory files
            memory_results = []
            for r in results:
                source_path = r["source_path"]
                if "memory" in source_path.lower() or source_path.startswith(self.memory_dir):
                    memory_results.append({
                        "memory_id": os.path.basename(source_path).replace('.md', ''),
                        "title": r["chunk_text"][:100],  # Use first part of chunk as title
                        "content_preview": r["chunk_text"],
                        "relevance_score": r.get("score", 0.0),
                        "source_path": source_path
                    })
            
            conn.close()
            return memory_results
        except Exception as e:
            print(f"Semantic search failed: {e}")
            # Fallback to metadata search
            return self._search_metadata_fallback(query, limit, min_importance)
    
    def _search_metadata_fallback(self, query: str, limit: int = 10, min_importance: float = 0.0) -> List[Dict[str, Any]]:
        """Fallback search in memory metadata."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Simple text search in title and tags
        cursor.execute("""
            SELECT memory_id, title, content_preview, importance, timestamp
            FROM memory_metadata
            WHERE (title ILIKE %s OR tags ILIKE %s)
            AND importance >= %s
            ORDER BY importance DESC
            LIMIT %s
        """, (f'%{query}%', f'%{query}%', min_importance, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "memory_id": row[0],
                "title": row[1],
                "content_preview": row[2],
                "relevance_score": row[3],  # Using importance as relevance score for fallback
                "timestamp": row[4]
            })
        
        return results
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific memory by ID."""
        # Get metadata from PostgreSQL database
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM memory_metadata WHERE memory_id = %s", (memory_id,))
        row = cursor.fetchone()
        # Get column names
        col_names = [desc[0] for desc in cursor.description]
        conn.close()
        
        if not row:
            return None
        
        # Read the actual memory file
        memory_file = os.path.join(self.memory_dir, f"{memory_id}.md")
        if os.path.exists(memory_file):
            with open(memory_file, 'r') as f:
                content = f.read()
        else:
            content = row[2]  # Use preview from metadata if file doesn't exist
        
        # Convert tuple to dict using column names
        row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
        
        return {
            "memory_id": row_dict['memory_id'],
            "title": row_dict['title'],
            "content": content,
            "timestamp": row_dict['timestamp'],
            "tags": row_dict['tags'].split(',') if row_dict['tags'] else [],
            "importance": row_dict['importance']
        }
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent memories."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT memory_id, title, content_preview, timestamp, tags, importance
            FROM memory_metadata
            ORDER BY timestamp DESC
            LIMIT %s
        """, (limit,))
        
        rows = cursor.fetchall()
        # Get column names
        col_names = [desc[0] for desc in cursor.description]
        conn.close()
        
        results = []
        for row in rows:
            # Convert tuple to dict using column names
            row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
            results.append({
                "memory_id": row_dict['memory_id'],
                "title": row_dict['title'],
                "content_preview": row_dict['content_preview'],
                "timestamp": row_dict['timestamp'],
                "tags": row_dict['tags'].split(',') if row_dict['tags'] else [],
                "importance": row_dict['importance']
            })
        
        return results
    
    def get_high_importance_memories(self, limit: int = 10, min_importance: float = 0.7) -> List[Dict[str, Any]]:
        """Get high importance memories."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT memory_id, title, content_preview, timestamp, tags, importance
            FROM memory_metadata
            WHERE importance >= %s
            ORDER BY importance DESC
            LIMIT %s
        """, (min_importance, limit))
        
        rows = cursor.fetchall()
        # Get column names
        col_names = [desc[0] for desc in cursor.description]
        conn.close()
        
        results = []
        for row in rows:
            # Convert tuple to dict using column names
            row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
            results.append({
                "memory_id": row_dict['memory_id'],
                "title": row_dict['title'],
                "content_preview": row_dict['content_preview'],
                "timestamp": row_dict['timestamp'],
                "tags": row_dict['tags'].split(',') if row_dict['tags'] else [],
                "importance": row_dict['importance']
            })
        
        return results


def main():
    """Example usage of the memory manager."""
    manager = MemoryManager()
    
    # Example: Store a memory
    memory_id = manager.store_memory(
        title="Example Memory",
        content="This is an example of how the enhanced memory system works. It integrates with semantic search to improve recall.",
        tags=["example", "memory", "test"],
        importance=0.8
    )
    
    print(f"Stored memory with ID: {memory_id}")
    
    # Example: Search for memories
    results = manager.search_memories("how the enhanced memory system works")
    print(f"\nFound {len(results)} matching memories:")
    for result in results:
        print(f"- {result['title']} (ID: {result['memory_id']}, Score: {result['relevance_score']:.2f})")
    
    # Example: Get a specific memory
    memory = manager.get_memory(memory_id)
    if memory:
        print(f"\nRetrieved memory: {memory['title']}")
        print(f"Content preview: {memory['content'][:100]}...")


if __name__ == "__main__":
    main()