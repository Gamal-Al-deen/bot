# -*- coding: utf-8 -*-
"""
فئة API الخاصة بموقع SMM
SMM API Client Class
"""

import requests
from config import API_KEY, API_URL


class SMM_API:
    """
    فئة للتعامل مع API موقع SMM
    Class to handle SMM website API
    """
    
    def __init__(self):
        """
        تهيئة عميل API
        Initialize API client
        """
        self.api_url = API_URL
        self.api_key = API_KEY
    
    def _make_request(self, action, data=None):
        """
        دالة مساعدة لإرسال طلبات API
        Helper function to send API requests
        
        @param action: اسم الإجراء (action) في API
        @param data: البيانات الإضافية للإرسال
        @return: dict - نتيجة الطلب أو None في حالة الخطأ
        """
        try:
            # إعداد البيانات الأساسية
            payload = {
                'key': self.api_key,
                'action': action
            }
            
            # إضافة البيانات الإضافية إذا وجدت
            if data:
                payload.update(data)
            
            # إرسال الطلب POST
            response = requests.post(self.api_url, data=payload, timeout=30)
            response.raise_for_status()
            
            # تحليل الاستجابة JSON
            result = response.json()
            
            # التحقق من وجود خطأ
            if 'error' in result:
                print(f"❌ خطأ في API: {result['error']}")
                return None
            
            return result
            
        except requests.exceptions.RequestException as e:
            print(f"❌ خطأ في الاتصال: {str(e)}")
            return None
        except Exception as e:
            print(f"❌ خطأ غير متوقع: {str(e)}")
            return None
    
    def balance(self):
        """
        الحصول على الرصيد الحالي
        Get current balance
        
        @return: float - الرصيد أو None في حالة الخطأ
        """
        result = self._make_request('balance')
        
        if result and 'balance' in result:
            try:
                return float(result['balance'])
            except (ValueError, TypeError):
                return None
        
        return None
    
    def services(self):
        """
        الحصول على قائمة الخدمات
        Get list of available services
        
        @return: list - قائمة الخدمات أو قائمة فارغة في حالة الخطأ
        """
        result = self._make_request('services')
        
        if result and isinstance(result, list):
            return result
        
        return []
    
    def order(self, service_id, link, quantity):
        """
        تقديم طلب جديد
        Place a new order
        
        @param service_id: معرف الخدمة
        @param link: الرابط المطلوب
        @param quantity: الكمية
        @return: int - معرف الطلب أو None في حالة الخطأ
        """
        data = {
            'service': service_id,
            'link': link,
            'quantity': quantity
        }
        
        result = self._make_request('order', data)
        
        if result and 'order' in result:
            try:
                return int(result['order'])
            except (ValueError, TypeError):
                return None
        
        return None
    
    def status(self, order_id):
        """
        التحقق من حالة طلب
        Check order status
        
        @param order_id: معرف الطلب
        @return: dict - حالة الطلب أو None في حالة الخطأ
        """
        data = {
            'order_id': order_id
        }
        
        result = self._make_request('status', data)
        
        if result and isinstance(result, dict):
            return result
        
        return None


# ⚠️ يمكن تعديل هذه الفئة حسب احتياجاتك
# ⚠️ You can modify this class according to your needs
