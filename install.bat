@echo off
echo ================================================
echo 🌲 Deforestation Monitoring System - Installation
echo ================================================
echo.

REM Check Python version
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python not found. Please install Python 3.8 or higher.
    exit /b 1
)

echo 📌 Python found

REM Create virtual environment
echo 📦 Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo ❌ Failed to create virtual environment
    exit /b 1
) else (
    echo ✅ Virtual environment created
)

REM Activate virtual environment
echo 🔌 Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ❌ Failed to activate virtual environment
    exit /b 1
) else (
    echo ✅ Virtual environment activated
)

REM Upgrade pip
echo 📦 Upgrading pip...
python -m pip install --upgrade pip >nul 2>&1
echo ✅ Pip upgraded

REM Install requirements
echo 📚 Installing requirements (this may take a few minutes)...
pip install -r requirements.txt
if errorlevel 1 (
    echo ❌ Failed to install requirements
    exit /b 1
) else (
    echo ✅ Requirements installed
)

REM Create directories
echo 📁 Creating directories...
if not exist logs mkdir logs
if not exist uploads mkdir uploads
if not exist reports mkdir reports
if not exist temp mkdir temp
echo ✅ Directories created

REM Initialize database
echo 🗄️  Initializing database...
python -c "from database import init_db; init_db()" 2>nul
if errorlevel 1 (
    echo ⚠️ Database initialization warning
) else (
    echo ✅ Database initialized
)

echo.
echo ================================================
echo ✅ Installation complete!
echo ================================================
echo.
echo To run the system:
echo   1. Run: run.bat
echo   2. Or: streamlit run app.py
echo.
echo Default admin credentials:
echo   Username: admin
echo   Password: Admin@123
echo.
echo ⚠️  Please change the admin password on first login!
echo ================================================
pause