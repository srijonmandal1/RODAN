import socket
import json

hostMACAddress = '4C:1D:96:A4:F8:7A'  # The MAC address of a Bluetooth adapter on the server. The server might have multiple Bluetooth adapters.
port = 5
backlog = 1
size = 1024
s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.bind((hostMACAddress, port))
s.listen(backlog)
try:
    client, address = s.accept()
    while 1:
        data = client.recv(size)
        if data:
            data = json.loads(data)
            print(f"Event: {data['event']}, Time: {data['time']}")
            # client.send(data)
except:
    print("Closing socket")
    client.close()
    s.close()
