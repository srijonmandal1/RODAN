import os
import time
from datetime import date

from flask import Flask, request, render_template, jsonify
from flask_pymongo import PyMongo
from dotenv import load_dotenv
from geopy.geocoders import Nominatim
from flask_socketio import SocketIO
from engineio.payload import Payload
import tweepy

from pluralize import pluralize


geolocator = Nominatim(user_agent="RODAN")
Payload.max_decode_packets = 500

if "DYNO" not in os.environ:
    load_dotenv()

app = Flask(__name__)
app.config.update(
    MONGO_URI=os.environ["MONGO_URI"]
    .replace("<username>", os.environ["DATABASE_USERNAME"])
    .replace("<password>", os.environ["PASSWORD"]),
    BEARER_TOKEN=os.environ["BEARER_TOKEN"],
    API_KEY=os.environ["API_KEY"],
    API_KEY_SECRET=os.environ["API_KEY_SECRET"],
    ACCESS_TOKEN=os.environ["ACCESS_TOKEN"],
    ACCESS_TOKEN_SECRET=os.environ["ACCESS_TOKEN_SECRET"],
)

mongo = PyMongo(app)
socketio = SocketIO(app)

auth = tweepy.Client(
    app.config["BEARER_TOKEN"],
    app.config["API_KEY"],
    app.config["API_KEY_SECRET"],
    app.config["ACCESS_TOKEN"],
    app.config["ACCESS_TOKEN_SECRET"],
)
api = tweepy.API(auth)


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/resources")
def resources():
    return render_template("resources.html")


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
    if {"device-id", "event", "count", "latitude", "longitude"} > set(event):
        return {
            "success": False,
            "message": 'Please provide an "event", a "count", a "latitude", and a "longitude"',
        }
    reverse_geocode_output = reverse_geocode(
        event["latitude"], event["longitude"], raw=True
    )
    event = {
        "device-id": event["device-id"],
        "event": event["event"],
        "count": event["count"],
        "latitude": event["latitude"],
        "longitude": event["longitude"],
        "time": time.time(),
        "date": str(date.today()),
        "location": reverse_geocode_output,
    }
    if event["event"] in ["fire", "accident", "pothole", "oversized vehicle"]:
        starting = "An" if event["event"][0] in ["a", "e", "i", "o", "u"] else "A"
        auth.create_tweet(
            text=f"{starting} {event[event]} was detected at {reverse_geocode_output['street']}, {reverse_geocode_output['town']}, {reverse_geocode_output['state']} {reverse_geocode_output['postcode']}"
        )
    mongo.db.events.insert_one(event)
    socketio.emit("events", get_agg_events(raw=True), broadcast=True)
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
        ),
        key=lambda item: item["_id"]["date"],
        reverse=True,
    )
    if raw:
        return agg_data
    return jsonify(agg_data)


def reverse_geocode(latitude, longitude, raw=False):
    address = geolocator.reverse(f"{latitude}, {longitude}", zoom=18).raw["address"]
    if raw:
        return address
    return f"{address['town']}, {address['state']} {address['postcode']}"


@app.context_processor
def pluralize_jinja():
    return dict(pluralize=pluralize)


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
