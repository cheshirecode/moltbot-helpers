#!/usr/bin/env python3
"""
Synchronization CLI for OpenClaw

This module provides command-line interface for memory-database synchronization.
"""

import argparse
import os
import sys
from datetime import datetime

# Add the src directory to the path for imports
src_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)))
sys.path.insert(0, src_dir)

from sync.sync_engine import MemorySync
from sync.realtime_sync import RealTimeSyncService
from process_manager import ProcessManager


def cmd_sync_memory_to_db(args):
    """Sync memory files to database."""
    sync = MemorySync()
    if args.file:
        count = sync.sync_memory_to_db(args.file, args.project)
        print(f"Synced {count} tasks from {args.file} to database")
    else:
        memory_dir = os.path.expanduser("~/.openclaw/workspace/memory")
        results = sync.sync_all_memory_files(memory_dir, args.project)
        total = sum(results.values())
        print(f"Synced {total} tasks from {len(results)} memory files to database")
        for file_path, count in results.items():
            print(f"  {file_path}: {count} tasks")


def cmd_export_db_to_memory(args):
    """Export database to memory file."""
    sync = MemorySync()
    count = sync.export_db_to_memory(args.project, args.output)
    print(f"Exported {count} entries from database to {args.output}")


def cmd_check_consistency(args):
    """Check consistency between memory files and database."""
    sync = MemorySync()
    result = sync.check_consistency(args.project)
    print(f"Consistency check for project '{args.project}':")
    print(f"  Database entries: {result['db_count']}")
    print(f"  Memory tasks: {result['memory_count']}")
    print(f"  Missing in database: {len(result['missing_in_db'])}")
    print(f"  Missing in memory: {len(result['missing_in_memory'])}")
    
    if result['missing_in_db']:
        print("  Missing in database:")
        for item in result['missing_in_db'][:10]:  # Limit output
            print(f"    - {item}")
        if len(result['missing_in_db']) > 10:
            print(f"    ... and {len(result['missing_in_db']) - 10} more")
            
    if result['missing_in_memory']:
        print("  Missing in memory:")
        for item in result['missing_in_memory'][:10]:  # Limit output
            print(f"    - {item}")
        if len(result['missing_in_memory']) > 10:
            print(f"    ... and {len(result['missing_in_memory']) - 10} more")


def cmd_start_service(args):
    """Start the real-time synchronization service."""
    service = RealTimeSyncService()
    
    # Register the service with process manager
    pm = ProcessManager()
    service_id = f"rt_sync_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    print(f"Starting real-time sync service with ID: {service_id}")
    pm.register_process(
        process_id=service_id,
        name="Real-time Sync Service",
        description="Monitors memory files and databases for changes and synchronizes them",
        pid=os.getpid(),  # This won't be accurate, but placeholder
        metadata={"type": "realtime-sync", "config": vars(args)}
    )
    
    try:
        service.start_service()
        print("Service is running. Press Ctrl+C to stop.")
        
        # Keep the service running
        while service.running:
            import time
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nReceived interrupt signal. Stopping service...")
    finally:
        service.stop_service()
        pm.unregister_process(service_id)


def cmd_stop_service(args):
    """Stop the real-time synchronization service."""
    pm = ProcessManager()
    processes = pm.list_processes()
    
    rt_sync_processes = {k: v for k, v in processes.items() 
                         if "realtime-sync" in v.get("metadata", {}).get("type", "")}
    
    if not rt_sync_processes:
        print("No real-time sync services found.")
        return
    
    for proc_id, info in rt_sync_processes.items():
        print(f"Stopping real-time sync service: {proc_id}")
        if pm.kill_process(proc_id):
            print(f"Stopped service {proc_id}")
        else:
            print(f"Failed to stop service {proc_id}")


def main():
    parser = argparse.ArgumentParser(description="Memory-Database Synchronization Tool")
    parser.add_argument("--project", default="openclaw", help="Project name to sync")
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Sync command
    parser_sync = subparsers.add_parser('sync', help='Sync memory files to database')
    parser_sync.add_argument('--file', help='Specific memory file to sync')
    parser_sync.set_defaults(func=cmd_sync_memory_to_db)
    
    # Export command
    parser_export = subparsers.add_parser('export', help='Export database to memory file')
    parser_export.add_argument('--output', required=True, help='Output file for database export')
    parser_export.set_defaults(func=cmd_export_db_to_memory)
    
    # Check command
    parser_check = subparsers.add_parser('check', help='Check consistency between memory and database')
    parser_check.set_defaults(func=cmd_check_consistency)
    
    # Start service command
    parser_start = subparsers.add_parser('start-service', help='Start real-time sync service')
    parser_start.set_defaults(func=cmd_start_service)
    
    # Stop service command
    parser_stop = subparsers.add_parser('stop-service', help='Stop real-time sync service')
    parser_stop.set_defaults(func=cmd_stop_service)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()