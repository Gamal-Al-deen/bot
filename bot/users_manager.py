# -*- coding: utf-8 -*-
"""
نظام إدارة المستخدمين والرصيد - Supabase
User Balance Management System - Supabase Version
"""

from database import (
    create_user,
    get_user,
    get_balance,
    add_balance,
    deduct_balance,
    set_balance,
    get_all_users_count,
    get_all_user_ids,
    user_exists,
    get_setting,
    set_setting,
    set_channel,
    get_channel,
    is_channel_configured
)
from functions import log_error


def registerUser(user_id, first_name="مستخدم", username="لا يوجد"):
    """
    تسجيل مستخدم جديد في قاعدة البيانات
    Register a new user in the database
    
    @param user_id: معرف المستخدم
    @param first_name: الاسم الأول
    @param username: اليوزرنيم
    @return: bool - True إذا تم التسجيل بنجاح
    """
    try:
        result = create_user(user_id, username, first_name)
        return result
    
    except Exception as e:
        log_error(f"❌ خطأ في registerUser: {str(e)}")
        return False


def getBalance(user_id):
    """
    الحصول على رصيد مستخدم معين
    Get balance for a specific user
    
    @param user_id: معرف المستخدم
    @return: float - الرصيد الحالي
    """
    try:
        return get_balance(user_id)
    
    except Exception as e:
        log_error(f"❌ خطأ في getBalance: {str(e)}")
        return 0.0


def addBalance(user_id, amount):
    """
    إضافة رصيد لمستخدم
    Add balance to a user
    
    @param user_id: معرف المستخدم
    @param amount: المبلغ المراد إضافته
    @return: bool - True إذا نجحت العملية
    """
    try:
        return add_balance(user_id, amount)
    
    except Exception as e:
        log_error(f"❌ خطأ في addBalance: {str(e)}")
        return False


def deductBalance(user_id, amount):
    """
    خصم رصيد من مستخدم
    Deduct balance from a user
    
    @param user_id: معرف المستخدم
    @param amount: المبلغ المراد خصمه
    @return: bool - True إذا نجحت العملية
    """
    try:
        return deduct_balance(user_id, amount)
    
    except Exception as e:
        log_error(f"❌ خطأ في deductBalance: {str(e)}")
        return False


def setBalance(user_id, amount):
    """
    تعيين رصيد معين لمستخدم (للأدمن فقط)
    Set specific balance for a user (Admin only)
    
    @param user_id: معرف المستخدم
    @param amount: المبلغ الجديد
    @return: bool - True إذا نجحت العملية
    """
    try:
        return set_balance(user_id, amount)
    
    except Exception as e:
        log_error(f"❌ خطأ في setBalance: {str(e)}")
        return False


def getUserData(user_id):
    """
    الحصول على جميع بيانات مستخدم
    Get all data for a specific user
    
    @param user_id: معرف المستخدم
    @return: dict - بيانات المستخدم
    """
    try:
        user = get_user(user_id)
        
        if user:
            return user
        
        # Return default if user doesn't exist
        return {"balance": 0.0, "username": "لا يوجد", "first_name": "مستخدم"}
    
    except Exception as e:
        log_error(f"❌ خطأ في getUserData: {str(e)}")
        return {"balance": 0.0}


def getAllUsersCount():
    """
    الحصول على عدد جميع المستخدمين
    Get total number of users
    
    @return: int - عدد المستخدمين
    """
    try:
        return get_all_users_count()
    
    except Exception as e:
        log_error(f"❌ خطأ في getAllUsersCount: {str(e)}")
        return 0


def getAllUserIds():
    """
    الحصول على قائمة جميع معرفات المستخدمين
    Get list of all user IDs
    
    @return: list - قائمة معرفات المستخدمين
    """
    try:
        return get_all_user_ids()
    
    except Exception as e:
        log_error(f"❌ خطأ في getAllUserIds: {str(e)}")
        return []


def getUserInfo(user_id):
    """
    الحصول على معلومات مستخدم كاملة
    Get complete user information
    
    @param user_id: معرف المستخدم
    @return: dict - معلومات المستخدم
    """
    try:
        user = get_user(user_id)
        
        if user:
            return {
                'user_id': str(user['user_id']),
                'balance': float(user.get('balance', 0.0)),
                'username': user.get('username', 'لا يوجد'),
                'first_name': user.get('first_name', 'مستخدم'),
                'registered': True
            }
        
        return {
            'user_id': str(user_id),
            'balance': 0.0,
            'username': 'لا يوجد',
            'first_name': 'مستخدم',
            'registered': False
        }
    
    except Exception as e:
        log_error(f"❌ خطأ في getUserInfo: {str(e)}")
        return {
            'user_id': str(user_id),
            'balance': 0.0,
            'registered': False
        }


def userExists(user_id):
    """
    التحقق من وجود مستخدم
    Check if user exists
    
    @param user_id: معرف المستخدم
    @return: bool - True إذا كان المستخدم موجوداً
    """
    try:
        return user_exists(user_id)
    
    except Exception as e:
        log_error(f"❌ خطأ في userExists: {str(e)}")
        return False


def isNewUser(user_id):
    """
    التحقق مما إذا كان المستخدم جديد (أول مرة)
    Check if user is new (first time)
    
    @param user_id: معرف المستخدم
    @return: bool - True إذا كان المستخدم جديد
    """
    try:
        return not user_exists(user_id)
    
    except Exception as e:
        log_error(f"❌ خطأ في isNewUser: {str(e)}")
        return False


# ========== نظام إشعارات الأدمن ==========

def getNotificationSettings():
    """
    الحصول على إعدادات إشعارات الأدمن
    Get admin notification settings
    
    @return: dict - إعدادات الإشعارات
    """
    try:
        value = get_setting('new_user_notifications')
        enabled = value.lower() == 'true' if value else True
        
        return {
            "new_user_notifications": enabled
        }
    
    except Exception as e:
        log_error(f"❌ خطأ في getNotificationSettings: {str(e)}")
        return {"new_user_notifications": True}


def isNewUserNotificationsEnabled():
    """
    التحقق من تفعيل إشعارات المستخدمين الجدد
    Check if new user notifications are enabled
    
    @return: bool - True إذا كانت مفعّلة
    """
    try:
        settings = getNotificationSettings()
        return settings.get("new_user_notifications", True)
    
    except Exception as e:
        log_error(f"❌ خطأ في isNewUserNotificationsEnabled: {str(e)}")
        return True


def toggleNewUserNotifications():
    """
    تبديل حالة إشعارات المستخدمين الجدد (تفعيل/إيقاف)
    Toggle new user notifications (enable/disable)
    
    @return: bool - الحالة الجديدة بعد التبديل
    """
    try:
        current_state = isNewUserNotificationsEnabled()
        new_state = not current_state
        
        set_setting('new_user_notifications', str(new_state).lower())
        
        status = "مفعّلة ✅" if new_state else "متوقفة ❌"
        log_error(f"🔔 تم تبديل إشعارات المستخدمين الجدد: {status}")
        
        return new_state
    
    except Exception as e:
        log_error(f"❌ خطأ في toggleNewUserNotifications: {str(e)}")
        return True


# ========== نظام قناة الإشعارات ==========

def setChannelUsername(username):
    """
    تعيين يوزرنيم القناة
    Set channel username
    
    @param username: يوزرنيم القناة (مع أو بدون @)
    @return: bool - True إذا تم الحفظ بنجاح
    """
    try:
        return set_channel(username)
    
    except Exception as e:
        log_error(f"❌ خطأ في setChannelUsername: {str(e)}")
        return False


def getChannelUsername():
    """
    الحصول على يوزرنيم القناة
    Get channel username
    
    @return: str - يوزرنيم القناة (بدون @)
    """
    try:
        channel = get_channel()
        if channel:
            return channel.get('channel_username', '')
        return ""
    
    except Exception as e:
        log_error(f"❌ خطأ في getChannelUsername: {str(e)}")
        return ""


def isChannelConfigured():
    """
    التحقق من إعداد القناة
    Check if channel is configured
    
    @return: bool - True إذا تم إعداد القناة
    """
    try:
        return is_channel_configured()
    
    except Exception as e:
        log_error(f"❌ خطأ في isChannelConfigured: {str(e)}")
        return False
