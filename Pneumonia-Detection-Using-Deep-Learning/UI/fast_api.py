from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from PIL import Image
import io, os
# UI/fast_api.py (snippet)
from Models.inference import load_maskrcnn, predict_and_annotate, DEFAULT_MASK_WEIGHTS

app = FastAPI()

# Dummy prediction function
def predict_image(image: Image.Image):
    # TODO: Replace with your real model
    return "Pneumonia Detected"

@app.post("/predict/")
async def predict(file: UploadFile = File(...)):
    try:
        # Read image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))

        # Predict
        prediction = predict_image(image)

        return JSONResponse(content={
            "filename": file.filename,
            "prediction": prediction
        })

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)


# app = FastAPI()

# Load model once at startup (this may take time)
MODEL = None
@app.on_event("startup")
def load_model():
    global MODEL
    MODEL = load_maskrcnn(DEFAULT_MASK_WEIGHTS)

@app.post("/detect")
async def detect(file: UploadFile = File(...), min_confidence: float = 0.5):
    content = await file.read()
    try:
        annotated_bytes, detections = predict_and_annotate(MODEL, content, save_to=None, min_confidence=min_confidence)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    if not detections:
        # Return JSON + original image if you prefer
        return JSONResponse({"message": "No Pneumonia detected", "detections": []})

    # Return annotated image PNG
    return StreamingResponse(io.BytesIO(annotated_bytes), media_type="image/png")
