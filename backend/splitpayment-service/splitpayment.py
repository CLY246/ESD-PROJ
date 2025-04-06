from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from datetime import datetime
from flasgger import Swagger

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:3306/splitpayment"
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# Initialize Flasgger with OpenAPI specifications
app.config['SWAGGER'] = {
    'title': 'Split Payment Microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'API for split payments',
}

swagger = Swagger(app)

class SplitPayment(db.Model):
    __tablename__ = 'SplitPayments'
    SplitPaymentID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, nullable=False)
    PayerUserID = db.Column(db.Integer, nullable=False)
    Amount = db.Column(db.Numeric(10, 2), nullable=False)
    TransactionID = db.Column(db.Integer, nullable=True)
    Status = db.Column(db.String(50), default='Pending')

    def json(self):
        return {
            "SplitPaymentID": self.SplitPaymentID,
            "OrderID": self.OrderID,
            "PayerUserID": self.PayerUserID,
            "Amount": float(self.Amount),
            "TransactionID": self.TransactionID,
            "Status": self.Status
        }

@app.route('/api/health')
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: API is running
    """
    return jsonify({"message": "Split Payment API is running!"})

@app.route("/splitpayments", methods=["POST"])
def create_split_payment():
    """
    Create a new split payment record
    ---
    tags:
      - Split Payments
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - OrderID
              - PayerUserID
              - Amount
            properties:
              OrderID:
                type: integer
              PayerUserID:
                type: integer
              Amount:
                type: number
                format: float
              SplitPaymentID:
                type: integer
              TransactionID:
                type: integer
            
    responses:
      201:
        description: Split payment created
        content:
          application/json:
            example:
              message: "Split payment created successfully"
              split_payment:
                SplitPaymentID: 1
                OrderID: 101
                PayerUserID: 5
                Amount: 10.5
                TransactionID: 123456
                Status: Pending
      400:
        description: Missing required fields
    """
    data = request.json
    order_id = data.get("OrderID")
    payer_user_id = data.get("PayerUserID")
    amount = data.get("Amount")
    transaction_id = data.get("TransactionID")

    if not order_id or not payer_user_id or not amount:
        return jsonify({"message": "OrderID, PayerUserID, and Amount are required"}), 400

    new_split_payment = SplitPayment(
        OrderID=order_id,
        PayerUserID=payer_user_id,
        Amount=amount,
        TransactionID=transaction_id,
        Status='Pending'
    )

    db.session.add(new_split_payment)
    db.session.commit()

    return jsonify({"message": "Split payment created successfully", "split_payment": new_split_payment.json()}), 201

@app.route("/splitpayments/order/<int:order_id>", methods=["GET"])
def get_split_payments_by_order(order_id):
    """
    Retrieve split payments by order ID
    ---
    tags:
      - Split Payments
    parameters:
      - name: order_id
        in: path
        type: integer
        required: true
        description: The order ID to filter split payments
    responses:
      200:
        description: List of split payments for the order
        content:
          application/json:
            example:
              - SplitPaymentID: 1
                OrderID: 101
                PayerUserID: 5
                Amount: 10.5
                TransactionID: 123456
                Status: Pending
    """
    split_payments = SplitPayment.query.filter_by(OrderID=order_id).all()
    return jsonify([sp.json() for sp in split_payments])

@app.route("/splitpayments/<int:split_payment_id>/status", methods=["PUT"])
def update_split_payment_status(split_payment_id):
    """
    Update the status of a split payment
    ---
    tags:
      - Split Payments
    parameters:
      - name: split_payment_id
        in: path
        type: integer
        required: true
        description: ID of the split payment to update
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            required:
              - Status
            properties:
              Status:
                type: string
                example: "Paid"
    responses:
      200:
        description: Status updated successfully
        content:
          application/json:
            example:
              message: "Split payment status updated"
      400:
        description: Missing Status field
      404:
        description: Split payment not found
    """
    data = request.json
    status = data.get("Status")
    if not status:
        return jsonify({"message": "Status is required"}), 400
    
    split_payment = SplitPayment.query.get(split_payment_id)
    if not split_payment:
        return jsonify({"message": "Split payment not found"}), 404
    
    split_payment.Status = status
    db.session.commit()
    return jsonify({"message": "Split payment status updated"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
