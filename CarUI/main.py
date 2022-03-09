import time
import sys
import argparse
import queue
import threading

import torch
import cv2
import screeninfo

import pygame
from pygame.locals import *
from pygame_classes import *

import text_to_speech
from pluralize import pluralize


class VideoCapture:
    def __init__(self, name):
        self.cap = cv2.VideoCapture(name)
        self.stop = False
        self.q = queue.Queue()
        t = threading.Thread(target=self._reader)
        t.daemon = True
        t.start()

    # read frames as soon as they are available, keeping only most recent one
    def _reader(self):
        while True:
            ret, frame = self.cap.read()
            if not ret:
                break
            if not self.q.empty():
                try:
                    self.q.get_nowait()  # discard previous (unprocessed) frame
                except queue.Empty:
                    pass
            self.q.put(frame)
            if self.stop:
                break

    def read(self):
        return self.q.get()

    def release(self):
        self.stop = True
        time.sleep(0.1)
        self.cap.release()


parser = argparse.ArgumentParser()
parser.add_argument("--source", help="the source of the video", default="0")

args = parser.parse_args()

# Model
# model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5m, yolov5l, yolov5x, custom
model = torch.hub.load('../../yolov5', 'custom', path='yolov5s.pt', source='local')
lisa_dataset = torch.hub.load('../../yolov5', 'custom', path='../weights/best.pt', source='local')


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

# screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
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
alert_level = 0
medium_font = pygame.font.Font(font_path, 27)
large_font = pygame.font.Font(font_path, 35)
alert = ""
time_since_alert = time.time()


def runUiFalse():
    global runUi
    runUi = False


quit_button = DefaultButton(screen, 10, 10, 100, 50,
                            runUiFalse, medium_font, "Quit")


def show_alert_always(text: str):
    global alert, time_since_alert
    if text:
        label = large_font.render(text, 1, (0, 0, 0))
        width, height = label.get_size()
        screen_width, screen_height = screen.get_size()
        screen.blit(label, (screen_width / 2 - width / 2, screen_height / 2 - height / 2))
        if time.time() - time_since_alert > 10:
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
    if alert_level > 1 or sound:
        time_since_alert = time.time()
        text_to_speech.parallel(sound_alert)


def find_events(events, results):
    audio_message = ""
    msg = ""
    print(results)
    for detected, number in results.items():
        # note
        # if detected == "traffic light":
        #       find the bounding box
        #       then in cropped image, get color of image
        #       alert if red, warning if yellow, and if green do nothing

        print(events[-1])

        if len(events) > 2 and detected in events[-2] and detected not in events[-3]:
            if number == 1:
                audio_message += f"A {detected} is in front of you. "
                msg += f"A {detected} is in front of you. "
            else:
                audio_message += f"{number} {pluralize(detected)} are in front of you. "
                msg += f"{number} {pluralize(detected)} are in front of you. "
    if msg:
        print(msg)
        show_alert(msg, audio_message, True)


alert_level = 1
show_alert("Drive Safe!", "Thank you for using Row Dan! Drive safe!", True)

whitelisted_classes = [
    'person', 'bicycle', 'car', 'motorcycle', 'bus', 'train', 'truck', 'traffic light', 'stop sign',

    'addedLane', 'curveLeft', 'curveRight', 'dip', 'doNotEnter', 'doNotPass',
    'intersection', 'keepRight', 'laneEnds', 'merge', 'noLeftTurn',
    'noRightTurn', 'pedestrianCrossing', 'rampSpeedAdvisory20',
    'rampSpeedAdvisory35', 'rampSpeedAdvisory40', 'rampSpeedAdvisory45',
    'rampSpeedAdvisory50', 'rampSpeedAdvisoryUrdbl', 'rightLaneMustTurn',
    'roundabout', 'school', 'schoolSpeedLimit25', 'signalAhead', 'slow',
    'speedLimit15', 'speedLimit25', 'speedLimit30', 'speedLimit35',
    'speedLimit40', 'speedLimit45', 'speedLimit50', 'speedLimit55',
    'speedLimit65', 'speedLimitUrdbl', 'stop', 'stopAhead', 'thruMergeLeft',
    'thruMergeRight', 'thruTrafficMergeLeft', 'truckSpeedLimit55', 'turnLeft',
    'turnRight', 'yield', 'yieldAhead', 'zoneAhead25', 'zoneAhead45'
]

events = []

if args.source.isnumeric():
    print(f"Using camera {int(args.source)}")
    cap = VideoCapture(int(args.source))
    # Get 10 frames from the camera to warn it up
    for _ in range(10):
        cap.read()
else:
    print(f"Loading video from {args.source}")
    cap = cv2.VideoCapture(args.source)
while runUi:
    if args.source.isnumeric():
        frame = cap.read()
    else:
        ret, frame = cap.read()
        if not ret:
            runUi = False
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('Video Stream', gray_frame)
    cv2.waitKey(1)

    if alert != "Drive Safe!" or not text_to_speech.text_to_speech_running:
        results = whitelist_keys(
            whitelisted_classes, {
                **get_classes_from_results(model(frame)),
                **get_classes_from_results(lisa_dataset(gray_frame))
            }
        )
    else:
        results = {}
    events.append(results)
    print(results)
    pygame.display.update()
    screen.fill(green if alert_level == 1
                else yellow if alert_level == 2
                else red)
    quit_button.draw()
    show_alert_always(alert)

    find_events(events, results)

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

cap.release()
sys.exit()
