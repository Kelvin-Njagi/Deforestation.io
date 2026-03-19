# At the top of database.py, add:
from pathlib import Path

# Ensure database directory exists
Path(".").mkdir(exist_ok=True)
from sqlalchemy import create_engine, Column, Integer, String, DateTime, Boolean, Float, Text, ForeignKey, Index
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import datetime
from config import config
import bcrypt
import logging

logger = logging.getLogger(__name__)

# Create engine
engine = create_engine(config.DATABASE_URL, connect_args={"check_same_thread": False} if 'sqlite' in config.DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False, index=True)
    email = Column(String(100), unique=True, nullable=False, index=True)
    full_name = Column(String(100))
    password_hash = Column(String(200), nullable=False)
    role = Column(String(20), default="user")  # admin, user, analyst, viewer
    is_active = Column(Boolean, default=False)  # Requires admin approval
    is_locked = Column(Boolean, default=False)
    login_attempts = Column(Integer, default=0)
    last_login = Column(DateTime)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Security questions for password reset
    security_question_1 = Column(String(200))
    security_answer_1 = Column(String(200))
    security_question_2 = Column(String(200))
    security_answer_2 = Column(String(200))
    
    # Relationships
    logs = relationship("SystemLog", back_populates="user")
    analyses = relationship("Analysis", back_populates="user")
    
    def set_password(self, password):
        salt = bcrypt.gensalt(rounds=config.BCRYPT_ROUNDS)
        self.password_hash = bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')
    
    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password_hash.encode('utf-8'))
    
    def verify_security_answer(self, question_num, answer):
        if question_num == 1:
            stored_answer = self.security_answer_1
        else:
            stored_answer = self.security_answer_2
        return bcrypt.checkpw(answer.encode('utf-8'), stored_answer.encode('utf-8'))

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    details = Column(Text)
    ip_address = Column(String(45))
    user_agent = Column(String(200))
    level = Column(String(20), default="INFO")  # INFO, WARNING, ERROR, CRITICAL
    timestamp = Column(DateTime, server_default=func.now(), index=True)
    
    # Relationships
    user = relationship("User", back_populates="logs")
    
    __table_args__ = (
        Index('idx_logs_timestamp_level', 'timestamp', 'level'),
    )

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    name = Column(String(200))
    description = Column(Text)
    image_path = Column(String(500))
    result_path = Column(String(500))
    ndvi_mean = Column(Float)
    forest_cover_percentage = Column(Float)
    deforested_area = Column(Float)  # in hectares
    change_detected = Column(Boolean, default=False)
    confidence_score = Column(Float)
    status = Column(String(20), default="pending")  # pending, processing, completed, failed
    created_at = Column(DateTime, server_default=func.now())
    completed_at = Column(DateTime)
    
    # Relationships
    user = relationship("User", back_populates="analyses")

class Alert(Base):
    __tablename__ = "alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(200))
    description = Column(Text)
    location = Column(String(200))
    latitude = Column(Float)
    longitude = Column(Float)
    severity = Column(String(20))  # low, medium, high, critical
    status = Column(String(20), default="active")  # active, acknowledged, resolved
    created_at = Column(DateTime, server_default=func.now())
    resolved_at = Column(DateTime)
    resolved_by = Column(Integer, ForeignKey("users.id"))

class ForestArea(Base):
    __tablename__ = "forest_areas"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200))
    region = Column(String(100))
    total_area = Column(Float)  # hectares
    forest_cover = Column(Float)  # percentage
    last_monitored = Column(DateTime)
    status = Column(String(50))  # stable, decreasing, increasing
    boundary_coords = Column(Text)  # JSON string of polygon coordinates

# Create tables
def init_db():
    Base.metadata.create_all(bind=engine)
    logger.info("Database initialized")
    
    # Create default admin if not exists
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
            admin.set_password("Admin@123")  # Change in production
            admin.security_question_1 = "What is your favorite color?"
            admin.security_answer_1 = bcrypt.hashpw(b"blue", bcrypt.gensalt()).decode('utf-8')
            admin.security_question_2 = "What city were you born in?"
            admin.security_answer_2 = bcrypt.hashpw(b"Nairobi", bcrypt.gensalt()).decode('utf-8')
            db.add(admin)
            db.commit()
            logger.info("Default admin user created")
    except Exception as e:
        logger.error(f"Error creating admin user: {e}")
    finally:
        db.close()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()