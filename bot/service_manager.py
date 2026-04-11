# -*- coding: utf-8 -*-
"""
نظام إدارة الخدمات والأقسام
Service & Category Management System

✅ Updated to use Supabase Database - No JSON!
"""

from functions import log_error
from database import (
    add_category as db_add_category,
    get_all_categories as db_get_all_categories,
    delete_category as db_delete_category,
    add_service as db_add_service,
    get_services_by_category as db_get_services_by_category,
    delete_service as db_delete_service
)


def getServicesConfig():
    """
    الحصول على إعدادات الخدمات والأقسام من Supabase
    Get services and categories configuration from Supabase
    
    @return: dict - إعدادات الخدمات
    """
    try:
        categories = db_get_all_categories()
        
        # Build config structure
        config = {
            "categories": [cat['name'] for cat in categories],
            "services": {},
            "categories_data": categories  # Keep full data with IDs
        }
        
        # Get services for each category
        for cat in categories:
            cat_id = cat['id']
            cat_name = cat['name']
            services = db_get_services_by_category(cat_id)
            config["services"][cat_name] = services
        
        log_error(f"📋 [GET_SERVICES_CONFIG] Retrieved {len(categories)} categories with services")
        return config
    
    except Exception as e:
        log_error(f"❌ خطأ في getServicesConfig: {str(e)}")
        import traceback
        log_error(f"📋 Full traceback:\n{traceback.format_exc()}")
        return {"categories": [], "services": {}, "categories_data": []}


def saveServicesConfig(config):
    """
    حفظ إعدادات الخدمات والأقسام
    NOTE: This is deprecated - data is saved directly via addCategory/addService
    
    @param config: dict - إعدادات الخدمات
    """
    log_error("⚠️ [DEPRECATED] saveServicesConfig called - data should be saved directly to Supabase")
    return False


def getAllCategories():
    """
    الحصول على جميع الأقسام من Supabase
    Get all categories from Supabase
    
    @return: list - قائمة الأقسام (أسماء فقط)
    """
    try:
        config = getServicesConfig()
        return config.get("categories", [])
    
    except Exception as e:
        log_error(f"❌ خطأ في getAllCategories: {str(e)}")
        return []


def getAllCategoriesData():
    """
    الحصول على جميع الأقسام مع البيانات الكاملة (IDs)
    Get all categories with full data including IDs
    
    @return: list - قائمة الأقسام (بيانات كاملة)
    """
    try:
        config = getServicesConfig()
        return config.get("categories_data", [])
    
    except Exception as e:
        log_error(f"❌ خطأ في getAllCategoriesData: {str(e)}")
        return []


def addCategory(category_name):
    """
    إضافة قسم جديد إلى Supabase
    Add a new category to Supabase
    
    @param category_name: اسم القسم
    @return: bool - True إذا تم الإضافة بنجاح
    """
    try:
        success = db_add_category(category_name)
        
        if success:
            log_error(f"✅ تم إضافة قسم جديد إلى Supabase: {category_name}")
        else:
            log_error(f"❌ فشل في إضافة القسم: {category_name}")
        
        return success
    
    except Exception as e:
        log_error(f"❌ خطأ في addCategory: {str(e)}")
        import traceback
        log_error(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False


def deleteCategory(category_name):
    """
    حذف قسم من Supabase
    Delete a category from Supabase
    
    @param category_name: اسم القسم
    @return: bool - True إذا تم الحذف بنجاح
    """
    try:
        # Get category ID first
        categories_data = getAllCategoriesData()
        category_id = None
        
        for cat in categories_data:
            if cat['name'] == category_name:
                category_id = cat['id']
                break
        
        if not category_id:
            log_error(f"❌ القسم '{category_name}' غير موجود")
            return False
        
        success = db_delete_category(category_id)
        
        if success:
            log_error(f"✅ تم حذف القسم: {category_name}")
        else:
            log_error(f"❌ فشل في حذف القسم: {category_name}")
        
        return success
    
    except Exception as e:
        log_error(f"❌ خطأ في deleteCategory: {str(e)}")
        import traceback
        log_error(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False


def addService(category_name, service_api_id):
    """
    إضافة خدمة جديدة إلى Supabase
    Add a new service to Supabase
    
    @param category_name: اسم القسم
    @param service_api_id: معرف الخدمة من API
    @return: bool - True إذا تم الإضافة بنجاح
    """
    try:
        # Get category ID first
        categories_data = getAllCategoriesData()
        category_id = None
        
        for cat in categories_data:
            if cat['name'] == category_name:
                category_id = cat['id']
                break
        
        if not category_id:
            log_error(f"❌ القسم '{category_name}' غير موجود")
            return False
        
        success = db_add_service(category_id, service_api_id)
        
        if success:
            log_error(f"✅ تم إضافة خدمة {service_api_id} إلى القسم '{category_name}' في Supabase")
        else:
            log_error(f"❌ فشل في إضافة الخدمة {service_api_id}")
        
        return success
    
    except Exception as e:
        log_error(f"❌ خطأ في addService: {str(e)}")
        import traceback
        log_error(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False


def deleteService(category_name, service_api_id):
    """
    حذف خدمة من Supabase
    Delete a service from Supabase
    
    @param category_name: اسم القسم
    @param service_api_id: معرف الخدمة من API
    @return: bool - True إذا تم الحذف بنجاح
    """
    try:
        # Get category ID first
        categories_data = getAllCategoriesData()
        category_id = None
        
        for cat in categories_data:
            if cat['name'] == category_name:
                category_id = cat['id']
                break
        
        if not category_id:
            log_error(f"❌ القسم '{category_name}' غير موجود")
            return False
        
        # Get services to find the service ID
        services = db_get_services_by_category(category_id)
        service_id = None
        
        for svc in services:
            if svc['service_api_id'] == service_api_id:
                service_id = svc['id']
                break
        
        if not service_id:
            log_error(f"❌ الخدمة {service_api_id} غير موجودة في القسم '{category_name}'")
            return False
        
        success = db_delete_service(service_id)
        
        if success:
            log_error(f"✅ تم حذف الخدمة {service_api_id} من القسم '{category_name}'")
        else:
            log_error(f"❌ فشل في حذف الخدمة {service_api_id}")
        
        return success
    
    except Exception as e:
        log_error(f"❌ خطأ في deleteService: {str(e)}")
        import traceback
        log_error(f"📋 Full traceback:\n{traceback.format_exc()}")
        return False


def getServicesByCategory(category_name):
    """
    الحصول على خدمات قسم معين
    Get services for a specific category
    
    @param category_name: اسم القسم
    @return: list - قائمة الخدمات
    """
    try:
        config = getServicesConfig()
        return config.get("services", {}).get(category_name, [])
    
    except Exception as e:
        log_error(f"❌ خطأ في getServicesByCategory: {str(e)}")
        return []
