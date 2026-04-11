# -*- coding: utf-8 -*-
"""
نظام إدارة المستخدمين والرصيد
User Balance Management System

✅ Updated to use Supabase Database - No JSON!
"""

from functions import log_error
from database import (
    create_user,
    get_user,
    update_user_balance,
    user_exists as db_user_exists,
    get_all_users_count,
    get_setting,
    set_setting,
    delete_setting,
)


def registerUser(user_id, first_name="مستخدم", username="لا يوجد"):
    """
    تسجيل مستخدم جديد في قاعدة البيانات
    Register a new user in Supabase database
    
    @param user_id: معرف المستخدم
    @param first_name: الاسم الأول
    @param username: اليوزرنيم
    @return: bool - True إذا كان المستخدم جديد، False إذا كان موجود
    """
    try:
        # استخدام Supabase بدلاً من JSON
        is_new = create_user(user_id, username, first_name)
        
        if is_new:
            log_error(f"✅ تم تسجيل مستخدم جديد في Supabase: {user_id} | Name: {first_name} | Username: {username}")
        else:
            log_error(f"ℹ️ المستخدم {user_id} موجود بالفعل في Supabase")
        
        return is_new
    
    except Exception as e:
        log_error(f"❌ خطأ في registerUser: {str(e)}")
        import traceback
        log_error(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False


def userExists(user_id):
    """
    التحقق من وجود مستخدم في قاعدة البيانات
    Check if user exists in Supabase
    
    @param user_id: معرف المستخدم
    @return: bool - True إذا كان المستخدم موجود
    """
    try:
        return db_user_exists(user_id)
    except Exception as e:
        log_error(f"❌ خطأ في userExists: {str(e)}")
        return False


def getUserBalance(user_id):
    """
    الحصول على رصيد المستخدم من قاعدة البيانات
    Get user balance from Supabase
    
    @param user_id: معرف المستخدم
    @return: float - رصيد المستخدم
    """
    try:
        user = get_user(user_id)
        if user:
            return float(user.get('balance', 0.0))
        return 0.0
    except Exception as e:
        log_error(f"❌ خطأ في getUserBalance: {str(e)}")
        return 0.0


def setUserBalance(user_id, balance):
    """
    تعيين رصيد المستخدم في قاعدة البيانات
    Set user balance in Supabase
    
    @param user_id: معرف المستخدم
    @param balance: الرصيد الجديد
    @return: bool - True إذا تم التحديث بنجاح
    """
    try:
        success = update_user_balance(user_id, float(balance))
        
        if success:
            log_error(f"✅ [BALANCE] User {user_id} balance set to {balance}")
        else:
            log_error(f"❌ [BALANCE] Failed to set balance for user {user_id}")
        
        return success
        
    except Exception as e:
        log_error(f"❌ خطأ في setUserBalance: {str(e)}")
        return False


def updateUserBalance(user_id, amount):
    """
    تحديث رصيد المستخدم (إضافة أو خصم)
    Update user balance (add or subtract) in Supabase
    
    @param user_id: معرف المستخدم
    @param amount: المبلغ (موجب للإضافة، سالب للخصم)
    @return: bool - True إذا تم التحديث بنجاح
    """
    try:
        # الحصول على الرصيد الحالي
        current_balance = getUserBalance(user_id)
        new_balance = current_balance + float(amount)
        
        # تحديث الرصيد في Supabase
        success = update_user_balance(user_id, new_balance)
        
        if success:
            log_error(f"✅ [BALANCE] User {user_id}: {current_balance} + {amount} = {new_balance}")
        else:
            log_error(f"❌ [BALANCE] Failed to update balance for user {user_id}")
        
        return success
        
    except Exception as e:
        log_error(f"❌ خطأ في updateUserBalance: {str(e)}")
        return False


def addBalance(user_id, amount):
    """
    إضافة رصيد للمستخدم
    Add balance to user
    
    @param user_id: معرف المستخدم
    @param amount: المبلغ المراد إضافته
    @return: bool - True إذا تمت الإضافة بنجاح
    """
    return updateUserBalance(user_id, abs(amount))


def removeBalance(user_id, amount):
    """
    خصم رصيد من المستخدم
    Remove balance from user
    
    @param user_id: معرف المستخدم
    @param amount: المبلغ المراد خصمه
    @return: bool - True إذا تم الخصم بنجاح
    """
    return updateUserBalance(user_id, -abs(amount))


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


def getUserInfo(user_id):
    """
    الحصول على معلومات المستخدم
    Get user information
    
    @param user_id: معرف المستخدم
    @return: dict - معلومات المستخدم أو None
    """
    try:
        return get_user(user_id)
    except Exception as e:
        log_error(f"❌ خطأ في getUserInfo: {str(e)}")
        return None


# ============================================
# Admin Notification Settings (جدول settings في Supabase)
# ============================================

_SETTING_NEW_USER_NOTIF = "new_user_notifications"
_SETTING_CHANNEL_LINK = "channel_invite_link"


def isNewUserNotificationsEnabled():
    """
    التحقق من تفعيل إشعارات المستخدمين الجدد
    Check if new user notifications are enabled
    """
    try:
        raw = get_setting(_SETTING_NEW_USER_NOTIF, "true").strip().lower()
        return raw in ("true", "1", "yes", "on")
    except Exception as e:
        log_error(f"❌ خطأ في isNewUserNotificationsEnabled: {str(e)}")
        return True


def toggleNewUserNotifications():
    """
    تبديل حالة إشعارات المستخدمين الجدد
    Toggle new user notifications
    """
    try:
        current = isNewUserNotificationsEnabled()
        new_state = not current
        if not set_setting(_SETTING_NEW_USER_NOTIF, "true" if new_state else "false"):
            log_error("❌ toggleNewUserNotifications: فشل حفظ الإعداد في Supabase")
            return current
        log_error(f"✅ New user notifications: {'ENABLED' if new_state else 'DISABLED'}")
        return new_state
    except Exception as e:
        log_error(f"❌ خطأ في toggleNewUserNotifications: {str(e)}")
        return True


# ============================================
# Channel Configuration (جدول settings في Supabase)
# ============================================

def getChannelConfig():
    """
    الحصول على إعدادات القناة
    Get channel configuration
    """
    try:
        link = get_setting(_SETTING_CHANNEL_LINK, "")
        if not link:
            return None
        return {"invite_link": link, "chat_id": None, "username": link}
    except Exception as e:
        log_error(f"❌ خطأ في getChannelConfig: {str(e)}")
        return None


def setChannelConfig(chat_id, invite_link):
    """
    حفظ إعدادات القناة
    Save channel configuration
    """
    try:
        if invite_link is None:
            return False
        text = str(invite_link).strip().lstrip("@")
        if not set_setting(_SETTING_CHANNEL_LINK, text):
            return False
        log_error(f"✅ Channel config saved (invite_link set)")
        return True
    except Exception as e:
        log_error(f"❌ خطأ في setChannelConfig: {str(e)}")
        return False


def removeChannelConfig():
    """
    حذف إعدادات القناة
    Remove channel configuration
    """
    try:
        ok = delete_setting(_SETTING_CHANNEL_LINK)
        if ok:
            log_error("✅ Channel config removed from Supabase")
        return ok
    except Exception as e:
        log_error(f"❌ خطأ في removeChannelConfig: {str(e)}")
        return False


# ============================================
# Compatibility Aliases (للحفاظ على التوافق مع bot.py)
# ============================================
# هذه الدوال هي أسماء بديلة للدوال الأصلية
# الهدف: عدم الحاجة لتعديل bot.py

def getBalance(user_id):
    """
    Alias for getUserBalance - للحفاظ على التوافق
    """
    return getUserBalance(user_id)


def deductBalance(user_id, amount):
    """
    Alias for removeBalance - للحفاظ على التوافق
    """
    return removeBalance(user_id, amount)


def getAllUserIds():
    """
    Get all user IDs from Supabase
    """
    try:
        from database import get_all_user_ids
        return get_all_user_ids()
    except Exception as e:
        log_error(f"❌ خطأ في getAllUserIds: {str(e)}")
        return []


def isNewUser(user_id):
    """
    Check if user is new (doesn't exist in database)
    """
    return not userExists(user_id)


def getChannelUsername():
    """
    Get channel username from config
    """
    try:
        config = getChannelConfig()
        if config:
            return config.get('invite_link', None)
        return None
    except:
        return None


def isChannelConfigured():
    """
    Check if channel is configured
    """
    return getChannelConfig() is not None


def setChannelUsername(username):
    """
    Set channel username (alias for compatibility)
    """
    try:
        text = str(username).strip().lstrip("@")
        if not text:
            log_error("❌ setChannelUsername: empty value")
            return False
        if not set_setting(_SETTING_CHANNEL_LINK, text):
            return False
        log_error(f"✅ Channel username set: {text}")
        return True
    except Exception as e:
        log_error(f"❌ خطأ في setChannelUsername: {str(e)}")
        return False
