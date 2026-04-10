# -*- coding: utf-8 -*-
"""
ملف الإعدادات - يحتوي على جميع المتغيرات الثابتة
Configuration file - Contains all static variables
"""

# ⚠️ ضع هنا توكن البوت الخاص بك
# ⚠️ Put your bot token here
BOT_TOKEN = "8641656014:AAE4n6WqbnusGtWkf5a-RuMXomVRGIN_J5M"

# ⚠️ ضع هنا مفتاح API الخاص بموقع SMM
# ⚠️ Put your SMM website API key here
API_KEY = "9bf0c5cc6a73e611dd2a7fcee8c3a6c6"

# رابط API الخاص بموقع SMM
# SMM API URL
API_URL = "https://smmparty.com/api/v2"

# رابط Telegram API (لا تقم بتعديله)
# Telegram API URL (Do not modify)
TELEGRAM_API_URL = "https://api.telegram.org/bot"

# ⚠️ ضع هنا معرف الأدمن الخاص بك
# ⚠️ Put your Admin Telegram ID here
ADMIN_ID = "8036934949"  # استبدل هذا بمعرفك

# إعدادات المستخدمين والرصيد
# User Balance Settings
DEFAULT_BALANCE = 0.0  # الرصيد الافتراضي للمستخدمين الجدد

# إعدادات التسعير الافتراضية
# Default Pricing Settings
DEFAULT_PRICING_TYPE = "percent"  # "percent" أو "fixed"
DEFAULT_PRICING_VALUE = 50  # النسبة المئوية أو المبلغ الثابت

# إعدادات قفل المستخدم
# User Lock Settings
USER_LOCK_TIMEOUT = 60  # مدة القفل بالثواني

# معرفات الحالات للمحادثة
# Conversation state identifiers
STATE_WAITING_SERVICE = "WAITING_SERVICE"
STATE_WAITING_LINK = "WAITING_LINK"
STATE_WAITING_QUANTITY = "WAITING_QUANTITY"
STATE_WAITING_ADMIN_ADD_BALANCE = "WAITING_ADMIN_ADD_BALANCE"
STATE_WAITING_ADMIN_REMOVE_BALANCE = "WAITING_ADMIN_REMOVE_BALANCE"
STATE_WAITING_ADMIN_USER_ID = "WAITING_ADMIN_USER_ID"

# ⚠️ تأكد من تعيين القيم أعلاه بشكل صحيح قبل تشغيل البوت
# ⚠️ Make sure to set the values above correctly before running the bot

# ============================================
# Supabase Configuration
# ============================================
# ⚠️ ضع هنا رابط Supabase الخاص بك
# ⚠️ Put your Supabase URL here
# تجده في: Project Settings > API > Project URL
SUPABASE_URL = "https://fjmhekbuhwjtwmwucrwc.supabase.co"  # مثال: https://xxxxx.supabase.co

# ⚠️ ضع هنا مفتاح الخدمة من Supabase
# ⚠️ Put your Supabase Service Role Key here
# تجده في: Project Settings > API > service_role key (secret)
SUPABASE_KEY = "sb_publishable_Xb32CM-jJdkwMgvlmW90aw_hE8EVaL2"
