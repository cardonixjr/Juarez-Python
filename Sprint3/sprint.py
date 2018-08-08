import numpy as np
import cv2
import darwin_motions as dm
from time import sleep
import sys
sys.path.append('..')
from head_tracker import JuarezHeadTracker
import os

MAX_P = 15
MAX_X_SPEED = 12 # Max linear velocity
UPDATE_RATE = 3 # Number of ticks
UPDATE_STEP = 0.5 # Increment in speed each update
CROSSED_LINE_OBJ_SIZE = 84000

STEP_SIZE = 0.01

CONFIG_INI = os.path.abspath("sprint.ini")

RED_COLOR_L = np.array([6, 180, 120])
RED_COLOR_H = np.array([20, 255, 255])
#RED_COLOR2_L = np.array([170, 80, 150])
#RED_COLOR2_H = np.array([180, 255, 255])
BLUE_COLOR_L = np.array([68, 100, 140])
BLUE_COLOR_H = np.array([72, 255, 255])

class States:
    INIT = -1
    READY = 0
    RUNNING_FORWARD = 1
    RUNNING_BACKWARDS = 2
    BACKWARDS_RECENTER = 3
    FINISHED = 4

class Button:
    START = 2
    RESET = 1
    NONE = 0

#tracker = JHT(sys.argv[1], mode="single")

dm.initMotionManager(CONFIG_INI)

def updateLinearSpeed(cur_speed):
    if cur_speed >= MAX_X_SPEED:
        return MAX_X_SPEED
    else:
        return cur_speed + UPDATE_STEP

def detectCenterFromImage(debug=False):
    ret, frame = cap.read()

    rgb = cv2.GaussianBlur(frame, (7, 7), 7)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    mask1 = cv2.inRange(hsv, RED_COLOR_L, RED_COLOR_H)
    mask2 = cv2.inRange(hsv, BLUE_COLOR_L, BLUE_COLOR_H)
    #mask3 = cv2.inRange(hsv, RED_COLOR2_L, RED_COLOR2_H)
    
    full_mask = cv2.bitwise_or(mask1, mask2)
    #full_mask = cv2.bitwise_or(full_mask, mask3)
    full_mask = cv2.morphologyEx(full_mask, cv2.MORPH_CLOSE, np.ones((5, 5)))

    if debug:
        cv2.imshow("Original", frame)
        cv2.imshow("red_mask", mask1)
        cv2.imshow("blue_mask", mask2)
        cv2.imshow("full_mask", full_mask)

        cv2.waitKey(1)
    
    largest_contour, area = findLargestContourFromMask(full_mask)

    if largest_contour is not None:
        M = cv2.moments(largest_contour)
        cx = int(M['m10']/M['m00'])
        cy = int(M['m01']/M['m00'])

        return (cx, cy), area
    else:
        return None, None

def centerHeadToPoint(pos, debug=False):
    cur_pan = dm.headGetPan()
    cur_tilt = dm.headGetTilt()

    print("POSS:", pos)
    dist_x = 320. - pos[0]
    dist_y = 240. - pos[1]

    if debug: 
        print(dist_x, dist_y)
        print("Pan: {} Tilt: {}".format(cur_pan, cur_tilt))

    new_pan = cur_pan + (dist_x * STEP_SIZE)
    new_tilt = cur_tilt + (dist_y * STEP_SIZE)

    return new_pan, new_tilt

def findLargestContourFromMask(mask, min_area=300):
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
        return None, None

cap = cv2.VideoCapture(0)

state = States.INIT
while True:
    btn = dm.getButton()
    if btn == Button.RESET: state = States.INIT

    if state == States.INIT:
        print("Init.")
        dm.walkStop()
        sleep(3) # Gambiarra pull up

        #dm.reinitializeMotionManager(CONFIG_INI)
        # Walk ready pose
        dm.playMotion(51)

        dm.headMoveToHome()
        dm.headMoveByAngle(0.0, 105.0)
        #dm.walkSetPeriodTime(580.0)
        #dm.walkSetXOffset(-6.5) # Walk forward X offset

        ticks = 0
        x_speed = 0.0
        dm.walkPrintParams()

        state = States.READY

    elif state == States.READY:
        print("Ready.")
        if btn == Button.START: state = States.RUNNING_FORWARD

    pos, area = detectCenterFromImage(debug=False)
    print("Current area", area)

    #obj_info = tracker.getObj()
    if pos is not None: 
        p, t = centerHeadToPoint(pos, debug=False)

        print("Here:", p, t)
        dm.headMoveByAngle(p, t)

    else:
        dm.walkStop()
        print("Object not detected this iteration.")
        continue # Skip this loop

    if state == States.RUNNING_FORWARD:
        print("walk forward")
        if ticks % UPDATE_RATE == 0:
            x_speed = updateLinearSpeed(x_speed)

        if p > MAX_P:
            p = MAX_P
            dm.walkSetVelocities(5.0, 0.0, p)
        elif p < -MAX_P:
            p = -MAX_P
            dm.walkSetVelocities(5.0, 0.0, p)
        else:
            dm.walkSetVelocities(x_speed, 0.0, p)

        dm.walkStart()

        if area > CROSSED_LINE_OBJ_SIZE:
            # Changing State
            state = States.RUNNING_BACKWARDS
            #dm.walkSetHipPitchOffset(-17.9)
            dm.walkStop()
            sleep(3)

    elif state == States.RUNNING_BACKWARDS:
        print("walk backwards")
        dm.walkSetVelocities(-11.0, 0.0, 0.0)
        if p > 15.0 or p < -15.0:
            state = States.BACKWARDS_RECENTER

        dm.walkStart()

    elif state == States.BACKWARDS_RECENTER:
        print("backwards recenter")
        if p > 1.5:
            dm.walkSetVelocities(-1.0, 0.0, 7.0)
        elif p < -1.5:
            dm.walkSetVelocities(-1.0, 0.0, -7.0)
        else:
            state = States.RUNNING_BACKWARDS

    print(ticks)
    print(x_speed)
    ticks += 1
