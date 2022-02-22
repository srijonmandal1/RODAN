import requests

event = {
    "num": 7,
    "class": "person"
}

requests.post("http://localhost:5000/api/v1/add-event", json=event)
