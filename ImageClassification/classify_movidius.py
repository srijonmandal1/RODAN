# USAGE
# python classify_movidius.py --conf config/config.json --model squeezenet --image images/beer.png
# python classify_movidius.py --conf config/config.json --model googlenet --image images/brown_bear.png

# import the necessary packages
from openvino.inference_engine import IENetwork
from openvino.inference_engine import IEPlugin
from conf import Conf
import numpy as np
import argparse
import pickle
import time
import cv2

# construct the argument parser and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to the input image")
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

# initialize the plugin for specified device
plugin = IEPlugin(device="MYRIAD")

# read the IR generated by the Model Optimizer (.xml and .bin files)
print("[INFO] loading models...")
net = IENetwork(
    model=conf["model_paths"]["ir"][args["model"]]["xml"],
    weights=conf["model_paths"]["ir"][args["model"]]["bin"])

# prepare input and output blobs
print("[INFO] preparing inputs...")
inputBlob = next(iter(net.inputs))
outputBlob = next(iter(net.outputs))

# set the default batch size as 1 and grab the number of input blobs,
# number of channels, the height, and width of the input blob
net.batch_size = 1
(n, c, h, w) = net.inputs[inputBlob].shape

# load model to the plugin
print("[INFO] Loading model to the plugin...")
execNet = plugin.load(network=net)

# load the input image and resize input frame to network size
orig = cv2.imread(args["image"])
frame = cv2.resize(orig, (w, h))

# change data layout from HxWxC to CxHxW
frame = frame.transpose((2, 0, 1))
frame = frame.reshape((n, c, h, w))

# perform inference and retrieve final layer output predictions
print("[INFO] classifying image...")
start = time.time()
results = execNet.infer({inputBlob: frame})
results = results[outputBlob]
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
cv2.waitKey(0)