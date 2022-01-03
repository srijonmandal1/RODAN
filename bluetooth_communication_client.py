import socket
import json
import time

serverMACAddress = '4C:1D:96:A4:F8:7A'
port = 5
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.connect((serverMACAddress, port))
while 1:
    event = input()
    if event == "quit":
        break
    event_json = json.dumps({"event": event, "time": time.time()})
    s.send(bytes(event_json, 'UTF-8'))
s.close()
