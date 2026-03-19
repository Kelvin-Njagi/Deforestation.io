#!/bin/bash
echo "========================================="
echo "🌲 Setting up Deforestation Monitoring System"
echo "========================================="

# Update package lists
echo "📦 Updating package lists..."
apt-get update -y

# Install required system packages
echo "📦 Installing system dependencies..."
apt-get install -y --no-install-recommends \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1

if [ True -eq 0 ]; then
    echo "✅ System packages installed successfully"
else
    echo "⚠️ Some packages failed to install, but continuing..."
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p /tmp/logs
mkdir -p /tmp/uploads
mkdir -p /tmp/reports
mkdir -p /tmp/temp

echo "✅ Directories created in /tmp"

# Set permissions
chmod -R 755 /tmp/logs
chmod -R 755 /tmp/uploads

echo "✅ Permissions set"
echo "========================================="
echo "✅ Setup complete!"
echo "========================================="
