import os
from datetime import timedelta

class Config:
    # Database
    DATABASE_URL = "sqlite:///deforestation_monitoring.db"
    
    # Security
    SECRET_KEY = "your-secret-key-change-in-production"
    ALGORITHM = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    BCRYPT_ROUNDS = 12
    
    # Session
    SESSION_TIMEOUT = timedelta(hours=8)
    MAX_LOGIN_ATTEMPTS = 5
    LOCKOUT_TIME = timedelta(minutes=15)
    
    # File uploads
    MAX_UPLOAD_SIZE = 200 * 1024 * 1024  # 200MB
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'tif', 'tiff'}
    UPLOAD_FOLDER = 'uploads'
    
    # Real-time updates
    REFRESH_INTERVAL = 30  # seconds
    
    # System settings
    DEBUG = False
    TESTING = False
    ENV = 'development'
    
    # Forest monitoring settings
    NDVI_THRESHOLD = 0.3
    MIN_FOREST_AREA = 100  # square meters
    ALERT_THRESHOLD = 0.15  # 15% change triggers alert

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    ENV = 'production'

# Select config based on environment
config = DevelopmentConfig()
