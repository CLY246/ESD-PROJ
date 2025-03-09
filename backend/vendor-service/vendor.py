from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS

app = Flask(__name__)

CORS(app)  

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+mysqlconnector://root:root@host.docker.internal:8889/Vendors"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)

class Vendor(db.Model):
    __tablename__ = "Vendors"
    
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
    __tablename__ = "MenuItems"

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

class Inventory(db.Model):
    __tablename__ = "Inventory"

    InventoryID = db.Column(db.Integer, primary_key=True, autoincrement=True)
    VendorID = db.Column(db.Integer, db.ForeignKey("Vendors.VendorID"), nullable=False)
    ItemID = db.Column(db.Integer, db.ForeignKey("MenuItems.ItemID"), nullable=False)
    QuantityAvailable = db.Column(db.Integer, nullable=False)
    LastUpdated = db.Column(db.TIMESTAMP, server_default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())

    def json(self):
        return {
            "InventoryID": self.InventoryID,
            "VendorID": self.VendorID,
            "ItemID": self.ItemID,
            "QuantityAvailable": self.QuantityAvailable,
            "LastUpdated": self.LastUpdated
        }
    

@app.route('/api/health')
def health_check():
    return jsonify({"message": "API is running!"})


@app.route("/vendors", methods=["GET"])
def get_vendors():
    vendors = Vendor.query.all()
    return jsonify([
        {
            "VendorID": v.VendorID,
            "VendorName": v.VendorName,
            "Location": v.Location,
            "OpeningHours": v.OpeningHours,
            "ImageURL": v.ImageURL,
            "Cuisine": v.Cuisine,
            "Rating": v.Rating
        }
        for v in vendors
    ])

@app.route("/menu/<int:vendor_id>", methods=["GET"])
def get_menu_items(vendor_id):
    menu_items = MenuItem.query.filter_by(VendorID=vendor_id).all()
    
    if not menu_items:
        return jsonify({"message": "No menu items found for this vendor."}), 404

    return jsonify([item.json() for item in menu_items])


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
    
    
