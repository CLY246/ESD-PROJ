import os
import sys
import json
import pika
import requests
import logging
import stripe

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Add the root path to Python so it can find rabbitmq/
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import rabbitmq.amqp_setup as amqp_setup  # ✅ now works

from invokes import invoke_http
from flask import Flask, request, jsonify
from flask_cors import CORS


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


# placeanorder.py
VENDOR_URL = "http://vendor-service:5000/vendors"    # stays the same
PAYMENT_URL = "http://payment-service:5000/payments"
ORDER_URL   = "http://ordermanagement-service:5000/orders"

pending_orders = {}

# Connect once to RabbitMQ
connection, channel = amqp_setup.connect()

@app.route("/api/health")
def health_check():
    return jsonify({"message": "Place Order Service is running!"})


# @app.route("/rabbitmq-health")
# def rabbitmq_health():
#     if amqp_setup.is_connection_open(connection):
#         return jsonify({"status": "RabbitMQ is healthy"}), 200
#     else:
#         return jsonify({"status": "RabbitMQ connection failed"}), 503



# @app.route("/vendors", methods=["GET"])
# def fetch_vendors_from_vendor_service():
#     try:
#         response = requests.get("http://vendor-service:5000/vendors")
#         vendors = response.json()
#         print("Vendors fetched via placeanorder-service")
#         return jsonify({
#             "source": "placeanorder",
#             "vendors": vendors
#         }), response.status_code
#     except Exception as e:
#         return jsonify({"message": "Failed to fetch vendors", "error": str(e)}), 500


# @app.route("/trigger_payment", methods=["POST"])
# def handle_trigger_payment():
#     order = request.get_json()
#     result = trigger_payment(order)
#     return jsonify(result), result.get("code", 500)


# @app.route("/trigger_ordermanagement", methods=["POST"])
# def handle_trigger_ordermanagement():
#     data = request.get_json()
#     order = data.get("order")
#     transaction_data = data.get("transaction_data")
#     vendor_info = data.get("vendor_info")

#     if not all([order, transaction_data, vendor_info]):
#         return jsonify({"code": 400, "message": "Missing required fields"}), 400

#     result = trigger_ordermanagement(order, transaction_data, vendor_info)
#     return jsonify(result), result.get("code", 500)


# @app.route("/trigger_amqp", methods=["POST"])
# def handle_trigger_amqp():
#     data = request.get_json()
#     order_result = data.get("order_result")
#     order = data.get("order")
#     new_order_id = data.get("new_order_id")

#     if not all([order_result, order, new_order_id]):
#         return jsonify({"code": 400, "message": "Missing required fields"}), 400

#     try:
#         trigger_amqp(order_result, order, new_order_id)
#         return jsonify({"code": 200, "message": "AMQP notifications sent"}), 200
#     except Exception as e:
#         return jsonify({"code": 500, "message": str(e)}), 500


# def get_vendor_info(vendor_id):
#     response = invoke_http(f"{VENDOR_URL}/{vendor_id}")
#     if response.get("code") == 200:
#         return response["data"]
#     return None



def trigger_payment(order):
    total_amount = order.get("TotalAmount")
    if total_amount is None:
        return {
            "code": 400,
            "message": "Missing 'TotalAmount' in order payload",
            "data": order
        }

    payment_payload = {"Amount": total_amount}
    logging.info("Sending payment payload: %s", payment_payload)

    payment_result = requests.post("http://payment-service:5000/payments", json=payment_payload)
    payment_result.raise_for_status()

    return payment_result.json()

@app.route("/place_order", methods=["POST"])
def handle_place_order():
    data = request.get_json()
    order = data.get("order")

    if not order:
        return jsonify({"code": 400, "message": "Missing required fields"}), 400

    try:
        payment_data = trigger_payment(order)
        transaction = payment_data.get("transaction")
        if not transaction:
            return jsonify({"code": 500, "message": "Payment failed"}), 500

        order_id = transaction.get("OrderID")
        transaction_id = transaction.get("TransactionID")
        payment_url = payment_data.get("paymentUrl")

        # Store for later finalization
        pending_orders[order_id] = {
            "order": order,
            "transaction_id": transaction_id
        }

        return jsonify({
            "code": 200,
            "message": "Payment session created",
            "paymentUrl": payment_url,
            "order_id": order_id,
            "transaction_id": transaction_id
        }), 200

    except Exception as e:
        logging.exception("Place order error")
        return jsonify({"code": 500, "message": "Internal error"}), 500
   

@app.route("/finalize_order/<int:order_id>", methods=["POST"])
def finalize_order(order_id):
    pending = pending_orders.get(order_id)
    logging.info(pending_orders)
    if not pending:
        return jsonify({"message": "Order not found or already finalized"}), 404

    order = pending["order"]
    transaction_id = pending["transaction_id"]
    vendor_id = order.get("VendorID")
    user_id = order.get("UserID")
    
    try:
        # 1. Get vendor & user info
        vendor_res = requests.get(f"http://vendor-service:5000/vendors/{vendor_id}")
        vendor_info = vendor_res.json()

        email_res = requests.get(f"http://user-service:5000/email/{user_id}")
        user_email = email_res.json().get("Email")

        # 2. Order Microservice
        order_payload = {
            "OrderID": order_id,
            "UserID": user_id,
            "TotalAmount": order["TotalAmount"],
            "TransactionID": transaction_id,
            "VendorID": vendor_id,
            "VendorName": vendor_info.get("VendorName", "Unknown"),
            "Cuisine": vendor_info.get("Cuisine", "Unknown"),
            "ImageURL": vendor_info.get("ImageURL", ""),
            "Items": order.get("OrderItems")
        }
        invoke_http(ORDER_URL, method="POST", json=order_payload)

        # 3. Order History
        order_history_payload = {
            "UserOrdersAPI": {
                "UserID": user_id,
                "OrderID": order_id,
                "OrderDetails": [
                    {
                        "Id": item["ItemID"],
                        "VendorID": item["VendorID"],
                        "VendorName": vendor_info.get("VendorName", "Unknown"),
                        "Cuisine": vendor_info.get("Cuisine", "Unknown"),
                        "ImageURL": vendor_info.get("ImageURL", ""),
                        "OrderId": order_id,
                    }
                    for item in order["OrderItems"]
                ]
            }
        }
        requests.post(
            "https://personal-aefq3pkb.outsystemscloud.com/OrderManagement/rest/OrderHistory/createHistory",
            json=order_history_payload,
            headers={"Content-Type": "application/json"}
        )

        # 4. Notification
        notification_payload = {
            "UserID": user_id,
            "OrderID": order_id,
            "Email": user_email,
            "TotalAmount": order["TotalAmount"],
            "NotificationType": "Order Update",
            "Message": "Your order was successfully placed!"
        }
        channel.basic_publish(
            exchange="order_topic",
            routing_key="order.placed.order.notification",
            body=json.dumps(notification_payload)
        )

        del pending_orders[order_id]
        return jsonify({"message": "Order finalized successfully"}), 200

    except Exception as e:
        logging.exception("Finalizing order error")
        return jsonify({"message": "Failed to finalize order"}), 500

        

if __name__ == "__main__":
    print("Starting Place Order Service...")
    app.run(host="0.0.0.0", port=5000, debug=True)
