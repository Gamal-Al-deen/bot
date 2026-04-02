# -*- coding: utf-8 -*-
"""
نقطة التشغيل الرئيسية للبوت - نظام Long Polling
Main bot entry point - Long Polling System

⚠️ تأكد من تشغيل البوت بشكل مستمر على Render
⚠️ Make sure to run the bot continuously on Render
"""

import time
import requests
from config import BOT_TOKEN, TELEGRAM_API_URL
from bot import handle_update
from functions import log_error


# ثوابت النظام
OFFSET_FILE = 'offset.txt'
LOG_FILE = 'log.txt'
POLLING_TIMEOUT = 30  # Timeout طويل للحصول على تحديثات
SLEEP_TIME = 2  # وقت الانتظار بين الطلبات


def read_offset():
    """
    قراءة آخر offset من الملف
    Read last offset from file
    
    @return: int - قيمة offset أو 0 إذا لم يوجد الملف
    """
    try:
        with open(OFFSET_FILE, 'r', encoding='utf-8') as f:
            content = f.read().strip()
            if content:
                return int(content)
    except FileNotFoundError:
        # إنشاء الملف إذا لم يوجد
        write_offset(0)
    except Exception as e:
        log_error(f"❌ خطأ في قراءة offset: {str(e)}")
    
    return 0


def write_offset(offset):
    """
    كتابة offset جديد في الملف
    Write new offset to file
    
    @param offset: القيمة الجديدة
    """
    try:
        with open(OFFSET_FILE, 'w', encoding='utf-8') as f:
            f.write(str(offset))
    except Exception as e:
        log_error(f"❌ خطأ في كتابة offset: {str(e)}")


def get_updates(offset, timeout=POLLING_TIMEOUT):
    """
    جلب التحديثات من Telegram API
    Get updates from Telegram API
    
    @param offset: بداية التحديثات المطلوبة
    @param timeout: وقت الانتظار الأقصى للاستجابة
    @return: list - قائمة التحديثات أو قائمة فارغة
    """
    try:
        url = f"{TELEGRAM_API_URL}{BOT_TOKEN}/getUpdates"
        
        params = {
            'offset': offset,
            'timeout': timeout,
            'allowed_updates': ['message', 'callback_query']
        }
        
        response = requests.get(url, params=params, timeout=timeout + 5)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get('ok'):
            return result.get('result', [])
        else:
            error_desc = result.get('description', 'خطأ غير معروف')
            log_error(f"❌ خطأ في getUpdates: {error_desc}")
            return []
    
    except requests.exceptions.Timeout:
        # هذا طبيعي - timeout بعد وقت الانتظار
        return []
    except requests.exceptions.RequestException as e:
        log_error(f"❌ خطأ في الاتصال: {str(e)}")
        return []
    except Exception as e:
        log_error(f"❌ خطأ غير متوقع في getUpdates: {str(e)}")
        return []


def process_updates(updates):
    """
    معالجة قائمة التحديثات
    Process list of updates
    
    @param updates: list - قائمة التحديثات
    """
    if not updates:
        return
    
    for update in updates:
        try:
            # معالجة كل تحديث
            handle_update(update)
            
            # استخراج update_id لتحديث offset
            update_id = update.get('update_id')
            
            if update_id is not None:
                # تحديث offset لمنع تلقي نفس الرسالة مرة أخرى
                new_offset = update_id + 1
                write_offset(new_offset)
        
        except Exception as e:
            log_error(f"❌ خطأ أثناء معالجة update: {str(e)}")
            # الاستمرار في معالجة التحديثات الأخرى


def main_loop():
    """
    الحلقة الرئيسية للبوت - لا تتوقف أبداً
    Main bot loop - Never stops
    
    ⚠️ هذا ضروري حتى لا يتوقف البوت
    ⚠️ This is essential so the bot doesn't stop
    """
    log_error("=" * 50)
    log_error("🚀 بدء تشغيل البوت...")
    log_error("=" * 50)
    
    # قراءة offset الابتدائي
    offset = read_offset()
    log_error(f"📍 Offset الابتدائي: {offset}")
    
    # عداد المحاولات لإعادة الاتصال في حالة الفشل المتكرر
    retry_count = 0
    max_retries = 10
    
    while True:
        try:
            # 🔄 جلب التحديثات
            updates = get_updates(offset)
            
            # ✅ معالجة التحديثات
            if updates:
                log_error(f"📨 تم استلام {len(updates)} تحديث(ات)")
                process_updates(updates)
                retry_count = 0  # إعادة تعيين العداد عند النجاح
            
            # 😴 انتظار قبل الطلب التالي
            time.sleep(SLEEP_TIME)
            
        except KeyboardInterrupt:
            log_error("⚠️ توقف البوت بواسطة المستخدم")
            break
        
        except Exception as e:
            log_error(f"❌ خطأ في الحلقة الرئيسية: {str(e)}")
            retry_count += 1
            
            # زيادة وقت الانتظار عند الفشل المتكرر
            if retry_count >= max_retries:
                log_error(f"⚠️ فشل متكرر ({retry_count} محاولات). انتظار أطول...")
                time.sleep(10)  # انتظار أطول
            else:
                time.sleep(SLEEP_TIME * 2)


if __name__ == '__main__':
    """
    نقطة بداية التشغيل
    Entry point
    
    ⚠️ تأكد من تشغيل هذا الملف لتشغيل البوت
    ⚠️ Make sure to run this file to start the bot
    """
    try:
        log_error("🎯 بدء بوت SMM...")
        main_loop()
    except Exception as e:
        log_error(f"❌ خطأ فادح عند البدء: {str(e)}")
        print(f"حدث خطأ: {str(e)}")
        print("يرجى التحقق من الإعدادات والمحاولة مرة أخرى.")
