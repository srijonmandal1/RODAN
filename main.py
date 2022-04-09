import threading
import time
import sys
import argparse
import socket
import json
import multiprocessing
import atexit

import serial
import pytesseract
import torch
import cv2
import screeninfo

import pygame
from pygame.locals import *
from pygame_classes import *

import text_to_speech
from pluralize import pluralize
from helper_classes import ThreadedVideoCapture
from whitelisted_classes import whitelisted_classes


parser = argparse.ArgumentParser()
parser.add_argument("--source", help="the source of the video", default="0")
parser.add_argument("--prod", help="production or not", action="store_true")

args = parser.parse_args()
# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5m, yolov5l, yolov5x, custom
model = torch.hub.load("../yolov5", "custom", path="yolov5_weights/yolov5s.pt", source="local")
lisa_dataset = torch.hub.load(
    "../yolov5", "custom", path="yolov5_weights/trafficsigns.pt", source="local"
)
fire_model = torch.hub.load(
    "../yolov5", "custom", path="yolov5_weights/fires.pt", source="local"
)

# ONLY SHOW SIGNIFICANT CLASSES AND REDUCE NUMBER OF TIMES ALERTS ARE SHOWN
# Add more..
significant_classes = [
    "fire",
    "person",
    "pedestrian",
    "car",
    "train",
    "traffic light",
    "stop",
    "stop sign",
    "pedestrianCrossing",
    "close_distance",
]

ser = serial.Serial("/dev/serial0", 115200, timeout=0)


def read_tfluna_data():
    while True:
        counter = ser.in_waiting  # count the number of bytes of the serial port
        if counter > 8:
            bytes_serial = ser.read(9)  # read 9 bytes
            ser.reset_input_buffer()  # reset buffer

            if (
                bytes_serial[0] == 0x59 and bytes_serial[1] == 0x59
            ):  # check first two bytes
                distance = (
                    bytes_serial[2] + bytes_serial[3] * 256
                )  # distance in next two bytes
                strength = (
                    bytes_serial[4] + bytes_serial[5] * 256
                )  # signal strength in next two bytes
                temperature = (
                    bytes_serial[6] + bytes_serial[7] * 256
                )  # temp in next two bytes
                temperature = (temperature / 8.0) - 256.0  # temp scaling and offset
                return distance / 100.0, strength, temperature


if not ser.isOpen():
    ser.open()


HOST = "localhost"
PORT = 6026

communication_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
communication_socket.connect((HOST, PORT))


def wait_for_first_communication():
    global phone_connected
    communication_socket.recv(1024)
    phone_connected = True


threading.Thread(target=wait_for_first_communication).start()


def get_classes_from_results(results):
    classes_detected = {}
    pred = results.pred[0]

    if pred.shape[0]:
        for c in pred[:, -1].unique():
            n = (pred[:, -1] == c).sum()  # detections per class
            classes_detected[results.names[int(c)]] = int(n)

    return classes_detected


pygame.init()
monitor_info = screeninfo.get_monitors()[0]
width = monitor_info.width
height = monitor_info.height

if args.prod:
    screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
else:
    screen = pygame.display.set_mode((width, height))
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
font_path = "Segoe-UI-Variable-Static-Display.ttf"


pygame.display.update()

runUi = True
# 1 - green
# 2 - yellow
# 3 - red
alert_level = 1
medium_font = pygame.font.Font(font_path, 27)
large_font = pygame.font.Font(font_path, 35)
alert = ""
time_since_alert = time.time()


def runUiFalse():
    global runUi
    runUi = False


quit_button = DefaultButton(screen, 10, 10, 100, 50, runUiFalse, medium_font, "Quit")


def show_text(text: str):
    global alert, time_since_alert
    if text:
        label = large_font.render(text, 1, (0, 0, 0))
        width, height = label.get_size()
        screen_width, screen_height = screen.get_size()
        screen.blit(
            label, (screen_width / 2 - width / 2, screen_height / 2 - height / 2)
        )
        pygame.display.update()
        if time_since_alert is not None and time.time() - time_since_alert > 10:
            alert = ""
            time_since_alert = None


def whitelist_keys(whitelisted, detected):
    # return {key: value for key, value in detected.items() if key in whitelisted}
    new_detected = {key: value for key, value in detected.items() if key in whitelisted}
    for key, value in detected.items():
        if key not in new_detected:
            print(f"{value} {key} have not been whitelisted")

    return new_detected


def show_alert(text: str, sound_alert: str, sound: bool = False):
    global alert, time_since_alert
    alert = text
    if alert_level >= 1 or sound:
        time_since_alert = time.time()
        text_to_speech.parallel(sound_alert)


def find_events(events, results):
    found = False
    audio_msg = ""
    msg = ""

    if "person" in results:
        events[-1]["pedestrian"] = events[-1]["person"]
        del events[-1]["person"]

    if "car" in results and results["car"] >= 5:
        events[-1]["heavy traffic"] = 1
        del events[-1]["car"]

    if "stop" in results and "stop sign" not in results:
        events[-1]["stop sign"] = events[-1]["stop"]
        del events[-1]["stop"]
    elif "stop" in results:
        del events[-1]["stop"]

    for detected, number in results.items():
        # note
        # if detected == "traffic light":
        #       find the bounding box
        #       then in cropped image, get color of image
        #       alert if red, warning if yellow, and if green do nothing

        send_to_bluetooth = True

        this_msg, this_audio_msg = send_events_and_process(
            detected, number, send_to_bluetooth
        )

        if this_msg is not None:
            if detected == "stop sign":
                this_msg = (
                    this_audio_msg
                ) = "There is a stop sign so remember to slow down!"
            elif detected == "heavy traffic":
                this_msg = (
                    this_audio_msg
                ) = "There seems to be heavy traffic ahead. Slow Down!"
            elif detected == "pedestrian" or detected == "pedestrianCrossing":
                this_msg = this_audio_msg = "Watch out! Pedestrians may be crossing."
            elif detected == "fire":
                this_msg = this_audio_msg = "Be careful! There is a fire."
            elif detected == "close_distance":
                this_msg = (
                    this_audio_msg
                ) = "Be careful. There is an object near your car."
            msg += this_msg
            audio_msg += this_audio_msg

    if msg:
        found = True
        print(msg)
        if detected in significant_classes:
            show_alert(msg, audio_msg, True)

    return found


def send_events_and_process(detected, number, send_to_bluetooth=True):
    to_return = (None, None)
    event_to_send_to_process = []

    if len(events) > 2 and detected not in events[-2]:
        event_to_send_to_process.append({"event": detected, "count": number})
        if number == 1:
            to_return = (f"A {detected} is ahead. ", f"A {detected} is ahead.")
        else:
            to_return = (
                f"{number} {pluralize(detected)} are ahead. ",
                f"{number} {pluralize(detected)} are ahead.",
            )
        if send_to_bluetooth:
            communication_socket.send(json.dumps(event_to_send_to_process).encode())

    return to_return


# coco128_queue = multiprocessing.Queue()
# lisa_queue = multiprocessing.Queue()
# fire_queue = multiprocessing.Queue()
# coco128_return_queue = multiprocessing.Queue()
# lisa_return_queue = multiprocessing.Queue()
# fire_return_queue = multiprocessing.Queue()


# def ml_inference_wrap(model_path, queue, return_queue):
#     import torch

#     model = torch.hub.load(
#         "../yolov5", "custom", path=model_path, source="local"
#     )



#     while True:

#         frame = queue.get()


#         func_output = model(frame)


#         classes_detected = {}
#         pred = func_output.pred[0]

#         if pred.shape[0]:
#             for c in pred[:, -1].unique():
#                 n = (pred[:, -1] == c).sum()  # detections per class
#                 classes_detected[func_output.names[int(c)]] = int(n)


#         print(classes_detected)

#         return_queue.put(classes_detected)


# coco128_model_process = multiprocessing.Process(target=ml_inference_wrap, args=("yolov5_weights/yolov5s.pt", coco128_queue, coco128_return_queue))
# lisa_model_process = multiprocessing.Process(target=ml_inference_wrap, args=("yolov5_weights/trafficsigns.pt", lisa_queue, lisa_return_queue))
# fire_model_process = multiprocessing.Process(target=ml_inference_wrap, args=("yolov5_weights/fires.pt", fire_queue, fire_return_queue))

# coco128_model_process.start()
# lisa_model_process.start()
# fire_model_process.start()


# def run_cpu_tasks_in_parallel(tasks, args):
#     process_args = []
#     for index, task in enumerate(tasks):
#         process_args.append((task, whitelisted_classes, args[index]))
#     with multiprocessing.Pool(5) as p:
#         output = p.starmap(ml_inference_wrap, process_args)
#     return {
#         key: value
#         for detected in output
#         for key, value in detected.items()
#     }


events = []

sign_cascade = cv2.CascadeClassifier("Speed_limit_classifier.xml")


def interpret_text(recognized_text):
    limits = ["25", "30", "35", "40", "45", "50", "55", "60", "65", "70", "75", "80"]
    recognized_text.upper()
    match = [x for x in limits if x in recognized_text]
    if match:
        match = match[0]
        events.append(match)
        send_events_and_process(f"{match} mph speed zone", 1)
        show_alert(
            f"The speed limit is {match} mph.", f"Slow down to {match} mph.", True
        )
    return match


def check_speed_limit(gray_frame):
    # Scan for speed limits signs
    signs = sign_cascade.detectMultiScale(gray_frame)
    speed_result = None
    for (x, y, w, h) in signs:
        # img = cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
        roi_gray = gray_frame[y : y + h, x : x + w]

        recognized_text = pytesseract.image_to_string(
            roi_gray, config="-c tessedit_char_whitelist=0123456789 --psm 6"
        )
        speed_result = interpret_text(recognized_text)
    return speed_result


cap = None


def end_program():
    communication_socket.send("end".encode())
    communication_socket.close()
    if cap is not None:
        cap.release()
    ser.close()


atexit.register(end_program)


phone_connected = False

show_alert(
    "Waiting for the phone to be connected to RODAN",
    "Please connect your phone to Row Dan",
)
while not phone_connected and runUi:
    pygame.display.update()
    screen.fill(green if alert_level == 1 else yellow if alert_level == 2 else red)
    quit_button.draw()

    show_text("Waiting for the phone to be connected to RODAN")

    for event in pygame.event.get():
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            pos = event.pos
            quit_button.check_click(*pos)
            sys.exit()
        elif event.type in [pygame.FINGERDOWN, pygame.FINGERUP]:
            pos = (event.x * screen.get_width(), event.y * screen.get_height())
            quit_button.check_click(*pos)
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == K_q:
                runUi = False
                sys.exit()

alert_level = 1
show_alert("Drive Safe!", "Thank you for using Row Dan! Drive safe!", True)

if args.source.isnumeric():
    print(f"Using camera {int(args.source)}")
    cap = ThreadedVideoCapture(int(args.source))
    # Get 10 frames from the camera to warn it up
    for _ in range(10):
        cap.read()
else:
    print(f"Loading video from {args.source}")
    cap = cv2.VideoCapture(args.source)


while runUi:
    ret, frame = cap.read()
    if not args.source.isnumeric() and not ret:
        runUi = False
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if not args.prod:
        cv2.imshow("Video Stream", gray_frame)
    cv2.waitKey(1)

    # coco128_queue.put(frame)
    # lisa_queue.put(gray_frame)
    # fire_queue.put(frame)

    if alert != "Drive Safe!" or not text_to_speech.text_to_speech_running:
        # results = whitelist_keys(
        #     whitelisted_classes,
        #     {
        #         **coco128_return_queue.get(),
        #         **lisa_return_queue.get(),
        #         **fire_return_queue.get()
        #     }
        # )
        results = whitelist_keys(
            whitelisted_classes,
            {
                **get_classes_from_results(model(frame)),
                **get_classes_from_results(lisa_dataset(gray_frame)),
                **get_classes_from_results(fire_model(frame)),
            },
        )
    else:
        results = {}

    distance, strength, temperature = read_tfluna_data()

    if distance < 0.7:
        results["close_distance"] = 1
    events.append(results)

    distance_display = medium_font.render(f"An object is: {distance} m away",True,blue)

    item_detected = find_events(events, results)

    if not item_detected:
        speed_output = check_speed_limit(gray_frame)

    speed_display = medium_font.render(f"Speed Limit: {speed_output}",True,blue)

    screen.blit(distance_display, (300, 100))
    screen.blit(speed_display, (300, 200))

    pygame.display.update()
    screen.fill(green if alert_level == 1 else yellow if alert_level == 2 else red)
    quit_button.draw()
    show_text(alert)

    for event in pygame.event.get():
        if event.type in [pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONUP]:
            pos = event.pos
            quit_button.check_click(*pos)
        elif event.type in [pygame.FINGERDOWN, pygame.FINGERUP]:
            pos = (event.x * screen.get_width(), event.y * screen.get_height())
            quit_button.check_click(*pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == K_q:
                runUi = False
    if len(events) > 200:
        events = events[:-2]


cv2.destroyAllWindows()
