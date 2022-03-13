import requests


def adding(number, result, latitude, longitude):
    event = {
        "count": int(number),
        "event": str(result),
        "latitude": latitude,
        "longitude": longitude
    }
    requests.post("http://localhost:5000/api/v1/add-event", json=event)


adding(10, 'cow', 37.658428, -121.876999)
adding(2, 'deer', 37.658428, -121.876999)
