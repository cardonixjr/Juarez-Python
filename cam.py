import cv2
import numpy as np

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()

    cv2.imshow("Frame", frame)

    k = cv2.waitKey(1)
    if k & 0xFF == ord('s'):
        cv2.imwrite("frame.jpg", frame)
    elif k & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
