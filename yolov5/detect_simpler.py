import torch
import cv2

# Model
model = torch.hub.load('ultralytics/yolov5', 'yolov5n')  # or yolov5m, yolov5l, yolov5x, custom

def get_classes_from_results(results):
    classes_detected = {}
    pred = results.pred[0]

    if pred.shape[0]:
        for c in pred[:, -1].unique():
            n = (pred[:, -1] == c).sum()  # detections per class
            classes_detected[results.names[int(c)]] = int(n)

    return classes_detected

cap = cv2.VideoCapture(0)
for _ in range(10):
    _, frame = cap.read()
while True:
    _, frame = cap.read()
    results = model(frame)
    print(str(get_classes_from_results(results)) + "                      ", end="\r")
    cv2.imshow("Frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
