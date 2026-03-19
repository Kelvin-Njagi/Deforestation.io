#!/usr/bin/env python
"""
Deforestation Monitoring System
Main entry point for running the application
"""

import os
import sys
import subprocess
import webbrowser
import time
from pathlib import Path

def check_dependencies():
    """Check if all dependencies are installed"""
    try:
        import streamlit
        import pandas
        import numpy
        import cv2
        import PIL
        import plotly
        import bcrypt
        import sqlalchemy
        print("✅ All dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def setup_database():
    """Initialize the database"""
    try:
        from database import init_db
        init_db()
        print("✅ Database initialized successfully")
        return True
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['logs', 'uploads', 'reports', 'temp']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    return True

def main():
    """Main function to run the application"""
    print("\n" + "="*60)
    print("🌲 DEFORESTATION MONITORING SYSTEM")
    print("="*60 + "\n")
    
    # Check Python version
    python_version = sys.version_info
    if python_version.major == 3 and python_version.minor >= 8:
        print(f"✅ Python version: {python_version.major}.{python_version.minor}.{python_version.micro}")
    else:
        print(f"⚠️ Python 3.8+ recommended (current: {python_version.major}.{python_version.minor})")
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Create directories
    create_directories()
    
    # Setup database
    if not setup_database():
        return
    
    print("\n" + "="*60)
    print("🚀 Starting Deforestation Monitoring System...")
    print("="*60 + "\n")
    
    # Get the absolute path to app.py
    app_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "app.py")
    
    # Open browser after a short delay
    def open_browser():
        time.sleep(3)
        webbrowser.open("http://localhost:8501")
    
    import threading
    threading.Thread(target=open_browser).start()
    
    # Run streamlit
    cmd = ["streamlit", "run", app_path, "--server.port=8501", "--server.address=localhost"]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user")
    except Exception as e:
        print(f"\n❌ Error running application: {e}")
        print("\nTry running manually: streamlit run app.py")

if __name__ == "__main__":
    main()