import bluetooth
import bluetooth_funcs
import threading
import json

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


events = []
connected = threading.Event()
wait_for_event = threading.Event()


def get_connections():
    print(f"Waiting for connection on RFCOMM channel {port}")
    client_sock, client_info = server_sock.accept()
    print(f"Accepted connection from {client_info}")
    connected.set()
    while True:
        try:
            wait_for_event.wait()
            wait_for_event.clear()
            for event in events:
                print(event)
                data = (json.dumps(event) + "\r\n").encode()
                print(f"sending {data}")
                client_sock.send(data)
        except IOError:
            print("An IOError was raised")
        except KeyboardInterrupt:
            break

    print("disconnected")

    client_sock.close()
    server_sock.close()
    print("all done")


socket_message_thread = threading.Thread(target=get_connections)
socket_message_thread.daemon = True
socket_message_thread.start()
