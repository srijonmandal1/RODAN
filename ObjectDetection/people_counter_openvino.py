# import the necessary packages
from pyimagesearch.directioncounter import DirectionCounter
from pyimagesearch.centroidtracker import CentroidTracker
from pyimagesearch.trackableobject import TrackableObject
from pyimagesearch.utils import Conf
from multiprocessing import Process
from multiprocessing import Queue
from multiprocessing import Value
from imutils.video import VideoStream
from imutils.video import FPS
import numpy as np
import argparse
import imutils
import time
import dlib
import cv2

def write_video(outputPath, writeVideo, frameQueue, W, H):
  # initialize the FourCC and video writer object
  fourcc = cv2.VideoWriter_fourcc(*"MJPG")
  writer = cv2.VideoWriter(outputPath, fourcc, 30, (W, H), True)

  # loop while the write flag is set or the output frame queue is not empty
  while writeVideo.value or not frameQueue.empty():
    # check if the output frame queue is not empty
    if not frameQueue.empty():
      # get the frame from the queue and write the frame
      frame = frameQueue.get()
      writer.write(frame)

  # release the video writer object
  writer.release()

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-t", "--target", type=str, required=True,
choices=["myriad", "cpu"],
help="target processor for object detection")
ap.add_argument("-m", "--mode", type=str, required=True,
choices=["horizontal", "vertical"],
help="direction in which people will be moving")
ap.add_argument("-c", "--conf", required=True,
help="Path to the input configuration file")
ap.add_argument("-i", "--input", type=str,
help="path to optional input video file")
ap.add_argument("-o", "--output", type=str,
help="path to optional output video file")
args = vars(ap.parse_args())

# load the configuration file
conf = Conf(args["conf"])

# initialize the list of class labels MobileNet SSD detects
CLASSES = ["background", "aeroplane", "bicycle", "bird", "boat",
"bottle", "bus", "car", "cat", "chair", "cow", "diningtable",
"dog", "horse", "motorbike", "person", "pottedplant", "sheep",
"sofa", "train", "tvmonitor"]

# load our serialized model from disk
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(conf["prototxt_path"],
conf["model_path"])

# check if the target processor is myriad, if so, then set the
# preferable target to myriad
if args["target"] == "myriad":
  net.setPreferableTarget(cv2.dnn.DNN_TARGET_MYRIAD)

# otherwise, the target processor is CPU
else:
  # set the preferable target processor to CPU and preferable
  # backend to OpenCV
  net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
  net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)

  
# if a video path was not supplied, grab a reference to the webcam
if not args.get("input", False):
  print("[INFO] starting video stream...")
  # vs = VideoStream(src=0).start()
  vs = VideoStream(usePiCamera=True).start()
  time.sleep(2.0)

# otherwise, grab a reference to the video file
else:
  print("[INFO] opening video file...")
  vs = cv2.VideoCapture(args["input"])


# initialize the video writer process (we'll instantiate later if
# need be) along with the frame dimensions
writerProcess = None
W = None
H = None

# instantiate our centroid tracker, then initialize a list to store
# each of our dlib correlation trackers, followed by a dictionary to
# map each unique object ID to a trackable object
ct = CentroidTracker(maxDisappeared=20, maxDistance=30)
trackers = []
trackableObjects = {}

# initialize the direction info variable (used to store information
# such as up/down or left/right people count) and a variable to store
# the the total number of frames processed thus far
directionInfo = None
totalFrames = 0

# start the frames per second throughput estimator
fps = FPS().start()

# loop over frames from the video stream
while True:
  # grab the next frame and handle if we are reading from either
  # VideoCapture or VideoStream
  frame = vs.read()
  frame = frame[1] if args.get("input", False) else frame

  # if we are viewing a video and we did not grab a frame then we
  # have reached the end of the video
  if args["input"] is not None and frame is None:
    break
    
  # convert the frame from BGR to RGB for dlib
  rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
  
  # check to see if the frame dimensions are not set
  if W is None or H is None:
    # set the frame dimensions and instantiate our direction
    # counter
    (H, W) = frame.shape[:2]
    dc = DirectionCounter(args["mode"], H, W)

  # begin writing the video to disk if required
  if args["output"] is not None and writerProcess is None:
    # set the value of the write flag (used to communicate when
    # to stop the process)
    writeVideo = Value('i', 1)

    # initialize a frame queue and start the video writer
    frameQueue = Queue()
    writerProcess = Process(target=write_video, args=(
      args["output"], writeVideo, frameQueue, W, H))
    writerProcess.start()

  # initialize the current status along with our list of bounding
  # box rectangles returned by either (1) our object detector or
  # (2) the correlation trackers
  status = "Waiting"
  rects = []

  # check to see if we should run a more computationally expensive
  # object detection method to aid our tracker
  if totalFrames % conf["skip_frames"] == 0:
    # set the status and initialize our new set of object
    # trackers
    status = "Detecting"
    trackers = []

  # convert the frame to a blob and pass the blob through the

  # network and obtain the detections
  blob = cv2.dnn.blobFromImage(frame, size=(300, 300),
  ddepth=cv2.CV_8U)
  net.setInput(blob, scalefactor=1.0/127.5, mean=[127.5,
  127.5, 127.5])
  detections = net.forward()
  
# loop over the detections
  for i in np.arange(0, detections.shape[2]):

  # extract the confidence (i.e., probability) associated
  # with the prediction
  confidence = detections[0, 0, i, 2]

  # filter out weak detections by requiring a minimum
  # confidence
  if confidence > conf["confidence"]:
    # extract the index of the class label from the
    # detections list
    idx = int(detections[0, 0, i, 1])

    # if the class label is not a person, ignore it
    if CLASSES[idx] != "person":
      continue
