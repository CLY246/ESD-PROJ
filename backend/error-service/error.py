import os
import json
import time
import pika
import threading
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from rabbitmq import amqp_setup
from sqlalchemy import text
from flasgger import Swagger

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres.rykllqzsqugqdvbvxdbv:Smelly246!@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
db = SQLAlchemy(app)

class ErrorLog(db.Model):
    __tablename__ = 'ErrorLog'
    ErrorID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Error_Date = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    Error_Details = db.Column(db.String(1000), nullable=False)

    def __init__(self, Error_Details):
        self.Error_Details = Error_Details

    def json(self):
        return {
            "ErrorID": self.ErrorID,
            "Error_Date": self.Error_Date,
            "Error_Details": self.Error_Details
        }

# Endpoint to log errors via Postman
@app.route('/api/log-error', methods=['POST'])
def log_error():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: API is running
    """
    try:
        # Get JSON data from the request
        data = request.get_json()
        error_details = data.get('Error_Details')

        if not error_details:
            return jsonify({"error": "Error details are required"}), 400

        # Create and save the error log to the database
        error_log = ErrorLog(Error_Details=error_details)
        db.session.add(error_log)
        db.session.commit()

        # Return success response with logged data
        return jsonify({
            "message": "Error logged successfully",
            "error": error_log.json()
        }), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({"message": "Error API is running!"})

monitorBindingKey = "*.error"
QUEUE_NAME = "error"


@app.route("/api/db-check")
def db_check():
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "Connected to DB ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
# Connect to RabbitMQ once
connection, channel = amqp_setup.connect()

def create_error_log(error_details):
    """Creates an activity log entry and commits to the database."""
    with app.app_context():
        try:
            error = ErrorLog(Error_Details=error_details)
            db.session.add(error)
            db.session.commit()
            print(f"📝 Logged error details: {error_details}")
        except Exception as e:
            print(f"❌ Error logging error details: {str(e)}")

def callback(channel, method, properties, body):
    """Handles incoming messages from RabbitMQ."""
    try:
        error_details = body.decode("utf-8")
        create_error_log(error_details)
    except Exception as e:
        print(f"❌ Failed to process message: {str(e)}")

def receive_error_log():
    """Sets up RabbitMQ listener in a separate thread."""
    try:
        # Make sure queue is declared and bound (optional if already done in amqp_setup)
        channel.queue_declare(queue=QUEUE_NAME, durable=True)
        channel.queue_bind(exchange=amqp_setup.EXCHANGE_NAME, queue=QUEUE_NAME, routing_key=monitorBindingKey)

        channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
        print(f"📡 Listening for messages on queue '{QUEUE_NAME}'... [Error Service]")
        channel.start_consuming()
    except Exception as e:
        print(f"❌ RabbitMQ Consumer Error: {str(e)}")

# Start the consumer thread
threading.Thread(target=receive_error_log, daemon=True).start()

# # Run Flask app
# if __name__ == "__main__":
#     print("🚀 Starting Flask app for Error Service...")
#     app.run(host="0.0.0.0", port=5000, debug=False)
    

# # -------------------- Create tables if not exist --------------------
# with app.app_context():
#     db.create_all()

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=os.getenv("FLASK_DEBUG", "False") == "True")


# -------------------- Create tables if not exist --------------------
with app.app_context():
    try:
        db.create_all()
        print("✅ Tables created successfully!")
    except Exception as e:
        print(f"❌ Error creating tables: {str(e)}")

# Run Flask app
if __name__ == "__main__":
    print("🚀 Starting Flask app for Error Service...")
    app.run(host="0.0.0.0", port=5000, debug=False)
