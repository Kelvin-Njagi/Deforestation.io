#!/bin/bash
echo "========================================="
echo "🌲 Setting up Deforestation Monitoring System"
echo "========================================="

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
