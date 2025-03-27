# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from datetime import datetime

# app = Flask(__name__)
# CORS(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/notification"
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# db = SQLAlchemy(app)

# class Notification(db.Model):
#     __tablename__ = 'Notifications' 

#     NotificationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     UserID = db.Column(db.Integer, nullable=False)
#     OrderID = db.Column(db.Integer, nullable=True)
#     NotificationType = db.Column(db.String(50))
#     Message = db.Column(db.Text, nullable=False)
#     Timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp())  # Changed to DateTime
#     IsRead = db.Column(db.Boolean, nullable=False, server_default='0')  # Ensure correct MySQL Boolean support

#     def json(self):
#         return {
#             "NotificationID": self.NotificationID,
#             "UserID": self.UserID,
#             "OrderID": self.OrderID,
#             "NotificationType": self.NotificationType,
#             "Message": self.Message,
#             "Timestamp": self.Timestamp,
#             "IsRead": self.IsRead
#         }

# @app.route('/api/health')
# def health_check():
#     return jsonify({"message": "Notification API is running!"})

# @app.route("/notifications", methods=["POST"])
# def create_notification():
#     data = request.json
#     user_id = data.get("UserID")
#     order_id = data.get("OrderID")
#     notification_type = data.get("NotificationType")
#     message = data.get("Message")

#     if not user_id or not notification_type or not message:
#         return jsonify({"message": "UserID, NotificationType, and Message are required"}), 400

#     new_notification = Notification(
#         UserID=user_id,
#         OrderID=order_id,
#         NotificationType=notification_type,
#         Message=message
#     )

#     db.session.add(new_notification)
#     db.session.commit()

#     return jsonify({"message": "Notification created successfully", "notification": new_notification.json()}), 201

# @app.route("/notifications/user/<int:user_id>", methods=["GET"])
# def get_notifications_by_user(user_id):
#     notifications = Notification.query.filter_by(UserID=user_id).all()
#     if not notifications:
#         return jsonify({"message": "No notifications found"}), 404  # Added error handling
#     return jsonify([n.json() for n in notifications])

# @app.route("/notifications/<int:notification_id>/read", methods=["PUT"])
# def mark_notification_as_read(notification_id):
#     notification = Notification.query.get(notification_id)
#     if not notification:
#         return jsonify({"message": "Notification not found"}), 404
    
#     notification.IsRead = True
#     db.session.commit()
#     return jsonify({"message": "Notification marked as read"})

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)









# import os
# import json
# import pika
# import threading
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from datetime import datetime
# from rabbitmq import amqp_setup


# # Flask App Setup
# app = Flask(__name__)
# CORS(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:3306/notification"
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# db = SQLAlchemy(app)

# class Notification(db.Model):
#     __tablename__ = 'Notifications'

#     NotificationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     UserID = db.Column(db.Integer, nullable=False)
#     OrderID = db.Column(db.Integer, nullable=True)
#     NotificationType = db.Column(db.String(50))
#     Message = db.Column(db.Text, nullable=False)
#     Timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp())
#     IsRead = db.Column(db.Boolean, nullable=False, server_default='0')

#     def json(self):
#         return {
#             "NotificationID": self.NotificationID,
#             "UserID": self.UserID,
#             "OrderID": self.OrderID,
#             "NotificationType": self.NotificationType,
#             "Message": self.Message,
#             "Timestamp": self.Timestamp,
#             "IsRead": self.IsRead
#         }

# @app.route('/api/health')
# def health_check():
#     return jsonify({"message": "Notification API is running!"})

# @app.route("/notifications", methods=["POST"])
# def create_notification():
#     data = request.json
#     user_id = data.get("UserID")
#     order_id = data.get("OrderID")
#     notification_type = data.get("NotificationType")
#     message = data.get("Message")

#     if not user_id or not notification_type or not message:
#         return jsonify({"message": "UserID, NotificationType, and Message are required"}), 400

#     new_notification = Notification(
#         UserID=user_id,
#         OrderID=order_id,
#         NotificationType=notification_type,
#         Message=message
#     )

#     db.session.add(new_notification)
#     db.session.commit()

#     return jsonify({"message": "Notification created successfully", "notification": new_notification.json()}), 201

# @app.route("/notifications/user/<int:user_id>", methods=["GET"])
# def get_notifications_by_user(user_id):
#     notifications = Notification.query.filter_by(UserID=user_id).all()
#     if not notifications:
#         return jsonify({"message": "No notifications found"}), 404
#     return jsonify([n.json() for n in notifications])

# @app.route("/notifications/<int:notification_id>/read", methods=["PUT"])
# def mark_notification_as_read(notification_id):
#     notification = Notification.query.get(notification_id)
#     if not notification:
#         return jsonify({"message": "Notification not found"}), 404
    
#     notification.IsRead = True
#     db.session.commit()
#     return jsonify({"message": "Notification marked as read"})

# # AMQP Consumer Setup
# RABBIT_HOST = "rabbitmq"
# RABBIT_PORT = 5672
# EXCHANGE_NAME = "order_topic"
# QUEUE_NAME = "Notification"

# def callback(channel, method, properties, body):
#     """ Callback function to process incoming messages from RabbitMQ """
#     try:
#         notification_data = json.loads(body)
#         print(f"📩 Received Notification Message: {notification_data}")

#         # Save to database
#         new_notification = Notification(
#             UserID=notification_data.get("UserID"),
#             OrderID=notification_data.get("OrderID"),
#             NotificationType=notification_data.get("NotificationType", "Order Update"),
#             Message=notification_data.get("Message", "No message provided"),
#         )

#         db.session.add(new_notification)
#         db.session.commit()

#         print("✅ Notification logged successfully in DB")
#     except Exception as e:
#         print(f"❌ Error processing message: {e}")
#         print(f"Message received: {body}")

# def consume_notifications():
#     """ AMQP Consumer to continuously listen for notifications """
#     try:
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
#         )
#         channel = connection.channel()
#         channel.queue_declare(queue=QUEUE_NAME, durable=True)

#         print(f"✅ Connected to RabbitMQ, listening on queue '{QUEUE_NAME}'...")
#         channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

#         channel.start_consuming()
#     except Exception as e:
#         print(f"❌ Unable to connect to RabbitMQ: {e}")

# if __name__ == '__main__':
#     # Start the AMQP Consumer in a separate thread
#     threading.Thread(target=consume_notifications, daemon=True).start()

#     # Start Flask API
#     print("🚀 Starting Flask Notification Service...")
#     app.run(host='0.0.0.0', port=5000, debug=True)





# import os
# import json
# import pika
# import threading
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from datetime import datetime
# from rabbitmq import amqp_setup
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import traceback

# # Flask App Setup
# app = Flask(__name__)
# CORS(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:3306/notification"
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
# db = SQLAlchemy(app)

# # Database Model
# class Notification(db.Model):
#     __tablename__ = 'notifications'  # 🔁 lowercase to match SQL

#     NotificationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     UserID = db.Column(db.Integer, nullable=False)
#     OrderID = db.Column(db.Integer, nullable=True)
#     NotificationType = db.Column(db.String(50))
#     Message = db.Column(db.Text, nullable=False)
#     Timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp())
#     IsRead = db.Column(db.Boolean, nullable=False, server_default='0')

#     def json(self):
#         return {
#             "NotificationID": self.NotificationID,
#             "UserID": self.UserID,
#             "OrderID": self.OrderID,
#             "NotificationType": self.NotificationType,
#             "Message": self.Message,
#             "Timestamp": self.Timestamp,
#             "IsRead": self.IsRead
#         }

# # Health endpoint
# @app.route('/api/health')
# def health_check():
#     return jsonify({"message": "Notification API is running!"})

# # REST endpoints
# @app.route("/notifications", methods=["POST"])
# def create_notification():
#     data = request.json
#     user_id = data.get("UserID")
#     order_id = data.get("OrderID")
#     notification_type = data.get("NotificationType")
#     message = data.get("Message")

#     if not user_id or not notification_type or not message:
#         return jsonify({"message": "UserID, NotificationType, and Message are required"}), 400

#     new_notification = Notification(
#         UserID=user_id,
#         OrderID=order_id,
#         NotificationType=notification_type,
#         Message=message
#     )

#     db.session.add(new_notification)
#     db.session.commit()

#     return jsonify({"message": "Notification created successfully", "notification": new_notification.json()}), 201

# @app.route("/notifications/user/<int:user_id>", methods=["GET"])
# def get_notifications_by_user(user_id):
#     notifications = Notification.query.filter_by(UserID=user_id).all()
#     if not notifications:
#         return jsonify({"message": "No notifications found"}), 404
#     return jsonify([n.json() for n in notifications])

# @app.route("/notifications/<int:notification_id>/read", methods=["PUT"])
# def mark_notification_as_read(notification_id):
#     notification = Notification.query.get(notification_id)
#     if not notification:
#         return jsonify({"message": "Notification not found"}), 404
    
#     notification.IsRead = True
#     db.session.commit()
#     return jsonify({"message": "Notification marked as read"})

# # RabbitMQ Consumer Setup
# QUEUE_NAME = "order_notification"

# def callback(channel, method, properties, body):
#     try:
#         notification_data = json.loads(body)
#         print(f"📩 Received Notification Message: {notification_data}")

#         new_notification = Notification(
#             UserID=notification_data.get("UserID"),
#             OrderID=notification_data.get("OrderID"),
#             NotificationType=notification_data.get("NotificationType", "Order Update"),
#             Message=notification_data.get("Message", "No message provided"),
#         )

#         db.session.add(new_notification)
#         db.session.commit()

#         print("✅ Notification logged successfully in DB")
#     except Exception as e:
#         print(f"❌ Error processing message: {e}")
#         print(f"Message received: {body}")

# def consume_notifications():
#     try:
#         connection, channel = amqp_setup.connect()

#         # 👇 This service should only declare its own queue
#         channel.queue_declare(queue=QUEUE_NAME, durable=True)
#         channel.queue_bind(exchange=amqp_setup.EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="*.order.notification")

#         print(f"✅ Connected to RabbitMQ, listening on queue '{QUEUE_NAME}'...")
#         channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
#         channel.start_consuming()

#     except Exception as e:
#         print(f"❌ Unable to connect to RabbitMQ: {e}")

# # Start consumer thread
# if __name__ == '__main__':
#     threading.Thread(target=consume_notifications, daemon=True).start()
#     print("🚀 Starting Flask Notification Service...")
#     app.run(host='0.0.0.0', port=5000, debug=True)

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

monitorBindingKey = "*.order.notification"
QUEUE_NAME = "order_notification"  
port = 465
email = "esdprojectt3@gmail.com"
password = "bmvd eeqx hymq nsjs"  # Gmail App Password


def send_order_email(body):
    try:
        # Parse the incoming JSON message to get the order details
        data = json.loads(body)
        userID = "recipient@example.com"  # Replace this with the user's email from the data
        print(f"Sending email to: {userID}")  # Debug line

        # Create the email content
        message = MIMEMultipart("alternative")
        message["From"] = email
        message["To"] = userID
        message["Subject"] = "Order Confirmation"

        # HTML content of the email
        text = """
            Hi, <br />
            <br />
            Thank you for your order!
            <br />
            <br />
            If you have any enquiries, please contact us by replying to this email.
            <br />
            <br />
            Sincerely, <br /> 
            ESDOrder Team
            """
        html = MIMEText(text, "html")
        message.attach(html)

        # Set up SSL context for secure connection
        context = ssl.create_default_context()
        with smtplib.SMTP_SSL("smtp.gmail.com", port, context=context) as server:
            print("Connecting to the email server...")  # Debug line
            server.login(email, password)
            server.sendmail(email, userID, message.as_string())  # Send the email

        print("Email sent to:", userID)
        return True

    except Exception as e:
        print("Error:", str(e))
        traceback.print_exc()
        return False


def callback(channel, method, properties, body):
    """Callback for handling the received RabbitMQ message"""
    print("\nReceived an order notification")
    send_order_email(body)
    print() 


def receiveOrderDetail():
    """Sets up RabbitMQ listener in a separate thread."""
    try:
        # Use the existing global connection and channel
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(exchange=amqp_setup.EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=monitorBindingKey)

        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
        print(f"📡 Listening for messages on queue '{QUEUE_NAME}'... [Notification Service]")
        channel.start_consuming()
    except Exception as e:
        print(f"❌ RabbitMQ Consumer Error: {str(e)}")


# Health check API endpoint
@app.route('/api/health')
def health_check():
    return jsonify({"message": "Notification API is running!"})


# Test Email API endpoint
@app.route('/send_test_email', methods=['POST'])
def send_test_email():
    """Manual email testing endpoint"""
    try:
        data = request.get_json()
        if send_order_email(json.dumps(data)):  # Test email with the provided data
            return jsonify({"message": "Test email sent!"}), 200
        else:
            return jsonify({"error": "Failed to send test email"}), 500
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Start the RabbitMQ consumer thread
threading.Thread(target=receiveOrderDetail, daemon=True).start()

# Run Flask app
if __name__ == "__main__":
    print("🚀 Starting Flask app for Notification Service...")
    app.run(host="0.0.0.0", port=5000, debug=True)