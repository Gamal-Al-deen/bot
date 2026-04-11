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


def update_user_balance(user_id: int, new_balance: float) -> bool:
    """
    Update user balance to a new amount (alias for set_balance)
    @param user_id: User ID
    @param new_balance: New balance amount
    @return: True if successful
    """
    return set_balance(user_id, new_balance)


# ============================================
# Categories & Services Functions
# ============================================

def add_category(name: str) -> bool:
    """
    Add a new category to Supabase
    @param name: Category name
    @return: True if successful
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        log_error(f"📁 [ADD_CATEGORY] Attempting to add category: {name}")
        
        # Insert category
        result = client.table('categories').insert({'name': name}).execute()
        
        if result.data:
            log_error(f"✅ [ADD_CATEGORY] Category '{name}' added successfully with ID: {result.data[0]['id']}")
            return True
        
        log_error(f"❌ [ADD_CATEGORY] Failed to add category '{name}'")
        return False
        
    except Exception as e:
        # Check if it's a duplicate error
        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
            log_error(f"⚠️ [ADD_CATEGORY] Category '{name}' already exists")
        else:
            log_error(f"❌ [ADD_CATEGORY] Error: {type(e).__name__}: {str(e)}")
            import traceback
            log_error(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False


def get_all_categories() -> List[Dict[str, Any]]:
    """
    Get all categories from Supabase
    @return: List of categories
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        result = client.table('categories').select('*').order('id', desc=False).execute()
        categories = result.data if result.data else []
        
        log_error(f"📁 [GET_CATEGORIES] Retrieved {len(categories)} categories")
        return categories
        
    except Exception as e:
        log_error(f"❌ [GET_CATEGORIES] Error: {str(e)}")
        return []


def delete_category(category_id: int) -> bool:
    """
    Delete a category from Supabase
    @param category_id: Category ID
    @return: True if successful
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        log_error(f"🗑️ [DELETE_CATEGORY] Deleting category ID: {category_id}")
        
        result = client.table('categories').delete().eq('id', category_id).execute()
        
        if result.data:
            log_error(f"✅ [DELETE_CATEGORY] Category {category_id} deleted")
            return True
        
        log_error(f"❌ [DELETE_CATEGORY] Failed to delete category {category_id}")
        return False
        
    except Exception as e:
        log_error(f"❌ [DELETE_CATEGORY] Error: {str(e)}")
        return False


def add_service(category_id: int, service_api_id: int) -> bool:
    """
    Add a new service to Supabase
    @param category_id: Category ID
    @param service_api_id: Service API ID from SMM panel
    @return: True if successful
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        log_error(f"🛠️ [ADD_SERVICE] Adding service API ID: {service_api_id} to category: {category_id}")
        
        # Insert service
        result = client.table('services').insert({
            'category_id': category_id,
            'service_api_id': service_api_id
        }).execute()
        
        if result.data:
            log_error(f"✅ [ADD_SERVICE] Service added successfully with ID: {result.data[0]['id']}")
            return True
        
        log_error(f"❌ [ADD_SERVICE] Failed to add service")
        return False
        
    except Exception as e:
        # Check if it's a duplicate error
        if 'duplicate' in str(e).lower() or 'unique' in str(e).lower():
            log_error(f"⚠️ [ADD_SERVICE] Service API ID {service_api_id} already exists in this category")
        else:
            log_error(f"❌ [ADD_SERVICE] Error: {type(e).__name__}: {str(e)}")
            import traceback
            log_error(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False


def get_services_by_category(category_id: int) -> List[Dict[str, Any]]:
    """
    Get all services for a specific category
    @param category_id: Category ID
    @return: List of services
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        result = client.table('services').select('*').eq('category_id', category_id).execute()
        services = result.data if result.data else []
        
        log_error(f"🛠️ [GET_SERVICES] Retrieved {len(services)} services for category {category_id}")
        return services
        
    except Exception as e:
        log_error(f"❌ [GET_SERVICES] Error: {str(e)}")
        return []


def delete_service(service_id: int) -> bool:
    """
    Delete a service from Supabase
    @param service_id: Service ID
    @return: True if successful
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        log_error(f"🗑️ [DELETE_SERVICE] Deleting service ID: {service_id}")
        
        result = client.table('services').delete().eq('id', service_id).execute()
        
        if result.data:
            log_error(f"✅ [DELETE_SERVICE] Service {service_id} deleted")
            return True
        
        log_error(f"❌ [DELETE_SERVICE] Failed to delete service {service_id}")
        return False
        
    except Exception as e:
        log_error(f"❌ [DELETE_SERVICE] Error: {str(e)}")
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


def get_all_users() -> List[Dict[str, Any]]:
    """
    Get all users (simple list)
    @return: List of user dictionaries
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        result = client.table('users').select(
            'user_id, username, first_name, balance, created_at'
        ).order(
            'created_at', desc=True
        ).execute()
        
        users = result.data if result.data else []
        log_error(f"👥 [GET_ALL_USERS] Retrieved {len(users)} users")
        return users
        
    except Exception as e:
        log_error(f"❌ [GET_ALL_USERS] Error: {str(e)}")
        return []


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


def get_all_users_paginated(page: int = 1, per_page: int = 20) -> Dict[str, Any]:
    """
    Get all users with pagination
    @param page: Page number (starts from 1)
    @param per_page: Number of users per page
    @return: Dict with users list, total count, and pagination info
    """
    try:
        client = get_supabase_client()
        if not client:
            return {'users': [], 'total': 0, 'page': page, 'per_page': per_page, 'total_pages': 0}
        
        log_error(f"👥 [GET_USERS] Fetching page {page} with {per_page} users per page")
        
        # Get total count
        count_result = client.table('users').select('user_id', count='exact').execute()
        total_users = count_result.count if count_result.count is not None else 0
        
        # Calculate pagination
        total_pages = (total_users + per_page - 1) // per_page  # Ceiling division
        offset = (page - 1) * per_page
        
        # Validate page number
        if page < 1:
            page = 1
        elif page > total_pages and total_pages > 0:
            page = total_pages
        
        # Fetch users with pagination
        result = client.table('users').select(
            'user_id, username, first_name, balance, created_at'
        ).order(
            'created_at', desc=True
        ).range(
            offset, offset + per_page - 1
        ).execute()
        
        users = result.data if result.data else []
        
        log_error(f"✅ [GET_USERS] Retrieved {len(users)} users (Page {page}/{total_pages}, Total: {total_users})")
        
        return {
            'users': users,
            'total': total_users,
            'page': page,
            'per_page': per_page,
            'total_pages': total_pages,
            'has_next': page < total_pages,
            'has_prev': page > 1
        }
        
    except Exception as e:
        log_error(f"❌ [GET_USERS] Error: {type(e).__name__}: {str(e)}")
        import traceback
        log_error(f"📋 [GET_USERS] Full traceback:\n{traceback.format_exc()}")
        return {
            'users': [],
            'total': 0,
            'page': page,
            'per_page': per_page,
            'total_pages': 0,
            'has_next': False,
            'has_prev': False
        }


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
