from flask import Flask,url_for,render_template,request
import spacy
activated = spacy.prefer_gpu()
from spacy import displacy
import json
import os
from textblob import TextBlob 

# HTML_WRAPPER for spaCy NER rendering.
HTML_WRAPPER = """<div style="overflow-x: auto; padding: 1rem">{}</div>"""

from flaskext.markdown import Markdown

# Empty model just for rendering text.
nlp_empty =spacy.blank("en")

app = Flask(__name__,static_url_path="",static_folder="img")
Markdown(app)

MODEL_PATH="./pretrained_model/spacy"

# Preset color and tag template for symptoms, drugs and dosage.
adr_ner_colors = {"SYMP": "#9370DB", "DRUG": "#F58B4C", "DOSE": "#B5C689"}
OPTIONS = {"ents": ["SYMP","DRUG","DOSE"], "colors": adr_ner_colors}


# Input is the file directory of the models (hard coded)
# Return a dictionary of pretrained model name and it's path.
def get_models(d):
	result = {}
	for f in os.listdir(d):
		result[f]=os.path.join(d, f)

	# Add 2 spaCy pre-trained model.
	result["en_core_web_sm"]="en_core_web_sm"
	result["en_core_web_md"]="en_core_web_md"

	return(result)

# Function to measure text sentiment.
# Trained on Twitter dataset.
def get_tweet_sentiment(tweet):
    analysis = TextBlob(tweet)
    return(analysis.sentiment.polarity)

import sys
# print(get_models(MODEL_PATH), file=sys.stderr)

# Landing page of the application.
# Require model paths to be load.
@app.route('/',methods=["GET"])
def index():
	model_names = get_models(MODEL_PATH)
	return render_template('index.html', model_names=model_names)

@app.route('/extract',methods=["GET","POST"])
def extract():
	if request.method == 'POST':
		# Initiate model depending on user's choice.
		selected_model = request.form['selected_model']
		nlp = spacy.load(os.path.join(selected_model))

		# Extract and analyse text
		raw_text = request.form['rawtext']
		docx = nlp(raw_text)

		# Disable color scheme for spaCy model.
		if selected_model == "en_core_web_sm" or selected_model == "en_core_web_md":
			html = displacy.render(docx,style="ent")
		else:
			html = displacy.render(docx,style="ent", options=OPTIONS)	

		html = html.replace("\n\n","\n")
		result = HTML_WRAPPER.format(html)

		doc=nlp_empty(raw_text)
		html = displacy.render(doc,style="ent")
		html = html.replace("\n\n","\n")
		raw_text = HTML_WRAPPER.format(html)

	return render_template('result.html',rawtext=raw_text,result=result)

# About page of the application.
# Self-introduction, motivation, summarise.
@app.route('/about')
def about_me():
	return render_template('about.html')

# No idea about these 2 functions. Modify later.
@app.route('/previewer')
def previewer():
	return render_template('previewer.html')

@app.route('/preview',methods=["GET","POST"])
def preview():
	if request.method == 'POST':
		newtext = request.form['newtext']
		result = newtext

	return render_template('preview.html',newtext=newtext,result=result)

if __name__ == '__main__':
	app.run(debug=True)