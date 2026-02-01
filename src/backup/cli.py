#!/usr/bin/env python3
"""
Backup CLI for Moltbot/OpenClaw Systems

This module provides command-line interface for backup and restore operations.
Backs up OpenClaw workspace files, databases, and configurations.
"""

import os
import sys
import argparse
from datetime import datetime
from .backup_util import MoltbotBackup


def cmd_create_backup(args):
    """Create a backup archive."""
    backup_util = MoltbotBackup(base_dir=args.base_dir, destination=args.destination)
    backup_path = backup_util.create_backup()
    print(f"Backup created successfully: {backup_path}")


def cmd_restore_backup(args):
    """Restore from a backup archive."""
    if not args.backup_file:
        print("Error: --backup-file is required for restore action")
        return
    
    backup_util = MoltbotBackup(base_dir=args.base_dir, destination=args.destination)
    backup_util.restore_backup(args.backup_file, args.restore_to)
    print("Restore completed successfully")


def cmd_list_backup(args):
    """List contents of a backup file."""
    if not args.backup_file:
        print("Error: --backup-file is required for list action")
        return
    
    backup_util = MoltbotBackup(base_dir=args.base_dir, destination=args.destination)
    backup_util.list_backup_contents(args.backup_file)


def cmd_info_backup(args):
    """Get information about a backup file."""
    if not args.backup_file:
        print("Error: --backup-file is required for info action")
        return
    
    backup_util = MoltbotBackup(base_dir=args.base_dir, destination=args.destination)
    info = backup_util.get_backup_info(args.backup_file)
    print(f"Backup: {info['filename']}")
    print(f"Size: {info['size']} bytes")
    print(f"Modified: {info['modified']}")
    print(f"Contents ({len(info['contents'])} items):")
    for item in info['contents']:
        print(f"  {item['name']} - {item['size']} bytes - {item['modified']}")


def main():
    parser = argparse.ArgumentParser(description="Moltbot/OpenClaw Backup Utility")
    parser.add_argument("--base-dir", help="Base directory to backup (default: ~)")
    parser.add_argument("--destination", help="Destination for backup (default: ~/Dropbox/Apps/moltbot-backups/)")
    
    subparsers = parser.add_subparsers(dest='action', help='Available backup commands')
    
    # Create command
    parser_create = subparsers.add_parser('create', help='Create a backup')
    parser_create.set_defaults(func=cmd_create_backup)
    
    # Restore command
    parser_restore = subparsers.add_parser('restore', help='Restore from backup')
    parser_restore.add_argument('--backup-file', required=True, help='Backup file to restore from')
    parser_restore.add_argument('--restore-to', help='Directory to restore to (default: base-dir)')
    parser_restore.set_defaults(func=cmd_restore_backup)
    
    # List command
    parser_list = subparsers.add_parser('list', help='List backup contents')
    parser_list.add_argument('--backup-file', required=True, help='Backup file to list')
    parser_list.set_defaults(func=cmd_list_backup)
    
    # Info command
    parser_info = subparsers.add_parser('info', help='Show backup info')
    parser_info.add_argument('--backup-file', required=True, help='Backup file to inspect')
    parser_info.set_defaults(func=cmd_info_backup)
    
    args = parser.parse_args()
    
    if hasattr(args, 'func'):
        args.func(args)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()