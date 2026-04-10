# 📌 مرجع سريع - بوت SMM المتقدم

## 👤 أوامر المستخدم

| الأمر | الوظيفة | مثال |
|-------|---------|------|
| `/start` | القائمة الرئيسية | `/start` |
| `/balance` | عرض الرصيد | `/balance` |
| `/services` | عرض الخدمات | `/services` |
| `/neworder` | طلب جديد | `/neworder` |
| `💰 رصيدي` | عرض الرصيد | زر |
| `🛒 الخدمات` | عرض الخدمات | زر |
| `🛒 طلب جديد` | طلب جديد | زر |
| `📞 التواصل مع الادمن` | معلومات التواصل | زر |
| `💳 الدفع / الاشتراك` | طرق الدفع | زر |
| `🔄 تحديث` | تحديث البيانات | زر |

---

## 👑 أوامر الأدمن

| الأمر | الوظيفة | مثال |
|-------|---------|------|
| `/addbalance` | إضافة رصيد | `/addbalance 123456789 10` |
| `/removebalance` | خصم رصيد | `/removebalance 123456789 5` |
| `/setpercent` | تسعير نسبي | `/setpercent 50` |
| `/setprice` | تسعير ثابت | `/setprice 5` |
| `/price` | عرض التسعير | `/price` |

---

## 💰 نظام الرصيد

### دوال أساسية:
```python
getBalance(user_id)           # عرض الرصيد
addBalance(user_id, amount)   # إضافة رصيد
deductBalance(user_id, amount) # خصم رصيد
setBalance(user_id, amount)   # تعيين رصيد
```

### ملف البيانات:
- **الموقع:** `users_data.json`
- **الصيغة:** JSON
- **الهيكل:**
  ```json
  {
    "user_id": {
      "balance": 0.0
    }
  }
  ```

---

## 💲 نظام التسعير

### أنواع التسعير:

**1. نسبي (Percent):**
```
السعر النهائي = السعر الأصلي + (السعر الأصلي × النسبة ÷ 100)
```

**2. ثابت (Fixed):**
```
السعر النهائي = السعر الأصلي + المبلغ الثابت
```

### دوال أساسية:
```python
calculatePrice(base_price)           # حساب السعر النهائي
setPercentPricing(value)             # تعيين نسبة
setFixedPricing(value)               # تعيين مبلغ ثابت
getPricingInfo()                     # معلومات التسعير
calculateOrderTotalPrice(rate, qty)  # سعر الطلب
```

### ملف الإعدادات:
- **الموقع:** `pricing_config.json`
- **الصيغة:** JSON
- **الهيكل:**
  ```json
  {
    "type": "percent",
    "value": 50
  }
  ```

---

## 🔐 نظام الأدمن

### الإعداد:
```python
# في config.py
ADMIN_ID = "YOUR_TELEGRAM_ID"
```

### دوال أساسية:
```python
isAdmin(user_id)                    # التحقق من أدمن
requireAdmin(user_id)               # التحقق مع رسالة
validateAdminCommand(user_id, cmd)  # التحقق وتسجيل
```

### رسائل الخطأ:
```
❌ ليس لديك صلاحية استخدام هذا الأمر.
```

---

## 🔒 نظام القفل

### دوال أساسية:
```python
acquireLock(user_id, timeout)  # قفل مستخدم
releaseLock(user_id)           # تحرير قفل
isLocked(user_id, timeout)     # التحقق من القفل
getLockStatus(user_id)         # حالة القفل
```

### الإعداد:
```python
# في config.py
USER_LOCK_TIMEOUT = 60  # بالثواني
```

### رسائل الخطأ:
```
⏳ لديك طلب قيد المعالجة. يرجى الانتظار.
```

---

## 📝 السجلات

### ملف السجلات:
- **الموقع:** `log.txt`
- **الصيغة:** نص مع طوابع زمنية

### أنواع السجلات:
- `[BALANCE]` - عمليات الرصيد
- `[ORDER]` - الطلبات
- `[PRICING]` - تغييرات التسعير
- `[ADMIN]` - أوامر الأدمن
- `[ERROR]` - الأخطاء

### مثال:
```
[2026-04-07 15:30:45] [BALANCE] User:123 | add 10$ | Before: 5$ | After: 15$
```

---

## 🚀 التشغيل

### 1. تثبيت المكتبات:
```bash
pip install -r requirements.txt
```

### 2. إعداد الأدمن:
```python
# في config.py
ADMIN_ID = "YOUR_TELEGRAM_ID"
```

### 3. تشغيل البوت:
```bash
python run.py
```

---

## ⚡ اختبار سريع

### 1. إضافة رصيد:
```
/addbalance YOUR_ID 100
```

### 2. التحقق من الرصيد:
```
/balance
```

### 3. تقديم طلب:
```
/neworder
```

### 4. عرض التسعير:
```
/price
```

---

## 🔍 استكشاف الأخطاء

### البوت لا يستجيب:
```bash
python run.py
tail -f log.txt
```

### خطأ في API:
```bash
python test_api_direct.py
```

### الأدمن لا يعمل:
```
تحقق من ADMIN_ID في config.py
```

---

## 📂 هيكل الملفات

```
bot/bot/bot/
├── bot.py                    # المنطق الرئيسي
├── api.py                    # SMM API
├── config.py                 # الإعدادات
├── functions.py              # دوال مساعدة
├── users_manager.py          # نظام الرصيد
├── pricing_system.py         # نظام التسعير
├── admin_system.py           # نظام الأدمن
├── lock_system.py            # نظام القفل
├── advanced_logger.py        # نظام السجلات
├── run.py                    # نقطة التشغيل
├── requirements.txt          # المكتبات
├── DOCUMENTATION_AR.md       # دليل شامل
├── SETUP_GUIDE.md            # دليل الإعداد
├── SUMMARY_AR.md             # ملخص التحديثات
├── QUICK_REFERENCE.md        # هذا الملف
├── users_data.json           # بيانات المستخدمين
├── pricing_config.json       # إعدادات التسعير
└── log.txt                   # السجلات
```

---

## 🎯 تدفق الطلب

```
1. /neworder
   ↓
2. اختيار الخدمة
   ↓
3. إرسال الرابط
   ↓
4. إرسال الكمية
   ↓
5. عرض ملخص الطلب مع السعر
   ↓
6. تأكيد/إلغاء
   ↓
7. التحقق من الرصيد
   ↓
8. خصم الرصيد
   ↓
9. تقديم الطلب لـ API
   ↓
10. نجاح/فشل + استرجاع إذا فشل
```

---

## 💡 نصائح سريعة

1. **اختبر قبل الاستخدام الفعلي**
2. **أضف رصيداً تجريبياً أولاً**
3. **راجع السجلات بانتظام**
4. **احتفظ بنسخ احتياطية**
5. **حدّث الأسعار حسب السوق**

---

## 📞 الدعم

- **دليل شامل:** `DOCUMENTATION_AR.md`
- **إعداد سريع:** `SETUP_GUIDE.md`
- **ملخص التحديثات:** `SUMMARY_AR.md`
- **السجلات:** `log.txt`

---

**🎉 جاهز للاستخدام!**
