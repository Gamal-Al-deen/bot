# -*- coding: utf-8 -*-
"""
دوال مساعدة للتعامل مع Telegram API
Helper functions for Telegram API
"""

import requests
import json
from config import BOT_TOKEN, TELEGRAM_API_URL


def log_error(message):
    """
    تسجيل الأخطاء في ملف log.txt
    Log errors to log.txt
    
    @param message: الرسالة التي سيتم تسجيلها
    """
    try:
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(f"{message}\n")
    except Exception as e:
        print(f"خطأ في كتابة اللوغ: {str(e)}")


def build_inline_keyboard(buttons):
    """
    بناء لوحة أزرار Inline Keyboard
    Build an Inline Keyboard layout
    
    @param buttons: قائمة الأزرار - يمكن أن تكون:
                   - list of dicts: [{'text': 'نص', 'callback_data': 'data'}]
                   - list of lists: [[{'text': 'نص', 'callback_data': 'data'}], ...]
    @return: dict - هيكل InlineKeyboardMarkup
    """
    try:
        # إذا كانت القائمة تحتوي على قوائم فرعية (صفوف)
        if buttons and len(buttons) > 0 and isinstance(buttons[0], list):
            keyboard = buttons
        else:
            # إذا كانت قائمة مسطحة، حولها إلى صف واحد
            keyboard = [buttons]
        
        inline_keyboard = {
            "inline_keyboard": keyboard
        }
        
        return inline_keyboard
        
    except Exception as e:
        log_error(f"❌ خطأ في build_inline_keyboard: {str(e)}")
        return {"inline_keyboard": []}


def send_message(chat_id, text, reply_markup=None, parse_mode="HTML"):
    """
    إرسال رسالة عبر Telegram API
    Send a message via Telegram API
    
    @param chat_id: معرف المحادثة
    @param text: نص الرسالة (يدعم UTF-8 والعربية)
    @param reply_markup: هيكل لوحة الأزرار الاختياري
    @param parse_mode: وضع التحليل (HTML أو Markdown)
    @return: bool - True إذا نجح الإرسال
    """
    try:
        url = f"{TELEGRAM_API_URL}{BOT_TOKEN}/sendMessage"
        
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        # إضافة لوحة الأزرار إذا وجدت
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        # إرسال الطلب
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        # التحقق من نجاح الإرسال
        if result.get("ok"):
            return True
        else:
            error_desc = result.get("description", "خطأ غير معروف")
            log_error(f"❌ فشل إرسال الرسالة: {error_desc}")
            return False
            
    except requests.exceptions.RequestException as e:
        log_error(f"❌ خطأ في الاتصال أثناء إرسال الرسالة: {str(e)}")
        return False
    except Exception as e:
        log_error(f"❌ خطأ غير متوقع في send_message: {str(e)}")
        return False


def edit_message_text(chat_id, message_id, text, reply_markup=None):
    """
    تعديل نص رسالة موجودة
    Edit an existing message text
    
    @param chat_id: معرف المحادثة
    @param message_id: معرف الرسالة
    @param text: النص الجديد
    @param reply_markup: لوحة الأزرار الجديدة (اختياري)
    @return: bool - True إذا نجح التعديل
    """
    try:
        url = f"{TELEGRAM_API_URL}{BOT_TOKEN}/editMessageText"
        
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }
        
        # إضافة لوحة الأزرار إذا وجدت
        if reply_markup:
            data["reply_markup"] = json.dumps(reply_markup)
        
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        if result.get("ok"):
            return True
        else:
            # تجاهل أخطاء "النص لم يتغير"
            if "message is not modified" in str(result.get("description", "")):
                return True
            log_error(f"❌ فشل تعديل الرسالة: {result.get('description')}")
            return False
            
    except Exception as e:
        log_error(f"❌ خطأ في edit_message_text: {str(e)}")
        return False


def answer_callback_query(callback_query_id, text=None, show_alert=False):
    """
    الرد على استفسار callback_query
    Answer a callback query
    
    @param callback_query_id: معرف الاستفسار
    @param text: نص الإشعار (اختياري)
    @param show_alert: إظهار كتنبيه (True) أو إشعار عادي (False)
    @return: bool - True إذا نجح الرد
    """
    try:
        url = f"{TELEGRAM_API_URL}{BOT_TOKEN}/answerCallbackQuery"
        
        data = {
            "callback_query_id": callback_query_id
        }
        
        if text:
            data["text"] = text
        
        data["show_alert"] = show_alert
        
        response = requests.post(url, data=data, timeout=30)
        response.raise_for_status()
        
        result = response.json()
        
        return result.get("ok", False)
        
    except Exception as e:
        log_error(f"❌ خطأ في answer_callback_query: {str(e)}")
        return False


# ⚠️ يمكن إضافة دوال أخرى حسب الحاجة
# ⚠️ You can add more functions as needed


def build_reply_keyboard(buttons, resize=True, one_time=False):
    """
    بناء لوحة أزرار Reply Keyboard
    Build a Reply Keyboard layout
    
    @param buttons: قائمة الأزرار - list of lists
    @param resize: تقليص حجم الأزرار
    @param one_time: إخفاء بعد الاستخدام
    @return: dict - هيكل ReplyKeyboardMarkup
    """
    try:
        keyboard = {
            "keyboard": buttons,
            "resize_keyboard": resize,
            "one_time_keyboard": one_time
        }
        
        return keyboard
        
    except Exception as e:
        log_error(f"❌ خطأ في build_reply_keyboard: {str(e)}")
        return {"keyboard": []}
