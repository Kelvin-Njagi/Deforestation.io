"""
Setup script for Deforestation Monitoring System
Run this script first to set up the environment
"""

import os
import sys
import subprocess
from pathlib import Path

def create_directories():
    """Create all necessary directories"""
    directories = ['logs', 'uploads', 'reports', 'temp', 'pages']
    
    print("\n📁 Creating directories...")
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)
        print(f"   ✅ Created: {directory}/")
    
    return True

def create_init_files():
    """Create __init__.py files for Python packages"""
    init_locations = ['', 'pages']
    
    for location in init_locations:
        init_file = Path(location) / '__init__.py'
        if not init_file.exists():
            init_file.touch()
            print(f"   ✅ Created: {init_file}")

def check_python_version():
    """Check Python version"""
    version = sys.version_info
    print(f"\n🐍 Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("   ✅ Python version compatible")
        return True
    else:
        print("   ❌ Python 3.8+ required")
        return False

def install_requirements():
    """Install required packages"""
    print("\n📦 Installing requirements...")
    
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"   ❌ Error installing requirements: {e}")
        return False

def main():
    """Main setup function"""
    print("="*60)
    print("🌲 DEFORESTATION MONITORING SYSTEM - SETUP")
    print("="*60)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Create __init__.py files
    create_init_files()
    
    # Install requirements
    if install_requirements():
        print("\n✅ All requirements installed successfully!")
    else:
        print("\n❌ Failed to install requirements")
        print("\nPlease install manually: pip install -r requirements.txt")
    
    print("\n" + "="*60)
    print("✅ SETUP COMPLETE!")
    print("="*60)
    print("\nNext steps:")
    print("1. Run the application: streamlit run app.py")
    print("2. Login with default admin credentials:")
    print("   Username: admin")
    print("   Password: Admin@123")
    print("\n⚠️  IMPORTANT: Change the admin password on first login!")
    print("="*60)

if __name__ == "__main__":
    main()
