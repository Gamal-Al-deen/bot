# -*- coding: utf-8 -*-
"""
طبقة قاعدة البيانات - Supabase
Database Layer - Supabase Integration

Contains all CRUD operations for:
- Users management
- Categories management
- Services management
- Pricing rules
- Orders management
- Settings management
- Channels management
"""

from supabase import create_client, Client
from config import SUPABASE_URL, SUPABASE_KEY
from functions import log_error
from typing import Optional, Dict, List, Any
from decimal import Decimal


# Global Supabase client instance
supabase_client: Optional[Client] = None


def init_db() -> bool:
    """
    Initialize Supabase connection and test it
    @return: bool - True if connection successful
    """
    global supabase_client
    
    try:
        log_error("🗄️ Initializing Supabase connection...")
        
        # Create Supabase client
        supabase_client = create_client(SUPABASE_URL, SUPABASE_KEY)
        
        # Test connection by fetching settings
        test_query = supabase_client.table('settings').select('key').limit(1).execute()
        
        if test_query.data is not None:
            log_error("✅ Supabase connected successfully!")
            return True
        else:
            log_error("❌ Supabase connection test failed")
            return False
            
    except Exception as e:
        log_error(f"❌ Critical error in init_db: {type(e).__name__}: {str(e)}")
        return False


def get_supabase_client() -> Optional[Client]:
    """
    Get Supabase client instance
    @return: Supabase client or None
    """
    if supabase_client is None:
        init_db()
    return supabase_client


# =====================================================
# USERS MANAGEMENT
# =====================================================

def create_user(user_id: int, username: str = "لا يوجد", first_name: str = "مستخدم") -> bool:
    """
    Register a new user
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        # Check if user exists first
        existing = client.table('users').select('user_id').eq('user_id', user_id).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update user info
            client.table('users').update({
                'username': username,
                'first_name': first_name
            }).eq('user_id', user_id).execute()
            log_error(f"ℹ️ User {user_id} exists - updated info")
            return False
        
        # Create new user
        client.table('users').insert({
            'user_id': user_id,
            'username': username,
            'first_name': first_name,
            'balance': 0.0
        }).execute()
        
        log_error(f"✅ New user registered: {user_id} | {first_name} | @{username}")
        return True
        
    except Exception as e:
        log_error(f"❌ Error in create_user: {type(e).__name__}: {str(e)}")
        return False


def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """
    Get user data by user_id
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        result = client.table('users').select('*').eq('user_id', user_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        return None
        
    except Exception as e:
        log_error(f"❌ Error in get_user: {type(e).__name__}: {str(e)}")
        return None


def get_balance(user_id: int) -> float:
    """
    Get user balance
    """
    try:
        user = get_user(user_id)
        if user:
            return float(user.get('balance', 0.0))
        return 0.0
        
    except Exception as e:
        log_error(f"❌ Error in get_balance: {type(e).__name__}: {str(e)}")
        return 0.0


def add_balance(user_id: int, amount: float) -> bool:
    """
    Add balance to user
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        amount = float(amount)
        if amount <= 0:
            log_error(f"❌ Invalid amount: {amount}")
            return False
        
        # Get current balance
        current_balance = get_balance(user_id)
        new_balance = current_balance + amount
        
        # Update balance
        result = client.table('users').update({
            'balance': new_balance
        }).eq('user_id', user_id).execute()
        
        if result.data:
            log_error(f"✅ Added {amount}$ to user {user_id} | New balance: {new_balance}$")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ Error in add_balance: {type(e).__name__}: {str(e)}")
        return False


def deduct_balance(user_id: int, amount: float) -> bool:
    """
    Deduct balance from user
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        amount = float(amount)
        if amount <= 0:
            log_error(f"❌ Invalid amount: {amount}")
            return False
        
        # Get current balance
        current_balance = get_balance(user_id)
        
        if current_balance < amount:
            log_error(f"❌ Insufficient balance for user {user_id} | Balance: {current_balance}$ | Required: {amount}$")
            return False
        
        new_balance = current_balance - amount
        
        # Update balance
        result = client.table('users').update({
            'balance': new_balance
        }).eq('user_id', user_id).execute()
        
        if result.data:
            log_error(f"✅ Deducted {amount}$ from user {user_id} | New balance: {new_balance}$")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ Error in deduct_balance: {type(e).__name__}: {str(e)}")
        return False


def set_balance(user_id: int, amount: float) -> bool:
    """
    Set exact balance for user
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        amount = float(amount)
        if amount < 0:
            log_error(f"❌ Negative balance: {amount}")
            return False
        
        result = client.table('users').update({
            'balance': amount
        }).eq('user_id', user_id).execute()
        
        if result.data:
            log_error(f"✅ Set balance for user {user_id} to {amount}$")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ Error in set_balance: {type(e).__name__}: {str(e)}")
        return False


def get_all_users_count() -> int:
    """
    Get total number of users
    """
    try:
        client = get_supabase_client()
        if not client:
            return 0
        
        result = client.table('users').select('user_id', count='exact').execute()
        return result.count if result.count is not None else 0
        
    except Exception as e:
        log_error(f"❌ Error in get_all_users_count: {type(e).__name__}: {str(e)}")
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
        return [user['user_id'] for user in result.data] if result.data else []
        
    except Exception as e:
        log_error(f"❌ Error in get_all_user_ids: {type(e).__name__}: {str(e)}")
        return []


def user_exists(user_id: int) -> bool:
    """
    Check if user exists
    """
    try:
        user = get_user(user_id)
        return user is not None
        
    except Exception as e:
        log_error(f"❌ Error in user_exists: {type(e).__name__}: {str(e)}")
        return False


# =====================================================
# CATEGORIES MANAGEMENT
# =====================================================

def create_category(name: str) -> bool:
    """
    Create a new category
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        # Check if category exists
        existing = client.table('categories').select('id').eq('name', name).execute()
        
        if existing.data and len(existing.data) > 0:
            log_error(f"⚠️ Category '{name}' already exists")
            return False
        
        # Create category
        result = client.table('categories').insert({
            'name': name
        }).execute()
        
        if result.data:
            log_error(f"✅ Category created: {name}")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ Error in create_category: {type(e).__name__}: {str(e)}")
        return False


def get_all_categories() -> List[Dict[str, Any]]:
    """
    Get all categories
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        result = client.table('categories').select('*').order('id', desc=False).execute()
        return result.data if result.data else []
        
    except Exception as e:
        log_error(f"❌ Error in get_all_categories: {type(e).__name__}: {str(e)}")
        return []


def get_category_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Get category by name
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        result = client.table('categories').select('*').eq('name', name).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        return None
        
    except Exception as e:
        log_error(f"❌ Error in get_category_by_name: {type(e).__name__}: {str(e)}")
        return None


def delete_category(category_id: int) -> bool:
    """
    Delete category (cascades to services and pricing rules)
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        result = client.table('categories').delete().eq('id', category_id).execute()
        
        if result.data:
            log_error(f"✅ Category deleted: ID {category_id}")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ Error in delete_category: {type(e).__name__}: {str(e)}")
        return False


# =====================================================
# SERVICES MANAGEMENT
# =====================================================

def add_service(category_id: int, service_api_id: int) -> Optional[int]:
    """
    Add service to category
    @return: service id or None
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        # Check if service already exists in this category
        existing = client.table('services').select('id').eq('category_id', category_id).eq('service_api_id', service_api_id).execute()
        
        if existing.data and len(existing.data) > 0:
            log_error(f"⚠️ Service {service_api_id} already exists in category {category_id}")
            return None
        
        # Add service
        result = client.table('services').insert({
            'category_id': category_id,
            'service_api_id': service_api_id
        }).execute()
        
        if result.data:
            service_id = result.data[0]['id']
            log_error(f"✅ Service added: API ID {service_api_id} to category {category_id}")
            return service_id
        
        return None
        
    except Exception as e:
        log_error(f"❌ Error in add_service: {type(e).__name__}: {str(e)}")
        return None


def get_services_by_category(category_id: int) -> List[Dict[str, Any]]:
    """
    Get all services in a category
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        result = client.table('services').select('*').eq('category_id', category_id).order('id', desc=False).execute()
        return result.data if result.data else []
        
    except Exception as e:
        log_error(f"❌ Error in get_services_by_category: {type(e).__name__}: {str(e)}")
        return []


def delete_service(service_id: int) -> bool:
    """
    Delete service (cascades to pricing rules)
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        result = client.table('services').delete().eq('id', service_id).execute()
        
        if result.data:
            log_error(f"✅ Service deleted: ID {service_id}")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ Error in delete_service: {type(e).__name__}: {str(e)}")
        return False


def get_all_services_flat() -> List[Dict[str, Any]]:
    """
    Get all services with category information
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        # Join services with categories
        result = client.table('services').select(
            'id, category_id, service_api_id, created_at, categories(name)'
        ).order('id', desc=False).execute()
        
        if not result.data:
            return []
        
        # Flatten the data
        services = []
        for service in result.data:
            services.append({
                'id': service['id'],
                'category_id': service['category_id'],
                'category_name': service['categories']['name'] if service.get('categories') else 'Unknown',
                'service_api_id': service['service_api_id'],
                'created_at': service['created_at']
            })
        
        return services
        
    except Exception as e:
        log_error(f"❌ Error in get_all_services_flat: {type(e).__name__}: {str(e)}")
        return []


def get_service_by_api_id(service_api_id: int) -> Optional[Dict[str, Any]]:
    """
    Get service info by API ID
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        result = client.table('services').select(
            'id, category_id, service_api_id, created_at, categories(name)'
        ).eq('service_api_id', service_api_id).execute()
        
        if result.data and len(result.data) > 0:
            service = result.data[0]
            return {
                'id': service['id'],
                'category_id': service['category_id'],
                'category_name': service['categories']['name'] if service.get('categories') else 'Unknown',
                'service_api_id': service['service_api_id'],
                'created_at': service['created_at']
            }
        
        return None
        
    except Exception as e:
        log_error(f"❌ Error in get_service_by_api_id: {type(e).__name__}: {str(e)}")
        return None


# =====================================================
# PRICING RULES
# =====================================================

def set_pricing_rule(service_id: int, pricing_type: str, price_value: float = None, percentage_value: float = None) -> bool:
    """
    Set pricing rule for a service
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        if pricing_type not in ['fixed', 'percentage']:
            log_error(f"❌ Invalid pricing type: {pricing_type}")
            return False
        
        # Check if pricing rule exists
        existing = client.table('pricing_rules').select('id').eq('service_id', service_id).execute()
        
        pricing_data = {
            'service_id': service_id,
            'pricing_type': pricing_type
        }
        
        if pricing_type == 'fixed' and price_value is not None:
            pricing_data['price_value'] = float(price_value)
        elif pricing_type == 'percentage' and percentage_value is not None:
            pricing_data['percentage_value'] = float(percentage_value)
        
        if existing.data and len(existing.data) > 0:
            # Update existing rule
            result = client.table('pricing_rules').update(pricing_data).eq('service_id', service_id).execute()
        else:
            # Insert new rule
            result = client.table('pricing_rules').insert(pricing_data).execute()
        
        if result.data:
            log_error(f"✅ Pricing rule set for service {service_id}: {pricing_type}")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ Error in set_pricing_rule: {type(e).__name__}: {str(e)}")
        return False


def get_pricing_rule(service_id: int) -> Optional[Dict[str, Any]]:
    """
    Get pricing rule for a service
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        result = client.table('pricing_rules').select('*').eq('service_id', service_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        # Return default pricing (percentage 50%)
        return {
            'pricing_type': 'percentage',
            'price_value': None,
            'percentage_value': 50.0
        }
        
    except Exception as e:
        log_error(f"❌ Error in get_pricing_rule: {type(e).__name__}: {str(e)}")
        return None


def calculate_final_price(service_id: int, api_rate: float, quantity: int) -> Dict[str, float]:
    """
    Calculate final price with per-service pricing
    """
    try:
        # Calculate original price
        original_price = (api_rate * quantity) / 1000.0
        
        # Get pricing rule
        pricing_rule = get_pricing_rule(service_id)
        
        if pricing_rule['pricing_type'] == 'fixed' and pricing_rule.get('price_value'):
            # Fixed pricing: price_value per 1000
            final_price = pricing_rule['price_value'] * (quantity / 1000.0)
        else:
            # Percentage pricing
            percentage = pricing_rule.get('percentage_value', 50.0)
            final_price = original_price + (original_price * percentage / 100.0)
        
        return {
            'original_price': round(original_price, 6),
            'final_price': round(final_price, 6),
            'quantity': quantity
        }
        
    except Exception as e:
        log_error(f"❌ Error in calculate_final_price: {type(e).__name__}: {str(e)}")
        return {
            'original_price': 0.0,
            'final_price': 0.0,
            'quantity': quantity
        }


# =====================================================
# ORDERS MANAGEMENT
# =====================================================

def create_order(user_id: int, service_api_id: int, original_price: float, 
                 final_price: float, quantity: int, link: str, 
                 status: str = 'pending', order_api_id: int = None) -> Optional[int]:
    """
    Create order record
    @return: order id or None
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        order_data = {
            'user_id': user_id,
            'service_api_id': service_api_id,
            'original_price': original_price,
            'final_price': final_price,
            'quantity': quantity,
            'link': link,
            'status': status
        }
        
        if order_api_id:
            order_data['order_api_id'] = order_api_id
        
        result = client.table('orders').insert(order_data).execute()
        
        if result.data:
            order_id = result.data[0]['id']
            log_error(f"✅ Order created: ID {order_id} for user {user_id}")
            return order_id
        
        return None
        
    except Exception as e:
        log_error(f"❌ Error in create_order: {type(e).__name__}: {str(e)}")
        return None


def get_user_orders(user_id: int) -> List[Dict[str, Any]]:
    """
    Get all orders for a user
    """
    try:
        client = get_supabase_client()
        if not client:
            return []
        
        result = client.table('orders').select('*').eq('user_id', user_id).order('created_at', desc=True).execute()
        return result.data if result.data else []
        
    except Exception as e:
        log_error(f"❌ Error in get_user_orders: {type(e).__name__}: {str(e)}")
        return []


def get_order(order_id: int) -> Optional[Dict[str, Any]]:
    """
    Get specific order
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        result = client.table('orders').select('*').eq('id', order_id).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        return None
        
    except Exception as e:
        log_error(f"❌ Error in get_order: {type(e).__name__}: {str(e)}")
        return None


# =====================================================
# SETTINGS MANAGEMENT
# =====================================================

def get_setting(key: str) -> Optional[str]:
    """
    Get setting value
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        result = client.table('settings').select('value').eq('key', key).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]['value']
        
        return None
        
    except Exception as e:
        log_error(f"❌ Error in get_setting: {type(e).__name__}: {str(e)}")
        return None


def set_setting(key: str, value: str) -> bool:
    """
    Set setting value
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        # Check if setting exists
        existing = client.table('settings').select('key').eq('key', key).execute()
        
        if existing.data and len(existing.data) > 0:
            # Update
            result = client.table('settings').update({'value': value}).eq('key', key).execute()
        else:
            # Insert
            result = client.table('settings').insert({'key': key, 'value': value}).execute()
        
        if result.data:
            log_error(f"✅ Setting updated: {key} = {value}")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ Error in set_setting: {type(e).__name__}: {str(e)}")
        return False


# =====================================================
# CHANNELS MANAGEMENT
# =====================================================

def set_channel(username: str) -> bool:
    """
    Set notification channel
    """
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        username = username.strip().lstrip('@')
        
        # Delete existing channels
        client.table('channels').delete().neq('id', 0).execute()
        
        # Insert new channel
        result = client.table('channels').insert({
            'channel_username': username,
            'enabled': True if username else False
        }).execute()
        
        if result.data:
            log_error(f"📣 Channel set: @{username}")
            return True
        
        return False
        
    except Exception as e:
        log_error(f"❌ Error in set_channel: {type(e).__name__}: {str(e)}")
        return False


def get_channel() -> Optional[Dict[str, Any]]:
    """
    Get channel info
    """
    try:
        client = get_supabase_client()
        if not client:
            return None
        
        result = client.table('channels').select('*').eq('enabled', True).limit(1).execute()
        
        if result.data and len(result.data) > 0:
            return result.data[0]
        
        return None
        
    except Exception as e:
        log_error(f"❌ Error in get_channel: {type(e).__name__}: {str(e)}")
        return None


def is_channel_configured() -> bool:
    """
    Check if channel is configured
    """
    try:
        channel = get_channel()
        return channel is not None and channel.get('channel_username', '').strip() != ''
        
    except Exception as e:
        log_error(f"❌ Error in is_channel_configured: {type(e).__name__}: {str(e)}")
        return False
