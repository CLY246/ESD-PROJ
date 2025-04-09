import pandas as pd
import numpy as np
import joblib
import json
from sklearn.linear_model import SGDClassifier
from sklearn.preprocessing import LabelEncoder

# Load dataset
df = pd.read_csv("order_history.csv")

# Build cuisine label encoding
cuisine_encoder = LabelEncoder()
df["CuisineEncoded"] = cuisine_encoder.fit_transform(df["Cuisine"])

# One-hot encoding for features
cuisine_columns = sorted(df["Cuisine"].unique())
cuisine_to_index = {cuisine: idx for idx, cuisine in enumerate(cuisine_columns)}

# Save columns to use later in real-time inference
with open("model/user_cuisine_columns.json", "w") as f:
    json.dump(cuisine_columns, f)

# Build feature vectors
feature_vectors = []
labels = []

vendor_groups = df.groupby("VendorID")

for _, group in vendor_groups:
    # Count cuisines per vendor
    cuisine_counts = group["Cuisine"].value_counts()
    
    feature = np.zeros(len(cuisine_columns))
    for cuisine, count in cuisine_counts.items():
        index = cuisine_to_index[cuisine]
        feature[index] = count

    # Pick the most frequent cuisine as label
    top_cuisine = cuisine_counts.idxmax()
    label = 1  # We’ll use binary class just to simulate positive “preference”

    feature_vectors.append(feature)
    labels.append(label)

# Train SGD Classifier (binary logistic regression)
model = SGDClassifier(loss='log_loss')
model.partial_fit(feature_vectors, labels, classes=np.array([0, 1]))

# Save model
joblib.dump(model, "model/online_model.pkl")
print("Model trained and saved to model/online_model.pkl")
