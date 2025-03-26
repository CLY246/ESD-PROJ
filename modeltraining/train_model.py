import tensorflow as tf
from tensorflow.keras import layers
import pandas as pd

# Load the data
data = pd.read_csv("order_history.csv")

# Ensure all string columns are strings (helps with dummies)
data["user_id"] = data["user_id"].astype(str)
data["cuisine"] = data["cuisine"].astype(str)
data["vendor_id"] = data["vendor_id"].astype(str)

# One-hot encode user and cuisine (features)
X = pd.get_dummies(data[["user_id", "cuisine"]])

# One-hot encode vendor_id (labels)
y = pd.get_dummies(data["vendor_id"])

# Convert to NumPy float32 arrays (so TensorFlow can handle them)
X = X.astype("float32")
y = y.astype("float32")

# Build the model (with Input layer to avoid warning)
model = tf.keras.Sequential([
    tf.keras.Input(shape=(X.shape[1],)),
    layers.Dense(64, activation='relu'),
    layers.Dense(64, activation='relu'),
    layers.Dense(y.shape[1], activation='softmax')
])

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Train the model
model.fit(X, y, epochs=10)

# Save it
model.save("model/recommendation_model.h5")
print("✅ Model trained and saved.")
