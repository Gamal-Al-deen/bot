# -*- coding: utf-8 -*-
"""
نظام التسعير المتقدم - Supabase
Advanced Pricing System - Supabase Version with Per-Service Pricing
"""

from database import (
    get_pricing_rule,
    set_pricing_rule,
    calculate_final_price,
    get_service_by_api_id
)
from functions import log_error


def calculatePrice(base_price, service_api_id=None):
    """
    حساب السعر النهائي بناءً على إعدادات التسعير
    Calculate final price based on pricing configuration
    
    @param base_price: السعر الأصلي من API (لـ 1000)
    @param service_api_id: معرف الخدمة من API (اختياري)
    @return: float - السعر النهائي بعد تطبيق التسعير
    """
    try:
        if service_api_id is None:
            # If no service ID provided, use default percentage (50%)
            final_price = base_price + (base_price * 50 / 100)
            return round(final_price, 6)
        
        # Get pricing rule for this service
        pricing_rule = get_pricing_rule(service_api_id)
        
        if pricing_rule['pricing_type'] == 'fixed' and pricing_rule.get('price_value'):
            # Fixed pricing: price_value per 1000
            final_price = pricing_rule['price_value']
        else:
            # Percentage pricing
            percentage = pricing_rule.get('percentage_value', 50.0)
            final_price = base_price + (base_price * percentage / 100)
        
        return round(final_price, 6)
    
    except Exception as e:
        log_error(f"❌ خطأ في calculatePrice: {str(e)}")
        return base_price


def setPercentPricing(service_id, percent_value):
    """
    تعيين التسعير كنسبة مئوية لخدمة معينة
    Set pricing as percentage for a specific service
    
    @param service_id: معرف الخدمة (من قاعدة البيانات)
    @param percent_value: النسبة المئوية
    @return: bool - True إذا نجحت العملية
    """
    try:
        percent_value = float(percent_value)
        if percent_value < 0:
            log_error(f"❌ محاولة تعيين نسبة سالبة: {percent_value}")
            return False
        
        result = set_pricing_rule(service_id, 'percentage', percentage_value=percent_value)
        
        if result:
            log_error(f"✅ تم تعيين التسعير إلى نسبة مئوية: {percent_value}% للخدمة {service_id}")
        
        return result
    
    except Exception as e:
        log_error(f"❌ خطأ في setPercentPricing: {str(e)}")
        return False


def setFixedPricing(service_id, fixed_value):
    """
    تعيين التسعير كمبلغ ثابت لخدمة معينة
    Set pricing as fixed amount for a specific service
    
    @param service_id: معرف الخدمة (من قاعدة البيانات)
    @param fixed_value: المبلغ الثابت (لكل 1000)
    @return: bool - True إذا نجحت العملية
    """
    try:
        fixed_value = float(fixed_value)
        if fixed_value < 0:
            log_error(f"❌ محاولة تعيين مبلغ سالب: {fixed_value}")
            return False
        
        result = set_pricing_rule(service_id, 'fixed', price_value=fixed_value)
        
        if result:
            log_error(f"✅ تم تعيين التسعير إلى مبلغ ثابت: {fixed_value}$ للخدمة {service_id}")
        
        return result
    
    except Exception as e:
        log_error(f"❌ خطأ في setFixedPricing: {str(e)}")
        return False


def getPricingInfo(service_api_id=None):
    """
    الحصول على معلومات التسعير الحالية بشكل نصي
    Get current pricing info as text
    
    @param service_api_id: معرف الخدمة (اختياري)
    @return: str - معلومات التسعير
    """
    try:
        if service_api_id is None:
            return "📊 <b>نظام التسعير:</b>\n\nيتم استخدام تسعير لكل خدمة بشكل منفصل.\n\n💡 اختر خدمة لعرض تسعيرها."
        
        # Get service info
        service = get_service_by_api_id(service_api_id)
        
        if not service:
            return f"❌ الخدمة {service_api_id} غير موجودة"
        
        # Get pricing rule
        pricing_rule = get_pricing_rule(service['id'])
        
        if pricing_rule['pricing_type'] == 'fixed':
            value = pricing_rule.get('price_value', 0)
            return f"📊 <b>نظام التسعير للخدمة {service_api_id}:</b>\n\n📌 النوع: مبلغ ثابت\n📌 القيمة: {value}$ لكل 1000\n\n💡 يتم تطبيق سعر ثابت على كل 1000 عنصر"
        else:
            value = pricing_rule.get('percentage_value', 50.0)
            return f"📊 <b>نظام التسعير للخدمة {service_api_id}:</b>\n\n📌 النوع: نسبة مئوية\n📌 القيمة: {value}%\n\n💡 يتم إضافة {value}% على السعر الأصلي"
    
    except Exception as e:
        log_error(f"❌ خطأ في getPricingInfo: {str(e)}")
        return "❌ خطأ في جلب معلومات التسعير"


def calculateOrderTotalPrice(base_rate, quantity, service_api_id=None):
    """
    حساب السعر الإجمالي للطلب بناءً على الكمية والسعر
    Calculate total order price based on quantity and rate
    
    @param base_rate: السعر لكل 1000 من API
    @param quantity: الكمية المطلوبة
    @param service_api_id: معرف الخدمة (اختياري)
    @return: dict - معلومات السعر التفصيلية
    """
    try:
        if service_api_id is None:
            # Fallback to old behavior (percentage 50%)
            original_price = (base_rate * quantity) / 1000
            final_price = original_price + (original_price * 50 / 100)
            
            return {
                "original_price": round(original_price, 6),
                "final_price": round(final_price, 6),
                "quantity": quantity,
                "rate_per_1000": base_rate
            }
        
        # Use per-service pricing
        # First, we need to get the service database ID
        service = get_service_by_api_id(service_api_id)
        
        if not service:
            # Service not in database, use default percentage
            original_price = (base_rate * quantity) / 1000
            final_price = original_price + (original_price * 50 / 100)
            
            return {
                "original_price": round(original_price, 6),
                "final_price": round(final_price, 6),
                "quantity": quantity,
                "rate_per_1000": base_rate
            }
        
        # Calculate with per-service pricing
        price_info = calculate_final_price(service['id'], base_rate, quantity)
        
        return {
            "original_price": price_info['original_price'],
            "final_price": price_info['final_price'],
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
