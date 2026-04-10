# -*- coding: utf-8 -*-
"""
نظام إدارة الخدمات والأقسام - Supabase
Service & Category Management System - Supabase Version
"""

from database import (
    create_category,
    get_all_categories,
    get_category_by_name,
    delete_category,
    add_service,
    get_services_by_category,
    delete_service,
    get_all_services_flat,
    get_service_by_api_id,
    set_pricing_rule
)
from functions import log_error


def getAllCategories():
    """
    الحصول على جميع الأقسام
    Get all categories
    
    @return: list - قائمة الأقسام
    """
    try:
        categories = get_all_categories()
        # Return only category names for backward compatibility
        return [cat['name'] for cat in categories]
    
    except Exception as e:
        log_error(f"❌ خطأ في getAllCategories: {str(e)}")
        return []


def addCategory(category_name):
    """
    إضافة قسم جديد
    Add a new category
    
    @param category_name: اسم القسم
    @return: bool - True إذا تم الإضافة بنجاح
    """
    try:
        return create_category(category_name)
    
    except Exception as e:
        log_error(f"❌ خطأ في addCategory: {str(e)}")
        return False


def deleteCategory(category_name):
    """
    حذف قسم وجميع خدماته
    Delete a category and all its services
    
    @param category_name: اسم القسم
    @return: bool - True إذا تم الحذف بنجاح
    """
    try:
        category = get_category_by_name(category_name)
        
        if not category:
            log_error(f"⚠️ القسم '{category_name}' غير موجود")
            return False
        
        return delete_category(category['id'])
    
    except Exception as e:
        log_error(f"❌ خطأ في deleteCategory: {str(e)}")
        return False


def addServiceToCategory(category_name, service_id, service_name):
    """
    إضافة خدمة إلى قسم معين
    Add a service to a specific category
    
    @param category_name: اسم القسم
    @param service_id: معرف الخدمة من API
    @param service_name: اسم الخدمة
    @return: bool - True إذا تم الإضافة بنجاح
    """
    try:
        category = get_category_by_name(category_name)
        
        if not category:
            log_error(f"⚠️ القسم '{category_name}' غير موجود")
            return False
        
        # Add service
        service_db_id = add_service(category['id'], service_id)
        
        if service_db_id is None:
            return False
        
        # Set default pricing (percentage 50%)
        set_pricing_rule(service_db_id, 'percentage', percentage_value=50.0)
        
        log_error(f"✅ تم إضافة خدمة {service_id} ({service_name}) إلى القسم '{category_name}'")
        return True
    
    except Exception as e:
        log_error(f"❌ خطأ في addServiceToCategory: {str(e)}")
        return False


def deleteServiceFromCategory(category_name, service_id):
    """
    حذف خدمة من قسم معين
    Delete a service from a specific category
    
    @param category_name: اسم القسم
    @param service_id: معرف الخدمة
    @return: bool - True إذا تم الحذف بنجاح
    """
    try:
        # Find the service
        services = get_all_services_flat()
        
        for service in services:
            if service['category_name'] == category_name and service['service_api_id'] == service_id:
                return delete_service(service['id'])
        
        log_error(f"⚠️ الخدمة {service_id} غير موجودة في القسم '{category_name}'")
        return False
    
    except Exception as e:
        log_error(f"❌ خطأ في deleteServiceFromCategory: {str(e)}")
        return False


def getServicesByCategory(category_name):
    """
    الحصول على خدمات قسم معين
    Get services for a specific category
    
    @param category_name: اسم القسم
    @return: list - قائمة الخدمات
    """
    try:
        category = get_category_by_name(category_name)
        
        if not category:
            return []
        
        services = get_services_by_category(category['id'])
        
        # Format for backward compatibility
        result = []
        for service in services:
            result.append({
                'service_id': service['service_api_id'],
                'service_name': f"Service {service['service_api_id']}"  # Name will be fetched from API
            })
        
        return result
    
    except Exception as e:
        log_error(f"❌ خطأ في getServicesByCategory: {str(e)}")
        return []


def getAllServicesFlat():
    """
    الحصول على جميع الخدمات في قائمة مسطحة
    Get all services in a flat list
    
    @return: list - قائمة جميع الخدمات مع أسماء أقسامها
    """
    try:
        services = get_all_services_flat()
        
        result = []
        for service in services:
            result.append({
                "category": service['category_name'],
                "service_id": service['service_api_id'],
                "service_name": f"Service {service['service_api_id']}"
            })
        
        return result
    
    except Exception as e:
        log_error(f"❌ خطأ في getAllServicesFlat: {str(e)}")
        return []


def getServiceInfo(service_id):
    """
    الحصول على معلومات خدمة معينة
    Get information about a specific service
    
    @param service_id: معرف الخدمة
    @return: dict - معلومات الخدمة أو None
    """
    try:
        service = get_service_by_api_id(service_id)
        
        if service:
            return {
                "category": service['category_name'],
                "service_id": service['service_api_id'],
                "service_name": f"Service {service['service_api_id']}"
            }
        
        return None
    
    except Exception as e:
        log_error(f"❌ خطأ في getServiceInfo: {str(e)}")
        return None
