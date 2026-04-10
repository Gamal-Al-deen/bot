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
    getAllUsersCount,
    isNewUser,
    registerUser,
    userExists,
    isNewUserNotificationsEnabled,
    toggleNewUserNotifications,
    getChannelUsername,
    isChannelConfigured,
    setChannelUsername
)
from pricing_system import (
    calculatePrice,
    setPercentPricing,
    setFixedPricing,
    getPricingInfo,
    calculateOrderTotalPrice
)
from database import (
    create_order as db_create_order
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
from channel_handler import handle_channel_username_input as _channel_handler
from service_manager import (
    getAllCategories,
    addCategory,
    deleteCategory,
    addServiceToCategory,
    deleteServiceFromCategory,
    getServicesByCategory,
    getAllServicesFlat,
    getServiceInfo
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
        elif state == 'WAITING_CHANNEL_USERNAME':
            _channel_handler(chat_id, user_id, text, user_states)
        elif state == 'WAITING_CATEGORY_NAME':
            handle_add_category_input(chat_id, user_id, text)
        elif state in ['WAITING_SERVICE_ID', 'WAITING_SERVICE_CONFIRM']:
            handle_service_id_input(chat_id, user_id, text)
        
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
            # رسالة عادية غير معروفة - عرض الرسالة مع الأزرار
            admin_check = checkAdminAccess(user_id, "unknown_message")
            is_admin = admin_check['access_granted']
            
            text = (
                "👋 مرحباً! استخدم الأزرار في الأسفل للتعامل مع البوت.\n\n"
                "يمكنك استخدام:\n"
                "• /start - لإعادة تشغيل البوت\n"
                "• /balance - لعرض رصيدك\n"
                "• /services - لعرض الخدمات"
            )
            
            # بناء الأزرار حسب نوع المستخدم
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
        elif data == 'admin_panel':
            handle_admin_panel(chat_id, user_id, first_name)
        elif data == 'admin_add_balance':
            handle_admin_add_balance_inline(chat_id, user_id)
        elif data == 'admin_remove_balance':
            handle_admin_remove_balance_inline(chat_id, user_id)
        elif data == 'admin_show_pricing':
            handle_admin_show_pricing_inline(chat_id, user_id)
        elif data == 'admin_broadcast':
            handle_broadcast_command(chat_id, user_id)
        elif data == 'admin_notifications':
            handle_admin_notifications_toggle(chat_id, user_id)
        elif data == 'admin_set_channel':
            handle_admin_set_channel(chat_id, user_id)
        elif data == 'admin_services_management':
            handle_admin_services_menu(chat_id, user_id)
        elif data == 'admin_add_category':
            handle_admin_add_category(chat_id, user_id)
        elif data == 'admin_delete_category':
            handle_admin_delete_category(chat_id, user_id)
        elif data == 'admin_add_service':
            handle_admin_add_service(chat_id, user_id)
        elif data == 'admin_delete_service':
            handle_admin_delete_service(chat_id, user_id)
        elif data == 'confirm_add_service':
            handle_confirm_add_service(chat_id, user_id)
        elif data.startswith('confirm_delete_cat_'):
            category_name = data.replace('confirm_delete_cat_', '')
            handle_confirm_delete_category(chat_id, user_id, category_name)
        elif data.startswith('add_service_to_'):
            category_name = data.replace('add_service_to_', '')
            handle_add_service_to_category(chat_id, user_id, category_name)
        elif data.startswith('confirm_delete_svc_'):
            # Format: confirm_delete_svc_CATEGORY_SERVICEID
            parts = data.replace('confirm_delete_svc_', '').rsplit('_', 1)
            if len(parts) == 2:
                category_name, service_id = parts
                handle_confirm_delete_service(chat_id, user_id, category_name, int(service_id))
        elif data == 'contact_admin':
            handle_contact_admin(chat_id, user_id, username)
        elif data.startswith('category_'):
            category_name = data.replace('category_', '')
            handle_category_services(chat_id, user_id, category_name)
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


def send_new_user_notification(user_id, first_name, username):
    """
    إرسال إشعار للأدمن عند انضمام مستخدم جديد
    Send notification to admin when new user joins
    
    @param user_id: معرف المستخدم الجديد
    @param first_name: الاسم الأول
    @param username: اليوزرنيم
    """
    try:
        # التحقق من تفعيل الإشعارات
        if not isNewUserNotificationsEnabled():
            log_error(f"🔔 إشعارات المستخدمين الجدد متوقفة - تم تخطي الإشعار للمستخدم {user_id}")
            return
        
        # الحصول على معرف الأدمن
        admin_id = getAdminId()
        
        # التحقق من إعداد ADMIN_ID
        if admin_id in ['', 'YOUR_ADMIN_ID_HERE', '0']:
            log_error(f"⚠️ لم يتم إعداد ADMIN_ID - لن يتم إرسال إشعار للمستخدم الجديد {user_id}")
            return
        
        # حساب إجمالي المستخدمين
        total_users = getAllUsersCount()
        
        # تنسيق اليوزرنيم
        username_display = f"@{username}" if username and username != 'لا يوجد' else "لا يوجد"
        
        # نص الإشعار
        notification_text = (
            f"🚀 <b>مستخدم جديد انضم للبوت!</b>\n\n"
            f"👤 <b>الاسم:</b> {first_name}\n"
            f"🔗 <b>اليوزرنيم:</b> {username_display}\n"
            f"🆔 <b>ID:</b> <code>{user_id}</code>\n\n"
            f"👥 <b>إجمالي المستخدمين:</b> {total_users}\n\n"
            f"📅 <b>تاريخ الانضمام:</b> {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # أزرار سريعة للإشعار
        keyboard = [
            [{'text': '💰 إضافة رصيد', 'callback_data': 'admin_add_balance'}],
            [{'text': '👤 عرض الحساب', 'url': f'https://t.me/{username}' if username and username != 'لا يوجد' else None}]
        ]
        
        # إزالة الأزرار التي تحتوي على None
        keyboard = [[btn for btn in row if btn.get('url') or btn.get('callback_data')] for row in keyboard]
        keyboard = [row for row in keyboard if row]  # إزالة الصفوف الفارغة
        
        if keyboard:
            reply_markup = build_inline_keyboard(keyboard)
            send_message(admin_id, notification_text, reply_markup)
        else:
            send_message(admin_id, notification_text)
        
        log_error(f"🔔 تم إرسال إشعار المستخدم الجديد للأدمن: User {user_id} ({first_name}) | Total: {total_users}")
    
    except Exception as e:
        log_error(f"❌ خطأ في send_new_user_notification: {str(e)}")
        logErrorWithDetails("new_user_notification_error", str(e), user_id)


def send_order_notification_to_channel(service_name, price, user_id, username="لا يوجد"):
    """
    إرسال إشعار الطلب إلى القناة المحددة
    Send order notification to configured channel
    
    @param service_name: اسم الخدمة
    @param price: السعر المدفوع
    @param user_id: معرف المستخدم
    @param username: يوزرنيم المستخدم
    """
    try:
        # التحقق من إعداد القناة
        if not isChannelConfigured():
            log_error(f"📣 لم يتم إعداد قناة النشر - تم تخطي إشعار الطلب")
            return False
        
        # الحصول على يوزرنيم القناة
        channel_username = getChannelUsername()
        
        if not channel_username:
            log_error(f"⚠️ يوزرنيم القناة فارغ - لن يتم إرسال الإشعار")
            return False
        
        # تنسيق يوزرنيم المستخدم
        user_display = f"@{username}" if username and username != 'لا يوجد' else f"ID: {user_id}"
        
        # نص الرسالة
        notification_text = (
            f"📢 <b>طلب جديد!</b>\n\n"
            f"🛒 <b>الخدمة:</b> {service_name}\n"
            f"💰 <b>السعر:</b> ${price:.2f}\n"
            f"👤 <b>المستخدم:</b> {user_display}\n\n"
            f"📅 {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # إرسال الرسالة إلى القناة
        # ملاحظة: channel_username يجب أن يكون بدون @
        channel_id = f"@{channel_username}"
        result = send_message(channel_id, notification_text)
        
        if result:
            log_error(f"📣 تم إرسال إشعار الطلب إلى القناة {channel_id}: Service={service_name}, Price=${price:.2f}, User={user_display}")
            return True
        else:
            log_error(f"❌ فشل إرسال إشعار الطلب إلى القناة {channel_id}")
            return False
    
    except Exception as e:
        log_error(f"❌ خطأ في send_order_notification_to_channel: {str(e)}")
        logErrorWithDetails("channel_notification_error", str(e), user_id, f"service:{service_name}")
        return False


def handle_start_command(chat_id, user_id, first_name="مستخدم", username="لا يوجد"):
    """
    معالجة أمر /start - مع فحص جذري للأدمن وإشعار المستخدمين الجدد
    Handle /start command - With radical admin check and new user notification
    """
    try:
        # تسجيل المستخدم أولاً (يتم الحفظ بشكل دائم)
        is_new = registerUser(user_id, first_name, username)
        
        # مسح حالة المستخدم
        if user_id in user_states:
            del user_states[user_id]
        releaseLock(user_id)
        
        # إرسال إشعار للأدمن إذا كان المستخدم جديد
        if is_new:
            send_new_user_notification(user_id, first_name, username)
        
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
        
        log_error(f"✅ Start command sent to user {user_id} (Admin: {is_admin}, New: {is_new})")
    
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
    معالجة طلب قائمة الخدمات - عرض الأقسام والخدمات المضافة من الأدمن فقط
    Handle services list request - Show only admin-added categories and services
    """
    try:
        # الحصول على الأقسام المضافة من الأدمن
        categories = getAllCategories()
        
        if not categories:
            send_message(chat_id, "🚧 <b>الخدمات قيد الإعداد</b>\n\nسيتم إضافة الخدمات قريباً.\nيرجى الانتظار أو التواصل مع الأدمن.")
            return
        
        # عرض قائمة الأقسام
        text = f"📁 <b>اختر القسم:</b>\n\n"
        
        for idx, category in enumerate(categories, 1):
            services_count = len(getServicesByCategory(category))
            text += f"{idx}️⃣ <b>{category}</b>\n"
            text += f"   🛒 الخدمات المتاحة: {services_count}\n\n"
        
        # بناء أزرار الأقسام
        buttons = []
        for category in categories:
            services_count = len(getServicesByCategory(category))
            btn_text = f"📁 {category} ({services_count})"
            buttons.append([{'text': btn_text, 'callback_data': f'category_{category}'}])
        
        buttons.append([{'text': '🔙 عودة', 'callback_data': 'back'}])
        
        reply_markup = build_inline_keyboard(buttons)
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_services: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ أثناء جلب الخدمات.")
        logErrorWithDetails("services_error", str(e), user_id)


def handle_category_services(chat_id, user_id, category_name):
    """
    عرض خدمات قسم معين
    Show services for a specific category
    """
    try:
        services = getServicesByCategory(category_name)
        
        if not services:
            send_message(chat_id, f"❌ لا توجد خدمات في قسم '{category_name}' حالياً.")
            return
        
        text = f"📁 <b>{category_name}</b>\n\n"
        text += f"🛒 <b>الخدمات المتاحة:</b>\n\n"
        
        # بناء أزرار الخدمات
        buttons = []
        for idx, service in enumerate(services, 1):
            service_id = service.get('service_id')
            service_name = service.get('service_name', 'خدمة')
            
            # الحصول على السعر من API
            base_rate = smm_api.get_service_rate(service_id)
            final_rate = calculatePrice(base_rate)
            
            text += f"{idx}. <b>{service_name}</b>\n"
            text += f"   💵 السعر: ${final_rate:.6f} لكل 1000\n"
            text += f"   🆔 ID: <code>{service_id}</code>\n\n"
            
            # زر للخدمة
            btn_text = f"📍 {service_name[:40]}"
            buttons.append([{'text': btn_text, 'callback_data': f'service_{service_id}'}])
        
        buttons.append([{'text': '🔙 العودة للأقسام', 'callback_data': 'services'}])
        
        reply_markup = build_inline_keyboard(buttons)
        send_message(chat_id, text, reply_markup)
        
        log_error(f"📁 User {user_id} viewed category: {category_name} ({len(services)} services)")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_category_services: {str(e)}")
        send_message(chat_id, "❌ حدث خطأ أثناء جلب خدمات القسم.")
        logErrorWithDetails("category_services_error", str(e), user_id)


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
            # Save order to Supabase
            db_order_id = db_create_order(
                user_id=user_id,
                service_api_id=int(service_id),
                original_price=price_info['original_price'],
                final_price=final_price,
                quantity=quantity,
                link=link,
                status='success',
                order_api_id=order_id
            )
            
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
            log_error(f"✅ Order successful for user {user_id} - Order ID: {order_id} - DB ID: {db_order_id}")
            
            # إرسال إشعار إلى القناة (في الخلفية - لا يؤثر على سرعة الطلب)
            try:
                # الحصول على معلومات المستخدم
                user_info = getUserInfo(user_id)
                username = message.get('from', {}).get('username', 'لا يوجد') if 'message' in locals() else 'لا يوجد'
                
                # إرسال الإشعار للقناة
                send_order_notification_to_channel(
                    service_name=f"Service #{service_id}",
                    price=final_price,
                    user_id=user_id,
                    username=username
                )
            except Exception as e:
                # لا نسمح لأي خطأ بالتأثير على الطلب
                log_error(f"⚠️ خطأ في إرسال إشعار القناة (لن يؤثر على الطلب): {str(e)}")
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


def handle_contact_admin(chat_id, user_id, username="لا يوجد"):
    """
    معالجة طلب التواصل مع الأدمن
    Handle contact admin request
    """
    try:

        text = (
        "📞 <b>للتواصل مع الدعم:</b>\n\n"
        "مرحباً بكم،\n\n"
        "إذا كنتم بحاجة إلى أي مساعدة أو لديكم استفسار، يُرجى التواصل مع المسؤول عبر إحدى الطرق التالية:\n\n"
        "✅ <b>تيليجرام:</b> @aym_nn7\n\n"
        "✅ <b>واتساب:</b> <a href='https://wa.me/967717152606'>اضغط هنا للدردشة</a> 24/7\n\n"
        "🕊️ شكراً لتواصلكم، وسنحرص على الرد عليكم في أقرب وقت ممكن.")

        keyboard = [[{'text': '🔙 عودة', 'callback_data': 'back'}]]
        reply_markup = build_inline_keyboard(keyboard)

        send_message(chat_id, text, reply_markup)

        
        # الحصول على معلومات الأدمن
      
        
        # إرسال إشعار للأدمن أن المستخدم يريد التواصل
        try:
            if admin_id and admin_id not in ['', 'YOUR_ADMIN_ID_HERE', '0']:
                username_display = f"@{username}" if username and username != 'لا يوجد' else "لا يوجد"
                
                notification_text = (
                    f"📩 <b>مستخدم يريد التواصل معك!</b>\n\n"
                    f"👤 <b>ID المستخدم:</b> <code>{user_id}</code>\n"
                    f"🔗 <b>اليوزرنيم:</b> {username_display}\n\n"
                    f"💡 <b>يمكنك التواصل معه عبر:</b>\n"
                    f"• إرسال رسالة مباشرة عبر ID\n"
                    f"• أو طلب منه إرسال رسالة لك"
                )
                
                send_message(admin_id, notification_text)
                log_error(f"📩 Admin {admin_id} notified about contact request from user {user_id}")
        except Exception as e:
            # لا نسمح للخطأ بالتأثير على الوظيفة الأساسية
            log_error(f"⚠️ خطأ في إرسال إشعار التواصل للأدمن: {str(e)}")
    
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
                
                # التحقق من وجود المستخدم
                if not userExists(target_user_id):
                    send_message(chat_id, f"❌ المستخدم {target_user_id} غير موجود في قاعدة البيانات.\n\n💡 يجب أن يكون المستخدم قد ضغط /start على البوت أولاً.")
                    return
                
                balance_before = getBalance(target_user_id)
                if addBalance(target_user_id, amount):
                    balance_after = getBalance(target_user_id)
                    
                    logBalanceOperation(target_user_id, "add_by_admin", amount, balance_before, balance_after)
                    logAdminOperation(user_id, "/addbalance", target_user_id, f"Amount:{amount}$")
                    
                    # إرسال رسالة تأكيد للأدمن
                    send_message(chat_id, f"✅ <b>تم إضافة الرصيد بنجاح!</b>\n\n👤 المستخدم: {target_user_id}\n💰 المبلغ: {amount}$\n📊 الرصيد قبل: {balance_before:.6f}$\n💵 الرصيد بعد: {balance_after:.6f}$")
                    
                    # إرسال إشعار للمستخدم
                    try:
                        notification_text = (
                            f"🎉 <b>مبروك!</b>\n\n"
                            f"💰 <b>تم إضافة رصيد إلى حسابك</b>\n"
                            f"📥 <b>القيمة:</b> {amount}$\n\n"
                            f"📊 <b>رصيدك قبل:</b> {balance_before:.6f}$\n"
                            f"💵 <b>رصيدك بعد:</b> {balance_after:.6f}$\n\n"
                            f"👮 <b>بواسطة الأدمن</b>\n\n"
                            f"💡 يمكنك الآن استخدام الرصيد لطلب الخدمات!"
                        )
                        
                        send_message(target_user_id, notification_text)
                        log_error(f"📩 User {target_user_id} notified about balance addition: {amount}$")
                    except Exception as e:
                        log_error(f"⚠️ خطأ في إرسال إشعار للمستخدم: {str(e)}")
                else:
                    send_message(chat_id, "❌ فشل في إضافة الرصيد.")
            
            except ValueError:
                send_message(chat_id, "❌ بيانات غير صالحة.\n\nالاستخدام: /addbalance USER_ID AMOUNT")
        
        elif len(parts) == 2:
            try:
                target_user_id = int(parts[1])
                
                # التحقق من وجود المستخدم
                if not userExists(target_user_id):
                    send_message(chat_id, f"❌ المستخدم {target_user_id} غير موجود في قاعدة البيانات.\n\n💡 يجب أن يكون المستخدم قد ضغط /start على البوت أولاً.")
                    return
                
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
        
        # التحقق من وجود المستخدم قبل إضافة الرصيد
        if not userExists(target_user_id):
            send_message(chat_id, f"❌ المستخدم {target_user_id} غير موجود في قاعدة البيانات.\n\n💡 يجب أن يكون المستخدم قد ضغط /start على البوت أولاً.")
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
                
                # إرسال رسالة تأكيد للأدمن
                send_message(chat_id, f"✅ <b>تم إضافة الرصيد بنجاح!</b>\n\n👤 المستخدم: {target_user_id}\n💰 المبلغ: {amount}$\n📊 الرصيد قبل: {balance_before:.6f}$\n💵 الرصيد بعد: {balance_after:.6f}$")
                
                # إرسال إشعار للمستخدم أن رصيده تم إضافته
                try:
                    notification_text = (
                        f"🎉 <b>مبروك!</b>\n\n"
                        f"💰 <b>تم إضافة رصيد إلى حسابك</b>\n"
                        f"📥 <b>القيمة:</b> {amount}$\n\n"
                        f"📊 <b>رصيدك قبل:</b> {balance_before:.6f}$\n"
                        f"💵 <b>رصيدك بعد:</b> {balance_after:.6f}$\n\n"
                        f"👮 <b>بواسطة الأدمن</b>\n\n"
                        f"💡 يمكنك الآن استخدام الرصيد لطلب الخدمات!"
                    )
                    
                    send_message(target_user_id, notification_text)
                    log_error(f"📩 User {target_user_id} notified about balance addition: {amount}$")
                except Exception as e:
                    # لا نسمح للخطأ بالتأثير على العملية
                    log_error(f"⚠️ خطأ في إرسال إشعار للمستخدم: {str(e)}")
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


def handle_admin_panel(chat_id, user_id, first_name="أدمن"):
    """
    عرض لوحة تحكم الأدمن الكاملة
    Show admin control panel
    """
    try:
        # فحص جذري للأدمن
        if not validateAdminCommand(user_id, "admin_panel"):
            send_message(chat_id, "❌ ليس لديك صلاحية استخدام هذه الميزة.")
            return
        
        # الحصول على الإحصائيات
        total_users = getAllUsersCount()
        admin_id = getAdminId()
        pricing_info = getPricingInfo()
        
        # نص لوحة التحكم
        text = f"👑 <b>لوحة تحكم الأدمن</b>\n\n"
        text += f"👤 مرحباً: {first_name}\n"
        text += f"🆔 ID الأدمن: <code>{admin_id}</code>\n\n"
        text += f"📊 <b>إحصائيات البوت:</b>\n"
        text += f"👥 إجمالي المستخدمين: {total_users}\n\n"
        text += f"⚙️ <b>الأوامر المتاحة:</b>\n\n"
        text += f"💰 <b>إدارة الرصيد:</b>\n"
        text += f"  • <code>/addbalance ID AMOUNT</code> - إضافة رصيد\n"
        text += f"  • <code>/removebalance ID AMOUNT</code> - خصم رصيد\n\n"
        text += f"📈 <b>إدارة التسعير:</b>\n"
        text += f"  • <code>/setpercent VALUE</code> - تسعير نسبي\n"
        text += f"  • <code>/setprice VALUE</code> - تسعير ثابت\n"
        text += f"  • <code>/price</code> - عرض التسعير الحالي\n\n"
        text += f"📢 <b>الرسائل الجماعية:</b>\n"
        text += f"  • <code>/broadcast</code> - إرسال رسالة للجميع\n"
        
        # أزرار لوحة التحكم
        keyboard = [
            [{'text': '💰 إضافة رصيد', 'callback_data': 'admin_add_balance'}, {'text': '💸 خصم رصيد', 'callback_data': 'admin_remove_balance'}],
            [{'text': '📊 عرض التسعير', 'callback_data': 'admin_show_pricing'}],
            [{'text': '📢 رسالة جماعية', 'callback_data': 'admin_broadcast'}],
            [{'text': '🔔 إشعارات المستخدمين', 'callback_data': 'admin_notifications'}],
            [{'text': '📣 إعداد قناة النشر', 'callback_data': 'admin_set_channel'}],
            [{'text': '📁 إدارة الخدمات', 'callback_data': 'admin_services_management'}],
            [{'text': '🔄 تحديث', 'callback_data': 'refresh'}, {'text': '🔙 عودة', 'callback_data': 'back'}]
        ]
        
        reply_markup = build_inline_keyboard(keyboard)
        send_message(chat_id, text, reply_markup)
        
        log_error(f"👑 Admin panel accessed by {user_id}")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_panel: {str(e)}")
        logErrorWithDetails("admin_panel_error", str(e), user_id)


def handle_admin_add_balance_inline(chat_id, user_id):
    """
    معالجة زر إضافة رصيد من لوحة الأدمن
    Handle admin add balance inline button
    """
    try:
        if not validateAdminCommand(user_id, "admin_add_balance_inline"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        send_message(
            chat_id,
            "💰 <b>إضافة رصيد لمستخدم</b>\n\n"
            "الاستخدام:\n"
            "<code>/addbalance USER_ID AMOUNT</code>\n\n"
            "مثال:\n"
            "<code>/addbalance 123456789 10</code>\n\n"
            "أو:\n"
            "<code>/addbalance USER_ID</code> (ثم إرسال المبلغ)"
        )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_add_balance_inline: {str(e)}")


def handle_admin_remove_balance_inline(chat_id, user_id):
    """
    معالجة زر خصم رصيد من لوحة الأدمن
    Handle admin remove balance inline button
    """
    try:
        if not validateAdminCommand(user_id, "admin_remove_balance_inline"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        send_message(
            chat_id,
            "💸 <b>خصم رصيد من مستخدم</b>\n\n"
            "الاستخدام:\n"
            "<code>/removebalance USER_ID AMOUNT</code>\n\n"
            "مثال:\n"
            "<code>/removebalance 123456789 5</code>\n\n"
            "أو:\n"
            "<code>/removebalance USER_ID</code> (ثم إرسال المبلغ)"
        )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_remove_balance_inline: {str(e)}")


def handle_admin_show_pricing_inline(chat_id, user_id):
    """
    معالجة زر عرض التسعير من لوحة الأدمن
    Handle admin show pricing inline button
    """
    try:
        if not validateAdminCommand(user_id, "admin_show_pricing_inline"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        pricing_info = getPricingInfo()
        
        keyboard = [[{'text': '🔙 عودة للوحة الأدمن', 'callback_data': 'admin_panel'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, pricing_info, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_show_pricing_inline: {str(e)}")


def handle_admin_notifications_toggle(chat_id, user_id):
    """
    معالجة زر إشعارات المستخدمين من لوحة الأدمن
    Handle admin notifications toggle button
    """
    try:
        if not validateAdminCommand(user_id, "admin_notifications_toggle"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        # تبديل حالة الإشعارات
        new_state = toggleNewUserNotifications()
        
        # عرض الحالة الجديدة
        if new_state:
            status_text = "✅ <b>مفعّلة</b>"
            status_emoji = "🔔"
            description = "سيتم إرسال إشعار للأدمن عند انضمام كل مستخدم جديد"
        else:
            status_text = "❌ <b>متوقفة</b>"
            status_emoji = "🔕"
            description = "لن يتم إرسال إشعارات عند انضمام مستخدمين جدد"
        
        text = f"{status_emoji} <b>إشعارات المستخدمين الجدد</b>\n\n"
        text += f"📊 <b>الحالة:</b> {status_text}\n\n"
        text += f"💡 {description}\n\n"
        text += f"اضغط على الزر أدناه للتبديل بين التفعيل والإيقاف"
        
        keyboard = [
            [{'text': '🔄 تبديل الحالة', 'callback_data': 'admin_notifications'}],
            [{'text': '🔙 عودة للوحة الأدمن', 'callback_data': 'admin_panel'}]
        ]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
        
        log_error(f"🔔 Admin {user_id} toggled notifications: {'Enabled' if new_state else 'Disabled'}")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_notifications_toggle: {str(e)}")
        logErrorWithDetails("admin_notifications_toggle_error", str(e), user_id)


def handle_admin_set_channel(chat_id, user_id):
    """
    معالجة زر إعداد قناة النشر من لوحة الأدمن
    Handle admin set channel button
    """
    try:
        if not validateAdminCommand(user_id, "admin_set_channel"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        # الحصول على القناة الحالية
        current_channel = getChannelUsername()
        
        if current_channel:
            text = f"📣 <b>إعداد قناة النشر</b>\n\n"
            text += f"📊 <b>القناة الحالية:</b> @{current_channel}\n\n"
            text += f"الآن أرسل يوزرنيم القناة الجديدة (مع أو بدون @)\n\n"
            text += f"💡 مثال: @mychannel أو mychannel\n\n"
            text += f"⚠️ <b>مهم:</b> تأكد أن البوت مضاف كأدمن في القناة"
        else:
            text = f"📣 <b>إعداد قناة النشر</b>\n\n"
            text += f"📊 <b>القناة الحالية:</b> لم يتم تحديد قناة\n\n"
            text += f"الآن أرسل يوزرنيم القناة (مع أو بدون @)\n\n"
            text += f"💡 مثال: @mychannel أو mychannel\n\n"
            text += f"⚠️ <b>مهم:</b> تأكد أن البوت مضاف كأدمن في القناة"
        
        # تعيين حالة الانتظار
        user_states[user_id] = {
            'state': 'WAITING_CHANNEL_USERNAME'
        }
        
        keyboard = [[{'text': '🔙 عودة للوحة الأدمن', 'callback_data': 'admin_panel'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(chat_id, text, reply_markup)
        
        log_error(f"📣 Admin {user_id} opened channel setup")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_set_channel: {str(e)}")
        logErrorWithDetails("admin_set_channel_error", str(e), user_id)


# ========== إدارة الخدمات والأقسام ==========

def handle_admin_services_menu(chat_id, user_id):
    """
    عرض قائمة إدارة الخدمات والأقسام
    Show services management menu
    """
    try:
        if not validateAdminCommand(user_id, "admin_services_management"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        categories = getAllCategories()
        all_services = getAllServicesFlat()
        
        text = f"📁 <b>إدارة الخدمات والأقسام</b>\n\n"
        text += f"📊 <b>الإحصائيات:</b>\n"
        text += f"📁 الأقسام: {len(categories)}\n"
        text += f"🛒 الخدمات: {len(all_services)}\n\n"
        text += f"💡 <b>اختر عملية:</b>"
        
        keyboard = [
            [{'text': '➕ إضافة قسم جديد', 'callback_data': 'admin_add_category'}],
            [{'text': '🗑️ حذف قسم', 'callback_data': 'admin_delete_category'}],
            [{'text': '➕ إضافة خدمة', 'callback_data': 'admin_add_service'}],
            [{'text': '🗑️ حذف خدمة', 'callback_data': 'admin_delete_service'}],
            [{'text': '🔙 عودة للوحة الأدمن', 'callback_data': 'admin_panel'}]
        ]
        
        reply_markup = build_inline_keyboard(keyboard)
        send_message(chat_id, text, reply_markup)
        
        log_error(f"📁 Admin {user_id} opened services management")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_services_menu: {str(e)}")
        logErrorWithDetails("admin_services_menu_error", str(e), user_id)


def handle_admin_add_category(chat_id, user_id):
    """
    معالجة إضافة قسم جديد
    Handle add new category
    """
    try:
        if not validateAdminCommand(user_id, "admin_add_category"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        user_states[user_id] = {
            'state': 'WAITING_CATEGORY_NAME'
        }
        
        keyboard = [[{'text': '🔙 إلغاء', 'callback_data': 'admin_services_management'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(
            chat_id,
            "➕ <b>إضافة قسم جديد</b>\n\n"
            "الآن أرسل اسم القسم الجديد:\n\n"
            "💡 مثال: خدمات الفيسبوك، التيلجرام، الانستجرام",
            reply_markup
        )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_add_category: {str(e)}")
        logErrorWithDetails("admin_add_category_error", str(e), user_id)


def handle_add_category_input(chat_id, user_id, text):
    """
    معالجة إدخال اسم القسم
    Handle category name input
    """
    try:
        # مسح حالة الانتظار
        if user_id in user_states:
            del user_states[user_id]
        
        category_name = text.strip()
        
        if not category_name:
            send_message(chat_id, "❌ اسم القسم لا يمكن أن يكون فارغاً.")
            return
        
        if addCategory(category_name):
            keyboard = [[{'text': '🔙 عودة للإدارة', 'callback_data': 'admin_services_management'}]]
            reply_markup = build_inline_keyboard(keyboard)
            
            send_message(
                chat_id,
                f"✅ <b>تم إضافة القسم بنجاح!</b>\n\n"
                f"📁 <b>القسم:</b> {category_name}\n\n"
                f"💡 يمكنك الآن إضافة خدمات لهذا القسم",
                reply_markup
            )
            
            log_error(f"📁 Category added: {category_name} by admin {user_id}")
        else:
            send_message(chat_id, "❌ فشل إضافة القسم. قد يكون موجوداً بالفعل.")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_add_category_input: {str(e)}")
        logErrorWithDetails("add_category_input_error", str(e), user_id)


def handle_admin_delete_category(chat_id, user_id):
    """
    عرض قائمة الأقسام للحذف
    Show categories list for deletion
    """
    try:
        if not validateAdminCommand(user_id, "admin_delete_category"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        categories = getAllCategories()
        
        if not categories:
            send_message(chat_id, "❌ لا توجد أقسام لحذفها.")
            return
        
        text = f"🗑️ <b>حذف قسم</b>\n\n"
        text += f"اختر القسم الذي تريد حذفه:\n\n"
        text += f"⚠️ <b>تحذير:</b> سيتم حذف القسم وجميع خدماته!"
        
        keyboard = []
        for cat in categories:
            keyboard.append([{'text': f'🗑️ {cat}', 'callback_data': f'confirm_delete_cat_{cat}'}])
        
        keyboard.append([{'text': '🔙 إلغاء', 'callback_data': 'admin_services_management'}])
        
        reply_markup = build_inline_keyboard(keyboard)
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_delete_category: {str(e)}")
        logErrorWithDetails("admin_delete_category_error", str(e), user_id)


def handle_confirm_delete_category(chat_id, user_id, category_name):
    """
    تأكيد حذف قسم
    Confirm category deletion
    """
    try:
        if deleteCategory(category_name):
            keyboard = [[{'text': '🔙 عودة للإدارة', 'callback_data': 'admin_services_management'}]]
            reply_markup = build_inline_keyboard(keyboard)
            
            send_message(
                chat_id,
                f"✅ <b>تم حذف القسم بنجاح!</b>\n\n"
                f"🗑️ <b>القسم المحذوف:</b> {category_name}\n\n"
                f"تم حذف القسم وجميع خدماته.",
                reply_markup
            )
            
            log_error(f"🗑️ Category deleted: {category_name} by admin {user_id}")
        else:
            send_message(chat_id, f"❌ فشل حذف القسم '{category_name}'.")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_confirm_delete_category: {str(e)}")
        logErrorWithDetails("confirm_delete_category_error", str(e), user_id)


def handle_admin_add_service(chat_id, user_id):
    """
    عرض قائمة الأقسام لإضافة خدمة
    Show categories list for adding service
    """
    try:
        if not validateAdminCommand(user_id, "admin_add_service"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        categories = getAllCategories()
        
        if not categories:
            send_message(chat_id, "❌ لا توجد أقسام. يجب إضافة قسم أولاً.")
            return
        
        text = f"➕ <b>إضافة خدمة</b>\n\n"
        text += f"اختر القسم الذي تريد إضافة الخدمة إليه:"
        
        keyboard = []
        for cat in categories:
            keyboard.append([{'text': f'📁 {cat}', 'callback_data': f'add_service_to_{cat}'}])
        
        keyboard.append([{'text': '🔙 إلغاء', 'callback_data': 'admin_services_management'}])
        
        reply_markup = build_inline_keyboard(keyboard)
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_add_service: {str(e)}")
        logErrorWithDetails("admin_add_service_error", str(e), user_id)


def handle_add_service_to_category(chat_id, user_id, category_name):
    """
    معالجة إضافة خدمة لقسم معين
    Handle adding service to category
    """
    try:
        if not validateAdminCommand(user_id, "add_service_to_category"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        user_states[user_id] = {
            'state': 'WAITING_SERVICE_ID',
            'category': category_name
        }
        
        keyboard = [[{'text': '🔙 إلغاء', 'callback_data': 'admin_add_service'}]]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(
            chat_id,
            f"➕ <b>إضافة خدمة إلى: {category_name}</b>\n\n"
            f"الآن أرسل <b>معرف الخدمة (Service ID)</b> من API:\n\n"
            f"💡 مثال: 123",
            reply_markup
        )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_add_service_to_category: {str(e)}")
        logErrorWithDetails("add_service_to_category_error", str(e), user_id)


def handle_service_id_input(chat_id, user_id, text):
    """
    معالجة إدخال معرف الخدمة
    Handle service ID input
    """
    try:
        user_state = user_states.get(user_id, {})
        
        if user_state.get('state') != 'WAITING_SERVICE_ID':
            send_message(chat_id, "❌ خطأ في الحالة.")
            return
        
        try:
            service_id = int(text.strip())
        except ValueError:
            send_message(chat_id, "❌ معرف الخدمة يجب أن يكون رقم.")
            return
        
        # التحقق من وجود الخدمة في API
        service_info = smm_api.get_service_by_id(service_id)
        
        if not service_info:
            send_message(chat_id, f"❌ الخدمة {service_id} غير موجودة في API.\n\nتأكد من معرف الخدمة.")
            return
        
        service_name = service_info.get('name', f'Service {service_id}')
        
        # حفظ service_id مؤقتاً
        user_states[user_id]['service_id'] = service_id
        user_states[user_id]['service_name'] = service_name
        user_states[user_id]['state'] = 'WAITING_SERVICE_CONFIRM'
        
        category = user_state.get('category')
        
        keyboard = [
            [{'text': '✅ تأكيد الإضافة', 'callback_data': f'confirm_add_service'}],
            [{'text': '❌ إلغاء', 'callback_data': 'admin_add_service'}]
        ]
        reply_markup = build_inline_keyboard(keyboard)
        
        send_message(
            chat_id,
            f"📋 <b>تأكيد إضافة الخدمة:</b>\n\n"
            f"📁 <b>القسم:</b> {category}\n"
            f"🆔 <b>Service ID:</b> <code>{service_id}</code>\n"
            f"📝 <b>اسم الخدمة:</b> {service_name}\n\n"
            f"هل تريد إضافة هذه الخدمة؟",
            reply_markup
        )
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_service_id_input: {str(e)}")
        logErrorWithDetails("service_id_input_error", str(e), user_id)


def handle_confirm_add_service(chat_id, user_id):
    """
    تأكيد إضافة الخدمة
    Confirm service addition
    """
    try:
        user_state = user_states.get(user_id, {})
        
        category = user_state.get('category')
        service_id = user_state.get('service_id')
        service_name = user_state.get('service_name')
        
        if not category or not service_id:
            send_message(chat_id, "❌ خطأ في البيانات.")
            return
        
        # مسح حالة الانتظار
        if user_id in user_states:
            del user_states[user_id]
        
        if addServiceToCategory(category, service_id, service_name):
            keyboard = [[{'text': '🔙 عودة للإدارة', 'callback_data': 'admin_services_management'}]]
            reply_markup = build_inline_keyboard(keyboard)
            
            send_message(
                chat_id,
                f"✅ <b>تم إضافة الخدمة بنجاح!</b>\n\n"
                f"📁 <b>القسم:</b> {category}\n"
                f"🆔 <b>Service ID:</b> <code>{service_id}</code>\n"
                f"📝 <b>الخدمة:</b> {service_name}",
                reply_markup
            )
            
            log_error(f"✅ Service {service_id} added to {category} by admin {user_id}")
        else:
            send_message(chat_id, "❌ فشل إضافة الخدمة. قد تكون موجودة بالفعل.")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_confirm_add_service: {str(e)}")
        logErrorWithDetails("confirm_add_service_error", str(e), user_id)


def handle_admin_delete_service(chat_id, user_id):
    """
    عرض قائمة الخدمات للحذف
    Show services list for deletion
    """
    try:
        if not validateAdminCommand(user_id, "admin_delete_service"):
            send_message(chat_id, "❌ ليس لديك صلاحية.")
            return
        
        all_services = getAllServicesFlat()
        
        if not all_services:
            send_message(chat_id, "❌ لا توجد خدمات لحذفها.")
            return
        
        text = f"🗑️ <b>حذف خدمة</b>\n\n"
        text += f"اختر الخدمة التي تريد حذفها:\n\n"
        
        keyboard = []
        for svc in all_services[:20]:  # عرض أول 20 خدمة
            btn_text = f"🗑️ {svc['service_name'][:30]} (ID: {svc['service_id']})"
            callback_data = f"confirm_delete_svc_{svc['category']}_{svc['service_id']}"
            keyboard.append([{'text': btn_text, 'callback_data': callback_data}])
        
        if len(all_services) > 20:
            text += f"(عرض أول 20 من {len(all_services)} خدمة)\n\n"
        
        keyboard.append([{'text': '🔙 إلغاء', 'callback_data': 'admin_services_management'}])
        
        reply_markup = build_inline_keyboard(keyboard)
        send_message(chat_id, text, reply_markup)
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_admin_delete_service: {str(e)}")
        logErrorWithDetails("admin_delete_service_error", str(e), user_id)


def handle_confirm_delete_service(chat_id, user_id, category_name, service_id):
    """
    تأكيد حذف خدمة
    Confirm service deletion
    """
    try:
        if deleteServiceFromCategory(category_name, service_id):
            keyboard = [[{'text': '🔙 عودة للإدارة', 'callback_data': 'admin_services_management'}]]
            reply_markup = build_inline_keyboard(keyboard)
            
            send_message(
                chat_id,
                f"✅ <b>تم حذف الخدمة بنجاح!</b>\n\n"
                f"🗑️ <b>القسم:</b> {category_name}\n"
                f"🆔 <b>Service ID:</b> <code>{service_id}</code>",
                reply_markup
            )
            
            log_error(f"🗑️ Service {service_id} deleted from {category_name} by admin {user_id}")
        else:
            send_message(chat_id, f"❌ فشل حذف الخدمة {service_id}.")
    
    except Exception as e:
        log_error(f"❌ خطأ في handle_confirm_delete_service: {str(e)}")
        logErrorWithDetails("confirm_delete_service_error", str(e), user_id)


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
