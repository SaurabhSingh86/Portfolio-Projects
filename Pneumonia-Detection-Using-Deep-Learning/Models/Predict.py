# here’s the lazy loading upgrade using st.cache_resource so your models don’t reload every time you click Predict:
# Models/Predict.py

import os
import sys
import torch
import streamlit as st
import tensorflow as tf
import numpy as np
from PIL import Image
import cv2
import pydicom

# -----------------------------
# Base Path for Saved Models
# -----------------------------
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # Capstone_Project
MODEL_DIR = os.path.join(BASE_DIR, "Saved_Models")

# -----------------------------
# Add local YOLOv5 repo to path
# -----------------------------
# YOLOV5_PATH = r"D:\Great Lakes\Case-Study\Case-Study\Capstone_Project\yolov5"
# if YOLOV5_PATH not in sys.path:
#     sys.path.insert(0, YOLOV5_PATH)

# from models.common import DetectMultiBackend

# -----------------------------
# Device detection
# -----------------------------
# DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
# print(f"Using device for YOLOv5: {DEVICE}")

# -----------------------------
# Lazy Loaders for CNN models
# -----------------------------
@st.cache_resource
def load_basic_cnn():
    path = os.path.join(MODEL_DIR, "basic_cnn_model.keras")  
    return tf.keras.models.load_model(path)

@st.cache_resource
def load_fine_tuned_cnn():
    path = os.path.join(MODEL_DIR, "fine_tuned_model_v2.keras") 
    return tf.keras.models.load_model(path)

@st.cache_resource
def load_resnet50():
    path = os.path.join(MODEL_DIR, "resnet50_model.keras")  
    return tf.keras.models.load_model(path)

@st.cache_resource
def load_mobilenetv2():
    path = os.path.join(MODEL_DIR, "transfer_learning_model_mobilenetv2.keras")
    return tf.keras.models.load_model(path)

@st.cache_resource
def load_densenet121():
    path = os.path.join(MODEL_DIR, "transfer_learning_model_densenet121.keras")
    return tf.keras.models.load_model(path)

    
from pathlib import Path

# -----------------------------
# Fix PosixPath issue on Windows for YOLOv5
# -----------------------------
import pathlib

if sys.platform == "win32":
    pathlib.PosixPath = pathlib.WindowsPath

YOLOV5_PATH = r"D:\Great Lakes\Case-Study\Case-Study\Capstone_Project\yolov5"
if YOLOV5_PATH not in sys.path:
    sys.path.insert(0, YOLOV5_PATH)

from yolov5.models.common import DetectMultiBackend
from yolov5.utils.torch_utils import select_device

@st.cache_resource
def load_yolov5():
    """Load YOLOv5 model safely on Windows"""
    weights_path = os.path.join(MODEL_DIR, "yolov5_best.pt")
    device = select_device("0" if torch.cuda.is_available() else "cpu")
    yolo_model = DetectMultiBackend(weights_path, device=device)
    return yolo_model


# -----------------------------
# Unified Predict Function
# -----------------------------
# while training our model was trained on images of size (224, 224, 3) (IMG_WIDTH=224, IMG_HEIGHT=224, IMG_CHANNELS=3).
# 👉 So, every image must be resized to 224x224 before prediction.

# During training, you explicitly divided by 255.0 inside data_generator.
# 👉 So, inference must also normalize pixel values to [0, 1].

# Keras models expect a batch of images, not a single one.
# 👉 Expand dimensions to make shape (1, 224, 224, 3).

# Since your last layer is Dense(1, activation='sigmoid'), predictions are probabilities between 0 and 1.
# 👉 You should set a threshold (default 0.5) to classify:

# > 0.5 → Pneumonia
# <= 0.5 → Normal

# Real-life Note

# Sometimes hospitals adjust the threshold (0.4, 0.6, etc.) depending on sensitivity vs specificity requirements.

# You can make this threshold configurable later in Streamlit (slider for doctors: "Choose sensitivity").


# -----------------------------
# Helper Functions
# -----------------------------
def preprocess_image(image, target_size=(224, 224)):
    """Resize, normalize, and prepare image for CNN model input"""
    image = image.resize(target_size)  # resize
    img_array = np.array(image).astype("float32") / 255.0  # normalize
    img_array = np.expand_dims(img_array, axis=0)  # batch dimension
    return img_array

def load_file_as_pil(file_or_path):
    """
    Load uploaded file or path as PIL.Image.
    Supports PNG/JPEG and DICOM (.dcm).
    """
    try:
        if (hasattr(file_or_path, "name") and file_or_path.name.lower().endswith(".dcm")) \
           or (isinstance(file_or_path, str) and file_or_path.lower().endswith(".dcm")):
            dcm = pydicom.dcmread(file_or_path, force=True)
            img_array = dcm.pixel_array.astype(np.float32)
            img_array = ((img_array - img_array.min()) / (img_array.max() - img_array.min()) * 255).astype(np.uint8)
            image = Image.fromarray(img_array).convert("RGB")
            return image
        else:
            return Image.open(file_or_path).convert("RGB")
    except Exception as e:
        print(f"File load error: {e}")
        return None

# -----------------------------
# CNN Prediction
# -----------------------------
def predict_image(model_name, model, file_or_image, threshold=0.5):
    """
    Run prediction on PNG/JPEG/DICOM or PIL.Image.
    Returns: (result_label, probability)
    """
    try:
        # If input is already PIL.Image
        if isinstance(file_or_image, Image.Image):
            image = file_or_image
        else:
            image = load_file_as_pil(file_or_image)
            if image is None:
                return "Prediction error: Could not read image", 0.0

        # Preprocess
        img_array = preprocess_image(image, target_size=(224, 224))

        # Predict probability
        pred = model.predict(img_array, verbose=0)[0][0]

        # Apply threshold
        result = "Pneumonia" if pred > threshold else "Normal"
        return result, pred

    except Exception as e:
        return f"Prediction error: {e}", 0.0

# -----------------------------
# YOLO Prediction
# -----------------------------
def predict_with_yolo(yolo_model, file_or_path, conf=0.25):
    """
    Run YOLOv5 prediction on image/DICOM file.
    Returns: (predictions, annotated_image)
    """
    # Load image
    if isinstance(file_or_path, Image.Image):
        image = np.array(file_or_path)
    elif str(file_or_path).lower().endswith(".dcm"):
        image = np.array(load_file_as_pil(file_or_path))
    else:
        image = str(file_or_path)  # path for YOLO
    
    # Run inference
    results = yolo_model(image, conf=conf)
    res = results[0]

    boxes = res.boxes.xyxy.cpu().numpy()
    scores = res.boxes.conf.cpu().numpy()
    classes = res.boxes.cls.cpu().numpy()
    names = res.names

    predictions = []
    for box, score, cls in zip(boxes, scores, classes):
        predictions.append({
            "class": names[int(cls)],
            "confidence": float(score),
            "box": box.tolist()
        })

    annotated = res.plot()
    return predictions, annotated

# def preprocess_image(image, target_size=(224, 224)):
#     """Resize, normalize, and prepare image for model input"""
#     image = image.resize(target_size)  # resize
#     img_array = np.array(image).astype("float32") / 255.0  # normalize
#     img_array = np.expand_dims(img_array, axis=0)  # batch dimension
#     return img_array

# def load_file_as_pil(file_or_path):
#     """
#     Load uploaded file or path as PIL.Image.
#     Supports PNG/JPEG and DICOM (.dcm).
#     """
#     try:
#         # Check if DICOM
#         if hasattr(file_or_path, "name") and file_or_path.name.lower().endswith(".dcm"):

#             dcm = pydicom.dcmread(file_or_path, force=True)
#             img_array = dcm.pixel_array.astype(np.float32)
#             img_array = ((img_array - img_array.min()) / (img_array.max() - img_array.min()) * 255).astype(np.uint8)
#             image = Image.fromarray(img_array).convert("RGB")
#             return image
#         else:
#             # PNG/JPEG
#             return Image.open(file_or_path).convert("RGB")
#     except Exception as e:
#         print(f"File load error: {e}")
#         return None

# def predict_image(model_name, model, file_or_image, threshold=0.5):
#     """
#     Run prediction on PNG/JPEG/DICOM or PIL.Image.
#     Returns: (result_label, probability)
#     """
#     try:
#         # If input is already PIL.Image
#         if isinstance(file_or_image, Image.Image):
#             image = file_or_image
#         else:
#             image = load_file_as_pil(file_or_image)
#             if image is None:
#                 return "Prediction error: Could not read image", 0.0

#         # Preprocess
#         img_array = preprocess_image(image, target_size=(224, 224))

#         # Predict probability
#         pred = model.predict(img_array, verbose=0)[0][0]

#         # Apply threshold
#         result = "Pneumonia" if pred > threshold else "Normal"
#         return result, pred

#     except Exception as e:
#         return f"Prediction error: {e}", 0.0

# def predict_with_yolo(model, pil_image, threshold=0.5):
#     """
#     Predict using YOLOv5 and return annotated image.
#     """
#     results = model(pil_image, augment=False, imgsz=640)  # default image size

#     if len(results.xyxy[0]) == 0:
#         return "Not Pneumonia", 0.0, pil_image

#     # Highest confidence detection
#     best_box = max(results.xyxy[0].cpu().numpy(), key=lambda x: x[4])
#     confidence = float(best_box[4])
#     if confidence < threshold:
#         return "Not Pneumonia", confidence, pil_image

#     # Draw bounding box
#     x1, y1, x2, y2 = map(int, best_box[:4])
#     img = np.array(pil_image.convert("RGB"))
#     annotated_img = cv2.rectangle(img.copy(), (x1, y1), (x2, y2), (255, 0, 0), 3)
#     annotated_img = cv2.putText(
#         annotated_img,
#         f"Pneumonia {confidence:.2f}",
#         (x1, y1 - 10),
#         cv2.FONT_HERSHEY_SIMPLEX,
#         0.9,
#         (255, 0, 0),
#         2
#     )

#     return "Pneumonia", confidence, Image.fromarray(annotated_img)

