#!/usr/bin/env python3
"""
PostgreSQL Real-time Synchronization Service

This script monitors file system changes and database updates to trigger synchronization
between memory files and PostgreSQL project tracker/family planning databases.
"""

import os
import psycopg2
import threading
import time
from datetime import datetime
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from .sync_engine_pg import MemorySync


class DatabaseChangeDetector:
    """Monitor PostgreSQL database changes using polling of change_log table."""
    
    def __init__(self, db_host=None, db_port=None, db_name=None, db_user=None, db_password=None, db_key=None, callback=None):
        self.db_host = db_host or os.environ.get("PT_DB_HOST", "localhost")
        self.db_port = db_port or int(os.environ.get("PT_DB_PORT", 5433))
        self.db_name = db_name or os.environ.get("PT_DB_NAME", "financial_analysis")
        self.db_user = db_user or os.environ.get("PT_DB_USER", "finance_user")
        self.db_password = db_password or os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
        self.db_key = db_key  # 'pt' or 'fp'
        self.callback = callback
        self.last_check = datetime.min
        self.running = False
        self.thread = None
        
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
        
    def start_monitoring(self):
        self.running = True
        self.thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.thread.start()
        
    def stop_monitoring(self):
        self.running = False
        if self.thread:
            self.thread.join(timeout=2)
    
    def _monitor_loop(self):
        while self.running:
            changes = self._check_for_changes()
            if changes:
                for change in changes:
                    self.callback(
                        'database', 
                        self.db_key,
                        change['operation'], 
                        change['table_name'],
                        change['record_id'],
                        change['timestamp']
                    )
            time.sleep(5)  # Check every 5 seconds
    
    def _check_for_changes(self):
        """Check for new changes since last check."""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT * FROM change_log 
            WHERE timestamp > %s
            ORDER BY timestamp DESC
        """, (self.last_check,))
        
        rows = cursor.fetchall()
        col_names = [desc[0] for desc in cursor.description]
        conn.close()
        
        changes = []
        for row in rows:
            # Convert tuple to dict using column names
            row_dict = {col_names[i]: row[i] for i in range(len(col_names))}
            changes.append({
                'id': row_dict['id'],
                'table_name': row_dict['table_name'],
                'operation': row_dict['operation'],
                'record_id': row_dict['record_id'],
                'timestamp': row_dict['timestamp']
            })
        
        if changes:
            # Update last check time to the newest change
            self.last_check = max(change['timestamp'] for change in changes)
        
        return changes


class MemoryFileSyncHandler(FileSystemEventHandler):
    """Handle file system events for memory files."""
    
    def __init__(self, sync_callback):
        super().__init__()
        self.sync_callback = sync_callback
        self.last_modified = {}
        
    def on_modified(self, event):
        if not event.is_directory and event.src_path.endswith('.md'):
            # Debounce rapid file changes
            current_time = time.time()
            if event.src_path in self.last_modified:
                if current_time - self.last_modified[event.src_path] < 2:  # 2 second debounce
                    return
            self.last_modified[event.src_path] = current_time
            
            print(f"Detected change in memory file: {event.src_path}")
            self.sync_callback('memory_file', 'modified', event.src_path)


class RealTimeSyncService:
    """Main service to coordinate PostgreSQL real-time synchronization."""
    
    def __init__(self, db_host=None, db_port=None, db_name=None, db_user=None, db_password=None):
        self.db_host = db_host or os.environ.get("PT_DB_HOST", "localhost")
        self.db_port = db_port or int(os.environ.get("PT_DB_PORT", 5433))
        self.db_name = db_name or os.environ.get("PT_DB_NAME", "financial_analysis")
        self.db_user = db_user or os.environ.get("PT_DB_USER", "finance_user")
        self.db_password = db_password or os.environ.get("PT_DB_PASSWORD", "secure_finance_password")
        
        self.memory_sync = MemorySync(
            db_host=self.db_host,
            db_port=self.db_port,
            db_name=self.db_name,
            db_user=self.db_user,
            db_password=self.db_password
        )
        self.observer = Observer()
        self.db_monitors = []
        self.running = False
        self.service_id = f"sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
    def _sync_callback(self, source_type, action, *args):
        """Callback triggered when changes are detected."""
        print(f"Change detected - {source_type} {action}, triggering sync...")
        
        if source_type == 'memory_file':
            if action == 'modified':
                file_path = args[0]
                print(f"Syncing {file_path} to PostgreSQL database...")
                try:
                    # Sync the changed file to database
                    count = self.memory_sync.sync_memory_to_db(file_path, "openclaw")
                    print(f"Synced {count} items from {file_path} to PostgreSQL database")
                except Exception as e:
                    print(f"Error syncing {file_path}: {e}")
        
        elif source_type == 'database':
            db_key = args[0]  # 'pt' or 'fp'
            operation = args[1]
            table_name = args[2]
            record_id = args[3]
            timestamp = args[4]
            
            print(f"Database {db_key}.{table_name} changed ({operation} ID:{record_id}) at {timestamp}")
            
            # Determine sync direction based on configuration
            # For now, we'll sync database changes back to memory as well
            if db_key == 'pt':
                self._sync_database_to_memory(db_key, table_name, record_id)
            elif db_key == 'fp':
                self._sync_database_to_memory(db_key, table_name, record_id)
    
    def _sync_database_to_memory(self, db_key, table_name, record_id):
        """Sync specific database record to memory files."""
        print(f"Syncing {db_key}.{table_name} ID:{record_id} to memory files...")
        
        # For now, we'll do a full export to update memory files
        # In a more refined implementation, we would extract just the changed record
        output_file = f"memory/db_export_{db_key}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        try:
            if db_key == 'pt':
                count = self.memory_sync.export_db_to_memory("openclaw", output_file)
                print(f"Exported {count} entries from {db_key} database to {output_file}")
            elif db_key == 'fp':
                # Family planning would need a different export function
                print(f"Export from {db_key} to memory not fully implemented yet")
        except Exception as e:
            print(f"Error exporting {db_key} database to memory: {e}")
    
    def start_service(self):
        """Start the PostgreSQL real-time synchronization service."""
        print(f"Starting PostgreSQL real-time synchronization service: {self.service_id}...")
        
        # Setup file system monitoring
        memory_dir = os.path.expanduser("~/.openclaw/workspace/memory")
        if os.path.exists(memory_dir):
            file_handler = MemoryFileSyncHandler(self._sync_callback)
            self.observer.schedule(file_handler, memory_dir, recursive=True)
            self.observer.start()
            print(f"Started monitoring memory directory: {memory_dir}")
        
        # Setup database monitoring for project tracker
        # In PostgreSQL version, we assume the database exists and is accessible
        try:
            pt_monitor = DatabaseChangeDetector(
                db_host=self.db_host,
                db_port=self.db_port,
                db_name=self.db_name,
                db_user=self.db_user,
                db_password=self.db_password,
                db_key='pt',  # Project Tracker
                callback=self._sync_callback
            )
            pt_monitor.start_monitoring()
            self.db_monitors.append(pt_monitor)
            print(f"Started monitoring PostgreSQL project tracker database")
        except Exception as e:
            print(f"Warning: Could not start monitoring project tracker database: {e}")
        
        # Setup database monitoring for family planning
        try:
            fp_monitor = DatabaseChangeDetector(
                db_host=self.db_host,
                db_port=self.db_port,
                db_name=self.db_name,
                db_user=self.db_user,
                db_password=self.db_password,
                db_key='fp',  # Family Planning
                callback=self._sync_callback
            )
            fp_monitor.start_monitoring()
            self.db_monitors.append(fp_monitor)
            print(f"Started monitoring PostgreSQL family planning database")
        except Exception as e:
            print(f"Warning: Could not start monitoring family planning database: {e}")
        
        self.running = True
        print(f"PostgreSQL real-time synchronization service {self.service_id} started successfully!")
        
    def stop_service(self):
        """Stop the PostgreSQL real-time synchronization service."""
        print(f"Stopping PostgreSQL real-time synchronization service: {self.service_id}...")
        
        self.observer.stop()
        self.observer.join()
        
        for monitor in self.db_monitors:
            monitor.stop_monitoring()
        
        self.running = False
        print(f"PostgreSQL real-time synchronization service {self.service_id} stopped.")


def main():
    """Main function to run the PostgreSQL real-time sync service."""
    service = RealTimeSyncService()
    
    try:
        service.start_service()
        print("Service is running. Press Ctrl+C to stop.")
        
        # Keep the service running
        while service.running:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nReceived interrupt signal. Stopping service...")
    finally:
        service.stop_service()


if __name__ == "__main__":
    main()