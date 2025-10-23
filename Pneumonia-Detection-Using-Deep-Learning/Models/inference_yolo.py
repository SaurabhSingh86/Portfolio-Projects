import torch
import cv2
import numpy as np
from PIL import Image

# -----------------------------
# Load YOLOv5 model
# -----------------------------
def load_yolo_model(yolo_repo_path, weights_path):
    """
    Load YOLOv5 custom model from local repo.
    """
    model = torch.hub.load(yolo_repo_path, 'custom', path=weights_path, source='local')
    model.eval()
    model.to("cuda" if torch.cuda.is_available() else "cpu")
    return model

# -----------------------------
# Predict image
# -----------------------------
def predict_yolo_image(model, image_pil, conf_threshold=0.5):
    # Convert PIL to NumPy array in BGR
    image = np.array(image_pil)[:, :, ::-1].copy()  # RGB -> BGR

    # Run YOLOv5 inference
    results = model(image)

    boxes = results.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2, conf, cls]
    
    detected = False
    max_conf = 0.0
    
    for box in boxes:
        x1, y1, x2, y2, conf, cls = box
        if conf >= conf_threshold:
            detected = True
            max_conf = max(max_conf, conf)
            # Draw rectangle
            cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
            cv2.putText(image, f"Pneumonia {conf:.2f}", (int(x1), int(y1)-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)
    
    # Convert back to PIL for Streamlit
    annotated_image = Image.fromarray(image[:, :, ::-1])  # BGR -> RGB
    return annotated_image, ("Pneumonia" if detected else "Normal"), max_conf


# def predict_yolo_image(model, image_pil, conf_threshold=0.5):
#     """
#     Predict bounding boxes on a PIL image.
#     Args:
#         model: YOLOv5 model
#         image_pil: PIL.Image
#         conf_threshold: minimum confidence to display
#     Returns:
#         annotated_image: PIL.Image with boxes drawn
#         detected: True if pneumonia detected, else False
#         max_conf: highest probability detected
#     """
#     import cv2
#     import numpy as np
#     from PIL import Image

#     # -----------------------------
#     # Convert PIL to BGR numpy array
#     # -----------------------------
#     if not isinstance(image_pil, np.ndarray):
#         image = np.array(image_pil)  # RGB
#         image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
#     else:
#         image = image_pil

#     # -----------------------------
#     # YOLO inference
#     # -----------------------------
#     # Convert PIL.Image to np.ndarray in BGR format for YOLOv5
#     if isinstance(image_pil, Image.Image):
#         image_np = np.array(image_pil)  # RGB
#         image_np = image_np[:, :, ::-1].copy()  # Convert to BGR
#     else:
#         image_np = image_pil
    
#     results = model(image_np)  # must be np.ndarray
#     boxes = results.xyxy[0].cpu().numpy()  # [x1, y1, x2, y2, conf, class]

#     detected = False
#     max_conf = 0.0

#     for box in boxes:
#         x1, y1, x2, y2, conf, cls = box
#         if conf >= conf_threshold:
#             detected = True
#             max_conf = max(max_conf, conf)
#             # Draw bounding box
#             cv2.rectangle(image, (int(x1), int(y1)), (int(x2), int(y2)), (0, 0, 255), 2)
#             cv2.putText(image, f"Pneumonia {conf:.2f}", (int(x1), int(y1)-10),
#                         cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

#     # Convert back to PIL
#     annotated_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
#     return annotated_image, "Pneumonia" if detected else "Normal", max_conf


