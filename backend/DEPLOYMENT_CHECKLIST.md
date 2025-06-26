# 🚀 Deployment Checklist

## ✅ Pre-Deployment Setup

### Firebase Setup
- [ ] Created Firebase project
- [ ] Enabled Authentication (Email/Password)
- [ ] Enabled Firestore Database
- [ ] Downloaded service account JSON file
- [ ] Saved JSON file as `firebase-service-account.json` in backend folder

### Code Preparation
- [ ] All deployment files are in place:
  - [ ] `Procfile`
  - [ ] `runtime.txt`
  - [ ] `railway.json` (for Railway)
  - [ ] `render.yaml` (for Render)
  - [ ] `requirements.txt` (clean, no problematic dependencies)
- [ ] Code is committed to Git repository
- [ ] Repository is pushed to GitHub

## 🔧 Environment Variables Setup

### Extract Firebase Credentials
```bash
cd backend
python extract_firebase_env.py firebase-service-account.json
```

### Required Environment Variables
- [ ] `FIREBASE_PROJECT_ID`
- [ ] `FIREBASE_PRIVATE_KEY_ID`
- [ ] `FIREBASE_PRIVATE_KEY` (with quotes and \n)
- [ ] `FIREBASE_CLIENT_EMAIL`
- [ ] `FIREBASE_CLIENT_ID`
- [ ] `FIREBASE_AUTH_URI`
- [ ] `FIREBASE_TOKEN_URI`
- [ ] `FIREBASE_AUTH_PROVIDER_X509_CERT_URL`
- [ ] `FIREBASE_CLIENT_X509_CERT_URL`
- [ ] `DEV_MODE=false`

## 🚂 Railway Deployment

### Account Setup
- [ ] Created Railway account
- [ ] Connected GitHub account

### Project Setup
- [ ] Created new project
- [ ] Connected repository
- [ ] Added all environment variables
- [ ] Triggered deployment

### Verification
- [ ] Build completed successfully
- [ ] Service is running
- [ ] Health check passes: `/health`
- [ ] API docs accessible: `/docs`

## 🌐 Render Deployment (Alternative)

### Account Setup
- [ ] Created Render account
- [ ] Connected GitHub account

### Service Setup
- [ ] Created new Web Service
- [ ] Connected repository
- [ ] Set build command: `pip install -r requirements.txt`
- [ ] Set start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- [ ] Added all environment variables
- [ ] Deployed service

### Verification
- [ ] Build completed successfully
- [ ] Service is running
- [ ] Health check passes: `/health`
- [ ] API docs accessible: `/docs`

## 🧪 Testing

### Run Test Script
```bash
cd backend
python test_deployment.py https://your-deployment-url
```

### Manual Testing
- [ ] Health endpoint: `GET /health`
- [ ] Root endpoint: `GET /`
- [ ] API documentation: `GET /docs`
- [ ] Firestore test: `GET /test-firestore`
- [ ] Authentication endpoints (if needed)

## 🔗 Frontend Integration

### Update Frontend Configuration
- [ ] Update API base URL in frontend
- [ ] Test frontend-backend connection
- [ ] Verify CORS is working

### Environment Variables for Frontend
- [ ] `VITE_API_BASE_URL=https://your-deployment-url`
- [ ] Firebase config for frontend authentication

## 📊 Monitoring

### Set Up Monitoring
- [ ] Enable logging in deployment platform
- [ ] Set up error notifications (optional)
- [ ] Monitor API usage and performance

### Common Issues to Watch For
- [ ] Environment variables not set correctly
- [ ] Firebase credentials issues
- [ ] Port configuration problems
- [ ] CORS issues with frontend
- [ ] Memory/CPU limits

## 🎉 Post-Deployment

### Documentation
- [ ] Update README with deployment URL
- [ ] Document environment variables
- [ ] Create troubleshooting guide

### Security
- [ ] Review Firebase security rules
- [ ] Enable authentication in production
- [ ] Set up proper CORS origins
- [ ] Review API rate limiting

### Performance
- [ ] Monitor response times
- [ ] Check memory usage
- [ ] Optimize if needed

## 🆘 Troubleshooting

### Common Problems
1. **Build Failures**
   - Check `requirements.txt`
   - Verify Python version compatibility
   - Check for missing dependencies

2. **Runtime Errors**
   - Check environment variables
   - Verify Firebase credentials
   - Check logs for specific errors

3. **Connection Issues**
   - Verify CORS configuration
   - Check network connectivity
   - Test with curl or Postman

### Useful Commands
```bash
# Test local deployment
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# Test deployment
python test_deployment.py https://your-url

# Check logs (platform specific)
# Railway: Check Deployments tab
# Render: Check Logs tab
```

## 📞 Support

If you encounter issues:
1. Check the deployment platform logs
2. Verify all environment variables are set
3. Test locally first
4. Check the troubleshooting section in `DEPLOYMENT.md` 