import socket
import json
import time

serverMACAddress = '4C:1D:96:A4:F8:7A'
port = 5
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.connect((serverMACAddress, port))
events = []
while 1:
    event = input("Event: ")
    event_type = input("Event Type: ")  # Event type, update
    update_event = {"type": event_type}
    if event_type == "update":
        to_update = events[0]
        events[0] = {"event": event, "time": time.time()}
    if event == "quit":
        break
    event_json = json.dumps({"event": event, "time": time.time(), **update_event})
    if event_type != "update":
        events.append({"event": event, "time": time.time(), **update_event})
    s.send(bytes(event_json, 'UTF-8'))
s.close()
