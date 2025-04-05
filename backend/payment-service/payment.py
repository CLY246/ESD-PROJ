from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import uuid
import stripe
from sqlalchemy import BigInteger
from sqlalchemy import text
from flasgger import Swagger


app = Flask(__name__)
# CORS(app)
# CORS(app, resources={r"/payments/*": {"origins": "*"}})
CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)

app.config["SQLALCHEMY_DATABASE_URI"] ="postgresql://postgres.ddrfpayfchyuvqifbatf:Cloud1064!@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# Initialize Flasgger with OpenAPI specifications
app.config['SWAGGER'] = {
    'title': 'Payment Microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'API to retrieve order queue and menu items',
}

swagger = Swagger(app)

class Transaction(db.Model):
    __tablename__ = 'Transactions'  

    TransactionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    OrderID = db.Column(db.Integer, nullable=False)
    Amount = db.Column(db.Numeric(10, 2), nullable=False)
    PaymentMethod = db.Column(db.String(50))
    PaymentStatus = db.Column(db.String(50), default='Pending')  # Ensures payments are validated first
    # TransactionDate = db.Column(db.DateTime, server_default=db.func.current_timestamp())  # Use DateTime

    def json(self):
        return {
            "TransactionID": self.TransactionID,
            "OrderID": self.OrderID,
            "Amount": float(self.Amount),
            "PaymentMethod": self.PaymentMethod,
            "PaymentStatus": self.PaymentStatus,
            # "TransactionDate": self.TransactionDate
        }
with app.app_context():
    db.create_all()



@app.route('/api/health')
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: API is running
    """
    return jsonify({"message": "Payment API is running!"})


@app.route("/api/db-check")
def db_check():
    """
    db check endpoint
    ---
    responses:
      200:
        description: Database is connected
        
        500: internal error
    """
    try:
        db.session.execute(text("SELECT 1"))
        return jsonify({"status": "Connected to DB ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route("/next-order-id", methods=["GET"])
def get_next_order_id():
    """
Get Next Order ID
---
tags:
  - Order
description: Retrieve the next available Order ID
responses:
  200:
    description: Successfully retrieved
    schema:
      type: object
      properties:
        OrderID:
          type: integer
          example: 10
  500:
    description: Server error
"""
    try:
        latest_transaction = db.session.query(Transaction).order_by(Transaction.OrderID.desc()).first()
        next_order_id = (latest_transaction.OrderID + 1) if latest_transaction else 1
        return jsonify({"OrderID": next_order_id})
    except Exception as e:
        return jsonify({"error": str(e)}), 500




stripe.api_key = "sk_test_51R2Nh0Bz8bLJBV2onRtvizH4yVf4xcufKaJTXshVg1g42nDYe1M9hGnDeJsM4IWMWCBq1GNEQs0rZ53ue6hA08Xe00IXHYXH0R"
endpoint_secret = os.getenv("whsec_119db3c043f993227277345c6a1fbc9d49d1898b2e8bd903181a0f326bcccd9a")


@app.route("/payments", methods=["GET"])
def get_all_transactions():
    """
Get All Transactions
---
tags:
  - Payments
description: Retrieve all transactions from the database
responses:
  200:
    description: A list of transactions
    schema:
      type: array
      items:
        type: object
        properties:
          TransactionID:
            type: integer
            example: 1
          OrderID:
            type: integer
            example: 1
          Amount:
            type: number
            format: float
            example: 20.5
          PaymentMethod:
            type: string
            example: Stripe
          PaymentStatus:
            type: string
            example: Success
"""

    transactions = Transaction.query.all()
    return jsonify([t.json() for t in transactions])


@app.route("/payments", methods=["POST"])
def process_payment():
    """
Process a New Payment
---
tags:
  - Payments
description: Initiates a Stripe Checkout session and records the payment
parameters:
  - in: body
    name: body
    required: true
    schema:
      type: object
      properties:
        Amount:
          type: number
          example: 10.0
responses:
  201:
    description: Payment session created
    schema:
      type: object
      properties:
        message:
          type: string
          example: Payment initiated successfully
        paymentUrl:
          type: string
          example: https://checkout.stripe.com/...
        transaction:
          type: object
          properties:
            TransactionID:
              type: integer
              example: 1
            OrderID:
              type: integer
              example: 1
            Amount:
              type: number
              example: 10.0
            PaymentMethod:
              type: string
              example: Stripe
            PaymentStatus:
              type: string
              example: Pending
  400:
    description: Invalid input
  500:
    description: Internal server error
"""

    data = request.json
    amount = data.get("Amount")

    if not amount:
        return jsonify({"message": "Amount is required"}), 400

    try:
        # 1: Generate new OrderID automatically
        latest_transaction = db.session.query(Transaction).order_by(Transaction.OrderID.desc()).first()
        order_id = (latest_transaction.OrderID + 1) if latest_transaction else 1
        print(f"Generated OrderID: {order_id}")

        # 2: Convert amount to cents for Stripe
        amount_in_cents = int(float(amount) * 100)


        # 3: Create Stripe session
        session = stripe.checkout.Session.create(
        payment_method_types=["card"],
        line_items=[{
            "price_data": {
            "currency": "sgd",
            "product_data": {"name": "Restaurant Order"},
            "unit_amount": amount_in_cents,
            },
            "quantity": 1,
        }],
        mode="payment",
        success_url=f"http://localhost:8080/success?order_id={order_id}",
        cancel_url="http://localhost:8080/cancel",
        metadata={"order_id": str(order_id)}
)       
     
        # 4: Save transaction to DB
        new_transaction = Transaction(
            OrderID=order_id,
            Amount=amount,
            PaymentMethod="Stripe",
            PaymentStatus="Pending"
        )

        db.session.add(new_transaction)
        db.session.commit()

        # : Return Stripe session URL
        return jsonify({
            "message": "Payment initiated successfully",
            "paymentUrl": session.url,
            "transaction": new_transaction.json()
        }), 201

    except Exception as e:
        return jsonify({
            "error": str(e),
            "message": "Payment processing failed",
            "transaction": None
        }), 500


@app.route('/webhook', methods=['POST'])
def stripe_webhook():
    """
Stripe Webhook Listener
---
tags:
  - Stripe
description: Handles Stripe webhook events for session completion
consumes:
  - application/json
produces:
  - application/json
responses:
  200:
    description: Webhook received
  400:
    description: Invalid payload or signature
"""
    payload = request.data
    sig_header = request.headers.get('stripe-signature')

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except stripe.error.SignatureVerificationError:
        return jsonify({"error": "Invalid signature"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 400

    # ✅ Handle the event
    if event["type"] == "checkout.session.completed":
        session = event["data"]["object"]
        print("✅ Payment success:", session)

        # Update your DB to mark transaction as "Success"
        order_id = session.get("metadata", {}).get("order_id")  # if using metadata
        if order_id:
            transaction = Transaction.query.filter_by(OrderID=order_id).first()
            if transaction:
                transaction.PaymentStatus = "Success"
                db.session.commit()

    return jsonify({"status": "received"}), 200



@app.route("/payments/transaction/<int:transaction_id>", methods=["GET"])
def get_payment_by_transaction_id(transaction_id):
    """
    Get Payment by Transaction ID
    ---
    tags:
      - Payments
    parameters:
      - name: transaction_id
        in: path
        type: integer
        required: true
        description: ID of the transaction to retrieve
    responses:
      200:
        description: Transaction retrieved successfully
        schema:
          type: object
          properties:
            TransactionID:
              type: integer
            OrderID:
              type: integer
            Amount:
              type: number
              format: float
            PaymentMethod:
              type: string
            PaymentStatus:
              type: string
      404:
        description: Transaction not found
    """
    
    transaction = Transaction.query.filter_by(TransactionID=transaction_id).first()
    if not transaction:
        return jsonify({"message": "Transaction not found"}), 404
    return jsonify(transaction.json()), 200


@app.route("/payments/<int:order_id>", methods=["GET"])
def get_payment_status(order_id):
    """
    Get Payment by Order ID
    ---
    tags:
    - Payments
    parameters:
    - in: path
      name: order_id
      required: true
      schema:
      type: integer
    responses:
        200:
          description: Transaction found
        404:
          description: Transaction not found
    """
    transaction = Transaction.query.filter_by(OrderID=order_id).first()
    if not transaction:
        return jsonify({"message": "Transaction not found"}), 404
    return jsonify(transaction.json())



# -------------------- Create tables if not exist --------------------
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv("FLASK_DEBUG", "False") == "True")




