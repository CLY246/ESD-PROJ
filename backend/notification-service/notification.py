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









import os
import json
import pika
import threading
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from rabbitmq import amqp_setup


# Flask App Setup
app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/notification"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Notification(db.Model):
    __tablename__ = 'Notifications'

    NotificationID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)
    OrderID = db.Column(db.Integer, nullable=True)
    NotificationType = db.Column(db.String(50))
    Message = db.Column(db.Text, nullable=False)
    Timestamp = db.Column(db.DateTime, server_default=db.func.current_timestamp())
    IsRead = db.Column(db.Boolean, nullable=False, server_default='0')

    def json(self):
        return {
            "NotificationID": self.NotificationID,
            "UserID": self.UserID,
            "OrderID": self.OrderID,
            "NotificationType": self.NotificationType,
            "Message": self.Message,
            "Timestamp": self.Timestamp,
            "IsRead": self.IsRead
        }

@app.route('/api/health')
def health_check():
    return jsonify({"message": "Notification API is running!"})

@app.route("/notifications", methods=["POST"])
def create_notification():
    data = request.json
    user_id = data.get("UserID")
    order_id = data.get("OrderID")
    notification_type = data.get("NotificationType")
    message = data.get("Message")

    if not user_id or not notification_type or not message:
        return jsonify({"message": "UserID, NotificationType, and Message are required"}), 400

    new_notification = Notification(
        UserID=user_id,
        OrderID=order_id,
        NotificationType=notification_type,
        Message=message
    )

    db.session.add(new_notification)
    db.session.commit()

    return jsonify({"message": "Notification created successfully", "notification": new_notification.json()}), 201

@app.route("/notifications/user/<int:user_id>", methods=["GET"])
def get_notifications_by_user(user_id):
    notifications = Notification.query.filter_by(UserID=user_id).all()
    if not notifications:
        return jsonify({"message": "No notifications found"}), 404
    return jsonify([n.json() for n in notifications])

@app.route("/notifications/<int:notification_id>/read", methods=["PUT"])
def mark_notification_as_read(notification_id):
    notification = Notification.query.get(notification_id)
    if not notification:
        return jsonify({"message": "Notification not found"}), 404
    
    notification.IsRead = True
    db.session.commit()
    return jsonify({"message": "Notification marked as read"})

# AMQP Consumer Setup
RABBIT_HOST = "rabbitmq"
RABBIT_PORT = 5672
EXCHANGE_NAME = "order_topic"
QUEUE_NAME = "Notification"

def callback(channel, method, properties, body):
    """ Callback function to process incoming messages from RabbitMQ """
    try:
        notification_data = json.loads(body)
        print(f"📩 Received Notification Message: {notification_data}")

        # Save to database
        new_notification = Notification(
            UserID=notification_data.get("UserID"),
            OrderID=notification_data.get("OrderID"),
            NotificationType=notification_data.get("NotificationType", "Order Update"),
            Message=notification_data.get("Message", "No message provided"),
        )

        db.session.add(new_notification)
        db.session.commit()

        print("✅ Notification logged successfully in DB")
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        print(f"Message received: {body}")

def consume_notifications():
    """ AMQP Consumer to continuously listen for notifications """
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=RABBIT_HOST, port=RABBIT_PORT)
        )
        channel = connection.channel()
        channel.queue_declare(queue=QUEUE_NAME, durable=True)

        print(f"✅ Connected to RabbitMQ, listening on queue '{QUEUE_NAME}'...")
        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)

        channel.start_consuming()
    except Exception as e:
        print(f"❌ Unable to connect to RabbitMQ: {e}")

if __name__ == '__main__':
    # Start the AMQP Consumer in a separate thread
    threading.Thread(target=consume_notifications, daemon=True).start()

    # Start Flask API
    print("🚀 Starting Flask Notification Service...")
    app.run(host='0.0.0.0', port=5000, debug=True)
