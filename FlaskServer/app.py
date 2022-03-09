import os
import time

from flask import *
from flask_pymongo import PyMongo
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = os.environ["MONGO_URI"].replace("<username>", os.environ["USERNAME"]).replace("<password>", os.environ["PASSWORD"])


mongo = PyMongo(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/examples")
def examples():
    return render_template("examples.html")


@app.route("/logs")
def page():
    return render_template("logs.html")


@app.route("/buy")
def buy():
    return render_template("buy.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/api/v1/add-event", methods=["POST"])
def add_events():
    event = request.json
    if "event" in event and "count" in event:
        events = {"event": event["event"], "count": event["count"], "time": time.time()}
    else:
        return {"success": False, }
    mongo.db.events.insert_one(event)
    return {"success": True}


@app.route("/api/v1/get-events")
def get_events():
    return jsonify([{**item, "_id": str(item["_id"])} for item in list(mongo.db.events.find())])


if __name__ == "__main__":
    app.run(debug=True)
