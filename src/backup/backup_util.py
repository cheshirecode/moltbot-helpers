"""
Backup Utility for Moltbot/OpenClaw Systems

This module provides comprehensive backup and restore functionality
for OpenClaw/Moltbot systems, including databases, configuration files,
and memory files.

Backs up:
- OpenClaw workspace memory files: ~/.openclaw/workspace/memory/
- Main memory file: ~/.openclaw/workspace/MEMORY.md
- Project databases: ~/projects/_openclaw/
- Seek configuration: ~/.config/seek/config.json
- All project databases in ~/projects/_openclaw/
"""

import os
import tarfile
import shutil
import json
import argparse
from datetime import datetime
from pathlib import Path
import subprocess


class MoltbotBackup:
    def __init__(self, base_dir=None, destination=None):
        """
        Initialize the backup utility.
        
        Args:
            base_dir (str): Base directory to backup (defaults to ~)
            destination (str): Destination directory for backups (defaults to ~/Dropbox/Apps/moltbot-backups/)
        """
        self.base_dir = base_dir or os.path.expanduser("~")
        self.destination = destination or os.path.expanduser("~/Dropbox/Apps/moltbot-backups/")
        self.timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        self.backup_filename = f"moltbot-backup-{self.timestamp}.tar.gz"
        
        # Define paths to backup (relative to base_dir)
        self.paths_to_backup = [
            ".openclaw/workspace/memory/",
            ".openclaw/workspace/MEMORY.md",
            "projects/_openclaw/"
        ]
        
        # Additional critical files (absolute paths from user home)
        # NOTE: We don't include project database files here since they're already
        # included in the projects/_openclaw/ directory backup
        self.critical_files = [
            ".config/seek/config.json"
        ]

    def create_backup(self):
        """Create a backup archive."""
        # Ensure destination directory exists
        os.makedirs(self.destination, exist_ok=True)
        
        backup_path = os.path.join(self.destination, self.backup_filename)
        
        print(f"Creating backup: {backup_path}")
        print(f"Base directory: {self.base_dir}")
        
        with tarfile.open(backup_path, "w:gz") as tar:
            # Backup primary paths
            for rel_path in self.paths_to_backup:
                full_path = os.path.join(self.base_dir, rel_path)
                if os.path.exists(full_path):
                    print(f"Adding {full_path} to backup...")
                    tar.add(full_path, arcname=rel_path)
                else:
                    print(f"Warning: Path does not exist: {full_path}")
            
            # Backup critical files from various locations
            for file_path in self.critical_files:
                full_path = os.path.expanduser(file_path)
                if os.path.exists(full_path):
                    print(f"Adding {full_path} to backup...")
                    # Use a logical archive name
                    arcname = file_path.replace("/", "_")
                    tar.add(full_path, arcname=arcname)
                else:
                    print(f"Warning: Critical file does not exist: {full_path}")
        
        print(f"Backup completed: {backup_path}")
        return backup_path

    def restore_backup(self, backup_file, restore_to=None):
        """
        Restore from a backup archive.
        
        Args:
            backup_file (str): Path to the backup file
            restore_to (str): Directory to restore to (defaults to base_dir)
        """
        restore_to = restore_to or self.base_dir
        
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file does not exist: {backup_file}")
        
        print(f"Restoring from {backup_file} to {restore_to}")
        
        # Create restore directory if it doesn't exist
        os.makedirs(restore_to, exist_ok=True)
        
        with tarfile.open(backup_file, "r:gz") as tar:
            tar.extractall(path=restore_to)
        
        print(f"Restore completed to: {restore_to}")

    def list_backup_contents(self, backup_file):
        """List contents of a backup file."""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file does not exist: {backup_file}")
        
        with tarfile.open(backup_file, "r:gz") as tar:
            members = tar.getmembers()
            for member in members:
                print(member.name)

    def get_backup_info(self, backup_file):
        """Get information about a backup file."""
        if not os.path.exists(backup_file):
            raise FileNotFoundError(f"Backup file does not exist: {backup_file}")
        
        info = {
            'filename': os.path.basename(backup_file),
            'size': os.path.getsize(backup_file),
            'modified': datetime.fromtimestamp(os.path.getmtime(backup_file)),
            'contents': []
        }
        
        with tarfile.open(backup_file, "r:gz") as tar:
            members = tar.getmembers()
            for member in members:
                info['contents'].append({
                    'name': member.name,
                    'size': member.size,
                    'modified': datetime.fromtimestamp(member.mtime) if member.mtime else None
                })
        
        return info


def main():
    parser = argparse.ArgumentParser(description="Moltbot/OpenClaw Backup Utility")
    parser.add_argument("action", choices=["create", "restore", "list", "info"], 
                        help="Action to perform")
    parser.add_argument("--base-dir", help="Base directory to backup (default: ~/clawd)")
    parser.add_argument("--destination", help="Destination for backup (default: ~/Dropbox/Apps/moltbot-backups/)")
    parser.add_argument("--backup-file", help="Backup file for restore/list/info actions")
    parser.add_argument("--restore-to", help="Directory to restore to (default: base-dir)")
    
    args = parser.parse_args()
    
    backup_util = MoltbotBackup(base_dir=args.base_dir, destination=args.destination)
    
    if args.action == "create":
        backup_path = backup_util.create_backup()
        print(f"Backup created successfully: {backup_path}")
        
    elif args.action == "restore":
        if not args.backup_file:
            parser.error("--backup-file is required for restore action")
        backup_util.restore_backup(args.backup_file, args.restore_to)
        print("Restore completed successfully")
        
    elif args.action == "list":
        if not args.backup_file:
            parser.error("--backup-file is required for list action")
        backup_util.list_backup_contents(args.backup_file)
        
    elif args.action == "info":
        if not args.backup_file:
            parser.error("--backup-file is required for info action")
        info = backup_util.get_backup_info(args.backup_file)
        print(f"Backup: {info['filename']}")
        print(f"Size: {info['size']} bytes")
        print(f"Modified: {info['modified']}")
        print(f"Contents ({len(info['contents'])} items):")
        for item in info['contents']:
            print(f"  {item['name']} - {item['size']} bytes - {item['modified']}")


if __name__ == "__main__":
    main()