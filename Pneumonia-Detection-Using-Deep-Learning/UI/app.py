import os
import numpy as np
import pandas as pd
from PIL import Image
import cv2
from flask import Flask,request,render_template
from werkzeug.utils import secure_filename

from tensorflow.keras.models import Model
from tensorflow.keras.layers import Input, Flatten, Dense, Dropout
from tensorflow.keras.applications.vgg19 import VGG19
# from tensorflow.keras.applications import VGG19


base_model = VGG19(include_top = False,input_shape=(128, 128,3))
x = base_model.output

flat = Flatten()(x)

class_1 = Dense(4608, activation = 'relu')(flat)

dropout = Dropout(0.2)(class_1)

class_2 = Dense(1152, activation='relu')(dropout)

output = Dense(2, activation='softmax')(class_2)

# model with empty weights
model_03 = Model(base_model.inputs, output)

# model_03.layers[16] = Dense(4608, input_shape=(8192, 4608))

# Trained model
model_03.load_weights(r"model_weights\vgg19_model_01.h5")



## create Flask app

app = Flask(__name__)

print("Model loaded succesfully.")

# API

# Helper functions

def get_className(classNo):
    if classNo==0:
        return "Normal"
    elif classNo==1:
        return "Pneumonia"


def get_result(img):
    # Read the image
    image = cv2.imread(img)
      
    # convert to RGB
    image = Image.fromarray(image,"RGB")
    
    # Resize the image for model's expected input size
    image = image.resize((128,128))
    
    # convert to numpy array
    image = np.array(image)
    
    # Nomalize the pixels value to (0 to 1)
    image = image/129.0
    
    # Expand dimensions to add the batch size
    input_img = np.expand_dims(image,axis=0)
    
    # Make Predictions
    result = model_03.predict(input_img)
    
    # Get the class index with highest probablity    
    result01 = np.argmax(result,axis=1)
    
    return result01


#  Routes

@app.route("/",methods=["GET"])
def index():
    return render_template("index.html")
    # return "<h1>Pneumonia Detector"

@app.route("/predict",methods=["POST","GET"])
def upload():
    if request.method == "POST":
        try:
            file = request.files['file']

            base_path = os.path.dirname(__file__)
            file_path = os.path.join(
                base_path,"uploads",secure_filename(file.filename)
            )
            
            file.save(file_path) 

            value = get_result(file_path)
            
            result = get_className(value)
            
            return result
        except Exception as e:
            print(f"Error {e}")
            
    return None
    
if __name__ == '__main__':
    app.run(debug=True)