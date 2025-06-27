#!/usr/bin/env python3
"""
Setup script for performance testing
"""

import subprocess
import sys

def install_dependency():
    """Install aiohttp for performance testing"""
    try:
        print("📦 Installing aiohttp for performance testing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "aiohttp"])
        print("✅ aiohttp installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install aiohttp: {e}")
        return False

def main():
    """Main setup function"""
    print("🚀 PERFORMANCE TEST SETUP")
    print("=" * 40)
    
    if install_dependency():
        print("\n✅ Setup completed!")
        print("\nTo run performance test:")
        print("  python test_performance.py")
    else:
        print("\n❌ Setup failed!")

if __name__ == "__main__":
    main() 