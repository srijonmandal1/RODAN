# Import the neccesary libraries
import argparse
import cv2
import time

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

while True:
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

    y = x
