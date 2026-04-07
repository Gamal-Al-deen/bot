# -*- coding: utf-8 -*-
"""
نظام السجلات المتقدم
Advanced Logging System
"""

import os
from datetime import datetime
from functions import log_error


def logOperation(operation_type, user_id, details):
    """
    تسجيل عملية مهمة
    Log an important operation
    
    @param operation_type: نوع العملية (balance, order, pricing, admin, error)
    @param user_id: معرف المستخدم
    @param details: تفاصيل العملية
    """
    try:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_message = f"[{timestamp}] [{operation_type.upper()}] User:{user_id} | {details}"
        log_error(log_message)
    
    except Exception as e:
        log_error(f"❌ خطأ في logOperation: {str(e)}")


def logBalanceOperation(user_id, operation, amount, balance_before, balance_after):
    """
    تسجيل عملية رصيد
    Log balance operation
    
    @param user_id: معرف المستخدم
    @param operation: نوع العملية (add, deduct)
    @param amount: المبلغ
    @param balance_before: الرصيد قبل
    @param balance_after: الرصيد بعد
    """
    try:
        details = f"{operation} {amount}$ | Before: {balance_before}$ | After: {balance_after}$"
        logOperation("balance", user_id, details)
    
    except Exception as e:
        log_error(f"❌ خطأ في logBalanceOperation: {str(e)}")


def logOrderOperation(user_id, order_id, service_id, quantity, total_price, status):
    """
    تسجيل عملية طلب
    Log order operation
    
    @param user_id: معرف المستخدم
    @param order_id: معرف الطلب
    @param service_id: معرف الخدمة
    @param quantity: الكمية
    @param total_price: السعر الإجمالي
    @param status: حالة الطلب (success, failed)
    """
    try:
        details = f"Order:{order_id} | Service:{service_id} | Qty:{quantity} | Price:{total_price}$ | Status:{status}"
        logOperation("order", user_id, details)
    
    except Exception as e:
        log_error(f"❌ خطأ في logOrderOperation: {str(e)}")


def logPricingOperation(admin_id, pricing_type, value):
    """
    تسجيل عملية تغيير التسعير
    Log pricing change operation
    
    @param admin_id: معرف الأدمن
    @param pricing_type: نوع التسعير (percent, fixed)
    @param value: القيمة
    """
    try:
        details = f"Admin:{admin_id} | Type:{pricing_type} | Value:{value}"
        logOperation("pricing", admin_id, details)
    
    except Exception as e:
        log_error(f"❌ خطأ في logPricingOperation: {str(e)}")


def logAdminOperation(admin_id, command, target_user=None, details=None):
    """
    تسجيل عملية أدمن
    Log admin operation
    
    @param admin_id: معرف الأدمن
    @param command: الأمر المنفذ
    @param target_user: المستخدم المستهدف (إن وجد)
    @param details: تفاصيل إضافية
    """
    try:
        detail_str = f"Target:{target_user} | {details}" if target_user else details
        logOperation("admin", admin_id, f"Command:{command} | {detail_str}")
    
    except Exception as e:
        log_error(f"❌ خطأ في logAdminOperation: {str(e)}")


def logErrorWithDetails(error_type, error_message, user_id=None, context=None):
    """
    تسجيل خطأ مع تفاصيل كاملة
    Log error with full details
    
    @param error_type: نوع الخطأ
    @param error_message: رسالة الخطأ
    @param user_id: معرف المستخدم (إن وجد)
    @param context: سياق إضافي
    """
    try:
        user_str = f"User:{user_id}" if user_id else "System"
        context_str = f" | Context:{context}" if context else ""
        logOperation("error", user_str, f"{error_type}: {error_message}{context_str}")
    
    except Exception as e:
        log_error(f"❌ خطأ في logErrorWithDetails: {str(e)}")
