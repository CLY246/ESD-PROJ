import os
import sys
import requests

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy import text
import traceback
from flasgger import Swagger


app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "http://localhost:8080"}}, supports_credentials=True)

# PostgreSQL Supabase Config
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.zwflnrnrvemjodtulkva:postgres@aws-0-ap-southeast-1.pooler.supabase.com:5432/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# Initialize Flasgger with OpenAPI specifications
app.config['SWAGGER'] = {
    'title': 'Order Management Microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'API to retrieve order queue and menu items',
}

swagger = Swagger(app)


# Define OutSystems API URL
OUTSYSTEMS_URL = "https://personal-aefq3pkb.outsystemscloud.com/OrderManagement/rest/OrderHistory/createHistory"


# -------------------- Models --------------------

class Order(db.Model):
    __tablename__ = "orders"
    OrderID = db.Column(db.Integer, primary_key=True, autoincrement=False, nullable=False)
    UserID = db.Column(db.String, nullable=False)
    OrderDateTime = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), nullable=False)
    TotalAmount = db.Column(db.Float, nullable=False)
    OrderStatus = db.Column(db.String(50), default="Completed")
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
    VendorID = db.Column(db.Integer, nullable=False)

    def json(self):
        return {
            "OrderItemID": self.OrderItemID,
            "OrderID": self.OrderID,
            "ItemID": self.ItemID,
            "Quantity": self.Quantity,
            "Price": self.Price,
            "VendorID": self.VendorID,
            "ItemName": self.ItemName,
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
    """
    Health check endpoint
    ---
    responses:
      200:
        description: API is running
    """
    return jsonify({"message": "OrderManagement API is running!"})



@app.route("/api/db-check")
def db_check():
    """
    db check endpoint
    ---
    responses:
      200:
        description: Supabase is running
        
        500: internal error
    """ 
    try:
        result = db.session.execute(text("SELECT 1"))
        return jsonify({"status": "Connected to Supabase DB ✅"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    


@app.route('/orders/<int:order_id>/history', methods=['POST'])
def create_order_history(order_id):
    """
    Add an item to an existing order.

    Adds a new item to the order with the given order_id. The item details 
    (ItemID, Quantity, Price, VendorID) are provided in the request body.

    ---
    tags:
      - Orders
    parameters:
      - in: path
        name: order_id
        type: integer
        required: true
        description: The ID of the order to add an item to.
      - in: body
        name: item_details
        required: true
        schema:
          type: object
          properties:
            ItemID:
              type: integer
              description: The ID of the item to add.
            Quantity:
              type: integer
              description: The quantity of the item.
            Price:
              type: number
              format: float
              description: The price of the item.
            VendorID:
              type: integer
              description: The ID of the vendor selling the item.
    responses:
      201:
        description: Item added successfully.
        schema:
          type: object
          properties:
            message:
              type: string
            OrderItemID:
              type: integer
      400:
        description: Missing item details.
      500:
        description: Internal server error.
    """
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
    """
    Retrieve a list of all orders.

    This endpoint returns all orders from the database in JSON format. It fetches 
    all orders and returns them in a list, with each order represented by its 
    respective JSON representation.

    ---
    tags:
      - Orders
    responses:
      200:
        description: A list of all orders in JSON format.
        schema:
          type: array
          items:
            type: object
            properties:
              OrderID:
                type: integer
                description: The ID of the order.
              OrderStatus:
                type: string
                description: The status of the order (e.g., 'pending', 'shipped').
              CreatedAt:
                type: string
                format: date-time
                description: The timestamp when the order was created.
              UpdatedAt:
                type: string
                format: date-time
                description: The timestamp when the order was last updated.
      500:
        description: Internal server error when retrieving the orders.
    """
    orders = Order.query.all()
    return jsonify([order.json() for order in orders])



@app.route('/orders', methods=['POST'])
def place_order():
    """
    Place a new order.

    ---
    tags:
      - Orders
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              UserID:
                type: string
              OrderID:
                type: integer
              TotalAmount:
                type: number
              TransactionID:
                type: string
              VendorID:
                type: string
              VendorName:
                type: string
              Cuisine:
                type: string
              ImageURL:
                type: string
              Items:
                type: array
                items:
                  type: object
                  properties:
                    ItemID:
                      type: string
                    ItemName:
                      type: string
                    Quantity:
                      type: integer
                    Price:
                      type: number
                    VendorID:
                      type: string
    responses:
      201:
        description: Order and items saved
      400:
        description: Missing data
      500:
        description: Failed to save order
    """
    
    try:
        data = request.json
        user_id = data.get("UserID")
        order_id = data.get("OrderID")
        total_amount = data.get("TotalAmount")
        transaction_id = data.get("TransactionID")
        vendor_id = data.get("VendorID")

        if not user_id or not total_amount or not transaction_id:
            return jsonify({"message": "Missing data"}), 400

        # Save main order
        new_order = Order(
            OrderID=order_id,
            UserID=user_id,
            TotalAmount=total_amount,
            TransactionID=transaction_id,
            VendorID=vendor_id,
            VendorName=data.get("VendorName"),
            Cuisine=data.get("Cuisine"),
            ImageURL=data.get("ImageURL"),
            OrderStatus="Completed"
        )
        db.session.add(new_order)

        # Save order items
        items = data.get("Items", [])
        print("Incoming Items:", items)
        for item in items:
            order_item = OrderItem(
                OrderID=order_id,
                ItemID=item.get("ItemID"),
                ItemName=item.get("ItemName", "Unnamed Item"),
                Quantity=item.get("Quantity", 1),
                Price=item.get("Price", 0.0),
                VendorID=item.get("VendorID")
            )
            db.session.add(order_item)

        db.session.commit()

        return jsonify({
            "code": 201,
            "message": " Order and items saved"
        }), 201

    except Exception as e:
        db.session.rollback()
        import traceback
        traceback.print_exc()
        return jsonify({
            "code": 500,
            "message": " Failed to save order",
            "error": str(e)
        }), 500



@app.route('/orders/<int:order_id>/items', methods=['GET'])
def get_order_items_by_order_id(order_id):
    """
    Get all items in an order by OrderID.

    ---
    tags:
      - Order Items
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: List of order items
      404:
        description: No items found
    """
    items = OrderItem.query.filter_by(OrderID=order_id).all()
    if not items:
        return jsonify({"message": "No items found for this OrderID"}), 404

    return jsonify([item.json() for item in items]), 200


@app.route('/orders/<int:order_id>/items', methods=['POST'])

def add_order_item(order_id):
    """
    Add an item to an existing order.

    ---
    tags:
      - Order Items
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              ItemID:
                type: string
              Quantity:
                type: integer
              Price:
                type: number
              VendorID:
                type: string
    responses:
      201:
        description: Item added
      400:
        description: Missing item details
    """
    
    data = request.json
    item_id = data.get("ItemID")
    quantity = data.get("Quantity")
    price = data.get("Price")
    vendor_id = data.get("VendorID")

    if not item_id or not quantity or not price or not vendor_id:
        return jsonify({"message": "Missing item details"}), 400

    new_item = OrderItem(OrderID=order_id, ItemID=item_id, Quantity=quantity, Price=price, VendorID=vendor_id)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"message": "Item added", "OrderItemID": new_item.OrderItemID}), 201

@app.route('/orders/<int:order_id>/status', methods=['PUT'])
def update_order_status(order_id):
    """
    Update the status of an order.

    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              OrderStatus:
                type: string
    responses:
      200:
        description: Order status updated
      404:
        description: Order not found
    """
    data = request.json
    status = data.get("OrderStatus")

    order = Order.query.filter_by(OrderID=order_id).first()
    if not order:
        return jsonify({"message": "Order not found"}), 404

    order.OrderStatus = status
    db.session.commit()

    return jsonify({"message": "Order status updated"}),200

@app.route('/orders/<int:order_id>', methods=['GET'])
def get_order(order_id):
    """
    Get order details by OrderID.

    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Order details
      404:
        description: Order not found
      500:
        description: Internal server error
    """
    try:
        print(f"Looking for OrderID {order_id}...")
        order = Order.query.filter_by(OrderID=order_id).first()
        if not order:
            return jsonify({"message": "Order not found"}), 404
        print("Found:", order.json())
        return jsonify(order.json()), 200
    except Exception as e:
        print("ERROR while fetching order:", e)
        return jsonify({"error": str(e)}), 500




@app.route('/orders/user/<user_id>', methods=['GET'])
def get_orders_by_user(user_id):
    """
    Get all orders placed by a user.

    ---
    tags:
      - Orders
    parameters:
      - name: user_id
        in: path
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of orders by user
    """
    orders = Order.query.filter_by(UserID=str(user_id)).all()
    return jsonify([order.json() for order in orders])


@app.route('/orders/<int:order_id>/full', methods=['GET'])
def get_full_order(order_id):
    """
    Get full order details including items.

    ---
    tags:
      - Orders
    parameters:
      - name: order_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Full order with items
      404:
        description: Order not found
    """
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
    """
    Get all order queue entries.

    ---
    tags:
      - Order Queue
    responses:
      200:
        description: All queue entries
    """
   
    queue = OrderQueue.query.all()
    return jsonify({"queue": [q.json() for q in queue]})

@app.route('/orderqueue', methods=["POST"])
def add_to_queue():
    """
    Add a new entry to the order queue.

    ---
    tags:
      - Order Queue
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              OrderID:
                type: integer
              EstimatedWaitTime:
                type: integer
    responses:
      201:
        description: Added to queue
      400:
        description: Missing queue data
    """
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
    """
    Update the status of a queue entry.

    ---
    tags:
      - Order Queue
    parameters:
      - name: queue_id
        in: path
        required: true
        schema:
          type: integer
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              Status:
                type: string
    responses:
      200:
        description: Queue updated
      404:
        description: Queue entry not found
    """
    data = request.json
    status = data.get("Status")

    queue_entry = OrderQueue.query.get(queue_id)
    if not queue_entry:
        return jsonify({"message": "Queue entry not found"}), 404

    
    queue_entry.Status = status
    db.session.commit()
    return jsonify({"message": "Queue updated"}),200
    # else:
    #     return jsonify({"message": "Status is required"}), 400
        

@app.route('/orderqueue/<int:queue_id>', methods=["DELETE"])
def delete_queue(queue_id):
    """
    Delete a queue entry.

    ---
    tags:
      - Order Queue
    parameters:
      - name: queue_id
        in: path
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Queue entry deleted
      404:
        description: Not found
    """
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





