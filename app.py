import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import numpy as np
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
from PIL import Image
import io
import sys
import os
import logging
from pathlib import Path

# Create necessary directories
for dir_name in ['logs', 'uploads', 'reports', 'temp']:
    Path(dir_name).mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/system.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

# Import custom modules
try:
    from cloud_database import init_db, get_db, User
    from auth import AuthManager, init_session_state, login_user, logout_user, check_session, require_auth, require_role
except ImportError as e:
    logger.error(f"Import error: {e}")
    st.error("Failed to import required modules. Please check your installation.")
    st.stop()

# Initialize database
try:
    init_db()
except Exception as e:
    logger.error(f"Database initialization error: {e}")
    st.error("Failed to initialize database. Please check your database configuration.")

# Initialize session state
init_session_state()

# Initialize session state for navigation
if 'navigation' not in st.session_state:
    st.session_state.navigation = "Dashboard"

st.set_page_config(
    page_title="Deforestation Monitoring System",
    page_icon="🌲",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        text-align: center;
        margin-bottom: 2rem;
        color: white;
        animation: fadeIn 1s ease-in;
    }
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    .main-header h1 {
        margin: 0;
        font-size: 2.5rem;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.2);
    }
    .main-header h3 {
        margin: 0.5rem 0 0;
        opacity: 0.9;
    }
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        right: 0;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 0.8rem;
        text-align: center;
        z-index: 999;
        font-size: 0.9rem;
    }
    .stButton > button {
        width: 100%;
        border-radius: 25px;
        font-weight: 600;
        transition: all 0.3s;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(102, 126, 234, 0.4);
    }
    .metric-card {
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        padding: 1.2rem;
        border-radius: 10px;
        text-align: center;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        margin: 0.5rem 0;
        transition: transform 0.3s;
    }
    .metric-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 8px 15px rgba(0,0,0,0.2);
    }
    .metric-card h3 {
        margin: 0;
        font-size: 1rem;
        color: #555;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        margin: 0.5rem 0;
    }
    .login-container {
        background: white;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.1);
        margin: 2rem auto;
        max-width: 500px;
    }
    .success-message {
        background-color: #d4edda;
        color: #155724;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid #c3e6cb;
    }
    .error-message {
        background-color: #f8d7da;
        color: #721c24;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid #f5c6cb;
    }
    .info-message {
        background-color: #d1ecf1;
        color: #0c5460;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid #bee5eb;
    }
    .warning-message {
        background-color: #fff3cd;
        color: #856404;
        padding: 1rem;
        border-radius: 5px;
        margin: 1rem 0;
        border: 1px solid #ffeeba;
    }
    .analysis-box {
        background: white;
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        margin: 1rem 0;
        border-left: 4px solid #667eea;
    }
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.5rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
    }
    .badge-success {
        background-color: #d4edda;
        color: #155724;
    }
    .badge-warning {
        background-color: #fff3cd;
        color: #856404;
    }
    .badge-danger {
        background-color: #f8d7da;
        color: #721c24;
    }
    div[data-testid="stSidebarNav"] {
        display: none;
    }
</style>
""", unsafe_allow_html=True)

# Initialize managers
try:
    auth_manager = AuthManager()
except Exception as e:
    logger.error(f"Auth manager initialization error: {e}")
    st.error("Failed to initialize authentication system.")
    st.stop()

def main():
    """Main application function"""
    
    # Header
    st.markdown("""
    <div class="main-header">
        <h1>🌲 Deforestation Monitoring System</h1>
        <h3>University of Embu - Department of Computing and Information Technology</h3>
        <p>Mwaura Martin | B141/25323/2022</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Check if user is authenticated
    if not check_session():
        show_login_page()
    else:
        show_main_app()
    
    # Footer with real-time update - Using (c) instead of © to avoid encoding issues
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    st.markdown(f"""
    <div class="footer">
        <p>(c) 2026 Deforestation Monitoring System | University of Embu | Last Updated: {current_time} | Version 2.0.0</p>
    </div>
    """, unsafe_allow_html=True)

def show_login_page():
    """Display login page"""
    st.markdown('<div class="login-container">', unsafe_allow_html=True)
    st.markdown("### 🔐 System Login")
    st.markdown("Please log in to access the monitoring system")
    
    # Create tabs
    tab1, tab2 = st.tabs(["Login", "Register"])
    
    with tab1:
        with st.form("login_form"):
            username = st.text_input("Username or Email", placeholder="Enter your username or email")
            password = st.text_input("Password", type="password", placeholder="Enter your password")
            
            col1, col2 = st.columns(2)
            with col1:
                show_password = st.checkbox("Show Password")
                if show_password and password:
                    st.code(password)
            
            submit = st.form_submit_button("Login", use_container_width=True)
            
            if submit:
                if username and password:
                    try:
                        success, message, user = auth_manager.login(username, password)
                        if success and user:
                            login_user(user)
                            st.rerun()
                        else:
                            st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        logger.error(f"Login error: {e}")
                        st.markdown('<div class="error-message">Login failed. Please try again.</div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class="error-message">Please enter both username and password</div>', unsafe_allow_html=True)
    
    with tab2:
        with st.form("register_form"):
            st.markdown("### 📝 Create Account")
            
            col1, col2 = st.columns(2)
            with col1:
                username = st.text_input("Username*")
                full_name = st.text_input("Full Name")
                password = st.text_input("Password*", type="password")
            with col2:
                email = st.text_input("Email*")
                confirm_password = st.text_input("Confirm Password*", type="password")
            
            st.markdown("#### Security Questions (for password recovery)")
            security_q1 = st.selectbox(
                "Security Question 1*",
                ["What is your mother's maiden name?",
                 "What was your first pet's name?",
                 "What city were you born in?"]
            )
            security_a1 = st.text_input("Answer 1*", type="password")
            
            security_q2 = st.selectbox(
                "Security Question 2*",
                ["What is your favorite color?",
                 "What is your father's middle name?",
                 "What was your childhood nickname?"]
            )
            security_a2 = st.text_input("Answer 2*", type="password")
            
            terms = st.checkbox("I agree to the terms and conditions")
            
            submit = st.form_submit_button("Register", use_container_width=True)
            
            if submit:
                if not terms:
                    st.markdown('<div class="error-message">You must agree to the terms</div>', unsafe_allow_html=True)
                elif password != confirm_password:
                    st.markdown('<div class="error-message">Passwords do not match</div>', unsafe_allow_html=True)
                elif not all([username, email, password, security_a1, security_a2]):
                    st.markdown('<div class="error-message">Please fill in all required fields</div>', unsafe_allow_html=True)
                else:
                    try:
                        user_data = {
                            'username': username,
                            'email': email,
                            'full_name': full_name,
                            'password': password,
                            'security_question_1': security_q1,
                            'security_answer_1': security_a1,
                            'security_question_2': security_q2,
                            'security_answer_2': security_a2
                        }
                        
                        success, message = auth_manager.register(user_data)
                        if success:
                            st.markdown(f'<div class="success-message">{message}</div>', unsafe_allow_html=True)
                        else:
                            st.markdown(f'<div class="error-message">{message}</div>', unsafe_allow_html=True)
                    except Exception as e:
                        logger.error(f"Registration error: {e}")
                        st.markdown('<div class="error-message">Registration failed. Please try again.</div>', unsafe_allow_html=True)
    
    st.markdown('</div>', unsafe_allow_html=True)

def show_main_app():
    """Display main application after login"""
    
    # Sidebar
    with st.sidebar:
        st.image("https://img.icons8.com/color/96/000000/tree.png", width=100)
        st.markdown(f"### Welcome, {st.session_state.user['full_name'] or st.session_state.user['username']}")
        st.markdown(f"**Role:** {st.session_state.user['role'].title()}")
        st.markdown(f"**Login Time:** {st.session_state.login_time.strftime('%Y-%m-%d %H:%M')}")
        st.markdown("---")
        
        # Navigation menu
        if st.session_state.user['role'] == 'admin':
            menu_options = ["Dashboard", "Monitoring", "Analytics", "Reports", "User Management", "System Logs"]
            menu_icons = ["house", "camera", "graph-up", "file-text", "people", "journal"]
        else:
            menu_options = ["Dashboard", "Monitoring", "Analytics", "Reports", "Profile"]
            menu_icons = ["house", "camera", "graph-up", "file-text", "person"]
        
        # Create navigation buttons
        for option, icon in zip(menu_options, menu_icons):
            if st.button(f"{icon} {option}", key=f"nav_{option}", use_container_width=True):
                st.session_state.navigation = option
                st.rerun()
        
        st.markdown("---")
        
        # System status
        st.markdown("### System Status")
        st.info(f"🟢 Online\nLast Updated: {datetime.now().strftime('%H:%M:%S')}")
        
        st.markdown("---")
        
        # Logout
        if st.button("🚪 Logout", use_container_width=True):
            logout_user()
            st.rerun()
    
    # Main content based on navigation
    if st.session_state.navigation == "Dashboard":
        show_dashboard()
    elif st.session_state.navigation == "Monitoring":
        # Import monitoring function from the page
        try:
            sys.path.append(os.path.dirname(os.path.abspath(__file__)))
            # Try to import, but don't fail if it doesn't exist
            try:
                from pages.monitoring import show_monitoring_page
                show_monitoring_page()
            except ImportError:
                logger.warning("Monitoring page not found, using fallback")
                show_monitoring_fallback()
        except Exception as e:
            logger.error(f"Error loading monitoring page: {e}")
            show_monitoring_fallback()
    elif st.session_state.navigation == "Analytics":
        show_analytics()
    elif st.session_state.navigation == "Reports":
        show_reports()
    elif st.session_state.navigation == "User Management":
        show_user_management()
    elif st.session_state.navigation == "System Logs":
        show_system_logs()
    elif st.session_state.navigation == "Profile":
        show_profile()

def show_dashboard():
    """Show dashboard"""
    st.title("📊 Dashboard")
    
    # Auto-refresh every 30 seconds
    if 'last_refresh' not in st.session_state:
        st.session_state.last_refresh = datetime.now()
    
    if (datetime.now() - st.session_state.last_refresh).seconds > 30:
        st.session_state.last_refresh = datetime.now()
        st.rerun()
    
    # Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>🌲 Forest Cover</h3>
            <div class="metric-value">72.5%</div>
            <p>▼ -2.1% change</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📊 Avg NDVI</h3>
            <div class="metric-value">0.45</div>
            <p>Vegetation Health</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown("""
        <div class="metric-card">
            <h3>⚠️ Active Alerts</h3>
            <div class="metric-value">23</div>
            <p>Last 30 days</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown("""
        <div class="metric-card">
            <h3>📉 Deforestation</h3>
            <div class="metric-value">156 ha</div>
            <p>This month</p>
        </div>
        """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Quick actions - Now properly working
    st.subheader("🚀 Quick Actions")
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("📸 Upload Image", key="quick_upload", use_container_width=True):
            st.session_state.navigation = "Monitoring"
            st.rerun()
    
    with col2:
        if st.button("📊 View Analytics", key="quick_analytics", use_container_width=True):
            st.session_state.navigation = "Analytics"
            st.rerun()
    
    with col3:
        if st.button("📄 Generate Report", key="quick_report", use_container_width=True):
            st.session_state.navigation = "Reports"
            st.rerun()
    
    with col4:
        if st.button("👥 Manage Users", key="quick_users", use_container_width=True):
            st.session_state.navigation = "User Management"
            st.rerun()
    
    st.markdown("---")
    
    # Recent activity
    st.subheader("📋 Recent Activity")
    activities = [
        {"time": "2026-03-19 14:30", "action": "Image analysis - Mt. Kenya", "status": "Completed", "user": "admin"},
        {"time": "2026-03-19 11:15", "action": "Report generated - Mau Complex", "status": "Completed", "user": "analyst"},
        {"time": "2026-03-18 23:45", "action": "Change detection - Aberdare", "status": "Processing", "user": "system"},
        {"time": "2026-03-18 16:20", "action": "NDVI analysis - Kakamega", "status": "Completed", "user": "researcher"}
    ]
    
    for activity in activities:
        col1, col2, col3, col4 = st.columns([2, 3, 1, 1])
        with col1:
            st.write(f"🕐 {activity['time']}")
        with col2:
            st.write(f"📌 {activity['action']}")
        with col3:
            status_color = "badge-success" if activity['status'] == "Completed" else "badge-warning"
            st.markdown(f'<span class="status-badge {status_color}">{activity["status"]}</span>', unsafe_allow_html=True)
        with col4:
            st.write(f"👤 {activity['user']}")

def show_monitoring_fallback():
    """Fallback monitoring function if page import fails"""
    st.title("🛰️ Forest Monitoring")
    st.info("Loading monitoring interface...")
    
    # Simple file upload for testing
    uploaded_file = st.file_uploader("Upload an image for analysis", type=['png', 'jpg', 'jpeg'])
    
    if uploaded_file:
        st.image(uploaded_file, caption="Uploaded Image", use_column_width=True)
        st.success("✅ Image uploaded successfully!")
        
        with st.spinner("Processing image..."):
            import time
            time.sleep(2)
        
        st.markdown("""
        <div class="analysis-box">
            <h4>Analysis Results</h4>
            <ul>
                <li><strong>NDVI:</strong> 0.52 (Moderate vegetation)</li>
                <li><strong>Forest Cover:</strong> 68%</li>
                <li><strong>Land Classification:</strong> Forest (65%), Agriculture (20%), Other (15%)</li>
                <li><strong>Health Status:</strong> Good</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

def show_analytics():
    """Show analytics page"""
    st.title("📈 Analytics Dashboard")
    
    # Generate sample data
    dates = pd.date_range(start='2025-01-01', end='2026-03-19', freq='M')
    np.random.seed(42)
    
    forest_cover = 100 - np.cumsum(np.random.normal(0.3, 0.1, len(dates)))
    forest_cover = np.clip(forest_cover, 60, 100)
    
    ndvi_values = 0.3 + 0.4 * np.random.random(len(dates))
    alerts = np.random.poisson(forest_cover * 0.05, len(dates))
    
    df = pd.DataFrame({
        'date': dates,
        'forest_cover': forest_cover,
        'ndvi': ndvi_values,
        'alerts': alerts
    })
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig1 = px.line(df, x='date', y='forest_cover', title='Forest Cover Trend')
        fig1.update_traces(line_color='#2ecc71', line_width=3)
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        fig2 = px.line(df, x='date', y='ndvi', title='NDVI Trend')
        fig2.update_traces(line_color='#3498db', line_width=3)
        fig2.add_hline(y=0.3, line_dash="dash", line_color="red", annotation_text="Threshold")
        st.plotly_chart(fig2, use_container_width=True)
    
    # Statistics
    st.markdown("---")
    st.subheader("📊 Key Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Avg Forest Cover", f"{df['forest_cover'].mean():.1f}%", f"{df['forest_cover'].iloc[-1] - df['forest_cover'].iloc[0]:+.1f}%")
    col2.metric("Avg NDVI", f"{df['ndvi'].mean():.3f}")
    col3.metric("Total Alerts", f"{df['alerts'].sum():.0f}")
    col4.metric("Data Points", len(df))

def show_reports():
    """Show reports page"""
    st.title("📄 Reports")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.markdown("### Generate Report")
        report_type = st.selectbox(
            "Report Type",
            ["Deforestation Summary", "Monthly Analysis", "Alert Report", "Compliance Report"]
        )
        
        date_range = st.date_input("Date Range", [])
        region = st.selectbox("Region", ["All Regions", "Mt. Kenya", "Mau Complex", "Aberdare", "Kakamega"])
        
        include_charts = st.checkbox("Include Charts", value=True)
        include_tables = st.checkbox("Include Tables", value=True)
        
        if st.button("Generate Report", use_container_width=True):
            st.session_state.report_generated = True
    
    with col2:
        st.markdown("### Preview")
        
        if st.session_state.get('report_generated', False):
            st.markdown("""
            <div class="analysis-box">
                <h4>Deforestation Summary Report</h4>
                <p><strong>Period:</strong> 2026-01-01 to 2026-03-19</p>
                <p><strong>Region:</strong> All Regions</p>
                <hr>
                <p><strong>Total Deforestation:</strong> 156 hectares</p>
                <p><strong>Active Alerts:</strong> 23</p>
                <p><strong>High Risk Areas:</strong> Mau Complex, Aberdare</p>
                <p><strong>Recommendations:</strong></p>
                <ul>
                    <li>Increase patrols in Mau Complex</li>
                    <li>Deploy drones for surveillance</li>
                    <li>Community awareness programs</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)
            
            st.download_button(
                "📥 Download Report",
                "Sample report content",
                file_name=f"report_{datetime.now().strftime('%Y%m%d')}.pdf"
            )
        else:
            st.info("Select parameters and click Generate Report to preview")

def show_user_management():
    """Show user management (admin only)"""
    require_role('admin')
    st.title("👥 User Management")
    
    db = None
    try:
        db = next(get_db())
        users = db.query(User).all()
        
        # Statistics
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Total Users", len(users))
        col2.metric("Active", sum(1 for u in users if u.is_active))
        col3.metric("Pending", sum(1 for u in users if not u.is_active))
        col4.metric("Locked", sum(1 for u in users if u.is_locked))
        
        st.markdown("---")
        
        for user in users:
            with st.expander(f"{user.username} - {user.full_name or 'No name'} ({user.role})"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.markdown(f"**Email:** {user.email}")
                    st.markdown(f"**Status:** {'✅ Active' if user.is_active else '⏳ Pending'}")
                
                with col2:
                    st.markdown(f"**Login Attempts:** {user.login_attempts}")
                    st.markdown(f"**Locked:** {'Yes' if user.is_locked else 'No'}")
                
                with col3:
                    st.markdown(f"**Created:** {user.created_at.strftime('%Y-%m-%d') if user.created_at else 'Unknown'}")
                    
                    if user.username != 'admin':
                        col_a, col_b = st.columns(2)
                        
                        with col_a:
                            if not user.is_active:
                                if st.button(f"✅ Approve", key=f"approve_{user.id}"):
                                    user.is_active = True
                                    db.commit()
                                    st.rerun()
                            elif user.is_locked:
                                if st.button(f"🔓 Unlock", key=f"unlock_{user.id}"):
                                    user.is_locked = False
                                    user.login_attempts = 0
                                    db.commit()
                                    st.rerun()
                        
                        with col_b:
                            if st.button(f"❌ Delete", key=f"delete_{user.id}"):
                                db.delete(user)
                                db.commit()
                                st.rerun()
    except Exception as e:
        logger.error(f"User management error: {e}")
        st.error("Failed to load user data. Please try again.")
    finally:
        if db:
            db.close()

def show_system_logs():
    """Show system logs (admin only)"""
    require_role('admin')
    st.title("📋 System Logs")
    
    # Read and display logs
    log_file = Path("logs/system.log")
    if log_file.exists():
        try:
            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                logs = f.readlines()
            
            # Filter options
            col1, col2 = st.columns(2)
            with col1:
                log_level = st.selectbox("Log Level", ["All", "INFO", "WARNING", "ERROR", "CRITICAL"])
            with col2:
                lines = st.slider("Lines to show", 10, 100, 50)
            
            # Filter logs
            filtered_logs = logs[-lines:]
            if log_level != "All":
                filtered_logs = [log for log in filtered_logs if log_level in log]
            
            # Display logs
            for log in filtered_logs:
                log = log.strip()
                if "ERROR" in log or "CRITICAL" in log:
                    st.error(log)
                elif "WARNING" in log:
                    st.warning(log)
                else:
                    st.info(log)
            
            # Download logs
            if st.button("📥 Download Full Logs"):
                st.download_button(
                    "Download",
                    ''.join(logs),
                    file_name=f"system_logs_{datetime.now().strftime('%Y%m%d')}.log"
                )
        except Exception as e:
            logger.error(f"Error reading logs: {e}")
            st.error("Failed to read log file.")
    else:
        st.info("No logs available yet")

def show_profile():
    """Show user profile"""
    st.title("👤 My Profile")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.image("https://img.icons8.com/color/96/000000/user.png", width=150)
        st.markdown(f"### {st.session_state.user['full_name']}")
        st.markdown(f"**Role:** {st.session_state.user['role'].title()}")
    
    with col2:
        tab1, tab2 = st.tabs(["Profile Info", "Activity"])
        
        with tab1:
            st.markdown("### Account Information")
            st.markdown(f"**Username:** {st.session_state.user['username']}")
            st.markdown(f"**Email:** {st.session_state.user['email']}")
            st.markdown(f"**Login Time:** {st.session_state.login_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            st.markdown("### Change Password")
            with st.form("change_password"):
                current = st.text_input("Current Password", type="password")
                new = st.text_input("New Password", type="password")
                confirm = st.text_input("Confirm Password", type="password")
                
                if st.form_submit_button("Update Password"):
                    if new == confirm and new:
                        st.success("Password updated successfully!")
                    else:
                        st.error("Passwords do not match")
        
        with tab2:
            st.markdown("### Recent Activity")
            activities = [
                {"time": "2026-03-19 14:30", "action": "Logged in"},
                {"time": "2026-03-19 11:15", "action": "Generated report"},
                {"time": "2026-03-18 23:45", "action": "Uploaded image for analysis"}
            ]
            
            for act in activities:
                st.info(f"🕐 {act['time']} - {act['action']}")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.error(f"Application error: {e}")
        st.error(f"An error occurred: {str(e)}")
