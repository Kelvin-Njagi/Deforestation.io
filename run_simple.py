"""
Simple runner for Deforestation Monitoring System
"""

import os
import sys
import subprocess
from pathlib import Path

def check_directories():
    """Ensure all directories exist"""
    directories = ['logs', 'uploads', 'reports', 'temp']
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory ready: {directory}/")

def main():
    print("\n" + "="*60)
    print("🌲 DEFORESTATION MONITORING SYSTEM")
    print("="*60)
    
    # Check directories
    check_directories()
    
    print("\n🚀 Starting application...")
    print("📱 Opening browser at http://localhost:8501")
    print("="*60 + "\n")
    
    # Run streamlit
    cmd = [sys.executable, "-m", "streamlit", "run", "app.py"]
    
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\n\n👋 System stopped by user")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\nTry running manually: streamlit run app.py")

if __name__ == "__main__":
    main()
