import streamlit as st
import os
import sys
from pathlib import Path

# Configure for cloud environment
if os.environ.get('STREAMLIT_RUNTIME_ENV') == 'cloud':
    # Use /tmp for cloud storage
    BASE_DIR = "/tmp"
    for dir_name in ['logs', 'uploads', 'reports', 'temp']:
        Path(os.path.join(BASE_DIR, dir_name)).mkdir(parents=True, exist_ok=True)
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    
    # Import cloud database
    from cloud_database import init_db, get_db, User
else:
    from database import init_db, get_db, User

# Rest of your app.py code (keep your existing code here)
# IMPORTANT: Copy your entire app.py content between these comments
