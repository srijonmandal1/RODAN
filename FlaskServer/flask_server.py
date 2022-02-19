import os
from flask import *
from dotenv import load_dotenv
from flask_session import Session
from flask_pymongo import PyMongo
from flask_minify import minify
import rcssmin
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ["MONGO_URI"].replace("<username>", os.environ["USERNAME"]).replace("<password>", os.environ["PASSWORD"])

minify(app=app, html=True, js=True, cssless=True, static=True)


css_map = {"static/css/theme.css": "static/css/theme.min.css"}

def minify_css(css_map):
    for source, dest in css_map.items():
        with open(source, "r") as infile:
            with open(dest, "w") as outfile:
                outfile.write(rcssmin.cssmin(infile.read()))

mongo = PyMongo(app)
Session(app)



@app.route('/')
def about():
    return render_template('index.html')


if __name__ == '__main__':
    minify_css(css_map)
    app.run(host="0.0.0.0", debug=True)