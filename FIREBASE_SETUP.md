# Firebase Auth Setup Guide

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Create a project" or "Add project"
3. Enter a project name (e.g., "ordix-stock-ordering")
4. Choose whether to enable Google Analytics (optional)
5. Click "Create project"

## Step 2: Enable Authentication

1. In your Firebase project, click on "Authentication" in the left sidebar
2. Click "Get started"
3. Click on the "Sign-in method" tab
4. Enable "Email/Password" authentication:
   - Click on "Email/Password"
   - Toggle "Enable" to ON
   - Click "Save"

## Step 3: Get Firebase Configuration

1. In your Firebase project, click on the gear icon (⚙️) next to "Project Overview"
2. Select "Project settings"
3. Scroll down to "Your apps" section
4. Click the web icon (</>)
5. Register your app:
   - Enter app nickname: "ordix-frontend"
   - Check "Also set up Firebase Hosting" (optional)
   - Click "Register app"
6. Copy the Firebase configuration object that looks like this:

```javascript
const firebaseConfig = {
  apiKey: "AIzaSyC...",
  authDomain: "your-project.firebaseapp.com",
  projectId: "your-project-id",
  storageBucket: "your-project.appspot.com",
  messagingSenderId: "123456789",
  appId: "1:123456789:web:abc123"
};
```

## Step 4: Create Environment File

1. In your `frontend` directory, create a file called `.env`
2. Add the following content, replacing the values with your Firebase config:

```env
# Firebase Configuration
VITE_FIREBASE_API_KEY=your-api-key-from-firebase-config
VITE_FIREBASE_AUTH_DOMAIN=your-project-id.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your-project-id
VITE_FIREBASE_STORAGE_BUCKET=your-project-id.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your-sender-id-from-firebase-config
VITE_FIREBASE_APP_ID=your-app-id-from-firebase-config

# API Configuration
VITE_API_URL=http://localhost:8000
```

## Step 5: Create Test User

1. In Firebase Console, go to "Authentication" → "Users"
2. Click "Add user"
3. Enter an email and password for testing
4. Click "Add user"

## Step 6: Test the Setup

1. Make sure your backend is running:
   ```bash
   cd backend
   source venv/bin/activate
   python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. Start your frontend:
   ```bash
   cd frontend
   npm run dev
   ```

3. Open your browser to `http://localhost:5173`
4. You should be redirected to the login page
5. Use the test user credentials you created in Step 5

## Troubleshooting

### Common Issues:

1. **"Firebase: Error (auth/invalid-api-key)"**
   - Check that your API key is correct in the `.env` file
   - Make sure the `.env` file is in the `frontend` directory

2. **"Firebase: Error (auth/user-not-found)"**
   - Make sure you've created a user in Firebase Console
   - Check that the email/password match exactly

3. **"Firebase: Error (auth/wrong-password)"**
   - Double-check the password for your test user

4. **Environment variables not loading**
   - Restart your Vite dev server after creating the `.env` file
   - Make sure the `.env` file is in the correct location

### Verify Configuration:

You can check if your environment variables are loading correctly by adding this to your Login component temporarily:

```javascript
console.log('Firebase Config:', {
  apiKey: import.meta.env.VITE_FIREBASE_API_KEY,
  authDomain: import.meta.env.VITE_FIREBASE_AUTH_DOMAIN,
  projectId: import.meta.env.VITE_FIREBASE_PROJECT_ID
});
```

## Next Steps

Once Firebase Auth is working:

1. Test login with your test user
2. You should be redirected to the dashboard after successful login
3. Test the logout functionality
4. The app will automatically handle authentication state

## Security Notes

- Never commit your `.env` file to version control
- The `.env` file is already in `.gitignore`
- Firebase API keys are safe to expose in frontend code (they're designed for this)
- For production, consider setting up proper domain restrictions in Firebase Console 