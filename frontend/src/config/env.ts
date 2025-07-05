// Simple environment configuration that works around TypeScript issues
export const config = {
  apiUrl: (import.meta as any)?.env?.VITE_API_URL || 'http://localhost:8000',
  firebase: {
    apiKey: (import.meta as any)?.env?.VITE_FIREBASE_API_KEY || "AIzaSyCaFitFM9ZbS2fjz0QJvocpGLUkzeF5AXI",
    authDomain: (import.meta as any)?.env?.VITE_FIREBASE_AUTH_DOMAIN || "ordix-stock-ordering.firebaseapp.com",
    projectId: (import.meta as any)?.env?.VITE_FIREBASE_PROJECT_ID || "ordix-stock-ordering",
    storageBucket: (import.meta as any)?.env?.VITE_FIREBASE_STORAGE_BUCKET || "ordix-stock-ordering.firebasestorage.app",
    messagingSenderId: (import.meta as any)?.env?.VITE_FIREBASE_MESSAGING_SENDER_ID || "758571654408",
    appId: (import.meta as any)?.env?.VITE_FIREBASE_APP_ID || "1:758571654408:web:99d197679cab335a56e0bd",
    measurementId: (import.meta as any)?.env?.VITE_FIREBASE_MEASUREMENT_ID || "G-JV7R4PZQHV"
  }
}; 