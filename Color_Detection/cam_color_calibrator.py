import sys
import cv2
import numpy as np
import os
from juarez_color_detector import SingleColorDetection

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python {} <color_save_file>".format(sys.argv[0]))
        sys.exit(1)

    filename = sys.argv[1]

    detector = SingleColorDetection(calibrateMode=True)

    if os.path.isfile(filename):
        print("Loading parameters from {}".format(filename))
        detector.loadParameters(filename)

    cap = cv2.VideoCapture(0)

    while True:
        ret, frame = cap.read()

        obj_pos = detector.detectFromRGB(frame)
        cv2.circle(frame, obj_pos, 3, (0, 0, 255), -1)
        cv2.imshow("Original", frame)

        k = cv2.waitKey(1) & 0xFF
        if k == ord('q'):
            break
        elif k == ord('r'):
            detector.loadParameters(sys.argv[1])
        elif k == ord('s'):
            detector.saveParameters(sys.argv[1])

cv2.destroyAllWindows()
