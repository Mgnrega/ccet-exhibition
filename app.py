from flask import Flask , render_template , request , redirect ,flash
from flask_cors import CORS
from PIL import Image
import base64
import re
from io import BytesIO
import numpy as np

import functions

app = Flask(__name__)
CORS(app)

@app.route("/checkuser" , methods=['GET' , 'POST'])
def check_user():
    
    if request.method=='POST':
        name = request.form['name']
        return functions.check_user(name)    

@app.route("/getencodings" , methods=['GET' , 'POST'])
def encodings():
    
    if request.method=='POST':
        name = request.form['name']
        image_data = re.sub('^data:image/.+;base64,', '', request.form['imageBase64'])
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image = np.array(image)

        return functions.get_encodings(image, name)

@app.route("/retrain" , methods=['GET' , 'POST'])
def retrain():
    
    if request.method=='POST':
        functions.retrain()   

@app.route("/recognize" , methods=['GET' , 'POST'])
def recognize():
    
    if request.method=='POST':
        image_data = re.sub('^data:image/.+;base64,', '', request.form['imageBase64'])
        image = Image.open(BytesIO(base64.b64decode(image_data)))
        image = np.array(image)

        return functions.recognize_image(image)






    