import pandas as pd
import tensorflow as tf
from tensorflow.keras import layers
import numpy as np
import json
import os

# Load dataset
df = pd.read_csv("order_history.csv")

# Clean and cast
df["cuisine"] = df["cuisine"].astype(str)
df["vendor_id"] = df["vendor_id"].astype(str)
df["user_id"] = df["user_id"].astype(str)

# Step 1: Build a user–cuisine frequency table
user_cuisine_counts = df.groupby(["user_id", "cuisine"]).size().unstack(fill_value=0)

# Save column structure for later prediction
if not os.path.exists("model"):
    os.makedirs("model")

with open("model/user_cuisine_columns.json", "w") as f:
    json.dump(user_cuisine_counts.columns.tolist(), f)

# Step 2: Prepare X (input) and y (target)
# X = how many times user ordered each cuisine
# y = which cuisines are "preferred" (ordered more than once)
X = user_cuisine_counts.astype("float32")
y = (user_cuisine_counts > 1).astype("float32")

# Step 3: Build the model
model = tf.keras.Sequential([
    layers.Input(shape=(X.shape[1],)),
    layers.Dense(64, activation='relu'),
    layers.Dense(64, activation='relu'),
    layers.Dense(y.shape[1], activation='sigmoid')  # sigmoid for multi-label
])

# Step 4: Compile the model
model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])

# Step 5: Train the model
model.fit(X, y, epochs=10, batch_size=8)

# Step 6: Save the model
model.save("model/user_cuisine_model.h5")
print("✅ User–Cuisine model trained and saved.")
