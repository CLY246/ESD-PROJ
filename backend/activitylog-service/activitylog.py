import os
import json
import time
import pika
import threading
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from rabbitmq import amqp_setup  # Use shared setup logic
from sqlalchemy import text
from flasgger import Swagger


# Flask App Setup
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.rykllqzsqugqdvbvxdbv:Smelly246!@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
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

# Endpoint to log activities via Postman
@app.route('/api/log-activity', methods=['POST'])
def log_activity():
    try:
        # Get JSON data from the request
        data = request.get_json()
        activity_description = data.get('Activity_Description')

        if not activity_description:
            return jsonify({"error": "Activity description is required"}), 400

        # Create and save the activity log to the database
        activity_log = Activity(Activity_Description=activity_description)
        db.session.add(activity_log)
        db.session.commit()

        # Return success response with logged data
        return jsonify({
            "message": "Activity logged successfully",
            "activity": activity_log.json()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Endpoint to retrieve all activity logs
@app.route('/api/get-activities', methods=['GET'])
def get_activities():
    try:
        # Query all activity logs from the database
        activities = Activity.query.all()
        if not activities:
            return jsonify({"message": "No activities found"}), 404
        
        # Convert the activity logs to JSON and return as a response
        return jsonify({"activities": [activity.json() for activity in activities]}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/db-check")
def db_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "Connected to DB ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
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

# # Run Flask app
# if __name__ == "__main__":
#     print("🚀 Starting Flask app for Activity Log Service...")
#     app.run(host="0.0.0.0", port=5000, debug=False)



# -------------------- Create tables if not exist --------------------
with app.app_context():
    try:
        db.create_all()
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")

# Run Flask app
if __name__ == "__main__":
    print("🚀 Starting Flask app for Activity Log Service...")
    app.run(host="0.0.0.0", port=5000, debug=False)
