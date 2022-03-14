from flask import *
from flask_pymongo import PyMongo
from dotenv import load_dotenv
import os

if "DYNO" not in os.environ:
    load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = (
    os.environ["MONGO_URI"]
    .replace("<username>", os.environ["USERNAME"])
    .replace("<password>", os.environ["PASSWORD"])
)

mongo = PyMongo(app)

agg_result = list(mongo.db.events.aggregate(
    [{ "$group" : {
        "_id" : {
            "date": "$date",
            "event_name": "$event"
        },
         "total": {"$sum" : 1}
        }}
    ]))

print((agg_result[0])['_id'])