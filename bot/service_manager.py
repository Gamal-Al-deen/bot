# -*- coding: utf-8 -*-
"""
نظام إدارة الخدمات والأقسام
Service & Category Management System
"""

import json
import os
from functions import log_error

# مسار ملف بيانات الخدمات
SERVICES_FILE = "services_config.json"


def getServicesConfig():
    """
    الحصول على إعدادات الخدمات والأقسام
    Get services and categories configuration
    
    @return: dict - إعدادات الخدمات
    """
    try:
        if os.path.exists(SERVICES_FILE):
            with open(SERVICES_FILE, 'r', encoding='utf-8') as f:
                config = json.load(f)
                return config
        else:
            # إعدادات افتراضية - بدون أقسام أو خدمات
            default_config = {
                "categories": [],
                "services": {}
            }
            saveServicesConfig(default_config)
            return default_config
    
    except Exception as e:
        log_error(f"❌ خطأ في getServicesConfig: {str(e)}")
        return {"categories": [], "services": {}}


def saveServicesConfig(config):
    """
    حفظ إعدادات الخدمات والأقسام
    Save services and categories configuration
    
    @param config: dict - إعدادات الخدمات
    """
    try:
        with open(SERVICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=4, ensure_ascii=False)
    
    except Exception as e:
        log_error(f"❌ خطأ في saveServicesConfig: {str(e)}")


def getAllCategories():
    """
    الحصول على جميع الأقسام
    Get all categories
    
    @return: list - قائمة الأقسام
    """
    try:
        config = getServicesConfig()
        return config.get("categories", [])
    
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
        config = getServicesConfig()
        categories = config.get("categories", [])
        
        # التحقق من عدم وجود القسم مسبقاً
        if category_name in categories:
            log_error(f"⚠️ القسم '{category_name}' موجود بالفعل")
            return False
        
        categories.append(category_name)
        config["categories"] = categories
        
        # تهيئة القسم في services إذا لم يكن موجوداً
        if category_name not in config["services"]:
            config["services"][category_name] = []
        
        saveServicesConfig(config)
        log_error(f"✅ تم إضافة قسم جديد: {category_name}")
        return True
    
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
        config = getServicesConfig()
        categories = config.get("categories", [])
        
        # التحقق من وجود القسم
        if category_name not in categories:
            log_error(f"⚠️ القسم '{category_name}' غير موجود")
            return False
        
        # حذف القسم من القائمة
        categories.remove(category_name)
        config["categories"] = categories
        
        # حذف خدمات القسم
        if category_name in config["services"]:
            del config["services"][category_name]
        
        saveServicesConfig(config)
        log_error(f"✅ تم حذف القسم: {category_name}")
        return True
    
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
        config = getServicesConfig()
        categories = config.get("categories", [])
        
        # التحقق من وجود القسم
        if category_name not in categories:
            log_error(f"⚠️ القسم '{category_name}' غير موجود")
            return False
        
        # تهيئة القسم إذا لم يكن موجوداً في services
        if category_name not in config["services"]:
            config["services"][category_name] = []
        
        services_list = config["services"][category_name]
        
        # التحقق من عدم وجود الخدمة مسبقاً
        for service in services_list:
            if str(service.get("service_id")) == str(service_id):
                log_error(f"⚠️ الخدمة {service_id} موجودة بالفعل في القسم '{category_name}'")
                return False
        
        # إضافة الخدمة
        services_list.append({
            "service_id": service_id,
            "service_name": service_name
        })
        
        config["services"][category_name] = services_list
        saveServicesConfig(config)
        
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
        config = getServicesConfig()
        
        # التحقق من وجود القسم
        if category_name not in config["services"]:
            log_error(f"⚠️ القسم '{category_name}' غير موجود")
            return False
        
        services_list = config["services"][category_name]
        
        # البحث عن الخدمة وحذفها
        original_count = len(services_list)
        services_list = [s for s in services_list if str(s.get("service_id")) != str(service_id)]
        
        if len(services_list) == original_count:
            log_error(f"⚠️ الخدمة {service_id} غير موجودة في القسم '{category_name}'")
            return False
        
        config["services"][category_name] = services_list
        saveServicesConfig(config)
        
        log_error(f"✅ تم حذف الخدمة {service_id} من القسم '{category_name}'")
        return True
    
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
        config = getServicesConfig()
        return config.get("services", {}).get(category_name, [])
    
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
        config = getServicesConfig()
        services_dict = config.get("services", {})
        
        all_services = []
        for category_name, services_list in services_dict.items():
            for service in services_list:
                all_services.append({
                    "category": category_name,
                    "service_id": service.get("service_id"),
                    "service_name": service.get("service_name")
                })
        
        return all_services
    
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
        config = getServicesConfig()
        services_dict = config.get("services", {})
        
        for category_name, services_list in services_dict.items():
            for service in services_list:
                if str(service.get("service_id")) == str(service_id):
                    return {
                        "category": category_name,
                        "service_id": service.get("service_id"),
                        "service_name": service.get("service_name")
                    }
        
        return None
    
    except Exception as e:
        log_error(f"❌ خطأ في getServiceInfo: {str(e)}")
        return None
