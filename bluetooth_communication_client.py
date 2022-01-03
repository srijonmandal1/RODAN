import socket
import json

serverMACAddress = '4C:1D:96:A4:F8:7A'
port = 5
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.connect((serverMACAddress,port))
while 1:
    event = input()
    if event == "quit":
        break
    s.send(bytes(json.dumps({"event": event, "time": time.time()}), 'UTF-8'))
s.close()
