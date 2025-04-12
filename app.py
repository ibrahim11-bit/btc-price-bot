import requests
import time
from datetime import datetime
from flask import Flask, render_template_string, request, redirect
import threading

app = Flask(__name__)

telegram_token = "7836344577:AAFmHU3aTGTuApnEdFzHEvYOoEt2-JhpMVo"
chat_id = "6853448995"
alerts = []

def send_telegram(message):
    try:
        url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
        data = {"chat_id": chat_id, "text": message}
        requests.post(url, data=data)
        print(f"تم الإرسال: {message}")
    except Exception as e:
        print(f"فشل الإرسال: {e}")

def get_binance_price():
    try:
        url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT"
        response = requests.get(url, timeout=5)
        return float(response.json()["price"])
    except Exception as e:
        print(f"خطأ في جلب السعر: {e}")
        return None

def start_bot():
    global alerts
    current_hour = datetime.now().replace(minute=0, second=0, microsecond=0)
    price = get_binance_price()
    high_price = price
    low_price = price
    send_telegram(f"تم تشغيل البوت - السعر الابتدائي: {price} دولار")
    alerts.append(f"تم تشغيل البوت - السعر: {price} دولار")

    while True:
        try:
            now = datetime.now()
            price = get_binance_price()
            if price is None:
                time.sleep(3)
                continue

            new_hour = now.replace(minute=0, second=0, microsecond=0)
            if new_hour > current_hour:
                current_hour = new_hour
                high_price = price
                low_price = price
                msg = f"بدأت ساعة جديدة - السعر الابتدائي: {price} دولار"
                send_telegram(msg)
                alerts.append(msg)

            if price > high_price:
                high_price = price
                msg = f"⬆️ قمة جديدة: {price} دولار"
                send_telegram(msg)
                alerts.append(msg)

            elif price < low_price:
                low_price = price
                msg = f"⬇️ قاع جديد: {price} دولار"
                send_telegram(msg)
                alerts.append(msg)

            time.sleep(1)

        except Exception as e:
            print(f"خطأ: {e}")
            time.sleep(5)

html_template = """
<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head><meta charset="UTF-8"><title>بوت سعر البتكوين</title></head>
<body>
<h2>BTC Bot يعمل</h2>
<form method="post"><button type="submit">إرسال السعر الآن</button></form>
<ul>{% for a in alerts[-5:] %}<li>{{ a }}</li>{% endfor %}</ul>
</body></html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    if request.method == 'POST':
        price = get_binance_price()
        msg = f"السعر الحالي للبتكوين: {price} دولار (إرسال يدوي)"
        send_telegram(msg)
        alerts.append(msg)
        return redirect('/')
    return render_template_string(html_template, alerts=alerts)

threading.Thread(target=start_bot).start()
app.run(host='0.0.0.0', port=10000)
