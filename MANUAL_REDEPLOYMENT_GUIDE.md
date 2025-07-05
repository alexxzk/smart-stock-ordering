# 🔄 Manual Redeployment Guide

## Overview

This guide will walk you through manually redeploying your Smart Stock Ordering application with the new POS and supplier integrations.

## Prerequisites

- Git repository connected to GitHub
- Railway account (for backend)
- Vercel account (for frontend)
- Node.js and npm installed

---

## 🚀 Step 1: Prepare Your Code

### 1.1 Commit Your Changes

```bash
# Check current status
git status

# Add all changes
git add .

# Commit with descriptive message
git commit -m "feat: Add POS and supplier integrations"

# Push to GitHub
git push origin main
```

### 1.2 Verify Your Changes

Make sure these new files are included:
- `backend/app/api/pos_integrations.py`
- `frontend/src/components/POSIntegrations.tsx`
- `frontend/src/pages/POSIntegrations.tsx`
- Updated `backend/app/main.py`
- Updated `frontend/src/App.tsx`
- Updated `frontend/src/components/Sidebar.tsx`

---

## 🏗️ Step 2: Deploy Backend (Railway)

### 2.1 Using Railway CLI

```bash
# Navigate to backend directory
cd backend

# Install Railway CLI (if not installed)
npm install -g @railway/cli

# Login to Railway
railway login

# Deploy to Railway
railway up

# Get your deployment URL
railway status
```

### 2.2 Using Railway Dashboard

1. Go to [Railway Dashboard](https://railway.app/dashboard)
2. Select your project
3. Go to **Deployments** tab
4. Click **Deploy** or wait for automatic deployment
5. Copy the deployment URL

### 2.3 Verify Backend Deployment

```bash
# Test health endpoint
curl https://your-railway-url.railway.app/health

# Test new POS integrations endpoint
curl https://your-railway-url.railway.app/api/pos-integrations/systems \
  -H "Authorization: Bearer test-token"

# Test new supplier integrations endpoint
curl https://your-railway-url.railway.app/api/supplier-integrations/suppliers \
  -H "Authorization: Bearer test-token"
```

---

## 🎨 Step 3: Deploy Frontend (Vercel)

### 3.1 Using Vercel CLI

```bash
# Navigate to frontend directory
cd frontend

# Install Vercel CLI (if not installed)
npm install -g vercel

# Login to Vercel
vercel login

# Deploy to Vercel
vercel --prod
```

### 3.2 Using Vercel Dashboard

1. Go to [Vercel Dashboard](https://vercel.com/dashboard)
2. Click **New Project**
3. Import your GitHub repository
4. Configure build settings:
   - **Framework Preset**: Vite
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`
5. Add environment variables:
   - `VITE_API_URL`: Your Railway backend URL
6. Click **Deploy**

### 3.3 Update Environment Variables

If you need to update the API URL:

```bash
# In your frontend directory
echo "VITE_API_URL=https://your-railway-url.railway.app" > .env
```

Or update in Vercel dashboard:
1. Go to your project settings
2. Navigate to **Environment Variables**
3. Update `VITE_API_URL` with your new backend URL

---

## 🧪 Step 4: Test Your Deployment

### 4.1 Test Backend APIs

```bash
# Test the complete integration
python test_integrations.py
```

### 4.2 Test Frontend Features

1. Open your deployed frontend URL
2. Navigate to **POS Integrations** in the sidebar
3. Try connecting a test POS system
4. Navigate to **Suppliers** and test supplier features
5. Verify all new features are working

### 4.3 Manual API Testing

```bash
# Test POS systems endpoint
curl -X GET "https://your-backend-url/api/pos-integrations/systems" \
  -H "Authorization: Bearer test-token"

# Test supplier pricing
curl -X POST "https://your-backend-url/api/supplier-integrations/pricing" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "supplier_id": "sysco",
    "items": ["coffee beans", "milk"]
  }'

# Test POS connection creation
curl -X POST "https://your-backend-url/api/pos-integrations/connect" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test-token" \
  -d '{
    "pos_type": "square",
    "name": "Test Store",
    "config": {"access_token": "test"},
    "is_active": true
  }'
```

---

## 🔧 Step 5: Configure Production Settings

### 5.1 Backend Environment Variables

In Railway dashboard, ensure these variables are set:

```bash
DEV_MODE=false
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY=your-private-key
FIREBASE_CLIENT_EMAIL=your-client-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=your-cert-url
```

### 5.2 Frontend Environment Variables

In Vercel dashboard, ensure these variables are set:

```bash
VITE_API_URL=https://your-railway-backend-url.railway.app
VITE_FIREBASE_API_KEY=your-firebase-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id
VITE_FIREBASE_APP_ID=your-app-id
```

---

## 🚨 Troubleshooting

### Common Issues

#### Backend Deployment Fails

**Problem**: Railway deployment fails
**Solutions**:
1. Check Railway logs for errors
2. Verify `requirements.txt` is up to date
3. Ensure all imports are correct
4. Check environment variables

```bash
# Check Railway logs
railway logs

# Verify requirements
pip install -r requirements.txt
```

#### Frontend Build Fails

**Problem**: Vercel build fails
**Solutions**:
1. Check build logs in Vercel dashboard
2. Verify all dependencies are in `package.json`
3. Check for TypeScript errors
4. Ensure all imports are correct

```bash
# Test build locally
npm run build

# Check for TypeScript errors
npx tsc --noEmit
```

#### API Connection Issues

**Problem**: Frontend can't connect to backend
**Solutions**:
1. Verify `VITE_API_URL` is correct
2. Check CORS settings in backend
3. Ensure backend is running
4. Test API endpoints directly

```bash
# Test API connection
curl https://your-backend-url/health

# Check CORS headers
curl -I https://your-backend-url/api/pos-integrations/systems
```

### Error Codes

| Error | Meaning | Solution |
|-------|---------|----------|
| `ERR_MODULE_NOT_FOUND` | Missing dependency | Run `npm install` |
| `ERR_CONNECTION_REFUSED` | Backend not running | Check Railway deployment |
| `401 Unauthorized` | Auth token missing | Check Firebase config |
| `500 Internal Server Error` | Backend error | Check Railway logs |

---

## ✅ Verification Checklist

After deployment, verify:

- [ ] Backend health endpoint responds
- [ ] POS integrations API works
- [ ] Supplier integrations API works
- [ ] Frontend builds successfully
- [ ] Frontend connects to backend
- [ ] New POS Integrations page loads
- [ ] New supplier features work
- [ ] All existing features still work
- [ ] Environment variables are set correctly

---

## 📞 Support

If you encounter issues:

1. **Check Logs**: Railway and Vercel provide detailed logs
2. **Test Locally**: Run the app locally to isolate issues
3. **Review Changes**: Ensure all new files are committed
4. **Contact Support**: Use the deployment platform's support

---

## 🎉 Success!

Once deployed, your app will have:

- ✅ **POS Integrations**: Connect to Square, Toast, Clover, etc.
- ✅ **Enhanced Supplier Management**: Real-time pricing and ordering
- ✅ **Quick Ordering**: One-click order placement
- ✅ **Real-time Sync**: Automatic inventory updates
- ✅ **Modern UI**: Updated interface with new features

Your Smart Stock Ordering system is now ready for production use with the new POS and supplier integrations! 🚀 