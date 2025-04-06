#commenting these lines out first to test grouporder.py
# import eventlet
# eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS, cross_origin
from sqlalchemy.dialects.postgresql import UUID
import uuid
# from flask_socketio import SocketIO, emit, join_room
from supabase import create_client
import os
import json
import logging
logging.basicConfig(level=logging.DEBUG)


from datetime import datetime
from flasgger import Swagger

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})


app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.ioskwqelrdcangizpzij:postgres@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

# Initialize Flasgger with OpenAPI specifications
app.config['SWAGGER'] = {
    'title': 'Group Order Microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'API for Retrieving, Creating and Deleting Group Order ',
}
swagger = Swagger(app)

class SharedCart(db.Model):
    __tablename__ = "shared_carts"

    CartID = db.Column(db.UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    Created_at = db.Column(db.DateTime, default=datetime.utcnow)
    VendorID = db.Column(db.Integer, nullable=False)
    Created_by = db.Column(db.UUID(as_uuid=True), nullable=False)

class CartItem(db.Model):
    __tablename__ = "cart_items"

    ID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    Added_at = db.Column(db.DateTime, default=datetime.utcnow)
    Cart_ID = db.Column(db.UUID(as_uuid=True), db.ForeignKey("shared_carts.CartID"), nullable=False)
    User_ID = db.Column(db.UUID(as_uuid=True), nullable=False)
    Item_ID = db.Column(db.Integer, nullable=False)
    Quantity = db.Column(db.Integer, nullable=False)

with app.app_context():
    db.create_all()


@app.route("/group-order/invite", methods=["POST"])
def create_group_order():
    """
    Create a new group order and return an invite link
    ---
    tags:
      - Group Order
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              vendorId:
                type: integer
              userId:
                type: string
            required:
              - vendorId
              - userId
    responses:
      200:
        description: Group order created
        content:
          application/json:
            schema:
              type: object
              properties:
                invite_link:
                  type: string
                cartId:
                  type: string
      400:
        description: Missing required fields
    """
    data = request.get_json()
    vendor_id = data.get("vendorId")
    created_by = data.get("userId")  # The user starting the group order

    if not vendor_id or not created_by:
        return jsonify({"error": "Missing required fields"}), 400

    shared_cart_id = uuid.uuid4()  # Generate unique cart ID
    invite_link = f"http://localhost:8080/group-order/join/{shared_cart_id}"

    new_cart = SharedCart(CartID=shared_cart_id, VendorID=vendor_id, Created_by=created_by)
    db.session.add(new_cart)
    db.session.commit()

    return jsonify({"invite_link": invite_link, "cartId": str(shared_cart_id)})

@app.route("/group-order/<cart_id>/vendor", methods=["GET"])
def get_vendor_from_cart(cart_id):
    """
    Get vendor ID from a shared cart
    ---
    tags:
      - Group Order
    parameters:
      - in: path
        name: cart_id
        required: true
        schema:
          type: string
    responses:
      200:
        description: Vendor ID retrieved
        content:
          application/json:
            schema:
              type: object
              properties:
                cartId:
                  type: string
                vendorId:
                  type: integer
      404:
        description: Shared cart not found
    """
    cart = SharedCart.query.filter_by(CartID=cart_id).first()
    if not cart:
        return jsonify({"error": "Shared cart not found"}), 404

    return jsonify({"cartId": cart_id, "vendorId": cart.VendorID})


@app.route("/group-order/join/<cart_id>", methods=["POST"])
def join_group_order(cart_id):
    """
    Join an existing group order
    ---
    tags:
      - Group Order
    parameters:
      - in: path
        name: cart_id
        required: true
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              userId:
                type: string
            required:
              - userId
    responses:
      200:
        description: Successfully joined group order
      400:
        description: User ID missing
      404:
        description: Cart not found
    """
    data = request.get_json()
    user_id = data.get("userId")  

    if not user_id:
        return jsonify({"error": "User ID is required"}), 400

    cart = SharedCart.query.filter_by(CartID=cart_id).first()
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    return jsonify({"message": "Successfully joined the group order", "cartId": cart_id})

@app.route("/group-order/<cart_id>/add-item", methods=["POST"])
def add_item_to_cart(cart_id):
    """
    Add item to shared cart
    ---
    tags:
      - Group Order
    parameters:
      - in: path
        name: cart_id
        required: true
        schema:
          type: string
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              userId:
                type: string
              itemId:
                type: integer
              quantity:
                type: integer
                default: 1
            required:
              - userId
              - itemId
    responses:
      200:
        description: Item added successfully
      400:
        description: Missing required fields
      404:
        description: Cart not found
    """
    data = request.get_json()
    user_id = data.get("userId")
    item_id = data.get("itemId")
    quantity = data.get("quantity", 1)

    if not user_id or not item_id:
        return jsonify({"error": "Missing required fields"}), 400

    cart = SharedCart.query.filter_by(CartID=cart_id).first()
    if not cart:
        return jsonify({"error": "Cart not found"}), 404

    new_item = CartItem(Cart_ID=cart_id, User_ID=user_id, Item_ID=item_id, Quantity=quantity)
    db.session.add(new_item)
    db.session.commit()

    return jsonify({"message": "Item added successfully", "cartId": cart_id})

@app.route("/group-order/<cart_id>", methods=["GET"])
def get_cart_items(cart_id):
    """
    Get all items in a shared cart
    ---
    tags:
      - Group Order
    parameters:
      - in: path
        name: cart_id
        required: true
        schema:
          type: string
    responses:
      200:
        description: List of cart items
        content:
          application/json:
            schema:
              type: object
              properties:
                CartID:
                  type: string
                Items:
                  type: array
                  items:
                    type: object
                    properties:
                      ID:
                        type: integer
                      Item_ID:
                        type: integer
                      User_ID:
                        type: string
                      Quantity:
                        type: integer
                      Added_at:
                        type: string
                        format: date-time
      500:
        description: Failed to fetch cart
    """
    
    try:
        cart_items = CartItem.query.filter_by(Cart_ID=cart_id).all()

        items = [
            {
                "ID": item.ID,
                "Item_ID": item.Item_ID,
                "User_ID": item.User_ID,
                "Quantity": item.Quantity,
                "Added_at": item.Added_at.isoformat() if item.Added_at else None
            }
            for item in cart_items
        ]

        return jsonify({
            "CartID": cart_id,
            "Items": items
        })
    except Exception as e:
        # Log the error if needed
        print(f"Error fetching cart {cart_id}: {str(e)}")
        return jsonify({"error": "Failed to fetch cart"}), 500
    
@app.route("/group-order/<cart_id>/remove-item/<item_id>", methods=["DELETE"])
def remove_item_from_cart(cart_id, item_id):
    """
    Remove a specific item from the cart
    ---
    tags:
      - Group Order
    parameters:
      - in: path
        name: cart_id
        required: true
        schema:
          type: string
      - in: path
        name: item_id
        required: true
        schema:
          type: integer
    responses:
      200:
        description: Item removed successfully
      404:
        description: Item not found in cart
    """
    item = CartItem.query.filter_by(Cart_ID=cart_id, ID=item_id).first()
    if not item:
        return jsonify({"error": "Item not found in cart"}), 404

    db.session.delete(item)
    db.session.commit()
    return jsonify({"message": "Item removed successfully", "cartId": cart_id})


@app.route("/group-order/<cart_id>/clear", methods=["DELETE"])
def clear_cart(cart_id):
    """
    Clear all items from the cart
    ---
    tags:
      - Group Order
    parameters:
      - in: path
        name: cart_id
        required: true
        schema:
          type: string
    responses:
      200:
        description: Cart cleared successfully
    """
    CartItem.query.filter_by(Cart_ID=cart_id).delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared successfully", "cartId": cart_id})



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)