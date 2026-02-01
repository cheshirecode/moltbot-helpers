"""
Process Management Utility for OpenClaw Services

This module provides tools to manage and track running services and processes
spawned by the OpenClaw system.
"""

import os
import subprocess
import psutil
import json
import threading
import time
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path


class ProcessManager:
    """
    Manages and tracks running services and processes spawned by OpenClaw.
    """
    
    def __init__(self, registry_file: str = None):
        self.registry_file = registry_file or os.path.expanduser("~/.openclaw/service_registry.json")
        self.process_registry = self._load_registry()
        self.lock = threading.Lock()
        
    def _load_registry(self) -> Dict[str, Any]:
        """Load the process registry from file."""
        if os.path.exists(self.registry_file):
            try:
                with open(self.registry_file, 'r') as f:
                    return json.load(f)
            except Exception:
                return {"services": {}}
        return {"services": {}}
    
    def _save_registry(self):
        """Save the process registry to file."""
        with self.lock:
            os.makedirs(os.path.dirname(self.registry_file), exist_ok=True)
            with open(self.registry_file, 'w') as f:
                json.dump(self.process_registry, f, indent=2)
    
    def register_process(self, process_id: int, name: str, description: str, pid: int, 
                         start_time: str = None, metadata: Dict = None) -> str:
        """
        Register a new process in the registry.
        
        Args:
            process_id: Unique identifier for the process
            name: Name of the service/process
            description: Description of the service
            pid: Process ID
            start_time: When the process was started
            metadata: Additional metadata about the process
        
        Returns:
            Process ID
        """
        if start_time is None:
            start_time = datetime.now().isoformat()
        
        if metadata is None:
            metadata = {}
        
        with self.lock:
            self.process_registry["services"][process_id] = {
                "name": name,
                "description": description,
                "pid": pid,
                "start_time": start_time,
                "status": "running",
                "metadata": metadata
            }
            self._save_registry()
        
        return process_id
    
    def unregister_process(self, process_id: str) -> bool:
        """Remove a process from the registry."""
        with self.lock:
            if process_id in self.process_registry["services"]:
                del self.process_registry["services"][process_id]
                self._save_registry()
                return True
            return False
    
    def get_process_info(self, process_id: str) -> Optional[Dict]:
        """Get information about a specific process."""
        if process_id in self.process_registry["services"]:
            return self.process_registry["services"][process_id]
        return None
    
    def list_processes(self) -> Dict[str, Dict]:
        """List all registered processes."""
        # Update status for each process
        updated_services = {}
        for proc_id, info in self.process_registry["services"].items():
            # Check if the actual process is still running
            try:
                proc = psutil.Process(info["pid"])
                if proc.is_running():
                    info["status"] = "running"
                else:
                    info["status"] = "stopped"
            except psutil.NoSuchProcess:
                info["status"] = "dead"
            
            updated_services[proc_id] = info
        
        # Update the registry with fresh status
        with self.lock:
            self.process_registry["services"] = updated_services
            self._save_registry()
        
        return updated_services
    
    def is_process_running(self, process_id: str) -> bool:
        """Check if a registered process is actually running."""
        if process_id not in self.process_registry["services"]:
            return False
        
        info = self.process_registry["services"][process_id]
        try:
            proc = psutil.Process(info["pid"])
            return proc.is_running()
        except psutil.NoSuchProcess:
            return False
    
    def kill_process(self, process_id: str) -> bool:
        """Kill a registered process and update registry."""
        if process_id not in self.process_registry["services"]:
            return False
        
        info = self.process_registry["services"][process_id]
        try:
            proc = psutil.Process(info["pid"])
            proc.terminate()  # Try graceful termination first
            
            # Wait a bit for graceful shutdown
            try:
                proc.wait(timeout=5)  # Wait up to 5 seconds
            except psutil.TimeoutExpired:
                proc.kill()  # Force kill if it doesn't terminate gracefully
            
            # Remove from registry
            self.unregister_process(process_id)
            return True
        except psutil.NoSuchProcess:
            # Process already dead, remove from registry
            self.unregister_process(process_id)
            return True
        except Exception as e:
            print(f"Error killing process {process_id}: {e}")
            return False
    
    def kill_all_processes(self, confirm: bool = True) -> int:
        """Kill all registered processes."""
        if confirm:
            processes = self.list_processes()
            if processes:
                print(f"Found {len(processes)} registered processes:")
                for proc_id, info in processes.items():
                    print(f"  - {proc_id}: {info['name']} (PID: {info['pid']}, Status: {info['status']})")
                
                response = input("Are you sure you want to kill all registered processes? (yes/no): ")
                if response.lower() not in ['yes', 'y']:
                    print("Operation cancelled.")
                    return 0
        
        processes = self.list_processes()
        killed_count = 0
        
        for proc_id in list(processes.keys()):  # Use list() to avoid dict changing during iteration
            if self.kill_process(proc_id):
                killed_count += 1
        
        print(f"Killed {killed_count} processes.")
        return killed_count
    
    def cleanup_dead_processes(self) -> int:
        """Remove dead processes from registry."""
        processes = self.list_processes()
        cleaned_count = 0
        
        for proc_id, info in processes.items():
            if info["status"] == "dead":
                self.unregister_process(proc_id)
                cleaned_count += 1
        
        if cleaned_count > 0:
            print(f"Cleaned up {cleaned_count} dead processes from registry.")
        
        return cleaned_count


def main():
    """Command-line interface for the process manager."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Process Management Utility for OpenClaw Services")
    parser.add_argument("action", choices=[
        'list', 'status', 'kill', 'kill-all', 'cleanup', 'register', 'unregister'
    ], help="Action to perform")
    parser.add_argument("--id", help="Process ID for specific operations")
    parser.add_argument("--confirm", action="store_true", help="Confirm operations that require confirmation")
    
    args = parser.parse_args()
    
    pm = ProcessManager()
    
    if args.action == 'list':
        processes = pm.list_processes()
        if processes:
            print(f"Registered processes ({len(processes)}):")
            for proc_id, info in processes.items():
                print(f"  ID: {proc_id}")
                print(f"    Name: {info['name']}")
                print(f"    Description: {info['description']}")
                print(f"    PID: {info['pid']}")
                print(f"    Status: {info['status']}")
                print(f"    Started: {info['start_time']}")
                print()
        else:
            print("No registered processes found.")
    
    elif args.action == 'status':
        if args.id:
            info = pm.get_process_info(args.id)
            if info:
                print(f"Process {args.id}:")
                print(f"  Name: {info['name']}")
                print(f"  Status: {info['status']}")
                print(f"  PID: {info['pid']}")
            else:
                print(f"Process {args.id} not found in registry.")
        else:
            processes = pm.list_processes()
            for proc_id, info in processes.items():
                print(f"{proc_id}: {info['status']} (PID: {info['pid']})")
    
    elif args.action == 'kill':
        if args.id:
            if pm.kill_process(args.id):
                print(f"Killed process {args.id}")
            else:
                print(f"Failed to kill process {args.id}")
        else:
            print("Please specify a process ID with --id")
    
    elif args.action == 'kill-all':
        killed_count = pm.kill_all_processes(confirm=not args.confirm)
        print(f"Operation completed. {killed_count} processes affected.")
    
    elif args.action == 'cleanup':
        cleaned_count = pm.cleanup_dead_processes()
        print(f"Cleanup completed. {cleaned_count} processes removed from registry.")
    
    elif args.action == 'register':
        print("Register action requires programmatic usage. Use the ProcessManager class directly.")
    
    elif args.action == 'unregister':
        if args.id:
            if pm.unregister_process(args.id):
                print(f"Unregistered process {args.id}")
            else:
                print(f"Failed to unregister process {args.id}")
        else:
            print("Please specify a process ID with --id")


if __name__ == "__main__":
    main()