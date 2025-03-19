from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
import os
import stripe

app = Flask(__name__)
# CORS(app)
CORS(app, resources={r"/payments/*": {"origins": "*"}})


app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:3306/payment"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Transaction(db.Model):
    __tablename__ = 'Transactions'  

    TransactionID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, nullable=False)
    Amount = db.Column(db.Numeric(10, 2), nullable=False)
    PaymentMethod = db.Column(db.String(50))
    PaymentStatus = db.Column(db.String(50), default='Pending')  # Ensures payments are validated first
    TransactionDate = db.Column(db.DateTime, server_default=db.func.current_timestamp())  # Use DateTime

    def json(self):
        return {
            "TransactionID": self.TransactionID,
            "OrderID": self.OrderID,
            "Amount": float(self.Amount),
            "PaymentMethod": self.PaymentMethod,
            "PaymentStatus": self.PaymentStatus,
            "TransactionDate": self.TransactionDate
        }

@app.route('/api/health')
def health_check():
    return jsonify({"message": "Payment API is running!"})




stripe.api_key = "sk_test_51R2Nh0Bz8bLJBV2onRtvizH4yVf4xcufKaJTXshVg1g42nDYe1M9hGnDeJsM4IWMWCBq1GNEQs0rZ53ue6hA08Xe00IXHYXH0R"

@app.route("/payments", methods=["POST"])
def process_payment():
    data = request.json
    order_id = data.get("OrderID")
    amount = data.get("Amount")

    if not order_id or not amount:
        return jsonify({"message": "OrderID and Amount are required"}), 400

    # Convert amount to cents for Stripe
    amount_in_cents = int(float(amount) * 100)

    try:
        # Create Stripe Checkout Session
        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "sgd",
                        "product_data": {"name": "Restaurant Order"},
                        "unit_amount": amount_in_cents,
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:8080/success",
            cancel_url="http://localhost:8080/cancel",
        )

        # Save transaction to DB
        new_transaction = Transaction(
            OrderID=order_id,
            Amount=amount,
            PaymentMethod="Stripe",
            PaymentStatus="Pending"
        )

        db.session.add(new_transaction)
        db.session.commit()

        return jsonify({"message": "Payment initiated successfully", "session_url": session.url, "transaction": new_transaction.json()}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# @app.route("/payments", methods=["POST"])
# def process_payment():
#     data = request.json
#     order_id = data.get("OrderID")
#     amount = data.get("Amount")
#     payment_method = data.get("PaymentMethod")

#     if not order_id or not amount or not payment_method:
#         return jsonify({"message": "OrderID, Amount, and PaymentMethod are required"}), 400

#     new_transaction = Transaction(
#         OrderID=order_id,
#         Amount=amount,
#         PaymentMethod=payment_method,
#         PaymentStatus='Pending'  # Initially Pending
#     )

#     db.session.add(new_transaction)
#     db.session.commit()

#     return jsonify({"message": "Payment initiated successfully", "transaction": new_transaction.json()}), 201

@app.route("/payments/<int:order_id>", methods=["GET"])
def get_payment_status(order_id):
    transaction = Transaction.query.filter_by(OrderID=order_id).first()
    if not transaction:
        return jsonify({"message": "Transaction not found"}), 404
    return jsonify(transaction.json())

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=os.getenv("FLASK_DEBUG", "False") == "True")