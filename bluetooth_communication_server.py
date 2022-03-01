import socket
import json

hostMACAddress = 'e4:5f:01:5e:90:a2'  # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
port = 5
backlog = 1
size = 1024
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.bind((hostMACAddress, port))
s.listen(backlog)
try:
    client, address = s.accept()
    while True:
        data = client.recv(size)
        if data:
            data = json.loads(data)
            print(f"Event: {data['event']}, Time: {data['time']}")
except Exception as e:
    print(e)
    print("Closing socket")
    client.close()
    s.close()
