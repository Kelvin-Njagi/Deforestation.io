#!/usr/bin/env python
"""
Complete runner for Deforestation Monitoring System
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def setup_environment():
    """Setup the environment"""
    print("\n" + "="*60)
    print("🌲 DEFORESTATION MONITORING SYSTEM")
    print("="*60)
    
    # Create directories
    directories = ['logs', 'uploads', 'reports', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Directory ready: {directory}/")
    
    # Initialize database
    try:
        from database import init_db
        init_db()
        print("✅ Database initialized")
    except Exception as e:
        print(f"⚠️ Database warning: {e}")
    
    print("\n🚀 Starting application...")
    print("📱 Opening browser at http://localhost:8501")
    print("="*60 + "\n")
    
    # Open browser after delay
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
    
    import threading
    threading.Thread(target=open_browser).start()
    
    # Run streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    subprocess.run(cmd)

if __name__ == "__main__":
    setup_environment()
