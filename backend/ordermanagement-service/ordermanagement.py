import os
import sys
import requests

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text



app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}, supports_credentials=True)

# PostgreSQL Supabase Config
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.zwflnrnrvemjodtulkva:postgres@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


# Define OutSystems API URL
OUTSYSTEMS_URL = "https://personal-aefq3pkb.outsystemscloud.com/OrderManagement/rest/OrderHistory/createHistory"


# -------------------- Models --------------------

class Order(db.Model):
    __tablename__ = "orders"
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=False)
    UserID = db.Column(db.String, nullable=False)
    OrderDateTime = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    TotalAmount = db.Column(db.Float, nullable=False)
    OrderStatus = db.Column(db.String(50), default="pending")
    TransactionID = db.Column(db.String(255), nullable=False)

    VendorID = db.Column(db.Integer, nullable=True)
    VendorName = db.Column(db.String(255))
    Cuisine = db.Column(db.String(255))
    ImageURL = db.Column(db.String(2048))

    def json(self):
        return {
            "OrderID": self.OrderID,
            "UserID": self.UserID,
            "OrderDateTime": self.OrderDateTime,
            "TotalAmount": self.TotalAmount,
            "OrderStatus": self.OrderStatus,
            "TransactionID": self.TransactionID,
            "VendorID": self.VendorID,
            "VendorName": self.VendorName,
            "Cuisine": self.Cuisine,
            "ImageURL": self.ImageURL
        }

class OrderItem(db.Model):
    __tablename__ = "order_items"
    OrderItemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, db.ForeignKey("orders.OrderID"), nullable=False)
    ItemID = db.Column(db.Integer, nullable=False)
    ItemName = db.Column(db.String(255)) 
    Quantity = db.Column(db.Integer, nullable=False)
    Price = db.Column(db.Float, nullable=False)
    StoreID = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            "OrderItemID": self.OrderItemID,
            "OrderID": self.OrderID,
            "ItemID": self.ItemID,
            "ItemName": self.ItemName,
            "Quantity": self.Quantity,
            "Price": self.Price,
            "StoreID": self.StoreID
        }


class OrderQueue(db.Model):
    __tablename__ = 'order_queue'
    QueueID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    OrderID = db.Column(db.Integer, db.ForeignKey("orders.OrderID"), nullable=False)
    Timestamp = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp())
    EstimatedWaitTime = db.Column(db.Integer, nullable=False)
    Status = db.Column(db.Enum('Pending', 'In Progress', 'Completed', name='order_status_enum'), default='Completed')

    def json(self):
        return {
            "QueueID": self.QueueID,
            "OrderID": self.OrderID,
            "Timestamp": self.Timestamp,
            "EstimatedWaitTime": self.EstimatedWaitTime,
            "Status": self.Status
        }

# -------------------- Routes --------------------

@app.route('/api/health')
def health_check():
    return jsonify({"message": "OrderManagement API is running!"})



@app.route("/api/db-check")
def db_check():
    try:
        result = db.session.execute(text("SELECT 1"))
        return jsonify({"status": "Connected to Supabase DB ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route('/orders/<int:order_id>/history', methods=['POST'])
def create_order_history(order_id):
    """Send order history to OutSystems"""
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404

    order_data = {
        "OrderID": order.OrderID,
        "UserID": order.UserID,
        "OrderDateTime": str(order.OrderDateTime),
        "TotalAmount": order.TotalAmount,
        "OrderStatus": order.OrderStatus,
        "TransactionID": order.TransactionID,
        "VendorID": order.VendorID,
        "VendorName": order.VendorName,
        "Cuisine": order.Cuisine,
        "ImageURL": order.ImageURL
    }

    try:
        response = requests.post(OUTSYSTEMS_URL, json=order_data)
        response.raise_for_status()  # Raise an error if the request fails
        return jsonify({"message": "Order history sent to OutSystems", "response": response.json()}), response.status_code
    except requests.exceptions.RequestException as e:
        return jsonify({"error": str(e)}), 500
    


    

@app.route("/orders", methods=["GET"])
def get_all_orders():
    orders = Order.query.all()
    return jsonify([order.json() for order in orders])



@app.route('/orders', methods=['POST'])
def place_order():
    data = request.json
    user_id = data.get("UserID")
    total_amount = data.get("TotalAmount")
    transaction_id = data.get("TransactionID")

    if not user_id or not total_amount or not transaction_id:
        return jsonify({"message": "Missing data"}), 400

    # Step 1: Create Order
    new_order = Order(
        OrderID=data.get("OrderID"),
        UserID=user_id,
        TotalAmount=total_amount,
        TransactionID=transaction_id,
        VendorID=data.get("VendorID"),
        VendorName=data.get("VendorName"),
        Cuisine=data.get("Cuisine"),
        ImageURL=data.get("ImageURL")
    )

    db.session.add(new_order)
    db.session.commit()  # Commit once to get new_order.OrderID

    # Step 2: Add Items if present
    for item in data.get("Items", []):
        order_item = OrderItem(
            OrderID=new_order.OrderID,
            ItemID=item["ItemID"],
            ItemName=item.get("ItemName"),  # ✅ use .get() in case it's optional
            Quantity=item["Quantity"],
            Price=item["Price"],
            StoreID=data.get("VendorID")
        )
        db.session.add(order_item)

    db.session.commit()

    return jsonify({"message": "Order placed", "OrderID": new_order.OrderID}), 201



@app.route('/orders/<int:order_id>/items', methods=['POST'])
def add_order_item(order_id):
    data = request.json
    item_id = data.get("ItemID")
    quantity = data.get("Quantity")
    price = data.get("Price")
    store_id = data.get("StoreID")

    if not item_id or not quantity or not price or not store_id:
        return jsonify({"message": "Missing item details"}), 400

    new_item = OrderItem(OrderID=order_id, ItemID=item_id, Quantity=quantity, Price=price, StoreID=store_id)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"message": "Item added", "OrderItemID": new_item.OrderItemID}), 201

@app.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    data = request.json
    status = data.get("OrderStatus")

    order = Order.query.filter_by(OrderID=order_id).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404

    order.OrderStatus = status
    db.session.commit()

    return jsonify({"message": "Order status updated"})

# @app.route('/orders/<int:order_id>', methods=['GET'])
# def get_order(order_id):
#     order = Order.query.filter_by(OrderID=order_id).first()
#     if not order:
#         return jsonify({"message": "Order not found"}), 404
#     return jsonify(order.json()), 200


@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    try:
        print(f"Looking for OrderID {order_id}...")
        order = Order.query.filter_by(OrderID=order_id).first()
        if not order:
            return jsonify({"message": "Order not found"}), 404
        print("Found:", order.json())
        return jsonify(order.json()), 200
    except Exception as e:
        print("❌ ERROR while fetching order:", e)
        return jsonify({"error": str(e)}), 500




@app.route('/orders/user/<user_id>', methods=['GET'])
def get_orders_by_user(user_id):
    orders = Order.query.filter_by(UserID=str(user_id)).all()
    return jsonify([order.json() for order in orders])


@app.route('/orders/<int:order_id>/full', methods=['GET'])
def get_full_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"message": "Order not found"}), 404
    items = OrderItem.query.filter_by(OrderID=order_id).all()
    return jsonify({
        "order": order.json(),
        "items": [item.json() for item in items]
    })

@app.route('/orderqueue', methods=["GET"])
def get_queue():
    queue = OrderQueue.query.all()
    return jsonify({"queue": [q.json() for q in queue]})

@app.route('/orderqueue', methods=["POST"])
def add_to_queue():
    data = request.json
    order_id = data.get("OrderID")
    est_time = data.get("EstimatedWaitTime")

    if not order_id or not est_time:
        return jsonify({"message": "Missing queue data"}), 400

    entry = OrderQueue(OrderID=order_id, EstimatedWaitTime=est_time)
    db.session.add(entry)
    db.session.commit()

    return jsonify({"message": "Added to queue", "QueueID": entry.QueueID}), 201

@app.route('/orderqueue/<int:queue_id>', methods=["PUT"])
def update_queue(queue_id):
    data = request.json
    status = data.get("Status")

    queue_entry = OrderQueue.query.get(queue_id)
    if not queue_entry:
        return jsonify({"message": "Queue entry not found"}), 404

    queue_entry.Status = status
    db.session.commit()

    return jsonify({"message": "Queue updated"})

@app.route('/orderqueue/<int:queue_id>', methods=["DELETE"])
def delete_queue(queue_id):
    entry = OrderQueue.query.get(queue_id)
    if not entry:
        return jsonify({"message": "Not found"}), 404

    db.session.delete(entry)
    db.session.commit()
    return jsonify({"message": "Deleted"})



# -------------------- Create tables if not exist --------------------
with app.app_context():
    db.create_all()

# -------------------- App start --------------------
if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)





