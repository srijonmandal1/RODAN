import bluetooth
import bluetooth_funcs
import json
import socket
import sys

HOST = "0.0.0.0"
PORT = 6015

bluetooth_funcs.make_discoverable()

server_sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
server_sock.bind(("", 0))
server_sock.listen(1)

port = 0

uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

bluetooth.advertise_service(
    server_sock, "RODAN RND Data Sender",
    service_id=uuid,
    service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
    profiles=[bluetooth.SERIAL_PORT_PROFILE],
)


def get_connections():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen(1)
        conn, addr = s.accept()
        print("Connected by", addr)
        print(f"Waiting for connection on RFCOMM channel {port}")
        client_sock, client_info = server_sock.accept()
        print(f"Accepted connection from {client_info}")
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
                            client_sock.send(data)
                    except json.JSONDecodeError:
                        if received == "end":
                            s.close()
                            server_sock.close()
                            print("Stopping the bluetooth server")
                            sys.exit()
                        print(f"Unable to decode {received}")
                except IOError:
                    print("An IOError was raised")
                except KeyboardInterrupt:
                    break

    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("all done")


get_connections()
