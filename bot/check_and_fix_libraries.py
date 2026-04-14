# -*- coding: utf-8 -*-
"""
سكربت فحص وإصلاح مشاكل المكتبات
Library Check & Fix Script

Run this script to diagnose and fix library issues:
python check_and_fix_libraries.py
"""

import sys
import subprocess
import os

def print_header(text):
    print("\n" + "=" * 80)
    print(f"  {text}")
    print("=" * 80)

def check_python_version():
    """Check Python version"""
    print_header("1️⃣ Python Version Check")
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    
    if version.major == 3 and version.minor >= 8:
        print("✅ Python version is compatible")
        return True
    else:
        print("❌ Python version too old, need 3.8+")
        return False

def check_supabase_installed():
    """Check if supabase is installed and its version"""
    print_header("2️⃣ Supabase Library Check")
    
    try:
        import supabase
        version = supabase.__version__ if hasattr(supabase, '__version__') else "unknown"
        print(f"✅ supabase is installed (version: {version})")
        
        # Check if version is old
        if version.startswith("2.3") or version.startswith("2.2") or version.startswith("2.1"):
            print(f"⚠️  WARNING: Version {version} is outdated!")
            print(f"💡 RECOMMENDED: Upgrade to >= 2.10.0")
            return "outdated"
        return True
        
    except ImportError:
        print("❌ supabase is NOT installed!")
        return False
    except Exception as e:
        print(f"❌ Error checking supabase: {e}")
        return False

def install_supabase():
    """Install or upgrade supabase"""
    print_header("3️⃣ Installing/Upgrading Supabase")
    
    print("📦 Installing supabase>=2.10.0...")
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "supabase>=2.10.0"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print("✅ supabase installed successfully!")
            print(result.stdout[-500:] if len(result.stdout) > 500 else result.stdout)
            return True
        else:
            print("❌ Installation failed!")
            print("STDOUT:", result.stdout[-500:])
            print("STDERR:", result.stderr[-500:])
            return False
            
    except subprocess.TimeoutExpired:
        print("❌ Installation timed out (120s)")
        return False
    except Exception as e:
        print(f"❌ Error during installation: {e}")
        return False

def test_supabase_connection():
    """Test if supabase works after installation"""
    print_header("4️⃣ Testing Supabase Client")
    
    try:
        from config import SUPABASE_URL, SUPABASE_KEY
        from supabase import create_client
        
        print(f"📋 URL: {SUPABASE_URL}")
        print(f"🔑 Key: {SUPABASE_KEY[:20]}...")
        
        print("\n🔌 Creating client...")
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        print("✅ Client created successfully!")
        
        print("\n🧪 Testing simple query...")
        result = client.table("settings").select("*").limit(1).execute()
        print(f"✅ Query successful! Rows: {len(result.data) if result.data else 0}")
        
        return True
        
    except Exception as e:
        print(f"❌ Test failed: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n🔍 Supabase Library Diagnostic Tool")
    print("=" * 80)
    
    # Step 1: Check Python
    if not check_python_version():
        print("\n❌ Please upgrade Python first!")
        return
    
    # Step 2: Check supabase
    status = check_supabase_installed()
    
    if status == "outdated":
        print("\n⚠️  Supabase is outdated. Upgrading...")
        if install_supabase():
            print("\n✅ Upgrade complete! Testing...")
            if test_supabase_connection():
                print("\n🎉 All tests passed! Your bot should work now.")
            else:
                print("\n❌ Tests failed after upgrade. Please check errors above.")
        else:
            print("\n❌ Upgrade failed. Please check network connection and try again.")
            
    elif status is False:
        print("\n❌ Supabase is not installed. Installing...")
        if install_supabase():
            print("\n✅ Installation complete! Testing...")
            if test_supabase_connection():
                print("\n🎉 All tests passed! Your bot should work now.")
            else:
                print("\n❌ Tests failed after installation. Please check errors above.")
        else:
            print("\n❌ Installation failed. Please check network connection and try again.")
            
    else:
        print("\n✅ Supabase is already installed and up to date!")
        print("\n🧪 Running connection test...")
        if test_supabase_connection():
            print("\n🎉 All tests passed! Your bot should work perfectly.")
        else:
            print("\n❌ Connection test failed. Please check errors above.")
    
    print("\n" + "=" * 80)
    print("Diagnostic complete!")
    print("=" * 80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Stopped by user")
    except Exception as e:
        print(f"\n\n❌ Fatal error: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
