from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

CORS(app)

# Database connection
app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/ordermanagement"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# Order Table to store order details
class Order(db.Model):
    __tablename__ = "Orders"
    
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    UserID = db.Column(db.Integer, nullable=False)  # Reference to user
    OrderDateTime = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    TotalAmount = db.Column(db.Float, nullable=False)
    OrderStatus = db.Column(db.String(50), default="pending")  # e.g., 'pending', 'completed'
    TransactionID = db.Column(db.String(255), nullable=False)

    def json(self):
        return {
            "OrderID": self.OrderID,
            "UserID": self.UserID,
            "OrderDateTime": self.OrderDateTime,
            "TotalAmount": self.TotalAmount,
            "OrderStatus": self.OrderStatus,
            "TransactionID": self.TransactionID
        }

# OrderItems Table to track specific items in an order
class OrderItem(db.Model):
    __tablename__ = "OrderItems"

    OrderItemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, db.ForeignKey("Orders.OrderID"), nullable=False)
    ItemID = db.Column(db.Integer, nullable=False)  # Reference to MenuItem or Product
    Quantity = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Float, nullable=False)
    StoreID = db.Column(db.Integer, nullable=False)  # Reference to Vendor

    def json(self):
        return {
            "OrderItemID": self.OrderItemID,
            "OrderID": self.OrderID,
            "ItemID": self.ItemID,
            "Quantity": self.Quantity,
            "Price": self.Price,
            "StoreID": self.StoreID
        }

# Health check endpoint
@app.route('/api/health')
def health_check():
    return jsonify({"message": "API is running!"})

# Place an order
@app.route('/orders', methods=['POST'])
def place_order():
    data = request.json
    user_id = data.get("UserID")
    total_amount = data.get("TotalAmount")
    transaction_id = data.get("TransactionID")
    
    if not user_id or not total_amount or not transaction_id:
        return jsonify({"message": "UserID, TotalAmount, and TransactionID are required"}), 400
    
    # Create new order
    new_order = Order(UserID=user_id, TotalAmount=total_amount, TransactionID=transaction_id)
    
    db.session.add(new_order)
    db.session.commit()

    return jsonify({"message": "Order placed successfully", "OrderID": new_order.OrderID}), 201

# Add items to an order
@app.route('/orders/<int:order_id>/items', methods=['POST'])
def add_order_item(order_id):
    data = request.json
    item_id = data.get("ItemID")
    quantity = data.get("Quantity")
    price = data.get("Price")
    store_id = data.get("StoreID")

    if not item_id or not quantity or not price or not store_id:
        return jsonify({"message": "ItemID, Quantity, Price, and StoreID are required"}), 400
    
    # Create new order item
    new_order_item = OrderItem(OrderID=order_id, ItemID=item_id, Quantity=quantity, Price=price, StoreID=store_id)

    db.session.add(new_order_item)
    db.session.commit()

    return jsonify({"message": "Order item added successfully", "OrderItemID": new_order_item.OrderItemID}), 201

# Get items of a specific order
@app.route('/orders/<int:order_id>/items', methods=['GET'])
def get_order_items(order_id):
    order_items = OrderItem.query.filter_by(OrderID=order_id).all()
    
    return jsonify([item.json() for item in order_items])

# Update order status
@app.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    order_status = data.get("OrderStatus")

    if not order_status:
        return jsonify({"message": "OrderStatus is required"}), 400
    
    order = Order.query.filter_by(OrderID=order_id).first()

    if not order:
        return jsonify({"message": "Order not found"}), 404

    order.OrderStatus = order_status
    db.session.commit()

    return jsonify({"message": "Order status updated successfully"})

# Get order status
@app.route('/orders/<int:order_id>/status', methods=['GET'])
def get_order_status(order_id):
    order = Order.query.filter_by(OrderID=order_id).first()
    
    if not order:
        return jsonify({"message": "Order not found"}), 404

    return jsonify(order.json())

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
