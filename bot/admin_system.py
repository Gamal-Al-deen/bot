# -*- coding: utf-8 -*-
"""
نظام إدارة الأدمن - نسخة محسنة وجذرية
Admin Management System - Improved & Radical Version
"""

from config import ADMIN_ID
from functions import log_error


def isAdmin(user_id):
    """
    التحقق مما إذا كان المستخدم هو الأدمن - فحص جذري ومستمر
    Check if user is admin - Radical and continuous check
    
    @param user_id: معرف المستخدم (int أو str)
    @return: bool - True إذا كان أدمن
    """
    try:
        # تحويل إلى strings للمقارنة الصحيحة
        user_id_str = str(user_id).strip()
        admin_id_str = str(ADMIN_ID).strip()
        
        # فحص دقيق
        is_admin = (user_id_str == admin_id_str)
        
        if is_admin:
            log_error(f"✅ تأكيد: المستخدم {user_id_str} هو الأدمن")
        else:
            log_error(f"❌ المستخدم {user_id_str} ليس أدمن (Admin ID: {admin_id_str})")
        
        return is_admin
    
    except Exception as e:
        log_error(f"❌ خطأ حرج في isAdmin: {str(e)}")
        return False


def checkAdminAccess(user_id, feature_name=""):
    """
    فحص شامل لصلاحيات الأدمن مع تسجيل تفصيلي
    Comprehensive admin access check with detailed logging
    
    @param user_id: معرف المستخدم
    @param feature_name: اسم الميزة المطلوب الوصول إليها
    @return: dict - نتيجة الفحص مع التفاصيل
    """
    try:
        user_id_str = str(user_id).strip()
        admin_id_str = str(ADMIN_ID).strip()
        
        result = {
            'is_admin': False,
            'user_id': user_id_str,
            'admin_id': admin_id_str,
            'feature': feature_name,
            'message': '',
            'access_granted': False
        }
        
        # فحص صارم
        if user_id_str == admin_id_str and admin_id_str not in ['', 'YOUR_ADMIN_ID_HERE', '0']:
            result['is_admin'] = True
            result['access_granted'] = True
            result['message'] = f"✅ وصول مصرح للأدمن: {feature_name}"
            log_error(f"👑 [ADMIN ACCESS] User:{user_id_str} | Feature:{feature_name} | GRANTED")
        else:
            result['access_granted'] = False
            
            if admin_id_str in ['', 'YOUR_ADMIN_ID_HERE', '0']:
                result['message'] = "⚠️ لم يتم إعداد ADMIN_ID بشكل صحيح في config.py"
                log_error(f"⚠️ [ADMIN NOT CONFIGURED] User:{user_id_str} | Feature:{feature_name}")
            else:
                result['message'] = "❌ ليس لديك صلاحية استخدام هذه الميزة"
                log_error(f"🚫 [ADMIN DENIED] User:{user_id_str} | Feature:{feature_name} | Admin ID:{admin_id_str}")
        
        return result
    
    except Exception as e:
        log_error(f"❌ خطأ حرج في checkAdminAccess: {str(e)}")
        return {
            'is_admin': False,
            'user_id': str(user_id),
            'admin_id': str(ADMIN_ID),
            'feature': feature_name,
            'message': f"❌ خطأ في التحقق: {str(e)}",
            'access_granted': False
        }


def requireAdmin(user_id, feature_name=""):
    """
    التحقق من صلاحية الأدمن مع إرجاع رسالة خطأ
    Check admin permission and return error message
    
    @param user_id: معرف المستخدم
    @param feature_name: اسم الميزة
    @return: tuple - (bool, str) - (هل هو أدمن, الرسالة)
    """
    try:
        result = checkAdminAccess(user_id, feature_name)
        return (result['access_granted'], result['message'])
    
    except Exception as e:
        log_error(f"❌ خطأ في requireAdmin: {str(e)}")
        return (False, "❌ خطأ في التحقق من الصلاحيات")


def getAdminId():
    """
    الحصول على معرف الأدمن الحالي
    Get current admin ID
    
    @return: str - معرف الأدمن
    """
    return str(ADMIN_ID).strip()


def isAdminConfigured():
    """
    التحقق من إعداد ADMIN_ID بشكل صحيح
    Check if ADMIN_ID is properly configured
    
    @return: bool - True إذا تم الإعداد بشكل صحيح
    """
    try:
        admin_id = str(ADMIN_ID).strip()
        is_configured = admin_id not in ['', 'YOUR_ADMIN_ID_HERE', '0']
        
        if not is_configured:
            log_error("⚠️ تحذير: ADMIN_ID لم يتم إعداده بشكل صحيح!")
        else:
            log_error(f"✅ ADMIN_ID تم إعداده: {admin_id}")
        
        return is_configured
    
    except Exception as e:
        log_error(f"❌ خطأ في isAdminConfigured: {str(e)}")
        return False


def validateAdminCommand(user_id, command_name):
    """
    التحقق من صلاحية الأدمن وتسجيل العملية - نسخة محسنة
    Validate admin permission and log operation - Improved version
    
    @param user_id: معرف المستخدم
    @param command_name: اسم الأمر
    @return: bool - True إذا كان لديه صلاحية
    """
    try:
        user_id_str = str(user_id).strip()
        admin_id_str = str(ADMIN_ID).strip()
        
        # فحص شامل
        if user_id_str == admin_id_str and admin_id_str not in ['', 'YOUR_ADMIN_ID_HERE', '0']:
            log_error(f"👑 [ADMIN COMMAND] Admin:{user_id_str} | Command:{command_name} | EXECUTED")
            return True
        else:
            log_error(f"🚫 [UNAUTHORIZED] User:{user_id_str} | Tried:{command_name} | Admin ID:{admin_id_str}")
            return False
    
    except Exception as e:
        log_error(f"❌ خطأ في validateAdminCommand: {str(e)}")
        return False


def getAdminFeatures():
    """
    الحصول على قائمة ميزات الأدمن
    Get list of admin features
    
    @return: list - قائمة الميزات
    """
    return [
        "إضافة رصيد للمستخدمين",
        "خصم رصيد من المستخدمين",
        "تعديل التسعير النسبي",
        "تعديل التسعير الثابت",
        "عرض إعدادات التسعير",
        "إرسال رسائل جماعية",
        "إحصائيات المستخدمين",
        "لوحة تحكم كاملة"
    ]
