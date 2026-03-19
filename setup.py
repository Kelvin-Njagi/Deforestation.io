import os
import sys
from pathlib import Path

# This file helps Streamlit Cloud set up the application

def create_directories():
    """Create necessary directories for the application"""
    directories = ['logs', 'uploads', 'reports', 'temp']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Created directory: {directory}")

def check_environment():
    """Check if running on Streamlit Cloud"""
    is_cloud = os.environ.get('STREAMLIT_RUNTIME_ENV') == 'cloud'
    print(f"Running on Streamlit Cloud: {is_cloud}")
    return is_cloud

if __name__ == "__main__":
    print("="*50)
    print("🌲 Deforestation Monitoring System - Setup")
    print("="*50)
    create_directories()
    print("✅ Setup complete!")
