#!/usr/bin/env python3
"""
Quick Fix Script for Backend Issues
Run this to fix import errors and get the backend running
"""

import os
import sys
import subprocess
import time

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        print(f"Error output: {e.stderr}")
        return False

def check_port_in_use(port):
    """Check if a port is in use"""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            return s.connect_ex(('localhost', port)) == 0
    except:
        return False

def kill_process_on_port(port):
    """Kill process using a specific port"""
    try:
        result = subprocess.run(f"lsof -ti:{port}", shell=True, capture_output=True, text=True)
        if result.stdout.strip():
            pid = result.stdout.strip()
            subprocess.run(f"kill -9 {pid}", shell=True)
            print(f"✅ Killed process {pid} on port {port}")
            time.sleep(1)
    except:
        pass

def main():
    print("🔧 Quick Fix for Backend Issues")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("app"):
        print("❌ Please run this script from the backend directory")
        sys.exit(1)
    
    # Kill any existing processes on port 8000
    if check_port_in_use(8000):
        print("🔍 Port 8000 is in use, killing existing process...")
        kill_process_on_port(8000)
    
    # Install dependencies
    print("\n📦 Installing dependencies...")
    run_command("pip install aiohttp==3.9.1", "Installing aiohttp")
    
    # Test the import
    print("\n🧪 Testing imports...")
    test_import = """
import sys
import os
sys.path.append(os.getcwd())

try:
    from app.main import app
    print("✅ Import successful!")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)
"""
    
    with open("test_import.py", "w") as f:
        f.write(test_import)
    
    if run_command("python test_import.py", "Testing imports"):
        print("✅ All imports working correctly")
    else:
        print("❌ Import test failed")
        sys.exit(1)
    
    # Clean up test file
    if os.path.exists("test_import.py"):
        os.remove("test_import.py")
    
    # Start the backend
    print("\n🚀 Starting backend...")
    print("Starting uvicorn server...")
    print("Press Ctrl+C to stop")
    
    try:
        subprocess.run([
            "uvicorn", "app.main:app", 
            "--host", "0.0.0.0", 
            "--port", "8000", 
            "--reload"
        ], check=True)
    except KeyboardInterrupt:
        print("\n⏹️  Backend stopped by user")
    except Exception as e:
        print(f"\n❌ Failed to start backend: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 