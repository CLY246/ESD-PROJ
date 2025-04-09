
from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import tensorflow as tf
import numpy as np
import os
from flask_sqlalchemy import SQLAlchemy
import traceback
import requests
import json
import logging
import pandas as pd
from flasgger import Swagger

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

# Initialize Flasgger with OpenAPI specifications
app.config['SWAGGER'] = {
    'title': 'Recommedation Microservice API',
    'version': 1.0,
    "openapi": "3.0.2",
    'description': 'API to retrieve vendors and menu items',
}

swagger = Swagger(app)


def recommend_top_cuisines(user_history_df, model_path="model/user_cuisine_model.h5", top_k=2):
    model = tf.keras.models.load_model(model_path)

    # Load column structure
    with open("model/user_cuisine_columns.json") as f:
        cuisine_columns = json.load(f)

    # Build feature row
    user_input = pd.Series(0, index=cuisine_columns, dtype="float32")
    for cuisine in user_history_df["Cuisine"]:
        if cuisine in user_input.index:
            user_input[cuisine] += 1

    # Predict top cuisines
    preds = model.predict(np.array([user_input]))[0]
    top_indices = preds.argsort()[-top_k:][::-1]
    top_cuisines = [cuisine_columns[i] for i in top_indices]

    return top_cuisines

class Vendor(db.Model):
    __tablename__ = "vendors"

    VendorID = db.Column(db.Integer, primary_key=True)
    VendorName = db.Column(db.String(255))
    Cuisine = db.Column(db.String(255))
    ImageURL = db.Column(db.String(2048))


@app.route('/test', methods=['POST'])
def recommendations():
    """
    Recommend Vendors Based on Order History
    ---
    tags:
      - Recommendation
    summary: Recommend vendors based on user's past orders
    requestBody:
      required: true
      content:
        application/json:
          schema:
            type: object
            properties:
              OrderHistory:
                type: array
                items:
                  type: object
                  properties:
                    VendorID:
                      type: integer
                      example: 101
                    ImageURL:
                      type: string
                    VendorName:
                      type: string
                      example: "Sushi Tei"
                    Cuisine:
                      type: string
                      example: "Japanese"
    responses:
      200:
        description: List of recommended vendors
        content:
          application/json:
            schema:
              type: object
              properties:
                recommended:
                  type: array
                  items:
                    type: object
                    properties:
                      VendorID:
                        type: integer
                        example: 102
                      VendorName:
                        type: string
                        example: "Korean Bites"
                      Cuisine:
                        type: string
                        example: "Korean"
                      ImageURL:
                        type: string
                        example: "https://example.com/images/korean-bites.jpg"
      400:
        description: Bad Request (e.g. missing OrderHistory)
      500:
        description: Internal Server Error
    """
    try:
        data = request.get_json()

        if not data or 'OrderHistory' not in data:
            return jsonify({"error": "OrderHistory data is required"}), 400

        order_history = data['OrderHistory']
        user_history_df = pd.DataFrame(order_history)

        top_cuisines = recommend_top_cuisines(user_history_df, model_path="model/user_cuisine_model.h5", top_k=2)
        print("Top predicted cuisines:", top_cuisines)
        logging.info(f"Top predicted cuisines: {top_cuisines}")

        vendors = Vendor.query.filter(Vendor.Cuisine.in_(top_cuisines)).limit(5).all()

        recommended_vendors = [{
            "VendorID": vendor.VendorID,
            "VendorName": vendor.VendorName,
            "Cuisine": vendor.Cuisine,
            "ImageURL": vendor.ImageURL
        } for vendor in vendors]

        return jsonify({"recommended": recommended_vendors})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500






from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
import traceback
import numpy as np
import pandas as pd
import joblib
import json
import os
from collections import Counter

app = Flask(__name__)
CORS(app)


MODEL_PATH = "model/online_model.pkl"
COLUMNS_PATH = "model/user_cuisine_columns.json"

# Load model and cuisine columns
if os.path.exists(MODEL_PATH):
    model = joblib.load(MODEL_PATH)
else:
    raise FileNotFoundError("online_model.pkl not found. Please run initial training.")

with open(COLUMNS_PATH) as f:
    cuisine_columns = json.load(f)

# Connect to Supabase/PostgreSQL
app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql://postgres.idoxtwehkovtpgpskzhh:postgres@aws-0-ap-southeast-1.pooler.supabase.com:6543/postgres"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {'pool_recycle': 299}
db = SQLAlchemy(app)


# SQLAlchemy model for vendor table
class Vendor(db.Model):
    __tablename__ = "vendors"
    VendorID = db.Column(db.Integer, primary_key=True)
    VendorName = db.Column(db.String(255))
    Cuisine = db.Column(db.String(255))
    ImageURL = db.Column(db.String(2048))


#  Helper: Recommend top cuisines
def recommend_top_cuisines(order_history_df, top_k=2):
    feature_vector = np.zeros(len(cuisine_columns))
    for cuisine in order_history_df["Cuisine"]:
        if cuisine in cuisine_columns:
            idx = cuisine_columns.index(cuisine)
            feature_vector[idx] += 1

    feature_vector = feature_vector.reshape(1, -1)

    try:
        proba = model.predict_proba(feature_vector)[0]
    except AttributeError:
        decision = model.decision_function(feature_vector)
        proba = (decision - np.min(decision)) / (np.max(decision) - np.min(decision))

    top_indices = np.argsort(proba)[-top_k:][::-1]
    top_cuisines = [cuisine_columns[i] for i in top_indices]

    return top_cuisines


# 1. Recommend endpoint
@app.route('/recommendation', methods=['POST'])
def recommendations():
    try:
        data = request.get_json()
        if not data or 'OrderHistory' not in data:
            return jsonify({"error": "OrderHistory data is required"}), 400

        order_history = data['OrderHistory']
        order_history_df = pd.DataFrame(order_history)

        cuisine_counts = Counter(order_history_df["Cuisine"])
        top_cuisines = [c for c, _ in cuisine_counts.most_common(2)]
        # top_cuisines = recommend_top_cuisines(order_history_df)
        print("Top predicted cuisines:", top_cuisines)

        recommended_vendors = []
        for cuisine in top_cuisines:
            try:
                vendor_res = requests.get(f"http://vendor-service:5000/vendors/cuisine/{cuisine}")
                if vendor_res.status_code == 200:
                    vendor_list = vendor_res.json().get("vendors", [])
                    recommended_vendors.extend(vendor_list)
                else:
                    print(f" No vendors found for cuisine: {cuisine}")
            except Exception as e:
                print(f"Error fetching vendors for {cuisine}:", str(e))

        # Optional: Deduplicate by VendorID
        seen = set()
        filtered_vendors = []
        for v in recommended_vendors:
            if v["VendorID"] not in seen:
                filtered_vendors.append(v)
                seen.add(v["VendorID"])

        # Step 4: Return response
        return jsonify({"recommended": filtered_vendors[:3]})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"error": "Internal server error", "details": str(e)}), 500


@app.route("/")
def home():
    """
    Health Check
    ---
    
    summary: Health check endpoint for the microservice
    responses:
      200:
        description: Service is running
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                  example: "Recommendation microservice is running."
    """
    return jsonify({"message": "Recommendation microservice is running."})




if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)


