#!/bin/bash

echo "🚀 Starting build process..."

# Set environment variables for better build performance
export PIP_NO_CACHE_DIR=1
export PIP_DISABLE_PIP_VERSION_CHECK=1

# Upgrade pip first
echo "📦 Upgrading pip..."
pip install --upgrade pip

# Install numpy first (pandas dependency)
echo "📦 Installing numpy..."
pip install numpy==1.24.3

# Install pandas with specific version
echo "📦 Installing pandas..."
pip install pandas==1.5.3

# Install the rest of the requirements
echo "📦 Installing remaining requirements..."
pip install -r requirements.txt

echo "✅ Build completed successfully!" 