# -*- coding: utf-8 -*-
"""
نظام قفل المستخدمين ومنع الطلبات المتعددة
User Lock System - Prevent Multiple Simultaneous Requests
"""

import time
from functions import log_error

# قاموس لتخزين حالة القفل للمستخدمين
user_locks = {}


def acquireLock(user_id, timeout=60):
    """
    الحصول على قفل للمستخدم
    Acquire lock for a user
    
    @param user_id: معرف المستخدم
    @param timeout: مدة القفل بالثواني (افتراضي 60)
    @return: bool - True إذا تم الحصول على القفل
    """
    try:
        current_time = time.time()
        
        # التحقق إذا كان المستخدم مقفلاً
        if user_id in user_locks:
            lock_info = user_locks[user_id]
            lock_time = lock_info.get('time', 0)
            
            # التحقق من انتهاء صلاحية القفل
            if current_time - lock_time < timeout:
                log_error(f"🔒 المستخدم {user_id} مقفل حالياً")
                return False
            else:
                # القفل منتهي الصلاحية، حذفه
                del user_locks[user_id]
        
        # تعيين قفل جديد
        user_locks[user_id] = {
            'time': current_time,
            'action': 'processing'
        }
        
        log_error(f"🔓 تم قفل المستخدم {user_id}")
        return True
    
    except Exception as e:
        log_error(f"❌ خطأ في acquireLock: {str(e)}")
        return False


def releaseLock(user_id):
    """
    تحرير قفل المستخدم
    Release user lock
    
    @param user_id: معرف المستخدم
    """
    try:
        if user_id in user_locks:
            del user_locks[user_id]
            log_error(f"🔓 تم تحرير قفل المستخدم {user_id}")
    
    except Exception as e:
        log_error(f"❌ خطأ في releaseLock: {str(e)}")


def isLocked(user_id, timeout=60):
    """
    التحقق مما إذا كان المستخدم مقفلاً
    Check if user is locked
    
    @param user_id: معرف المستخدم
    @param timeout: مدة القفل بالثواني
    @return: bool - True إذا كان مقفلاً
    """
    try:
        if user_id in user_locks:
            lock_time = user_locks[user_id].get('time', 0)
            current_time = time.time()
            
            if current_time - lock_time < timeout:
                return True
            else:
                # القفل منتهي الصلاحية
                del user_locks[user_id]
                return False
        
        return False
    
    except Exception as e:
        log_error(f"❌ خطأ في isLocked: {str(e)}")
        return False


def getLockStatus(user_id):
    """
    الحصول على حالة قفل المستخدم
    Get user lock status
    
    @param user_id: معرف المستخدم
    @return: dict - معلومات القفل
    """
    try:
        if user_id in user_locks:
            lock_info = user_locks[user_id]
            lock_time = lock_info.get('time', 0)
            current_time = time.time()
            elapsed = current_time - lock_time
            
            return {
                'locked': True,
                'elapsed_seconds': round(elapsed, 2),
                'action': lock_info.get('action', 'unknown')
            }
        else:
            return {
                'locked': False,
                'elapsed_seconds': 0,
                'action': 'none'
            }
    
    except Exception as e:
        log_error(f"❌ خطأ في getLockStatus: {str(e)}")
        return {'locked': False, 'elapsed_seconds': 0, 'action': 'error'}
