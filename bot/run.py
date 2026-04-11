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
from database import init_db


# إنشاء تطبيق Flask
app = Flask(__name__)


def setup_bot_commands():
    """
    إعداد أوامر البوت الرسمية (Menu Button)
    Setup official bot commands for Telegram Menu Button
    
    This uses Telegram Bot API setMyCommands to register commands
    that appear in the Menu button next to the message input field.
    
    @return: bool - True إذا نجح الإعداد
    """
    try:
        from config import ADMIN_ID
        
        log_error("\n" + "=" * 60)
        log_error("📋 Setting up Bot Commands (Menu Button)...")
        log_error("=" * 60)
        
        # 1️⃣ أوامر المستخدم - تظهر لجميع المستخدمين
        user_commands = [
            {"command": "start", "description": "تشغيل البوت"},
            {"command": "services", "description": "عرض الخدمات"},
            {"command": "balance", "description": "عرض رصيدك"},
            {"command": "myaccount", "description": "عرض معلومات حسابك"}
        ]
        
        log_error("👥 Setting user commands (visible to everyone)...")
        user_response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands",
            json={"commands": user_commands},
            timeout=10
        )
        
        if user_response.status_code == 200:
            user_result = user_response.json()
            if user_result.get('ok'):
                log_error(f"✅ User commands set successfully ({len(user_commands)} commands)")
                for cmd in user_commands:
                    log_error(f"   /{cmd['command']} - {cmd['description']}")
            else:
                log_error(f"❌ Failed to set user commands: {user_result}")
        else:
            log_error(f"❌ HTTP {user_response.status_code} error setting user commands")
        
        # 2️⃣ أوامر الأدمن - تظهر فقط للأدمن المحدد
        admin_commands = [
            {"command": "start", "description": "تشغيل البوت"},
            {"command": "balance", "description": "عرض رصيدك"},
            {"command": "services", "description": "عرض الخدمات"},
            {"command": "myaccount", "description": "عرض معلومات حسابك"},
            {"command": "adminpanel", "description": "لوحة الأدمن"},
            {"command": "addbalance", "description": "إضافة رصيد"},
            {"command": "removebalance", "description": "خصم رصيد"},
            {"command": "setprice", "description": "تعديل التسعير"},
            {"command": "setpercent", "description": "تعيين تسعير نسبي"},
            {"command": "addcategory", "description": "إضافة قسم"},
            {"command": "addservice", "description": "إضافة خدمة"},
            {"command": "deleteservice", "description": "حذف خدمة"},
            {"command": "deletecategory", "description": "حذف قسم"},
            {"command": "broadcast", "description": "إرسال رسالة جماعية"},
            {"command": "toggle_notifications", "description": "تشغيل/إيقاف الإشعارات"},
            {"command": "setchannel", "description": "تحديد قناة النشر"}
        ]
        
        log_error(f"\n👑 Setting admin commands (visible only to admin {ADMIN_ID})...")
        admin_response = requests.post(
            f"https://api.telegram.org/bot{BOT_TOKEN}/setMyCommands",
            json={
                "commands": admin_commands,
                "scope": {
                    "type": "chat",
                    "chat_id": int(ADMIN_ID)
                }
            },
            timeout=10
        )
        
        if admin_response.status_code == 200:
            admin_result = admin_response.json()
            if admin_result.get('ok'):
                log_error(f"✅ Admin commands set successfully ({len(admin_commands)} commands)")
                log_error(f"   (Visible only to admin: {ADMIN_ID})")
            else:
                log_error(f"❌ Failed to set admin commands: {admin_result}")
        else:
            log_error(f"❌ HTTP {admin_response.status_code} error setting admin commands")
        
        log_error("=" * 60)
        log_error("✅ Bot commands setup complete!")
        log_error("💡 Menu button (📋) now appears next to message input")
        log_error("=" * 60)
        
        return True
    
    except Exception as e:
        log_error(f"❌ Critical error in setup_bot_commands: {type(e).__name__}: {str(e)}")
        return False


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
    
    log_error("🗄️ تهيئة الاتصال بـ Supabase...")
    if init_db():
        log_error("✅ Supabase: جاهز")
    else:
        log_error("❌ Supabase: فشل التحقق — راجع المفاتيح والجداول في لوحة التحكم")
    
    # الحصول على المنفذ من متغيرات البيئة
    port = int(os.environ.get("PORT", 10000))
    
    log_error(f"📍 Port: {port}")
    log_error(f"🌐 Mode: Webhook (NOT Polling)")
    
    # ⚠️ إعداد أوامر البوت الرسمية (Menu Button)
    log_error("\n📋 Setting up Bot Commands (Menu Button)...")
    commands_success = setup_bot_commands()
    
    if commands_success:
        log_error("\n✅ Bot commands setup successful!")
    else:
        log_error("\n⚠️  Bot commands setup failed, but bot will start anyway")
    
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
