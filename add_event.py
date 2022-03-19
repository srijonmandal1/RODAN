import requests
import time
import datetime


def add_event(id, number, result, latitude, longitude, time=time.time(), date=str(datetime.date.today())):
    event = {
        "device-id": id,
        "count": int(number),
        "event": str(result),
        "latitude": latitude,
        "longitude": longitude,
        "time": int(time),
        "date": str(date),
    }
    requests.post("http://localhost:5000/api/v1/add-event", json=event)


add_event('RDN1', 3, 'pedestrian', 37.658428, -121.876999)
add_event('RDN1', 1, 'stop sign', 37.658428, -121.876999)
add_event('RDN1', 1, 'heavy traffic', 37.658428, -121.876999)
