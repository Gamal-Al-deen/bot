# -*- coding: utf-8 -*-
"""
سكربت اختبار البوت - للتأكد من أن كل شيء يعمل
Bot Test Script - Verify everything works

⚠️ قم بتشغيل هذا الملف بعد تعديل config.py
⚠️ Run this script after modifying config.py
"""

from api import SMM_API
from functions import send_message, log_error
from config import BOT_TOKEN, API_KEY, API_URL


def test_config():
    """اختبار الإعدادات"""
    print("=" * 50)
    print("🔍 اختبار الإعدادات...")
    print("=" * 50)
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ خطأ: BOT_TOKEN لم يتم تعديله!")
        return False
    else:
        print("✅ BOT_TOKEN صحيح")
    
    if API_KEY == "YOUR_API_KEY_HERE":
        print("❌ خطأ: API_KEY لم يتم تعديله!")
        return False
    else:
        print("✅ API_KEY صحيح")
    
    if API_URL == "https://your-smm-site.com/api/v2":
        print("⚠️  تحذير: API_URL قد يحتاج إلى تعديل")
    else:
        print("✅ API_URL مخصص")
    
    return True


def test_api():
    """اختبار API"""
    print("\n" + "=" * 50)
    print("🔌 اختبار SMM API...")
    print("=" * 50)
    
    api = SMM_API()
    
    # اختبار الرصيد
    print("\n📊 جاري اختبار الرصيد...")
    balance = api.balance()
    if balance is not None:
        print(f"✅ الرصيد: ${balance:.4f}")
    else:
        print("❌ فشل جلب الرصيد")
    
    # اختبار الخدمات
    print("\n📦 جاري اختبار الخدمات...")
    services = api.services()
    if services:
        print(f"✅ تم جلب {len(services)} خدمة")
        print("\nأول 3 خدمات:")
        for i, service in enumerate(services[:3], 1):
            name = service.get('name', 'Unknown')
            price = service.get('rate', 0)
            print(f"  {i}. {name} - ${price}/1000")
    else:
        print("❌ لا توجد خدمات أو فشل في الاتصال")
    
    return True


def test_logging():
    """اختبار نظام التسجيل"""
    print("\n" + "=" * 50)
    print("📝 اختبار نظام التسجيل...")
    print("=" * 50)
    
    try:
        log_error("🧪 رسالة اختبار - Test message")
        print("✅ تم تسجيل رسالة الاختبار بنجاح")
        print("📄 تحقق من ملف log.txt")
        return True
    except Exception as e:
        print(f"❌ فشل التسجيل: {str(e)}")
        return False


def test_telegram():
    """اختبار Telegram API"""
    print("\n" + "=" * 50)
    print("💬 اختبار Telegram API...")
    print("=" * 50)
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ لا يمكن اختبار Telegram - BOT_TOKEN غير صحيح")
        return False
    
    print("⚠️  لإرسال رسالة اختبار:")
    print("1. شغل البوت: python run.py")
    print("2. أرسل /start للبوت على Telegram")
    print("3. راجع ملف log.txt للنتائج")
    
    return True


def main():
    """الدالة الرئيسية"""
    print("\n🚀 بدء اختبار بوت SMM...\n")
    
    # اختبار الإعدادات
    if not test_config():
        print("\n❌ توقف: يرجى تعديل config.py أولاً!")
        return
    
    # اختبار API
    test_api()
    
    # اختبار التسجيل
    test_logging()
    
    # اختبار Telegram
    test_telegram()
    
    print("\n" + "=" * 50)
    print("✅ انتهى الاختبار!")
    print("=" * 50)
    
    print("\n📋 الخطوات التالية:")
    print("1. إذا نجحت جميع الاختبارات، البوت جاهز")
    print("2. شغل البوت: python run.py")
    print("3. اختبر على Telegram")
    print("4. انشر على Render")
    
    print("\n🎉 حظاً موفقاً!")


if __name__ == '__main__':
    try:
        main()
    except Exception as e:
        print(f"\n❌ خطأ فادح: {str(e)}")
        print("يرجى التحقق من الإعدادات والمحاولة مرة أخرى.")
