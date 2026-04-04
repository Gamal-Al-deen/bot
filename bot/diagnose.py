# -*- coding: utf-8 -*-
"""
سكربت تشخيص البوت - Bot Diagnostic Script
يتحقق من جميع النقاط الحرجة
"""

import requests
import json
from config import BOT_TOKEN, API_KEY, API_URL, TELEGRAM_API_URL


def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60)


def test_bot_token():
    """اختبار BOT_TOKEN"""
    print_header("1️⃣ اختبار BOT_TOKEN")
    
    if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ BOT_TOKEN غير صحيح!")
        return False
    
    url = f"{TELEGRAM_API_URL}{BOT_TOKEN}/getMe"
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            bot_info = result.get('result', {})
            print(f"✅ BOT_TOKEN صحيح!")
            print(f"   اسم البوت: @{bot_info.get('username', 'Unknown')}")
            print(f"   المعرف: {bot_info.get('id', 'Unknown')}")
            return True
        else:
            print(f"❌ خطأ: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        return False


def test_smm_api():
    """اختبار SMM API"""
    print_header("2️⃣ اختبار SMM API")
    
    if not API_KEY or API_KEY == "YOUR_API_KEY_HERE":
        print("❌ API_KEY غير صحيح!")
        return False
    
    if not API_URL or API_URL == "https://your-smm-site.com/api/v2":
        print("⚠️  API_URL قد يحتاج إلى تعديل")
    
    # اختبار الرصيد
    try:
        payload = {'key': API_KEY, 'action': 'balance'}
        response = requests.post(API_URL, data=payload, timeout=10)
        result = response.json()
        
        if 'balance' in result:
            print(f"✅ SMM API يعمل!")
            print(f"   الرصيد: ${result['balance']}")
            return True
        elif 'error' in result:
            print(f"⚠️  خطأ من API: {result['error']}")
            return False
        else:
            print(f"❌ استجابة غير متوقعة: {result}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال بـ SMM: {str(e)}")
        return False


def test_get_updates():
    """اختبار getUpdates"""
    print_header("3️⃣ اختبار getUpdates (Long Polling)")
    
    url = f"{TELEGRAM_API_URL}{BOT_TOKEN}/getUpdates"
    params = {'offset': 0, 'timeout': 5}
    
    try:
        response = requests.get(url, params=params, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            updates = result.get('result', [])
            print(f"✅ getUpdates يعمل!")
            print(f"   عدد التحديثات: {len(updates)}")
            
            if updates:
                print(f"\n   آخر تحديث:")
                last_update = updates[-1]
                if 'message' in last_update:
                    msg = last_update['message']
                    print(f"   من: {msg.get('from', {}).get('first_name', 'Unknown')}")
                    print(f"   النص: {msg.get('text', 'No text')}")
            
            return True
        else:
            print(f"❌ خطأ: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        return False


def check_webhook():
    """التحقق من webhook"""
    print_header("4️⃣ التحقق من Webhook")
    
    url = f"{TELEGRAM_API_URL}{BOT_TOKEN}/getWebhookInfo"
    
    try:
        response = requests.get(url, timeout=10)
        result = response.json()
        
        if result.get('ok'):
            webhook_info = result.get('result', {})
            url_webhook = webhook_info.get('url', '')
            
            if not url_webhook or url_webhook == '':
                print("✅ لا يوجد webhook (يستخدم Long Polling)")
                return True
            else:
                print(f"⚠️  هناك webhook نشط: {url_webhook}")
                print("   يُلغى استخدامه مع Long Polling!")
                print("   للحذف: افتح المتصفح واذهب إلى:")
                delete_url = f"{TELEGRAM_API_URL}{BOT_TOKEN}/deleteWebhook"
                print(f"   {delete_url}")
                return False
        else:
            print(f"❌ خطأ: {result.get('description')}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ: {str(e)}")
        return False


def test_render_url():
    """اختبار Render URL"""
    print_header("5️⃣ اختبار Render URL")
    
    render_url = input("أدخل رابط Render (مثال: https://bot-1-u5r4.onrender.com/): ").strip()
    
    if not render_url:
        print("⏭️  تخطي الاختبار")
        return True
    
    try:
        # اختبار الصفحة الرئيسية
        response = requests.get(render_url, timeout=10)
        
        if response.status_code == 200:
            print(f"✅ Render URL يعمل!")
            print(f"   الحالة: {response.status_code}")
            
            if "SMM Bot is Running" in response.text:
                print("   ✅ صفحة الحالة تظهر!")
            else:
                print("   ⚠️  صفحة الحالة لا تظهر بشكل صحيح")
            
            # اختبار health endpoint
            health_url = f"{render_url}/health"
            try:
                health_response = requests.get(health_url, timeout=5)
                if health_response.status_code == 200:
                    print(f"   ✅ Health endpoint يعمل!")
                    print(f"   الصحة: {health_response.text}")
            except:
                print(f"   ⚠️  Health endpoint لم يستجب")
            
            return True
        else:
            print(f"❌ Render URL لا يعمل: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ خطأ في الاتصال: {str(e)}")
        return False


def main():
    """الدالة الرئيسية"""
    print("\n🔍 بدء تشخيص بوت SMM...\n")
    
    results = []
    
    # 1. اختبار BOT_TOKEN
    results.append(("BOT_TOKEN", test_bot_token()))
    
    # 2. اختبار SMM API
    results.append(("SMM API", test_smm_api()))
    
    # 3. اختبار getUpdates
    results.append(("getUpdates", test_get_updates()))
    
    # 4. التحقق من webhook
    results.append(("Webhook", check_webhook()))
    
    # 5. اختبار Render URL
    results.append(("Render URL", test_render_url()))
    
    # الخلاصة
    print_header("📊 الخلاصة")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}: {'ناجح' if result else 'فشل'}")
    
    # النتيجة النهائية
    success_count = sum(1 for _, r in results if r)
    total_count = len(results)
    
    print(f"\nالنتيجة: {success_count}/{total_count} اختبارات ناجحة")
    
    if success_count == total_count:
        print("\n🎉 جميع الاختبارات نجحت!")
        print("\nالخطوات التالية:")
        print("1. تأكد من أن البوت يعمل على Render")
        print("2. راقب Logs على Render")
        print("3. جرّب /start على Telegram")
    else:
        print("\n⚠️  بعض الاختبارات فشلت!")
        print("راجع النتائج أعلاه وقم بإصلاح المشاكل.")
    
    print("\n" + "=" * 60)
    print("انتهى التشخيص")
    print("=" * 60)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  أوقف بواسطة المستخدم")
    except Exception as e:
        print(f"\n\n❌ خطأ فادح: {str(e)}")
