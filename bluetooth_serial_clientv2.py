#!/usr/bin/env python
"""
A simple test server that returns a random number when sent the text "temp" via Bluetooth serial.
"""

import os
import glob
import time
import random

import bluetooth
import make_bluetooth_discoverable

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", 0))
server_sock.listen(1)

port = 0

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

bluetooth.advertise_service(
    server_sock, "TestServer",
    service_id = uuid,
    service_classes = [uuid, bluetooth.SERIAL_PORT_CLASS],
    profiles = [bluetooth.SERIAL_PORT_PROFILE], 
)

print(f"Waiting for connection on RFCOMM channel {port}")
client_sock, client_info = server_sock.accept()
print(f"Accepted connection from {client_info}")

while True:
    try:
        data = '{"event": "deer", "count": 5}\r\n'.encode()
        print(f"sending {data}")
        client_sock.send(data)
        time.sleep(5)
    except IOError:
        pass
    except KeyboardInterrupt:
        print("disconnected")

        client_sock.close()
        server_sock.close()
        print("all done")

        break
