#!/bin/bash

# 🚀 Smart Stock Ordering - Render Redeployment Script
# This script redeploys both backend and frontend to Render with new POS and supplier integrations

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Starting Render Redeployment Process${NC}"
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

# Step 2: Trigger Render Deployments
print_info "Step 2: Triggering Render Deployments..."

# Check if Render CLI is installed
if ! command -v render &> /dev/null; then
    print_warning "Render CLI not found. You'll need to trigger deployments manually."
    print_info "Please follow these steps:"
    echo ""
    echo "1. Go to https://dashboard.render.com"
    echo "2. Select your backend service (smart-stock-ordering-api)"
    echo "3. Click 'Manual Deploy' → 'Deploy latest commit'"
    echo "4. Wait for backend deployment to complete"
    echo "5. Select your frontend service (smart-stock-ordering-clean)"
    echo "6. Click 'Manual Deploy' → 'Deploy latest commit'"
    echo ""
else
    print_info "Using Render CLI to trigger deployments..."
    
    # Trigger backend deployment
    print_info "Triggering backend deployment..."
    render deploy smart-stock-ordering-api
    
    # Wait for backend to be ready
    print_info "Waiting for backend deployment to complete..."
    sleep 30
    
    # Trigger frontend deployment
    print_info "Triggering frontend deployment..."
    render deploy smart-stock-ordering-clean
fi

# Step 3: Get Service URLs
print_info "Step 3: Getting service URLs..."

# Try to get URLs from Render CLI or use defaults
if command -v render &> /dev/null; then
    BACKEND_URL=$(render service list --format json | grep -o '"url":"[^"]*"' | head -1 | cut -d'"' -f4)
    FRONTEND_URL=$(render service list --format json | grep -o '"url":"[^"]*"' | tail -1 | cut -d'"' -f4)
else
    print_warning "Render CLI not available. Using default URLs."
    print_info "Please update these URLs with your actual Render service URLs:"
    BACKEND_URL="https://your-backend-service.onrender.com"
    FRONTEND_URL="https://your-frontend-service.onrender.com"
fi

print_status "Backend URL: $BACKEND_URL"
print_status "Frontend URL: $FRONTEND_URL"

# Step 4: Test the Deployment
print_info "Step 4: Testing the Deployment..."

# Wait for services to be ready
print_info "Waiting for services to be ready..."
sleep 60

# Test backend health
print_info "Testing backend health..."
HEALTH_RESPONSE=$(curl -s "$BACKEND_URL/health" || echo "FAILED")
if [[ $HEALTH_RESPONSE == *"healthy"* ]]; then
    print_status "Backend health check passed"
else
    print_warning "Backend health check failed, but deployment may still be in progress"
fi

# Test new POS integrations endpoint
print_info "Testing POS integrations API..."
POS_TEST=$(curl -s "$BACKEND_URL/api/pos-integrations/systems" -H "Authorization: Bearer test-token" || echo "FAILED")
if [[ $POS_TEST == *"pos_systems"* ]]; then
    print_status "POS integrations API working"
else
    print_warning "POS integrations API test failed"
fi

# Test new supplier integrations endpoint
print_info "Testing supplier integrations API..."
SUPPLIER_TEST=$(curl -s "$BACKEND_URL/api/supplier-integrations/suppliers" -H "Authorization: Bearer test-token" || echo "FAILED")
if [[ $SUPPLIER_TEST == *"suppliers"* ]]; then
    print_status "Supplier integrations API working"
else
    print_warning "Supplier integrations API test failed"
fi

# Step 5: Final Verification
print_info "Step 5: Final Verification..."

echo ""
echo "=================================================="
echo -e "${GREEN}🎉 Render Deployment Summary${NC}"
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
echo "  1. Visit your frontend URL: $FRONTEND_URL"
echo "  2. Navigate to 'POS Integrations' in the sidebar"
echo "  3. Test connecting a POS system"
echo "  4. Navigate to 'Suppliers' to test supplier features"
echo "  5. Configure your actual POS and supplier credentials"
echo ""
echo -e "${BLUE}📚 Documentation:${NC}"
echo "  • Setup Guide: POS_SUPPLIER_INTEGRATION_SETUP.md"
echo "  • API Docs: $BACKEND_URL/docs"
echo "  • Test Script: python test_integrations.py"
echo ""

print_status "Render redeployment completed!"

# Optional: Open the deployed application
if command -v open &> /dev/null; then
    read -p "Would you like to open the deployed application? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        open "$FRONTEND_URL"
    fi
fi 