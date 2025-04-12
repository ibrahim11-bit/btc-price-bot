import ccxt import requests import time import json from datetime import datetime, timedelta from flask import Flask, render_template_string, request, redirect import os import threading

app = Flask(name)

بيانات تيليجرام

telegram_token = "7836344577:AAFmHU3aTGTuApnEdFzHEvYOoEt2-JhpMVo" chat_id = "6853448995"

سجل التنبيهات

alerts = []

واجهة HTML بسيطة

html_template = """

<!DOCTYPE html><html lang="ar" dir="rtl">
<head>
    <meta charset="UTF-8">
    <title>متابعة سعر البتكوين</title>
</head>
<body>
    <h2>البوت يعمل: متابعة سعر البتكوين بالعربية</h2>
    <form method="post">
        <button type="submit">إرسال السعر الحالي إلى تيليجرام</button>
    </form>
    <h3>آخر التنبيهات:</h3>
    <ul>
        {% for alert in alerts[-5:] %}
            <li>{{ alert }}</li>
        {% endfor %}
    </ul>
</body>
</html>
"""@app.route('/', methods=['GET', 'POST']) def home(): if request.method == 'POST': try: price = exchange.fetch_ticker('BTC/USD')['last'] message = f"السعر الحالي للبتكوين: {price} دولار أمريكي (تم الإرسال يدويًا)" send_telegram(message) alerts.append(message) except Exception as e: alerts.append(f"خطأ في جلب السعر: {e}") return redirect('/') return render_template_string(html_template, alerts=alerts)

def send_telegram(message): try: url = f"https://api.telegram.org/bot{telegram_token}/sendMessage" data = {"chat_id": chat_id, "text": message} r = requests.post(url, data=data) print(f"تم الإرسال: {message}") except Exception as e: print(f"فشل إرسال الرسالة: {e}")

LAST_HOUR_FILE = "last_hour.json"

def load_last_hour(): if os.path.exists(LAST_HOUR_FILE): with open(LAST_HOUR_FILE, 'r') as f: data = json.load(f) return datetime.strptime(data['last_hour'], "%Y-%m-%dT%H:00:00") else: return datetime.now().replace(minute=0, second=0, microsecond=0)

def save_last_hour(hour_time): with open(LAST_HOUR_FILE, 'w') as f: json.dump({"last_hour": hour_time.strftime("%Y-%m-%dT%H:00:00")}, f)

def start_bot(): global exchange exchange = ccxt.kraken() exchange.load_time_difference()

last_checked_hour = load_last_hour()
price = exchange.fetch_ticker('BTC/USD')['last']
high_alert = price
low_alert = price

send_telegram("تم تشغيل بوت متابعة سعر البتكوين لحظيًا، مع تنبيهات القمة والقاع كل ساعة")
send_telegram(f"بداية الساعة: {price} دولار أمريكي")

while True:
    try:
        now = datetime.now()
        current_hour = now.replace(minute=0, second=0, microsecond=0)

        ticker = exchange.fetch_ticker('BTC/USD')
        price = ticker['last']

        print(f"السعر الحالي: {price} | أعلى: {high_alert} | أدنى: {low_alert}")

        if current_hour > last_checked_hour:
            last_checked_hour = current_hour
            save_last_hour(current_hour)
            high_alert = price
            low_alert = price
            msg = f"بدأت ساعة جديدة. السعر الابتدائي: {price} دولار أمريكي"
            send_telegram(msg)
            alerts.append(msg)

        if price > high_alert:
            high_alert = price
            msg = f"⬆️ تم تجاوز أعلى سعر خلال الساعة: {price} دولار أمريكي"
            send_telegram(msg)
            alerts.append(msg)

        elif price < low_alert:
            low_alert = price
            msg = f"⬇️ تم كسر أدنى سعر خلال الساعة: {price} دولار أمريكي"
            send_telegram(msg)
            alerts.append(msg)

        time.sleep(1)

    except Exception as e:
        error_msg = f"حدث خطأ أثناء التشغيل: {str(e)}"
        print(error_msg)
        send_telegram(error_msg)
        alerts.append(error_msg)
        time.sleep(5)

threading.Thread(target=start_bot).start() app.run(host='0.0.0.0', port=10000)

