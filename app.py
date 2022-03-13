import os
import time
import datetime

from flask import *
from flask_pymongo import PyMongo
from dotenv import load_dotenv

from pluralize import pluralize

if "DYNO" not in os.environ:
    load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = (
    os.environ["MONGO_URI"]
    .replace("<username>", os.environ["USERNAME"])
    .replace("<password>", os.environ["PASSWORD"])
)


mongo = PyMongo(app)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/examples")
def examples():
    return render_template("examples.html")


@app.route("/logs")
def logs():
    return render_template("logs.html", events=list(mongo.db.events.find({})))


@app.route("/buy")
def buy():
    return render_template("buy.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/api/v1/add-event", methods=["POST"])
def add_events():
    event = request.json
    if (
        "event" in event
        and "count" in event
        and "latitude" in event
        and "longitude" in event
        and "device-id" in event
    ):
        event = {
            "event": event["event"],
            "count": event["count"],
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "device-id": event["device-id"],
            "time": time.time(),
        }
    else:
        return {
            "success": False,
            "message": 'Please provide an "event", a "count", a "latitude", and a "longitude"',
        }
    mongo.db.events.insert_one(event)
    return {"success": True}


@app.route("/api/v1/get-events")
def get_events():
    return jsonify(
        [{**item, "_id": str(item["_id"])} for item in list(mongo.db.events.find())]
    )


@app.context_processor
def pluralize_jinja():
    return dict(pluralize=pluralize)


@app.context_processor
def format_date():
    return dict(
        format_date=lambda time: datetime.datetime.fromtimestamp(time).strftime(
            "%-I:%-M %m/%d/%Y"
        )
    )


if __name__ == "__main__":
    app.run(debug=True)
