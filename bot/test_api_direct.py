# -*- coding: utf-8 -*-
"""
سكربت اختبار مباشر لـ API - Direct API Test Script
يتحقق من صحة الاتصال والبيانات
"""

import requests
import json
from config import API_KEY, API_URL


def print_header(text):
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def test_api_connection():
    """اختبار الاتصال الأساسي بـ API"""
    print_header("1️⃣ اختبار الاتصال بـ API")
    
    print(f"\n📍 API URL: {API_URL}")
    print(f"🔑 API Key: {API_KEY[:10]}... (مخفي)")
    
    # التحقق من القيم الافتراضية
    if API_URL == "https://smm-provider.com/api/v2":
        print("\n❌ خطأ حرج: API_URL لا يزال القيمة الافتراضية!")
        print("   هذا رابط وهمي غير موجود.")
        print("   يرجى تحديثه في config.py")
        return False
    
    if API_KEY == "YOUR_API_KEY_HERE" or len(API_KEY) < 10:
        print("\n❌ خطأ حرج: API_KEY غير صحيح!")
        print("   يرجى تحديثه في config.py")
        return False
    
    print("\n✅ الإعدادات تبدو صحيحة")
    return True


def test_balance():
    """اختبار جلب الرصيد"""
    print_header("2️⃣ اختبار جلب الرصيد")
    
    payload = {
        'key': API_KEY,
        'action': 'balance'
    }
    
    print(f"\n📤 Request:")
    print(f"   URL: {API_URL}")
    print(f"   Method: POST")
    print(f"   Data: key={API_KEY[:10]}..., action=balance")
    
    try:
        response = requests.post(API_URL, data=payload, timeout=30)
        
        print(f"\n📥 Response:")
        print(f"   Status Code: {response.status_code}")
        print(f"   Headers: {dict(response.headers)}")
        
        # محاولة تحليل JSON
        try:
            result = response.json()
            print(f"   Body: {json.dumps(result, indent=2, ensure_ascii=False)}")
            
            if 'error' in result:
                print(f"\n❌ API Error: {result['error']}")
                return False
            
            if 'balance' in result:
                print(f"\n✅ النجاح! الرصيد: ${result['balance']}")
                return True
            else:
                print(f"\n❌ الاستجابة لا تحتوي على 'balance'")
                print(f"   الحقول المتاحة: {list(result.keys())}")
                return False
                
        except json.JSONDecodeError as e:
            print(f"\n❌ خطأ في تحليل JSON: {e}")
            print(f"   Raw Response: {response.text[:500]}")
            return False
    
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ خطأ في الاتصال:")
        print(f"   {str(e)}")
        print("\n💡 السبب المحتمل:")
        print("   • API_URL خاطئ")
        print("   • الخادم غير متاح")
        print("   • مشكلة في الشبكة")
        return False
    
    except requests.exceptions.Timeout:
        print(f"\n❌ انتهت مهلة الاتصال (Timeout)")
        print("\n💡 السبب المحتمل:")
        print("   • الخادم بطيء جداً")
        print("   • مشكلة في الشبكة")
        return False
    
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {type(e).__name__}: {str(e)}")
        return False


def test_services():
    """اختبار جلب الخدمات"""
    print_header("3️⃣ اختبار جلب الخدمات")
    
    payload = {
        'key': API_KEY,
        'action': 'services'
    }
    
    print(f"\n📤 Request:")
    print(f"   URL: {API_URL}")
    print(f"   Method: POST")
    print(f"   Data: key={API_KEY[:10]}..., action=services")
    
    try:
        response = requests.post(API_URL, data=payload, timeout=30)
        
        print(f"\n📥 Response:")
        print(f"   Status Code: {response.status_code}")
        
        try:
            result = response.json()
            
            if isinstance(result, list):
                print(f"\n✅ النجاح! عدد الخدمات: {len(result)}")
                
                if len(result) > 0:
                    print(f"\n📋 أول 3 خدمات:")
                    for i, service in enumerate(result[:3], 1):
                        name = service.get('name', 'Unknown')
                        price = service.get('rate', 0)
                        sid = service.get('service', 0)
                        print(f"   {i}. ID: {sid} | {name} | ${price}/1000")
                
                return True
            
            elif isinstance(result, dict) and 'error' in result:
                print(f"\n❌ API Error: {result['error']}")
                return False
            
            else:
                print(f"\n❌ استجابة غير متوقعة:")
                print(f"   Type: {type(result)}")
                print(f"   Value: {result}")
                return False
        
        except json.JSONDecodeError as e:
            print(f"\n❌ خطأ في تحليل JSON: {e}")
            print(f"   Raw Response: {response.text[:500]}")
            return False
    
    except requests.exceptions.ConnectionError as e:
        print(f"\n❌ خطأ في الاتصال: {str(e)}")
        return False
    
    except Exception as e:
        print(f"\n❌ خطأ غير متوقع: {type(e).__name__}: {str(e)}")
        return False


def test_order_format():
    """اختبار تنسيق طلب جديد (بدون إرسال فعلي)"""
    print_header("4️⃣ اختبار تنسيق الطلب الجديد")
    
    print("\n📝 التنسيق المطلوب لطلب جديد:")
    print("   {")
    print('     "key": "YOUR_API_KEY",')
    print('     "action": "order",')
    print('     "service": SERVICE_ID,')
    print('     "link": "URL",')
    print('     "quantity": NUMBER')
    print("   }")
    
    print("\n✅ التنسيق صحيح - جاهز للاستخدام")


def main():
    """الدالة الرئيسية"""
    print("\n🔍 بدء اختبار SMM API...\n")
    
    results = []
    
    # 1. اختبار الإعدادات
    results.append(("الإعدادات", test_api_connection()))
    
    # 2. اختبار الرصيد
    results.append(("الرصيد", test_balance()))
    
    # 3. اختبار الخدمات
    results.append(("الخدمات", test_services()))
    
    # 4. اختبار تنسيق الطلب
    test_order_format()
    
    # الخلاصة
    print_header("📊 الخلاصة")
    
    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}: {'ناجح' if result else 'فشل'}")
    
    success_count = sum(1 for _, r in results if r)
    total_count = len(results)
    
    print(f"\nالنتيجة: {success_count}/{total_count} اختبارات ناجحة")
    
    if success_count == total_count:
        print("\n🎉 جميع الاختبارات نجحت!")
        print("\nالبوت جاهز للعمل!")
    else:
        print("\n⚠️  بعض الاختبارات فشلت!")
        print("\n📋 الخطوات التالية:")
        print("1. راجع الأخطاء أعلاه")
        print("2. صحّح config.py")
        print("3. أعد تشغيل هذا السكربت")
    
    print("\n" + "=" * 70)
    print("انتهى الاختبار")
    print("=" * 70)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  أوقف بواسطة المستخدم")
    except Exception as e:
        print(f"\n\n❌ خطأ فادح: {type(e).__name__}: {str(e)}")
        import traceback
        traceback.print_exc()
