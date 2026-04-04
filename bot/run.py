# -*- coding: utf-8 -*-
"""
نقطة التشغيل الرئيسية للبوت - Flask Webhook Server
Main bot entry point - Flask Webhook Server for Render

⚠️ تم استبدال Long Polling بـ Webhook للتوافق مع Render
⚠️ Replaced Long Polling with Webhook for Render compatibility
"""

from flask import Flask, request
import os
import requests
from config import BOT_TOKEN
from bot import handle_update
from functions import log_error


# إنشاء تطبيق Flask
app = Flask(__name__)


def setup_webhook():
    """
    إعداد Webhook تلقائياً عند بدء التشغيل
    Automatically setup webhook on startup
    
    @return: bool - True إذا نجح الإعداد
    """
    try:
        # الحصول على URL من متغيرات البيئة (Render)
        render_url = os.environ.get('RENDER_EXTERNAL_URL', '')
        
        if not render_url:
            # Fallback للتشغيل المحلي
            port = os.environ.get('PORT', 10000)
            render_url = f"http://localhost:{port}"
            log_error("⚠️  RENDER_EXTERNAL_URL غير موجود - وضع محلي")
        
        # بناء رابط webhook
        webhook_url = f"{render_url}/webhook"
        
        log_error("=" * 60)
        log_error("🔗 إعداد Webhook...")
        log_error(f"   Render URL: {render_url}")
        log_error(f"   Webhook URL: {webhook_url}")
        log_error("=" * 60)
        
        # 1️⃣ حذف Webhook القديم أولاً
        log_error("🗑️  جاري حذف Webhook القديم...")
        delete_response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/deleteWebhook",
            timeout=10
        )
        
        if delete_response.status_code == 200:
            delete_result = delete_response.json()
            if delete_result.get('ok'):
                log_error("✅ تم حذف Webhook القديم بنجاح")
            else:
                log_error(f"⚠️  تحذير عند حذف Webhook: {delete_result}")
        else:
            log_error(f"❌ فشل حذف Webhook: HTTP {delete_response.status_code}")
        
        # انتظار قصير
        import time
        time.sleep(1)
        
        # 2️⃣ ضبط Webhook الجديد
        log_error("📝 جاري ضبط Webhook الجديد...")
        set_response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setWebhook",
            params={
                'url': webhook_url,
                'allowed_updates': ['message', 'callback_query']
            },
            timeout=10
        )
        
        if set_response.status_code == 200:
            set_result = set_response.json()
            
            if set_result.get('ok'):
                log_error("✅ تم ضبط Webhook بنجاح!")
                log_error(f"📊 المعلومات: {set_result.get('result', {})}")
                return True
            else:
                error_desc = set_result.get('description', 'خطأ غير معروف')
                log_error(f"❌ فشل ضبط Webhook: {error_desc}")
                return False
        else:
            log_error(f"❌ خطأ HTTP {set_response.status_code} عند ضبط Webhook")
            return False
    
    except Exception as e:
        log_error(f"❌ خطأ فادح في setup_webhook: {type(e).__name__}: {str(e)}")
        return False


@app.route("/", methods=["GET"])
def home():
    """
    الصفحة الرئيسية - للتحقق من أن البوت يعمل
    Home page - Health check endpoint
    """
    return """
    <html>
    <head><title>SMM Bot - Webhook Mode</title></head>
    <body style="font-family: Arial, sans-serif; text-align: center; padding: 50px;">
        <h1 style="color: #4CAF50;">✅ SMM Bot is Running!</h1>
        <p style="font-size: 18px;">Mode: <strong>Webhook</strong> (Not Polling)</p>
        <p style="color: #666;">The bot is working perfectly on Render.</p>
        <hr>
        <p style="font-size: 14px; color: #999;">
            Webhook Endpoint: <code>/webhook</code><br>
            Status: <span style="color: green;">Active</span>
        </p>
    </body>
    </html>
    """


@app.route("/health", methods=["GET"])
def health():
    """
    نقطة فحص الصحة - للمراقبة الخارجية
    Health check endpoint - For external monitoring
    """
    from datetime import datetime
    
    return {
        "status": "healthy",
        "mode": "webhook",
        "timestamp": datetime.now().isoformat(),
        "bot": "running"
    }, 200


@app.route("/webhook", methods=["POST"])
def webhook():
    """
    نقطة استقبال التحديثات من Telegram
    Webhook endpoint - Receives updates from Telegram
    
    @return: str - "ok" إذا نجحت المعالجة
    """
    try:
        # التحقق من نوع المحتوى
        if not request.is_json:
            log_error("❌ الطلب ليس JSON")
            return "Invalid content type", 400
        
        # استخراج بيانات التحديث
        update = request.get_json()
        
        if not update:
            log_error("❌ لا توجد بيانات في الطلب")
            return "No data", 400
        
        # تسجيل وصول التحديث (اختياري - يمكن تعطيله لتقليل اللوغ)
        update_id = update.get('update_id', 'Unknown')
        
        if 'message' in update:
            msg_type = 'Message'
            chat_id = update['message'].get('chat', {}).get('id', 'Unknown')
            text = update['message'].get('text', 'No text')[:50]
        elif 'callback_query' in update:
            msg_type = 'Callback'
            chat_id = update['callback_query'].get('from', {}).get('id', 'Unknown')
            text = update['callback_query'].get('data', 'No data')[:50]
        else:
            msg_type = 'Unknown'
            chat_id = 'Unknown'
            text = 'N/A'
        
        log_error(f"📨 [{msg_type}] from {chat_id}: {text}")
        
        # معالجة التحديث عبر الدالة الموجودة
        handle_update(update)
        
        # إرجاع نجاح لـ Telegram
        return "ok", 200
    
    except Exception as e:
        # تسجيل الخطأ
        error_type = type(e).__name__
        error_msg = str(e)[:200]
        log_error(f"❌ Webhook Error: {error_type}: {error_msg}")
        
        # إرجاع خطأ لـ Telegram (سيحاول إعادة الإرسال)
        return "error", 500


@app.route("/status", methods=["GET"])
def status():
    """
    معلومات عن حالة Webhook
    Webhook status information
    """
    try:
        response = requests.get(
            f"https://api.telegram.org/bot{BOT_TOKEN}/getWebhookInfo",
            timeout=10
        )
        
        if response.status_code == 200:
            result = response.json()
            return result, 200
        else:
            return {"error": "Failed to get webhook info"}, 500
    
    except Exception as e:
        return {"error": str(e)}, 500


if __name__ == "__main__":
    """
    نقطة بداية التشغيل
    Entry point
    
    ⚠️ يتم إعداد Webhook تلقائياً قبل بدء الخادم
    ⚠️ Webhook is automatically setup before starting server
    """
    
    log_error("=" * 60)
    log_error("🚀 Starting SMM Bot in Webhook Mode...")
    log_error("=" * 60)
    
    # الحصول على المنفذ من متغيرات البيئة
    port = int(os.environ.get("PORT", 10000))
    
    log_error(f"📍 Port: {port}")
    log_error(f"🌐 Mode: Webhook (NOT Polling)")
    
    # ⚠️ إعداد Webhook قبل بدء الخادم
    log_error("\n🔧 Initializing Webhook...")
    webhook_success = setup_webhook()
    
    if webhook_success:
        log_error("\n✅ Webhook setup successful!")
        log_error("🎯 Bot is ready to receive updates!\n")
    else:
        log_error("\n⚠️  Webhook setup failed, but server will start anyway")
        log_error("💡 You may need to set webhook manually\n")
    
    # بدء خادم Flask
    log_error(f"🌐 Starting Flask server on 0.0.0.0:{port}...")
    log_error("=" * 60)
    
    app.run(host="0.0.0.0", port=port, debug=False)
