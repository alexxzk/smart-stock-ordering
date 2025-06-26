#!/usr/bin/env python3
"""
Test script to verify your deployed API is working correctly.
Replace the BASE_URL with your actual deployment URL.
"""

import requests
import sys

def test_deployment(base_url):
    """Test various endpoints of the deployed API"""
    
    print(f"Testing deployment at: {base_url}")
    print("=" * 50)
    
    # Test 1: Health check
    print("\n1. Testing health check...")
    try:
        response = requests.get(f"{base_url}/health")
        if response.status_code == 200:
            print("✅ Health check passed!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Health check failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Health check error: {e}")
    
    # Test 2: Root endpoint
    print("\n2. Testing root endpoint...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Root endpoint working!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Root endpoint failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Root endpoint error: {e}")
    
    # Test 3: API documentation
    print("\n3. Testing API documentation...")
    try:
        response = requests.get(f"{base_url}/docs")
        if response.status_code == 200:
            print("✅ API documentation accessible!")
            print(f"   Visit: {base_url}/docs")
        else:
            print(f"❌ API docs failed: {response.status_code}")
    except Exception as e:
        print(f"❌ API docs error: {e}")
    
    # Test 4: Firestore connection (if Firebase is configured)
    print("\n4. Testing Firestore connection...")
    try:
        response = requests.get(f"{base_url}/test-firestore")
        if response.status_code == 200:
            print("✅ Firestore connection working!")
            print(f"   Response: {response.json()}")
        else:
            print(f"❌ Firestore test failed: {response.status_code}")
            print("   This might be due to missing Firebase credentials")
    except Exception as e:
        print(f"❌ Firestore test error: {e}")
    
    print("\n" + "=" * 50)
    print("🎉 Deployment test completed!")
    print(f"📖 API Documentation: {base_url}/docs")
    print(f"🔍 Interactive API: {base_url}/redoc")

def main():
    if len(sys.argv) != 2:
        print("Usage: python test_deployment.py <your-deployment-url>")
        print("\nExamples:")
        print("python test_deployment.py https://your-app.railway.app")
        print("python test_deployment.py https://your-app.onrender.com")
        sys.exit(1)
    
    base_url = sys.argv[1].rstrip('/')  # Remove trailing slash
    test_deployment(base_url)

if __name__ == "__main__":
    main() 