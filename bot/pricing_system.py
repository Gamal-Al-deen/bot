# -*- coding: utf-8 -*-
"""
نظام التسعير المتقدم - محدث لاستخدام Supabase فقط
Advanced Pricing System - Updated to use Supabase only (no local JSON)
"""

from functions import log_error
from database import get_setting, set_setting


def getPricingConfig():
    """
    قراءة إعدادات التسعير من Supabase
    Read pricing configuration from Supabase
    
    @return: dict - إعدادات التسعير
    """
    try:
        pricing_type = get_setting('pricing_type', 'percent')
        pricing_value = float(get_setting('pricing_value', '50'))
        
        config = {
            "type": pricing_type,
            "value": pricing_value
        }
        
        log_error(f"✅ [PRICING] Loaded config from Supabase: type={pricing_type}, value={pricing_value}")
        return config
    
    except Exception as e:
        log_error(f"❌ خطأ في getPricingConfig: {str(e)}")
        return {"type": "percent", "value": 50}


def savePricingConfig(config):
    """
    حفظ إعدادات التسعير في Supabase
    Save pricing configuration to Supabase
    
    @param config: dict - إعدادات التسعير
    """
    try:
        pricing_type = config.get('type', 'percent')
        pricing_value = str(config.get('value', 50))
        
        set_setting('pricing_type', pricing_type)
        set_setting('pricing_value', pricing_value)
        
        log_error(f"✅ [PRICING] Saved config to Supabase: type={pricing_type}, value={pricing_value}")
    
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
