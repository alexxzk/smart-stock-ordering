#!/bin/bash

echo "🚀 Testing Railway Deployment"
echo "============================="
echo ""

# Get the app URL from user
echo "Please enter your Railway app URL (e.g., https://unable-thunder-production-xxxx.up.railway.app):"
read APP_URL

echo ""
echo "Testing endpoints..."

# Test health endpoint
echo "1. Testing health endpoint..."
HEALTH_RESPONSE=$(curl -s "$APP_URL/health")
if [[ $? -eq 0 ]]; then
    echo "✅ Health endpoint working: $HEALTH_RESPONSE"
else
    echo "❌ Health endpoint failed"
fi

# Test root endpoint
echo ""
echo "2. Testing root endpoint..."
ROOT_RESPONSE=$(curl -s "$APP_URL/")
if [[ $? -eq 0 ]]; then
    echo "✅ Root endpoint working: $ROOT_RESPONSE"
else
    echo "❌ Root endpoint failed"
fi

# Test Firestore connection
echo ""
echo "3. Testing Firestore connection..."
FIRESTORE_RESPONSE=$(curl -s "$APP_URL/test-firestore")
if [[ $? -eq 0 ]]; then
    echo "✅ Firestore test: $FIRESTORE_RESPONSE"
else
    echo "❌ Firestore test failed"
fi

echo ""
echo "🎉 Deployment Test Complete!"
echo ""
echo "Your app URLs:"
echo "- Main App: $APP_URL"
echo "- API Docs: $APP_URL/docs"
echo "- Health Check: $APP_URL/health"
echo ""
echo "If all tests passed, your app is successfully deployed! 🚀" 