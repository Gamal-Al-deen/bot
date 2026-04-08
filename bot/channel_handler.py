# -*- coding: utf-8 -*-
"""
معالج إدخال قناة النشر
Channel Username Input Handler
"""

from functions import send_message, build_inline_keyboard, log_error
from users_manager import setChannelUsername, getChannelUsername
from advanced_logger import logErrorWithDetails

# هذا الملف مؤقت - سيتم نقل المحتوى إلى bot.py


def handle_channel_username_input(chat_id, user_id, text, user_states):
    """
    معالجة إدخال يوزرنيم القناة
    Handle channel username input
    """
    try:
        # مسح حالة الانتظار
        if user_id in user_states:
            del user_states[user_id]
        
        # تعيين يوزرنيم القناة
        if setChannelUsername(text):
            channel_username = getChannelUsername()
            
            keyboard = [[{'text': '🔙 عودة للوحة الأدمن', 'callback_data': 'admin_panel'}]]
            reply_markup = build_inline_keyboard(keyboard)
            
            send_message(
                chat_id,
                f"✅ <b>تم تعيين قناة النشر بنجاح!</b>\n\n"
                f"📣 <b>القناة:</b> @{channel_username}\n\n"
                f"💡 الآن سيتم إرسال إشعارات الطلبات إلى هذه القناة\n\n"
                f"⚠️ تأكد أن البوت مضاف كأدمن في القناة",
                reply_markup
            )
            
            log_error(f"📣 Channel set to @{channel_username} by admin {user_id}")
        else:
            send_message(chat_id, "❌ فشل في تعيين القناة. يرجى المحاولة مرة أخرى.")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_channel_username_input: {str(e)}")
        logErrorWithDetails("channel_username_input_error", str(e), user_id)
