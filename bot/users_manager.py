# -*- coding: utf-8 -*-
"""
نظام إدارة المستخدمين والرصيد
User Balance Management System
"""

import json
import os
from functions import log_error

# مسار ملف بيانات المستخدمين
USERS_FILE = "users_data.json"


def getUsers():
    """
    قراءة بيانات جميع المستخدمين من الملف
    Read all users data from file
    
    @return: dict - قاموس بيانات المستخدمين
    """
    try:
        if os.path.exists(USERS_FILE):
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data
        else:
            # إنشاء ملف جديد إذا لم يكن موجوداً
            saveUsers({})
            return {}
    
    except Exception as e:
        log_error(f"❌ خطأ في getUsers: {str(e)}")
        return {}


def saveUsers(users_data):
    """
    حفظ بيانات المستخدمين في الملف
    Save users data to file
    
    @param users_data: dict - بيانات المستخدمين
    """
    try:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_data, f, indent=4, ensure_ascii=False)
    
    except Exception as e:
        log_error(f"❌ خطأ في saveUsers: {str(e)}")


def getBalance(user_id):
    """
    الحصول على رصيد مستخدم معين
    Get balance for a specific user
    
    @param user_id: معرف المستخدم
    @return: float - الرصيد الحالي
    """
    try:
        users = getUsers()
        user_id_str = str(user_id)
        
        # إنشاء المستخدم تلقائياً إذا لم يكن موجوداً
        if user_id_str not in users:
            users[user_id_str] = {"balance": 0.0}
            saveUsers(users)
            log_error(f"✅ تم إنشاء مستخدم جديد: {user_id_str}")
        
        return float(users[user_id_str].get("balance", 0.0))
    
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
        # التحقق من صحة المبلغ
        amount = float(amount)
        if amount <= 0:
            log_error(f"❌ محاولة إضافة مبلغ غير صالح: {amount}")
            return False
        
        users = getUsers()
        user_id_str = str(user_id)
        
        # إنشاء المستخدم إذا لم يكن موجوداً
        if user_id_str not in users:
            users[user_id_str] = {"balance": 0.0}
        
        # إضافة الرصيد
        users[user_id_str]["balance"] = float(users[user_id_str]["balance"]) + amount
        saveUsers(users)
        
        new_balance = users[user_id_str]["balance"]
        log_error(f"✅ تم إضافة {amount}$ للمستخدم {user_id_str} | الرصيد الجديد: {new_balance}$")
        
        return True
    
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
        # التحقق من صحة المبلغ
        amount = float(amount)
        if amount <= 0:
            log_error(f"❌ محاولة خصم مبلغ غير صالح: {amount}")
            return False
        
        users = getUsers()
        user_id_str = str(user_id)
        
        # إنشاء المستخدم إذا لم يكن موجوداً
        if user_id_str not in users:
            users[user_id_str] = {"balance": 0.0}
        
        current_balance = float(users[user_id_str]["balance"])
        
        # التحقق من وجود رصيد كافٍ
        if current_balance < amount:
            log_error(f"❌ رصيد غير كافٍ للمستخدم {user_id_str} | الرصيد: {current_balance}$ | المطلوب: {amount}$")
            return False
        
        # خصم الرصيد
        users[user_id_str]["balance"] = current_balance - amount
        saveUsers(users)
        
        new_balance = users[user_id_str]["balance"]
        log_error(f"✅ تم خصم {amount}$ من المستخدم {user_id_str} | الرصيد الجديد: {new_balance}$")
        
        return True
    
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
        amount = float(amount)
        if amount < 0:
            log_error(f"❌ محاولة تعيين رصيد سالب: {amount}")
            return False
        
        users = getUsers()
        user_id_str = str(user_id)
        
        # إنشاء المستخدم إذا لم يكن موجوداً
        if user_id_str not in users:
            users[user_id_str] = {"balance": 0.0}
        
        users[user_id_str]["balance"] = amount
        saveUsers(users)
        
        log_error(f"✅ تم تعيين رصيد المستخدم {user_id_str} إلى {amount}$")
        return True
    
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
        users = getUsers()
        user_id_str = str(user_id)
        
        if user_id_str not in users:
            users[user_id_str] = {"balance": 0.0}
            saveUsers(users)
        
        return users[user_id_str]
    
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
        users = getUsers()
        return len(users)
    
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
        users = getUsers()
        return list(users.keys())
    
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
        users = getUsers()
        user_id_str = str(user_id)
        
        if user_id_str not in users:
            users[user_id_str] = {"balance": 0.0}
            saveUsers(users)
        
        user_data = users[user_id_str]
        
        return {
            'user_id': user_id_str,
            'balance': float(user_data.get('balance', 0.0)),
            'registered': True
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
        users = getUsers()
        return str(user_id) in users
    
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
        return not userExists(user_id)
    
    except Exception as e:
        log_error(f"❌ خطأ في isNewUser: {str(e)}")
        return False


# ========== نظام إشعارات الأدمن ==========

NOTIFICATIONS_FILE = "admin_notifications.json"


def getNotificationSettings():
    """
    الحصول على إعدادات إشعارات الأدمن
    Get admin notification settings
    
    @return: dict - إعدادات الإشعارات
    """
    try:
        if os.path.exists(NOTIFICATIONS_FILE):
            with open(NOTIFICATIONS_FILE, 'r', encoding='utf-8') as f:
                settings = json.load(f)
                return settings
        else:
            # إعدادات افتراضية - الإشعارات مفعّلة
            default_settings = {
                "new_user_notifications": True
            }
            saveNotificationSettings(default_settings)
            return default_settings
    
    except Exception as e:
        log_error(f"❌ خطأ في getNotificationSettings: {str(e)}")
        return {"new_user_notifications": True}


def saveNotificationSettings(settings):
    """
    حفظ إعدادات إشعارات الأدمن
    Save admin notification settings
    
    @param settings: dict - إعدادات الإشعارات
    """
    try:
        with open(NOTIFICATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=4, ensure_ascii=False)
    
    except Exception as e:
        log_error(f"❌ خطأ في saveNotificationSettings: {str(e)}")


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
        return True  # افتراضياً مفعّلة


def toggleNewUserNotifications():
    """
    تبديل حالة إشعارات المستخدمين الجدد (تفعيل/إيقاف)
    Toggle new user notifications (enable/disable)
    
    @return: bool - الحالة الجديدة بعد التبديل
    """
    try:
        settings = getNotificationSettings()
        current_state = settings.get("new_user_notifications", True)
        new_state = not current_state
        
        settings["new_user_notifications"] = new_state
        saveNotificationSettings(settings)
        
        status = "مفعّلة ✅" if new_state else "متوقفة ❌"
        log_error(f"🔔 تم تبديل إشعارات المستخدمين الجدد: {status}")
        
        return new_state
    
    except Exception as e:
        log_error(f"❌ خطأ في toggleNewUserNotifications: {str(e)}")
        return True
