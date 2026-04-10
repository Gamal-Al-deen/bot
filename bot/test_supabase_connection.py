# -*- coding: utf-8 -*-
"""
اختبار اتصال Supabase - تشخيص شامل
Supabase Connection Test - Comprehensive Diagnosis

Run this script to diagnose Supabase connection issues:
python test_supabase_connection.py
"""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from functions import log_error

def main():
    print("=" * 80)
    print("🔍 SUPABASE CONNECTION DIAGNOSTIC TOOL")
    print("=" * 80)
    
    # Test 1: Check if supabase library is installed
    print("\n1️⃣ Checking if supabase library is installed...")
    try:
        from supabase import create_client
        print("   ✅ supabase library is installed")
    except ImportError as e:
        print(f"   ❌ supabase library NOT installed!")
        print(f"   💡 FIX: Run 'pip install supabase'")
        return
    
    # Test 2: Load configuration
    print("\n2️⃣ Loading configuration from config.py...")
    try:
        from config import SUPABASE_URL, SUPABASE_KEY
        print(f"   ✅ Configuration loaded")
        print(f"   📋 SUPABASE_URL: {SUPABASE_URL}")
        print(f"   🔑 SUPABASE_KEY starts with: {SUPABASE_KEY[:20]}...")
        
        # Check if using wrong key type
        if SUPABASE_KEY.startswith("sb_publishable_"):
            print(f"\n   ⚠️  WARNING: You're using a PUBLISHABLE KEY!")
            print(f"   ❌ This key type CANNOT bypass RLS policies!")
            print(f"   💡 FIX: Use the service_role key instead")
            print(f"   💡 Find it in: Supabase Dashboard > Settings > API > service_role")
            print(f"   💡 The service_role key starts with 'eyJ...'")
        elif SUPABASE_URL == "YOUR_SUPABASE_URL":
            print(f"\n   ❌ ERROR: SUPABASE_URL is not configured!")
            print(f"   💡 FIX: Update config.py with your actual Supabase URL")
        elif SUPABASE_KEY == "YOUR_SUPABASE_KEY":
            print(f"\n   ❌ ERROR: SUPABASE_KEY is not configured!")
            print(f"   💡 FIX: Update config.py with your service_role key")
        else:
            print(f"   ✅ Configuration looks valid")
            
    except Exception as e:
        print(f"   ❌ Failed to load config: {str(e)}")
        return
    
    # Test 3: Initialize database
    print("\n3️⃣ Initializing database connection...")
    try:
        from database import init_db, test_database_connection
        
        success = init_db()
        
        if success:
            print("   ✅ Database initialized successfully!")
            
            # Run comprehensive tests
            print("\n4️⃣ Running comprehensive database tests...")
            test_success = test_database_connection()
            
            if test_success:
                print("\n" + "=" * 80)
                print("🎉 ALL TESTS PASSED - SUPABASE IS WORKING CORRECTLY!")
                print("=" * 80)
                print("\n💡 Your bot should now be able to:")
                print("   ✅ Create users")
                print("   ✅ Add categories")
                print("   ✅ Add services")
                print("   ✅ Save orders")
                print("\n🚀 You can now run your bot: python run.py")
            else:
                print("\n" + "=" * 80)
                print("⚠️  SOME TESTS FAILED - CHECK log.txt FOR DETAILS")
                print("=" * 80)
        else:
            print("   ❌ Database initialization failed!")
            print("   📋 Check log.txt for detailed error messages")
            
    except Exception as e:
        print(f"   ❌ Error during initialization: {str(e)}")
        import traceback
        traceback.print_exc()
    
    print("\n" + "=" * 80)
    print("📋 Diagnostic complete! Check log.txt for full details")
    print("=" * 80)

if __name__ == "__main__":
    main()
