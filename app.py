import ccxt
import requests
import time

# بيانات API من Binance
binance_api_key = "ufWZdhQkNw4TtfbIoWMLYLo5L4WFn7rKPvDBfhkgqn5lXsioB8cxlssWOL0mHkwN"
binance_secret = "LjujCCnshLsCJPYaJ0bzOKmOPQfIJdR10NHkaYe7VojAJrIpAJatWdzlpDoBhOR5"

# بيانات بوت تيليجرام
telegram_token = "7717938028:AAEj7GeCNPmw0O5LSdxoqolnYUspwsCDivM"
chat_id = "6853448995"

# إعداد اتصال Binance
exchange = ccxt.binance({
    'apiKey': binance_api_key,
    'secret': binance_secret,
    'enableRateLimit': True,
})

# تعقب أعلى وأدنى سعر
highest = 0
lowest = float('inf')

# دالة إرسال رسالة تيليجرام
def send_telegram(msg):
    url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
    data = {"chat_id": chat_id, "text": msg}
    requests.post(url, data=data)

# بدء البوت
send_telegram("تم تشغيل بوت مراقبة BTC/USDT")

while True:
    try:
        ticker = exchange.fetch_ticker('BTC/USDT')
        price = ticker['last']

        # فحص القمة الجديدة
        if price > highest:
            highest = price
            send_telegram(f"قمة جديدة: {highest} USD")

        # فحص القاع الجديد
        if price < lowest:
            lowest = price
            send_telegram(f"قاع جديد: {lowest} USD")

        time.sleep(1)  # تحديث سريع (كل ثانية)
    
    except Exception as e:
        send_telegram(f"خطأ في البوت: {str(e)}")
        time.sleep(5)
