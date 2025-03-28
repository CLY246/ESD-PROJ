import os
import sys
import json
import pika

# Add the root path to Python so it can find rabbitmq/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import rabbitmq.amqp_setup as amqp_setup  # ✅ now works

from invokes import invoke_http
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app)


VENDOR_URL = "http://vendor-service:5000/vendors"
PAYMENT_URL = "http://payment-service:5000/payments"  # Update if needed
ORDER_URL = "http://ordermanagement-service:5000/orders"



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





@app.route("/place_order", methods=["POST"])
def place_order():
    if request.is_json:
        try:
            order = request.get_json()
            print("\n📦 Received an order in JSON:", order)

            result = processPlaceOrder(order)
            return jsonify(result), result["code"]

        except Exception as e:
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            ex_str = str(e) + f" at {exc_type}: {fname}: line {exc_tb.tb_lineno}"
            print(f"❌ Error: {ex_str}")

            return jsonify({"code": 500, "message": "place_order.py internal error", "exception": ex_str}), 500

    return jsonify({"code": 400, "message": "Invalid JSON input"}), 400


def get_vendor_info(vendor_id):
    response = invoke_http(f"{VENDOR_URL}/{vendor_id}")
    if response.get("code") == 200:
        return response["data"]
    return None


def processPlaceOrder(order):
    print("📦 Starting order placement process...")

    # Step 1: Get vendor info
    vendor_info = get_vendor_info(order["VendorID"])
    if not vendor_info:
        return {"code": 404, "message": "❌ Vendor not found"}
    print("📦 Vendor info:", vendor_info)

    # Step 2: Build payload for OrderManagement
    order_payload = {
        "OrderID": order["OrderID"], 
        "UserID": order["UserID"],
        "TotalAmount": order["TotalAmount"],
        "TransactionID": order["TransactionID"],
        "VendorID": vendor_info["VendorID"],
        "VendorName": vendor_info["VendorName"],
        "Cuisine": vendor_info["Cuisine"],
        "ImageURL": vendor_info["ImageURL"]
    }

    # Step 3: Create Order
    order_result = invoke_http(ORDER_URL, method="POST", json=order_payload)
    print(f"📦 Order service response: {order_result}")

    if order_result.get("code") not in range(200, 300):
        channel.basic_publish(
            exchange=amqp_setup.EXCHANGE_NAME,
            routing_key="order.error",
            body=json.dumps(order_result)
        )
        return {
            "code": 500,
            "data": {"order_result": order_result},
            "message": "❌ Order creation failed"
        }

    # Step 4: Extract the newly created OrderID
    new_order_id = order_result["data"].get("OrderID")
    print("🆕 Created OrderID:", new_order_id)

    # Step 5: Call payment service
    print("💳 Sending to payment service...")
    payment_payload = {
        "OrderID": new_order_id,
        "Amount": order["TotalAmount"],
        "TransactionID": order["TransactionID"]
    }

    payment_result = invoke_http(PAYMENT_URL, method="POST", json=payment_payload)
    print("🧾 Payment response:", payment_result)

    if payment_result.get("code", 201) != 201:
        return {
            "code": 500,
            "message": "❌ Payment failed",
            "data": payment_result
        }

    # Step 6: Publish order success
    channel.basic_publish(
        exchange=amqp_setup.EXCHANGE_NAME,
        routing_key="order.info",
        body=json.dumps(order_result)
    )

    # Step 7: Notify user
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

    return {"code": 201, "data": {"order_result": order_result, "payment_result": payment_result}}


if __name__ == "__main__":
    print("🚀 Starting Place Order Service...")
    app.run(host="0.0.0.0", port=5000, debug=True)
