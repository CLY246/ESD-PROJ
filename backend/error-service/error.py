# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from datetime import datetime

# app = Flask(__name__)
# CORS(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/error"
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

# db = SQLAlchemy(app)

# class ErrorLog(db.Model):
#     __tablename__ = 'ErrorLog'
#     ErrorID = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     Timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
#     ServiceName = db.Column(db.String(100), nullable=False)
#     OrderID = db.Column(db.Integer, nullable=True)
#     ErrorDetails = db.Column(db.Text, nullable=False)
#     Severity = db.Column(db.String(20), nullable=False)

#     def json(self):
#         return {
#             "ErrorID": self.ErrorID,
#             "Timestamp": self.Timestamp,
#             "ServiceName": self.ServiceName,
#             "OrderID": self.OrderID,
#             "ErrorDetails": self.ErrorDetails,
#             "Severity": self.Severity
#         }

# @app.route('/api/health')
# def health_check():
#     return jsonify({"message": "Error API is running!"})

# @app.route("/errors", methods=["POST"])
# def log_error():
#     data = request.json
#     service_name = data.get("ServiceName")
#     order_id = data.get("OrderID")
#     error_details = data.get("ErrorDetails")
#     severity = data.get("Severity")

#     if not service_name or not error_details or not severity:
#         return jsonify({"message": "ServiceName, ErrorDetails, and Severity are required"}), 400

#     new_error = ErrorLog(
#         ServiceName=service_name,
#         OrderID=order_id,
#         ErrorDetails=error_details,
#         Severity=severity
#     )

#     db.session.add(new_error)
#     db.session.commit()

#     return jsonify({"message": "Error logged successfully", "error": new_error.json()}), 201

# @app.route("/errors", methods=["GET"])
# def get_errors():
#     errors = ErrorLog.query.all()
#     return jsonify([e.json() for e in errors])

# @app.route("/errors/<int:error_id>", methods=["GET"])
# def get_error_by_id(error_id):
#     error = ErrorLog.query.get(error_id)
#     if not error:
#         return jsonify({"message": "Error not found"}), 404
#     return jsonify(error.json())

# if __name__ == '__main__':
#     app.run(host='0.0.0.0', port=5000, debug=True)


# import os
# import json
# import threading
# from flask import Flask, request, jsonify
# from flask_sqlalchemy import SQLAlchemy
# from flask_cors import CORS
# from rabbitmq import amqp_setup

# # Flask App Setup
# app = Flask(__name__)
# CORS(app)

# app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:3306/ErrorLog"
# app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
# db = SQLAlchemy(app)


# # DB Model
# class ErrorLog(db.Model):
#     __tablename__ = 'ErrorLog'
#     ErrorID = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     Timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
#     ServiceName = db.Column(db.String(100), nullable=False)
#     OrderID = db.Column(db.Integer, nullable=True)
#     ErrorDetails = db.Column(db.Text, nullable=False)
#     Severity = db.Column(db.String(20), nullable=False)

#     def json(self):
#         return {
#             "ErrorID": self.ErrorID,
#             "Timestamp": self.Timestamp,
#             "ServiceName": self.ServiceName,
#             "OrderID": self.OrderID,
#             "ErrorDetails": self.ErrorDetails,
#             "Severity": self.Severity
#         }

# # Health endpoint
# @app.route('/api/health')
# def health_check():
#     return jsonify({"message": "Error API is running!"})

# # Logging API
# @app.route("/errors", methods=["POST"])
# def log_error():
#     data = request.json
#     service_name = data.get("ServiceName")
#     order_id = data.get("OrderID")
#     error_details = data.get("ErrorDetails")
#     severity = data.get("Severity")

#     if not service_name or not error_details or not severity:
#         return jsonify({"message": "ServiceName, ErrorDetails, and Severity are required"}), 400

#     new_error = ErrorLog(
#         ServiceName=service_name,
#         OrderID=order_id,
#         ErrorDetails=error_details,
#         Severity=severity
#     )

#     db.session.add(new_error)
#     db.session.commit()

#     return jsonify({"message": "Error logged successfully", "error": new_error.json()}), 201

# @app.route("/errors", methods=["GET"])
# def get_errors():
#     errors = ErrorLog.query.all()
#     return jsonify([e.json() for e in errors])

# @app.route("/errors/<int:error_id>", methods=["GET"])
# def get_error_by_id(error_id):
#     error = ErrorLog.query.get(error_id)
#     if not error:
#         return jsonify({"message": "Error not found"}), 404
#     return jsonify(error.json())

# # --- RabbitMQ Consumer Setup ---
# QUEUE_NAME = "error"

# def callback(channel, method, properties, body):
#     """Handles incoming error messages from RabbitMQ"""
#     try:
#         error_data = json.loads(body)
#         print(f"📩 Received Error Message: {error_data}")

#         new_error = ErrorLog(
#             ServiceName=error_data.get("ServiceName", "Unknown"),
#             OrderID=error_data.get("OrderID"),
#             ErrorDetails=error_data.get("ErrorDetails", "No details"),
#             Severity=error_data.get("Severity", "Low"),
#         )

#         db.session.add(new_error)
#         db.session.commit()

#         print("✅ Error logged successfully in DB")
#     except Exception as e:
#         print(f"❌ Error processing message: {e}")
#         print(f"Message received: {body}")

# def consume_errors():
#     """Starts consuming from RabbitMQ error queue"""
#     try:
#         connection, channel = amqp_setup.connect()

#         # Declare & bind only this service's queue
#         channel.queue_declare(queue=QUEUE_NAME, durable=True)
#         channel.queue_bind(exchange=amqp_setup.EXCHANGE_NAME, queue=QUEUE_NAME, routing_key="*.error")

#         print(f"✅ Connected to RabbitMQ, listening on queue '{QUEUE_NAME}'...")
#         channel.basic_consume(queue=QUEUE_NAME, on_message_callback=callback, auto_ack=True)
#         channel.start_consuming()
#     except Exception as e:
#         print(f"❌ Unable to connect to RabbitMQ: {e}")

# # Start consumer thread + Flask app
# if __name__ == '__main__':
#     threading.Thread(target=consume_errors, daemon=True).start()
#     print("🚀 Starting Flask Error Service...")
#     app.run(host='0.0.0.0', port=5000, debug=True)

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
