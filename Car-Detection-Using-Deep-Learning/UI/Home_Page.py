# app.py
import streamlit as st
from ultralytics import YOLO
import numpy as np
from PIL import Image
import cv2
import tempfile, os, time
import pandas as pd
from io import BytesIO
from collections import Counter



# Optional OCR
try:
    import pytesseract
    pytesseract.pytesseract.tesseract_cmd = 'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'
    OCR_AVAILABLE = True
except Exception:
    OCR_AVAILABLE = False

st.set_page_config("🚘 Car Surveillance", layout="wide")

# ---------------------------
# Utils
# ---------------------------
@st.cache_resource
def load_model(weights_path: str):
    model = YOLO(weights_path)
    return model

def pil_to_bgr_np(img_pil: Image.Image):
    np_img = np.array(img_pil.convert("RGB"))
    return np_img[:, :, ::-1].copy()

def bgr_np_to_pil(img_bgr: np.ndarray):
    return Image.fromarray(img_bgr[:, :, ::-1])

def draw_boxes_on_image(image_np_bgr, detections, model):
    """
    detections: results[0].boxes (Ultralytics Boxes object)
    model: loaded YOLO model (for names)
    """
    img = image_np_bgr.copy()
    boxes_info = []
    for box in detections:
        xyxy = box.xyxy[0].cpu().numpy() if hasattr(box.xyxy, "__call__") else box.xyxy[0].numpy()
        x1, y1, x2, y2 = map(int, xyxy)
        conf = float(box.conf[0]) if hasattr(box.conf, "__call__") or hasattr(box.conf, "numpy") else float(box.conf)
        cls = int(box.cls[0]) if hasattr(box.cls, "__call__") or hasattr(box.cls, "numpy") else int(box.cls)
        label = model.names.get(cls, str(cls)) if hasattr(model, "names") else str(cls)

        # Draw rectangle and label
        cv2.rectangle(img, (x1, y1), (x2, y2), (14, 204, 121), 2)
        text = f"{label} {conf:.2f}"
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.6, 1)
        cv2.rectangle(img, (x1, y1 - 20), (x1 + tw + 6, y1), (14, 204, 121), -1)
        cv2.putText(img, text, (x1 + 3, y1 - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 0), 1, cv2.LINE_AA)

        boxes_info.append({"label": label, "conf": conf, "xyxy": (x1, y1, x2, y2)})
    return img, boxes_info

def dominant_color_in_bbox(img_bgr, xyxy):
    x1, y1, x2, y2 = xyxy
    patch = img_bgr[max(0,y1):y2, max(0,x1):x2]
    if patch.size == 0:
        return (0,0,0)
    # Resize small patch to speed up
    small = cv2.resize(patch, (50,50), interpolation=cv2.INTER_AREA)
    # Convert to RGB for human-readable
    small_rgb = small[:,:,::-1].reshape(-1,3)
    # Use simple mode (most common color)
    colors, counts = np.unique(small_rgb, axis=0, return_counts=True)
    dominant = colors[counts.argmax()]
    return tuple(int(c) for c in dominant)  # R,G,B

def ocr_license_plate(img_bgr, xyxy):
    if not OCR_AVAILABLE:
        return None
    x1,y1,x2,y2 = xyxy
    patch = img_bgr[max(0,y1):y2, max(0,x1):x2]
    if patch.size == 0:
        return None
    patch_rgb = patch[:,:,::-1]
    pil = Image.fromarray(patch_rgb)
    # Basic configuration; tweak as needed
    text = pytesseract.image_to_string(pil, config='--psm 7')
    text = text.strip()
    return text if text else None

# ---------------------------
# App UI
# ---------------------------
st.title("🚘 Car Surveillance — YOLO Integration")
st.markdown("Upload image or video, or use webcam. Model weights assumed at `D:\LLM Projects\Car_Detection\Saved_Models\yolov8n_best.pt`")

# sidebar
with st.sidebar:
    st.header("Settings")
    weights_path = st.text_input("Model Weights Path", value="D:\LLM Projects\Car_Detection\Saved_Models\yolov8n_best.pt")
    conf_thresh = st.slider("Confidence threshold", 0.0, 1.0, 0.45, 0.01)
    iou_thresh = st.slider("IOU NMS threshold", 0.0, 1.0, 0.45, 0.01)
    show_dominant_color = st.checkbox("Show dominant color of bbox", value=True)
    enable_ocr = st.checkbox("Try OCR for license plates (pytesseract)", value=False)
    if enable_ocr and not OCR_AVAILABLE:
        st.warning("pytesseract not installed or not importable in the environment. OCR disabled.")

# load model (cached)
try:
    model = load_model(weights_path)
except Exception as e:
    st.error(f"Failed to load model from {weights_path}: {e}")
    st.stop()

# Input choice
input_mode = st.radio("Input Mode", ["Image Upload", "Video Upload", "Webcam (Realtime)"])

# Session results storage
if "detections_log" not in st.session_state:
    st.session_state.detections_log = []

# ---------- IMAGE ----------
if input_mode == "Image Upload":
    uploaded = st.file_uploader("Upload an image", type=["jpg","jpeg","png"])
    if uploaded:
        image = Image.open(uploaded).convert("RGB")
        st.image(image, caption="Original", width='stretch')
        if st.button("Run Detection on Image"):
            img_bgr = pil_to_bgr_np(image)
            results = model(img_bgr, conf=conf_thresh, iou=iou_thresh)
            boxes = results[0].boxes  # Ultralytics Boxes
            annotated_bgr, boxes_info = draw_boxes_on_image(img_bgr, boxes, model)

            display_pil = bgr_np_to_pil(annotated_bgr)
            st.image(display_pil, caption="Annotated", width='stretch')

            # Collect metadata
            detections_meta = []
            for b in boxes_info:
                meta = {"label": b["label"], "confidence": b["conf"], "bbox": b["xyxy"]}
                if show_dominant_color:
                    dom_rgb = dominant_color_in_bbox(img_bgr, b["xyxy"])
                    meta["dominant_color_rgb"] = dom_rgb
                if enable_ocr:
                    lp = ocr_license_plate(img_bgr, b["xyxy"])
                    meta["ocr_plate"] = lp
                detections_meta.append(meta)

            st.subheader("Detections")
            st.json(detections_meta)

            # Save to session log
            st.session_state.detections_log.append({
                "type": "image",
                "filename": uploaded.name,
                "time": time.time(),
                "detections": detections_meta
            })

            # Download button for annotated image
            buf = BytesIO()
            display_pil.save(buf, format="PNG")
            st.download_button("Download annotated image", data=buf.getvalue(), file_name="annotated.png", mime="image/png")

# ---------- VIDEO ----------
elif input_mode == "Video Upload":
    uploaded_vid = st.file_uploader("Upload a video (mp4/mov/avi)", type=["mp4","mov","avi"])
    max_frames = st.slider("Max frames to process (for preview)", min_value=10, max_value=1000, value=200, step=10)
    if uploaded_vid:
        tfile = tempfile.NamedTemporaryFile(delete=False)
        tfile.write(uploaded_vid.read())
        vid_path = tfile.name

        if st.button("Run Detection on Video"):
            cap = cv2.VideoCapture(vid_path)
            fps = cap.get(cv2.CAP_PROP_FPS) or 25.0
            w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

            # temp output
            out_path = tempfile.NamedTemporaryFile(suffix=".mp4", delete=False).name
            fourcc = cv2.VideoWriter_fourcc(*"mp4v")
            out_vid = cv2.VideoWriter(out_path, fourcc, fps, (w,h))

            frame_idx = 0
            video_detections = []
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame_idx += 1
                if frame_idx > max_frames:
                    break
                # run detection (do small resize if you want speed)
                results = model(frame, conf=conf_thresh, iou=iou_thresh)
                boxes = results[0].boxes
                annotated_frame, boxes_info = draw_boxes_on_image(frame, boxes, model)

                # optionally compute meta
                frame_meta = []
                for b in boxes_info:
                    meta = {"label": b["label"], "confidence": b["conf"], "bbox": b["xyxy"]}
                    if show_dominant_color:
                        meta["dominant_color_rgb"] = dominant_color_in_bbox(frame, b["xyxy"])
                    if enable_ocr:
                        meta["ocr_plate"] = ocr_license_plate(frame, b["xyxy"])
                    frame_meta.append(meta)
                video_detections.append({"frame": frame_idx, "detections": frame_meta})

                out_vid.write(annotated_frame)

            cap.release()
            out_vid.release()

            st.success("Video processed (partial if limited by max frames).")
            # show video
            with open(out_path, "rb") as f:
                st.video(f.read())

            # Save to session log
            st.session_state.detections_log.append({
                "type": "video",
                "filename": uploaded_vid.name,
                "time": time.time(),
                "detections": video_detections,
                "output_path": out_path
            })
            st.write(f"Processed video saved at {out_path} (temporary).")

# ---------- WEBCAM REALTIME ----------
else:  # Webcam
    st.info("Webcam mode: Press Start to open your webcam and run realtime detection. Close the window to stop.")
    start = st.button("Start Webcam (Realtime)")
    if start:
        # Streamlit can't show opencv window directly in some hosts — using frame-by-frame display
        cap = cv2.VideoCapture(0)
        if not cap.isOpened():
            st.error("Unable to access webcam.")
        else:
            placeholder = st.empty()
            stop_flag = False
            try:
                while True:
                    ret, frame = cap.read()
                    if not ret:
                        break
                    results = model(frame, conf=conf_thresh, iou=iou_thresh)
                    boxes = results[0].boxes
                    annotated_frame, boxes_info = draw_boxes_on_image(frame, boxes, model)

                    # show frame
                    annotated_rgb = annotated_frame[:, :, ::-1]
                    placeholder.image(annotated_rgb, channels="RGB", width='stretch')

                    # a small delay - 1/fps
                    if cv2.waitKey(1) & 0xFF == ord("q"):
                        break
            except KeyboardInterrupt:
                pass
            finally:
                cap.release()
                placeholder.empty()
                st.success("Webcam stream stopped.")

# ---------------------------
# Detections Log / Export
# ---------------------------
st.sidebar.markdown("---")
st.sidebar.subheader("Session Detections Log")
if st.sidebar.button("Show Log"):
    st.sidebar.write(pd.DataFrame(st.session_state.detections_log))

if st.sidebar.button("Export Log (CSV)"):
    rows = []
    for entry in st.session_state.detections_log:
        rows.append({
            "type": entry.get("type"),
            "filename": entry.get("filename"),
            "time": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(entry.get("time"))),
            "num_entries": len(entry.get("detections"))
        })
    if rows:
        df = pd.DataFrame(rows)
        csv = df.to_csv(index=False).encode("utf-8")
        st.sidebar.download_button("Download CSV", csv, file_name="detections_log.csv", mime="text/csv")
    else:
        st.sidebar.info("No detections to export yet.")
