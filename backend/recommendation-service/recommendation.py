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



from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import tensorflow as tf
import numpy as np
import psycopg2
import os
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config["DEBUG"] = True
CORS(app)  

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.idoxtwehkovtpgpskzhh:postgres@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy()
with app.app_context():
    db.init_app(app)


class Recommendation(db.Model):
    __tablename__ = "recommended_vendors"
    vendor_id = db.Column(db.Integer, primary_key=True)
    vendor_name = db.Column(db.String(255), nullable=False)
    cuisine = db.Column(db.String(255), nullable=False)
    image_url = db.Column(db.String(255), nullable=True)
# 🔹 Load TensorFlow model
MODEL_PATH = "model/recommendation_model.h5"
model = tf.keras.models.load_model(MODEL_PATH)

# 🔹 Cuisine categories used during training
CUISINE_TYPES = ["Japanese", "Korean", "Western", "Chinese", "Thai", "Indian"]

# 🔹 Supabase PostgreSQL credentials
DB_URL = "aws-0-ap-southeast-1.pooler.supabase.com"
DB_PORT = "6543"
DB_NAME = "postgres"
DB_USER = "postgres.idoxtwehkovtpgpskzhh"
DB_PASS = "postgres"

def get_supabase_connection():
    return psycopg2.connect(
        host=DB_URL,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASS
    )

@app.route("/recommend", methods=["POST"])
def recommend_vendors():
    data = request.get_json()
    user_id = data.get("user_id")

    if not user_id:
        return jsonify({"error": "Missing user_id"}), 400

    try:
        # ✅ STEP 1: Fetch order data from OutSystems REST API
        outsystems_api_url = f"https://outsystems.example.com/api/order_history/{user_id}"
        headers = {
            "Authorization": "Bearer <your_api_token>",  # Replace with your API token if required
            "Content-Type": "application/json"
        }
        response = requests.get(outsystems_api_url, headers=headers)

        if response.status_code != 200:
            return jsonify({"error": "Failed to fetch data from OutSystems API"}), 500

        order_data = response.json()
        orders = order_data.get("orders", [])

        if not orders:
            return jsonify({"recommended": [], "message": "No orders found for user."})

        # ✅ STEP 2: Extract vendor IDs from the API response
        vendor_ids = [order["vendor_id"] for order in orders]

        # ✅ STEP 3: Query Supabase to get cuisines for these vendor IDs
        conn = get_supabase_connection()
        cur = conn.cursor()

        # Fetch cuisines for the vendor IDs
        cur.execute("SELECT cuisine FROM vendors WHERE vendor_id = ANY(%s)", (vendor_ids,))
        cuisines_ordered = [row[0] for row in cur.fetchall()]

        cur.close()
        conn.close()

        # ✅ STEP 4: Count cuisine frequencies
        feature_vector = [cuisines_ordered.count(c) for c in CUISINE_TYPES]

        # ✅ STEP 5: Predict user preferences (vector of probabilities for each cuisine)
        prediction = model.predict(np.array([feature_vector]))[0]  # 1D array

        # ✅ STEP 6: Get top N predicted cuisines (we’ll use top 2)
        top_indices = np.argsort(prediction)[-2:][::-1]
        top_cuisines = [CUISINE_TYPES[i] for i in top_indices]

        # ✅ STEP 7: Query Supabase vendors matching those top cuisines
        conn = get_supabase_connection()
        cur = conn.cursor()

        # Use tuple-style format for SQL query (Postgres ARRAY)
        cur.execute("SELECT * FROM vendors WHERE cuisine = ANY(%s) LIMIT 5", (top_cuisines,))
        rows = cur.fetchall()

        columns = [desc[0] for desc in cur.description]
        recommended_vendors = [dict(zip(columns, row)) for row in rows]

        cur.close()
        conn.close()

        return jsonify({"recommended": recommended_vendors})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/")
def home():
    return jsonify({"message": "✅ Recommendation microservice is running."})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5013)
