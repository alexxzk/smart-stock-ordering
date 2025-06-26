# Backend Deployment Guide

This guide will help you deploy the Smart Stock Ordering API backend to either Railway or Render.

## Prerequisites

1. **Firebase Project Setup**
   - Create a Firebase project at https://console.firebase.google.com/
   - Enable Authentication and Firestore
   - Download your Firebase service account key (JSON file)
   - Note your Firebase project ID

2. **Git Repository**
   - Ensure your code is in a Git repository (GitHub, GitLab, etc.)

## Option 1: Deploy to Railway

### Step 1: Create Railway Account
1. Go to https://railway.app/
2. Sign up with your GitHub account
3. Create a new project

### Step 2: Connect Repository
1. Click "Deploy from GitHub repo"
2. Select your repository
3. Railway will automatically detect the Python project

### Step 3: Configure Environment Variables
In your Railway project dashboard, go to the "Variables" tab and add:

```
FIREBASE_PROJECT_ID=your-firebase-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=your-service-account-email
FIREBASE_CLIENT_ID=your-client-id
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=your-cert-url
DEV_MODE=false
```

### Step 4: Deploy
1. Railway will automatically deploy when you push to your main branch
2. Or click "Deploy" in the dashboard
3. Your API will be available at the provided URL

## Option 2: Deploy to Render

### Step 1: Create Render Account
1. Go to https://render.com/
2. Sign up with your GitHub account
3. Create a new account

### Step 2: Create New Web Service
1. Click "New +" → "Web Service"
2. Connect your GitHub repository
3. Configure the service:
   - **Name**: smart-stock-ordering-api
   - **Environment**: Python
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Step 3: Configure Environment Variables
In the "Environment" tab, add the same variables as listed above for Railway.

### Step 4: Deploy
1. Click "Create Web Service"
2. Render will build and deploy your application
3. Your API will be available at the provided URL

## Environment Variables Setup

### Firebase Service Account Setup
1. Go to Firebase Console → Project Settings → Service Accounts
2. Click "Generate new private key"
3. Download the JSON file
4. Extract the values and add them as environment variables:

```bash
# Example of how to extract from the JSON file:
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=abc123...
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQC...\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=123456789012345678901
FIREBASE_AUTH_URI=https://accounts.google.com/o/oauth2/auth
FIREBASE_TOKEN_URI=https://oauth2.googleapis.com/token
FIREBASE_AUTH_PROVIDER_X509_CERT_URL=https://www.googleapis.com/oauth2/v1/certs
FIREBASE_CLIENT_X509_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-xxxxx%40your-project.iam.gserviceaccount.com
```

## Testing Your Deployment

Once deployed, test your API:

1. **Health Check**: `GET https://your-app-url.railway.app/health`
2. **API Documentation**: `https://your-app-url.railway.app/docs`
3. **Root Endpoint**: `GET https://your-app-url.railway.app/`

## Troubleshooting

### Common Issues

1. **Build Failures**
   - Check that all dependencies are in `requirements.txt`
   - Ensure Python version is compatible (3.11+)

2. **Environment Variables**
   - Verify all Firebase credentials are correctly set
   - Check that `DEV_MODE=false` in production

3. **Port Issues**
   - The app uses `$PORT` environment variable (automatically set by platforms)
   - Ensure uvicorn is configured to use `0.0.0.0` as host

4. **Firebase Connection**
   - Test with the `/test-firestore` endpoint
   - Verify service account has proper permissions

### Logs
- **Railway**: Check the "Deployments" tab for build and runtime logs
- **Render**: Check the "Logs" tab in your service dashboard

## Updating Your Deployment

Both platforms support automatic deployments:
- Push changes to your main branch
- The platform will automatically rebuild and deploy
- Monitor the deployment logs for any issues

## Cost Considerations

- **Railway**: Free tier available, then pay-as-you-go
- **Render**: Free tier available, then $7/month for web services

Both platforms offer generous free tiers for development and testing. 