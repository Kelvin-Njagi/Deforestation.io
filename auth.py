import streamlit as st
from cloud_database import SessionLocal, User, SystemLog
from datetime import datetime, timedelta
import bcrypt
import logging
import re
from typing import Tuple, Optional

logger = logging.getLogger(__name__)

class AuthManager:
    def __init__(self):
        self.session = SessionLocal()
    
    def __del__(self):
        self.session.close()
    
    def validate_password(self, password: str) -> Tuple[bool, str]:
        """Validate password strength"""
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not re.search(r"[A-Z]", password):
            return False, "Password must contain at least one uppercase letter"
        if not re.search(r"[a-z]", password):
            return False, "Password must contain at least one lowercase letter"
        if not re.search(r"\d", password):
            return False, "Password must contain at least one number"
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            return False, "Password must contain at least one special character"
        return True, "Password is valid"
    
    def validate_email(self, email: str) -> bool:
        """Validate email format"""
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return re.match(pattern, email) is not None
    
    def login(self, username: str, password: str, ip_address: str = None) -> Tuple[bool, str, Optional[User]]:
        """Authenticate user"""
        try:
            user = self.session.query(User).filter(
                (User.username == username) | (User.email == username)
            ).first()
            
            if not user:
                return False, "Invalid username or password", None
            
            if user.is_locked:
                return False, "Account is locked. Contact administrator.", None
            
            if not user.is_active:
                return False, "Account pending administrator approval", None
            
            if user.check_password(password):
                user.login_attempts = 0
                user.last_login = datetime.now()
                user.is_locked = False
                self.session.commit()
                return True, "Login successful", user
            else:
                user.login_attempts += 1
                if user.login_attempts >= 5:
                    user.is_locked = True
                self.session.commit()
                return False, f"Invalid password. Attempts remaining: {5 - user.login_attempts}", None
                
        except Exception as e:
            logger.error(f"Login error: {e}")
            return False, "System error occurred", None
    
    def register(self, user_data: dict) -> Tuple[bool, str]:
        """Register new user"""
        try:
            if not self.validate_email(user_data['email']):
                return False, "Invalid email format"
            
            valid, msg = self.validate_password(user_data['password'])
            if not valid:
                return False, msg
            
            if self.session.query(User).filter(User.username == user_data['username']).first():
                return False, "Username already exists"
            
            if self.session.query(User).filter(User.email == user_data['email']).first():
                return False, "Email already registered"
            
            user = User(
                username=user_data['username'],
                email=user_data['email'],
                full_name=user_data.get('full_name', ''),
                role="user",
                is_active=False
            )
            user.set_password(user_data['password'])
            
            user.security_question_1 = user_data['security_question_1']
            user.security_answer_1 = bcrypt.hashpw(user_data['security_answer_1'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user.security_question_2 = user_data['security_question_2']
            user.security_answer_2 = bcrypt.hashpw(user_data['security_answer_2'].encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            
            self.session.add(user)
            self.session.commit()
            
            return True, "Registration successful. Waiting for admin approval."
            
        except Exception as e:
            logger.error(f"Registration error: {e}")
            return False, f"Registration failed: {str(e)}"

# Session management functions
def init_session_state():
    """Initialize session state variables"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    if 'login_time' not in st.session_state:
        st.session_state.login_time = None

def login_user(user):
    """Set user session"""
    st.session_state.authenticated = True
    st.session_state.user = {
        'id': user.id,
        'username': user.username,
        'email': user.email,
        'full_name': user.full_name,
        'role': user.role
    }
    st.session_state.login_time = datetime.now()

def logout_user():
    """Clear user session"""
    st.session_state.authenticated = False
    st.session_state.user = None
    st.session_state.login_time = None

def check_session():
    """Check if session is still valid"""
    return st.session_state.get('authenticated', False)

def require_auth():
    """Require authentication"""
    if not check_session():
        st.warning("Please log in to access this page")
        st.stop()

def require_role(required_role):
    """Require specific role"""
    if not check_session():
        st.warning("Please log in to access this page")
        st.stop()
    
    if st.session_state.user['role'] != required_role and st.session_state.user['role'] != 'admin':
        st.error("You don't have permission to access this page")
        st.stop()
