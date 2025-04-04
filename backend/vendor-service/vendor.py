from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from collections import defaultdict
import os
from os import environ
from flasgger import Swagger

app = Flask(__name__)

CORS(app)  

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.idoxtwehkovtpgpskzhh:postgres@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


# Initialize Flasgger with OpenAPI specifications
app.config['SWAGGER'] = {
    'title': 'Vendor Microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'API to retrieve, update, and delete vendors and menu items',
}

swagger = Swagger(app)

# Swagger schema definitions
app.config['SWAGGER']['definitions'] = {
    "Vendor": {
        "type": "object",
        "properties": {
            "VendorID": {"type": "integer"},
            "VendorName": {"type": "string"},
            "Location": {"type": "string"},
            "OpeningHours": {"type": "string"},
            "ImageURL": {"type": "string"},
            "Cuisine": {"type": "string"},
            "Rating": {"type": "number", "format": "float"}
        }
    },
    "MenuItem": {
        "type": "object",
        "properties": {
            "ItemID": {"type": "integer"},
            "VendorID": {"type": "integer"},
            "ItemName": {"type": "string"},
            "Description": {"type": "string"},
            "Price": {"type": "number", "format": "float"},
            "Category": {"type": "string"},
            "ImageURL": {"type": "string"}
        }
    }
}


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
    """
    Health check endpoint
    ---
    responses:
      200:
        description: Supabase is running
        
        500: internal error
    """
    
    return jsonify({"message": "Flask app is connected to Supabase!"})

@app.route('/api/health')
def health_check():
    """
    Health check endpoint
    ---
    responses:
      200:
        description: API is running
    """
    return jsonify({"message": "API is running!"})


@app.route("/vendors", methods=["GET"])
def get_vendors():
    
    """
    Get all vendors
    ---
    summary: Retrieve all vendors
    description: Fetches all vendors from the database
    responses:
        200:
            description: A list of vendors
            schema:
                type: array
                items:
                    $ref: '#/definitions/Vendor'
        404:
            description: No vendors found
        500:
            description: Internal server error
    """
    
    try:
        vendors = Vendor.query.all()
        if not vendors:
            return jsonify({"message": "No vendors found"}), 404
        return jsonify([vendor.json() for vendor in vendors])
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/vendors/<int:vendor_id>", methods=["GET"])
def get_vendor(vendor_id):
    """
    Get a single vendor by ID
    ---
    summary: Retrieve vendor details
    parameters:
      - name: vendor_id
        in: path
        type: integer
        required: true
        description: The ID of the vendor
    responses:
        200:
            description: Vendor details
            schema:
                $ref: '#/definitions/Vendor'
        404:
            description: Vendor not found
    """
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
    """
    Get a specific menu item
    ---
    summary: Retrieve details of a menu item
    parameters:
      - name: item_id
        in: path
        type: integer
        required: true
        description: The ID of the menu item
    responses:
        200:
            description: Menu item details
            schema:
                $ref: '#/definitions/MenuItem'
        404:
            description: Item not found
    """
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


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)