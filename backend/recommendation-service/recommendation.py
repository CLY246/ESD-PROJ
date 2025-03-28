# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests
# import tensorflow as tf
# import numpy as np
# import psycopg2
# import os

# app = Flask(__name__)
# CORS(app)

# # TensorFlow model
# MODEL_PATH = "model/recommendation_model.h5"
# model = tf.keras.models.load_model(MODEL_PATH)

# # Supabase DB credentials (adjust with env vars)
# DB_URL = "aws-0-ap-southeast-1.pooler.supabase.com"
# DB_PORT = "6543"
# DB_NAME = "postgres"
# DB_USER = "postgres.idoxtwehkovtpgpskzhh"
# DB_PASS = "postgres"

# # Connect to Supabase (PostgreSQL)
# def get_supabase_connection():
#     return psycopg2.connect(
#         host=DB_URL,
#         port=DB_PORT,
#         dbname=DB_NAME,
#         user=DB_USER,
#         password=DB_PASS
#     )


# @app.route("/recommend", methods=["POST"])
# def recommend_vendors():
#     data = request.get_json()
#     user_id = data.get("user_id")

#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400

#     try:
#         # STEP 1: Get order history (from orders microservice)
#         orders_response = requests.get("http://ordermanagement-service:5000/orders/{user_id}")        
#         order_data = orders_response.json()

#         cuisines_ordered = [order["cuisine"] for order in order_data["orders"]]

#         # STEP 2: Encode order history (e.g., cuisine frequency)
#         cuisine_types = ["Japanese", "Korean", "Western", "Chinese", "Thai", "Indian"]
#         feature_vector = [cuisines_ordered.count(c) for c in cuisine_types]

#         # STEP 3: Predict cuisine preferences
#         prediction = model.predict(np.array([feature_vector]))[0]  # array of scores

#         # Get top 2 cuisines
#         top_indices = np.argsort(prediction)[-2:][::-1]
#         top_cuisines = [cuisine_types[i] for i in top_indices]

#         # STEP 4: Query vendors by top cuisines from Supabase
#         conn = get_supabase_connection()
#         cur = conn.cursor()

#         cur.execute("SELECT * FROM vendors WHERE cuisine = ANY(%s) LIMIT 5", (top_cuisines,))
#         rows = cur.fetchall()

#         columns = [desc[0] for desc in cur.description]
#         recommended_vendors = [dict(zip(columns, row)) for row in rows]

#         cur.close()
#         conn.close()

#         return jsonify({"recommended": recommended_vendors})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500


# @app.route("/")
# def home():
#     return jsonify({"message": "Recommendation microservice running!"})


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5013)



# from flask import Flask, request, jsonify
# from flask_cors import CORS
# import requests
# import tensorflow as tf
# import numpy as np
# import psycopg2
# import os
# from flask_sqlalchemy import SQLAlchemy

# app = Flask(__name__)
# app.config["DEBUG"] = True
# CORS(app)  

# app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.idoxtwehkovtpgpskzhh:postgres@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
# app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# db = SQLAlchemy()
# with app.app_context():
#     db.init_app(app)


# class Recommendation(db.Model):
#     __tablename__ = "recommended_vendors"
#     vendor_id = db.Column(db.Integer, primary_key=True)
#     vendor_name = db.Column(db.String(255), nullable=False)
#     cuisine = db.Column(db.String(255), nullable=False)
#     image_url = db.Column(db.String(255), nullable=True)
# # 🔹 Load TensorFlow model
# MODEL_PATH = "model/recommendation_model.h5"
# model = tf.keras.models.load_model(MODEL_PATH)

# # 🔹 Cuisine categories used during training
# CUISINE_TYPES = ["Japanese", "Korean", "Western", "Chinese", "Thai", "Indian"]

# # 🔹 Supabase PostgreSQL credentials
# DB_URL = "aws-0-ap-southeast-1.pooler.supabase.com"
# DB_PORT = "6543"
# DB_NAME = "postgres"
# DB_USER = "postgres.idoxtwehkovtpgpskzhh"
# DB_PASS = "postgres"

# def get_supabase_connection():
#     return psycopg2.connect(
#         host=DB_URL,
#         port=DB_PORT,
#         dbname=DB_NAME,
#         user=DB_USER,
#         password=DB_PASS
#     )

# @app.route("/recommend", methods=["POST"])
# def recommend_vendors():
#     data = request.get_json()
#     user_id = data.get("user_id")

#     if not user_id:
#         return jsonify({"error": "Missing user_id"}), 400

#     try:
#         # ✅ STEP 1: Fetch order data from OutSystems REST API
#         outsystems_api_url = f"https://outsystems.example.com/api/order_history/{user_id}"
#         headers = { 
#             "Content-Type": "application/json"
#         }
#         response = requests.get(outsystems_api_url, headers=headers)

#         if response.status_code != 200:
#             return jsonify({"error": "Failed to fetch data from OutSystems API"}), 500

#         order_data = response.json()
#         orders = order_data.get("orders", [])

#         if not orders:
#             return jsonify({"recommended": [], "message": "No orders found for user."})

#         # ✅ STEP 2: Extract vendor IDs from the API response
#         vendor_ids = [order["vendor_id"] for order in orders]

#         # ✅ STEP 3: Query Supabase to get cuisines for these vendor IDs
#         conn = get_supabase_connection()
#         cur = conn.cursor()

#         # Fetch cuisines for the vendor IDs
#         cur.execute("SELECT cuisine FROM vendors WHERE vendor_id = ANY(%s)", (vendor_ids,))
#         cuisines_ordered = [row[0] for row in cur.fetchall()]

#         cur.close()
#         conn.close()


#         feature_vector = [cuisines_ordered.count(c) for c in CUISINE_TYPES]


#         prediction = model.predict(np.array([feature_vector]))[0]  # 1D array

#         top_indices = np.argsort(prediction)[-2:][::-1]
#         top_cuisines = [CUISINE_TYPES[i] for i in top_indices]


#         conn = get_supabase_connection()
#         cur = conn.cursor()

#         # Use tuple-style format for SQL query (Postgres ARRAY)
#         cur.execute("SELECT * FROM vendors WHERE cuisine = ANY(%s) LIMIT 5", (top_cuisines,))
#         rows = cur.fetchall()

#         columns = [desc[0] for desc in cur.description]
#         recommended_vendors = [dict(zip(columns, row)) for row in rows]

#         cur.close()
#         conn.close()

#         return jsonify({"recommended": recommended_vendors})

#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# @app.route("/")
# def home():
#     return jsonify({"message": "✅ Recommendation microservice is running."})

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5013)








from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import tensorflow as tf
import numpy as np
import psycopg2
import os
from flask_sqlalchemy import SQLAlchemy
import traceback
import requests
import json
import logging

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)  


# db = SQLAlchemy()
# with app.app_context():
#     db.init_app(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.idoxtwehkovtpgpskzhh:postgres@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}

db = SQLAlchemy(app)


# class Recommendation(db.Model):
#     __tablename__ = "recommended_vendors"
#     vendor_id = db.Column(db.Integer, primary_key=True)
#     vendor_name = db.Column(db.String(255), nullable=False)
#     cuisine = db.Column(db.String(255), nullable=False)
#     image_url = db.Column(db.String(255), nullable=True)
# 🔹 Load TensorFlow model
MODEL_PATH = "model/recommendation_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

with open("model/cuisine_columns.json", "r") as f:
    CUISINE_COLUMNS = json.load(f)

with open("model/vendor_columns.json", "r") as f:
    VENDOR_COLUMNS = json.load(f)

# 🔹 Cuisine categories used during training
CUISINE_TYPES = ["Japanese", "Korean", "Western", "Chinese", "Thai", "Indian"]

class Vendor(db.Model):
    __tablename__ = "vendors"

    VendorID = db.Column(db.Integer, primary_key=True)
    VendorName = db.Column(db.String(255))
    Cuisine = db.Column(db.String(255))
    ImageURL = db.Column(db.String(2048))


@app.route('/test', methods=['POST'])
def recommendations():
    try:
        data = request.get_json()

        if not data or 'OrderHistory' not in data:
            return jsonify({"error": "OrderHistory data is required"}), 400

        order_history = data['OrderHistory']

        # Step 1: Count cuisines (use correct key: "Cuisine")
        cuisines_ordered = [order["Cuisine"] for order in order_history]

        # Step 2: Build feature vector from cuisine_columns
        cuisine_counts = {cuisine: cuisines_ordered.count(cuisine) for cuisine in CUISINE_COLUMNS}
        feature_vector = [cuisine_counts.get(col, 0) for col in CUISINE_COLUMNS]

        # Step 3: Predict
        prediction = model.predict(np.array([feature_vector]))[0]
        top_indices = np.argsort(prediction)[-2:][::-1]
        # top_vendor_ids = [str(order["VendorID"]) for order in order_history[:1]]
        top_cuisines = [CUISINE_COLUMNS[i] for i in top_indices]
        # top_cuisines = ['Western'] 
        # top_vendor_ids = [VENDOR_COLUMNS[i] for i in top_indices]
        print("Top predicted cuisines:", top_cuisines)
        logging.info(f" Top predicted cuisines: {top_cuisines}")

        # Step 4: Filter orders for top vendor matches
        seen = set()
        recommended_vendors = []
        
        vendors = Vendor.query.filter(Vendor.Cuisine.in_(top_cuisines)).limit(5).all()

        recommended_vendors = [{
            "VendorID": vendor.VendorID,
            "VendorName": vendor.VendorName,
            "Cuisine": vendor.Cuisine,
            "ImageURL": vendor.ImageURL
        } for vendor in vendors]
        return jsonify({"recommended": recommended_vendors})

    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


# @app.route("/recommend/orderhistory", methods=["POST"])
# def recommend_vendors(orderhistory):
#     try:
#        data = request.get_json()

#         order_data = data.get("UserOrdersAPI", {}).get("OrderDetails", [])
#         orders = order_data.get("UserOrdersAPI", {}).get("OrderDetails", [])

#         if not orders:
#             return jsonify({"recommended": [], "message": "No orders found for user."})

#         # 🧠 Step 1: Count cuisines
#         cuisines_ordered = [order["Cuisine"] for order in orders]
#         feature_vector = [cuisines_ordered.count(c) for c in CUISINE_TYPES]

#         # 🧠 Step 2: Predict top cuisines
#         prediction = model.predict(np.array([feature_vector]))[0]
#         top_indices = np.argsort(prediction)[-2:][::-1]
#         top_cuisines = [CUISINE_TYPES[i] for i in top_indices]

#         # 🔍 Step 3: Filter orders for vendors matching top cuisines
#         seen_vendors = set()
#         recommended_vendors = []
#         for order in orders:
#             if order["Cuisine"] in top_cuisines and order["VendorID"] not in seen_vendors:
#                 recommended_vendors.append({
#                     "VendorID": order["VendorID"],
#                     "VendorName": order["VendorName"],
#                     "Cuisine": order["Cuisine"],
#                     "ImageURL": order["ImageURL"]
#                 })
#                 seen_vendors.add(order["VendorID"])

#             if len(recommended_vendors) >= 5:
#                 break

#         return jsonify({"recommended": recommended_vendors})

#     except Exception as e:
#         import traceback
#         traceback.print_exc()
#         return jsonify({"error": "Server error", "details": str(e)}), 500



@app.route("/")
def home():
    return jsonify({"message": "✅ Recommendation microservice is running."})




# -------------------- Create tables if not exist -------------------

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
