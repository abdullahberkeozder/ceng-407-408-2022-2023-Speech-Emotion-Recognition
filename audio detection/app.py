from flask import Flask, render_template, request
from keras.models import load_model
from keras.preprocessing import image
from keras.metrics import AUC
import numpy as np
import pandas as pd
import os
import librosa
import librosa, warnings
import numpy as np
import pandas as pd
from sklearn.preprocessing import LabelEncoder
from tensorflow.keras.models import load_model
#import tensorflow as tf
from transformers import TFAutoModel
from scipy.io.wavfile import write
from flask import Flask, redirect, url_for, request, render_template
import numpy as np
import pandas as pd
import time
import os
from collections import Counter
import json
from tensorflow.keras.models import model_from_json
from tensorflow.keras.models import load_model
from transformers import AutoTokenizer,TFBertModel
from transformers import BertModel, BertConfig
import torch
import tensorflow as tf
from transformers import BertModel, BertConfig, TFBertForPreTraining, BertTokenizer, TFBertModel
import h5py
import torch
import transformers
from tensorflow.keras.preprocessing.text import Tokenizer
import speech_recognition as sr
from numpy.linalg import norm

### Flask imports
import requests
from flask import Flask, render_template, session, request, redirect, flash, Response
### Audio imports ###
 
app = Flask(__name__)

final = pd.read_pickle("extracted_df.pkl")
y = np.array(final["Emotions"].tolist())
le = LabelEncoder()
le.fit_transform(y)
Model1_ANN = load_model("Model1.h5")
Model2_BERT = load_model("Model2.h5", custom_objects={"TFBertModel": transformers.TFBertModel})
print(y)

def extract_feature(audio_path):
    audio_data, sample_rate = librosa.load(audio_path, res_type="kaiser_fast")
    feature = librosa.feature.mfcc(y=audio_data, sr=sample_rate, n_mfcc=40)
    feature_scaled = np.mean(feature.T, axis=0)
    return np.array([feature_scaled])

##oran
def ANN_print_prediction(audio_path):
    prediction_feature = extract_feature(audio_path) 
    predicted_vector = Model1_ANN.predict(prediction_feature) * 100 #
    #print(predicted_vector[0][0]) #anger oran
    #print(predicted_vector[0][1]) #excited oran
    #print(predicted_vector[0][2]) #frustration oran
    #print(predicted_vector[0][3]) #happy oran
    #print(predicted_vector[0][4]) #neutral oran
    #print(predicted_vector[0][5]) #sadness oran
    return predicted_vector[0]
    encoded_dict = {'Angry':0, 'Excited': 1, 'Frust': 2,'Happy':3, 'Neutral': 4,'Sad':5}
    #for key, value in zip(encoded_dict.keys(), predicted_vector[0]):
    #    print(key, value)

def speech2text(audio_path):
	recognizer = sr.Recognizer()
	with sr.AudioFile(audio_path) as source:
		recorded_audio = recognizer.listen(source)
		print("Done recording")
	try:
		print("Recognizing the text")
		text = recognizer.recognize_google(
				recorded_audio,
				language="en-US"
			)
		print("Decoded Text : {}".format(text))
		new_text=prepare_text(text)
		return new_text
	except Exception as ex:
		print(ex)

tokenizer = AutoTokenizer.from_pretrained('bert-base-cased')
def prepare_text(texts):
	prepared_text = tokenizer(
		text=texts,
		add_special_tokens=True,
		max_length=39,
		truncation=True,
		padding='max_length',
		return_tensors='tf',
		return_token_type_ids=False,
		return_attention_mask=True,
		verbose=True)
	return prepared_text


def predict_BERT(audio_path):
	prepared_text = speech2text(audio_path)
	prediction = Model2_BERT.predict({'input_ids': prepared_text['input_ids'], 'attention_mask': prepared_text['attention_mask']}) * 100
	# predicted_class = le.inverse_transform([np.argmax(prediction)])
	encoded_dict = {'Other':0, 'Angry': 1, 'Excited': 2,'Otherd':3, 'Sad': 4,'Othder':5, 'Frustration': 6, 'Happy': 7,'Odther':8, 'Neutral': 9}
	for key, value in zip(encoded_dict.keys(), prediction[0]):
		print(key, value)

	sendPrediction = [prediction[0][1], prediction[0][2], prediction[0][4], prediction[0][6], prediction[0][7], prediction[0][9]]
	return sendPrediction

def predict_BERT_text(text):
	prepared_text = prepare_text(text)
	prediction = Model2_BERT.predict({'input_ids': prepared_text['input_ids'], 'attention_mask': prepared_text['attention_mask']}) * 100
	# predicted_class = le.inverse_transform([np.argmax(prediction)])
	encoded_dict = {'Other':0, 'Angry': 1, 'Excited': 2,'Otherd':3, 'Sad': 4,'Othder':5, 'Frustration': 6, 'Happy': 7,'Odther':8, 'Neutral': 9}
	for key, value in zip(encoded_dict.keys(), prediction[0]):
		print(key, value)
	sendPrediction = [prediction[0][1], prediction[0][2], prediction[0][4], prediction[0][6], prediction[0][7], prediction[0][9]]

	return sendPrediction


 # print(predict_BERT("./deneme.wav"))
#print(ANN_print_prediction("./deneme.wav"))


@app.route("/")
@app.route("/first")
def first():
	return render_template('first.html')


@app.route("/login")
def login():
	return render_template('login.html')


@app.route("/faq")
def faq():
	return render_template('faq.html')


@app.route("/main", methods=['GET'])
def main():
	return render_template("main.html")


@app.route("/index", methods=['GET'])
def index():
	return render_template("index.html")


@app.route("/indexs", methods=['GET'])
def indexs():
	return render_template("indexs.html")


@app.route("/text", methods=['GET'])
def text():
	return render_template("text.html")

@app.route("/finalRes", methods=['GET'])
def finalRes():
	return render_template("finalRes.html")


@app.route("/submit", methods = ['GET', 'POST'])
def get_output():
	if request.method == 'POST':
		audio_path = request.files['wavfile']

		img_path = "static/tests/" + audio_path.filename	
		audio_path.save(img_path)
	 
		predict_result1 =  ANN_print_prediction(img_path)
		predict_result2 = predict_BERT(img_path)
		norm_of_text = norm(predict_result2)
		encoded_dict2 = {'Angry': 0, 'Excited': 1, 'Sad': 2, 'Frustration': 3, 'Happy': 4, 'Neutral': 5}
		encoded_dict1 = {'Angry': 0, 'Excited': 1, 'Frustration': 2, 'Happy': 3, 'Neutral': 4, 'Sad': 5}
		for key, value in zip(encoded_dict2.keys(), encoded_dict2.values()):
			if value == np.argmax(predict_result2):
				predict_result2_emo = key

		for key, value in zip(encoded_dict1.keys(), encoded_dict1.values()):
			if value == np.argmax(predict_result1):
				predict_result1_emo = key				
	return render_template("prediction.html", prediction = predict_result1_emo, prediction2 = predict_result2_emo, prediction2Rate = predict_result2[np.argmax(predict_result2)], prediction1Rate=predict_result1[np.argmax(predict_result1)], audio_path= img_path)


@app.route("/submit_text", methods=['GET', 'POST'])
def get_output_text():
	if request.method == 'POST':
		input_text = request.form['input_text']

		prediction = predict_BERT_text(input_text)
		encoded_dict = {'Anger': 0, 'Excited': 1, 'Sadness': 2, 'Frustration': 3, 'Happiness': 4, 'Neutral': 5}
		for key, value in zip(encoded_dict.keys(), encoded_dict.values()):
			if value == np.argmax(prediction):
				predict_result_emo = key

	return render_template("prediction_text.html", prediction=predict_result_emo, predictionRate=prediction[np.argmax(prediction)])



@app.route("/chart")
def chart():
	return render_template('chart.html')
@app.route("/performance")
def performance():
	return render_template('performance.html')       
 
if __name__ =='__main__':
	app.run(debug = True)