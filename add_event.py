import requests

def adding(number,result):
    event = {
        "num": int(number),
        "class": str(result)
    }
    requests.post("http://localhost:5000/api/v1/add-event", json=event)

adding(10,'Cow')

