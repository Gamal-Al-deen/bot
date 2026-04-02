# 🤖 بوت SMM - دليل التشغيل السريع
# SMM Bot - Quick Start Guide

## 📁 هيكل المشروع

```
bot/
├── config.py          # ⚙️ الإعدادات (BOT_TOKEN, API_KEY)
├── api.py             # 🔌 فئة SMM API
├── functions.py       # 📩 دوال Telegram المساعدة
├── bot.py             # 🧠 منطق البوت الرئيسي
├── run.py             # 🔄 نقطة التشغيل (Long Polling)
├── requirements.txt   # 📦 المكتبات المطلوبة
├── offset.txt         # 📍 تخزين آخر update (تلقائي)
├── log.txt            # 📝 سجل الأحداث (تلقائي)
├── .gitignore         # 🚫 ملفات مستبعدة من Git
├── DEPLOYMENT.md      # 📚 دليل النشر المفصل
└── README.md          # 📖 هذا الملف
```

---

## ⚡ البدء السريع

### 1️⃣ تثبيت المتطلبات

```bash
cd bot
pip install -r requirements.txt
```

### 2️⃣ تعديل الإعدادات

افتح `config.py` وعدل:

```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
API_KEY = "YOUR_API_KEY_HERE"
API_URL = "https://your-smm-site.com/api/v2"
```

### 3️⃣ التشغيل

```bash
python run.py
```

---

## 🎯 اختبار البوت

1. افتح Telegram
2. ابحث عن بوتك باستخدام BOT_TOKEN
3. أرسل `/start`
4. جرب الأزرار:
   - 💰 رصيد
   - 📦 خدمات
   - 🛒 طلب جديد

---

## 📊 الميزات

✅ **رصيد** - عرض الرصيد من SMM API  
✅ **خدمات** - عرض قائمة الخدمات  
✅ **طلب جديد** - تقديم طلب كامل  
✅ **Inline Keyboard** - واجهة احترافية  
✅ **Logging** - تسجيل جميع الأحداث  
✅ **Offset Management** - منع الرسائل المكررة  
✅ **Error Handling** - معالجة شاملة للأخطاء  

---

## 🌐 النشر على Render

راجع ملف `DEPLOYMENT.md` للحصول على دليل شامل لنشر البوت على Render مجاناً.

---

## 🔧 التطوير

### إضافة ميزة جديدة:

1. عدل `bot.py` لإضافة معالج جديد
2. أضف الدالة في `functions.py` إذا لزم الأمر
3. اختبر محلياً
4. ارفع على GitHub للنشر على Render

### مثال: إضافة زر

في `bot.py`:

```python
elif text == 'مساعدة':
    send_message(chat_id, "كيف يمكنني مساعدتك؟")
```

---

## 🐛 حل المشاكل

| المشكلة | الحل |
|---------|------|
| البوت لا يستجيب | تحقق من BOT_TOKEN في config.py |
| خطأ API | تحقق من API_KEY و API_URL |
| رسائل مكررة | احذف offset.txt وأعد التشغيل |
| البوت يتوقف | راجع log.txt للأخطاء |

---

## 📞 الحصول على BOT_TOKEN

1. افتح Telegram
2. ابحث عن @BotFather
3. أرسل `/newbot`
4. اتبع التعليمات
5. انسخ التوكن

---

## ⚠️ تحذيرات

- ❌ لا تشارك BOT_TOKEN مع أحد
- ❌ لا ترفع config.py على GitHub (إذا كان يحتوي على tokens)
- ✅ احتفظ بنسخة احتياطية من API_KEY
- ✅ اختبر محلياً قبل النشر

---

## 📈 الترقية

لتحسين الأداء:

1. زد عدد الخدمات المعروضة
2. أضف ميزات جديدة (حالة الطلب، إلخ)
3. استخدم database لتخزين المستخدمين
4. أضف لوحة تحكم للمشرفين

---

## 🎉 انتهى الدليل

بوتك جاهز الآن! 🚀

للحصول على مساعدة إضافية، راجع `DEPLOYMENT.md`.
