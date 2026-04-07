# -*- coding: utf-8 -*-
"""
المنطق الرئيسي للبوت - نسخة محسنة وجذرية
Main bot logic - Improved & Radical Version
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
    USER_LOCK_TIMEOUT
)
from users_manager import (
    getBalance, 
    addBalance, 
    deductBalance, 
    getUserInfo,
    getAllUserIds,
    getAllUsersCount
)
from pricing_system import (
    calculatePrice,
    setPercentPricing,
    setFixedPricing,
    getPricingInfo,
    calculateOrderTotalPrice
)
from admin_system import (
    isAdmin, 
    validateAdminCommand,
    checkAdminAccess,
    isAdminConfigured,
    getAdminId
)
from lock_system import acquireLock, releaseLock, isLocked
from advanced_logger import (
    logBalanceOperation,
    logOrderOperation,
    logPricingOperation,
    logAdminOperation,
    logErrorWithDetails,
    logBroadcastOperation
)

# إنشاء كائن API
smm_api = SMM_API()

# قاموس لتخزين حالة المستخدمين والبيانات المؤقتة
user_states = {}


def handle_update(update):
    """
    المعالجة الرئيسية للتحديثات
    Main update handler
    """
    try:
        if 'callback_query' in update:
            handle_callback_query(update['callback_query'])
        elif 'message' in update:
            handle_message(update['message'])
    except Exception as e:
        log_error(f"❌ خطأ في handle_update: {str(e)}")
        logErrorWithDetails("handle_update_error", str(e))


def handle_message(message):
    """
    معالجة الرسائل الواردة
    Handle incoming messages
    """
    try:
        chat_id = message.get('chat', {}).get('id')
        text = message.get('text', '').strip()
        user_id = message.get('from', {}).get('id')
        username = message.get('from', {}).get('username', 'لا يوجد')
        first_name = message.get('from', {}).get('first_name', 'مستخدم')
        
        if not chat_id or not user_id:
            return
        
        # تسجيل المستخدم تلقائياً
        user_states.setdefault(user_id, {})
        
        user_state = user_states.get(user_id, {})
        state = user_state.get('state')
        
        # معالجة حالات الانتظار
        if state == STATE_WAITING_LINK:
            handle_link_input(chat_id, user_id, text)
        elif state == STATE_WAITING_QUANTITY:
            handle_quantity_input(chat_id, user_id, text)
        elif state == STATE_WAITING_ADMIN_ADD_BALANCE:
            handle_admin_add_balance_input(chat_id, user_id, text)
        elif state == STATE_WAITING_ADMIN_REMOVE_BALANCE:
            handle_admin_remove_balance_input(chat_id, user_id, text)
        elif state == 'WAITING_BROADCAST':
            handle_broadcast_message_input(chat_id, user_id, text)
        
        # معالجة الأوامر
        elif text == '/start':
            handle_start_command(chat_id, user_id, first_name, username)
        elif text == '/balance' or text == '💰 رصيدي':
            handle_balance(chat_id, user_id)
        elif text == '/services' or text == '🛒 الخدمات':
            handle_services(chat_id, user_id)
        elif text == '/myaccount' or text == '👤 حسابي':
            handle_my_account(chat_id, user_id, first_name, username)
        elif text == '💳 الدفع / الاشتراك':
            handle_payment_info(chat_id, user_id)
        elif text == '🔄 تحديث':
            handle_refresh(chat_id, user_id, first_name, username)
        
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
        elif text == '/broadcast':
            handle_broadcast_command(chat_id, user_id)
        
        else:
            send_message(chat_id, "👋 مرحباً! استخدم الأزرار في الأسفل للتعامل مع البوت.")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_message: {str(e)}")
        logErrorWithDetails("handle_message_error", str(e), user_id if 'user_id' in locals() else None)


def handle_callback_query(callback_query):
    """
    معالجة استفسارات Inline Keyboard
    Handle Inline Keyboard callback queries
    """
    try:
        chat_id = callback_query.get('message', {}).get('chat', {}).get('id')
        data = callback_query.get('data')
        user_id = callback_query.get('from', {}).get('id')
        username = callback_query.get('from', {}).get('username', 'لا يوجد')
        first_name = callback_query.get('from', {}).get('first_name', 'مستخدم')
        callback_query_id = callback_query.get('id')
        
        if not data or not chat_id:
            answer_callback_query(callback_query_id)
            return
        
        # التحقق من القفل
        if isLocked(user_id, USER_LOCK_TIMEOUT):
            answer_callback_query(callback_query_id, text="⏳ يرجى الانتظار، جاري معالجة طلب سابق...", show_alert=True)
            return
        
        answer_callback_query(callback_query_id)
        
        log_error(f"🔘 Callback: {data} | User: {user_id}")
        
        # معالجة البيانات
        if data == 'balance':
            handle_balance(chat_id, user_id)
        elif data == 'services':
            handle_services(chat_id, user_id)
        elif data == 'my_account':
            handle_my_account(chat_id, user_id, first_name, username)
        elif data == 'payment_info':
            handle_payment_info(chat_id, user_id)
        elif data == 'refresh':
            handle_refresh(chat_id, user_id, first_name, username)
        elif data.startswith('service_'):
            service_id = data.replace('service_', '')
            handle_service_selection(chat_id, user_id, service_id)
        elif data.startswith('page_'):
            page_number = int(data.replace('page_', ''))
            handle_services(chat_id, user_id, page_number)
        elif data == 'confirm_order':
            handle_order_confirmation(chat_id, user_id)
        elif data == 'cancel_order':
            handle_order_cancel(chat_id, user_id)
        elif data == 'back':
            handle_start_command(chat_id, user_id, first_name, username)
        elif data.startswith('status_'):
            order_id = data.replace('status_', '')
            handle_order_status(chat_id, user_id, order_id)
        else:
            log_error(f"⚠️ Callback غير معروف: {data}")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_callback_query: {str(e)}")
        logErrorWithDetails("handle_callback_error", str(e), user_id if 'user_id' in locals() else None)


def handle_start_command(chat_id, user_id, first_name="مستخدم", username="لا يوجد"):
    """
    معالجة أمر /start - مع فحص جذري للأدمن
    Handle /start command - With radical admin check
    """
    try:
        # مسح حالة المستخدم
        if user_id in user_states:
            del user_states[user_id]
        releaseLock(user_id)
        
        # فحص جذري للأدمن
        admin_check = checkAdminAccess(user_id, "start_command")
        is_admin = admin_check['access_granted']
        
        # رسالة الترحيب
        welcome_text = f"👋 <b>أهلاً بك {first_name}!</b>\n\n"
        welcome_text += "🤖 <b>بوت SMM المتقدم</b>\n\n"
        welcome_text += "✅ خدمات سوشيال ميديا بجودة عالية\n"
        welcome_text += "💰 أسعار منافسة\n"
        welcome_text += "⚡ تنفيذ سريع\n"
        welcome_text += "📞 دعم فني 24/7\n\n"
        welcome_text += "اختر من القائمة 👇"
        
        # بناء الأزرار - مختلف للأدمن والمستخدم العادي
        if is_admin:
            # أزرار الأدمن - بدون زر التواصل مع الأدمن
            keyboard = [
                [{'text': '💰 رصيدي', 'callback_data': 'balance'}, {'text': '🛒 الخدمات', 'callback_data': 'services'}],
                [{'text': '👤 حسابي', 'callback_data': 'my_account'}],
                [{'text': '💳 الدفع / الاشتراك', 'callback_data': 'payment_info'}, {'text': '🔄 تحديث', 'callback_data': 'refresh'}],
                [{'text': '👑 لوحة الأدمن', 'callback_data': 'admin_panel'}]
            ]
            log_error(f"👑 Admin {user_id} accessed start menu with admin privileges")
        else:
            # أزرار المستخدم العادي - مع زر التواصل مع الأدمن
            keyboard = [
                [{'text': '💰 رصيدي', 'callback_data': 'balance'}, {'text': '🛒 الخدمات', 'callback_data': 'services'}],
                [{'text': '👤 حسابي', 'callback_data': 'my_account'}],
                [{'text': '📞 التواصل مع الادمن', 'callback_data': 'contact_admin'}, {'text': '💳 الدفع / الاشتراك', 'callback_data': 'payment_info'}],
                [{'text': '🔄 تحديث', 'callback_data': 'refresh'}]
            ]
        
        reply_markup = build_inline_keyboard(keyboard)
        send_message(chat_id, welcome_text, reply_markup)
        
        log_error(f"✅ Start command sent to user {user_id} (Admin: {is_admin})")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_start_command: {str(e)}")
        logErrorWithDetails("start_command_error", str(e), user_id)


def handle_my_account(chat_id, user_id, first_name="مستخدم", username="لا يوجد"):
    """
    عرض معلومات حساب المستخدم
    Show user account information
    """
    try:
        user_info = getUserInfo(user_id)
        balance = user_info['balance']
        
        text = f"👤 <b>معلومات حسابك:</b>\n\n"
        text += f"👤 الاسم: {first_name}\n"
        text += f"📧 Username: @{username}\n"
        text += f"🆔 <b>ID:</b> <code>{user_id}</code>\n"
        text += f"💰 <b>الرصيد:</b> {balance:.6f}$\n\n"
        text += f"💡 <b>ملاحظة:</b> عند شحن الرصيد، أرسل هذا ID للأدمن"
        
        keyboard = [
            [{'text': '🔄 تحديث', 'callback_data': 'refresh'}],
            [{'text': '🔙 عودة', 'callback_data': 'back'}]
        ]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_my_account: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ أثناء جلب معلومات الحساب.")
        logErrorWithDetails("my_account_error", str(e), user_id)


def handle_balance(chat_id, user_id):
    """
    معالجة طلب الرصيد
    Handle balance request
    """
    try:
        balance = getBalance(user_id)
        
        text = f"💰 <b>رصيدك الحالي:</b>\n\n"
        text += f"💵 <b>{balance:.6f}$</b>\n\n"
        text += f"💡 استخدم زر الطلب لشراء الخدمات"
        
        keyboard = [
            [{'text': '🛒 الخدمات', 'callback_data': 'services'}],
            [{'text': '🔄 تحديث', 'callback_data': 'refresh'}],
            [{'text': '🔙 عودة', 'callback_data': 'back'}]
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
        services = smm_api.services()
        
        if not services:
            send_message(chat_id, "❌ لا توجد خدمات متاحة حالياً.")
            return
        
        services_per_page = 10
        total_pages = (len(services) + services_per_page - 1) // services_per_page
        
        start_idx = page * services_per_page
        end_idx = min(start_idx + services_per_page, len(services))
        page_services = services[start_idx:end_idx]
        
        text = f"<b>🛒 اختر الخدمة (صفحة {page + 1}/{total_pages}):</b>\n\n"
        
        for idx, service in enumerate(page_services, start_idx + 1):
            name = service.get('name', 'خدمة غير معروفة')[:50]
            base_rate = float(service.get('rate', 0))
            service_id = service.get('service', 0)
            final_rate = calculatePrice(base_rate)
            
            text += f"{idx}. <b>{name}</b>\n"
            text += f"   💵 السعر: ${final_rate:.6f} لكل 1000\n"
            text += f"   🆔 ID: <code>{service_id}</code>\n\n"
        
        buttons = []
        for service in page_services:
            service_id = service.get('service', 0)
            name = service.get('name', 'خدمة')[:40]
            buttons.append([{'text': f'📍 {name}', 'callback_data': f'service_{service_id}'}])
        
        nav_buttons = []
        if page > 0:
            nav_buttons.append({'text': '⬅️ السابق', 'callback_data': f'page_{page-1}'})
        if page < total_pages - 1:
            nav_buttons.append({'text': 'التالي ➡️', 'callback_data': f'page_{page+1}'})
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([{'text': '🔙 عودة', 'callback_data': 'back'}])
        
        reply_markup = build_inline_keyboard(buttons)
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_services: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ أثناء جلب الخدمات.")
        logErrorWithDetails("services_error", str(e), user_id)


def handle_service_selection(chat_id, user_id, service_id):
    """
    معالجة اختيار خدمة
    Handle service selection
    """
    try:
        if not acquireLock(user_id, USER_LOCK_TIMEOUT):
            send_message(chat_id, "⏳ لديك طلب قيد المعالجة. يرجى الانتظار.")
            return
        
        user_states[user_id] = {
            'state': STATE_WAITING_LINK,
            'service_id': service_id
        }
        
        text = f"✅ <b>تم اختيار الخدمة: {service_id}</b>\n\n"
        text += "الآن أرسل <b>الرابط</b> الذي تريد العمل عليه:"
        
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
        if not link or not link.startswith('http'):
            send_message(chat_id, "❌ الرابط غير صالح.\n\nيرجى إرسال رابط صحيح يبدأ بـ http:// أو https://")
            return
        
        user_states[user_id]['link'] = link
        user_states[user_id]['state'] = STATE_WAITING_QUANTITY
        
        text = f"✅ <b>تم حفظ الرابط:</b>\n{link}\n\n"
        text += "الآن أرسل <b>الكمية</b> المطلوبة:"
        
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
        try:
            quantity = int(quantity_text)
            if quantity <= 0:
                raise ValueError("الكمية يجب أن تكون موجبة")
        except ValueError:
            send_message(chat_id, "❌ الكمية غير صالحة.\n\nيرجى إرسال رقم صحيح موجب.")
            return
        
        user_states[user_id]['quantity'] = quantity
        
        service_id = user_states[user_id].get('service_id')
        link = user_states[user_id].get('link')
        
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
        
        summary_text = f"<b>📋 ملخص طلبك:</b>\n\n"
        summary_text += f"🔖 الخدمة: {service_id}\n"
        summary_text += f"🔗 الرابط: {link}\n"
        summary_text += f"🔢 الكمية: {quantity}\n"
        summary_text += f"💵 <b>السعر الإجمالي: ${price_info['final_price']:.6f}</b>\n\n"
        summary_text += "هل تريد تأكيد الطلب؟"
        
        buttons = [[
            {'text': '✅ تأكيد', 'callback_data': 'confirm_order'},
            {'text': '❌ إلغاء', 'callback_data': 'cancel_order'}
        ]]
        
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
        user_state = user_states.get(user_id, {})
        
        service_id = user_state.get('service_id')
        link = user_state.get('link')
        quantity = user_state.get('quantity')
        
        if not all([service_id, link, quantity]):
            send_message(chat_id, "❌ بيانات الطلب غير مكتممة.")
            releaseLock(user_id)
            return
        
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
        
        current_balance = getBalance(user_id)
        if current_balance < final_price:
            send_message(chat_id, f"❌ <b>رصيدك غير كافٍ!</b>\n\n💰 رصيدك: {current_balance:.6f}$\n💵 المطلوب: {final_price:.6f}$\n📉 العجز: {final_price - current_balance:.6f}$\n\nيرجى شحن رصيدك أولاً.")
            releaseLock(user_id)
            return
        
        balance_before = current_balance
        if not deductBalance(user_id, final_price):
            send_message(chat_id, "❌ فشل في خصم الرصيد. يرجى المحاولة لاحقاً.")
            releaseLock(user_id)
            return
        
        balance_after = getBalance(user_id)
        logBalanceOperation(user_id, "deduct", final_price, balance_before, balance_after)
        
        order_id = smm_api.order(service_id, link, quantity)
        
        if order_id:
            text = f"✅ <b>تم تقديم طلبك بنجاح!</b>\n\n"
            text += f"🔢 معرف الطلب: {order_id}\n"
            text += f"🔖 الخدمة: {service_id}\n"
            text += f"🔢 الكمية: {quantity}\n"
            text += f"💵 المبلغ المخصوم: {final_price:.6f}$\n"
            text += f"💰 رصيدك الجديد: {balance_after:.6f}$\n\n"
            text += "يمكنك التحقق من حالة الطلب لاحقاً."
            
            buttons = [[{'text': '📊 حالة الطلب', 'callback_data': f'status_{order_id}'}]]
            reply_markup = build_inline_keyboard(buttons)
            
            send_message(chat_id, text, reply_markup)
            logOrderOperation(user_id, order_id, service_id, quantity, final_price, "success")
            log_error(f"✅ Order successful for user {user_id} - Order ID: {order_id}")
        else:
            addBalance(user_id, final_price)
            balance_after_refund = getBalance(user_id)
            logBalanceOperation(user_id, "refund", final_price, balance_after, balance_after_refund)
            
            send_message(chat_id, "❌ فشل تقديم الطلب.\n\nتم استرجاع المبلغ إلى رصيدك تلقائياً.\nيرجى المحاولة لاحقاً أو التواصل مع الدعم.")
            logOrderOperation(user_id, "failed", service_id, quantity, final_price, "failed")
        
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
        if user_id in user_states:
            del user_states[user_id]
        releaseLock(user_id)
        
        send_message(chat_id, "❌ <b>تم إلغاء العملية.</b>\n\nاستخدم /start للبدء من جديد.")
    
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
            
            keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
            reply_markup = build_inline_keyboard(keyboard)
            send_message(chat_id, text, reply_markup)
        else:
            send_message(chat_id, "❌ لم يتم العثور على معلومات الطلب.")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_order_status: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ أثناء جلب حالة الطلب.")
        logErrorWithDetails("order_status_error", str(e), user_id, f"order_id:{order_id}")


def handle_payment_info(chat_id, user_id):
    """
    معالجة طلب معلومات الدفع - مع إظهار ID المستخدم
    Handle payment info request - With user ID displayed
    """
    try:
        text = f"💳 <b>طرق الدفع المتاحة:</b>\n\n"
        text += f"🆔 <b>ID الخاص بك:</b> <code>{user_id}</code>\n\n"
        text += f"📌 <b>مهم:</b> أرسل هذا ID للأدمن عند شحن الرصيد\n\n"
        text += f"🏦 <b>التحويل البنكي:</b>\n"
        text += f"Bank: Example Bank\n"
        text += f"Account: 1234567890\n\n"
        text += f"💰 <b>PayPal:</b>\n"
        text += f"Email: paypal@example.com\n\n"
        text += f"📱 <b>وسائل دفع أخرى:</b>\n"
        text += f"يرجى التواصل مع الأدمن\n\n"
        text += f"⚠️ بعد الدفع، أرسل إثبات الدفع للأدمن مع ID الخاص بك"
        
        keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_payment_info: {str(e)}")
        logErrorWithDetails("payment_info_error", str(e), user_id)


def handle_refresh(chat_id, user_id, first_name="مستخدم", username="لا يوجد"):
    """
    معالجة زر التحديث - تحديث شامل
    Handle refresh button - Comprehensive refresh
    """
    try:
        balance = getBalance(user_id)
        
        text = f"✅ <b>تم تحديث بياناتك بنجاح!</b>\n\n"
        text += f"👤 الاسم: {first_name}\n"
        text += f"🆔 ID: <code>{user_id}</code>\n"
        text += f"💰 <b>الرصيد:</b> {balance:.6f}$\n\n"
        text += f"🔄 تم تحديث الأسعار والخدمات"
        
        # فحص جذري للأدمن
        admin_check = checkAdminAccess(user_id, "refresh")
        is_admin = admin_check['access_granted']
        
        if is_admin:
            keyboard = [
                [{'text': '💰 رصيدي', 'callback_data': 'balance'}, {'text': '🛒 الخدمات', 'callback_data': 'services'}],
                [{'text': '👤 حسابي', 'callback_data': 'my_account'}],
                [{'text': '💳 الدفع / الاشتراك', 'callback_data': 'payment_info'}, {'text': '🔄 تحديث', 'callback_data': 'refresh'}],
                [{'text': '👑 لوحة الأدمن', 'callback_data': 'admin_panel'}]
            ]
        else:
            keyboard = [
                [{'text': '💰 رصيدي', 'callback_data': 'balance'}, {'text': '🛒 الخدمات', 'callback_data': 'services'}],
                [{'text': '👤 حسابي', 'callback_data': 'my_account'}],
                [{'text': '📞 التواصل مع الادمن', 'callback_data': 'contact_admin'}, {'text': '💳 الدفع / الاشتراك', 'callback_data': 'payment_info'}],
                [{'text': '🔄 تحديث', 'callback_data': 'refresh'}]
            ]
        
        reply_markup = build_inline_keyboard(keyboard)
        send_message(chat_id, text, reply_markup)
        
        log_error(f"🔄 Refreshed data for user {user_id} (Admin: {is_admin})")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_refresh: {str(e)}")
        logErrorWithDetails("refresh_error", str(e), user_id)


def handle_contact_admin(chat_id, user_id):
    """
    معالجة طلب التواصل مع الأدمن
    Handle contact admin request
    """
    try:
        text = f"📞 <b>للتواصل مع الأدمن:</b>\n\n"
        text += f"📱 Telegram: @YourAdminUsername\n"
        text += f"📧 Email: admin@example.com\n\n"
        text += f"🆔 ID الخاص بك: <code>{user_id}</code>\n"
        text += f"💡 أرسل هذا ID عند التواصل\n\n"
        text += f"⏰ أوقات العمل: 24/7\n"
        text += f"💬 نحن هنا لمساعدتك!"
        
        keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_contact_admin: {str(e)}")
        logErrorWithDetails("contact_admin_error", str(e), user_id)


# ========== أوامر الأدمن ==========


def handle_admin_add_balance_command(chat_id, user_id, text):
    """
    معالجة أمر إضافة الرصيد (أدمن فقط) - فحص جذري
    Handle admin add balance command - Radical check
    """
    try:
        if not validateAdminCommand(user_id, "/addbalance"):
            send_message(chat_id, "❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return
        
        parts = text.split()
        
        if len(parts) == 3:
            try:
                target_user_id = int(parts[1])
                amount = float(parts[2])
                
                if amount <= 0:
                    send_message(chat_id, "❌ المبلغ يجب أن يكون موجباً.")
                    return
                
                balance_before = getBalance(target_user_id)
                if addBalance(target_user_id, amount):
                    balance_after = getBalance(target_user_id)
                    
                    logBalanceOperation(target_user_id, "add_by_admin", amount, balance_before, balance_after)
                    logAdminOperation(user_id, "/addbalance", target_user_id, f"Amount:{amount}$")
                    
                    send_message(chat_id, f"✅ <b>تم إضافة الرصيد بنجاح!</b>\n\n👤 المستخدم: {target_user_id}\n💰 المبلغ: {amount}$\n📊 الرصيد قبل: {balance_before:.6f}$\n💵 الرصيد بعد: {balance_after:.6f}$")
                else:
                    send_message(chat_id, "❌ فشل في إضافة الرصيد.")
            
            except ValueError:
                send_message(chat_id, "❌ بيانات غير صالحة.\n\nالاستخدام: /addbalance USER_ID AMOUNT")
        
        elif len(parts) == 2:
            try:
                target_user_id = int(parts[1])
                user_states[user_id] = {
                    'state': STATE_WAITING_ADMIN_ADD_BALANCE,
                    'target_user_id': target_user_id
                }
                send_message(chat_id, f"💰 <b>إضافة رصيد للمستخدم {target_user_id}</b>\n\nالآن أرسل المبلغ:")
            except ValueError:
                send_message(chat_id, "❌ معرف المستخدم غير صالح.")
        
        else:
            send_message(chat_id, "📝 <b>إضافة رصيد:</b>\n\n<code>/addbalance USER_ID AMOUNT</code>\n\nأو:\n<code>/addbalance USER_ID</code>")
    
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
                send_message(chat_id, "❌ المبلغ يجب أن يكون موجباً.")
                return
            
            balance_before = getBalance(target_user_id)
            if addBalance(target_user_id, amount):
                balance_after = getBalance(target_user_id)
                
                logBalanceOperation(target_user_id, "add_by_admin", amount, balance_before, balance_after)
                logAdminOperation(user_id, "/addbalance", target_user_id, f"Amount:{amount}$")
                
                send_message(chat_id, f"✅ <b>تم إضافة الرصيد بنجاح!</b>\n\n👤 المستخدم: {target_user_id}\n💰 المبلغ: {amount}$\n📊 الرصيد قبل: {balance_before:.6f}$\n💵 الرصيد بعد: {balance_after:.6f}$")
            else:
                send_message(chat_id, "❌ فشل في إضافة الرصيد.")
        
        except ValueError:
            send_message(chat_id, "❌ مبلغ غير صالح. أرسل رقم صحيح:")
            return
        
        if user_id in user_states:
            del user_states[user_id]
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_add_balance_input: {str(e)}")
        logErrorWithDetails("admin_add_balance_input_error", str(e), user_id)


def handle_admin_remove_balance_command(chat_id, user_id, text):
    """
    معالجة أمر خصم الرصيد (أدمن فقط) - فحص جذري
    Handle admin remove balance command - Radical check
    """
    try:
        if not validateAdminCommand(user_id, "/removebalance"):
            send_message(chat_id, "❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return
        
        parts = text.split()
        
        if len(parts) == 3:
            try:
                target_user_id = int(parts[1])
                amount = float(parts[2])
                
                if amount <= 0:
                    send_message(chat_id, "❌ المبلغ يجب أن يكون موجباً.")
                    return
                
                balance_before = getBalance(target_user_id)
                if deductBalance(target_user_id, amount):
                    balance_after = getBalance(target_user_id)
                    
                    logBalanceOperation(target_user_id, "remove_by_admin", amount, balance_before, balance_after)
                    logAdminOperation(user_id, "/removebalance", target_user_id, f"Amount:{amount}$")
                    
                    send_message(chat_id, f"✅ <b>تم خصم الرصيد بنجاح!</b>\n\n👤 المستخدم: {target_user_id}\n💰 المبلغ: {amount}$\n📊 الرصيد قبل: {balance_before:.6f}$\n💵 الرصيد بعد: {balance_after:.6f}$")
                else:
                    send_message(chat_id, "❌ فشل في خصم الرصيد (رصيد غير كافٍ).")
            
            except ValueError:
                send_message(chat_id, "❌ بيانات غير صالحة.\n\nالاستخدام: /removebalance USER_ID AMOUNT")
        
        elif len(parts) == 2:
            try:
                target_user_id = int(parts[1])
                user_states[user_id] = {
                    'state': STATE_WAITING_ADMIN_REMOVE_BALANCE,
                    'target_user_id': target_user_id
                }
                send_message(chat_id, f"💸 <b>خصم رصيد من المستخدم {target_user_id}</b>\n\nالآن أرسل المبلغ:")
            except ValueError:
                send_message(chat_id, "❌ معرف المستخدم غير صالح.")
        
        else:
            send_message(chat_id, "📝 <b>خصم رصيد:</b>\n\n<code>/removebalance USER_ID AMOUNT</code>\n\nأو:\n<code>/removebalance USER_ID</code>")
    
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
                send_message(chat_id, "❌ المبلغ يجب أن يكون موجباً.")
                return
            
            balance_before = getBalance(target_user_id)
            if deductBalance(target_user_id, amount):
                balance_after = getBalance(target_user_id)
                
                logBalanceOperation(target_user_id, "remove_by_admin", amount, balance_before, balance_after)
                logAdminOperation(user_id, "/removebalance", target_user_id, f"Amount:{amount}$")
                
                send_message(chat_id, f"✅ <b>تم خصم الرصيد بنجاح!</b>\n\n👤 المستخدم: {target_user_id}\n💰 المبلغ: {amount}$\n📊 الرصيد قبل: {balance_before:.6f}$\n💵 الرصيد بعد: {balance_after:.6f}$")
            else:
                send_message(chat_id, "❌ فشل في خصم الرصيد (رصيد غير كافٍ).")
        
        except ValueError:
            send_message(chat_id, "❌ مبلغ غير صالح. أرسل رقم صحيح:")
            return
        
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
                logPricingOperation(user_id, "percent", percent_value)
                logAdminOperation(user_id, "/setpercent", details=f"Percent:{percent_value}%")
                
                send_message(chat_id, f"✅ <b>تم تعيين التسعير بنجاح!</b>\n\n📊 النوع: نسبة مئوية\n📌 القيمة: {percent_value}%\n\n💡 سيتم إضافة {percent_value}% على السعر الأصلي")
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
                logPricingOperation(user_id, "fixed", fixed_value)
                logAdminOperation(user_id, "/setprice", details=f"Fixed:{fixed_value}$")
                
                send_message(chat_id, f"✅ <b>تم تعيين التسعير بنجاح!</b>\n\n📊 النوع: مبلغ ثابت\n📌 القيمة: {fixed_value}$\n\n💡 سيتم إضافة {fixed_value}$ على السعر الأصلي")
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
        keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, pricing_info, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_show_pricing: {str(e)}")
        logErrorWithDetails("admin_show_pricing_error", str(e), user_id)


def handle_broadcast_command(chat_id, user_id):
    """
    معالجة أمر الرسالة الجماعية (أدمن فقط)
    Handle broadcast message command (Admin only)
    """
    try:
        if not validateAdminCommand(user_id, "/broadcast"):
            send_message(chat_id, "❌ ليس لديك صلاحية استخدام هذا الأمر.")
            return
        
        # بدء وضع الرسالة الجماعية
        user_states[user_id] = {
            'state': 'WAITING_BROADCAST'
        }
        
        send_message(
            chat_id,
            "📢 <b>وضع الرسالة الجماعية</b>\n\n"
            "الآن أرسل الرسالة التي تريد إرسالها لجميع المستخدمين.\n\n"
            "⚠️ سيتم إرسال الرسالة لكل المستخدمين المسجلين في البوت."
        )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_broadcast_command: {str(e)}")
        logErrorWithDetails("broadcast_command_error", str(e), user_id)


def handle_broadcast_message_input(chat_id, user_id, message_text):
    """
    معالجة نص الرسالة الجماعية وإرسالها
    Handle broadcast message text input and send to all users
    """
    try:
        # مسح حالة الانتظار
        if user_id in user_states:
            del user_states[user_id]
        
        # الحصول على قائمة جميع المستخدمين
        user_ids = getAllUserIds()
        total_users = len(user_ids)
        
        if total_users == 0:
            send_message(chat_id, "❌ لا يوجد مستخدمين مسجلين في البوت.")
            return
        
        # إشعار الأدمن بالبدء
        send_message(chat_id, f"📢 جاري إرسال الرسالة إلى {total_users} مستخدم...\n\nيرجى الانتظار.")
        
        success_count = 0
        failed_count = 0
        failed_users = []
        
        # إرسال الرسالة لكل مستخدم
        for target_user_id in user_ids:
            try:
                # تخطي إرسال الرسالة للأدمن نفسه إذا كان في القائمة
                if str(target_user_id) == str(user_id):
                    success_count += 1
                    continue
                
                # إرسال الرسالة
                if send_message(target_user_id, message_text):
                    success_count += 1
                    log_error(f"✅ Broadcast sent to user {target_user_id}")
                else:
                    failed_count += 1
                    failed_users.append(target_user_id)
                    log_error(f"❌ Broadcast failed for user {target_user_id}")
            
            except Exception as e:
                failed_count += 1
                failed_users.append(target_user_id)
                log_error(f"❌ Broadcast error for user {target_user_id}: {str(e)}")
        
        # تسجيل العملية
        logBroadcastOperation(user_id, total_users, success_count, failed_count, message_text)
        
        # إرسال تقرير للأدمن
        report = f"✅ <b>تم إرسال الرسالة الجماعية!</b>\n\n"
        report += f"👥 إجمالي المستخدمين: {total_users}\n"
        report += f"✅ تم الإرسال بنجاح: {success_count}\n"
        report += f"❌ فشل الإرسال: {failed_count}\n"
        
        if failed_users:
            report += f"\n📋 المستخدمون الذين فشل الإرسال لهم:\n"
            report += ", ".join([str(uid) for uid in failed_users[:10]])
            if len(failed_users) > 10:
                report += f" ...و {len(failed_users) - 10} آخرين"
        
        send_message(chat_id, report)
        log_error(f"📢 Broadcast completed: Total:{total_users} | Success:{success_count} | Failed:{failed_count}")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_broadcast_message_input: {str(e)}")
        logErrorWithDetails("broadcast_message_error", str(e), user_id)
