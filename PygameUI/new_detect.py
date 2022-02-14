# Import the neccesary libraries
import argparse
import cv2
import time

import pygame
from pygame.locals import *
from pygame_classes import *
import time

import text_to_speech

pygame.init()


screen = pygame.display.set_mode((320, 480), pygame.FULLSCREEN)
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
time_since_alert = None

def runUiFalse():
    global runUi
    for process in text_to_speech.text_to_speech_processes:
        process.terminate()
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


def show_alert(text: str, sound_alert: str, sound: bool = False):
    global alert, time_since_alert
    alert = text
    time_since_alert = time.time()
    if alert_level > 1 or sound:
        text_to_speech.parallel(sound_alert)


with open("log.txt", "w") as f:
    pass


alert_level = 1
show_alert("Drive Safe!", "Thank you for using Row Dan! Drive safe!", True)
x = 0


# construct the argument parse
parser = argparse.ArgumentParser(
    description="Script to run MobileNet-SSD object detection network ")
parser.add_argument(
    "--video", help="path to video file. If empty, camera's stream will be used")
parser.add_argument("--thr", default=0.2, type=float,
                    help="confidence threshold to filter out weak detections")
args = parser.parse_args()


# Labels of Network.
classNames = {0: "background",
              1: "aeroplane", 2: "bicycle", 3: "bird", 4: "boat",
              5: "bottle", 6: "bus", 7: "car", 8: "cat", 9: "chair",
              10: "cow", 11: "diningtable", 12: "dog", 13: "horse",
              14: "motorbike", 15: "person", 16: "pottedplant",
              17: "sheep", 18: "sofa", 19: "train", 20: "tvmonitor"}

# Open video file or capture device.
if args.video:
    cap = cv2.VideoCapture(args.video)
else:
    cap = cv2.VideoCapture(0)

# Load the Caffe model
net = cv2.dnn.readNetFromCaffe("models/MobileNetSSD_deploy.prototxt",
                               "models/MobileNetSSD_deploy.caffemodel")

x = y = 0

while runUi:

    x += 1
    print(x)
    pygame.display.update()
    screen.fill(green if alert_level == 1
                else yellow if alert_level == 2
                else red)
    quit_button.draw()
    show_alert_always(alert)
    for event in pygame.event.get():
        print(x, 1, event.type, pygame.MOUSEBUTTONDOWN, pygame.MOUSEBUTTONDOWN)
        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEBUTTONUP:
            print(x, 2)
            pos = event.pos
            print(pos)
            quit_button.check_click(*pos)
        elif event.type == pygame.FINGERDOWN or event.type == pygame.FINGERUP:
            pos = (event.x * screen.get_width(), event.y * screen.get_height())
            quit_button.check_click(*pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == K_q:
                runUi = False


    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    frame_resized = cv2.resize(frame, (300, 300))

    net.setInput(cv2.dnn.blobFromImage(
        frame_resized, 0.007843, (300, 300), (127.5, 127.5, 127.5), False))
    # Prediction of network
    detections = net.forward()

    # Size of frame resize (300x300)
    rows, cols = frame_resized.shape[0], frame_resized.shape[1]

    for i in range(detections.shape[2]):
        confidence = detections[0, 0, i, 2]  # Confidence of prediction
        if confidence > args.thr:  # Filter prediction
            class_id = int(detections[0, 0, i, 1])  # Class label

            # Object location
            xLeftBottom = int(detections[0, 0, i, 3] * cols)
            yLeftBottom = int(detections[0, 0, i, 4] * rows)
            xRightTop = int(detections[0, 0, i, 5] * cols)
            yRightTop = int(detections[0, 0, i, 6] * rows)

            # Factor for scale to original size of frame
            heightFactor = frame.shape[0]/300.0
            widthFactor = frame.shape[1]/300.0
            # Scale object detection to frame
            xLeftBottom = int(widthFactor * xLeftBottom)
            yLeftBottom = int(heightFactor * yLeftBottom)
            xRightTop = int(widthFactor * xRightTop)
            yRightTop = int(heightFactor * yRightTop)

            # Draw label and confidence of prediction in frame resized
            if class_id in classNames:
                label = classNames[class_id]
                if confidence > 0.7:
                    x += 1

                    with open("log.txt", "r") as f:
                        lines = f.readlines()

                    past_items = [item.split(":")[0] for item in lines[-y:]]
                    if label not in past_items:
                        with open("log.txt", "a") as f:
                            print(f"{label}:{time.time()}", file=f)
                            if label == "tvmonitor":
                                show_alert("Slow Down!", "You are approaching a stop sign.", True)
                            elif label == "pottedplant":
                                show_alert("Chill out!", "You will crash.",True)
                            elif label == "person":
                                show_alert("WATCH OUT!", "You will hurt someone.",True)
                    else:
                        index_of_object = past_items.index(label)
                        with open("log.txt", "r") as f:
                            lines = f.readlines()

                        for index, line in enumerate(lines[::-1]):
                            if line.split(":")[0] == label:
                                break
                        lines[len(lines) - 1 - index] = f"{label}:{time.time()}"

                        with open("log.txt", "w") as f:
                            for line in lines:
                                print(line.strip(), file=f)


    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

    y = x

