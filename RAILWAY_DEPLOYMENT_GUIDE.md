# 🚂 Railway Deployment Guide

## 📋 **Prerequisites**

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway CLI**: Install with `npm install -g @railway/cli`
3. **Git Repository**: Your code should be in a Git repo (GitHub, GitLab, etc.)

## 🚀 **Step-by-Step Deployment**

### **Step 1: Prepare Your Project**

```bash
# Make sure you're in the project root
cd /path/to/your/smart-stock-app

# Make deployment script executable
chmod +x deploy_railway.sh

# Run the deployment setup
./deploy_railway.sh
```

### **Step 2: Deploy Backend**

```bash
# Navigate to backend directory
cd backend

# Initialize Railway project
railway init

# Add environment variables (replace with your actual values)
railway variables set FIREBASE_PROJECT_ID=your-project-id
railway variables set FIREBASE_PRIVATE_KEY_ID=your-private-key-id
railway variables set FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour Private Key Here\n-----END PRIVATE KEY-----\n"
railway variables set FIREBASE_CLIENT_EMAIL=your-service-account@your-project.iam.gserviceaccount.com
railway variables set FIREBASE_CLIENT_ID=your-client-id
railway variables set FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
railway variables set FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
railway variables set FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
railway variables set FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/your-service-account%40your-project.iam.gserviceaccount.com
railway variables set DEV_MODE=false

# Add Redis database
railway add
# Select "Redis" from the list

# Deploy the backend
railway up
```

### **Step 3: Get Backend URL**

After deployment, Railway will give you a URL like:
```
https://your-app-name-production.up.railway.app
```

Save this URL - you'll need it for the frontend.

### **Step 4: Deploy Frontend**

```bash
# Navigate to frontend directory
cd ../frontend

# Initialize Railway project for frontend
railway init

# Add environment variables
railway variables set VITE_API_URL=https://your-app-name-production.up.railway.app

# Deploy frontend
railway up
```

## 🔧 **Configuration Files**

### **railway.json** (Backend)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "gunicorn -k uvicorn.workers.UvicornWorker app.main:app --workers 4 --bind 0.0.0.0:$PORT",
    "healthcheckPath": "/health",
    "healthcheckTimeout": 300,
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### **railway.json** (Frontend)
```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "npm run preview",
    "healthcheckPath": "/",
    "healthcheckTimeout": 300
  }
}
```

## 🌐 **Environment Variables**

### **Backend Variables**
- `FIREBASE_PROJECT_ID`: Your Firebase project ID
- `FIREBASE_PRIVATE_KEY_ID`: From Firebase service account
- `FIREBASE_PRIVATE_KEY`: From Firebase service account
- `FIREBASE_CLIENT_EMAIL`: From Firebase service account
- `FIREBASE_CLIENT_ID`: From Firebase service account
- `FIREBASE_AUTH_URI`: https://accounts.google.com/o/oauth2/auth
- `FIREBASE_TOKEN_URI`: https://oauth2.googleapis.com/token
- `FIREBASE_AUTH_PROVIDER_X509_CERT_URL`: https://www.googleapis.com/oauth2/v1/certs
- `FIREBASE_CLIENT_X509_CERT_URL`: From Firebase service account
- `DEV_MODE`: false
- `REDIS_URL`: Automatically set by Railway Redis add-on

### **Frontend Variables**
- `VITE_API_URL`: Your backend Railway URL

## 📊 **Performance Features**

### **Backend Optimizations**
- ✅ **Gunicorn + Uvicorn**: 4 workers for parallel processing
- ✅ **Redis Caching**: Persistent, shared cache across instances
- ✅ **Health Checks**: Automatic monitoring and restart
- ✅ **Gzip Compression**: Faster response times
- ✅ **Performance Logging**: Detailed timing metrics

### **Frontend Optimizations**
- ✅ **Static Hosting**: CDN-backed delivery
- ✅ **Client-Side Caching**: 1-minute TTL for API responses
- ✅ **Request Deduplication**: Prevents duplicate API calls
- ✅ **Automatic Retry**: Handles temporary failures

## 🔍 **Monitoring & Debugging**

### **Check Deployment Status**
```bash
# View logs
railway logs

# Check service status
railway status

# View environment variables
railway variables

# Restart service if needed
railway restart
```

### **Health Checks**
```bash
# Backend health
curl https://your-backend-url.railway.app/health

# Cache health
curl https://your-backend-url.railway.app/api/cache/health

# Cache stats
curl https://your-backend-url.railway.app/api/cache/stats
```

### **Performance Testing**
```bash
# Test API endpoints
curl https://your-backend-url.railway.app/api/inventory/
curl https://your-backend-url.railway.app/api/suppliers/
curl https://your-backend-url.railway.app/api/forecasting/models
```

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Build Fails**
   - Check `requirements.txt` has all dependencies
   - Verify Python version compatibility
   - Check Railway logs for specific errors

2. **Environment Variables**
   - Ensure all Firebase variables are set correctly
   - Check for typos in variable names
   - Verify Firebase service account permissions

3. **Redis Connection**
   - Ensure Redis add-on is added to the project
   - Check `REDIS_URL` is automatically set
   - Verify Redis is running in Railway dashboard

4. **CORS Issues**
   - Update frontend API URL to match backend URL
   - Check CORS settings in backend code

### **Performance Issues**

1. **Slow First Load**
   - This is normal (cold start)
   - Subsequent loads will be cached and fast

2. **High Memory Usage**
   - Monitor in Railway dashboard
   - Consider upgrading plan if needed

3. **Database Slow**
   - Check Firestore indexes are built
   - Monitor Firestore usage in Firebase console

## 📈 **Scaling**

### **Railway Plans**
- **Free**: 500 hours/month, 512MB RAM
- **Pro**: $5/month, 2GB RAM, unlimited hours
- **Team**: $20/month, 4GB RAM, team features

### **Auto-Scaling**
- Railway automatically scales based on traffic
- Redis cache is shared across all instances
- No manual scaling configuration needed

## 🎉 **Success!**

After deployment, your app will be available at:
- **Frontend**: `https://your-frontend-name.railway.app`
- **Backend API**: `https://your-backend-name.railway.app`
- **API Docs**: `https://your-backend-name.railway.app/docs`

### **Expected Performance**
- **First API call**: 0.5-1.0s (cold start)
- **Cached API calls**: 0.001-0.005s (instant)
- **Frontend load**: < 2s (CDN-backed)
- **Database queries**: 0.05-0.15s (with indexes)

Your smart stock ordering app is now deployed with production-grade performance optimizations! 🚀 