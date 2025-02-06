# استخدام صورة Python الرسمية
FROM python:3.9-slim

# تحديد مسار العمل داخل الحاوية
WORKDIR /app

# نسخ الملفات من جهازك إلى الحاوية
COPY . /app

# تثبيت المتطلبات
RUN pip install --no-cache-dir -r requirements.txt

# تحديد متغير البيئة للبوت توكن
ENV BOT_TOKEN="7841909549:AAE-IP8TXNsmHVZmuXBjb6CEiMvxaljJNz8"

# فتح المنفذ الذي سيتم تشغيله عليه
EXPOSE 5000

# تشغيل التطبيق باستخدام Python
CMD ["python", "app.py"]
