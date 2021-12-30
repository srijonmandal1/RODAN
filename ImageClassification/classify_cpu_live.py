# USAGE
# python3 classify_cpu_live.py --conf config/config.json --model squeezenet
# python3 classify_cpu_live.py --conf config/config.json --model googlenet

# import the necessary packages
from conf import Conf
import numpy as np
import argparse
import pickle
import time
import cv2

cap = cv2.VideoCapture(0)

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-m", "--model", required=True,
                choices=["squeezenet", "googlenet"],
                help="model to be used for classify")
ap.add_argument("-c", "--conf", required=True,
                help="path to the input configuration file")
args = vars(ap.parse_args())

# load the configuration file
conf = Conf(args["conf"])

# load the imagenet class labels
classes = pickle.loads(open(conf["labels_path"], "rb").read())

# load our serialized model from disk, set the preferable backend and
# set the preferable target
print("[INFO] loading model...")
net = cv2.dnn.readNetFromCaffe(
    conf["model_paths"]["caffe"][args["model"]]["prototxt"],
    conf["model_paths"]["caffe"][args["model"]]["caffemodel"])
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

# retrieve various preprocessing values such as input height/width,
# channel mean, and scale factor
(H, W) = conf["preprocess"][args["model"]]["input_size"]
mean = conf["preprocess"][args["model"]]["mean"]
scale = 1.0 / conf["preprocess"][args["model"]]["scale"]

while True:
    # load the input image and resize input frame to network size
    # orig = cv2.imread(args["image"])
    _, orig = cap.read()
    frame = cv2.resize(orig, (W, H))

    # convert the frame to a blob and perform a forward pass through the
    # model and obtain the classification result
    blob = cv2.dnn.blobFromImage(frame, scale, (W, H), mean)
    print("[INFO] classifying image...")
    start = time.time()
    net.setInput(blob)
    results = net.forward()
    end = time.time()
    print("[INFO] classification took {:.4f} seconds...".format(
        end - start))

    # sort the indexes of the probabilities in descending order (higher
    # probabilitiy first) and grab the top-5 predictions
    idxs = np.argsort(results.reshape((1000)))[::-1][:5]

    # loop over the top-5 predictions and display them
    for (i, idx) in enumerate(idxs):
        # check if the model type is SqueezeNet, and if so and retrieve
        # the probability  using special indexing as the output format of
        # SqueezeNet is (1, 1000, 1, 1)
        if args["model"] == "squeezenet":
            proba = results[0][idx][0][0]

        # otherwise, it's a GoogLeNet model so retrieve the probability
        # from the output which is of the form (1, 1000)
        else:
            proba = results[0][idx]

        # draw the top prediction on the input image
        if i == 0:
            text = "Label: {}, {:.2f}%".format(classes[idx],
                                            proba * 100)
            cv2.putText(orig, text, (5, 25), cv2.FONT_HERSHEY_SIMPLEX,
                        0.7, (0, 0, 255), 2)

        # display the predicted label + associated probability to the
        # console
        print("[INFO] {}. label: {}, probability: {:.2f}%".format(i + 1,
                                                                classes[idx], proba * 100))

    # display the output image
    cv2.imshow("Result", orig)
    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
