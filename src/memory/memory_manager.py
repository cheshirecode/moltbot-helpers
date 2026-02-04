"""
Memory Manager for OpenClaw

This module provides enhanced memory management capabilities that integrate
with the semantic search system to improve recall and context.
"""
import os
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path


class MemoryManager:
    """
    Enhanced memory system that integrates semantic search capabilities
    to improve recall and context.
    """
    
    def __init__(self, memory_dir: str = None, db_path: str = None):
        """Initialize the memory manager."""
        self.memory_dir = memory_dir or os.path.expanduser("~/.openclaw/workspace/memory")
        self.db_path = db_path or os.path.expanduser("~/projects/_openclaw/memory-enhancements.db")
        
        # Ensure memory directory exists
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        
        # Initialize database for memory metadata
        self._init_db()
    
    def _init_db(self):
        """Initialize the memory metadata database."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create table for memory metadata
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS memory_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                memory_id TEXT UNIQUE NOT NULL,
                title TEXT,
                content_preview TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                tags TEXT,
                importance REAL DEFAULT 0.5  -- 0.0 to 1.0 scale
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON memory_metadata(timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_tags ON memory_metadata(tags)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_importance ON memory_metadata(importance)")
        
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
        
        # Store metadata in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            INSERT INTO memory_metadata (memory_id, title, content_preview, tags, importance)
            VALUES (?, ?, ?, ?, ?)
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
            conn = sqlite3.connect(cfg["dbPath"])
            
            # Import necessary functions from seek modules
            from seek.indexer import chunk_markdown, embed, upsert_chunks
            from seek.store import init_db
            
            # Re-initialize the DB connection properly
            conn = init_db(cfg["dbPath"])
            
            # Chunk and embed the memory file
            chunks = chunk_markdown(memory_file, cfg.get("chunkSize", 256), cfg.get("chunkOverlap", 32))
            
            if chunks:
                texts = [c[0] for c in chunks]
                embeddings = embed(texts, cfg["model"])
                upsert_chunks(conn, memory_file, "openclaw-memory", chunks, embeddings)
            
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
            from seek.search import hybrid_search
            from seek.config import load_config
            from seek.store import init_db
            
            cfg = load_config()
            conn = init_db(cfg["dbPath"])
            
            # Embed the query
            from seek.indexer import embed
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
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Simple text search in title and tags
        cursor.execute("""
            SELECT memory_id, title, content_preview, importance, timestamp
            FROM memory_metadata
            WHERE (title LIKE ? OR tags LIKE ?)
            AND importance >= ?
            ORDER BY importance DESC
            LIMIT ?
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
        # Get metadata from database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM memory_metadata WHERE memory_id = ?", (memory_id,))
        row = cursor.fetchone()
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
        
        return {
            "memory_id": row[1],
            "title": row[2],
            "content": content,
            "timestamp": row[4],
            "tags": row[5].split(',') if row[5] else [],
            "importance": row[6]
        }
    
    def get_recent_memories(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get the most recent memories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT memory_id, title, content_preview, timestamp, tags, importance
            FROM memory_metadata
            ORDER BY timestamp DESC
            LIMIT ?
        """, (limit,))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "memory_id": row[0],
                "title": row[1],
                "content_preview": row[2],
                "timestamp": row[3],
                "tags": row[4].split(',') if row[4] else [],
                "importance": row[5]
            })
        
        return results
    
    def get_high_importance_memories(self, limit: int = 10, min_importance: float = 0.7) -> List[Dict[str, Any]]:
        """Get high importance memories."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT memory_id, title, content_preview, timestamp, tags, importance
            FROM memory_metadata
            WHERE importance >= ?
            ORDER BY importance DESC
            LIMIT ?
        """, (min_importance, limit))
        
        rows = cursor.fetchall()
        conn.close()
        
        results = []
        for row in rows:
            results.append({
                "memory_id": row[0],
                "title": row[1],
                "content_preview": row[2],
                "timestamp": row[3],
                "tags": row[4].split(',') if row[4] else [],
                "importance": row[5]
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