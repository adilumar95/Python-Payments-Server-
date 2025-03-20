import os
import logging
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# 🔹 Replace with your actual Telegram Bot Token
BOT_TOKEN = "7214027935:AAFQ3JP7nRTihzIjJKRT8yRjJBESENHibJ4"
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# 🔹 Set up logging
logging.basicConfig(level=logging.INFO)

@app.route('/')
def home():
    return "🚀 Telegram Stars Payment Server is Running!"

# 🔹 Route to Create an Invoice Link
@app.route('/create-invoice', methods=['POST'])
def create_invoice():
    data = request.json
    user_id = data.get("user_id")

    invoice_payload = {
        "title": "Buy Game Coins",
        "description": "Purchase 1000 coins using Telegram Stars",
        "payload": "buy_1000_coins",
        "provider_token": "",  # Empty for Telegram Stars
        "currency": "XTR",  # Telegram Stars currency
        "prices": [{"label": "1000 Coins", "amount": 100}]
    }

    response = requests.post(f"{TELEGRAM_API_URL}/createInvoiceLink", json=invoice_payload)
    invoice_data = response.json()

    if invoice_data.get("ok"):
        return jsonify({"invoice_url": invoice_data["result"]})
    else:
        return jsonify({"error": "Failed to create invoice", "details": invoice_data}), 500

# 🔹 Route to Handle Successful Payments
@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    update = request.json

    if "message" in update and "successful_payment" in update["message"]:
        user_id = update["message"]["from"]["id"]
        stars_spent = update["message"]["successful_payment"]["total_amount"] / 100
        coins_to_add = stars_spent * 200  # Example: 1 Star = 200 Coins

        logging.info(f"✅ Payment received! User {user_id} spent {stars_spent} Stars. Adding {coins_to_add} coins.")

        # 🔹 Send confirmation message to user
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id,
            "text": f"✅ Payment successful! You received {coins_to_add} game coins."
        })

        return jsonify({"status": "success", "coins_added": coins_to_add})
    
    return jsonify({"status": "error", "message": "Invalid payment update"}), 400

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 3000))
    app.run(host="0.0.0.0", port=PORT)
