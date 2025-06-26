# Firebase Quick Start Guide

## 🚀 Quick Setup (5 minutes)

### 1. Create Firebase Project
1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project"
3. Name: `smart-stock-ordering`
4. Enable Google Analytics (optional)
5. Click "Create project"

### 2. Enable Services
1. **Authentication** → Get Started → Email/Password → Enable
2. **Firestore Database** → Create Database → Start in test mode
3. **Storage** → Get Started (optional)

### 3. Get Configuration
1. **Backend (Service Account):**
   - Project Settings → Service Accounts
   - Generate new private key
   - Save as `backend/config/firebase_config.json`

2. **Frontend (Web App):**
   - Project Settings → General → Your apps
   - Add web app → Name: "Smart Stock Frontend"
   - Copy config to `frontend/src/config/firebase.ts`

### 4. Run Setup Script
```bash
./setup_firebase.sh
```

### 5. Test
```bash
# Terminal 1: Backend
cd backend && python -m uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend  
cd frontend && npm run dev
```

Visit: http://localhost:5173

## 🔧 Manual Configuration

### Backend Environment Variables
Create `backend/.env`:
```env
FIREBASE_PROJECT_ID=your-project-id
FIREBASE_PRIVATE_KEY_ID=your-private-key-id
FIREBASE_PRIVATE_KEY="-----BEGIN PRIVATE KEY-----\nYour private key here\n-----END PRIVATE KEY-----\n"
FIREBASE_CLIENT_EMAIL=firebase-adminsdk-xxxxx@your-project-id.iam.gserviceaccount.com
FIREBASE_CLIENT_ID=your-client-id
SECRET_KEY=your-secret-key-here
```

### Frontend Environment Variables
Create `frontend/.env`:
```env
VITE_FIREBASE_API_KEY=your-api-key
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-messaging-sender-id
VITE_FIREBASE_APP_ID=your-app-id
VITE_API_BASE_URL=http://localhost:8000
```

## 🔒 Security Rules

Deploy Firestore security rules:
```bash
npm install -g firebase-tools
firebase login
firebase init firestore
firebase deploy --only firestore:rules
```

## 📱 Privacy Features

The app includes:
- ✅ GDPR/CCPA compliance
- ✅ Data export functionality
- ✅ Data deletion requests
- ✅ Privacy consent management
- ✅ Cookie controls
- ✅ Analytics opt-out

## 🚨 Troubleshooting

### Common Issues:

1. **"No module named 'app'"**
   - Run backend from the `backend` directory
   - Ensure you're in the correct directory

2. **Firebase initialization error**
   - Check your service account key format
   - Verify project ID matches

3. **CORS errors**
   - Backend is running on port 8000
   - Frontend is running on port 5173
   - Check CORS settings in `backend/app/main.py`

4. **Authentication fails**
   - Verify Firebase Auth is enabled
   - Check API key in frontend config
   - Ensure service account has proper permissions

### Test Endpoints:
- Backend health: http://localhost:8000/health
- Firebase test: http://localhost:8000/test-firestore
- API docs: http://localhost:8000/docs

## 📞 Support

If you encounter issues:
1. Check the console logs
2. Verify Firebase configuration
3. Test individual endpoints
4. Review the security guide: `FIREBASE_SECURITY_GUIDE.md`

## 🎯 Next Steps

1. **Production Setup:**
   - Update security rules
   - Set up proper authentication
   - Configure monitoring

2. **Data Migration:**
   - Import your existing data
   - Set up backup procedures
   - Test data integrity

3. **Advanced Features:**
   - Gmail API integration
   - Advanced analytics
   - Custom ML models

Happy coding! 🚀 