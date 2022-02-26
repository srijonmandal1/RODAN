import time
import sys

import torch
import cv2
import screeninfo

import pygame
from pygame.locals import *
from pygame_classes import *

import text_to_speech
from pluralize import pluralize

# Model
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')  # or yolov5m, yolov5l, yolov5x, custom

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

screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
# screen = pygame.display.set_mode((width, height))
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


def whitelist_keys(whitelisted, dict):
    return {key: value for key, value in dict.items() if key in whitelisted}


def show_alert(text: str, sound_alert: str, sound: bool = False):
    global alert, time_since_alert
    alert = text
    if alert_level > 1 or sound:
        time_since_alert = time.time()
        text_to_speech.parallel(sound_alert)

alert_level = 1
show_alert("Drive Safe!", "Thank you for using Row Dan! Drive safe!", True)
whitelisted_classes = [
    'person', 'bicycle', 'car', 'motorcycle', 'bus', 'train', 'truck',
]
events = []

cap = cv2.VideoCapture(0)
for _ in range(10):
    _ = cap.read()
while runUi:
    _, frame = cap.read()
    if alert != "Drive Safe!" and not text_to_speech.text_to_speech_running:
        results = whitelist_keys(whitelisted_classes, get_classes_from_results(model(frame)))
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
    for detected, number in results.items():
        if len(events) > 2 and detected in events[-2] and detected not in events[-3]:
            if number == 1:
                show_alert(f"A {detected} is in front of you", f"A {detected} is in front of you", True)
            else:
                show_alert(f"{number} {pluralize(detected)} are in front of you", f"{number} {pluralize(detected)} are in front of you", True)
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
