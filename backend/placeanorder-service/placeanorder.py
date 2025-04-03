import os
import sys
import json
import pika
import requests

# Add the root path to Python so it can find rabbitmq/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import rabbitmq.amqp_setup as amqp_setup  # ✅ now works

from invokes import invoke_http
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


# placeanorder.py
VENDOR_URL = "http://vendor-service:5000/vendors"    # stays the same
PAYMENT_URL = "http://payment-service:5000/payments"
ORDER_URL   = "http://ordermanagement-service:5000/orders"




# Connect once to RabbitMQ
connection, channel = amqp_setup.connect()

@app.route("/api/health")
def health_check():
    return jsonify({"message": "Place Order Service is running!"})


@app.route("/rabbitmq-health")
def rabbitmq_health():
    if amqp_setup.is_connection_open(connection):
        return jsonify({"status": "RabbitMQ is healthy ✅"}), 200
    else:
        return jsonify({"status": "RabbitMQ connection failed ❌"}), 503



@app.route("/vendors", methods=["GET"])
def fetch_vendors_from_vendor_service():
    try:
        response = requests.get("http://vendor-service:5000/vendors")
        vendors = response.json()
        print("📡 Vendors fetched via placeanorder-service")
        return jsonify({
            "source": "placeanorder",
            "vendors": vendors
        }), response.status_code
    except Exception as e:
        return jsonify({"message": "Failed to fetch vendors", "error": str(e)}), 500


@app.route("/trigger_payment", methods=["POST"])
def handle_trigger_payment():
    order = request.get_json()
    result = trigger_payment(order)
    return jsonify(result), result.get("code", 500)


@app.route("/trigger_ordermanagement", methods=["POST"])
def handle_trigger_ordermanagement():
    data = request.get_json()
    order = data.get("order")
    transaction_data = data.get("transaction_data")
    vendor_info = data.get("vendor_info")

    if not all([order, transaction_data, vendor_info]):
        return jsonify({"code": 400, "message": "Missing required fields"}), 400

    result = trigger_ordermanagement(order, transaction_data, vendor_info)
    return jsonify(result), result.get("code", 500)


@app.route("/trigger_amqp", methods=["POST"])
def handle_trigger_amqp():
    data = request.get_json()
    order_result = data.get("order_result")
    order = data.get("order")
    new_order_id = data.get("new_order_id")

    if not all([order_result, order, new_order_id]):
        return jsonify({"code": 400, "message": "Missing required fields"}), 400

    try:
        trigger_amqp(order_result, order, new_order_id)
        return jsonify({"code": 200, "message": "AMQP notifications sent"}), 200
    except Exception as e:
        return jsonify({"code": 500, "message": str(e)}), 500



# @app.route("/place_order", methods=["POST"])
# def place_order():
#     if request.is_json:
#         try:
#             order = request.get_json()
#             print("\n📦 Received an order in JSON:", order)

#             result = processPlaceOrder(order)
#             return jsonify(result), result["code"]

#         except Exception as e:
#             exc_type, exc_obj, exc_tb = sys.exc_info()
#             fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#             ex_str = str(e) + f" at {exc_type}: {fname}: line {exc_tb.tb_lineno}"
#             print(f"❌ Error: {ex_str}")

#             return jsonify({"code": 500, "message": "place_order.py internal error", "exception": ex_str}), 500

#     return jsonify({"code": 400, "message": "Invalid JSON input"}), 400


def get_vendor_info(vendor_id):
    response = invoke_http(f"{VENDOR_URL}/{vendor_id}")
    if response.get("code") == 200:
        return response["data"]
    return None



def trigger_payment(order):
    total_amount = order.get("TotalAmount")
    if total_amount is None:
        return {
            "code": 400,
            "message": "❌ Missing 'TotalAmount' in order payload",
            "data": order
        }

    payment_payload = {
        "Amount": total_amount
    }

    print("💳 Sending payment payload:", payment_payload)

    payment_result = invoke_http(PAYMENT_URL, method="POST", json=payment_payload)
    print("🧾 Payment response:", payment_result)

    return payment_result


def trigger_ordermanagement(order, transaction_data, vendor_info):
    order_id = transaction_data.get("OrderID")
    transaction_id = transaction_data.get("TransactionID")

    order_payload = {
        "OrderID": order_id,
        "UserID": order["UserID"],
        "TotalAmount": order["TotalAmount"],
        "TransactionID": transaction_id,
        "VendorID": vendor_info["VendorID"],
        "VendorName": vendor_info.get("VendorName", "Unknown"),
        "Cuisine": vendor_info.get("Cuisine", "Unknown"),
        "ImageURL": vendor_info["ImageURL"],
        "Items": order["OrderItems"]
    }

    order_result = invoke_http(ORDER_URL, method="POST", json=order_payload)
    print("📦 Raw order service response:", order_result)

    return order_result


def trigger_amqp(order_result, order, new_order_id):
    # Publish order success
    channel.basic_publish(
        exchange=amqp_setup.EXCHANGE_NAME,
        routing_key="order.info",
        body=json.dumps(order_result)
    )

    try:
        notification_data = {
            "UserID": order["UserID"],
            "OrderID": new_order_id,
            "NotificationType": "Order Update",
            "Message": "🎉 Your order was successfully placed!"
        }

        channel.basic_publish(
            exchange=amqp_setup.EXCHANGE_NAME,
            routing_key="order.placed.order.notification",
            body=json.dumps(notification_data)
        )
        print("📤 Notification sent via RabbitMQ")
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")




if __name__ == "__main__":
    print("🚀 Starting Place Order Service...")
    app.run(host="0.0.0.0", port=5000, debug=True)
