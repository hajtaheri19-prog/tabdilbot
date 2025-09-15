# 🧪 راهنمای کامل تست ربات تبدیلا

## 📋 **مراحل تست ربات**

### **1. تست اولیه - بررسی وابستگی‌ها**
```bash
# بررسی نصب python-telegram-bot
python -c "import telegram; print('✅ python-telegram-bot:', telegram.__version__)"

# بررسی سایر وابستگی‌ها
python -c "import requests, aiohttp, jdatetime, hijridate, babel, pytz; print('✅ All dependencies OK')"
```

### **2. تست عملکرد ماژول‌ها**
```bash
# تست عملکرد کلی
python test_bot.py

# تست آفلاین کامل
python test_offline.py

# تست API های ارز دیجیتال
python test_crypto_apis.py
```

### **3. تست اتصال به اینترنت**
```bash
# تست اتصال به API های خارجی
python -c "
import requests
try:
    r = requests.get('https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd', timeout=5)
    print('✅ Internet connection OK')
except:
    print('❌ Internet connection failed')
"
```

### **4. تست ربات در حالت آفلاین**
```bash
# تست بدون اتصال به اینترنت
python test_offline.py
```

### **5. تست ربات در حالت آنلاین**
```bash
# اجرای ربات اصلی
python run_bot.py

# یا ربات ساده
python simple_bot.py
```

---

## 🔍 **نحوه تست دستی ربات**

### **مرحله 1: شروع ربات**
1. ربات را در تلگرام پیدا کنید
2. دستور `/start` را ارسال کنید
3. باید پیام خوش‌آمدگویی دریافت کنید

### **مرحله 2: تست تبدیل واحد**
```
کاربر: 10 km to mile
ربات: 📏 تبدیل length
      📊 10 km = 6.21 mile
```

### **مرحله 3: تست محاسبه**
```
کاربر: 2 + 3 * 4
ربات: 🧮 محاسبه: 2 + 3 * 4
      📊 نتیجه: 14
```

### **مرحله 4: تست قیمت ارز دیجیتال**
```
کاربر: BTC
ربات: 💰 BTC
      💵 قیمت: $115,659.00
      📈 تغییر 24h: -0.12%
      📊 حجم 24h: $15,234,567,890
      🏢 ارزش بازار: $2,300,000,000,000
      🔗 منبع: coingecko
```

### **مرحله 5: تست چندین ارز**
```
کاربر: BTC,ETH,DOGE
ربات: 💰 قیمت‌های ارزهای دیجیتال
      BTC: $115,659.00 📈 +2.45%
      ETH: $4,622.11 📉 -1.23%
      DOGE: $0.28 📈 +5.67%
```

### **مرحله 6: تست منوها**
- روی دکمه‌های منو کلیک کنید
- بررسی کنید که همه منوها کار می‌کنند
- تست کنید که برگشت به منوی اصلی کار می‌کند

---

## 🚨 **مشکلات رایج و راه‌حل‌ها**

### **مشکل 1: Timeout در اتصال**
```
❌ Error: Timed out
```
**راه‌حل:**
- اتصال اینترنت را بررسی کنید
- فایروال را بررسی کنید
- از ربات آفلاین استفاده کنید

### **مشکل 2: API های خارجی کار نمی‌کنند**
```
❌ Cannot connect to host api.binance.com
```
**راه‌حل:**
- این مشکل طبیعی است در ایران
- CoinGecko معمولاً کار می‌کند
- از VPN استفاده کنید

### **مشکل 3: Database Error**
```
❌ Database connection failed
```
**راه‌حل:**
- فایل `bot.db` را حذف کنید
- ربات را دوباره اجرا کنید
- دیتابیس خودکار ایجاد می‌شود

### **مشکل 4: Import Error**
```
❌ ModuleNotFoundError
```
**راه‌حل:**
```bash
pip install -r requirements.txt
```

---

## 📊 **نتایج تست موفق**

### **تست آفلاین:**
```
🧪 تست آفلاین ربات تبدیلا
==================================================
1️⃣ Testing Database...
✅ Database initialized successfully

2️⃣ Testing Unit Converter...
✅ Length: 10 km = 6.21 mile
✅ Weight: 100 kg = 220.46 lb
✅ Temperature: 25°C = 77.00°F

3️⃣ Testing Calculator...
✅ 2 + 3 * 4 = 14
✅ sqrt(16) = 4
✅ sin(pi/2) = 1
✅ log(100) = 4.605170186

4️⃣ Testing Date Converter...
✅ Current time (IRST): 2025-09-14 23:21:08

5️⃣ Testing UI Components...
✅ Welcome message: 505 characters
✅ Main menu keyboard: 6 rows
✅ Currency menu keyboard: 3 rows

6️⃣ Testing Admin Service...
✅ User stats: 0 conversions

🎉 All offline tests completed successfully!
✅ Bot is ready for online testing!
```

### **تست آنلاین:**
```
🌐 Testing Online APIs...
==============================
✅ Crypto API: BTC = $115,659.00
⏰ Currency API timeout (10s) - this is normal if internet is slow
✅ Online API tests completed!
```

---

## 🎯 **چک‌لیست تست**

### **✅ تست‌های ضروری:**
- [ ] نصب وابستگی‌ها
- [ ] ایجاد دیتابیس
- [ ] تست تبدیل واحد
- [ ] تست محاسبه
- [ ] تست تاریخ
- [ ] تست UI
- [ ] تست admin service

### **✅ تست‌های اختیاری:**
- [ ] تست API های ارز دیجیتال
- [ ] تست تبدیل ارز
- [ ] تست آب و هوا
- [ ] تست ترجمه

### **✅ تست‌های کاربری:**
- [ ] دستور /start
- [ ] منوهای مختلف
- [ ] تشخیص هوشمند متن
- [ ] inline query
- [ ] error handling

---

## 🚀 **اجرای نهایی ربات**

### **روش 1: ربات نهایی (پیشنهادی)**
```bash
python run_bot.py
```

### **روش 2: ربات ساده**
```bash
python simple_bot.py
```

### **روش 3: ربات پیشرفته**
```bash
python advanced_bot.py
```

---

## 📱 **تست در تلگرام**

### **1. پیدا کردن ربات:**
- نام کاربری ربات را در تلگرام جستجو کنید
- یا از لینک مستقیم استفاده کنید

### **2. شروع مکالمه:**
```
/start
```

### **3. تست دستورات:**
```
/help
/menu
```

### **4. تست تبدیل‌ها:**
```
10 km to mile
100 USD to IRR
BTC
2 + 3 * 4
```

### **5. تست منوها:**
- روی دکمه‌های مختلف کلیک کنید
- بررسی کنید که همه کار می‌کنند

---

## 🎉 **نتیجه نهایی**

**اگر همه تست‌ها موفق باشند:**
- ✅ ربات آماده استفاده است
- ✅ تمام قابلیت‌ها کار می‌کنند
- ✅ API ها به درستی متصل شده‌اند
- ✅ دیتابیس ایجاد شده
- ✅ UI کاملاً عملکرد دارد

**ربات تبدیلا آماده ارائه خدمات پیشرفته به کاربران است! 🚀**






