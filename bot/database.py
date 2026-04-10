# -*- coding: utf-8 -*-
"""
طبقة قاعدة البيانات - Supabase
Database Layer - Supabase Integration with Full Debugging

Contains all CRUD operations with comprehensive logging
"""

try:
    from supabase import create_client, Client
    HAS_SUPABASE = True
except ImportError:
    HAS_SUPABASE = False
    print("⚠️ WARNING: supabase library not installed!")
    print("Run: pip install supabase")

from config import SUPABASE_URL, SUPABASE_KEY
from functions import log_error
from typing import Optional, Dict, List, Any


# Global Supabase client instance
supabase_client: Optional[Client] = None


def init_db() -> bool:
    """
    Initialize Supabase connection with comprehensive debugging
    """
    global supabase_client
    
    try:
        log_error("=" * 60)
        log_error("🗄️ DATABASE INITIALIZATION STARTED")
        log_error("=" * 60)
        
        # Check if supabase library is installed
        if not HAS_SUPABASE:
            log_error("❌ CRITICAL: supabase library is NOT installed!")
            log_error("💡 Run: pip install supabase")
            return False
        
        # Log configuration (hide sensitive parts)
        masked_key = SUPABASE_KEY[:20] + "..." if len(SUPABASE_KEY) > 20 else SUPABASE_KEY
        log_error(f"📋 SUPABASE_URL: {SUPABASE_URL}")
        log_error(f"🔑 SUPABASE_KEY: {masked_key}")
        log_error(f"🔑 Key starts with: {SUPABASE_KEY[:15]}")
        
        # Validate configuration
        if SUPABASE_URL == "YOUR_SUPABASE_URL" or not SUPABASE_URL.startswith("http"):
            log_error("❌ CRITICAL: SUPABASE_URL is not configured correctly!")
            log_error("💡 Update config.py with your actual Supabase URL")
            return False
        
        if SUPABASE_KEY == "YOUR_SUPABASE_KEY" or SUPABASE_KEY.startswith("sb_publishable_"):
            log_error("❌ CRITICAL: SUPABASE_KEY is incorrect!")
            log_error("⚠️ You're using a publishable/anon key!")
            log_error("💡 You MUST use the service_role key (secret)")
            log_error("💡 Find it in: Supabase Dashboard > Settings > API > service_role")
            return False
        
        # Create Supabase client
        log_error("🔌 Creating Supabase client...")
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        log_error("✅ Supabase client created successfully")
        
        # Test connection with a simple query
        log_error("🧪 Testing database connection...")
        try:
            test_query = supabase_client.table('settings').select('key').limit(1).execute()
            log_error(f"📊 Test query response: {test_query}")
            log_error(f"📊 Data returned: {test_query.data}")
            log_error(f"📊 Has error attribute: {hasattr(test_query, 'error')}")
            
            if hasattr(test_query, 'error') and test_query.error:
                log_error(f"❌ Database query error: {test_query.error}")
                return False
            
            log_error("✅ Database connection test PASSED!")
            log_error("=" * 60)
            log_error("🎉 DATABASE INITIALIZATION COMPLETED SUCCESSFULLY")
            log_error("=" * 60)
            return True
            
        except Exception as query_error:
            log_error(f"❌ Database query failed: {type(query_error).__name__}")
            log_error(f"❌ Error details: {str(query_error)}")
            
            # Check if it's an RLS issue
            if "row-level security" in str(query_error).lower() or "RLS" in str(query_error).upper():
                log_error("⚠️ This appears to be an RLS (Row Level Security) issue")
                log_error("💡 Make sure you're using service_role key, not anon key")
            
            return False
            
    except Exception as e:
        log_error(f"❌ CRITICAL ERROR in init_db: {type(e).__name__}")
        log_error(f"❌ Error message: {str(e)}")
        import traceback
        log_error(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False


def get_supabase_client() -> Optional[Client]:
    """
    Get Supabase client instance
    """
    if supabase_client is None:
        log_error("⚠️ Supabase client not initialized, attempting to initialize...")
        if not init_db():
            return None
    return supabase_client


# =====================================================
# USERS MANAGEMENT - WITH FULL DEBUGGING
# =====================================================

def create_user(user_id: int, username: str = "لا يوجد", first_name: str = "مستخدم") -> bool:
    """
    Register a new user with comprehensive logging
    """
    try:
        log_error(f"👤 [CREATE_USER] Attempting to create/update user: {user_id}")
        log_error(f"👤 [CREATE_USER] Username: {username}, First Name: {first_name}")
        
        client = get_supabase_client()
        if not client:
            log_error("❌ [CREATE_USER] Supabase client is None!")
            return False
        
        # Check if user exists first
        log_error(f"🔍 [CREATE_USER] Checking if user {user_id} exists...")
        existing = client.table('users').select('user_id').eq('user_id', user_id).execute()
        
        log_error(f"📊 [CREATE_USER] Existing user query result: {existing}")
        log_error(f"📊 [CREATE_USER] Data: {existing.data}")
        
        if existing.data and len(existing.data) > 0:
            log_error(f"ℹ️ [CREATE_USER] User {user_id} already exists - updating info")
            # Update user info
            update_result = client.table('users').update({
                'username': username,
                'first_name': first_name
            }).eq('user_id', user_id).execute()
            
            log_error(f"📊 [CREATE_USER] Update result: {update_result}")
            log_error(f"✅ [CREATE_USER] User info updated successfully")
            return False  # Not a new user
        
        # Create new user
        log_error(f"➕ [CREATE_USER] Inserting new user {user_id}...")
        user_data = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'balance': 0.0
        }
        log_error(f"📦 [CREATE_USER] Data to insert: {user_data}")
        
        insert_result = client.table('users').insert(user_data).execute()
        
        log_error(f"📊 [CREATE_USER] Insert result: {insert_result}")
        log_error(f"📊 [CREATE_USER] Insert data: {insert_result.data}")
        
        # Check for errors
        if hasattr(insert_result, 'error') and insert_result.error:
            log_error(f"❌ [CREATE_USER] Insert error: {insert_result.error}")
            return False
        
        if insert_result.data:
            log_error(f"✅ [CREATE_USER] User {user_id} created successfully!")
            log_error(f"✅ [CREATE_USER] Database returned: {insert_result.data[0]}")
            return True
        else:
            log_error(f"❌ [CREATE_USER] No data returned from insert")
            return False
        
    except Exception as e:
        log_error(f"❌ [CREATE_USER] EXCEPTION: {type(e).__name__}")
        log_error(f"❌ [CREATE_USER] Error message: {str(e)}")
        import traceback
        log_error(f"📋 [CREATE_USER] Full traceback:\n{traceback.format_exc()}")
        return False


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user data with logging
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        result = client.table('users').select('*').eq('user_id', user_id).execute()
        
        if result.data and len(result.data) > 0:
            log_error(f"✅ [GET_USER] User {user_id} found")
            return result.data[0]
        
        log_error(f"⚠️ [GET_USER] User {user_id} not found")
        return None
        
    except Exception as e:
        log_error(f"❌ [GET_USER] Error: {type(e).__name__}: {str(e)}")
        return None


def get_balance(user_id: int) -> float:
    """
    Get user balance
    """
    try:
        user = get_user(user_id)
        if user:
            balance = float(user.get('balance', 0.0))
            log_error(f"💰 [GET_BALANCE] User {user_id}: {balance}")
            return balance
        return 0.0
        
    except Exception as e:
        log_error(f"❌ [GET_BALANCE] Error: {str(e)}")
        return 0.0


def add_balance(user_id: int, amount: float) -> bool:
    """
    Add balance with logging
    """
    try:
        log_error(f"💰 [ADD_BALANCE] Adding {amount} to user {user_id}")
        
        client = get_supabase_client()
        if not client:
            return False
        
        amount = float(amount)
        current_balance = get_balance(user_id)
        new_balance = current_balance + amount
        
        log_error(f"💰 [ADD_BALANCE] Current: {current_balance}, New: {new_balance}")
        
        result = client.table('users').update({
            'balance': new_balance
        }).eq('user_id', user_id).execute()
        
        if result.data:
            log_error(f"✅ [ADD_BALANCE] Success! New balance: {new_balance}")
            return True
        
        log_error(f"❌ [ADD_BALANCE] Failed - no data returned")
        return False
        
    except Exception as e:
        log_error(f"❌ [ADD_BALANCE] Error: {str(e)}")
        return False


def deduct_balance(user_id: int, amount: float) -> bool:
    """
    Deduct balance with logging
    """
    try:
        log_error(f"💸 [DEDUCT_BALANCE] Deducting {amount} from user {user_id}")
        
        client = get_supabase_client()
        if not client:
            return False
        
        amount = float(amount)
        current_balance = get_balance(user_id)
        
        if current_balance < amount:
            log_error(f"❌ [DEDUCT_BALANCE] Insufficient balance: {current_balance} < {amount}")
            return False
        
        new_balance = current_balance - amount
        
        result = client.table('users').update({
            'balance': new_balance
        }).eq('user_id', user_id).execute()
        
        if result.data:
            log_error(f"✅ [DEDUCT_BALANCE] Success! New balance: {new_balance}")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ [DEDUCT_BALANCE] Error: {str(e)}")
        return False


def set_balance(user_id: int, amount: float) -> bool:
    """
    Set exact balance
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        result = client.table('users').update({
            'balance': float(amount)
        }).eq('user_id', user_id).execute()
        
        return bool(result.data)
        
    except Exception as e:
        log_error(f"❌ [SET_BALANCE] Error: {str(e)}")
        return False


def get_all_users_count() -> int:
    """
    Get total users count
    """
    try:
        client = get_supabase_client()
        if not client:
            return 0
        
        result = client.table('users').select('user_id', count='exact').execute()
        count = result.count if result.count is not None else 0
        log_error(f"👥 [USERS_COUNT] Total users: {count}")
        return count
        
    except Exception as e:
        log_error(f"❌ [USERS_COUNT] Error: {str(e)}")
        return 0


def get_all_user_ids() -> List[int]:
    """
    Get all user IDs
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        result = client.table('users').select('user_id').execute()
        user_ids = [user['user_id'] for user in result.data] if result.data else []
        log_error(f"👥 [USER_IDS] Retrieved {len(user_ids)} user IDs")
        return user_ids
        
    except Exception as e:
        log_error(f"❌ [USER_IDS] Error: {str(e)}")
        return []


def user_exists(user_id: int) -> bool:
    """
    Check if user exists
    """
    try:
        user = get_user(user_id)
        exists = user is not None
        log_error(f"🔍 [USER_EXISTS] User {user_id}: {exists}")
        return exists
        
    except Exception as e:
        log_error(f"❌ [USER_EXISTS] Error: {str(e)}")
        return False


# =====================================================
# TEST FUNCTION - Run this to verify connection
# =====================================================

def test_database_connection():
    """
    Comprehensive database test
    """
    try:
        log_error("=" * 60)
        log_error("🧪 RUNNING COMPREHENSIVE DATABASE TEST")
        log_error("=" * 60)
        
        client = get_supabase_client()
        if not client:
            log_error("❌ TEST FAILED: Cannot get Supabase client")
            return False
        
        # Test 1: SELECT from settings
        log_error("\n📝 Test 1: SELECT from settings table")
        try:
            result = client.table('settings').select('*').execute()
            log_error(f"✅ Settings query successful: {len(result.data) if result.data else 0} rows")
        except Exception as e:
            log_error(f"❌ Settings query failed: {str(e)}")
            return False
        
        # Test 2: SELECT from users
        log_error("\n📝 Test 2: SELECT from users table")
        try:
            result = client.table('users').select('*').limit(5).execute()
            log_error(f"✅ Users query successful: {len(result.data) if result.data else 0} rows")
        except Exception as e:
            log_error(f"❌ Users query failed: {str(e)}")
            return False
        
        # Test 3: INSERT test user
        log_error("\n📝 Test 3: INSERT test user")
        try:
            test_user_id = 999999999
            result = client.table('users').insert({
                'user_id': test_user_id,
                'username': 'test_user',
                'first_name': 'Test',
                'balance': 0.0
            }).execute()
            
            if result.data:
                log_error(f"✅ Test user inserted successfully!")
                # Clean up
                client.table('users').delete().eq('user_id', test_user_id).execute()
                log_error(f"🧹 Test user cleaned up")
            else:
                log_error(f"❌ Test user insert failed")
                return False
        except Exception as e:
            log_error(f"❌ Test user insert failed: {str(e)}")
            return False
        
        log_error("\n" + "=" * 60)
        log_error("🎉 ALL TESTS PASSED!")
        log_error("=" * 60)
        return True
        
    except Exception as e:
        log_error(f"❌ TEST FAILED: {str(e)}")
        return False
