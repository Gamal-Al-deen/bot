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
        
        # Test connection (settings أولاً، ثم users إن فشل الأول)
        log_error("🧪 Testing database connection...")
        last_err = None
        for probe_table in ('settings', 'users'):
            try:
                test_query = supabase_client.table(probe_table).select('*').limit(1).execute()
                log_error(f"📊 Test query on '{probe_table}': rows={len(test_query.data) if test_query.data else 0}")
                if hasattr(test_query, 'error') and test_query.error:
                    log_error(f"❌ Database query error: {test_query.error}")
                    return False
                log_error(f"✅ Database connection test PASSED (via '{probe_table}')")
                log_error("=" * 60)
                log_error("🎉 DATABASE INITIALIZATION COMPLETED SUCCESSFULLY")
                log_error("=" * 60)
                return True
            except Exception as probe_exc:
                last_err = probe_exc
                log_error(f"⚠️ Probe on '{probe_table}' failed: {type(probe_exc).__name__}: {str(probe_exc)[:200]}")
                continue
        log_error(f"❌ Database query failed on all probe tables. Last error: {last_err}")
        if last_err and ("row-level security" in str(last_err).lower() or "RLS" in str(last_err).upper()):
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
# SETTINGS (جدول settings — تخزين دائم في Supabase)
# =====================================================

def get_setting(key: str, default: str = "") -> str:
    """قراءة قيمة من جدول settings."""
    try:
        client = get_supabase_client()
        if not client:
            log_error(f"❌ [SETTINGS] get_setting: no client for key={key!r}")
            return default
        result = client.table("settings").select("value").eq("key", key).limit(1).execute()
        if result.data and len(result.data) > 0:
            return str(result.data[0].get("value", default))
        return default
    except Exception as e:
        log_error(f"❌ [SETTINGS] get_setting({key!r}): {type(e).__name__}: {str(e)}")
        return default


def set_setting(key: str, value: str) -> bool:
    """كتابة أو تحديث قيمة في جدول settings."""
    try:
        client = get_supabase_client()
        if not client:
            log_error(f"❌ [SETTINGS] set_setting: no client for key={key!r}")
            return False
        existing = client.table("settings").select("key").eq("key", key).limit(1).execute()
        val = str(value)
        if existing.data:
            client.table("settings").update({"value": val}).eq("key", key).execute()
        else:
            client.table("settings").insert({"key": key, "value": val}).execute()
        log_error(f"✅ [SETTINGS] set key={key!r}")
        return True
    except Exception as e:
        log_error(f"❌ [SETTINGS] set_setting({key!r}): {type(e).__name__}: {str(e)}")
        return False


def delete_setting(key: str) -> bool:
    """حذف مفتاح من جدول settings."""
    try:
        client = get_supabase_client()
        if not client:
            log_error(f"❌ [SETTINGS] delete_setting: no client for key={key!r}")
            return False
        client.table("settings").delete().eq("key", key).execute()
        log_error(f"✅ [SETTINGS] deleted key={key!r}")
        return True
    except Exception as e:
        log_error(f"❌ [SETTINGS] delete_setting({key!r}): {type(e).__name__}: {str(e)}")
        return False


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
        
        # Create new user (مع .select() لضمان إرجاع الصف حتى لو كان الاستجابة minimal)
        log_error(f"➕ [CREATE_USER] Inserting new user {user_id}...")
        user_data = {
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'balance': 0.0
        }
        log_error(f"📦 [CREATE_USER] Data to insert: {user_data}")
        
        insert_result = client.table('users').insert(user_data).select('user_id').execute()
        
        log_error(f"📊 [CREATE_USER] Insert result data: {insert_result.data}")
        
        if hasattr(insert_result, 'error') and insert_result.error:
            log_error(f"❌ [CREATE_USER] Insert error: {insert_result.error}")
            return False
        
        if insert_result.data:
            log_error(f"✅ [CREATE_USER] User {user_id} created successfully!")
            return True
        
        verify = client.table('users').select('user_id').eq('user_id', user_id).limit(1).execute()
        if verify.data:
            log_error(f"✅ [CREATE_USER] User {user_id} present after insert (verified by SELECT)")
            return True
        
        log_error(f"❌ [CREATE_USER] Insert did not persist user {user_id}")
        return False
        
    except Exception as e:
        err = str(e).lower()
        if 'duplicate' in err or 'unique' in err or 'already exists' in err:
            log_error(f"ℹ️ [CREATE_USER] Race or duplicate for {user_id}, falling back to update")
            try:
                client = get_supabase_client()
                if client:
                    client.table('users').update({
                        'username': username,
                        'first_name': first_name
                    }).eq('user_id', user_id).execute()
                return False
            except Exception as inner:
                log_error(f"❌ [CREATE_USER] Fallback update failed: {inner}")
                return False
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
# CATEGORIES & BOT SERVICES (عرض الخدمات في البوت — Supabase فقط)
# =====================================================

def _normalize_api_service_id(service_id) -> int:
    return int(service_id)


def _get_category_id(client, category_name: str) -> Optional[int]:
    r = client.table("categories").select("id").eq("name", category_name).limit(1).execute()
    if r.data:
        return int(r.data[0]["id"])
    return None


def list_category_names() -> List[str]:
    try:
        client = get_supabase_client()
        if not client:
            log_error("❌ [CATEGORIES] list_category_names: no client")
            return []
        r = client.table("categories").select("name").order("id").execute()
        if not r.data:
            return []
        return [row["name"] for row in r.data]
    except Exception as e:
        log_error(f"❌ [CATEGORIES] list_category_names: {type(e).__name__}: {str(e)}")
        return []


def insert_category(name: str) -> bool:
    try:
        client = get_supabase_client()
        if not client:
            return False
        if _get_category_id(client, name) is not None:
            log_error(f"⚠️ [CATEGORIES] insert_category: '{name}' already exists")
            return False
        client.table("categories").insert({"name": name}).execute()
        log_error(f"✅ [CATEGORIES] inserted '{name}'")
        return True
    except Exception as e:
        log_error(f"❌ [CATEGORIES] insert_category: {type(e).__name__}: {str(e)}")
        return False


def delete_category_by_name(name: str) -> bool:
    try:
        client = get_supabase_client()
        if not client:
            return False
        cid = _get_category_id(client, name)
        if cid is None:
            log_error(f"⚠️ [CATEGORIES] delete: '{name}' not found")
            return False
        client.table("categories").delete().eq("id", cid).execute()
        log_error(f"✅ [CATEGORIES] deleted '{name}' (id={cid})")
        return True
    except Exception as e:
        log_error(f"❌ [CATEGORIES] delete_category_by_name: {type(e).__name__}: {str(e)}")
        return False


def insert_service_in_category(category_name: str, service_id, service_name: str) -> bool:
    try:
        client = get_supabase_client()
        if not client:
            return False
        cid = _get_category_id(client, category_name)
        if cid is None:
            log_error(f"⚠️ [SERVICES] insert: category '{category_name}' not found")
            return False
        api_id = _normalize_api_service_id(service_id)
        dup = (
            client.table("services")
            .select("id")
            .eq("category_id", cid)
            .eq("service_api_id", api_id)
            .limit(1)
            .execute()
        )
        if dup.data:
            log_error(f"⚠️ [SERVICES] service_api_id={api_id} already in '{category_name}'")
            return False
        row = {
            "category_id": cid,
            "service_api_id": api_id,
            "service_name": service_name or "",
        }
        client.table("services").insert(row).execute()
        log_error(f"✅ [SERVICES] added api_id={api_id} to '{category_name}'")
        return True
    except Exception as e:
        log_error(f"❌ [SERVICES] insert_service_in_category: {type(e).__name__}: {str(e)}")
        return False


def delete_service_in_category(category_name: str, service_id) -> bool:
    try:
        client = get_supabase_client()
        if not client:
            return False
        cid = _get_category_id(client, category_name)
        if cid is None:
            log_error(f"⚠️ [SERVICES] delete: category '{category_name}' not found")
            return False
        api_id = _normalize_api_service_id(service_id)
        before = (
            client.table("services")
            .select("id")
            .eq("category_id", cid)
            .eq("service_api_id", api_id)
            .limit(1)
            .execute()
        )
        if not before.data:
            log_error(f"⚠️ [SERVICES] delete: api_id={api_id} not in '{category_name}'")
            return False
        client.table("services").delete().eq("category_id", cid).eq("service_api_id", api_id).execute()
        log_error(f"✅ [SERVICES] removed api_id={api_id} from '{category_name}'")
        return True
    except Exception as e:
        log_error(f"❌ [SERVICES] delete_service_in_category: {type(e).__name__}: {str(e)}")
        return False


def select_services_for_category(category_name: str) -> List[Dict[str, Any]]:
    """قائمة خدمات القسم بصيغة متوافقة مع bot: service_id, service_name."""
    try:
        client = get_supabase_client()
        if not client:
            return []
        cid = _get_category_id(client, category_name)
        if cid is None:
            return []
        r = (
            client.table("services")
            .select("service_api_id, service_name")
            .eq("category_id", cid)
            .order("id")
            .execute()
        )
        out = []
        for row in r.data or []:
            out.append(
                {
                    "service_id": row.get("service_api_id"),
                    "service_name": row.get("service_name") or "خدمة",
                }
            )
        return out
    except Exception as e:
        log_error(f"❌ [SERVICES] select_services_for_category: {type(e).__name__}: {str(e)}")
        return []


def select_all_services_flat() -> List[Dict[str, Any]]:
    try:
        client = get_supabase_client()
        if not client:
            return []
        r = (
            client.table("services")
            .select("service_api_id, service_name, category_id")
            .order("id")
            .execute()
        )
        if not r.data:
            return []
        cat_map: Dict[int, str] = {}
        cr = client.table("categories").select("id, name").execute()
        for c in cr.data or []:
            cat_map[int(c["id"])] = c["name"]
        flat = []
        for row in r.data:
            cid = int(row["category_id"])
            flat.append(
                {
                    "category": cat_map.get(cid, "?"),
                    "service_id": row.get("service_api_id"),
                    "service_name": row.get("service_name") or "خدمة",
                }
            )
        return flat
    except Exception as e:
        log_error(f"❌ [SERVICES] select_all_services_flat: {type(e).__name__}: {str(e)}")
        return []


def lookup_service_by_api_id(service_id) -> Optional[Dict[str, Any]]:
    try:
        client = get_supabase_client()
        if not client:
            return None
        api_id = _normalize_api_service_id(service_id)
        r = (
            client.table("services")
            .select("service_api_id, service_name, category_id")
            .eq("service_api_id", api_id)
            .limit(1)
            .execute()
        )
        if not r.data:
            return None
        row = r.data[0]
        cid = int(row["category_id"])
        cn = client.table("categories").select("name").eq("id", cid).limit(1).execute()
        cat_name = cn.data[0]["name"] if cn.data else "?"
        return {
            "category": cat_name,
            "service_id": row.get("service_api_id"),
            "service_name": row.get("service_name") or "خدمة",
        }
    except Exception as e:
        log_error(f"❌ [SERVICES] lookup_service_by_api_id: {type(e).__name__}: {str(e)}")
        return None


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
            }).select('user_id').execute()
            
            ok = bool(result.data)
            if not ok:
                chk = client.table('users').select('user_id').eq('user_id', test_user_id).limit(1).execute()
                ok = bool(chk.data)
            if ok:
                log_error(f"✅ Test user inserted successfully!")
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
