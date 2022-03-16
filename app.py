import os
import time
import datetime
from datetime import date

from flask import Flask, request, render_template, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from geopy.geocoders import Nominatim

from pluralize import pluralize


geolocator = Nominatim(user_agent="RODAN")

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
    event_stats = list(
        mongo.db.events.aggregate(
            [
                {
                    "$group": {
                        "_id": {
                            "date": "$date",
                            "event": "$event",
                            "location": "$location",
                        },
                        "total": {"$sum": 1},
                    }
                }
            ]
        )
    )

    return render_template("home.html", agg_result=event_stats)


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
def add_event():
    event = request.json
    if (
        "device-id" in event
        and "event" in event
        and "count" in event
        and "latitude" in event
        and "longitude" in event
    ):
        event = {
            "device-id": event["device-id"],
            "event": event["event"],
            "count": event["count"],
            "latitude": event["latitude"],
            "longitude": event["longitude"],
            "time": time.time(),
            "date": str(date.today()),
            "location": reverse_geocode(
                event["latitude"], event["longitude"], raw=True
            ),
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
            "%-I:%M %-m/%d/%Y"
        )
    )


def reverse_geocode(latitude, longitude, raw=False):
    address = geolocator.reverse(f"{latitude}, {longitude}").address.split(", ")
    if raw:
        return address
    return f"{address[2]}, {address[4]} {address[5]}"


@app.context_processor
def reverse_geocode_jinja_func():
    return dict(reverse_geocode=reverse_geocode)


if __name__ == "__main__":
    app.run(debug=True)
