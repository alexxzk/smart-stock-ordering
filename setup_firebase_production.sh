#!/bin/bash

echo "🔒 Setting up Firebase Production Environment"
echo "=============================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}Step 1: Firebase Project Setup${NC}"
echo "1. Go to https://console.firebase.google.com/"
echo "2. Click 'Create a project'"
echo "3. Enter your café name (e.g., 'my-cafe-prod')"
echo "4. Enable Google Analytics (optional)"
echo "5. Click 'Create project'"
echo ""

echo -e "${BLUE}Step 2: Enable Services${NC}"
echo "In your Firebase project, enable these services:"
echo "✅ Authentication"
echo "✅ Firestore Database"
echo "✅ Storage (optional, for images)"
echo "✅ Functions (optional, for automation)"
echo ""

echo -e "${BLUE}Step 3: Authentication Setup${NC}"
echo "In Authentication > Sign-in method, enable:"
echo "✅ Email/Password"
echo "✅ Google (for employees)"
echo "✅ Phone (for customers)"
echo ""

echo -e "${BLUE}Step 4: Firestore Database Setup${NC}"
echo "1. Go to Firestore Database"
echo "2. Click 'Create database'"
echo "3. Choose 'Start in production mode'"
echo "4. Select a location close to your café"
echo "5. Click 'Done'"
echo ""

echo -e "${BLUE}Step 5: Get Configuration${NC}"
echo "1. Go to Project Settings (gear icon)"
echo "2. Scroll down to 'Your apps'"
echo "3. Click 'Add app' > Web"
echo "4. Register app with name 'Café Management'"
echo "5. Copy the config object"
echo ""

echo -e "${BLUE}Step 6: Service Account Setup${NC}"
echo "1. In Project Settings > Service accounts"
echo "2. Click 'Generate new private key'"
echo "3. Download the JSON file"
echo "4. Keep this file secure - never commit to git!"
echo ""

echo -e "${BLUE}Step 7: Update Environment Files${NC}"
echo "Update your .env files with the new Firebase config:"
echo ""

echo -e "${YELLOW}Backend (.env):${NC}"
echo "FIREBASE_PROJECT_ID=your-project-id"
echo "FIREBASE_PRIVATE_KEY=your-private-key"
echo "FIREBASE_CLIENT_EMAIL=your-service-account-email"
echo ""

echo -e "${YELLOW}Frontend (.env):${NC}"
echo "VITE_FIREBASE_API_KEY=your-api-key"
echo "VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com"
echo "VITE_FIREBASE_PROJECT_ID=your-project-id"
echo "VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com"
echo "VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id"
echo "VITE_FIREBASE_APP_ID=your-app-id"
echo ""

echo -e "${BLUE}Step 8: Security Rules${NC}"
echo "In Firestore > Rules, replace with secure rules:"
echo "See FIREBASE_SECURITY_GUIDE.md for complete rules"
echo ""

echo -e "${BLUE}Step 9: Test Setup${NC}"
echo "1. Start your backend: cd backend && python -m uvicorn app.main:app --reload"
echo "2. Start your frontend: cd frontend && npm run dev"
echo "3. Test authentication and data access"
echo ""

echo -e "${GREEN}✅ Firebase Production Setup Complete!${NC}"
echo ""
echo -e "${YELLOW}Important Security Notes:${NC}"
echo "🔒 Never commit .env files to git"
echo "🔒 Keep service account keys secure"
echo "🔒 Regularly review security rules"
echo "🔒 Monitor Firebase usage and costs"
echo "🔒 Set up automated backups"
echo ""

echo -e "${BLUE}Need Help?${NC}"
echo "📖 Read FIREBASE_SECURITY_GUIDE.md for detailed instructions"
echo "🔧 Run this script again if you need to review the steps"
echo "📞 Contact me for additional support" 