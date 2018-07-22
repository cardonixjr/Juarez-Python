import cv2
import numpy as np
import darwin_motions as dm

class JuarezHeadTracker:
    def __init__(self, debug=False):
        self.debug = debug

        self.IMG_WIDTH = 640
        self.IMG_HEIGHT = 480

        self.STEP_SIZE = 0.01

        self.LOWER = np.array([25, 150, 150])
        self.UPPER = np.array([35, 255, 255])
        self.close_k = np.ones((5, 5), np.uint8)

        self.cap = cv2.VideoCapture(0)

    def init_motion(self):
        dm.initMotionManager()
        dm.playMotion(1)

        dm.headMoveToHome()

    def centerHeadToPoint(self, pos):
        cur_pan = dm.headGetPan()
        cur_tilt = dm.headGetTilt()

        dist_x = self.IMG_WIDTH/2. - pos[0]
        dist_y = self.IMG_HEIGHT/2. - pos[1]

        if self.debug: print(dist_x, dist_y)

        new_pan = cur_pan + (dist_x * self.STEP_SIZE)
        new_tilt = cur_tilt + (dist_y * self.STEP_SIZE)

        return new_pan, new_tilt

    def findLargestContour(self, contours):
        best_i = None
        best_area = 300 # Minimum wanted area

        for i, c in enumerate(contours):
            cur_area = cv2.contourArea(c)
            if cur_area > best_area:
                best_i = i
                best_area = cur_area

        return best_i, best_area

    def getObjPosFromBGR(self):
        ret, frame = self.cap.read()

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.LOWER, self.UPPER)

        cnt, _ = cv2.findContours(mask, cv2.CHAIN_APPROX_SIMPLE, 
                                  cv2.RETR_LIST)
        if self.debug:
            cv2.imshow("HSV", hsv)
            cv2.imshow("Mask", mask)

        if cnt is not None:
            i, _ = self.findLargestContour(cnt)

            if i != None:
                x, y, w, h, = cv2.boundingRect(cnt[i])
                cx = int(x + w/2.)
                cy = int(y + h/2.)
                
                if self.debug: print(cx, cy)

                return cx, cy

            else:
                return None

    def _getObjPosFromBGR(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.LOWER, self.UPPER)

        cnt, _ = cv2.findContours(mask.copy(), cv2.CHAIN_APPROX_SIMPLE, 
                                  cv2.RETR_LIST)
        if self.debug:
            cv2.imshow("HSV", hsv)
            cv2.imshow("Mask", mask)

        if cnt is not None:
            i, _ = self.findLargestContour(cnt)

            if i != None:
                x, y, w, h, = cv2.boundingRect(cnt[i])
                cx = int(x + w/2.)
                cy = int(y + h/2.)
                
                if self.debug: print(cx, cy)

                return cx, cy

            else:
                return None

    def run(self):
        self.init_motion()

        while True:
            ret, frame = self.cap.read()

            pos = self._getObjPosFromBGR(frame)
            if pos is not None:
                cx, cy = pos

                cv2.circle(frame, (cx, cy), 3, (0, 0, 255), 3)

                pan, tilt = self.centerHeadToPoint((cx, cy))

                dm.headMoveByAngle(pan, tilt)

            if self.debug:
                cv2.imshow("Vision", frame)

                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        cv2.destroyAllWindows()

if __name__ == "__main__":
    juarez_ht = JuarezHeadTracker(debug=True)
    juarez_ht.run()
