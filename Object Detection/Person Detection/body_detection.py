import cv2
import mediapipe as mp


mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_holistic = mp.solutions.holistic

# For webcam input:
cap = cv2.VideoCapture(0)
with mp_holistic.Holistic(
        min_detection_confidence=0.4,
        min_tracking_confidence=0.4) as holistic:
    while cap.isOpened():
        success, image = cap.read()
        if not success:
            print("Ignoring empty camera frame.")
            # If loading a video, use "break" instead of "continue".
            continue

        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        results = holistic.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

        if results.pose_landmarks:
            print("Person Detected")

        # Draw landmark annotation on the image.
        image.flags.writeable = True
        mp_drawing.draw_landmarks(
            image,
            results.pose_landmarks,
            mp_holistic.POSE_CONNECTIONS,
        )
        image.flags.writeable = False

        cv2.imshow("MediaPipe Holistic", image)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
cap.release()
