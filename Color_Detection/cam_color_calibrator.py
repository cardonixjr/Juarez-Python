import sys
import cv2
import numpy as np
import os
from juarez_color_detector import *

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python {} <mode> <color_save_file>".format(sys.argv[0]))
        sys.exit(1)

    mode = sys.argv[1]
    filename = sys.argv[2]

    if mode == "Single":
        detector = SingleColorDetection(calibrateMode=True)
    elif mode == "Sprint":
        detector = SprintColorDetection(calibrateMode=True)

    if os.path.isfile(filename):
        print("Loading parameters from {}".format(filename))
        detector.loadParameters(filename)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        obj_pos = detector.detectFromRGB(frame)

        if obj_pos != None:
            if obj_pos[0] != None: # Gambiarra
                cv2.circle(frame, (int(obj_pos[0]), int(obj_pos[1])), 3, (0, 0, 255), -1)

        cv2.imshow("Original", frame)

        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('r'):
            detector.loadParameters(filename)
        elif k == ord('s'):
            detector.saveParameters(filename)

cv2.destroyAllWindows()
