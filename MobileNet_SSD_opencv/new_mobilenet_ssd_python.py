# Import the neccesary libraries
import argparse
import cv2
import time

# construct the argument parse
parser = argparse.ArgumentParser(
    description="Script to run MobileNet-SSD object detection network ")
parser.add_argument(
    "--video", help="path to video file. If empty, camera's stream will be used")
parser.add_argument("--prototxt", default="MobileNetSSD_deploy.prototxt",
                    help="Path to text network file: "
                    "MobileNetSSD_deploy.prototxt for Caffe model or "
                    )
parser.add_argument("--weights", default="MobileNetSSD_deploy.caffemodel",
                    help="Path to weights: "
                    "MobileNetSSD_deploy.caffemodel for Caffe model or "
                    )
parser.add_argument("--thr", default=0.2, type=float,
                    help="confidence threshold to filter out weak detections")
args = parser.parse_args()

with open("log.txt", "w") as f:
    pass

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

with open("log.txt", "w") as f:
    pass

# Load the Caffe model
net = cv2.dnn.readNetFromCaffe(args.prototxt, args.weights)

x, y = 0, 0
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        break

    # resize frame for prediction
    frame_resized = cv2.resize(frame, (300, 300))

    # MobileNet requires fixed dimensions for input image(s)
    # so we have to ensure that it is resized to 300x300 pixels.
    # set a scale factor to image because network the objects has differents size.
    # We perform a mean subtraction (127.5, 127.5, 127.5) to normalize the input;
    # after executing this command our "blob" now has the shape:
    # (1, 3, 300, 300)
    blob = cv2.dnn.blobFromImage(
        frame_resized, 0.007843, (300, 300), (127.5, 127.5, 127.5), False)
    # Set to network the input blob
    net.setInput(blob)
    # Prediction of network
    detections = net.forward()

    # Size of frame resize (300x300)
    cols = frame_resized.shape[1]
    rows = frame_resized.shape[0]

    # For get the class and location of object detected,
    # There is a fix index for class, location and confidence
    # value in @detections array .
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
            # Draw location of object
            cv2.rectangle(frame, (xLeftBottom, yLeftBottom), (xRightTop, yRightTop),
                          (0, 255, 0))

            # Draw label and confidence of prediction in frame resized
            if class_id in classNames:
                label = classNames[class_id] + ": " + str(confidence)
                labelSize, baseLine = cv2.getTextSize(
                    label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)

                yLeftBottom = max(yLeftBottom, labelSize[1])
                cv2.rectangle(frame, (xLeftBottom, yLeftBottom - labelSize[1]),
                              (xLeftBottom + labelSize[0],
                               yLeftBottom + baseLine),
                              (255, 255, 255), cv2.FILLED)
                cv2.putText(frame, label, (xLeftBottom, yLeftBottom),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0))

                # temporary limit
                if confidence > 0.7:
                    x += 1
                    object_name = label.split(':')[0]

                    with open("log.txt", "r") as f:
                        lines = f.readlines()

                    past_items = [item.split(":")[0] for item in lines[-y:]]
                    if object_name not in past_items:
                        with open("log.txt", "a") as f:
                            print(f"{object_name}:{time.time()}", file=f)
                    else:
                        index_of_object = past_items.index(object_name)
                        with open("log.txt", "r") as f:
                            lines = f.readlines()

                        for index, line in enumerate(lines[::-1]):
                            if line.split(":")[0] == object_name:
                                break

                        index = len(lines) - 1 - index
                        lines[index] = f"{object_name}:{time.time()}"

                        with open("log.txt", "w") as f:
                            for line in lines:
                                print(line.strip(), file=f)

    y = x

    cv2.namedWindow("frame", cv2.WINDOW_NORMAL)
    cv2.imshow("frame", frame)
    if cv2.waitKey(1) & 0xFF == ord("q"):  # Break with ESC
        break
