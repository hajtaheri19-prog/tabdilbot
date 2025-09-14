# 🚀 راهنمای نصب و راه‌اندازی ربات تبدیلا

## 📋 پیش‌نیازها

### سیستم عامل
- Windows 10/11
- macOS 10.14+
- Linux (Ubuntu 18.04+, CentOS 7+)

### نرم‌افزارهای مورد نیاز
- Python 3.8 یا بالاتر
- pip (مدیر بسته Python)
- Git (برای کلون کردن پروژه)

---

## 🔧 نصب

### مرحله 1: کلون کردن پروژه
```bash
git clone https://github.com/your-username/telegram-bot.git
cd telegram-bot
```

### مرحله 2: ایجاد محیط مجازی
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

### مرحله 3: نصب وابستگی‌ها
```bash
pip install -r requirements.txt
```

### مرحله 4: تنظیمات
1. فایل `config.py` را باز کنید
2. توکن ربات خود را قرار دهید:
```python
BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
```

3. شناسه ادمین خود را اضافه کنید:
```python
ADMIN_USER_IDS = [YOUR_TELEGRAM_USER_ID]
```

### مرحله 5: اجرای ربات
```bash
python main.py
```

---

## 🔑 دریافت توکن ربات

### مرحله 1: ایجاد ربات جدید
1. به تلگرام بروید و با [@BotFather](https://t.me/BotFather) صحبت کنید
2. دستور `/newbot` را ارسال کنید
3. نام ربات را وارد کنید (مثل: تبدیلا)
4. نام کاربری ربات را وارد کنید (مثل: tabdila_bot)
5. توکن ربات را کپی کنید

### مرحله 2: تنظیم ربات
```
/setdescription - تنظیم توضیحات ربات
/setabouttext - تنظیم متن درباره
/setuserpic - تنظیم تصویر پروفایل
/setcommands - تنظیم دستورات
```

---

## 🆔 دریافت شناسه کاربری

### روش 1: استفاده از ربات
1. با [@userinfobot](https://t.me/userinfobot) صحبت کنید
2. شناسه عددی خود را کپی کنید

### روش 2: استفاده از API
1. پیامی به ربات خود ارسال کنید
2. از API تلگرام استفاده کنید:
```bash
curl "https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates"
```

---

## 🗄️ تنظیم پایگاه داده

### SQLite (پیش‌فرض)
پایگاه داده SQLite به صورت خودکار ایجاد می‌شود.

### PostgreSQL (اختیاری)
```bash
pip install psycopg2-binary
```

در `config.py`:
```python
DATABASE_URL = "postgresql://user:password@localhost/dbname"
```

### MySQL (اختیاری)
```bash
pip install mysql-connector-python
```

در `config.py`:
```python
DATABASE_URL = "mysql://user:password@localhost/dbname"
```

---

## 🔧 تنظیمات پیشرفته

### API Keys
برای استفاده از قابلیت‌های پیشرفته، کلیدهای API زیر را دریافت کنید:

#### OpenWeather API (آب و هوا)
1. به [OpenWeatherMap](https://openweathermap.org/api) بروید
2. حساب کاربری ایجاد کنید
3. کلید API را دریافت کنید
4. در `config.py` قرار دهید:
```python
OPENWEATHER_API_KEY = "your_api_key_here"
```

#### Alpha Vantage API (سهام)
1. به [Alpha Vantage](https://www.alphavantage.co/support/#api-key) بروید
2. کلید API رایگان دریافت کنید
3. در `config.py` قرار دهید:
```python
ALPHA_VANTAGE_API_KEY = "your_api_key_here"
```

#### CoinMarketCap API (ارز دیجیتال)
1. به [CoinMarketCap](https://coinmarketcap.com/api/) بروید
2. حساب کاربری ایجاد کنید
3. کلید API را دریافت کنید
4. در `config.py` قرار دهید:
```python
COINMARKETCAP_API_KEY = "your_api_key_here"
```

#### Google Translate API (ترجمه)
1. به [Google Cloud Console](https://console.cloud.google.com/) بروید
2. پروژه جدید ایجاد کنید
3. Google Translate API را فعال کنید
4. کلید API را دریافت کنید
5. در `config.py` قرار دهید:
```python
GOOGLE_TRANSLATE_API_KEY = "your_api_key_here"
```

---

## 🚀 اجرا در سرور

### استفاده از systemd (Linux)
1. فایل سرویس ایجاد کنید:
```bash
sudo nano /etc/systemd/system/telegram-bot.service
```

2. محتوای زیر را اضافه کنید:
```ini
[Unit]
Description=Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/path/to/your/bot
ExecStart=/path/to/your/bot/venv/bin/python main.py
Restart=always

[Install]
WantedBy=multi-user.target
```

3. سرویس را فعال کنید:
```bash
sudo systemctl enable telegram-bot
sudo systemctl start telegram-bot
```

### استفاده از PM2 (Node.js)
```bash
npm install -g pm2
pm2 start main.py --name telegram-bot --interpreter python
pm2 save
pm2 startup
```

### استفاده از Docker
1. فایل `Dockerfile` ایجاد کنید:
```dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
CMD ["python", "main.py"]
```

2. Docker image بسازید:
```bash
docker build -t telegram-bot .
```

3. Container اجرا کنید:
```bash
docker run -d --name telegram-bot telegram-bot
```

---

## 🔒 امنیت

### تنظیمات امنیتی
1. **توکن ربات**: هرگز توکن را در کد عمومی قرار ندهید
2. **متغیرهای محیطی**: از متغیرهای محیطی استفاده کنید:
```bash
export BOT_TOKEN="your_bot_token"
export ADMIN_USER_IDS="123456789,987654321"
```

3. **فایروال**: پورت‌های غیرضروری را ببندید
4. **به‌روزرسانی**: سیستم را منظم به‌روزرسانی کنید

### پشتیبان‌گیری
```bash
# پشتیبان‌گیری از پایگاه داده
cp bot.db bot_backup_$(date +%Y%m%d).db

# پشتیبان‌گیری از لاگ‌ها
cp bot.log bot_log_backup_$(date +%Y%m%d).log
```

---

## 🐛 عیب‌یابی

### مشکلات رایج

#### ربات پاسخ نمی‌دهد
1. بررسی کنید که توکن صحیح است
2. بررسی کنید که ربات فعال است
3. لاگ‌ها را بررسی کنید:
```bash
tail -f bot.log
```

#### خطای پایگاه داده
1. بررسی کنید که فایل `bot.db` قابل نوشتن است
2. مجوزهای فایل را بررسی کنید:
```bash
chmod 664 bot.db
```

#### خطای API
1. کلیدهای API را بررسی کنید
2. محدودیت نرخ API را بررسی کنید
3. اتصال اینترنت را بررسی کنید

### لاگ‌گیری
```python
import logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
```

---

## 📊 مانیتورینگ

### آمار عملکرد
```bash
# استفاده از CPU
top -p $(pgrep -f main.py)

# استفاده از حافظه
ps aux | grep main.py

# استفاده از دیسک
df -h
```

### لاگ‌های سیستم
```bash
# لاگ‌های systemd
journalctl -u telegram-bot -f

# لاگ‌های PM2
pm2 logs telegram-bot
```

---

## 🔄 به‌روزرسانی

### به‌روزرسانی کد
```bash
git pull origin main
pip install -r requirements.txt
```

### به‌روزرسانی وابستگی‌ها
```bash
pip list --outdated
pip install --upgrade package_name
```

### به‌روزرسانی سیستم
```bash
# Ubuntu/Debian
sudo apt update && sudo apt upgrade

# CentOS/RHEL
sudo yum update

# macOS
brew update && brew upgrade
```

---

## 📞 پشتیبانی

### راه‌های ارتباط
- **GitHub Issues**: [اینجا](https://github.com/your-username/telegram-bot/issues)
- **Email**: support@example.com
- **Telegram**: [@support_bot](https://t.me/support_bot)

### گزارش باگ
هنگام گزارش باگ، اطلاعات زیر را ارسال کنید:
1. نسخه Python
2. نسخه سیستم عامل
3. پیام خطای کامل
4. مراحل تکرار مشکل

---

## 📚 منابع اضافی

### مستندات
- [python-telegram-bot](https://python-telegram-bot.readthedocs.io/)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [SQLite Documentation](https://www.sqlite.org/docs.html)

### آموزش‌ها
- [آموزش Python](https://docs.python.org/3/tutorial/)
- [آموزش Git](https://git-scm.com/docs)
- [آموزش Linux](https://linux.die.net/man/)

---

## ✅ چک‌لیست نصب

- [ ] Python 3.8+ نصب شده
- [ ] پروژه کلون شده
- [ ] محیط مجازی ایجاد شده
- [ ] وابستگی‌ها نصب شده
- [ ] توکن ربات تنظیم شده
- [ ] شناسه ادمین تنظیم شده
- [ ] پایگاه داده ایجاد شده
- [ ] ربات اجرا شده
- [ ] تست عملکرد انجام شده

---

## 🎉 تبریک!

ربات تبدیلا با موفقیت نصب و راه‌اندازی شد! 

حالا می‌توانید:
- از تمام قابلیت‌های ربات استفاده کنید
- پنل مدیریت را مدیریت کنید
- کاربران را مدیریت کنید
- آمار و گزارش‌ها را مشاهده کنید

**نکته**: برای دریافت آخرین به‌روزرسانی‌ها، پروژه را star کنید!

---

*آخرین به‌روزرسانی: 2024*
*نسخه راهنما: 2.0.0*


