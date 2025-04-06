import json
import pika
import threading
import os
import smtplib
import ssl
import traceback
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from rabbitmq import amqp_setup
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
import logging

logging.basicConfig(level=logging.DEBUG)

# Flask App Setup
app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("dbURL") or \
    "mysql+mysqlconnector://root:root@host.docker.internal:3306/notification"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
db = SQLAlchemy(app)

# Connect to RabbitMQ once
connection, channel = amqp_setup.connect()

monitorBindingKey = "order.placed.*.notification"

QUEUE_NAME = "order_notification"  
port = 465
email = "yumsinmytumss@gmail.com"
password = "ncforaixllildixk"  # Gmail App Password


def send_order_email(body):
    try:
        # Parse the incoming JSON message
        data = json.loads(body)
        user_email = data.get("Email")  # Ensure this key is in the RabbitMQ message

        if not user_email:
            logging.error("Error: Missing Email in message!")
            return False  # Don't proceed if email is missing

        logging.info(f"Sending email to: {user_email}")

         # Create email content
        message = MIMEMultipart("alternative")
        message["From"] = email
        message["To"] = user_email
        message["Subject"] = "Order Confirmation"

        # Email body
        text = f"""
        Hi, <br /><br />
        Thank you for your order! <br /><br />
        Order ID: {data.get("OrderID")}<br />
        Total Amount: ${data.get("TotalAmount", "N/A")}<br />
        <br />
        If you have any questions, please contact us. <br /><br />
        Sincerely, <br />
        ESDOrder Team
        """
        html = MIMEText(text, "html")
        message.attach(html)

        # Send email
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            server.login(email, password)
            server.sendmail(email, user_email, message.as_string())

        logging.info("Email sent successfully!")
        return True

    except Exception as e:
        logging.exception(f"Email Sending Error: {e}")
        return False

def callback(channel, method, properties, body):
    logging.info("Received order notification: %s", body)
    success = send_order_email(body)
    if not success:
        logging.warning("Email send failed for message: %s", body) 


def receiveOrderDetail():
    """Sets up RabbitMQ listener in a separate thread."""
    try:
        # Use the existing global connection and channel
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(exchange="order_topic", queue=QUEUE_NAME, routing_key="order.placed.order.notification")
        channel.queue_bind(exchange="order_topic", queue=QUEUE_NAME, routing_key="order.placed.grouporder.notification")

        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
        logging.info(f"Listening for messages on queue '{QUEUE_NAME}'... [Notification Service]")
        channel.start_consuming()
    except Exception as e:
        logging.info(f"RabbitMQ Consumer Error: {str(e)}")


# Health check API endpoint
@app.route('/api/health')
def health_check():
    return jsonify({"message": "Notification API is running!"})


# Test Email API endpoint
@app.route('/send_email', methods=['POST'])
def send_test_email():
    """Manual email testing endpoint"""
    try:
        data = request.get_json()
        if send_order_email(json.dumps(data)):  # Test email with the provided data
            return jsonify({"message": "Email sent successfully!"}), 200
        else:
            return jsonify({"error": "Email Sending Error"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Start the RabbitMQ consumer thread
threading.Thread(target=receiveOrderDetail, daemon=True).start()

# Run Flask app
if __name__ == "__main__":
    print("🚀 Starting Flask app for Notification Service...")
    app.run(host="0.0.0.0", port=5000, debug=True)