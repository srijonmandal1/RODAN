import os
from flask import *
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ["MONGO_URI"].replace(
    "<username>", os.environ["USERNAME"]).replace("<password>", os.environ["PASSWORD"])

mongo = PyMongo(app)

mongo.db.events.delete_many({})
