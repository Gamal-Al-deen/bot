# -*- coding: utf-8 -*-
"""
نظام إدارة الخدمات والأقسام — التخزين في Supabase فقط (بدون ملفات محلية).
Service & Category Management — Supabase-backed persistence.
"""

from functions import log_error
from database import (
    list_category_names,
    insert_category,
    delete_category_by_name,
    insert_service_in_category,
    delete_service_in_category,
    select_services_for_category,
    select_all_services_flat,
    lookup_service_by_api_id,
)


def getServicesConfig():
    """
    توافق خلفي: يعيد هيكلاً يشبه ملف JSON القديم (للقراءة فقط من Supabase).
    """
    try:
        categories = list_category_names()
        services = {}
        for cat in categories:
            services[cat] = select_services_for_category(cat)
        return {"categories": categories, "services": services}
    except Exception as e:
        log_error(f"❌ خطأ في getServicesConfig: {str(e)}")
        return {"categories": [], "services": {}}


def saveServicesConfig(config):
    """
    توافق خلفي: لا يُستخدم للكتابة المباشرة؛ الأقسام/الخدمات تُدار عبر دوال CRUD.
    """
    log_error("ℹ️ saveServicesConfig: مُهمل — استخدم addCategory / addServiceToCategory إلخ (Supabase).")


def getAllCategories():
    try:
        return list_category_names()
    except Exception as e:
        log_error(f"❌ خطأ في getAllCategories: {str(e)}")
        return []


def addCategory(category_name):
    try:
        return insert_category(category_name)
    except Exception as e:
        log_error(f"❌ خطأ في addCategory: {str(e)}")
        return False


def deleteCategory(category_name):
    try:
        return delete_category_by_name(category_name)
    except Exception as e:
        log_error(f"❌ خطأ في deleteCategory: {str(e)}")
        return False


def addServiceToCategory(category_name, service_id, service_name):
    try:
        return insert_service_in_category(category_name, service_id, service_name)
    except Exception as e:
        log_error(f"❌ خطأ في addServiceToCategory: {str(e)}")
        return False


def deleteServiceFromCategory(category_name, service_id):
    try:
        return delete_service_in_category(category_name, service_id)
    except Exception as e:
        log_error(f"❌ خطأ في deleteServiceFromCategory: {str(e)}")
        return False


def getServicesByCategory(category_name):
    try:
        return select_services_for_category(category_name)
    except Exception as e:
        log_error(f"❌ خطأ في getServicesByCategory: {str(e)}")
        return []


def getAllServicesFlat():
    try:
        return select_all_services_flat()
    except Exception as e:
        log_error(f"❌ خطأ في getAllServicesFlat: {str(e)}")
        return []


def getServiceInfo(service_id):
    try:
        return lookup_service_by_api_id(service_id)
    except Exception as e:
        log_error(f"❌ خطأ في getServiceInfo: {str(e)}")
        return None
