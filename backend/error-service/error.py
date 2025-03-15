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






import os
import json
import pika
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import threading
from rabbitmq import amqp_setup


# Flask App Setup
app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/error"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class ErrorLog(db.Model):
    __tablename__ = 'ErrorLog'
    ErrorID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    ServiceName = db.Column(db.String(100), nullable=False)
    OrderID = db.Column(db.Integer, nullable=True)
    ErrorDetails = db.Column(db.Text, nullable=False)
    Severity = db.Column(db.String(20), nullable=False)

    def json(self):
        return {
            "ErrorID": self.ErrorID,
            "Timestamp": self.Timestamp,
            "ServiceName": self.ServiceName,
            "OrderID": self.OrderID,
            "ErrorDetails": self.ErrorDetails,
            "Severity": self.Severity
        }

@app.route('/api/health')
def health_check():
    return jsonify({"message": "Error API is running!"})

@app.route("/errors", methods=["POST"])
def log_error():
    data = request.json
    service_name = data.get("ServiceName")
    order_id = data.get("OrderID")
    error_details = data.get("ErrorDetails")
    severity = data.get("Severity")

    if not service_name or not error_details or not severity:
        return jsonify({"message": "ServiceName, ErrorDetails, and Severity are required"}), 400

    new_error = ErrorLog(
        ServiceName=service_name,
        OrderID=order_id,
        ErrorDetails=error_details,
        Severity=severity
    )

    db.session.add(new_error)
    db.session.commit()

    return jsonify({"message": "Error logged successfully", "error": new_error.json()}), 201

@app.route("/errors", methods=["GET"])
def get_errors():
    errors = ErrorLog.query.all()
    return jsonify([e.json() for e in errors])

@app.route("/errors/<int:error_id>", methods=["GET"])
def get_error_by_id(error_id):
    error = ErrorLog.query.get(error_id)
    if not error:
        return jsonify({"message": "Error not found"}), 404
    return jsonify(error.json())

# AMQP Consumer Setup
RABBIT_HOST = "rabbitmq"
RABBIT_PORT = 5672
EXCHANGE_NAME = "order_topic"
QUEUE_NAME = "Error"

def callback(channel, method, properties, body):
    """ Callback function to process incoming messages from RabbitMQ """
    try:
        error_data = json.loads(body)
        print(f"📩 Received Error Message: {error_data}")

        # Save to database
        new_error = ErrorLog(
            ServiceName=error_data.get("ServiceName", "Unknown"),
            OrderID=error_data.get("OrderID"),
            ErrorDetails=error_data.get("ErrorDetails", "No details"),
            Severity=error_data.get("Severity", "Low"),
        )

        db.session.add(new_error)
        db.session.commit()

        print("✅ Error logged successfully in DB")
    except Exception as e:
        print(f"❌ Error processing message: {e}")
        print(f"Message received: {body}")

def consume_errors():
    """ AMQP Consumer to continuously listen for error messages """
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
    threading.Thread(target=consume_errors, daemon=True).start()

    # Start Flask API
    print("🚀 Starting Flask Error Service...")
    app.run(host='0.0.0.0', port=5000, debug=True)
