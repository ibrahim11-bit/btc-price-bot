import requests import time from datetime import datetime, timedelta from flask import Flask, render_template_string, request, redirect import threading

app = Flask(name)

telegram_token = "7836344577:AAFmHU3aTGTuApnEdFzHEvYOoEt2-JhpMVo" chat_id = "6853448995" alerts = []

إرسال رسالة إلى تيليجرام

def send_telegram(message): try: url = f"https://api.telegram.org/bot{telegram_token}/sendMessage" data = {"chat_id": chat_id, "text": message} requests.post(url, data=data) print(f"تم الإرسال: {message}") except Exception as e: print(f"فشل الإرسال: {e}")

الحصول على سعر البيتكوين من بينانس

def get_binance_price(): try: url = "https://api.binance.com/api/v3/ticker/price?symbol=BTCUSDT" response = requests.get(url, timeout=5) return float(response.json()["price"]) except Exception as e: print(f"خطأ في جلب السعر: {e}") return None

تشغيل البوت في الخلفية

def start_bot(): global alerts current_hour = datetime.now().replace(minute=0, second=0, microsecond=0) daily_reference = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)

price = get_binance_price()
high_price = price
low_price = price
daily_high = price
daily_low = price
last_5min_alert = datetime.now() - timedelta(minutes=5)

send_telegram(f"تم تشغيل البوت - السعر الابتدائي: {price} دولار")
alerts.append(f"تم التشغيل - السعر: {price} دولار")

while True:
    try:
        now = datetime.now()
        price = get_binance_price()
        if price is None:
            time.sleep(3)
            continue

        print(f"{now.strftime('%H:%M:%S')} | السعر الحالي: {price} | القمة: {high_price} | القاع: {low_price}")

        # تنبيه كل 5 دقائق بالسعر الحالي
        if (now - last_5min_alert).total_seconds() >= 300:
            msg = f"⏱️ تحديث 5 دقائق: السعر الحالي = {price} دولار"
            send_telegram(msg)
            alerts.append(msg)
            last_5min_alert = now

        # بداية ساعة جديدة
        new_hour = now.replace(minute=0, second=0, microsecond=0)
        if new_hour > current_hour:
            # محاكاة تداول وهمي
            buy_price = low_price
            sell_price = high_price
            profit = round(sell_price - buy_price, 2)
            trade_summary = f"🧪 محاكاة التداول - ملخص الساعة:\n⬇️ شراء عند: {buy_price}\n⬆️ بيع عند: {sell_price}\n💰 الربح النظري: {profit} دولار (1 BTC)"
            send_telegram(trade_summary)
            alerts.append(trade_summary)

            # ملخص الساعة العادي
            summary = f"🕐 ملخص الساعة:\n⬆️ أعلى سعر: {high_price}\n⬇️ أقل سعر: {low_price}\n↔️ الفرق: {round(high_price - low_price, 2)} دولار"
            send_telegram(summary)
            alerts.append(summary)

            # إعادة التعيين
            current_hour = new_hour
            high_price = price
            low_price = price

        # بداية يوم جديد
        if now.date() > daily_reference.date():
            daily_summary = f"📊 ملخص اليوم:\n⬆️ أعلى سعر: {daily_high}\n⬇️ أقل سعر: {daily_low}\n↔️ الفرق: {round(daily_high - daily_low, 2)} دولار"
            send_telegram(daily_summary)
            alerts.append(daily_summary)
            daily_reference = now.replace(hour=0, minute=0, second=0, microsecond=0)
            daily_high = price
            daily_low = price

        # تنبيه القمة
        if price > high_price:
            high_price = price
            msg = f"⬆️ قمة جديدة: {price} دولار"
            send_telegram(msg)
            alerts.append(msg)

        # تنبيه القاع
        elif price < low_price:
            low_price = price
            msg = f"⬇️ قاع جديد: {price} دولار"
            send_telegram(msg)
            alerts.append(msg)

        # تحديث القمة اليومية
        if price > daily_high:
            daily_high = price
        # تحديث القاع اليومي
        if price < daily_low:
            daily_low = price

        time.sleep(1)

    except Exception as e:
        print(f"خطأ أثناء التشغيل: {e}")
        time.sleep(5)

واجهة الويب

html_template = """

<!DOCTYPE html><html lang=\"ar\" dir=\"rtl\">
<head><meta charset=\"UTF-8\"><title>بوت البتكوين</title></head>
<body>
<h2>البوت يعمل - BTC</h2>
<form method=\"post\"><button type=\"submit\">إرسال السعر الآن</button></form>
<ul>{% for a in alerts[-5:] %}<li>{{ a }}</li>{% endfor %}</ul>
</body></html>
"""@app.route('/', methods=['GET', 'POST']) def home(): if request.method == 'POST': price = get_binance_price() msg = f"السعر الحالي للبتكوين: {price} دولار (إرسال يدوي)" send_telegram(msg) alerts.append(msg) return redirect('/') return render_template_string(html_template, alerts=alerts)

تشغيل البوت والواجهة

threading.Thread(target=start_bot).start() app.run(host='0.0.0.0', port=10000)

