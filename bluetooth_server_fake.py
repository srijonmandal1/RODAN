import json
import socket
import time
import requests

HOST = "0.0.0.0"
PORT = 6011

# SERVER_URL = "https://rodan-das.herokuapp.com/api/v1/add-event"
SERVER_URL = "http://localhost:5000/api/v1/add-event"


def get_connections():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        print("Connected by", addr)
        time.sleep(1)
        conn.send(b"Connected")
        with conn:
            while True:
                try:
                    received = conn.recv(1024).decode()
                    try:
                        events = json.loads(received)
                        for event in events:
                            print(event)
                            data = (json.dumps(event) + "\r\n").encode()
                            print(f"sending {data}")
                            requests.post(SERVER_URL, json={
                                **data,
                                "device-id": "RND1",
                                "latitude": 37.6604,
                                "longitude": -121.8758
                            })
                    except json.JSONDecodeError:
                        print(f"Unable to decode {received}")
                except IOError:
                    print("An IOError was raised")
                except KeyboardInterrupt:
                    break

    print("disconnected")

    print("all done")


get_connections()
