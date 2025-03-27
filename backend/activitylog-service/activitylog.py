# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from datetime import datetime

# app = Flask(__name__)
# CORS(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/activitylog"
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# db = SQLAlchemy(app)

# class ActivityLog(db.Model):
#     __tablename__ = 'ActivityLog'
#     ActivityID = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     Timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
#     UserID = db.Column(db.Integer, nullable=True)
#     OrderID = db.Column(db.Integer, nullable=True)
#     EventType = db.Column(db.String(100), nullable=False)
#     Details = db.Column(db.Text, nullable=True)

#     def json(self):
#         return {
#             "ActivityID": self.ActivityID,
#             "Timestamp": self.Timestamp,
#             "UserID": self.UserID,
#             "OrderID": self.OrderID,
#             "EventType": self.EventType,
#             "Details": self.Details
#         }

# @app.route('/api/health')
# def health_check():
#     return jsonify({"message": "Activity Log API is running!"})

# @app.route("/activity", methods=["POST"])
# def log_activity():
#     data = request.json
#     user_id = data.get("UserID")
#     order_id = data.get("OrderID")
#     event_type = data.get("EventType")
#     details = data.get("Details")

#     if not event_type:
#         return jsonify({"message": "EventType is required"}), 400

#     new_activity = ActivityLog(
#         UserID=user_id,
#         OrderID=order_id,
#         EventType=event_type,
#         Details=details
#     )

#     db.session.add(new_activity)
#     db.session.commit()

#     return jsonify({"message": "Activity logged successfully", "activity": new_activity.json()}), 201

# @app.route("/activity", methods=["GET"])
# def get_all_activities():
#     activities = ActivityLog.query.all()
#     return jsonify([a.json() for a in activities])

# @app.route("/activity/<int:activity_id>", methods=["GET"])
# def get_activity_by_id(activity_id):
#     activity = ActivityLog.query.get(activity_id)
#     if not activity:
#         return jsonify({"message": "Activity not found"}), 404
#     return jsonify(activity.json())

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)





import os
import json
import time
import pika
import threading
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from rabbitmq import amqp_setup  # ✅ Use shared setup logic

# Flask App Setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("dbURL") or \
    "mysql+mysqlconnector://root:root@host.docker.internal:3306/activityLog"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
db = SQLAlchemy(app)

# ActivityLog Table
class Activity(db.Model):
    __tablename__ = 'ActivityLog'  # Matches SQL exactly (case-sensitive)

    ActivityID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Activity_Date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    Activity_Description = db.Column(db.String(1000), nullable=False)

    def __init__(self, Activity_Description):
        self.Activity_Description = Activity_Description

    def json(self):
        return {
            "ActivityID": self.ActivityID,
            "Activity_Date": self.Activity_Date,
            "Activity_Description": self.Activity_Description
        }


# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({"message": "Activity Log API is running!"})

monitorBindingKey = "#"
QUEUE_NAME = "activity_log"

# Connect to RabbitMQ once
connection, channel = amqp_setup.connect()

def create_activity_log(activity_description):
    """Creates an activity log entry and commits to the database."""
    with app.app_context():
        try:
            activity = Activity(Activity_Description=activity_description)
            db.session.add(activity)
            db.session.commit()
            print(f"📝 Logged activity: {activity_description}")
        except Exception as e:
            print(f"❌ Error logging activity: {str(e)}")

def callback(channel, method, properties, body):
    """Handles incoming messages from RabbitMQ."""
    try:
        activity_description = body.decode("utf-8")
        create_activity_log(activity_description)
    except Exception as e:
        print(f"❌ Failed to process message: {str(e)}")

def receive_order_log():
    """Sets up RabbitMQ listener in a separate thread."""
    try:
        # Make sure queue is declared and bound (optional if already done in amqp_setup)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(exchange=amqp_setup.EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=monitorBindingKey)

        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
        print(f"📡 Listening for messages on queue '{QUEUE_NAME}'... [Activity Log Service]")
        channel.start_consuming()
    except Exception as e:
        print(f"❌ RabbitMQ Consumer Error: {str(e)}")

# Start the consumer thread
threading.Thread(target=receive_order_log, daemon=True).start()

# Run Flask app
if __name__ == "__main__":
    print("🚀 Starting Flask app for Activity Log Service...")
    app.run(host="0.0.0.0", port=5000, debug=False)