// Simple environment configuration that works around TypeScript issues
export const config = {
  apiUrl: (import.meta as any)?.env?.VITE_API_URL || 'http://localhost:8000',
  firebase: {
    apiKey: (import.meta as any)?.env?.VITE_FIREBASE_API_KEY || "YOUR_API_KEY",
    authDomain: (import.meta as any)?.env?.VITE_FIREBASE_AUTH_DOMAIN || "YOUR_PROJECT_ID.firebaseapp.com",
    projectId: (import.meta as any)?.env?.VITE_FIREBASE_PROJECT_ID || "YOUR_PROJECT_ID",
    storageBucket: (import.meta as any)?.env?.VITE_FIREBASE_STORAGE_BUCKET || "YOUR_PROJECT_ID.appspot.com",
    messagingSenderId: (import.meta as any)?.env?.VITE_FIREBASE_MESSAGING_SENDER_ID || "YOUR_MESSAGING_SENDER_ID",
    appId: (import.meta as any)?.env?.VITE_FIREBASE_APP_ID || "YOUR_APP_ID",
    measurementId: (import.meta as any)?.env?.VITE_FIREBASE_MEASUREMENT_ID || "YOUR_MEASUREMENT_ID"
  }
}; 