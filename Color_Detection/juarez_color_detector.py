import cv2
import numpy as np
import json

class HSVColorParam:
    def __init__(self):
        self.lower = np.array([0, 0, 0], np.uint8)
        self.upper = np.array([255, 255, 255], np.uint8)
        self.blur_size = (5, 5)
        self.blur_sigma = 5
        self.close_kernel = np.ones((5, 5), np.uint8)

    def getArrays(self):
        return self.lower, self.upper

    # The functions below should be passed as callbacks to the gui trackbars
    def _setLowerHue(self, x):
        self.lower[0] = x
    def _setLowerSat(self, x):
        self.lower[1] = x
    def _setLowerVal(self, x):
        self.lower[2] = x
    def _setUpperHue(self, x):
        self.upper[0] = x
    def _setUpperSat(self, x):
        self.upper[1] = x
    def _setUpperVal(self, x):
        self.upper[2] = x
    def _setBlurSize(self, x):
        if x % 2 != 0:
            self.blur_size = (x, x)
    def _setBlurSigma(self, x):
        self.blur_sigma = x
    def _setCloseSize(self, x):
        self.close_kernel = np.ones((x, x), np.uint8)

def findLargestContourFromMask(mask, min_area=100):
    _, contours, _ = cv2.findContours(mask.copy(), cv2.RETR_LIST, 
                                      cv2.CHAIN_APPROX_SIMPLE)

    largest_i = None
    largest_area = min_area
    for i, c in enumerate(contours):
        cur_area = cv2.contourArea(c)
        if cur_area > largest_area:
            largest_i = i
            largest_area = cur_area

    if largest_i != None:
        return contours[largest_i], largest_area 
    else:
        return None

def findCenterOfContours(mask, min_area):
    _, contours, _ = cv2.findContours(mask.copy(), cv2.RETR_LIST, 
                                      cv2.CHAIN_APPROX_SIMPLE)

    centers_x = []
    centers_y = []
    areas = []
    for c in contours:
        cur_area = cv2.contourArea(c)
        if cur_area < min_area:
            continue
        else:
            M = cv2.moments(c)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            centers_x.append(cx)
            centers_y.append(cy)
            areas.append(cur_area)

    if len(centers_x) != 0:
        return np.mean(centers_x), np.mean(centers_y), np.sum(areas)
    else:
        return None, None, None

class SingleColorDetection:
    def __init__(self, calibrateMode=False):
        self.param = HSVColorParam()

        self.calibrateMode = calibrateMode
        if calibrateMode == True:
            self._initGui()

    def _initGui(self): # creates windows and trackbars
        cv2.namedWindow("Mask Controls")
        cv2.createTrackbar("L_Hue", "Mask Controls", 0, 255, 
                            self.param._setLowerHue)
        cv2.createTrackbar("L_Sat", "Mask Controls", 0, 255,
                            self.param._setLowerSat)
        cv2.createTrackbar("L_Val", "Mask Controls", 0, 255,
                            self.param._setLowerVal)
        cv2.createTrackbar("U_Hue", "Mask Controls", 255, 255,
                            self.param._setUpperHue)
        cv2.createTrackbar("U_Sat", "Mask Controls", 255, 255,
                            self.param._setUpperSat)
        cv2.createTrackbar("U_Val", "Mask Controls", 255, 255,
                            self.param._setUpperVal)
        cv2.createTrackbar("Gaussian Blur Size", "Mask Controls", 5, 33,
                            self.param._setBlurSize)
        cv2.createTrackbar("Gaussian Blur Sigma", "Mask Controls", 5, 33,
                            self.param._setBlurSigma)
        cv2.createTrackbar("Closing Size", "Mask Controls", 5, 33,
                            self.param._setCloseSize)

    def detectFromRGB(self, rgb_frame, return_area=False):
        rgb_frame = cv2.GaussianBlur(rgb_frame, self.param.blur_size,
                                     self.param.blur_sigma)
        hsv = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.param.lower, self.param.upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.param.close_kernel)

        r = findLargestContourFromMask(mask)

        if self.calibrateMode:
            cv2.imshow("HSV", hsv)
            cv2.imshow("Mask", mask)

        if r is not None:
            obj_contour, area = r
            M = cv2.moments(obj_contour)
            cx = int(M['m10']/M['m00'])
            cy = int(M['m01']/M['m00'])

            if return_area:
                return (cx, cy), area
            else:
                return (cx, cy)
        else:
            return None

    def saveParameters(self, filename):
        # Build a dictionary of the parameters to save as JSON
        params = {'Lower_Hue': int(self.param.lower[0]),
                  'Lower_Sat': int(self.param.lower[1]),
                  'Lower_Val': int(self.param.lower[2]),
                  'Upper_Hue': int(self.param.upper[0]),
                  'Upper_Sat': int(self.param.upper[1]),
                  'Upper_Val': int(self.param.upper[2]),
                  'Blur_Size': int(self.param.blur_size[0]),
                  'Blur_Sigma': int(self.param.blur_sigma),
                  'Close_Size': int(self.param.close_kernel.shape[0])}

        with open(filename, 'w') as f:
            json.dump(params, f)
            print("Saved to {}".format(filename))

    def loadParameters(self, filename):
        with open(filename, 'r') as f:
            params = json.load(f)

        lower = np.array([params['Lower_Hue'], params['Lower_Sat'],
                          params['Lower_Val']], np.uint8)
        upper = np.array([params['Upper_Hue'], params['Upper_Sat'],
                          params['Upper_Val']], np.uint8)

        blur_size = (params['Blur_Size'], params['Blur_Size'])
        close_kernel = np.ones((params['Close_Size'], params['Close_Size']),
                             np.uint8)

        self.param.lower = lower
        self.param.upper = upper
        self.param.blur_size = blur_size
        self.param.blur_sigma = params['Blur_Sigma']
        self.param.close_kernel = close_kernel

        if self.calibrateMode:
            cv2.setTrackbarPos("L_Hue", "Mask Controls", params['Lower_Hue'])
            cv2.setTrackbarPos("L_Sat", "Mask Controls", params['Lower_Sat'])
            cv2.setTrackbarPos("L_Val", "Mask Controls", params['Lower_Val'])
            cv2.setTrackbarPos("U_Hue", "Mask Controls", params['Upper_Hue'])
            cv2.setTrackbarPos("U_Sat", "Mask Controls", params['Upper_Sat'])
            cv2.setTrackbarPos("U_Val", "Mask Controls", params['Upper_Val'])
            cv2.setTrackbarPos("Gaussian Blur Size", "Mask Controls",
                               params['Blur_Size'])
            cv2.setTrackbarPos("Gaussian Blur Sigma", "Mask Controls",
                               params['Blur_Sigma'])
            cv2.setTrackbarPos("Closing Size", "Mask Controls",
                               params['Close_Size'])

class SprintColorDetection:
    def __init__(self, calibrateMode=False):
        self.param = HSVColorParam()

        self.calibrateMode = calibrateMode
        if calibrateMode == True:
            self._initGui()

    def _initGui(self): # creates windows and trackbars
        cv2.namedWindow("Mask Controls")
        cv2.createTrackbar("L_Hue", "Mask Controls", 0, 255, 
                            self.param._setLowerHue)
        cv2.createTrackbar("L_Sat", "Mask Controls", 0, 255,
                            self.param._setLowerSat)
        cv2.createTrackbar("L_Val", "Mask Controls", 0, 255,
                            self.param._setLowerVal)
        cv2.createTrackbar("U_Hue", "Mask Controls", 255, 255,
                            self.param._setUpperHue)
        cv2.createTrackbar("U_Sat", "Mask Controls", 255, 255,
                            self.param._setUpperSat)
        cv2.createTrackbar("U_Val", "Mask Controls", 255, 255,
                            self.param._setUpperVal)
        cv2.createTrackbar("Gaussian Blur Size", "Mask Controls", 5, 33,
                            self.param._setBlurSize)
        cv2.createTrackbar("Gaussian Blur Sigma", "Mask Controls", 5, 33,
                            self.param._setBlurSigma)
        cv2.createTrackbar("Closing Size", "Mask Controls", 5, 33,
                            self.param._setCloseSize)

    def detectFromRGB(self, rgb_frame, area):
        rgb_frame = cv2.GaussianBlur(rgb_frame, self.param.blur_size,
                                     self.param.blur_sigma)
        hsv = cv2.cvtColor(rgb_frame, cv2.COLOR_BGR2HSV)

        mask = cv2.inRange(hsv, self.param.lower, self.param.upper)
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.param.close_kernel)

        if self.calibrateMode:
            cv2.imshow("HSV", hsv)
            cv2.imshow("Mask", mask)

        return findCenterOfContours(mask, area)

    def saveParameters(self, filename):
        # Build a dictionary of the parameters to save as JSON
        params = {'Lower_Hue': int(self.param.lower[0]),
                  'Lower_Sat': int(self.param.lower[1]),
                  'Lower_Val': int(self.param.lower[2]),
                  'Upper_Hue': int(self.param.upper[0]),
                  'Upper_Sat': int(self.param.upper[1]),
                  'Upper_Val': int(self.param.upper[2]),
                  'Blur_Size': int(self.param.blur_size[0]),
                  'Blur_Sigma': int(self.param.blur_sigma),
                  'Close_Size': int(self.param.close_kernel.shape[0])}

        with open(filename, 'w') as f:
            json.dump(params, f)
            print("Saved to {}".format(filename))

    def loadParameters(self, filename):
        with open(filename, 'r') as f:
            params = json.load(f)

        lower = np.array([params['Lower_Hue'], params['Lower_Sat'],
                          params['Lower_Val']], np.uint8)
        upper = np.array([params['Upper_Hue'], params['Upper_Sat'],
                          params['Upper_Val']], np.uint8)

        blur_size = (params['Blur_Size'], params['Blur_Size'])
        close_kernel = np.ones((params['Close_Size'], params['Close_Size']),
                             np.uint8)

        self.param.lower = lower
        self.param.upper = upper
        self.param.blur_size = blur_size
        self.param.blur_sigma = params['Blur_Sigma']
        self.param.close_kernel = close_kernel

        if self.calibrateMode:
            cv2.setTrackbarPos("L_Hue", "Mask Controls", params['Lower_Hue'])
            cv2.setTrackbarPos("L_Sat", "Mask Controls", params['Lower_Sat'])
            cv2.setTrackbarPos("L_Val", "Mask Controls", params['Lower_Val'])
            cv2.setTrackbarPos("U_Hue", "Mask Controls", params['Upper_Hue'])
            cv2.setTrackbarPos("U_Sat", "Mask Controls", params['Upper_Sat'])
            cv2.setTrackbarPos("U_Val", "Mask Controls", params['Upper_Val'])
            cv2.setTrackbarPos("Gaussian Blur Size", "Mask Controls",
                               params['Blur_Size'])
            cv2.setTrackbarPos("Gaussian Blur Sigma", "Mask Controls",
                               params['Blur_Sigma'])
            cv2.setTrackbarPos("Closing Size", "Mask Controls",
                               params['Close_Size'])
