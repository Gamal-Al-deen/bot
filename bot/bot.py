# -*- coding: utf-8 -*-
"""
المنطق الرئيسي للبوت - معالجة الأوامر والتحديثات (نسخة متقدمة)
Main bot logic - Handle commands and updates (Advanced Version)
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
    STATE_WAITING_QUANTITY,
    STATE_WAITING_ADMIN_ADD_BALANCE,
    STATE_WAITING_ADMIN_REMOVE_BALANCE,
    STATE_WAITING_ADMIN_USER_ID,
    USER_LOCK_TIMEOUT
)
from users_manager import (
    getBalance, 
    addBalance, 
    deductBalance, 
    setBalance,
    getUserData,
    getAllUsersCount
)
from pricing_system import (
    calculatePrice,
    setPercentPricing,
    setFixedPricing,
    getPricingInfo,
    calculateOrderTotalPrice
)
from admin_system import isAdmin, validateAdminCommand
from lock_system import acquireLock, releaseLock, isLocked
from advanced_logger import (
    logBalanceOperation,
    logOrderOperation,
    logPricingOperation,
    logAdminOperation,
    logErrorWithDetails
)

# إنشاء كائن API
smm_api = SMM_API()

# قاموس لتخزين حالة المستخدمين والبيانات المؤقتة
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
        logErrorWithDetails("handle_update_error", str(e))


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
        
        if not chat_id or not user_id:
            return
        
        # التحقق من حالة المستخدم
        user_state = user_states.get(user_id, {})
        state = user_state.get('state')
        
        # معالجة حالات الانتظار المختلفة
        if state == STATE_WAITING_LINK:
            handle_link_input(chat_id, user_id, text)
        
        elif state == STATE_WAITING_QUANTITY:
            handle_quantity_input(chat_id, user_id, text)
        
        elif state == STATE_WAITING_ADMIN_USER_ID:
            handle_admin_user_id_input(chat_id, user_id, text)
        
        elif state == STATE_WAITING_ADMIN_ADD_BALANCE:
            handle_admin_add_balance_input(chat_id, user_id, text)
        
        elif state == STATE_WAITING_ADMIN_REMOVE_BALANCE:
            handle_admin_remove_balance_input(chat_id, user_id, text)
        
        # معالجة الأوامر
        elif text == '/start':
            handle_start_command(chat_id, user_id)
        
        elif text == '/balance' or text == '💰 رصيدي':
            handle_balance(chat_id, user_id)
        
        elif text == '/services' or text == '🛒 الخدمات':
            handle_services(chat_id, user_id)
        
        elif text == '/neworder' or text == '🛒 طلب جديد':
            handle_new_order(chat_id, user_id)
        
        elif text == '📞 التواصل مع الادمن':
            handle_contact_admin(chat_id, user_id)
        
        elif text == '💳 الدفع / الاشتراك':
            handle_payment_info(chat_id, user_id)
        
        elif text == '🔄 تحديث':
            handle_refresh(chat_id, user_id)
        
        # أوامر الأدمن
        elif text.startswith('/addbalance'):
            handle_admin_add_balance_command(chat_id, user_id, text)
        
        elif text.startswith('/removebalance'):
            handle_admin_remove_balance_command(chat_id, user_id, text)
        
        elif text.startswith('/setpercent'):
            handle_admin_set_percent(chat_id, user_id, text)
        
        elif text.startswith('/setprice'):
            handle_admin_set_fixed_price(chat_id, user_id, text)
        
        elif text == '/price':
            handle_admin_show_pricing(chat_id, user_id)
        
        else:
            # رسالة عادية غير معروفة
            send_message(
                chat_id,
                "👋 مرحباً! استخدم الأزرار في الأسفل للتعامل مع البوت.\n\n"
                "يمكنك استخدام:\n"
                "• /start - لإعادة تشغيل البوت\n"
                "• /balance - لعرض رصيدك\n"
                "• /services - لعرض الخدمات"
            )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_message: {str(e)}")
        logErrorWithDetails("handle_message_error", str(e), user_id)


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
        
        # التحقق من القفل
        if isLocked(user_id, USER_LOCK_TIMEOUT):
            answer_callback_query(callback_query_id, text="⏳ يرجى الانتظار، جاري معالجة طلب سابق...", show_alert=True)
            return
        
        # الرد على الاستفسار أولاً
        answer_callback_query(callback_query_id)
        
        log_error(f"🔘 تم الضغط على زر: {data} من المستخدم {user_id}")
        
        # معالجة البيانات المختلفة
        if data == 'balance':
            handle_balance(chat_id, user_id)
        
        elif data == 'services':
            handle_services(chat_id, user_id)
        
        elif data == 'new_order':
            handle_new_order(chat_id, user_id)
        
        elif data == 'contact_admin':
            handle_contact_admin(chat_id, user_id)
        
        elif data == 'payment_info':
            handle_payment_info(chat_id, user_id)
        
        elif data == 'refresh':
            handle_refresh(chat_id, user_id)
        
        elif data.startswith('service_'):
            # اختيار خدمة
            service_id = data.replace('service_', '')
            handle_service_selection(chat_id, user_id, service_id)
        
        elif data.startswith('page_'):
            # تصفح صفحات الخدمات
            page_number = int(data.replace('page_', ''))
            handle_services_pagination(chat_id, user_id, page_number)
        
        elif data == 'confirm_order':
            handle_order_confirmation(chat_id, user_id)
        
        elif data == 'cancel_order':
            handle_order_cancel(chat_id, user_id)
        
        elif data == 'back':
            handle_start_command(chat_id, user_id)
        
        elif data.startswith('status_'):
            order_id = data.replace('status_', '')
            handle_order_status(chat_id, user_id, order_id)
        
        else:
            log_error(f"⚠️ callback_data غير معروف: {data}")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_callback_query: {str(e)}")
        logErrorWithDetails("handle_callback_error", str(e), user_id)


def handle_start_command(chat_id, user_id):
    """
    معالجة أمر /start
    Handle /start command
    """
    try:
        # مسح حالة المستخدم إذا وجدت
        if user_id in user_states:
            del user_states[user_id]
        
        # تحرير القفل
        releaseLock(user_id)
        
        # رسالة الترحيب
        welcome_text = (
            "👋 <b>أهلاً بك في بوت SMM المتقدم!</b>\n\n"
            "يمكنك من خلال هذا البوت:\n"
            "• التحقق من رصيدك\n"
            "• عرض الخدمات المتاحة\n"
            "• تقديم طلبات جديدة\n"
            "• التواصل مع الأدمن\n"
            "• معرفة طرق الدفع\n\n"
            "اختر من القائمة في الأسفل 👇"
        )
        
        # بناء الأزرار الرئيسية
        keyboard = [
            [{'text': '💰 رصيدي', 'callback_data': 'balance'}, {'text': '🛒 الخدمات', 'callback_data': 'services'}],
            [{'text': '🛒 طلب جديد', 'callback_data': 'new_order'}],
            [{'text': '📞 التواصل مع الادمن', 'callback_data': 'contact_admin'}, {'text': '💳 الدفع / الاشتراك', 'callback_data': 'payment_info'}],
            [{'text': '🔄 تحديث', 'callback_data': 'refresh'}]
        ]
        
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, welcome_text, reply_markup)
        
        log_error(f"✅ تم إرسال رسالة ترحيب للمستخدم {user_id}")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_start_command: {str(e)}")
        logErrorWithDetails("start_command_error", str(e), user_id)


def handle_balance(chat_id, user_id):
    """
    معالجة طلب الرصيد
    Handle balance request
    """
    try:
        # جلب رصيد المستخدم من النظام المحلي
        balance = getBalance(user_id)
        
        text = f"💰 <b>رصيدك الحالي:</b>\n\n💵 {balance:.6f}$"
        
        # زر العودة والتحديث
        keyboard = [
            [{'text': '🔄 تحديث', 'callback_data': 'refresh'}],
            [{'text': '🔙 عودة للقائمة الرئيسية', 'callback_data': 'back'}]
        ]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_balance: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ غير متوقع.")
        logErrorWithDetails("balance_error", str(e), user_id)


def handle_services(chat_id, user_id, page=0):
    """
    معالجة طلب قائمة الخدمات
    Handle services list request
    """
    try:
        # جلب الخدمات من API
        services = smm_api.services()
        
        if not services:
            send_message(chat_id, "❌ لا توجد خدمات متاحة حالياً.")
            return
        
        # عدد الخدمات في كل صفحة
        services_per_page = 10
        total_pages = (len(services) + services_per_page - 1) // services_per_page
        
        # تحديد الخدمات للصفحة الحالية
        start_idx = page * services_per_page
        end_idx = min(start_idx + services_per_page, len(services))
        page_services = services[start_idx:end_idx]
        
        text = f"<b>📦 الخدمات المتاحة (صفحة {page + 1}/{total_pages}):</b>\n\n"
        
        for idx, service in enumerate(page_services, start_idx + 1):
            name = service.get('name', 'خدمة غير معروفة')
            base_rate = float(service.get('rate', 0))
            service_id = service.get('service', 0)
            
            # حساب السعر بعد تطبيق التسعير
            final_rate = calculatePrice(base_rate)
            
            text += f"{idx}. <b>{name[:50]}</b>\n"
            text += f"   السعر الأصلي: ${base_rate:.6f} لكل 1000\n"
            text += f"   السعر النهائي: ${final_rate:.6f} لكل 1000\n"
            text += f"   المعرف: <code>{service_id}</code>\n\n"
        
        # أزرار الخدمات
        buttons = []
        for service in page_services:
            service_id = service.get('service', 0)
            name = service.get('name', 'خدمة')[:40]
            buttons.append([
                {'text': f'📍 {name}', 'callback_data': f'service_{service_id}'}
            ])
        
        # أزرار التنقل بين الصفحات
        nav_buttons = []
        if page > 0:
            nav_buttons.append({'text': '⬅️ السابق', 'callback_data': f'page_{page-1}'})
        if page < total_pages - 1:
            nav_buttons.append({'text': 'التالي ➡️', 'callback_data': f'page_{page+1}'})
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        # زر العودة
        buttons.append([{'text': '🔙 عودة للقائمة الرئيسية', 'callback_data': 'back'}])
        
        reply_markup = build_inline_keyboard(buttons)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_services: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ أثناء جلب الخدمات.")
        logErrorWithDetails("services_error", str(e), user_id)


def handle_services_pagination(chat_id, user_id, page_number):
    """
    معالجة تصفح صفحات الخدمات
    Handle services pagination
    """
    try:
        handle_services(chat_id, user_id, page_number)
    except Exception as e:
        log_error(f"❌ خطأ في handle_services_pagination: {str(e)}")


def handle_new_order(chat_id, user_id):
    """
    بدء عملية طلب جديد
    Start new order process
    """
    try:
        # التحقق من القفل
        if isLocked(user_id, USER_LOCK_TIMEOUT):
            send_message(chat_id, "⏳ لديك طلب قيد المعالجة. يرجى الانتظار.")
            return
        
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
        logErrorWithDetails("new_order_error", str(e), user_id)


def handle_service_selection(chat_id, user_id, service_id):
    """
    معالجة اختيار خدمة
    Handle service selection
    """
    try:
        # الحصول على قفل
        if not acquireLock(user_id, USER_LOCK_TIMEOUT):
            send_message(chat_id, "⏳ لديك طلب قيد المعالجة. يرجى الانتظار.")
            return
        
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
        releaseLock(user_id)
        logErrorWithDetails("service_selection_error", str(e), user_id)


def handle_link_input(chat_id, user_id, link):
    """
    معالجة إدخال الرابط
    Handle link input
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
        releaseLock(user_id)
        logErrorWithDetails("link_input_error", str(e), user_id)


def handle_quantity_input(chat_id, user_id, quantity_text):
    """
    معالجة إدخال الكمية
    Handle quantity input
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
        
        # جلب تفاصيل الخدمة من API
        services = smm_api.services()
        service_info = None
        for service in services:
            if str(service.get('service')) == str(service_id):
                service_info = service
                break
        
        if not service_info:
            send_message(chat_id, "❌ خطأ: لم يتم العثور على معلومات الخدمة.")
            releaseLock(user_id)
            return
        
        base_rate = float(service_info.get('rate', 0))
        price_info = calculateOrderTotalPrice(base_rate, quantity)
        
        # عرض ملخص الطلب للتأكيد
        summary_text = (
            "<b>📋 ملخص طلبك:</b>\n\n"
            f"🔖 الخدمة: {service_id}\n"
            f"🔗 الرابط: {link}\n"
            f"🔢 الكمية: {quantity}\n"
            f"💰 السعر الأصلي: ${price_info['original_price']:.6f}\n"
            f"💵 السعر النهائي: ${price_info['final_price']:.6f}\n\n"
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
        releaseLock(user_id)
        logErrorWithDetails("quantity_input_error", str(e), user_id)


def handle_order_confirmation(chat_id, user_id):
    """
    معالجة تأكيد الطلب
    Handle order confirmation
    """
    try:
        # الحصول على بيانات الطلب
        user_state = user_states.get(user_id, {})
        
        service_id = user_state.get('service_id')
        link = user_state.get('link')
        quantity = user_state.get('quantity')
        
        if not all([service_id, link, quantity]):
            send_message(chat_id, "❌ بيانات الطلب غير مكتممة.")
            releaseLock(user_id)
            return
        
        # جلب تفاصيل الخدمة
        services = smm_api.services()
        service_info = None
        for service in services:
            if str(service.get('service')) == str(service_id):
                service_info = service
                break
        
        if not service_info:
            send_message(chat_id, "❌ خطأ: لم يتم العثور على معلومات الخدمة.")
            releaseLock(user_id)
            return
        
        base_rate = float(service_info.get('rate', 0))
        price_info = calculateOrderTotalPrice(base_rate, quantity)
        final_price = price_info['final_price']
        
        # التحقق من رصيد المستخدم
        current_balance = getBalance(user_id)
        if current_balance < final_price:
            send_message(
                chat_id,
                f"❌ <b>رصيدك غير كافٍ!</b>\n\n"
                f"💰 رصيدك الحالي: {current_balance:.6f}$\n"
                f"💵 المطلوب: {final_price:.6f}$\n"
                f"📉 العجز: {final_price - current_balance:.6f}$\n\n"
                "يرجى شحن رصيدك أولاً."
            )
            releaseLock(user_id)
            return
        
        # خصم الرصيد
        balance_before = current_balance
        if not deductBalance(user_id, final_price):
            send_message(chat_id, "❌ فشل في خصم الرصيد. يرجى المحاولة لاحقاً.")
            releaseLock(user_id)
            return
        
        balance_after = getBalance(user_id)
        
        # تسجيل عملية الرصيد
        logBalanceOperation(user_id, "deduct", final_price, balance_before, balance_after)
        
        # تقديم الطلب عبر API
        order_id = smm_api.order(service_id, link, quantity)
        
        if order_id:
            text = (
                f"✅ <b>تم تقديم طلبك بنجاح!</b>\n\n"
                f"🔢 معرف الطلب: {order_id}\n"
                f"🔖 الخدمة: {service_id}\n"
                f"🔢 الكمية: {quantity}\n"
                f"💵 المبلغ المخصوم: {final_price:.6f}$\n"
                f"💰 رصيدك الجديد: {balance_after:.6f}$\n\n"
                "يمكنك التحقق من حالة الطلب لاحقاً."
            )
            
            # زر التحقق من الحالة
            buttons = [[{'text': '📊 حالة الطلب', 'callback_data': f'status_{order_id}'}]]
            reply_markup = build_inline_keyboard(buttons)
            
            send_message(chat_id, text, reply_markup)
            
            # تسجيل عملية الطلب
            logOrderOperation(user_id, order_id, service_id, quantity, final_price, "success")
            
            log_error(f"✅ تم تقديم طلب ناجح للمستخدم {user_id} - Order ID: {order_id}")
        
        else:
            # استرجاع الرصيد إذا فشل الطلب
            addBalance(user_id, final_price)
            balance_after_refund = getBalance(user_id)
            
            logBalanceOperation(user_id, "refund", final_price, balance_after, balance_after_refund)
            
            send_message(
                chat_id,
                "❌ فشل تقديم الطلب.\n\n"
                "تم استرجاع المبلغ إلى رصيدك تلقائياً.\n"
                "يرجى المحاولة لاحقاً أو التواصل مع الدعم."
            )
            
            # تسجيل عملية الطلب الفاشل
            logOrderOperation(user_id, "failed", service_id, quantity, final_price, "failed")
        
        # مسح حالة المستخدم وتحرير القفل
        if user_id in user_states:
            del user_states[user_id]
        releaseLock(user_id)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_order_confirmation: {str(e)}")
        releaseLock(user_id)
        send_message(chat_id, "❌ حدث خطأ أثناء معالجة الطلب.")
        logErrorWithDetails("order_confirmation_error", str(e), user_id)


def handle_order_cancel(chat_id, user_id):
    """
    معالجة إلغاء الطلب
    Handle order cancellation
    """
    try:
        # مسح حالة المستخدم
        if user_id in user_states:
            del user_states[user_id]
        
        # تحرير القفل
        releaseLock(user_id)
        
        text = "❌ <b>تم إلغاء العملية.</b>\n\nيمكنك استخدام /start للبدء من جديد."
        send_message(chat_id, text)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_order_cancel: {str(e)}")
        releaseLock(user_id)


def handle_order_status(chat_id, user_id, order_id):
    """
    معالجة طلب حالة الطلب
    Handle order status request
    """
    try:
        status = smm_api.status(order_id)
        
        if status:
            text = f"<b>📊 حالة الطلب #{order_id}:</b>\n\n"
            
            if 'status' in status:
                text += f"📌 الحالة: {status['status']}\n"
            if 'remains' in status:
                text += f"🔢 المتبقي: {status['remains']}\n"
            if 'charge' in status:
                text += f"💰 التكلفة: ${status['charge']}\n"
            
            # زر العودة
            keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
            reply_markup = build_inline_keyboard(keyboard)
            
            send_message(chat_id, text, reply_markup)
        else:
            send_message(chat_id, "❌ لم يتم العثور على معلومات الطلب.")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_order_status: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ أثناء جلب حالة الطلب.")
        logErrorWithDetails("order_status_error", str(e), user_id, f"order_id:{order_id}")


def handle_contact_admin(chat_id, user_id):
    """
    معالجة طلب التواصل مع الأدمن
    Handle contact admin request
    """
    try:
        text = (
            "📞 <b>للتواصل مع الأدمن:</b>\n\n"
            "📱 Telegram: @YourAdminUsername\n"
            "📧 Email: admin@example.com\n\n"
            "⏰ أوقات العمل: 24/7\n"
            "💬 نحن هنا لمساعدتك!"
        )
        
        keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_contact_admin: {str(e)}")
        logErrorWithDetails("contact_admin_error", str(e), user_id)


def handle_payment_info(chat_id, user_id):
    """
    معالجة طلب معلومات الدفع
    Handle payment info request
    """
    try:
        text = (
            "💳 <b>طرق الدفع المتاحة:</b>\n\n"
            "🏦 <b>التحويل البنكي:</b>\n"
            "Bank: Example Bank\n"
            "Account: 1234567890\n\n"
            "💰 <b>PayPal:</b>\n"
            "Email: paypal@example.com\n\n"
            "📱 <b>وسائل دفع أخرى:</b>\n"
            "يرجى التواصل مع الأدمن للمزيد من المعلومات\n\n"
            "⚠️ بعد الدفع، أرسل إثبات الدفع للأدمن ليتم شحن رصيدك."
        )
        
        keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_payment_info: {str(e)}")
        logErrorWithDetails("payment_info_error", str(e), user_id)


def handle_refresh(chat_id, user_id):
    """
    معالجة زر التحديث/إعادة التعبئة
    Handle refresh button
    """
    try:
        # تحديث رصيد المستخدم
        balance = getBalance(user_id)
        
        text = f"✅ <b>تم تحديث بياناتك بنجاح!</b>\n\n💰 رصيدك الحالي: {balance:.6f}$"
        
        # الأزرار الرئيسية
        keyboard = [
            [{'text': '💰 رصيدي', 'callback_data': 'balance'}, {'text': '🛒 الخدمات', 'callback_data': 'services'}],
            [{'text': '🛒 طلب جديد', 'callback_data': 'new_order'}],
            [{'text': '📞 التواصل مع الادمن', 'callback_data': 'contact_admin'}, {'text': '💳 الدفع / الاشتراك', 'callback_data': 'payment_info'}],
            [{'text': '🔄 تحديث', 'callback_data': 'refresh'}]
        ]
        
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
        
        log_error(f"🔄 تم تحديث بيانات المستخدم {user_id}")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_refresh: {str(e)}")
        logErrorWithDetails("refresh_error", str(e), user_id)


# ========== أوامر الأدمن ==========


def handle_admin_add_balance_command(chat_id, user_id, text):
    """
    معالجة أمر إضافة الرصيد (أدمن فقط)
    Handle admin add balance command
    """
    try:
        if not validateAdminCommand(user_id, "/addbalance"):
            send_message(chat_id, "❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return
        
        # تحليل الأمر
        parts = text.split()
        
        if len(parts) == 3:
            # /addbalance USER_ID AMOUNT
            try:
                target_user_id = int(parts[1])
                amount = float(parts[2])
                
                if amount <= 0:
                    send_message(chat_id, "❌ المبلغ يجب أن يكون موجباً.")
                    return
                
                # إضافة الرصيد
                balance_before = getBalance(target_user_id)
                if addBalance(target_user_id, amount):
                    balance_after = getBalance(target_user_id)
                    
                    # تسجيل العملية
                    logBalanceOperation(target_user_id, "add_by_admin", amount, balance_before, balance_after)
                    logAdminOperation(user_id, "/addbalance", target_user_id, f"Amount:{amount}$")
                    
                    send_message(
                        chat_id,
                        f"✅ <b>تم إضافة الرصيد بنجاح!</b>\n\n"
                        f"👤 المستخدم: {target_user_id}\n"
                        f"💰 المبلغ: {amount}$\n"
                        f"📊 الرصيد قبل: {balance_before:.6f}$\n"
                        f"💵 الرصيد بعد: {balance_after:.6f}$"
                    )
                else:
                    send_message(chat_id, "❌ فشل في إضافة الرصيد.")
            
            except ValueError:
                send_message(chat_id, "❌ بيانات غير صالحة.\n\nالاستخدام: /addbalance USER_ID AMOUNT")
        
        elif len(parts) == 2:
            # بدء عملية إضافة الرصيد خطوة بخطوة
            try:
                target_user_id = int(parts[1])
                
                # حفظ حالة الأدمن
                user_states[user_id] = {
                    'state': STATE_WAITING_ADMIN_ADD_BALANCE,
                    'target_user_id': target_user_id
                }
                
                send_message(
                    chat_id,
                    f"💰 <b>إضافة رصيد للمستخدم {target_user_id}</b>\n\n"
                    f"الآن أرسل المبلغ الذي تريد إضافته:"
                )
            
            except ValueError:
                send_message(chat_id, "❌ معرف المستخدم غير صالح.\n\nالاستخدام: /addbalance USER_ID")
        
        else:
            send_message(
                chat_id,
                "📝 <b>إضافة رصيد لمستخدم:</b>\n\n"
                "الاستخدام:\n"
                "<code>/addbalance USER_ID AMOUNT</code>\n\n"
                "أو:\n"
                "<code>/addbalance USER_ID</code> (ثم إرسال المبلغ)"
            )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_add_balance_command: {str(e)}")
        logErrorWithDetails("admin_add_balance_error", str(e), user_id)


def handle_admin_add_balance_input(chat_id, user_id, text):
    """
    معالجة إدخال مبلغ إضافة الرصيد (أدمن)
    Handle admin add balance amount input
    """
    try:
        user_state = user_states.get(user_id, {})
        target_user_id = user_state.get('target_user_id')
        
        if not target_user_id:
            send_message(chat_id, "❌ خطأ: لم يتم تحديد المستخدم.")
            if user_id in user_states:
                del user_states[user_id]
            return
        
        try:
            amount = float(text)
            
            if amount <= 0:
                send_message(chat_id, "❌ المبلغ يجب أن يكون موجباً.\n\nالرجاء إرسال مبلغ صحيح:")
                return
            
            # إضافة الرصيد
            balance_before = getBalance(target_user_id)
            if addBalance(target_user_id, amount):
                balance_after = getBalance(target_user_id)
                
                # تسجيل العملية
                logBalanceOperation(target_user_id, "add_by_admin", amount, balance_before, balance_after)
                logAdminOperation(user_id, "/addbalance", target_user_id, f"Amount:{amount}$")
                
                send_message(
                    chat_id,
                    f"✅ <b>تم إضافة الرصيد بنجاح!</b>\n\n"
                    f"👤 المستخدم: {target_user_id}\n"
                    f"💰 المبلغ: {amount}$\n"
                    f"📊 الرصيد قبل: {balance_before:.6f}$\n"
                    f"💵 الرصيد بعد: {balance_after:.6f}$"
                )
            else:
                send_message(chat_id, "❌ فشل في إضافة الرصيد.")
        
        except ValueError:
            send_message(chat_id, "❌ مبلغ غير صالح.\n\nالرجاء إرسال رقم صحيح:")
            return
        
        # مسح الحالة
        if user_id in user_states:
            del user_states[user_id]
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_add_balance_input: {str(e)}")
        logErrorWithDetails("admin_add_balance_input_error", str(e), user_id)


def handle_admin_remove_balance_command(chat_id, user_id, text):
    """
    معالجة أمر خصم الرصيد (أدمن فقط)
    Handle admin remove balance command
    """
    try:
        if not validateAdminCommand(user_id, "/removebalance"):
            send_message(chat_id, "❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return
        
        # تحليل الأمر
        parts = text.split()
        
        if len(parts) == 3:
            # /removebalance USER_ID AMOUNT
            try:
                target_user_id = int(parts[1])
                amount = float(parts[2])
                
                if amount <= 0:
                    send_message(chat_id, "❌ المبلغ يجب أن يكون موجباً.")
                    return
                
                # خصم الرصيد
                balance_before = getBalance(target_user_id)
                if deductBalance(target_user_id, amount):
                    balance_after = getBalance(target_user_id)
                    
                    # تسجيل العملية
                    logBalanceOperation(target_user_id, "remove_by_admin", amount, balance_before, balance_after)
                    logAdminOperation(user_id, "/removebalance", target_user_id, f"Amount:{amount}$")
                    
                    send_message(
                        chat_id,
                        f"✅ <b>تم خصم الرصيد بنجاح!</b>\n\n"
                        f"👤 المستخدم: {target_user_id}\n"
                        f"💰 المبلغ: {amount}$\n"
                        f"📊 الرصيد قبل: {balance_before:.6f}$\n"
                        f"💵 الرصيد بعد: {balance_after:.6f}$"
                    )
                else:
                    send_message(chat_id, "❌ فشل في خصم الرصيد (رصيد غير كافٍ).")
            
            except ValueError:
                send_message(chat_id, "❌ بيانات غير صالحة.\n\nالاستخدام: /removebalance USER_ID AMOUNT")
        
        elif len(parts) == 2:
            # بدء عملية خصم الرصيد خطوة بخطوة
            try:
                target_user_id = int(parts[1])
                
                # حفظ حالة الأدمن
                user_states[user_id] = {
                    'state': STATE_WAITING_ADMIN_REMOVE_BALANCE,
                    'target_user_id': target_user_id
                }
                
                send_message(
                    chat_id,
                    f"💸 <b>خصم رصيد من المستخدم {target_user_id}</b>\n\n"
                    f"الآن أرسل المبلغ الذي تريد خصمه:"
                )
            
            except ValueError:
                send_message(chat_id, "❌ معرف المستخدم غير صالح.\n\nالاستخدام: /removebalance USER_ID")
        
        else:
            send_message(
                chat_id,
                "📝 <b>خصم رصيد من مستخدم:</b>\n\n"
                "الاستخدام:\n"
                "<code>/removebalance USER_ID AMOUNT</code>\n\n"
                "أو:\n"
                "<code>/removebalance USER_ID</code> (ثم إرسال المبلغ)"
            )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_remove_balance_command: {str(e)}")
        logErrorWithDetails("admin_remove_balance_error", str(e), user_id)


def handle_admin_remove_balance_input(chat_id, user_id, text):
    """
    معالجة إدخال مبلغ خصم الرصيد (أدمن)
    Handle admin remove balance amount input
    """
    try:
        user_state = user_states.get(user_id, {})
        target_user_id = user_state.get('target_user_id')
        
        if not target_user_id:
            send_message(chat_id, "❌ خطأ: لم يتم تحديد المستخدم.")
            if user_id in user_states:
                del user_states[user_id]
            return
        
        try:
            amount = float(text)
            
            if amount <= 0:
                send_message(chat_id, "❌ المبلغ يجب أن يكون موجباً.\n\nالرجاء إرسال مبلغ صحيح:")
                return
            
            # خصم الرصيد
            balance_before = getBalance(target_user_id)
            if deductBalance(target_user_id, amount):
                balance_after = getBalance(target_user_id)
                
                # تسجيل العملية
                logBalanceOperation(target_user_id, "remove_by_admin", amount, balance_before, balance_after)
                logAdminOperation(user_id, "/removebalance", target_user_id, f"Amount:{amount}$")
                
                send_message(
                    chat_id,
                    f"✅ <b>تم خصم الرصيد بنجاح!</b>\n\n"
                    f"👤 المستخدم: {target_user_id}\n"
                    f"💰 المبلغ: {amount}$\n"
                    f"📊 الرصيد قبل: {balance_before:.6f}$\n"
                    f"💵 الرصيد بعد: {balance_after:.6f}$"
                )
            else:
                send_message(chat_id, "❌ فشل في خصم الرصيد (رصيد غير كافٍ).")
        
        except ValueError:
            send_message(chat_id, "❌ مبلغ غير صالح.\n\nالرجاء إرسال رقم صحيح:")
            return
        
        # مسح الحالة
        if user_id in user_states:
            del user_states[user_id]
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_remove_balance_input: {str(e)}")
        logErrorWithDetails("admin_remove_balance_input_error", str(e), user_id)


def handle_admin_set_percent(chat_id, user_id, text):
    """
    معالجة أمر تعيين التسعير النسبي (أدمن فقط)
    Handle admin set percent pricing command
    """
    try:
        if not validateAdminCommand(user_id, "/setpercent"):
            send_message(chat_id, "❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return
        
        parts = text.split()
        
        if len(parts) != 2:
            send_message(chat_id, "❌ الاستخدام: /setpercent VALUE\n\nمثال: /setpercent 50")
            return
        
        try:
            percent_value = float(parts[1])
            
            if percent_value < 0:
                send_message(chat_id, "❌ النسبة يجب أن تكون موجبة أو صفر.")
                return
            
            if setPercentPricing(percent_value):
                # تسجيل العملية
                logPricingOperation(user_id, "percent", percent_value)
                logAdminOperation(user_id, "/setpercent", details=f"Percent:{percent_value}%")
                
                send_message(
                    chat_id,
                    f"✅ <b>تم تعيين التسعير بنجاح!</b>\n\n"
                    f"📊 النوع: نسبة مئوية\n"
                    f"📌 القيمة: {percent_value}%\n\n"
                    f"💡 سيتم إضافة {percent_value}% على السعر الأصلي"
                )
            else:
                send_message(chat_id, "❌ فشل في تعيين التسعير.")
        
        except ValueError:
            send_message(chat_id, "❌ قيمة غير صالحة.\n\nالاستخدام: /setpercent VALUE")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_set_percent: {str(e)}")
        logErrorWithDetails("admin_set_percent_error", str(e), user_id)


def handle_admin_set_fixed_price(chat_id, user_id, text):
    """
    معالجة أمر تعيين التسعير الثابت (أدمن فقط)
    Handle admin set fixed pricing command
    """
    try:
        if not validateAdminCommand(user_id, "/setprice"):
            send_message(chat_id, "❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return
        
        parts = text.split()
        
        if len(parts) != 2:
            send_message(chat_id, "❌ الاستخدام: /setprice VALUE\n\nمثال: /setprice 5")
            return
        
        try:
            fixed_value = float(parts[1])
            
            if fixed_value < 0:
                send_message(chat_id, "❌ المبلغ يجب أن يكون موجب أو صفر.")
                return
            
            if setFixedPricing(fixed_value):
                # تسجيل العملية
                logPricingOperation(user_id, "fixed", fixed_value)
                logAdminOperation(user_id, "/setprice", details=f"Fixed:{fixed_value}$")
                
                send_message(
                    chat_id,
                    f"✅ <b>تم تعيين التسعير بنجاح!</b>\n\n"
                    f"📊 النوع: مبلغ ثابت\n"
                    f"📌 القيمة: {fixed_value}$\n\n"
                    f"💡 سيتم إضافة {fixed_value}$ على السعر الأصلي"
                )
            else:
                send_message(chat_id, "❌ فشل في تعيين التسعير.")
        
        except ValueError:
            send_message(chat_id, "❌ قيمة غير صالحة.\n\nالاستخدام: /setprice VALUE")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_set_fixed_price: {str(e)}")
        logErrorWithDetails("admin_set_fixed_error", str(e), user_id)


def handle_admin_show_pricing(chat_id, user_id):
    """
    معالجة أمر عرض التسعير الحالي (أدمن فقط)
    Handle admin show pricing command
    """
    try:
        if not validateAdminCommand(user_id, "/price"):
            send_message(chat_id, "❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return
        
        pricing_info = getPricingInfo()
        
        # زر العودة
        keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, pricing_info, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_show_pricing: {str(e)}")
        logErrorWithDetails("admin_show_pricing_error", str(e), user_id)


def handle_admin_user_id_input(chat_id, user_id, text):
    """
    معالجة إدخال معرف المستخدم من الأدمن
    Handle admin user ID input
    """
    try:
        # هذه الدالة احتياطية في حال الحاجة إليها مستقبلاً
        send_message(chat_id, "⚠️ هذه الحالة غير مستخدمة حالياً.")
        
        if user_id in user_states:
            del user_states[user_id]
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_user_id_input: {str(e)}")
        logErrorWithDetails("admin_user_id_input_error", str(e), user_id)
