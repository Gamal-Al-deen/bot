# 📘 دليل نظام قاعدة البيانات - Supabase

## 📋 فهرس المحتويات
1. [نظرة عامة على النظام](#نظرة-عامة-على-النظام)
2. [الجداول والعلاقات](#الجداول-والعلاقات)
3. [إعداد Supabase](#إعداد-supabase)
4. [ملف config.py](#ملف-configpy)
5. [ملف database.py](#ملف-databasepy)
6. [كيفية تشغيل البوت](#كيفية-تشغيل-البوت)
7. [نظام التسعير لكل خدمة](#نظام-التسعير-لكل-خدمة)
8. [إدارة الخدمات والأقسام](#إدارة-الخدمات-والأقسام)
9. [أمثلة عملية](#أمثلة-عملية)
10. [استكشاف الأخطاء](#استكشاف-الأخطاء)

---

## نظرة عامة على النظام

تم نقل البوت من نظام تخزين يعتمد على ملفات JSON إلى قاعدة بيانات احترافية **Supabase PostgreSQL** مع:

✅ **قابلية التوسع**: دعم آلاف المستخدمين والطلبات  
✅ **العلاقات**: روابط بين الجداول لضمان سلامة البيانات  
✅ **التسعير لكل خدمة**: كل خدمة لها قاعدة تسعير خاصة (ثابتة أو نسبية)  
✅ **الأمان**: قيود وصلاحيات على مستوى قاعدة البيانات  
✅ **الأداء**: فهارس (Indexes) للاستعلامات السريعة  
✅ **لا فقدان للبيانات**: جميع العمليات محفوظة في قاعدة بيانات سحابية

---

## الجداول والعلاقات

### 1️⃣ users (المستخدمون)
| العمود | النوع | الوصف |
|--------|------|--------|
| user_id | BIGINT (PK) | معرف المستخدم من Telegram |
| username | TEXT | اسم المستخدم |
| first_name | TEXT | الاسم الأول |
| balance | DECIMAL(15,6) | الرصيد الحالي |
| is_admin | BOOLEAN | هل هو أدمن؟ |
| created_at | TIMESTAMP | تاريخ التسجيل |

### 2️⃣ categories (الأقسام)
| العمود | النوع | الوصف |
|--------|------|--------|
| id | SERIAL (PK) | معرف القسم |
| name | TEXT (UNIQUE) | اسم القسم |
| created_at | TIMESTAMP | تاريخ الإنشاء |

### 3️⃣ services (الخدمات)
| العمود | النوع | الوصف |
|--------|------|--------|
| id | SERIAL (PK) | معرف الخدمة في قاعدة البيانات |
| category_id | INTEGER (FK) | رابط للقسم |
| service_api_id | INTEGER | معرف الخدمة من SMM API |
| created_at | TIMESTAMP | تاريخ الإضافة |

⚠️ **مهم**: لا يتم تخزين اسم أو سعر الخدمة هنا - يتم جلبهم من API مباشرة!

### 4️⃣ pricing_rules (قواعد التسعير)
| العمود | النوع | الوصف |
|--------|------|--------|
| id | SERIAL (PK) | معرف قاعدة التسعير |
| service_id | INTEGER (FK) | رابط للخدمة |
| pricing_type | TEXT | نوع التسعير: `fixed` أو `percentage` |
| price_value | DECIMAL | السعر الثابت (لكل 1000) |
| percentage_value | DECIMAL | النسبة المئوية |
| created_at | TIMESTAMP | تاريخ الإنشاء |

### 5️⃣ orders (الطلبات)
| العمود | النوع | الوصف |
|--------|------|--------|
| id | SERIAL (PK) | معرف الطلب في قاعدة البيانات |
| user_id | BIGINT (FK) | رابط للمستخدم |
| service_api_id | INTEGER | معرف الخدمة من API |
| original_price | DECIMAL | السعر الأصلي من API |
| final_price | DECIMAL | السعر النهائي بعد التسعير |
| quantity | INTEGER | الكمية |
| link | TEXT | الرابط |
| status | TEXT | حالة الطلب |
| order_api_id | INTEGER | معرف الطلب من SMM API |
| created_at | TIMESTAMP | تاريخ الطلب |

### 6️⃣ settings (الإعدادات)
| العمود | النوع | الوصف |
|--------|------|--------|
| key | TEXT (PK) | مفتاح الإعداد |
| value | TEXT | قيمة الإعداد |
| updated_at | TIMESTAMP | تاريخ آخر تحديث |

### 7️⃣ channels (القنوات)
| العمود | النوع | الوصف |
|--------|------|--------|
| id | SERIAL (PK) | معرف القناة |
| channel_username | TEXT | يوزرنيم القناة |
| enabled | BOOLEAN | مفعلة؟ |
| created_at | TIMESTAMP | تاريخ الإضافة |

---

## إعداد Supabase

### الخطوة 1: إنشاء مشروع Supabase
1. اذهب إلى https://supabase.com
2. سجّل الدخول أو أنشئ حساب جديد
3. اضغط على **New Project**
4. اختر الاسم وكلمة المرور

### الخطوة 2: تنفيذ SQL Schema
1. اذهب إلى **SQL Editor** من القائمة الجانبية
2. انسخ محتوى ملف `supabase_schema.sql`
3. الصقه في المحرر واضغط **Run**
4. تأكد من إنشاء جميع الجداول السبعة

### الخطوة 3: الحصول على المفاتيح
1. اذهب إلى **Project Settings** ⚙️
2. اختر **API** من القائمة
3. انسخ القيم التالية:
   - **Project URL**: `https://xxxxx.supabase.co`
   - **service_role key** (secret): مفتاح طويل يبدأ بـ `eyJ...`

⚠️ **مهم جداً**: استخدم **service_role** key وليس anon key!

### الخطوة 4: تحديث config.py
افتح ملف `config.py` وعدّل:

```python
SUPABASE_URL = "https://xxxxx.supabase.co"  # ضع رابط مشروعك
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."  # ضع service_role key
```

---

## ملف config.py

يحتوي على إعدادات البوت الأساسية + إعدادات Supabase:

```python
# Telegram Bot Token
BOT_TOKEN = "YOUR_BOT_TOKEN"

# SMM API Configuration
API_KEY = "YOUR_SMM_API_KEY"
API_URL = "https://smmparty.com/api/v2"

# Admin ID
ADMIN_ID = "YOUR_TELEGRAM_ID"

# Supabase Configuration
SUPABASE_URL = "https://xxxxx.supabase.co"
SUPABASE_KEY = "your_service_role_key"
```

---

## ملف database.py

### الوظائف المتاحة:

#### إدارة المستخدمين:
```python
create_user(user_id, username, first_name)  # تسجيل مستخدم
get_user(user_id)                            # جلب بيانات المستخدم
get_balance(user_id)                         # جلب الرصيد
add_balance(user_id, amount)                 # إضافة رصيد
deduct_balance(user_id, amount)              # خصم رصيد
set_balance(user_id, amount)                 # تعيين رصيد
get_all_users_count()                        # عدد المستخدمين
get_all_user_ids()                           # جميع المعرفات
user_exists(user_id)                         # هل المستخدم موجود؟
```

#### إدارة الأقسام:
```python
create_category(name)                        # إنشاء قسم
get_all_categories()                         # جميع الأقسام
get_category_by_name(name)                   # جلب قسم بالاسم
delete_category(category_id)                 # حذف قسم
```

#### إدارة الخدمات:
```python
add_service(category_id, service_api_id)     # إضافة خدمة
get_services_by_category(category_id)        # خدمات القسم
delete_service(service_id)                   # حذف خدمة
get_all_services_flat()                      # جميع الخدمات
get_service_by_api_id(service_api_id)        # جلب خدمة
```

#### قواعد التسعير:
```python
set_pricing_rule(service_id, type, ...)      # تعيين تسعير
get_pricing_rule(service_id)                 # جلب التسعير
calculate_final_price(service_id, rate, qty) # حساب السعر
```

#### إدارة الطلبات:
```python
create_order(...)                            # إنشاء طلب
get_user_orders(user_id)                     # طلبات المستخدم
get_order(order_id)                          # جلب طلب
```

#### الإعدادات والقنوات:
```python
get_setting(key)                             # جلب إعداد
set_setting(key, value)                      # تعيين إعداد
set_channel(username)                        # تعيين قناة
get_channel()                                # جلب القناة
is_channel_configured()                      # هل القناة موجودة؟
```

---

## كيفية تشغيل البوت

### 1. تثبيت المتطلبات
```bash
pip install -r requirements.txt
```

### 2. إعداد Supabase
- أنشئ المشروع ونفّذ SQL Schema
- حدّث `config.py` بـ `SUPABASE_URL` و `SUPABASE_KEY`

### 3. تشغيل البوت
```bash
python run.py
```

### 4. التحقق من الاتصال
عند التشغيل، ستظهر الرسائل التالية في `log.txt`:
```
🗄️ Initializing Supabase Database...
✅ Supabase connected successfully!
🎯 Database system is ready!
```

❌ إذا ظهر خطأ:
```
⚠️ Supabase connection failed!
💡 Please check your SUPABASE_URL and SUPABASE_KEY in config.py
```

---

## نظام التسعير لكل خدمة

### أنواع التسعير:

#### 1️⃣ التسعير النسبي (Percentage)
```
السعر النهائي = السعر الأصلي + (السعر الأصلي × النسبة / 100)
```

**مثال:**
- سعر API: $1.00 لكل 1000
- النسبة: 50%
- السعر النهائي: $1.00 + ($1.00 × 50 / 100) = **$1.50**

#### 2️⃣ التسعير الثابت (Fixed)
```
السعر النهائي = السعر الثابت × (الكمية / 1000)
```

**مثال:**
- السعر الثابت: $2.00 لكل 1000
- الكمية: 5000
- السعر النهائي: $2.00 × (5000 / 1000) = **$10.00**

### تعيين التسعير:

عند إضافة خدمة جديدة، يتم تلقائياً تعيين تسعير نسبي 50%.

لتغيير تسعير خدمة معينة، استخدم الدوال في `pricing_system.py`:

```python
# تسعير نسبي 30%
setPercentPricing(service_db_id, 30.0)

# تسعير ثابت $1.50 لكل 1000
setFixedPricing(service_db_id, 1.50)
```

---

## إدارة الخدمات والأقسام

### إضافة قسم جديد:
1. الأدمن يختار "إضافة قسم" من لوحة التحكم
2. يرسل اسم القسم
3. يتم حفظه في جدول `categories`

### إضافة خدمة:
1. الأدمن يختار القسم
2. يرسل `service_api_id` من SMM API
3. البوت يتحقق من وجود الخدمة في API
4. يتم حفظ الخدمة في جدول `services`
5. يتم تعيين تسعير افتراضي (نسبة 50%) في `pricing_rules`

### حذف قسم:
⚠️ **تحذير**: حذف قسم يحذف جميع خدماته وقواعد تسعيرها تلقائياً (CASCADE DELETE)

---

## أمثلة عملية

### مثال 1: إضافة خدمة بتسعير نسبي

```python
# 1. إضافة قسم
create_category("خدمات Instagram")

# 2. جلب معرف القسم
category = get_category_by_name("خدمات Instagram")
# النتيجة: {'id': 1, 'name': 'خدمات Instagram'}

# 3. إضافة خدمة
service_id = add_service(category['id'], 123)  # 123 من API
# النتيجة: 1 (معرف الخدمة في قاعدة البيانات)

# 4. تعيين تسعير نسبي 40%
set_pricing_rule(service_id, 'percentage', percentage_value=40.0)

# 5. حساب السعر
# إذا كان سعر API = $2.00 لكل 1000
price = calculate_final_price(service_id, 2.0, 1000)
# النتيجة: {'original_price': 2.0, 'final_price': 2.8, 'quantity': 1000}
```

### مثال 2: إضافة خدمة بتسعير ثابت

```python
# إضافة خدمة
service_id = add_service(1, 456)

# تعيين تسعير ثابت $3.00 لكل 1000
set_pricing_rule(service_id, 'fixed', price_value=3.0)

# حساب السعر لـ 5000 عنصر
price = calculate_final_price(service_id, 2.0, 5000)
# النتيجة: {'original_price': 10.0, 'final_price': 15.0, 'quantity': 5000}
# لأن: $3.00 × (5000/1000) = $15.00
```

### مثال 3: تقديم طلب وحفظه

```python
# 1. خصم الرصيد
deduct_balance(user_id, final_price)

# 2. تقديم الطلب لـ API
order_api_id = smm_api.order(service_id, link, quantity)

# 3. حفظ الطلب في قاعدة البيانات
db_order_id = create_order(
    user_id=user_id,
    service_api_id=service_id,
    original_price=original_price,
    final_price=final_price,
    quantity=quantity,
    link=link,
    status='success',
    order_api_id=order_api_id
)
```

---

## استكشاف الأخطاء

### ❌ خطأ: "Supabase connection failed"

**الأسباب:**
- `SUPABASE_URL` أو `SUPABASE_KEY` خاطئة
- لم يتم تنفيذ SQL Schema
- المشروع غير نشط

**الحل:**
1. تأكد من القيم في `config.py`
2. نفّذ `supabase_schema.sql` في SQL Editor
3. تأكد من أن المشروع Running في Supabase

### ❌ خطأ: "relation does not exist"

**السبب:** الجداول غير موجودة

**الحل:**
```sql
-- تحقق من الجداول
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public';
```

إذا كانت مفقودة، نفذ `supabase_schema.sql` مجدداً.

### ❌ خطأ: "duplicate key value violates unique constraint"

**السبب:** محاولة إضافة قسم أو خدمة موجودة

**الحل:** تحقق من الوجود قبل الإضافة (الدوال تفعل ذلك تلقائياً)

### ❌ خطأ: "foreign key constraint"

**السبب:** محاولة إضافة_service بقسم غير موجود

**الحل:** تأكد من وجود القسم أولاً

---

## 🎯 ملخص النظام

| المكون | الوصف |
|--------|--------|
| `config.py` | إعدادات Supabase + البوت |
| `database.py` | جميع عمليات قاعدة البيانات |
| `users_manager.py` | إدارة المستخدمين (يستخدم database.py) |
| `service_manager.py` | إدارة الخدمات (يستخدم database.py) |
| `pricing_system.py` | نظام التسعير لكل خدمة |
| `bot.py` | المنطق الرئيسي + حفظ الطلبات |
| `run.py` | تهيئة قاعدة البيانات عند التشغيل |
| `supabase_schema.sql` | هيكل قاعدة البيانات |

---

## 📞 الدعم

إذا واجهت أي مشاكل:
1. تحقق من `log.txt` للحصول على تفاصيل الخطأ
2. تأكد من إعداد Supabase بشكل صحيح
3. تحقق من أن جميع الجداول موجودة
4. تأكد من تثبيت `supabase` library: `pip install supabase`

---

**✅ تم تصميم هذا النظام ليكون:**
- قابل للتوسع (Scalable)
- آمن (Secure)
- سهل الصيانة (Maintainable)
- احترافي (Professional)

**🚀 جاهز للإنتاج!**
