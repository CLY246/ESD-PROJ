from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from collections import defaultdict
import os
from os import environ

app = Flask(__name__)

CORS(app)  

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.idoxtwehkovtpgpskzhh:postgres@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


class Vendor(db.Model):
    __tablename__ = "vendors"  

    VendorID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    VendorName = db.Column(db.String(255), nullable=False)
    Location = db.Column(db.String(255), nullable=False)
    OpeningHours = db.Column(db.String(255), nullable=False)
    ImageURL = db.Column(db.String(2048), nullable=False)
    Cuisine = db.Column(db.String(255), nullable=False)
    Rating = db.Column(db.Float, default=0.00)

    def json(self):
        return {
            "VendorID": self.VendorID,
            "VendorName": self.VendorName,
            "Location": self.Location,
            "OpeningHours": self.OpeningHours,
            "ImageURL": self.ImageURL,
            "Cuisine": self.Cuisine,
            "Rating": self.Rating
        }

class MenuItem(db.Model):
    __tablename__ = "menuitems"

    ItemID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    VendorID = db.Column(db.Integer, db.ForeignKey("Vendors.VendorID"), nullable=False)
    ItemName = db.Column(db.String(255), nullable=False)
    Description = db.Column(db.Text)
    Price = db.Column(db.Float, nullable=False)
    Category = db.Column(db.String(100))
    ImageURL = db.Column(db.String(2048)) 

    def json(self):
        return {
            "ItemID": self.ItemID,
            "VendorID": self.VendorID,
            "ItemName": self.ItemName,
            "Description": self.Description,
            "Price": self.Price,
            "Category": self.Category,
            "ImageURL": self.ImageURL
        }

# class Inventory(db.Model):
#     __tablename__ = "Inventory"

#     InventoryID = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     VendorID = db.Column(db.Integer, db.ForeignKey("Vendors.VendorID"), nullable=False)
#     ItemID = db.Column(db.Integer, db.ForeignKey("MenuItems.ItemID"), nullable=False)
#     QuantityAvailable = db.Column(db.Integer, nullable=False)
#     LastUpdated = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

#     def json(self):
#         return {
#             "InventoryID": self.InventoryID,
#             "VendorID": self.VendorID,
#             "ItemID": self.ItemID,
#             "QuantityAvailable": self.QuantityAvailable,
#             "LastUpdated": self.LastUpdated
#         }
    
@app.route("/")
def home():
    return jsonify({"message": "Flask app is connected to Supabase!"})

@app.route('/api/health')
def health_check():
    return jsonify({"message": "API is running!"})


@app.route("/vendors", methods=["GET"])
def get_vendors():
    try:
        vendors = Vendor.query.all()
        if not vendors:
            return jsonify({"message": "No vendors found"}), 404
        return jsonify([vendor.json() for vendor in vendors])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/vendors/<int:vendor_id>", methods=["GET"])
def get_vendor(vendor_id):
    vendor = Vendor.query.filter_by(VendorID=vendor_id).first()

    if not vendor:
        return jsonify({"error": "Vendor not found"}), 404

    return jsonify(
        {
            "VendorID": vendor.VendorID,
            "VendorName": vendor.VendorName,
            "Location": vendor.Location,
            "OpeningHours": vendor.OpeningHours,
            "ImageURL": vendor.ImageURL,
            "Cuisine": vendor.Cuisine,
            "Rating": vendor.Rating,
        }
    )

@app.route("/menu/<int:vendor_id>", methods=["GET"])
def get_menu_items(vendor_id):
    menu_items = MenuItem.query.filter_by(VendorID=vendor_id).all()
    
    if not menu_items:
        return jsonify({"message": "No menu items found for this vendor."}), 404
    
    categorized_menu = defaultdict(list)
    
    for item in menu_items:
        categorized_menu[item.Category].append(item.json())

    return jsonify(categorized_menu)

@app.route("/menuitem/<int:item_id>", methods=["GET"])
def get_menu_item(item_id):
    item = MenuItem.query.filter_by(ItemID=item_id).first()

    if not item:
        return jsonify({"message": "Item not found"}), 404

    return jsonify({
        "ItemID": item.ItemID,
        "ItemName": item.ItemName,
        "Description": item.Description,
        "Price": item.Price,
        "ImageURL": item.ImageURL
    })
