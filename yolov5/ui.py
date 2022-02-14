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

alert_level = 1
show_alert("Drive Safe!", "Thank you for using Row Dan! Drive safe!", True)
x = 0
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
