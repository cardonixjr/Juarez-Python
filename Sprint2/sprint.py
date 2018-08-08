import darwin_motions as dm
from time import sleep
import sys
sys.path.append('..')
from head_tracker import JuarezHeadTracker as JHT
import os

MAX_P = 15
MAX_X_SPEED = 12 # Max linear velocity
UPDATE_RATE = 3 # Number of ticks
UPDATE_STEP = 0.5 # Increment in speed each update
CROSSED_LINE_OBJ_SIZE = 74000

CONFIG_INI = os.path.abspath("sprint.ini")

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

tracker = JHT(sys.argv[1], mode="single")

dm.initMotionManager(CONFIG_INI)

def updateLinearSpeed(cur_speed):
    if cur_speed >= MAX_X_SPEED:
        return MAX_X_SPEED
    else:
        return cur_speed + UPDATE_STEP

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

    obj_info = tracker.getObj()
    if obj_info is not None: 
        pos, area = obj_info
        print("Area:", area)
        #area = obj_info[2]

        p, t = tracker.centerHeadToPoint(pos)

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
            sleep(1)

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

        dm.walkStart()

    print(ticks)
    print(x_speed)
    ticks += 1
