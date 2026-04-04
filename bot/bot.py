# -*- coding: utf-8 -*-
"""
المنطق الرئيسي للبوت - معالجة الأوامر والتحديثات
Main bot logic - Handle commands and updates
"""

from api import SMM_API
from functions import (
    send_message, 
    build_inline_keyboard, 
    answer_callback_query,
    log_error
)
from config import (
    STATE_WAITING_SERVICE, 
    STATE_WAITING_LINK, 
    STATE_WAITING_QUANTITY
)


# إنشاء كائن API
smm_api = SMM_API()

# قاموس لتخزين حالة المستخدمين والبيانات المؤقتة
# Dictionary to store user states and temporary data
user_states = {}


def handle_update(update):
    """
    المعالجة الرئيسية للتحديثات
    Main update handler
    
    @param update: dict - بيانات التحديث من Telegram
    """
    try:
        # التحقق من نوع التحديث
        if 'callback_query' in update:
            # معالجة استفسارات الأزرار
            handle_callback_query(update['callback_query'])
        
        elif 'message' in update:
            # معالجة الرسائل
            handle_message(update['message'])
        
    except Exception as e:
        log_error(f"❌ خطأ في handle_update: {str(e)}")


def handle_message(message):
    """
    معالجة الرسائل الواردة
    Handle incoming messages
    
    @param message: dict - بيانات الرسالة
    """
    try:
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        user_id = message.get('from', {}).get('id')
        
        if not chat_id:
            return
        
        # التحقق من حالة المستخدم
        user_state = user_states.get(user_id, {})
        
        if user_state.get('state') == STATE_WAITING_LINK:
            # المستخدم يرسل الرابط
            handle_link_input(chat_id, user_id, text)
        
        elif user_state.get('state') == STATE_WAITING_QUANTITY:
            # المستخدم يرسل الكمية
            handle_quantity_input(chat_id, user_id, text)
        
        elif text == '/start':
            # أمر البدء
            handle_start_command(chat_id, user_id)
        
        elif text == 'رصيد':
            # طلب الرصيد
            handle_balance(chat_id, user_id)
        
        elif text == 'خدمات':
            # طلب قائمة الخدمات
            handle_services(chat_id, user_id)
        
        elif text == 'طلب جديد':
            # طلب جديد
            handle_new_order(chat_id, user_id)
        
        else:
            # رسالة عادية غير معروفة
            send_message(
                chat_id,
                "👋 مرحباً! استخدم الأزرار في الأسفل للتعامل مع البوت.\n\n"
                "يمكنك استخدام:\n"
                "• /start - لإعادة تشغيل البوت"
            )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_message: {str(e)}")


def handle_callback_query(callback_query):
    """
    معالجة استفسارات Inline Keyboard
    Handle Inline Keyboard callback queries
    
    @param callback_query: dict - بيانات الاستفسار
    """
    try:
        chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
        message_id = callback_query.get('message', {}).get('message_id')
        data = callback_query.get('data')
        user_id = callback_query.get('from', {}).get('id')
        callback_query_id = callback_query.get('id')
        
        if not data or not chat_id:
            answer_callback_query(callback_query_id)
            return
        
        # الرد على الاستفسار أولاً
        answer_callback_query(callback_query_id)
        
        log_error(f"🔘 تم الضغط على زر: {data} من المستخدم {user_id}")
        
        # معالجة البيانات المختلفة
        if data == 'balance':
            # طلب الرصيد
            handle_balance(chat_id, user_id)
        
        elif data == 'services':
            # طلب قائمة الخدمات
            handle_services(chat_id, user_id)
        
        elif data == 'new_order':
            # طلب جديد
            handle_new_order(chat_id, user_id)
        
        elif data.startswith('service_'):
            # اختيار خدمة
            service_id = data.replace('service_', '')
            handle_service_selection(chat_id, user_id, service_id)
        
        elif data == 'confirm_order':
            # تأكيد الطلب
            handle_order_confirmation(chat_id, user_id)
        
        elif data == 'cancel_order':
            # إلغاء الطلب
            handle_order_cancel(chat_id, user_id)
        
        elif data == 'back':
            # زر العودة - إعادة عرض القائمة الرئيسية
            handle_start_command(chat_id, user_id)
        
        else:
            log_error(f"⚠️  callback_data غير معروف: {data}")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_callback_query: {str(e)}")


def handle_start_command(chat_id, user_id):
    """
    معالجة أمر /start
    Handle /start command
    
    @param chat_id: معرف المحادثة
    @param user_id: معرف المستخدم
    """
    try:
        # مسح حالة المستخدم إذا وجدت
        if user_id in user_states:
            del user_states[user_id]
        
        # رسالة الترحيب
        welcome_text = (
            "👋 <b>أهلاً بك في بوت SMM!</b>\n\n"
            "يمكنك من خلال هذا البوت:\n"
            "• التحقق من رصيدك\n"
            "• عرض الخدمات المتاحة\n"
            "• تقديم طلبات جديدة\n\n"
            "اختر من القائمة في الأسفل 👇"
        )
        
        # بناء الأزرار الرئيسية
        buttons = [
            {'text': '💰 رصيد', 'callback_data': 'balance'},
            {'text': '📦 خدمات', 'callback_data': 'services'},
            {'text': '🛒 طلب جديد', 'callback_data': 'new_order'}
        ]
        
        # تنظيم الأزرار في صفوف
        keyboard = [
            [buttons[0], buttons[1]],  # صف أول: رصيد وخدمات
            [buttons[2]]  # صف ثاني: طلب جديد
        ]
        
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, welcome_text, reply_markup)
        
        log_error(f"✅ تم إرسال رسالة ترحيب للمستخدم {user_id}")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_start_command: {str(e)}")


def handle_balance(chat_id, user_id):
    """
    معالجة طلب الرصيد
    Handle balance request
    
    @param chat_id: معرف المحادثة
    @param user_id: معرف المستخدم
    """
    try:
        # جلب الرصيد من API
        balance = smm_api.balance()
        
        if balance is not None:
            text = f"💰 <b>رصيدك الحالي:</b>\n\n${balance:.4f}"
        else:
            text = "❌ حدث خطأ أثناء جلب الرصيد.\n\nيرجى المحاولة لاحقاً."
        
        # زر العودة
        keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_balance: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ غير متوقع.")


def handle_services(chat_id, user_id):
    """
    معالجة طلب قائمة الخدمات
    Handle services list request
    
    @param chat_id: معرف المحادثة
    @param user_id: معرف المستخدم
    """
    try:
        # جلب الخدمات من API
        services = smm_api.services()
        
        if not services:
            send_message(chat_id, "❌ لا توجد خدمات متاحة حالياً.")
            return
        
        # عرض أول 5 خدمات فقط
        display_services = services[:5]
        
        text = "<b>📦 الخدمات المتاحة:</b>\n\n"
        
        for idx, service in enumerate(display_services, 1):
            name = service.get('name', 'خدمة غير معروفة')
            price = service.get('rate', 0)
            service_id = service.get('service', 0)
            
            text += f"{idx}. <b>{name}</b>\n"
            text += f"   السعر: ${price} لكل 1000\n"
            text += f"   المعرف: {service_id}\n\n"
        
        if len(services) > 5:
            text += f"... وهناك {len(services) - 5} خدمات أخرى"
        
        # أزرار الخدمات
        buttons = []
        for service in display_services:
            service_id = service.get('service', 0)
            name = service.get('name', 'خدمة')[:30]  # تقصير الاسم
            buttons.append([
                {'text': f'📍 {name}', 'callback_data': f'service_{service_id}'}
            ])
        
        # زر العودة
        buttons.append([{'text': '🔙 عودة', 'callback_data': 'back'}])
        
        reply_markup = build_inline_keyboard(buttons)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_services: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ أثناء جلب الخدمات.")


def handle_new_order(chat_id, user_id):
    """
    بدء عملية طلب جديد
    Start new order process
    
    @param chat_id: معرف المحادثة
    @param user_id: معرف المستخدم
    """
    try:
        # جلب الخدمات
        services = smm_api.services()
        
        if not services:
            send_message(chat_id, "❌ لا توجد خدمات متاحة حالياً.")
            return
        
        text = "<b>🛒 اختر الخدمة:</b>\n\n"
        
        # عرض أول 10 خدمات
        display_services = services[:10]
        
        buttons = []
        for service in display_services:
            service_id = service.get('service', 0)
            name = service.get('name', 'خدمة')[:40]
            buttons.append([
                {'text': f'{name}', 'callback_data': f'service_{service_id}'}
            ])
        
        buttons.append([{'text': '❌ إلغاء', 'callback_data': 'cancel_order'}])
        
        reply_markup = build_inline_keyboard(buttons)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_new_order: {str(e)}")


def handle_service_selection(chat_id, user_id, service_id):
    """
    معالجة اختيار خدمة
    Handle service selection
    
    @param chat_id: معرف المحادثة
    @param user_id: معرف المستخدم
    @param service_id: معرف الخدمة المختارة
    """
    try:
        # حفظ حالة المستخدم
        user_states[user_id] = {
            'state': STATE_WAITING_LINK,
            'service_id': service_id
        }
        
        text = (
            f"✅ <b>تم اختيار الخدمة: {service_id}</b>\n\n"
            "الآن يرجى إرسال <b>الرابط</b> الذي تريد العمل عليه:"
        )
        
        send_message(chat_id, text)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_service_selection: {str(e)}")


def handle_link_input(chat_id, user_id, link):
    """
    معالجة إدخال الرابط
    Handle link input
    
    @param chat_id: معرف المحادثة
    @param user_id: معرف المستخدم
    @param link: الرابط المرسل
    """
    try:
        # التحقق من صحة الرابط
        if not link or not link.startswith('http'):
            send_message(
                chat_id,
                "❌ الرابط غير صالح.\n\n"
                "يرجى إرسال رابط صحيح يبدأ بـ http:// أو https://"
            )
            return
        
        # حفظ الرابط في حالة المستخدم
        user_states[user_id]['link'] = link
        user_states[user_id]['state'] = STATE_WAITING_QUANTITY
        
        text = (
            f"✅ <b>تم حفظ الرابط:</b>\n{link}\n\n"
            "الآن يرجى إرسال <b>الكمية</b> المطلوبة:"
        )
        
        send_message(chat_id, text)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_link_input: {str(e)}")


def handle_quantity_input(chat_id, user_id, quantity_text):
    """
    معالجة إدخال الكمية
    Handle quantity input
    
    @param chat_id: معرف المحادثة
    @param user_id: معرف المستخدم
    @param quantity_text: الكمية المرسلة كنص
    """
    try:
        # التحقق من أن الكمية رقم صحيح
        try:
            quantity = int(quantity_text)
            
            if quantity <= 0:
                raise ValueError("الكمية يجب أن تكون موجبة")
        
        except ValueError:
            send_message(
                chat_id,
                "❌ الكمية غير صالحة.\n\n"
                "يرجى إرسال رقم صحيح موجب."
            )
            return
        
        # حفظ الكمية
        user_states[user_id]['quantity'] = quantity
        
        # الحصول على تفاصيل الطلب
        service_id = user_states[user_id].get('service_id')
        link = user_states[user_id].get('link')
        
        # عرض ملخص الطلب للتأكيد
        summary_text = (
            "<b>📋 ملخص طلبك:</b>\n\n"
            f"🔖 الخدمة: {service_id}\n"
            f"🔗 الرابط: {link}\n"
            f"🔢 الكمية: {quantity}\n\n"
            "هل تريد تأكيد الطلب؟"
        )
        
        # أزرار التأكيد
        buttons = [
            [
                {'text': '✅ تأكيد', 'callback_data': 'confirm_order'},
                {'text': '❌ إلغاء', 'callback_data': 'cancel_order'}
            ]
        ]
        
        reply_markup = build_inline_keyboard(buttons)
        
        send_message(chat_id, summary_text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_quantity_input: {str(e)}")


def handle_order_confirmation(chat_id, user_id):
    """
    معالجة تأكيد الطلب
    Handle order confirmation
    
    @param chat_id: معرف المحادثة
    @param user_id: معرف المستخدم
    """
    try:
        # الحصول على بيانات الطلب
        user_state = user_states.get(user_id, {})
        
        service_id = user_state.get('service_id')
        link = user_state.get('link')
        quantity = user_state.get('quantity')
        
        if not all([service_id, link, quantity]):
            send_message(chat_id, "❌ بيانات الطلب غير مكتممة.")
            return
        
        # تقديم الطلب عبر API
        order_id = smm_api.order(service_id, link, quantity)
        
        if order_id:
            text = (
                f"✅ <b>تم تقديم طلبك بنجاح!</b>\n\n"
                f"🔢 معرف الطلب: {order_id}\n"
                f"🔖 الخدمة: {service_id}\n"
                f"🔢 الكمية: {quantity}\n\n"
                "يمكنك التحقق من حالة الطلب لاحقاً."
            )
            
            # زر التحقق من الحالة
            buttons = [[{'text': '📊 حالة الطلب', 'callback_data': f'status_{order_id}'}]]
            reply_markup = build_inline_keyboard(buttons)
            
            send_message(chat_id, text, reply_markup)
            
            log_error(f"✅ تم تقديم طلب ناجح للمستخدم {user_id} - Order ID: {order_id}")
        
        else:
            send_message(
                chat_id,
                "❌ فشل تقديم الطلب.\n\n"
                "يرجى المحاولة لاحقاً أو التواصل مع الدعم."
            )
        
        # مسح حالة المستخدم
        if user_id in user_states:
            del user_states[user_id]
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_order_confirmation: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ أثناء معالجة الطلب.")


def handle_order_cancel(chat_id, user_id):
    """
    معالجة إلغاء الطلب
    Handle order cancellation
    
    @param chat_id: معرف المحادثة
    @param user_id: معرف المستخدم
    """
    try:
        # مسح حالة المستخدم
        if user_id in user_states:
            del user_states[user_id]
        
        text = "❌ <b>تم إلغاء العملية.</b>\n\nيمكنك استخدام /start للبدء من جديد."
        send_message(chat_id, text)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_order_cancel: {str(e)}")


# ⚠️ يمكن إضافة معالجات أخرى حسب الحاجة
# ⚠️ You can add more handlers as needed
