import cv2

cap = cv2.VideoCapture(0)

while True:
    _, image = cap.read()
    if not _:
        continue

    cv2.imshow("Video Testing", image)

    if cv2.waitKey(1) & 0xFF == ord("q"):
        break

cap.release()
