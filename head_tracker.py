import cv2
import numpy as np
import darwin_motions as dm
import sys
sys.path.append("/home/juarez/Darwin-Python/Color_Detection")
from juarez_color_detector import *

DEFAULT_CONFIG = "/home/juarez/Darwin-tools/Data/config.ini"

class JuarezHeadTracker:
    def __init__(self, color_file, debug=False):
        # Keeps track of what should be printed
        self.debug = debug

        # Frame dimensions of Logitech c270 image
        self.IMG_WIDTH = 640
        self.IMG_HEIGHT = 480

        # Increment in head joints position
        self.STEP_SIZE = 0.01

        # Create detector object and load color parameters from file
        self.detector = SingleColorDetection(calibrateMode=False)
        self.detector.loadParameters(color_file)

        # Setup OpenCV video Capture
        self.cap = cv2.VideoCapture(0)

    def _init_motion(self):
        dm.initMotionManager(DEFAULT_CONFIG)
        dm.playMotion(52)

        dm.headMoveToHome()

    # Given an (x, y) position, perform an iteration to move head towards its
    # direction
    def centerHeadToPoint(self, pos):
        cur_pan = dm.headGetPan()
        cur_tilt = dm.headGetTilt()

        dist_x = self.IMG_WIDTH/2. - pos[0]
        dist_y = self.IMG_HEIGHT/2. - pos[1]

        if self.debug: 
            print(dist_x, dist_y)
            print("Pan: {} Tilt: {}".format(cur_pan, cur_tilt))

        new_pan = cur_pan + (dist_x * self.STEP_SIZE)
        new_tilt = cur_tilt + (dist_y * self.STEP_SIZE)

        return new_pan, new_tilt

    def getObj(self):
        ret, frame = self.cap.read()

        return self.detector.detectFromRGB(frame, return_area=True)

    def run(self):
        self._init_motion()

        while True:
            ret, frame = self.cap.read()

            r = self.detector.detectFromRGB(frame, return_area=True)
            if r is not None:
                obj_pos, obj_area = r
                if self.debug:
                    cv2.circle(frame, (obj_pos[0], obj_pos[1]), 2,
                               (0, 0, 255), -1)
                    print(obj_pos, obj_area)

                pan, tilt = self.centerHeadToPoint(obj_pos)

                dm.headMoveByAngle(pan, tilt)

            if self.debug:
                cv2.imshow("Vision", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python {} <color_parameters_file>".format(sys.argv[0]))
        sys.exit(1)

    juarez_ht = JuarezHeadTracker(sys.argv[1], debug=True)
    juarez_ht.run()
