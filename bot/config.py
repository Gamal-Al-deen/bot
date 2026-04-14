# -*- coding: utf-8 -*-
"""
ملف الإعدادات - يحتوي على جميع المتغيرات الثابتة
Configuration file - Contains all static variables
"""

import os

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
# على Render/VPS يُفضّل تعيين SUPABASE_URL و SUPABASE_SERVICE_ROLE_KEY في Environment (تتجاوز القيم أدناه).
_SUPABASE_URL_FALLBACK = "https://fjmhekbuhwjtwmwucrwc.supabase.co"
_SUPABASE_KEY_FALLBACK = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImZqbWhla2J1aHdqdHdtd3VjcndjIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc3NTc3MjMzMSwiZXhwIjoyMDkxMzQ4MzMxfQ.8S427ImdS_ETWeJco7lvWGY7MiM7c8KeEYht7zYQ_YQ"

SUPABASE_URL = (os.environ.get("SUPABASE_URL") or "").strip() or _SUPABASE_URL_FALLBACK
_env_key = (
    os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
    or os.environ.get("SUPABASE_KEY")
    or ""
).strip()
SUPABASE_KEY = _env_key or _SUPABASE_KEY_FALLBACK

# ⚠️ ضع هنا مفتاح الخدمة من Supabase
# ⚠️ Put your Supabase Service Role Key here
# تجده في: Project Settings > API > service_role key (secret)
