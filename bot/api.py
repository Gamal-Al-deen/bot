# -*- coding: utf-8 -*-
"""
فئة API الخاصة بموقع SMM - مع حماية كاملة من الأعطال
SMM API Client Class - With full crash protection for Render
"""

import requests
import json
import time
from config import API_KEY, API_URL
from functions import log_error


class SMM_API:
    """
    فئة للتعامل مع API موقع SMM مع حماية كاملة
    Class to handle SMM website API with full crash protection
    """
    
    def __init__(self):
        """
        تهيئة عميل API مع Session لإعادة الاستخدام
        Initialize API client with Session for reuse
        """
        self.api_url = API_URL
        self.api_key = API_KEY
        
        # إنشاء Session لإعادة استخدام الاتصال (أفضل للأداء)
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'SMM-Bot/1.0',
            'Content-Type': 'application/x-www-form-urlencoded'
        })
        
        # إعدادات retry
        self.max_retries = 3
        self.retry_delay = 2  # ثواني
    
    def _make_request(self, action, data=None):
        """
        دالة مساعدة لإرسال طلبات API مع حماية كاملة و retry mechanism
        Helper function with full protection and retry mechanism
        
        @param action: اسم الإجراء (action) في API
        @param data: البيانات الإضافية للإرسال
        @return: dict - نتيجة الطلب أو None في حالة الخطأ
        """
        last_error = None
        
        for attempt in range(1, self.max_retries + 1):
            try:
                # إعداد البيانات الأساسية
                payload = {
                    'key': self.api_key,
                    'action': action
                }
                
                # إضافة البيانات الإضافية إذا وجدت
                if data:
                    payload.update(data)
                
                # 📝 Log: قبل إرسال الطلب (فقط في المحاولة الأولى)
                if attempt == 1:
                    log_error(f"🔍 API Request [{action}]:")
                    log_error(f"   URL: {self.api_url}")
                    log_error(f"   Payload: key={self.api_key[:10]}..., action={action}")
                
                # إرسال الطلب POST مع timeout قصير لمنع التعليق
                response = self.session.post(
                    self.api_url, 
                    data=payload, 
                    timeout=15  # Timeout أقصر لمنع Hanging على Render
                )
                
                # 📝 Log: استجابة HTTP (فقط في المحاولة الأولى)
                if attempt == 1:
                    log_error(f"📥 HTTP Status: {response.status_code}")
                
                # التحقق من نجاح الطلب HTTP
                response.raise_for_status()
                
                # تحليل الاستجابة JSON
                result = response.json()
                
                # 📝 Log: الاستجابة الكاملة (فقط في المحاولة الأولى)
                if attempt == 1:
                    log_error(f"📤 API Response: {json.dumps(result, ensure_ascii=False)[:300]}")
                
                # التحقق من وجود خطأ في استجابة API
                if 'error' in result:
                    error_msg = result['error']
                    log_error(f"❌ API Error: {error_msg}")
                    return None
                
                # ✅ نجح!
                if attempt > 1:
                    log_error(f"✅ نجحت المحاولة {attempt}/{self.max_retries}")
                
                return result
                
            except requests.exceptions.ConnectionError as e:
                last_error = f"ConnectionError: {str(e)}"
                log_error(f"⚠️  محاولة {attempt}/{self.max_retries} - خطأ اتصال: {str(e)[:100]}")
                
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * attempt  # Exponential backoff
                    log_error(f"😴 انتظار {wait_time}ث قبل إعادة المحاولة...")
                    time.sleep(wait_time)
                
            except requests.exceptions.Timeout as e:
                last_error = f"Timeout: {str(e)}"
                log_error(f"⚠️  محاولة {attempt}/{self.max_retries} - Timeout")
                
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * attempt
                    log_error(f"😴 انتظار {wait_time}ث قبل إعادة المحاولة...")
                    time.sleep(wait_time)
                
            except requests.exceptions.HTTPError as e:
                last_error = f"HTTP {response.status_code}"
                log_error(f"❌ HTTP Error {response.status_code}: {str(e)[:100]}")
                # لا نعيد المحاولة لأخطاء HTTP (4xx, 5xx) - المشكلة من السيرفر
                return None
                
            except requests.exceptions.RequestException as e:
                last_error = f"RequestException: {type(e).__name__}"
                log_error(f"❌ Request Error (محاولة {attempt}): {type(e).__name__}")
                
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * attempt
                    time.sleep(wait_time)
                
            except json.JSONDecodeError as e:
                last_error = "JSONDecodeError"
                log_error(f"❌ JSON Decode Error - الاستجابة ليست JSON صالح")
                try:
                    log_error(f"   Raw Response: {response.text[:300]}")
                except:
                    pass
                return None  # لا نعيد المحاولة لخطأ JSON
                
            except Exception as e:
                last_error = f"Unexpected {type(e).__name__}"
                log_error(f"❌ Unexpected Error (محاولة {attempt}): {type(e).__name__}: {str(e)[:100]}")
                
                if attempt < self.max_retries:
                    wait_time = self.retry_delay * attempt
                    time.sleep(wait_time)
        
        # ❌ فشلت جميع المحاولات
        log_error(f"❌ فشل نهائي بعد {self.max_retries} محاولات: {last_error}")
        return None
    
    def balance(self):
        """
        الحصول على الرصيد الحالي - محمي بالكامل
        Get current balance - Fully protected
        
        @return: float - الرصيد أو None في حالة الخطأ
        """
        try:
            log_error("💰 جاري جلب الرصيد...")
            result = self._make_request('balance')
            
            if result is None:
                log_error("❌ فشل جلب الرصيد - _make_request returned None")
                return None
            
            if 'balance' in result:
                try:
                    balance_value = float(result['balance'])
                    log_error(f"✅ الرصيد تم جلبه بنجاح: ${balance_value}")
                    return balance_value
                except (ValueError, TypeError) as e:
                    log_error(f"❌ خطأ في تحويل الرصيد: {type(e).__name__}")
                    return None
            else:
                log_error(f"❌ لا يوجد حقل 'balance' في الاستجابة")
                return None
        
        except Exception as e:
            # حماية نهائية - لن يسمح لهذا الاستثناء بالمرور
            log_error(f"❌ CRITICAL ERROR in balance(): {type(e).__name__}: {str(e)[:100]}")
            return None
    
    def services(self):
        """
        الحصول على قائمة الخدمات - محمي بالكامل
        Get list of available services - Fully protected
        
        @return: list - قائمة الخدمات أو قائمة فارغة في حالة الخطأ
        """
        try:
            log_error("📦 جاري جلب الخدمات...")
            result = self._make_request('services')
            
            if result is None:
                log_error("❌ فشل جلب الخدمات - _make_request returned None")
                return []
            
            if isinstance(result, list):
                log_error(f"✅ تم جلب {len(result)} خدمة بنجاح")
                return result
            else:
                log_error(f"❌ الاستجابة ليست قائمة: type={type(result).__name__}")
                return []
        
        except Exception as e:
            # حماية نهائية - لن يسمح لهذا الاستثناء بالمرور
            log_error(f"❌ CRITICAL ERROR in services(): {type(e).__name__}: {str(e)[:100]}")
            return []
    
    def order(self, service_id, link, quantity):
        """
        تقديم طلب جديد - محمي بالكامل
        Place a new order - Fully protected
        
        @param service_id: معرف الخدمة
        @param link: الرابط المطلوب
        @param quantity: الكمية
        @return: int - معرف الطلب أو None في حالة الخطأ
        """
        try:
            log_error(f"🛒 جاري تقديم طلب: service={service_id}, quantity={quantity}")
            
            data = {
                'service': service_id,
                'link': link,
                'quantity': quantity
            }
            
            result = self._make_request('order', data)
            
            if result is None:
                log_error("❌ فشل تقديم الطلب - _make_request returned None")
                return None
            
            if 'order' in result:
                try:
                    order_id = int(result['order'])
                    log_error(f"✅ تم تقديم الطلب بنجاح - Order ID: {order_id}")
                    return order_id
                except (ValueError, TypeError) as e:
                    log_error(f"❌ خطأ في تحويل Order ID: {type(e).__name__}")
                    return None
            else:
                log_error(f"❌ لا يوجد حقل 'order' في الاستجابة")
                return None
        
        except Exception as e:
            # حماية نهائية - لن يسمح لهذا الاستثناء بالمرور
            log_error(f"❌ CRITICAL ERROR in order(): {type(e).__name__}: {str(e)[:100]}")
            return None
    
    def status(self, order_id):
        """
        التحقق من حالة طلب - محمي بالكامل
        Check order status - Fully protected
        
        @param order_id: معرف الطلب
        @return: dict - حالة الطلب أو None في حالة الخطأ
        """
        try:
            log_error(f"📊 جاري فحص حالة الطلب: {order_id}")
            
            data = {
                'order_id': order_id
            }
            
            result = self._make_request('status', data)
            
            if result is None:
                log_error("❌ فشل فحص الحالة - _make_request returned None")
                return None
            
            if isinstance(result, dict):
                log_error(f"✅ تم جلب حالة الطلب بنجاح")
                return result
            else:
                log_error(f"❌ الاستجابة ليست dict: type={type(result).__name__}")
                return None
        
        except Exception as e:
            # حماية نهائية - لن يسمح لهذا الاستثناء بالمرور
            log_error(f"❌ CRITICAL ERROR in status(): {type(e).__name__}: {str(e)[:100]}")
            return None
    
    def health_check(self):
        """
        فحص صحة الاتصال بـ API
        Health check for API connection
        
        @return: bool - True إذا كان API متاح
        """
        try:
            log_error("🏥 جاري فحص صحة API...")
            result = self._make_request('balance')
            
            if result is not None:
                log_error("✅ API متاح ويعمل بشكل صحيح")
                return True
            else:
                log_error("⚠️  API غير متاح أو هناك مشكلة في الاتصال")
                return False
        
        except Exception as e:
            log_error(f"❌ Health check failed: {type(e).__name__}")
            return False
    
    def get_service_by_id(self, service_id):
        """
        الحصول على معلومات خدمة معينة حسب المعرف
        Get specific service information by ID
        
        @param service_id: معرف الخدمة
        @return: dict - معلومات الخدمة أو None
        """
        try:
            services = self.services()
            
            for service in services:
                if str(service.get('service')) == str(service_id):
                    log_error(f"✅ تم العثور على الخدمة: {service_id}")
                    return service
            
            log_error(f"❌ لم يتم العثور على الخدمة: {service_id}")
            return None
        
        except Exception as e:
            log_error(f"❌ خطأ في get_service_by_id: {str(e)}")
            return None
    
    def get_service_rate(self, service_id):
        """
        الحصول على سعر خدمة معينة
        Get service rate by ID
        
        @param service_id: معرف الخدمة
        @return: float - السعر لكل 1000 أو 0
        """
        try:
            service = self.get_service_by_id(service_id)
            
            if service:
                rate = float(service.get('rate', 0))
                log_error(f"💰 سعر الخدمة {service_id}: {rate}$")
                return rate
            else:
                return 0.0
        
        except Exception as e:
            log_error(f"❌ خطأ في get_service_rate: {str(e)}")
            return 0.0


# ⚠️ يمكن تعديل هذه الفئة حسب احتياجاتك
# ⚠️ You can modify this class according to your needs
