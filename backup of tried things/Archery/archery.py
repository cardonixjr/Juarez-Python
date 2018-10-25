import darwin_motions as dm
from time import sleep
import sys
sys.path.append('../..')
from head_tracker import JuarezHeadTracker as JHT
import os

WALKING_INI = os.path.abspath("walking_archery.ini")
MOTION_INI = os.path.abspath("motion_archery.ini")

SHOOTING_PAN = 71.00
LOOK_STEP = 0.5

class States:
    INIT = -1
    READY = 0
    TRACK_TARGET = 1
    AIM_TARGET = 2
    SHOOT = 3
    FINISH = 4

class Button:
    START = 2
    RESET = 1
    NONE = 0

# Load tracker with .json color from command line
tracker = JHT(mode='single', sys.argv[1])

# Load motion manager with archery walking offsets

dm.initMotionManager(WALKING_INI)

state = States.INIT
while True:
    # Get button states
    btn = dm.getButton()
    # If reset button is pressed change state back to init state
    if btn == Button.RESET: 
        dm.walkStop()
        dm.motionLoadINI(WALKING_INI)
        state = States.INIT

    if state == States.INIT:
        print("Init.")
        sleep(2)
        # Sets up robot initial robot. This state is run only once. 
        dm.walkLoadINI(WALKING_INI)

        dm.playMotion(52) # Bow Walk ready motion
        dm.headMoveToHome()
        look_dir = 1 # This is used to change directions when looking for the target
        
        state = States.READY

    elif state == States.READY:
        print("Ready.")
        # Wait for the start button press

        if btn == Button.START: state = States.TRACK_TARGET

    # Look for target
    elif state == States.TRACK_TARGET:
        print("Track Target.")
        # Get obj info from tracker
        obj_info = tracker.getObj()

        if obj_info is not None:
            pos, _ = obj_info
            p, t = tracker.centerHeadToPoint(pos)

            dm.headMoveByAngle(p, t)

            state = States.AIM_TARGET

        else:
            cur_pan = dm.headGetPan()
            cur_tilt = dm.headGetTilt()

            if cur_pan > 45:
                look_dir = 0
            elif cur_pan < -45:
                look_dir = 1

            if look_dir == 1:
                dm.headMoveByAngle(cur_pan + LOOK_STEP, cur_tilt)
            else:
                dm.headMoveByAngle(cur_pan - LOOK_STEP, cur_tilt)

    elif state == States.AIM_TARGET:
        print("Aiming at target")
        # Get obj info from tracker
        obj_info = tracker.getObj()

        if obj_info is not None:
            pos, _ = obj_info
            p, t = tracker.centerHeadToPoint(pos)

            dm.headMoveByAngle(p, t)

            # Rotate body until pan angle matches shooting angle
            dm.walkSetVelocities(-1.5, 0.0, -8.0)
            dm.walkStart()

            # STATE CHANGE
            if p > SHOOTING_PAN:
                dm.walkStop()

                dm.playMotion(72) # Ready bow motion

                dm.motionLoadINI(MOTION_INI)

                state = States.SHOOT
        else:
            # Go back to search target
            dm.walkStop()
            state = States.TRACK_TARGET

    elif state == States.SHOOT:
        print("Shoot.")
        sleep(1)
        dm.playMotion(73)
        state = States.FINISH

    elif state == States.FINISH:
        print("Finished.")
        pass # Do nothing
