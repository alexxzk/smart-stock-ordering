import firebase_admin
from firebase_admin import credentials, firestore
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv("config.env")

# Global variables
_db = None

def get_firestore_client():
    """Get Firestore client, initializing Firebase if needed"""
    global _db
    
    # Check if we're in dev mode
    if os.getenv("DEV_MODE", "false").lower() == "true":
        print("✅ Firebase initialized in dev mode (mock)")
        return None
    
    if _db is not None:
        return _db
    
    # Initialize Firebase if not already done
    if not firebase_admin._apps:
        try:
            # For development, you can use a service account key file
            # cred = credentials.Certificate("path/to/serviceAccountKey.json")
            # For production, use environment variables
            firebase_private_key = os.getenv("FIREBASE_PRIVATE_KEY")
            if not firebase_private_key:
                print("⚠️  FIREBASE_PRIVATE_KEY not found in environment variables")
                # Create a dummy app for development
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": "dummy-project",
                    "private_key_id": "dummy",
                    "private_key": "-----BEGIN PRIVATE KEY-----\ndummy\n-----END PRIVATE KEY-----\n",
                    "client_email": "dummy@dummy.iam.gserviceaccount.com",
                    "client_id": "dummy",
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy%40dummy.iam.gserviceaccount.com"
                })
            else:
                # Fix the private key format - handle both escaped and unescaped newlines
                if "\\n" in firebase_private_key:
                    firebase_private_key = firebase_private_key.replace("\\n", "\n")
                
                # Ensure the private key has proper formatting
                if not firebase_private_key.startswith("-----BEGIN PRIVATE KEY-----"):
                    firebase_private_key = f"-----BEGIN PRIVATE KEY-----\n{firebase_private_key}\n-----END PRIVATE KEY-----\n"
                
                cred = credentials.Certificate({
                    "type": "service_account",
                    "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                    "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                    "private_key": firebase_private_key,
                    "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                    "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                    "token_uri": "https://oauth2.googleapis.com/token",
                    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                    "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
                })
            firebase_admin.initialize_app(cred)
            print("✅ Firebase initialized successfully")
        except Exception as e:
            print(f"⚠️  Firebase initialization failed: {e}")
            # Create a dummy app for development
            cred = credentials.Certificate({
                "type": "service_account",
                "project_id": "dummy-project",
                "private_key_id": "dummy",
                "private_key": "-----BEGIN PRIVATE KEY-----\ndummy\n-----END PRIVATE KEY-----\n",
                "client_email": "dummy@dummy.iam.gserviceaccount.com",
                "client_id": "dummy",
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/dummy%40dummy.iam.gserviceaccount.com"
            })
            firebase_admin.initialize_app(cred)
    
    # Initialize Firestore
    try:
        _db = firestore.client()
        print("✅ Firestore initialized successfully")
        return _db
    except Exception as e:
        print(f"⚠️  Firestore initialization failed: {e}")
        return None 