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
