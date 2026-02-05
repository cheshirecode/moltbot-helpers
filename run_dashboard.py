#!/usr/bin/env python3
"""
Task Management Dashboard Runner

Simple script to launch the task management dashboard
"""

import subprocess
import sys
import os
import webbrowser
import time
from urllib.request import urlopen
from urllib.error import URLError

def check_port(port):
    """Check if a port is available."""
    try:
        urlopen(f"http://localhost:{port}", timeout=2)
        return True
    except URLError:
        return False

def main():
    print("🚀 Launching OpenClaw Task Management Dashboard...")
    
    # Check if the port is already in use
    port = 5000
    if check_port(port):
        print(f"⚠️  Port {port} appears to be in use. Please close any existing dashboard instances.")
        return
    
    # Get the directory where this script is located
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Check if api.py exists in the current directory
    api_file = os.path.join(script_dir, "api.py")
    if not os.path.exists(api_file):
        print(f"❌ API file not found at {api_file}")
        return
    
    print(f"📂 Using API file from current directory: {script_dir}")
    
    # Start the Flask server in a subprocess
    print("🔌 Starting API server...")
    server_process = subprocess.Popen([sys.executable, "api.py"])
    
    # Wait a moment for the server to start
    time.sleep(3)
    
    # Check if the server started successfully
    if server_process.poll() is not None:
        print("❌ Failed to start the API server")
        return
    
    print(f"🌐 Opening dashboard in your browser at http://localhost:{port}")
    
    # Open the browser to the dashboard
    webbrowser.open(f"http://localhost:{port}")
    
    print("✅ Dashboard launched successfully!")
    print(f"💡 Access the dashboard at: http://localhost:{port}")
    print("💡 Press Ctrl+C to stop the server")
    
    try:
        # Keep the script running to keep the server alive
        server_process.wait()
    except KeyboardInterrupt:
        print("\n🛑 Shutting down dashboard server...")
        server_process.terminate()
        server_process.wait()
        print("👋 Dashboard server stopped.")

if __name__ == "__main__":
    main()