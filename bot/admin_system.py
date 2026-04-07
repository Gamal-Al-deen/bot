# -*- coding: utf-8 -*-
"""
نظام إدارة الأدمن
Admin Management System
"""

from config import ADMIN_ID
from functions import log_error


def isAdmin(user_id):
    """
    التحقق مما إذا كان المستخدم هو الأدمن
    Check if user is admin
    
    @param user_id: معرف المستخدم
    @return: bool - True إذا كان أدمن
    """
    try:
        return str(user_id) == str(ADMIN_ID)
    
    except Exception as e:
        log_error(f"❌ خطأ في isAdmin: {str(e)}")
        return False


def requireAdmin(user_id):
    """
    التحقق من صلاحية الأدمن مع إرسال رسالة خطأ إذا لم يكن أدمن
    Check admin permission and send error message if not admin
    
    @param user_id: معرف المستخدم
    @return: bool - True إذا كان أدمن
    """
    try:
        if isAdmin(user_id):
            return True
        else:
            log_error(f"⚠️ محاولة وصول غير مصرح بها من المستخدم {user_id}")
            return False
    
    except Exception as e:
        log_error(f"❌ خطأ في requireAdmin: {str(e)}")
        return False


def getAdminId():
    """
    الحصول على معرف الأدمن
    Get admin ID
    
    @return: str - معرف الأدمن
    """
    return str(ADMIN_ID)


def validateAdminCommand(user_id, command_name):
    """
    التحقق من صلاحية الأدمن وتسجيل العملية
    Validate admin permission and log the operation
    
    @param user_id: معرف المستخدم
    @param command_name: اسم الأمر
    @return: bool - True إذا كان لديه صلاحية
    """
    try:
        if isAdmin(user_id):
            log_error(f"👑 الأدمن {user_id} نفذ الأمر: {command_name}")
            return True
        else:
            log_error(f"🚫 مستخدم غير مصرح {user_id} حاول تنفيذ: {command_name}")
            return False
    
    except Exception as e:
        log_error(f"❌ خطأ في validateAdminCommand: {str(e)}")
        return False
