#!/bin/bash

# 🚀 Frontend Deployment Script
# This script ensures proper configuration for frontend deployment

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Frontend Deployment Setup${NC}"
echo "=================================================="

# Function to print colored output
print_status() {
    echo -e "${GREEN}✅ $1${NC}"
}

print_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

print_error() {
    echo -e "${RED}❌ $1${NC}"
}

print_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

# Step 1: Verify we're in the right directory
print_info "Step 1: Verifying project structure..."

if [ ! -d "frontend" ]; then
    print_error "frontend directory not found. Please run this script from the project root."
    exit 1
fi

if [ ! -f "frontend/package.json" ]; then
    print_error "frontend/package.json not found. Invalid project structure."
    exit 1
fi

print_status "Project structure verified"

# Step 2: Check Node.js version
print_info "Step 2: Checking Node.js version..."

if ! command -v node &> /dev/null; then
    print_error "Node.js is not installed. Please install Node.js 18 or higher."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    print_warning "Node.js version $NODE_VERSION detected. Version 18 or higher is recommended."
else
    print_status "Node.js version $NODE_VERSION is compatible"
fi

# Step 3: Build the frontend
print_info "Step 3: Building frontend..."

cd frontend

print_info "Installing dependencies..."
npm install

print_info "Running build..."
npm run build

if [ $? -eq 0 ]; then
    print_status "Frontend build completed successfully"
else
    print_error "Frontend build failed"
    exit 1
fi

cd ..

# Step 4: Verify build output
print_info "Step 4: Verifying build output..."

if [ -d "frontend/dist" ]; then
    print_status "Build output directory exists"
    
    if [ -f "frontend/dist/index.html" ]; then
        print_status "Main HTML file exists"
    else
        print_warning "Main HTML file not found in build output"
    fi
else
    print_error "Build output directory not found"
    exit 1
fi

# Step 5: Display deployment instructions
print_info "Step 5: Deployment Instructions"

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Frontend Build Successful!${NC}"
echo "=================================================="
echo ""
echo -e "${YELLOW}📋 Deployment Settings for Render:${NC}"
echo ""
echo "Service Type: Web Service"
echo "Environment: Node"
echo "Root Directory: frontend"
echo "Build Command: npm install && npm run build"
echo "Start Command: npm run preview"
echo ""
echo -e "${YELLOW}🔧 Environment Variables:${NC}"
echo "NODE_VERSION=18"
echo "VITE_API_BASE_URL=https://your-backend-service.onrender.com"
echo "VITE_APP_NAME=Smart Stock Ordering"
echo "VITE_APP_VERSION=1.0.0"
echo ""
echo -e "${YELLOW}🚀 Alternative Deployment Options:${NC}"
echo "1. Netlify: Deploy the frontend/dist folder"
echo "2. Vercel: Connect your GitHub repository"
echo "3. GitHub Pages: Deploy static files from frontend/dist"
echo ""
echo -e "${BLUE}📁 Build output location:${NC} frontend/dist/"
echo ""

print_status "Deployment preparation completed!"

# Optional: Open the local preview
if command -v open &> /dev/null; then
    read -p "Would you like to preview the built application locally? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cd frontend
        npm run preview
    fi
fi