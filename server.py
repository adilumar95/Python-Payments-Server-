import os
import logging
import requests
import uuid  # 🔹 For generating unique payment IDs
from flask import Flask, request, jsonify

app = Flask(__name__)

# Telegram Bot Token
BOT_TOKEN = os.getenv("BOT_TOKEN", "7214027935:AAFQ3JP7nRTihzIjJKRT8yRjJBESENHibJ4")
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

# In-memory payment record (should be replaced with a database in production)
latest_payments = {}

# Logging setup
logging.basicConfig(level=logging.INFO)
logging.info("🚀 Telegram Stars Payment Server is Starting...")

@app.route('/')
def home():
    logging.info("✅ Home route accessed")
    return "🚀 Telegram Stars Payment Server is Running!"

# Create an Invoice
@app.route('/create-invoice', methods=['POST'])
def create_invoice():
    logging.info("💰 Invoice request received")
    data = request.json
    user_id = data.get("user_id")

    invoice_payload = {
        "title": "Buy Game Coins",
        "description": "Purchase 1000 coins using Telegram Stars",
        "payload": "buy_1000_coins",  # Static payload (not used for identifying user)
        "provider_token": "",  # Empty for Telegram Stars
        "currency": "XTR",
        "prices": [{"label": "1000 Coins", "amount": 100}]
    }

    response = requests.post(f"{TELEGRAM_API_URL}/createInvoiceLink", json=invoice_payload)
    invoice_data = response.json()

    if invoice_data.get("ok"):
        logging.info("✅ Invoice created successfully")
        return jsonify({"invoice_url": invoice_data["result"]})
    else:
        logging.error(f"❌ Invoice creation failed: {invoice_data}")
        return jsonify({"error": "Failed to create invoice", "details": invoice_data}), 500

# Handle Successful Payment
@app.route('/payment-webhook', methods=['POST'])
def payment_webhook():
    logging.info("🔔 Payment webhook received")
    update = request.json

    if "message" in update and "successful_payment" in update["message"]:
        user_id = str(update["message"]["from"]["id"])
        stars_spent = update["message"]["successful_payment"]["total_amount"] / 100
        coins_to_add = int(stars_spent * 200)
        payment_id = str(uuid.uuid4())  # 🔹 Generate a unique payment ID

        logging.info(f"✅ Payment received! User {user_id} spent {stars_spent} Stars. Adding {coins_to_add} coins.")

        # Save payment data per user
        latest_payments[user_id] = {
            "payment_id": payment_id,
            "coins": coins_to_add
        }

        # Send Confirmation Message
        requests.post(f"{TELEGRAM_API_URL}/sendMessage", json={
            "chat_id": user_id,
            "text": f"✅ Payment successful! You received {coins_to_add} game coins."
        })

        return jsonify({"status": "success", "coins_added": coins_to_add})

    logging.warning("⚠️ Invalid payment update received")
    return jsonify({"status": "error", "message": "Invalid payment update"}), 400

# Endpoint for Unity to Fetch Latest Payment
@app.route('/latest-payment', methods=['GET'])
def latest_payment():
    user_id = request.args.get("user_id", "")
    if user_id in latest_payments:
        return jsonify(latest_payments[user_id])
    else:
        return jsonify({"payment_id": "", "coins": 0})

if __name__ == "__main__":
    PORT = int(os.environ.get("PORT", 10000))  # Use Render's dynamic port
    logging.info(f"🌍 Starting Flask server on port {PORT}...")
    app.run(host="0.0.0.0", port=PORT, debug=True)
