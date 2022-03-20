import os
import time
import json
from datetime import date

from flask import Flask, request, render_template, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from flask_socketio import SocketIO, emit
from engineio.payload import Payload

from pluralize import pluralize


geolocator = Nominatim(user_agent="RODAN")
Payload.max_decode_packets = 500

if "DYNO" not in os.environ:
    load_dotenv()

app = Flask(__name__)
app.config["MONGO_URI"] = (
    os.environ["MONGO_URI"]
    .replace("<username>", os.environ["DATABASE_USERNAME"])
    .replace("<password>", os.environ["PASSWORD"])
)

mongo = PyMongo(app)
socketio = SocketIO(app)


@app.route("/")
def home():
    return render_template("home.html", agg_result=get_agg_events(raw=True))


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
    socketio.emit("events", json.dumps(get_agg_events(raw=True)), broadcast=True)
    return {"success": True}


@app.route("/api/v1/get-events")
def get_events():
    return jsonify(
        [{**item, "_id": str(item["_id"])} for item in list(mongo.db.events.find())]
    )


@app.route("/api/v1/get-agg-events")
def get_agg_events(raw=False):
    agg_data = sorted(
        list(
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
        ), key=lambda item: item["_id"]["date"], reverse=True
    )
    if raw:
        return agg_data
    return jsonify(agg_data)


@app.context_processor
def pluralize_jinja():
    return dict(pluralize=pluralize)


def reverse_geocode(latitude, longitude, raw=False):
    address = geolocator.reverse(f"{latitude}, {longitude}").address.split(", ")
    if raw:
        return address
    return f"{address[2]}, {address[4]} {address[5]}"


@app.context_processor
def reverse_geocode_jinja_func():
    return dict(reverse_geocode=reverse_geocode)


@app.context_processor
def format_date():
    def format_date_func(date):
        date = date.split("-")
        return f"{date[1].strip('0')}/{date[2]}/{date[0]}"

    return dict(format_date=format_date_func)


@socketio.on("connect")
def connect():
    pass


@socketio.on("disconnect")
def disconnect():
    pass


if __name__ == "__main__":
    socketio.run(app, debug=True)
