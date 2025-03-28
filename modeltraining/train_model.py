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

# One-hot encode cuisine (input features)
X = pd.get_dummies(df[["cuisine"]], prefix='', prefix_sep='')

# One-hot encode vendor_id (target)
y = pd.get_dummies(df["vendor_id"])

# Save column structures for later use in prediction
if not os.path.exists("model"):
    os.makedirs("model")

with open("model/cuisine_columns.json", "w") as f:
    json.dump(X.columns.tolist(), f)

with open("model/vendor_columns.json", "w") as f:
    json.dump(y.columns.tolist(), f)

# Convert to float32 for TensorFlow
X = X.astype("float32")
y = y.astype("float32")

# Build a simple feedforward model
model = tf.keras.Sequential([
    tf.keras.Input(shape=(X.shape[1],)),
    layers.Dense(32, activation="relu"),
    layers.Dense(32, activation="relu"),
    layers.Dense(y.shape[1], activation="softmax")
])

# Compile model
model.compile(optimizer="adam", loss="categorical_crossentropy", metrics=["accuracy"])

# Train model
model.fit(X, y, epochs=10, batch_size=16)

# Save model
model.save("model/recommendation_model.h5")
print("✅ Model trained and saved.")
