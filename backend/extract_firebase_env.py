#!/usr/bin/env python3
"""
Helper script to extract Firebase environment variables from service account JSON file.
Run this script with your Firebase service account JSON file to get the environment variables.
"""

import json
import sys
import os

def extract_firebase_env(json_file_path):
    """Extract Firebase environment variables from JSON file"""
    try:
        with open(json_file_path, 'r') as f:
            data = json.load(f)
        
        # Handle private key properly
        private_key = data.get("private_key", "").replace("\n", "\\n")
        
        env_vars = {
            'FIREBASE_PROJECT_ID': data.get('project_id', ''),
            'FIREBASE_PRIVATE_KEY_ID': data.get('private_key_id', ''),
            'FIREBASE_PRIVATE_KEY': f'"{private_key}"',
            'FIREBASE_CLIENT_EMAIL': data.get('client_email', ''),
            'FIREBASE_CLIENT_ID': data.get('client_id', ''),
            'FIREBASE_AUTH_URI': data.get('auth_uri', ''),
            'FIREBASE_TOKEN_URI': data.get('token_uri', ''),
            'FIREBASE_AUTH_PROVIDER_X509_CERT_URL': data.get('auth_provider_x509_cert_url', ''),
            'FIREBASE_CLIENT_X509_CERT_URL': data.get('client_x509_cert_url', ''),
            'DEV_MODE': 'false'
        }
        
        print("=== Firebase Environment Variables ===\n")
        for key, value in env_vars.items():
            print(f"{key}={value}")
        
        print("\n=== For Railway/Render ===\n")
        print("Copy these variables to your deployment platform's environment variables section:")
        for key, value in env_vars.items():
            print(f"{key}: {value}")
            
        return env_vars
        
    except FileNotFoundError:
        print(f"Error: File '{json_file_path}' not found.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON file '{json_file_path}'.")
        return None
    except Exception as e:
        print(f"Error: {str(e)}")
        return None

def main():
    if len(sys.argv) != 2:
        print("Usage: python extract_firebase_env.py <path-to-firebase-service-account.json>")
        print("\nExample:")
        print("python extract_firebase_env.py ./firebase-service-account.json")
        sys.exit(1)
    
    json_file_path = sys.argv[1]
    extract_firebase_env(json_file_path)

if __name__ == "__main__":
    main() 