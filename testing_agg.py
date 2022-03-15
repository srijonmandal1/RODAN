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

# x=list(mongo.db.events.aggregate(
#     { "$group" : {
#         "_id" : {
#             "date": "$date",
#             "event_name": "$event",
#             "city": "$city"
#         },
#          "total": {"$sum" : 1}
#         }}
#     ))
y = list(mongo.db.events.find({}))

print(y)