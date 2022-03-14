import cv2
import torch
import sys
import numpy
import time
import queue
import threading
from PIL import Image

# Model
model = torch.hub.load('../yolov5', 'custom', path='lisa_weights/best.pt', source='local')

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

cap = VideoCapture(0)

for _ in range(10):
    cap.read()

while True:
    img = cv2.cvtColor(cap.read(), cv2.COLOR_RGB2BGR)
    grayscale_img = cv2.cvtColor(cv2.cvtColor(img, cv2.COLOR_BGR2GRAY), cv2.COLOR_GRAY2BGR)

    # Inference
    results = model(img, size=640)  # includes NMS

    results.render()
    # some_img = numpy.array(Image.fromarray(results.imgs[0]).convert('RGB'))[:, :, ::-1]
    # some_img = cv2.resize(some_img,(400,400))
    # cv2.imshow("hi", some_img)

    cv2.imshow('Vid',numpy.array(Image.fromarray(results.imgs[0]).convert('RGB'))[:, :, ::-1])

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
