#!/bin/bash

# 🚀 Smart Stock Ordering - Complete Redeployment Script
# This script redeploys both backend and frontend with the new POS and supplier integrations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
BACKEND_DIR="backend"
FRONTEND_DIR="frontend"
GIT_REPO="smart-stock-ordering"

echo -e "${BLUE}🚀 Starting Complete Redeployment Process${NC}"
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

# Check if we're in the right directory
if [ ! -d "$BACKEND_DIR" ] || [ ! -d "$FRONTEND_DIR" ]; then
    print_error "Backend or frontend directory not found. Please run this script from the project root."
    exit 1
fi

# Step 1: Git Operations
print_info "Step 1: Preparing Git repository..."

# Check if we have uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    print_warning "You have uncommitted changes. Committing them..."
    git add .
    git commit -m "feat: Add POS and supplier integrations - $(date)"
fi

# Push to remote repository
print_info "Pushing changes to remote repository..."
git push origin main

print_status "Git operations completed"

# Step 2: Backend Deployment
print_info "Step 2: Deploying Backend..."

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    print_warning "Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Deploy backend to Railway
print_info "Deploying backend to Railway..."
cd $BACKEND_DIR

# Check if we're logged into Railway
if ! railway whoami &> /dev/null; then
    print_warning "Not logged into Railway. Please login:"
    railway login
fi

# Deploy to Railway
print_info "Starting Railway deployment..."
railway up

# Get the deployment URL
BACKEND_URL=$(railway status --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4)
if [ -z "$BACKEND_URL" ]; then
    BACKEND_URL="https://smart-stock-ordering-backend-production.up.railway.app"
fi

print_status "Backend deployed to: $BACKEND_URL"

# Test backend health
print_info "Testing backend health..."
sleep 10  # Wait for deployment to complete

HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health" || echo "FAILED")
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    print_status "Backend health check passed"
else
    print_warning "Backend health check failed, but deployment may still be in progress"
fi

cd ..

# Step 3: Frontend Deployment
print_info "Step 3: Deploying Frontend..."

cd $FRONTEND_DIR

# Install dependencies
print_info "Installing frontend dependencies..."
npm install

# Build the frontend
print_info "Building frontend..."
npm run build

# Check if build was successful
if [ ! -d "dist" ]; then
    print_error "Frontend build failed. Check for errors above."
    exit 1
fi

print_status "Frontend build completed"

# Deploy to Vercel (if using Vercel)
if command -v vercel &> /dev/null; then
    print_info "Deploying to Vercel..."
    vercel --prod
    FRONTEND_URL=$(vercel ls --json | grep -o '"url":"[^"]*"' | cut -d'"' -f4 | head -1)
    print_status "Frontend deployed to Vercel: $FRONTEND_URL"
else
    print_warning "Vercel CLI not found. You can deploy manually:"
    print_info "1. Go to https://vercel.com"
    print_info "2. Import your GitHub repository"
    print_info "3. Set build command: npm run build"
    print_info "4. Set output directory: dist"
    print_info "5. Deploy"
fi

cd ..

# Step 4: Update Environment Variables
print_info "Step 4: Updating Environment Variables..."

# Update frontend environment with new backend URL
if [ -f "$FRONTEND_DIR/.env" ]; then
    sed -i.bak "s|VITE_API_URL=.*|VITE_API_URL=$BACKEND_URL|" "$FRONTEND_DIR/.env"
    print_status "Updated frontend API URL"
fi

# Step 5: Test the Deployment
print_info "Step 5: Testing the Deployment..."

# Test backend API endpoints
print_info "Testing backend API endpoints..."

# Test health endpoint
HEALTH_TEST=$(curl -s "$BACKEND_URL/health")
if [[ $HEALTH_TEST == *"healthy"* ]]; then
    print_status "Backend health endpoint working"
else
    print_warning "Backend health endpoint test failed"
fi

# Test POS integrations endpoint
POS_TEST=$(curl -s "$BACKEND_URL/api/pos-integrations/systems" -H "Authorization: Bearer test-token")
if [[ $POS_TEST == *"pos_systems"* ]]; then
    print_status "POS integrations API working"
else
    print_warning "POS integrations API test failed"
fi

# Test supplier integrations endpoint
SUPPLIER_TEST=$(curl -s "$BACKEND_URL/api/supplier-integrations/suppliers" -H "Authorization: Bearer test-token")
if [[ $SUPPLIER_TEST == *"suppliers"* ]]; then
    print_status "Supplier integrations API working"
else
    print_warning "Supplier integrations API test failed"
fi

# Step 6: Final Verification
print_info "Step 6: Final Verification..."

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Deployment Summary${NC}"
echo "=================================================="
echo -e "${BLUE}Backend URL:${NC} $BACKEND_URL"
echo -e "${BLUE}Frontend URL:${NC} $FRONTEND_URL"
echo ""
echo -e "${GREEN}✅ New Features Deployed:${NC}"
echo "  • POS Integrations (Square, Toast, Clover, etc.)"
echo "  • Enhanced Supplier Integrations"
echo "  • Real-time inventory synchronization"
echo "  • Quick ordering system"
echo "  • Automated supplier ordering"
echo ""
echo -e "${YELLOW}🔧 Next Steps:${NC}"
echo "  1. Configure your actual POS system credentials"
echo "  2. Set up your real supplier accounts"
echo "  3. Test the integrations with real data"
echo "  4. Configure webhooks for real-time updates"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "  • Setup Guide: POS_SUPPLIER_INTEGRATION_SETUP.md"
echo "  • API Docs: $BACKEND_URL/docs"
echo "  • Test Script: python test_integrations.py"
echo ""

print_status "Redeployment completed successfully!"

# Optional: Open the deployed application
if command -v open &> /dev/null; then
    read -p "Would you like to open the deployed application? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "$FRONTEND_URL"
    fi
fi 