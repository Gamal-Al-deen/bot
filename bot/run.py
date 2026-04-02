# -*- coding: utf-8 -*-
"""
نقطة التشغيل الرئيسية للبوت - نظام Long Polling مع خادم ويب لـ Render
Main bot entry point - Long Polling System with Web Server for Render

⚠️ تأكد من تشغيل البوت بشكل مستمر على Render
⚠️ Make sure to run the bot continuously on Render
"""

import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
from config import BOT_TOKEN, TELEGRAM_API_URL
from bot import handle_update
from functions import log_error


# ثوابت النظام
OFFSET_FILE = 'offset.txt'
LOG_FILE = 'log.txt'
POLLING_TIMEOUT = 30  # Timeout طويل للحصول على تحديثات
SLEEP_TIME = 2  # وقت الانتظار بين الطلبات
PORT = int(os.environ.get('PORT', 8080))  # منفذ Render


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


def health_check_handler():
    """
    معالج طلب الصحة - للحفاظ على البوت نشطاً
    Health check handler - Keep the bot alive
    """
    class HealthHandler(BaseHTTPRequestHandler):
        def do_GET(self):
            if self.path == '/':
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                message = """
                <html>
                <head><title>SMM Bot is Running</title></head>
                <body>
                    <h1>✅ SMM Bot is Running!</h1>
                    <p>The bot is working perfectly using Long Polling.</p>
                    <p>No webhook needed - everything is handled automatically.</p>
                </body>
                </html>
                """
                self.wfile.write(message.encode())
            elif self.path == '/health':
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(b'{"status": "healthy", "bot": "running"}')
            else:
                self.send_response(404)
                self.end_headers()
        
        def log_message(self, format, *args):
            # كتم سجلات HTTP
            pass
    
    return HealthHandler


def start_web_server():
    """
    بدء خادم الويب البسيط لـ Render
    Start simple web server for Render
    
    ⚠️ هذا ضروري فقط لـ Render
    ⚠️ This is only needed for Render
    """
    try:
        server = HTTPServer(('0.0.0.0', PORT), health_check_handler())
        log_error(f"🌐 خادم الويب يعمل على المنفذ {PORT}")
        print(f"🌐 Web server running on port {PORT}")
        
        # تشغيل الخادم في خيط منفصل
        server_thread = threading.Thread(target=server.serve_forever, daemon=True)
        server_thread.start()
        
        log_error(f"✅ تم بدء خادم الويب بنجاح")
        return server
        
    except Exception as e:
        log_error(f"❌ خطأ في بدء خادم الويب: {str(e)}")
        print(f"❌ Error starting web server: {str(e)}")
        return None


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
    
    # 🌐 بدء خادم الويب لـ Render
    server = start_web_server()
    
    if not server:
        log_error("⚠️ فشل بدء خادم الويب، لكن البوت سيستمر")
        print("⚠️ Failed to start web server, but bot will continue")
    
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
            if server:
                server.shutdown()
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
    import os
    
    try:
        log_error("🎯 بدء بوت SMM...")
        print("🚀 Starting SMM Bot...")
        print(f"🌐 Running on port {os.environ.get('PORT', 8080)}")
        main_loop()
    except Exception as e:
        log_error(f"❌ خطأ فادح عند البدء: {str(e)}")
        print(f"حدث خطأ: {str(e)}")
        print("يرجى التحقق من الإعدادات والمحاولة مرة أخرى.")
