# -*- coding: utf-8 -*-
"""
نظام التسعير المتقدم
Advanced Pricing System
"""

import json
import os
from functions import log_error

# مسار ملف إعدادات التسعير
PRICING_FILE = "pricing_config.json"


def getPricingConfig():
    """
    قراءة إعدادات التسعير من الملف
    Read pricing configuration from file
    
    @return: dict - إعدادات التسعير
    """
    try:
        if os.path.exists(PRICING_FILE):
            with open(PRICING_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        else:
            # إعدادات افتراضية
            default_config = {
                "type": "percent",  # percent أو fixed
                "value": 50  # النسبة المئوية أو المبلغ الثابت
            }
            savePricingConfig(default_config)
            log_error("✅ تم إنشاء ملف إعدادات التسعير الافتراضية")
            return default_config
    
    except Exception as e:
        log_error(f"❌ خطأ في getPricingConfig: {str(e)}")
        return {"type": "percent", "value": 50}


def savePricingConfig(config):
    """
    حفظ إعدادات التسعير في الملف
    Save pricing configuration to file
    
    @param config: dict - إعدادات التسعير
    """
    try:
        with open(PRICING_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    except Exception as e:
        log_error(f"❌ خطأ في savePricingConfig: {str(e)}")


def calculatePrice(base_price):
    """
    حساب السعر النهائي بناءً على إعدادات التسعير
    Calculate final price based on pricing configuration
    
    @param base_price: السعر الأصلي من API
    @return: float - السعر النهائي بعد تطبيق التسعير
    """
    try:
        config = getPricingConfig()
        pricing_type = config.get("type", "percent")
        value = float(config.get("value", 0))
        
        if pricing_type == "percent":
            # تسعير نسبي: السعر الأصلي + (السعر الأصلي * النسبة / 100)
            final_price = base_price + (base_price * value / 100)
        elif pricing_type == "fixed":
            # تسعير ثابت: السعر الأصلي + المبلغ الثابت
            final_price = base_price + value
        else:
            # في حالة وجود نوع غير معروف، استخدم النسبة الافتراضية
            log_error(f"⚠️ نوع تسعير غير معروف: {pricing_type}، استخدام percent")
            final_price = base_price + (base_price * 50 / 100)
        
        return round(final_price, 6)
    
    except Exception as e:
        log_error(f"❌ خطأ في calculatePrice: {str(e)}")
        return base_price  # إرجاع السعر الأصلي في حالة الخطأ


def setPercentPricing(percent_value):
    """
    تعيين التسعير كنسبة مئوية
    Set pricing as percentage
    
    @param percent_value: النسبة المئوية
    @return: bool - True إذا نجحت العملية
    """
    try:
        percent_value = float(percent_value)
        if percent_value < 0:
            log_error(f"❌ محاولة تعيين نسبة سالبة: {percent_value}")
            return False
        
        config = {
            "type": "percent",
            "value": percent_value
        }
        
        savePricingConfig(config)
        log_error(f"✅ تم تعيين التسعير إلى نسبة مئوية: {percent_value}%")
        return True
    
    except Exception as e:
        log_error(f"❌ خطأ في setPercentPricing: {str(e)}")
        return False


def setFixedPricing(fixed_value):
    """
    تعيين التسعير كمبلغ ثابت
    Set pricing as fixed amount
    
    @param fixed_value: المبلغ الثابت
    @return: bool - True إذا نجحت العملية
    """
    try:
        fixed_value = float(fixed_value)
        if fixed_value < 0:
            log_error(f"❌ محاولة تعيين مبلغ سالب: {fixed_value}")
            return False
        
        config = {
            "type": "fixed",
            "value": fixed_value
        }
        
        savePricingConfig(config)
        log_error(f"✅ تم تعيين التسعير إلى مبلغ ثابت: {fixed_value}$")
        return True
    
    except Exception as e:
        log_error(f"❌ خطأ في setFixedPricing: {str(e)}")
        return False


def getPricingInfo():
    """
    الحصول على معلومات التسعير الحالية بشكل نصي
    Get current pricing info as text
    
    @return: str - معلومات التسعير
    """
    try:
        config = getPricingConfig()
        pricing_type = config.get("type", "percent")
        value = config.get("value", 0)
        
        if pricing_type == "percent":
            return f"📊 <b>نظام التسعير الحالي:</b>\n\n📌 النوع: نسبة مئوية\n📌 القيمة: {value}%\n\n💡 يتم إضافة {value}% على السعر الأصلي"
        elif pricing_type == "fixed":
            return f"📊 <b>نظام التسعير الحالي:</b>\n\n📌 النوع: مبلغ ثابت\n📌 القيمة: {value}$\n\n💡 يتم إضافة {value}$ على السعر الأصلي"
        else:
            return "❌ نظام تسعير غير معروف"
    
    except Exception as e:
        log_error(f"❌ خطأ في getPricingInfo: {str(e)}")
        return "❌ خطأ في جلب معلومات التسعير"


def calculateOrderTotalPrice(base_rate, quantity):
    """
    حساب السعر الإجمالي للطلب بناءً على الكمية والسعر
    Calculate total order price based on quantity and rate
    
    @param base_rate: السعر لكل 1000 من API
    @param quantity: الكمية المطلوبة
    @return: dict - معلومات السعر التفصيلية
    """
    try:
        # حساب السعر الأصلي للطلب
        original_price = (base_rate * quantity) / 1000
        
        # حساب السعر النهائي بعد تطبيق التسعير
        final_price = calculatePrice(original_price)
        
        return {
            "original_price": round(original_price, 6),
            "final_price": round(final_price, 6),
            "quantity": quantity,
            "rate_per_1000": base_rate
        }
    
    except Exception as e:
        log_error(f"❌ خطأ في calculateOrderTotalPrice: {str(e)}")
        return {
            "original_price": 0,
            "final_price": 0,
            "quantity": quantity,
            "rate_per_1000": base_rate
        }
