#!/bin/bash
# This script runs during Streamlit Cloud deployment

echo "========================================="
echo "🌲 Setting up Deforestation Monitoring System"
echo "========================================="

# Create necessary directories
mkdir -p /tmp/logs
mkdir -p /tmp/uploads
mkdir -p /tmp/reports
mkdir -p /tmp/temp

echo "✅ Created directories in /tmp"

# Set permissions
chmod -R 755 /tmp/logs
chmod -R 755 /tmp/uploads

echo "✅ Setup complete"
echo "========================================="
