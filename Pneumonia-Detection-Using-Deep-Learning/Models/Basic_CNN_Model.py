# Case-Study/Capstone_Project/Models/BasicCNNModel.py

import tensorflow as tf
import numpy as np
from tensorflow.keras.models import load_model
from PIL import Image
import cv2
import os

# -----------------------------
# Load Basic CNN Model
# -----------------------------
def load_basic_cnn_model(model_path="basic_cnn_model.keras"):
    """
    Loads the Basic CNN model from given path.
    """
    try:
        model = load_model(model_path)
        return model
    except Exception as e:
        raise RuntimeError(f"❌ Error loading Basic CNN model: {e}")


# -----------------------------
# Preprocess Image
# -----------------------------
def preprocess_image(image, target_size=(150, 150)):
    """
    Preprocess input image (PIL or path) for prediction.
    
    Args:
        image: PIL.Image object OR string path to image file
        target_size: expected input size for model
    
    Returns:
        numpy array ready for model
    """
    # If image is a path, open with PIL
    if isinstance(image, str) and os.path.exists(image):
        image = Image.open(image)

    # Ensure it's PIL before processing
    if not isinstance(image, Image.Image):
        raise ValueError("Input must be a PIL.Image or valid image path")

    # Convert PIL → numpy (RGB)
    img = image.convert("RGB")
    img = img.resize(target_size)
    img_array = np.array(img, dtype=np.float32) / 255.0
    img_array = np.expand_dims(img_array, axis=0)  # (1, H, W, C)

    return img_array


# -----------------------------
# Predict
# -----------------------------
def predict_basic_cnn(model, image):
    """
    Run prediction on image (path or PIL).
    Returns label string.
    """
    processed = preprocess_image(image)
    preds = model.predict(processed)

    # Assuming binary classification (Normal vs Pneumonia)
    predicted_class = np.argmax(preds, axis=1)[0]

    labels = {0: "Normal", 1: "Pneumonia"}
    return labels.get(predicted_class, "Unknown")
