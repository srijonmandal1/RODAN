import threading
import pygame
from pygame.locals import *
from pygame_classes import *
import time

import text_to_speech


pygame.init()


screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
white = (255, 255, 255)
red = (255, 0, 0)
green = (0, 255, 0)
blue = (0, 0, 255)
yellow = (255, 255, 0)
font_path = "Segoe-UI-Variable-Static-Display.ttf"

pygame.display.update()

runUi = True
# 0 - green
# 1 - yellow
# 2 - red
alert_level = 0
medium_font = pygame.font.Font(font_path, 27)
alert = ""
time_since_alert = None


def runUiFalse():
    global runUi
    runUi = False


quit_button = DefaultButton(screen, 10, 10, 100, 50,
                            runUiFalse, medium_font, "Quit")


def show_alert_always(text: str):
    global alert, time_since_alert
    if text:
        label = medium_font.render(text, 1, (0, 0, 0))
        width, height = label.get_size()
        screen_width, screen_height = screen.get_size()
        screen.blit(screen, (screen_width / 2 - width / 2, screen_height / 2 - height / 2))
        if time.time() - time_since_alert > 10:
            alert = ""
            time_since_alert = None


def show_alert(text: str, sound_alert: str):
    global alert, time_since_alert
    alert = text
    time_since_alert = time.time()
    if alert_level > 1:
        text_to_speech.parallel(sound_alert)
        print(1)


alert_level = 2
show_alert("Hi", "Bye hi hi hi")
while runUi:
    pygame.display.update()
    screen.fill(green if alert_level == 1
                else yellow if alert_level == 2
                else red)
    quit_button.draw()
    show_alert_always(alert)
    for event in pygame.event.get():
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = event.pos
            quit_button.check_click(*pos)
        elif event.type == pygame.FINGERDOWN:
            pos = (event.x * screen.get_width(), event.y * screen.get_height())
            quit_button.check_click(*pos)
        elif event.type == pygame.KEYDOWN:
            if event.key == K_q:
                runUi = False
