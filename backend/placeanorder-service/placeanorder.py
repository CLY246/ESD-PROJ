import os
import json
import pika
import sys

import rabbitmq.amqp_setup as amqp_setup  # ✅ Import the fixed amqp_setup

from invokes import invoke_http
from flask import Flask, request, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

ORDER_URL = "http://ordermanagement-service:5000/orders"

# Connect once to RabbitMQ
connection, channel = amqp_setup.connect()

@app.route("/api/health")
def health_check():
    return jsonify({"message": "Place Order Service is running!"})


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


def processPlaceOrder(order):
    # ✅ No reconnection logic, since we connect once at startup
    print("📨 Invoking order microservice...")
    order_result = invoke_http(ORDER_URL, method="POST", json=order)
    print(f"🔁 order_result: {order_result}")

    message = json.dumps(order_result)

    if order_result["code"] not in range(200, 300):
        print("📤 Publish message with routing_key=order.error\n")
        channel.basic_publish(
            exchange=amqp_setup.EXCHANGE_NAME,
            routing_key="order.error",
            body=message
        )
        return {
            "code": 500,
            "data": {"order_result": order_result},
            "message": "Order creation failed"
        }

    print("📤 Publish message with routing_key=order.info\n")
    channel.basic_publish(
        exchange=amqp_setup.EXCHANGE_NAME,
        routing_key="order.info",
        body=message
    )

    # ✅ Send to Notification Microservice
    try:
        notification_data = {
            "UserID": order["UserID"],
            "OrderID": order_result["data"]["OrderID"],
            "NotificationType": "Order Update",
            "Message": "🎉 Your order was successfully placed!"
        }

        channel.basic_publish(
            exchange=amqp_setup.EXCHANGE_NAME,
            routing_key="order.placed.order.notification",  # 📨 Matches *.order.notification
            body=json.dumps(notification_data)
        )
        print("📤 Notification sent via RabbitMQ")
    except Exception as e:
        print(f"❌ Failed to send notification: {e}")

    return {"code": 201, "data": {"order_result": order_result}}



if __name__ == "__main__":
    print("🚀 Starting Place Order Service...")
    app.run(host="0.0.0.0", port=5000, debug=True)
