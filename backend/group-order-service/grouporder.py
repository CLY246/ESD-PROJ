import eventlet
eventlet.monkey_patch()

from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from sqlalchemy.dialects.postgresql import UUID
import uuid
from flask_socketio import SocketIO, emit, join_room
from supabase import create_client
import os
import json


from datetime import datetime

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*", async_mode="eventlet")

CORS(app)  

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.ioskwqelrdcangizpzij:postgres@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

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


@socketio.on("join_cart")
def join_cart(data):
    cart_id = data.get("cartId")
    join_room(cart_id)  
    emit("cart_message", {"message": f"User joined cart {cart_id}"}, room=cart_id)


@app.route("/group-order/invite", methods=["POST"])
def create_group_order():
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
    cart = SharedCart.query.filter_by(CartID=cart_id).first()
    if not cart:
        return jsonify({"error": "Shared cart not found"}), 404

    return jsonify({"cartId": cart_id, "vendorId": cart.VendorID})


@app.route("/group-order/join/<cart_id>", methods=["POST"])
def join_group_order(cart_id):
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

    cart_items = CartItem.query.filter_by(Cart_ID=cart_id).all()
    updated_cart = [
        {
            "ID": str(item.ID),"Item_ID": str(item.Item_ID),"Quantity": item.Quantity,"User_ID": str(item.User_ID)
        }
        for item in cart_items
    ]
    print("Emitting cart_updated event:", json.dumps({"cartId": cart_id, "items": updated_cart}, indent=2))
    socketio.emit("cart_updated", {"cartId": cart_id, "items": updated_cart}, to=None)

    return jsonify({"message": "Item added successfully", "cartId": cart_id})

@app.route("/group-order/<cart_id>", methods=["GET"])
def get_cart_items(cart_id):
    cart_items = CartItem.query.filter_by(Cart_ID=cart_id).all()
    
    if not cart_items:
        return jsonify({"message": "Cart is empty", "cartId": cart_id})

    items = [
        {
            "ID": item.ID,
            "Item_ID": item.Item_ID,
            "User_ID": item.User_ID,
            "Quantity": item.Quantity,
            "Added_at": item.Added_at
        }
        for item in cart_items
    ]
    return jsonify({"CartID": cart_id, "Items": items})

@app.route("/group-order/<cart_id>/remove-item/<item_id>", methods=["DELETE"])
def remove_item_from_cart(cart_id, item_id):
    item = CartItem.query.filter_by(Cart_ID=cart_id, ID=item_id).first()

    if not item:
        return jsonify({"error": "Item not found in cart"}), 404

    db.session.delete(item)
    db.session.commit()

    cart_items = CartItem.query.filter_by(Cart_ID=cart_id).all()
    updated_cart = [
        { "ID": str(item.ID),"Item_ID": str(item.Item_ID),"Quantity": item.Quantity,"User_ID": str(item.User_ID)}
        for item in cart_items
    ]
    print("Emitting cart_updated event:", json.dumps({"cartId": cart_id, "items": updated_cart}, indent=2))
    socketio.emit("cart_updated", {"cartId": cart_id, "items": updated_cart}, to=None)

    return jsonify({"message": "Item removed successfully", "cartId": cart_id})


@app.route("/group-order/<cart_id>/clear", methods=["DELETE"])
def clear_cart(cart_id):
    CartItem.query.filter_by(Cart_ID=cart_id).delete()
    db.session.commit()
    return jsonify({"message": "Cart cleared successfully", "cartId": cart_id})


@socketio.on("connect")
def handle_connect():
    print("WebSocket Connected!")
    emit("message", {"status": "connected"}, broadcast=True)

@socketio.on("disconnect")
def handle_disconnect():
    print("WebSocket Disconnected")
