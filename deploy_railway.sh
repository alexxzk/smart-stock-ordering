#!/bin/bash

# 🚂 Railway Deployment Script for Smart Stock Ordering App
# This script helps you deploy your app to Railway

set -e

echo "🚂 RAILWAY DEPLOYMENT SETUP"
echo "=========================="

# Check if Railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
else
    echo "✅ Railway CLI found"
fi

# Check if logged in to Railway
if ! railway whoami &> /dev/null; then
    echo "🔐 Please login to Railway:"
    railway login
else
    echo "✅ Already logged in to Railway"
fi

echo ""
echo "📋 DEPLOYMENT STEPS:"
echo "==================="
echo ""
echo "1. 🏗️  Create Railway project:"
echo "   railway init"
echo ""
echo "2. 🔧 Add environment variables:"
echo "   railway variables set FIREBASE_PROJECT_ID=your_project_id"
echo "   railway variables set FIREBASE_PRIVATE_KEY_ID=your_private_key_id"
echo "   railway variables set FIREBASE_PRIVATE_KEY='your_private_key'"
echo "   railway variables set FIREBASE_CLIENT_EMAIL=your_client_email"
echo "   railway variables set FIREBASE_CLIENT_ID=your_client_id"
echo "   railway variables set FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth"
echo "   railway variables set FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token"
echo "   railway variables set FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs"
echo "   railway variables set FIREBASE_CLIENT_X509_CERT_URL=your_cert_url"
echo "   railway variables set DEV_MODE=false"
echo ""
echo "3. 🗄️  Add Redis database:"
echo "   railway add"
echo "   (Select Redis from the list)"
echo ""
echo "4. 🚀 Deploy backend:"
echo "   railway up"
echo ""
echo "5. 🌐 Deploy frontend (separate service):"
echo "   cd frontend"
echo "   railway init"
echo "   railway up"
echo ""
echo "📝 NOTES:"
echo "========"
echo "- Backend will be available at: https://your-app-name.railway.app"
echo "- Frontend will be available at: https://your-frontend-name.railway.app"
echo "- Redis will be automatically connected via REDIS_URL environment variable"
echo "- Update frontend API URL to point to your backend URL"
echo ""
echo "🔍 TROUBLESHOOTING:"
echo "=================="
echo "- Check logs: railway logs"
echo "- View variables: railway variables"
echo "- Restart service: railway restart"
echo "- Check health: curl https://your-app-name.railway.app/health"
echo ""
echo "✅ Ready to deploy! Run the commands above step by step." 