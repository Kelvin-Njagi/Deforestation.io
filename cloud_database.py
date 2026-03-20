import streamlit as st
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import bcrypt
import os
from pathlib import Path

# Use local path instead of /tmp for local development
import sys
IS_CLOUD = os.environ.get('STREAMLIT_RUNTIME_ENV') == 'cloud'

if IS_CLOUD:
    BASE_DIR = "/tmp"
else:
    BASE_DIR = "."

DATABASE_URL = f"sqlite:///{BASE_DIR}/deforestation_monitoring.db"

# Create directories
for dir_name in ['logs', 'uploads', 'reports', 'temp']:
    Path(os.path.join(BASE_DIR, dir_name)).mkdir(parents=True, exist_ok=True)

# Create engine
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default="user")
    is_active = Column(Boolean, default=False)
    is_locked = Column(Boolean, default=False)
    login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime)
    created_at = Column(DateTime, default=datetime.now)

    # Security questions
    security_question_1 = Column(String(200))
    security_answer_1 = Column(String(200))
    security_question_2 = Column(String(200))
    security_answer_2 = Column(String(200))

    def set_password(self, password):
        salt = bcrypt.gensalt()
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))

class SystemLog(Base):
    __tablename__ = "system_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text)
    ip_address = Column(String(45))
    level = Column(String(20), default="INFO")
    timestamp = Column(DateTime, default=datetime.now, index=True)

def init_db():
    """Initialize database with tables and default admin"""
    Base.metadata.create_all(bind=engine)
    print("? Database initialized")

    # Create default admin
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.role == "admin").first()
        if not admin:
            admin = User(
                username="admin",
                email="admin@forestmonitor.org",
                full_name="System Administrator",
                role="admin",
                is_active=True
            )
            admin.set_password("Admin@123")
            admin.security_question_1 = "What is your favorite color?"
            admin.security_answer_1 = bcrypt.hashpw(b"blue", bcrypt.gensalt()).decode('utf-8')
            admin.security_question_2 = "What city were you born in?"
            admin.security_answer_2 = bcrypt.hashpw(b"Nairobi", bcrypt.gensalt()).decode('utf-8')
            db.add(admin)
            db.commit()
            print("? Default admin user created")
    except Exception as e:
        print(f"?? Error creating admin: {e}")
    finally:
        db.close()

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Initialize database on import
init_db()
