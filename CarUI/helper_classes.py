import cv2
import threading
import queue
import time


class ThreadedVideoCapture:
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
        return True, self.q.get()

    def release(self):
        self.stop = True
        time.sleep(0.1)
        self.cap.release()
