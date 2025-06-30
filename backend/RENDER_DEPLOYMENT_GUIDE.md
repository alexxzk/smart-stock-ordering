# Render Deployment Guide

## 🚀 Deployment Steps

### 1. Environment Variables Setup

Add these environment variables in your Render dashboard under **Environment Variables**:

#### Firebase Configuration
```
FIREBASE_PROJECT_ID=ordix-65b91
FIREBASE_PRIVATE_KEY_ID=756baae223c75323be849546b88a7c04c610bc75
FIREBASE_PRIVATE_KEY=-----BEGIN PRIVATE KEY-----\nMIIEvgIBADANBgkqhkiG9w0BAQEFAASCBKgwggSkAgEAAoIBAQCt4PvqdoMJj4eT\nTD1SztrSJLiefEWCClNAw7PJsdIOD8kqOwl1PRXKWUujMxkNEL/hqHwSmVvLDb8E\nBBKzWJq5Ych8cHO79qtXooBO2oCiUgSc34QgMjSxiyY2/7mzZYo6LTsZtzv5gdab\nDqVsWdxVY/QNNUtNecnOvttQMOQqfbcz37YTakG0zsJvAHSpOnm07uLZ1H2ZgiEE\n7blnmalMOXz+bj24ed6rQMxBXJT6HEXXq6t0SVpQKV8KqcHnMWC2wiLt7G4aPwpm\nM3OKUMik+R2ETr2kkeEOTH9VUb/tHg3QYrFVRPZ2rZvCz7JWvyUh6vNTrPTRLRdu\nadQCNz7jAgMBAAECggEAIfNurOrEDk9YtRGrXapnPqYN6GAygEA83kX4KndOoRFD\nAbxyTdKGGTMTWkPlbdAp70ljJIyOSFkgRYv4DM3NtEncCDQ63OY+sYdYz0zJ1if2\nn5zjIxg6gro9VXrcSyOV+GMRiaVmEANioHcdJMltBL1WD2grEm8n0PciQoexXXxI\n+ecmZ2qeARN5gY9Az7iMczNQFHjXQbGQQ6WWDkElEcEFqhmXBTUmc5eJyoMe/fbj\n7ZP16kleIq3zc/SfnPgeN3YIZIyVaWz7fvGxmwEbuOebNu5BnQxSWWEVvQMAWo+D\nmzgN7zqe8EceePE+cYTnD1qtUNqQqHrI+x/SC8c83QKBgQDikaMTeS+0PhsHRyh+\nqsgLMnKqeAdo0qPVlHv0cWm3dbH4QnViK+NAfIUgjZvGvktEHXC4uxjZ+Sajf2XO\nfZLWQToeF6OYPeWA8woqHn9vZhNd/Kx1vYPWlgK/398F9qvUncdTwUb0D67PT2as\nCYmzhIqwGPh7nPufP+g4MhE99wKBgQDEdy68N9dlpiAee2vYC9ftDzA+bZDewFmj\npi6d8bZI8Z/8n+Y66Me32D/owgJA35BFbTYggD+MCDo3EdSotdXkbBBRr7l0++ul\n/8ajirZBtYDZItZBExki0ADdmFfIIBSI0yXHwu8XikYX1xfaze/iGbH91vhXfmeY\nVQ+QZeI7dQKBgCsDbyxRQ4c6izMUhVGW5qeJik9mvjFeXBA+QlIj/egAhisVoudi\nYaBqg3OsrrhKhEuIM1A+5Pbs4DMGCrPrDydx9rCj2EEc7ydN/M4GQDdL771WLP+l\nXRQuIpN+0v502CZjVeZGuUu4dn2RG3Lp1KSqMxI/i10cboDLRzD0AGX9AoGBALvB\nBonbd97txw46dxLOJrmnZTyT6vnlqwTJIQ3SXJkTSQjdKuIragoZAOKI3ixvOuoO\nd8bRqWlCx5evU6Mzu0iDuYjHPZ49zrMiYAwU2R6svYlFUKp5/PCXBey/1Uws1FL6\nLsXcVjAR9fB8n5B8dH6IfeCPm1/KLmiXCbu+klitAoGBAI8cX5NJluAmSGE+CiXU\nh7JtmjS8gkDrs0JnOTusxmdoyDyAARHrUGFJo7cFvGozVJ127PHNIUNquf63SIU6\nwE+gVYvbermNtSyPPhvx7EWPYbGKZl9e/7o6fb/0xsQAfhZtT6nbgWDviexJZ3Uc\nb8ZVNA3jAFQxaBIdVvFDwzDX\n-----END PRIVATE KEY-----\n
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-fbsvc@ordix-65b91.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=107886089682568023479
FIREBASE_CLIENT_CERT_URL=https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-fbsvc%40ordix-65b91.iam.gserviceaccount.com
```

#### Production Settings
```
DEV_MODE=false
DEBUG=false
```

#### Security
```
SECRET_KEY=ordix-production-secret-key-2024-secure-random-string
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

#### CORS Configuration
```
FRONTEND_URL=https://smart-stock-ordering-frontend.onrender.com
```

#### Optional Weather API
```
OPENWEATHER_API_KEY=your-openweather-api-key
WEATHER_LOCATION=London,UK
```

### 2. Deployment Configuration

Your `render.yaml` is already configured correctly with:
- ✅ Service name: `smart-stock-ordering-api`
- ✅ Build command: `pip install -r requirements.txt`
- ✅ Start command: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
- ✅ Health check: `/health`
- ✅ Python version: 3.11.7

### 3. Testing Deployment

After deployment, test these endpoints:

1. **Health Check**: `https://your-app-name.onrender.com/health`
2. **API Root**: `https://your-app-name.onrender.com/`
3. **API Docs**: `https://your-app-name.onrender.com/docs`
4. **Firestore Test**: `https://your-app-name.onrender.com/test-firestore`

### 4. Troubleshooting

#### Common Issues:

1. **Build Failures**: Check that all dependencies are in `requirements.txt`
2. **Environment Variables**: Ensure all Firebase credentials are set correctly
3. **CORS Errors**: Verify frontend URL is in allowed origins
4. **Authentication**: Make sure `DEV_MODE=false` for production

#### Logs:
- Check Render logs for any startup errors
- Monitor the `/health` endpoint for application status

### 5. Post-Deployment

1. Update your frontend to use the new API URL
2. Test all major functionality
3. Monitor performance and logs
4. Set up any additional monitoring if needed

## 🎯 Ready to Deploy!

Your application is now configured for production deployment on Render. The key changes made:

- ✅ Updated CORS settings for production URLs
- ✅ Created production environment configuration
- ✅ Set up proper security settings
- ✅ Provided complete environment variable list

Deploy with confidence! 🚀 