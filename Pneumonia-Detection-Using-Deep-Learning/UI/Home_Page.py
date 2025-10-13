import streamlit as st
import numpy as np
import pandas as pd
from PIL import Image, UnidentifiedImageError
import textwrap
import sys, cv2
import pydicom


sys.path.insert(0, "../")  # keep folder structure intact
from Models.Predict import load_basic_cnn, load_fine_tuned_cnn, load_densenet121, load_mobilenetv2, load_resnet50, load_yolov5, predict_image, load_file_as_pil, predict_with_yolo
from Models.inference_yolo import load_yolo_model, predict_yolo_image
from Utils.label_utils import normalize_label

yolo_repo_path = r"D:\Great Lakes\Case-Study\Case-Study\Capstone_Project\yolov5"
weights_path = r"D:\Great Lakes\Case-Study\Case-Study\Capstone_Project\Saved_Models\yolov5_best.pt"


import warnings
warnings.filterwarnings("ignore", category=FutureWarning)

# -----------------------------
# Streamlit Config
# -----------------------------
st.set_page_config(page_title="Pneumonia Detection", layout="wide")

# -----------------------------
# Initialize Session State
# -----------------------------
if "results_df" not in st.session_state:
    st.session_state.results_df = pd.DataFrame(
        columns=["Image Name", "Model Name", "Threshold", "Probability", "Actual Result", "Predicted Result", "Feedback"]
    )

if "uploader_key" not in st.session_state:
    st.session_state.uploader_key = 0

if "current_prediction" not in st.session_state:
    st.session_state.current_prediction = None

# -----------------------------
# Title
# -----------------------------
st.markdown(
    "<h1 style='text-align: center; color: #2C3E50;'>🩺 Pneumonia Detection System</h1>",
    unsafe_allow_html=True
)

# # -----------------------------
# # Upload + Model Selection
# # -----------------------------
# col_left, col_right = st.columns(2)
# model = None

# with col_left:
#     model_choice = st.selectbox("Select Model", ["Basic CNN Model", "Fine-Tuned CNN Model", "ResNet50", "MobileNetV2", "YOLOv5"])
    
#     if model_choice == "Basic CNN Model":
#         model = load_basic_cnn()
        
#     elif model_choice == "Fine-Tuned CNN Model":
#         model = load_fine_tuned_cnn()
        
#     elif model_choice == "ResNet50":
#         model = load_resnet50()
        
#     elif model_choice == "MobileNetV2":
#         model = load_mobilenetv2()
        
#     elif model_choice == "DenseNet121":
#         model = load_densenet121()
        
#     elif model_choice == "YOLOv5":
#         model = load_yolov5()
        
#     # else:
#     #     model = load_mobilenet()

# -----------------------------
# Upload + Model Selection
# -----------------------------
col_left, col_right = st.columns(2)

selected_model = None
is_yolo = False   # flag to distinguish YOLO vs CNN

with col_left:
    model_choice = st.selectbox(
        "Select Model", 
        ["Basic CNN Model", "Fine-Tuned CNN Model", "ResNet50", "MobileNetV2", "DenseNet121", "YOLOv5"]
    )
    
    if model_choice == "Basic CNN Model":
        selected_model = load_basic_cnn()
    elif model_choice == "Fine-Tuned CNN Model":
        selected_model = load_fine_tuned_cnn()
    elif model_choice == "ResNet50":
        selected_model = load_resnet50()
    elif model_choice == "MobileNetV2":
        selected_model = load_mobilenetv2()
    elif model_choice == "DenseNet121":
        selected_model = load_densenet121()
    elif model_choice == "YOLOv5":
        selected_model = load_yolov5()
        is_yolo = True

with col_right:
    uploaded_file = st.file_uploader(
        "Upload Chest X-Ray Image",
        type=["jpg", "png", "jpeg", "dcm"],
        key=f"uploader_{st.session_state.uploader_key}"
    )

# Threshold slider
threshold = st.slider(
    "🔧 Set Prediction Threshold",
    min_value=0.1,
    max_value=0.9,
    value=0.5,
    step=0.01,
    help="Adjust sensitivity: Lower threshold = more pneumonia cases detected, Higher threshold = fewer false alarms."
)

# -----------------------------
# Predict & Reset Buttons
# -----------------------------
col1, col2 = st.columns(2)

# Reset button
with col2:
    if st.button("🔄 Reset Page", width='stretch'):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()

# Predict button
# with col1:
#     if st.button("🔍 Predict", width='stretch'):
#         if uploaded_file is None:
#             st.warning("⚠️ Please upload an image first.")
#         else:
#             # Extract image name safely
#             image_name = uploaded_file.name if hasattr(uploaded_file, "name") else "uploaded_image"

#             # Load as PIL.Image
#             image = load_file_as_pil(uploaded_file)
#             if image is None:
#                 st.error("⚠️ Could not read uploaded image.")
#             else:
#                 # -----------------------------
#                 # Run prediction
#                 # -----------------------------
#                 if model_choice == "YOLOv5":
#                     try:
#                         # Load YOLO model (once)
#                         yolo_model = load_yolo_model(yolo_repo_path, weights_path)

#                         # Inference
#                         annotated_img, prediction, prob = predict_yolo_image(yolo_model, image, threshold)
#                         display_img = annotated_img
#                     except Exception as e:
#                         st.error(f"⚠️ YOLOv5 Prediction failed: {e}")
#                         prediction = "Error"
#                         prob = 0.0
#                         display_img = image
#                 else:
#                     # CNN models
#                     prediction, prob = predict_image(model_choice, selected_model , image, threshold)
#                     display_img = image

#                 # -----------------------------
#                 # Store results in session
#                 # -----------------------------
#                 st.session_state["current_prediction"] = {
#                     "image_name": image_name,
#                     "prediction": prediction,
#                     "threshold": threshold,
#                     "image": display_img,
#                     "probability": prob,
#                 }

#                 # -----------------------------
#                 # Display results
#                 # -----------------------------
#                 st.success(f"✅ Prediction: **{prediction}** (Threshold: {threshold}) (Prob: {prob:.2f})")
#                 st.image(display_img, caption=f"Prediction: {prediction} | Probability: {prob:.2f}", width='stretch')

#                 # -----------------------------
#                 # Reset uploader for next image
#                 # -----------------------------
#                 st.session_state.uploader_key += 1
#                 st.rerun()

with col1:
    if st.button("🔍 Predict", width='stretch'):
        if uploaded_file is None:
            st.warning("⚠️ Please upload an image first.")
        else:
            # Extract image name safely
            image_name = uploaded_file.name if hasattr(uploaded_file, "name") else "uploaded_image"

            # Load as PIL.Image
            image = load_file_as_pil(uploaded_file)
            if image is None:
                st.error("⚠️ Could not read uploaded image.")
            else:
                # -------------------------------
                # Run Prediction
                # -------------------------------
                if model_choice == "YOLOv5":
                        # try:
                        # Load YOLOv5 once
                        yolo_model = load_yolo_model(yolo_repo_path, weights_path)
                        
                        # Convert PIL to np.ndarray (BGR) for YOLO
                        image_np = np.array(image)[:, :, ::-1].copy()  # RGB -> BGR

                        # Run inference
                        results = yolo_model(image_np)

                        # Extract boxes, confidences, classes
                        boxes = results.xyxy[0].cpu().numpy()
                        detected = False
                        max_conf = 0.0

                        for box in boxes:
                            x1, y1, x2, y2, conf, cls = box
                            max_conf = max(max_conf, conf)  # Track max confidence for any box
                            if conf >= threshold:
                                detected = True
                                # max_conf = max(max_conf, conf)
                                # Draw bounding box
                                cv2.rectangle(image_np, (int(x1), int(y1)), (int(x2), int(y2)), (0,0,255), 2)
                                cv2.putText(image_np, f"Pneumonia {conf:.2f}", (int(x1), int(y1)-10),
                                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255), 2)

                        # Convert back to PIL
                        annotated_img = Image.fromarray(image_np[:, :, ::-1])  # BGR -> RGB

                        # Prepare prediction label
                        prediction = "Pneumonia" if detected else "Normal"
                        raw_prob = max_conf
                        display_img = annotated_img
                    # # try:
                    #     # Load YOLO model once
                    #     yolo_model = load_yolo_model(yolo_repo_path, weights_path)
                        
                    #     # Inference
                    #     annotated_img, prediction, raw_prob = predict_yolo_image(
                    #         yolo_model,
                    #         image,       # PIL image from uploader
                    #         threshold    # confidence threshold from slider
                    #     )
                    #     display_img = annotated_img

                    # # except Exception as e:
                    # #     st.error(f"⚠️ YOLOv5 Prediction failed: {e}")
                    # #     prediction = "Error"
                    # #     raw_prob = 0.0
                    # #     display_img = image
                else:
                    prediction, raw_prob = predict_image(model_choice, selected_model, image, threshold)
                    display_img = image


                # -------------------------------
                # Store in Session
                # -------------------------------
                st.session_state["current_prediction"] = {
                    "image_name": image_name,
                    "prediction": prediction,
                    "threshold": threshold,
                    "image": display_img,
                    "probability": raw_prob,
                }

                # -------------------------------
                # Display Results
                # -------------------------------
                st.success(f"✅ Prediction: **{prediction}** (Threshold: {threshold}) (Prob: {raw_prob:.2f})")
                st.image(display_img, caption=f"Prediction: {prediction} | Probability: {raw_prob:.2f}", width='stretch')
                
                # Reset uploader
                st.session_state.uploader_key += 1
                st.rerun()


# # -----------------------------
# # Predict & Reset Buttons
# # -----------------------------
# col1, col2 = st.columns(2)

# with col2:
#     if st.button("🔄 Reset Page", width='stretch'):
#         for key in list(st.session_state.keys()):
#             del st.session_state[key]
#         st.rerun()

# with col1:
#     if st.button("🔍 Predict", width='stretch'):
#         if uploaded_file is None:
#             st.warning("⚠️ Please upload an image first.")
#         else:
#             # Extract image name safely
#             image_name = uploaded_file.name if hasattr(uploaded_file, "name") else "uploaded_image"

#             # Load as PIL.Image
#             image = load_file_as_pil(uploaded_file)
#             if image is None:
#                 st.error("⚠️ Could not read uploaded image.")
#             else:
#                 # Run prediction
#                 # prediction, raw_prob = predict_image(model_choice, model, image, threshold)
#                 # if model_choice == "YOLOv5":
#                 #     # prediction, raw_prob, annotated_img = predict_with_yolo(model, image, threshold)
#                 #     # display_img = annotated_img
#                 #     try:
#                 #         prediction, raw_prob, annotated_img = predict_with_yolo(model, image, threshold)
#                 #         display_img = annotated_img
                        
#                 #     except Exception as e:
#                 #         st.error(f"⚠️ YOLOv5 Prediction failed: {e}")
#                 #         display_img = image
#                 # else:
#                 #     prediction, raw_prob = predict_image(model_choice, model, image, threshold)
#                 #     display_img = image
                
#                 if model_choice == "YOLOv5":
#                     try:
#                         # prediction, raw_prob, annotated_img = predict_with_yolo(model, image, threshold)
                        
#                         # load once
#                         yolo_model = load_yolo_model(yolo_repo_path, weights_path)
                        
#                         # inference
#                         annotated_img, prediction, prob = predict_yolo_image(yolo_model, image, threshold)
#                         display_img = annotated_img
#                     except Exception as e:
#                         st.error(f"⚠️ YOLOv5 Prediction failed: {e}")
#                         prediction = "Error"
#                         raw_prob = 0.0
#                         display_img = image
#                 else:
#                     prediction, raw_prob = predict_image(model_choice, model, image, threshold)
#                     display_img = image



#                 # Store in session
#                 st.session_state["current_prediction"] = {
#                     "image_name": image_name,
#                     "prediction": prediction,
#                     "threshold": threshold,
#                     "image": display_img, # image,
#                     "probability": raw_prob,
#                 }

#                 st.success(f"✅ Prediction: **{prediction}** (Threshold: {threshold}) (Prob: {raw_prob:.2f})")

#                 # Show the annotated or normal image
#                 # st.image(
#                 #     display_img,
#                 #     caption=f"Prediction: {prediction} | Probability: {raw_prob:.2f}",
#                 #     width='stretch'
#                 # )
                
#                 predictions, annotated = predict_with_yolo(model, uploaded_file.name)

#                 # Show annotated image
#                 st.image(annotated, caption="YOLOv5 Detection Results", width='stretch')

#                 # Show prediction details
#                 for p in predictions:
#                     st.write(f"Class: {p['class']}, Confidence: {p['confidence']:.2f}")

#                 # Reset uploader
#                 st.session_state.uploader_key += 1
#                 st.rerun()

# -----------------------------
# Load CSV Class Info
# -----------------------------
data_dir = r"D:\Great Lakes\Case-Study\Case-Study\Capstone_Project\Data\stage_2_detailed_class_info.csv"
class_info_df = pd.read_csv(data_dir)
class_info_df = class_info_df.drop_duplicates(subset=["patientId", "class"])

# Map patientId → simplified class
patient_class_map = {}
for pid, cls in zip(class_info_df["patientId"], class_info_df["class"]):
    if cls == "Normal":
        patient_class_map[pid] = "Normal"
        
    elif cls in ["Pneumonia", "Lung Opacity"]:
        patient_class_map[pid] = "Pneumonia"
        
    else:
        # Treat "Abnormal but not Pneumonia" as Normal for training
        patient_class_map[pid] = "Normal"
        # patient_class_map[pid] = "Normal (Abnormal)"
        
    # elif cls in ["Not Normal", "No Lung Opacity", "No Lung Opacity / Not Normal", "Abnormal"]:
    #     patient_class_map[pid] = "No Lung Opacity / Not Normal"
    # else:
    #     patient_class_map[pid] = "Pneumonia"

# CSV → user-friendly label + color
csv_to_radio_map = {
    "Normal": ("Normal", "#05BA50"),
    "Pneumonia": ("Pneumonia (Lung Opacity)", "#E74C3C"),
    "Normal (Abnormal)": ("Abnormal (not Pneumonia)", "#F39C12")
}

# -----------------------------
# Show Prediction if available
# -----------------------------
if st.session_state.get("current_prediction") is not None:
    pred = st.session_state["current_prediction"]
    print("\npred: ", pred)
    if pred["prediction"] == "Normal":
        pred["prediction"] = "Not Pneumonia"
    print("prediction after: ", pred["prediction"])
        
    # normalized_prediction = "Not Pneumonia" if pred["prediction"] == "Normal" else "Pneumonia"
    # print("prediction after: ", normalized_prediction)
    # print("prediction after: ", normalized_prediction["prediction"])
    

    # Extract patientId from uploaded file name
    patient_id = pred["image_name"].split(".")[0]
    csv_class_raw = patient_class_map.get(patient_id)  # None if not in CSV
    actual_class_from_csv, badge_color = csv_to_radio_map.get(csv_class_raw, ("N/A", "#95A5A6"))

    # Layout: Image + Prediction Card
    col1, col2 = st.columns([1, 1])
    with col1:
        st.image(pred["image"], caption=f"Uploaded Image ({pred['image_name']})", width="stretch")

    with col2:
        st.markdown(
            f"""
            <div style='
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100%;
                min-height: 300px;  /* ensures some minimum height */
            '>
                <div style='
                    border:2px solid {"green" if pred["prediction"]=="Not Pneumonia" else "red"};
                    padding:15px;
                    border-radius:10px;
                    text-align:center;
                    background-color:{"#d4edda" if pred["prediction"]=="Not Pneumonia" else "#f8d7da"};
                    color:{"green" if pred["prediction"]=="Not Pneumonia" else "red"};
                    font-weight:bold;
                    font-size:22px;
                    width: 80%;
                '>
                    { f"✅ Not Pneumonia <br/> Probability: {pred['probability']:.2f}" if pred["prediction"]=="Not Pneumonia" else f"🚨 Pneumonia Detected <br/> Probability: {pred['probability']:.2f}" }
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

    # -----------------------------
    # CSV Class Display
    # -----------------------------
    st.markdown(
        f"<b>CSV Class: </b> <span style='color:{badge_color}'>{actual_class_from_csv}</span>",
        unsafe_allow_html=True
    )

    # -----------------------------
    # Enter Actual Result (radio)
    # -----------------------------
    options = ["Not Pneumonia", "Pneumonia"]
    # options = ["Normal", "Pneumonia (Lung Opacity)", "Abnormal (not Pneumonia)"]
    # Define mapping dictionary → background normalized values
    map_dict = {
        "Not Pneumonia": "Not Pneumonia",
        # "Normal": "Normal",
        "Pneumonia": "Pneumonia",
        # "Pneumonia (Lung Opacity)": "Pneumonia",
        # "Abnormal (not Pneumonia)": "Normal (Abnormal)"
        # "Abnormal (not Pneumonia)": "Normal"
    }

    
    # Show radio buttons with original labels
    actual_result_display = st.radio(
        "Enter Actual Result:",
        options,
        index=options.index(actual_class_from_csv) if actual_class_from_csv in options else 0,
        horizontal=True,
        key="actual_result_radio"
    )
    
    # Convert to normalized value (background handling)
    actual_result = map_dict[actual_result_display]

    # -----------------------------
    # Feedback (radio)
    # -----------------------------
    feedback = st.radio(
        "Is the prediction correct? (Note: User opinion, does NOT affect accuracy)",
        ["Yes", "No"],
        horizontal=True,
        key="feedback_radio"
    )

    # -----------------------------
    # Submit Feedback
    # -----------------------------
    if st.button("✅ Submit Feedback"):
        if actual_result is None:
            st.warning("⚠️ Please select the Actual Result before submitting.")
        elif feedback is None:
            st.warning("⚠️ Please select Yes or No for feedback before submitting.")
        else:
            new_row = {
                "Image Name": pred.get("image_name", "unknown"),
                "Model Name": model_choice,
                "Threshold": pred.get("threshold", 0.5),
                "Probability": pred.get("probability", 0.0),
                "Actual Result": actual_result,
                "Predicted Result": pred.get("prediction", "Unknown"),
                "Feedback": feedback,
            }

            st.session_state.results_df = pd.concat(
                [st.session_state.results_df, pd.DataFrame([new_row])],
                ignore_index=True
            )

            st.success("✅ Feedback recorded & saved in table.")
            st.session_state.current_prediction = None
            st.rerun()

# -----------------------------
# Results Table
# -----------------------------
st.subheader("📊 Results Table")
cols_to_show = ["Image Name", "Model Name", "Threshold", "Probability", "Actual Result", "Predicted Result", "Feedback"]
display_cols = [c for c in cols_to_show if c in st.session_state.results_df.columns]
display_df = st.session_state.results_df[display_cols]

edited_df = st.data_editor(display_df, num_rows="dynamic")

# -----------------------------
# Accuracy Calculation (Actual vs Predicted + User Agreement)
# -----------------------------
if not edited_df.empty:
    st.subheader("📈 Model-wise Accuracy")
    model_groups = edited_df.groupby("Model Name")
    cols = st.columns(len(model_groups))

    for (model, group), col in zip(model_groups, cols):
        print("model, group", model, group)
        
        # Map Abnormal → Normal for evaluation
        preds = group["Predicted Result"].replace({"Normal": "Not Pneumonia"})
        actuals = group["Actual Result"].replace({"Normal": "Not Pneumonia"})

        correct_preds = (preds == actuals).sum()
        total_preds = len(group)
        accuracy = (correct_preds / total_preds) * 100 if total_preds > 0 else 0


        # correct_preds = (group["Predicted Result"] == group["Actual Result"]).sum()
        # total_preds = len(group)
        # accuracy = (correct_preds / total_preds) * 100 if total_preds > 0 else 0

        # User Agreement
        if "Feedback" in group.columns:
            user_agreement_yes = (group["Feedback"] == "Yes").sum()
            total_feedbacks = group["Feedback"].notna().sum()
            user_agreement = (user_agreement_yes / total_feedbacks) * 100 if total_feedbacks > 0 else 0
        else:
            user_agreement = 0

        # Emoji mapping
        acc_emoji = "😎" if accuracy > 79 else "🤓" if accuracy > 65 else "😐" if accuracy > 50 else "☹️"
        ua_emoji  = "😎" if user_agreement > 79 else "🤓" if user_agreement > 65 else "😐" if user_agreement > 50 else "☹️"

        html_block = f"""
        <style>
            .card {{
                border: 2px solid #3498db;
                border-radius: 12px;
                padding: 20px;
                margin: 10px 0;
                background-color: #f9f9f9;
                box-shadow: 2px 2px 8px rgba(0,0,0,0.1);
                text-align: center;
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }}
            .card:hover {{
                transform: scale(1.05);
                box-shadow: 4px 4px 16px rgba(0,0,0,0.2);
            }}
            .badge {{
                display:inline-block;
                padding:8px 18px;
                border-radius:25px;
                background: linear-gradient(135deg, #6a11cb 0%, #2575fc 100%);
                color:#fff;
                font-size:20px;
                font-weight:700;
                box-shadow: 2px 2px 6px rgba(0,0,0,0.2);
                letter-spacing:0.5px;
                margin-bottom:15px;
            }}
        </style>

        <div class="card">
            <div class="badge">{model}</div>
            <p style="font-size:20px; font-weight:bold; color:#34495E; margin:8px 0;">
                Accuracy: {accuracy:.2f}% {acc_emoji}
            </p>
            <p style="font-size:20px; font-weight:bold; color:#34495E; margin:8px 0;">
                User Agreement: {user_agreement:.2f}% {ua_emoji}
            </p>
            <hr style="border:0; border-top:1px solid #ccc; margin:12px auto; width:80%;">
            <p style="font-size:14px; color:#7F8C8D; margin:4px 0;">Based on {total_preds} images</p>
            <p style="font-size:12px; color:#AAB7B8; margin-top:5px;">
                <i>⚠️ User Agreement is based on feedback and does not affect accuracy.</i>
            </p>
        </div>
        """
        col.markdown(textwrap.dedent(html_block), unsafe_allow_html=True)

