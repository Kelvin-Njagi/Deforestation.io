#!/bin/bash

echo "================================================"
echo "🌲 Deforestation Monitoring System - Installation"
echo "================================================"
echo

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "📌 Python version: $python_version"

# Create virtual environment
echo -n "📦 Creating virtual environment..."
python3 -m venv venv
if [ $? -eq 0 ]; then
    echo " ✅"
else
    echo " ❌"
    exit 1
fi

# Activate virtual environment
echo -n "🔌 Activating virtual environment..."
source venv/bin/activate
if [ $? -eq 0 ]; then
    echo " ✅"
else
    echo " ❌"
    exit 1
fi

# Upgrade pip
echo -n "📦 Upgrading pip..."
pip install --upgrade pip > /dev/null 2>&1
echo " ✅"

# Install requirements
echo "📚 Installing requirements (this may take a few minutes)..."
pip install -r requirements.txt
if [ $? -eq 0 ]; then
    echo "✅ Requirements installed successfully"
else
    echo "❌ Failed to install requirements"
    exit 1
fi

# Create directories
echo -n "📁 Creating directories..."
mkdir -p logs uploads reports temp
echo " ✅"

# Initialize database
echo -n "🗄️  Initializing database..."
python3 -c "from database import init_db; init_db()" 2>/dev/null
if [ $? -eq 0 ]; then
    echo " ✅"
else
    echo " ❌"
fi

echo
echo "================================================"
echo "✅ Installation complete!"
echo "================================================"
echo
echo "To run the system:"
echo "  1. Activate virtual environment: source venv/bin/activate"
echo "  2. Run: python run.py"
echo "  3. Or: streamlit run app.py"
echo
echo "Default admin credentials:"
echo "  Username: admin"
echo "  Password: Admin@123"
echo
echo "⚠️  Please change the admin password on first login!"
echo "================================================"