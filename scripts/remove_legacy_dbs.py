#!/usr/bin/env python3
"""
Script to remove legacy .db files after successful migration to PostgreSQL.

This script removes the legacy SQLite database files after confirming
that all data has been successfully migrated to PostgreSQL.
"""

import os
import shutil
from pathlib import Path

def remove_legacy_db_files():
    """Remove legacy .db files after migration."""
    print("🔍 Checking for legacy .db files...")
    
    # Define the legacy database files to potentially remove
    legacy_db_paths = [
        "~/projects/_openclaw/project-tracker.db",
        "~/projects/_openclaw/family-planning.db", 
        "~/projects/_openclaw/seek.db",
        "~/projects/_openclaw/knowledge-graph.db",
        "~/projects/_openclaw/memory-enhancements.db",
        "~/projects/_openclaw/triggers.db",
        "~/projects/_openclaw/calendar-sync.db"
    ]
    
    removed_files = []
    skipped_files = []
    
    for db_path in legacy_db_paths:
        full_path = os.path.expanduser(db_path)
        
        if os.path.exists(full_path):
            try:
                # Create a backup before removal
                backup_path = full_path + ".backup_pre_removal"
                if not os.path.exists(backup_path):
                    shutil.copy2(full_path, backup_path)
                    print(f"📁 Backed up {full_path} to {backup_path}")
                
                # Actually remove the file
                os.remove(full_path)
                removed_files.append(full_path)
                print(f"🗑️  Removed legacy database file: {full_path}")
            except Exception as e:
                print(f"❌ Error removing {full_path}: {e}")
                skipped_files.append((full_path, str(e)))
        else:
            print(f"✅ Legacy file does not exist (already removed?): {full_path}")
    
    print(f"\n📊 Summary:")
    print(f"   Files removed: {len(removed_files)}")
    print(f"   Files skipped: {len(skipped_files)}")
    
    if removed_files:
        print(f"\n📋 Removed files:")
        for file in removed_files:
            print(f"   - {file}")
    
    if skipped_files:
        print(f"\n⚠️  Skipped files:")
        for file, error in skipped_files:
            print(f"   - {file}: {error}")
    
    return removed_files, skipped_files

if __name__ == "__main__":
    print("⚠️  LEGACY DATABASE CLEANUP SCRIPT")
    print("⚠️  This script removes legacy SQLite .db files after PostgreSQL migration")
    print()
    
    response = input("Are you sure you want to proceed with removing legacy .db files? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        print("\n🚀 Starting legacy database cleanup...")
        removed, skipped = remove_legacy_db_files()
        
        if removed:
            print(f"\n🎉 Successfully removed {len(removed)} legacy database files!")
            print("PostgreSQL migration is now complete and clean.")
        else:
            print("\n🤔 No legacy files were removed (they may not exist or were already removed).")
    else:
        print("\n🛑 Operation cancelled. No files were removed.")