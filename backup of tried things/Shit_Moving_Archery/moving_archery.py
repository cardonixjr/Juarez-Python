import darwin_motions as dm
from time import sleep
import sys
sys.path.append('..')
import math
from head_tracker import JuarezHeadTracker as JHT

WALKING_INI = "/home/juarez/Darwin-Python/Archery/walking_archery.ini"
MOTION_INI = "/home/juarez/Darwin-Python/Archery/motion_archery.ini"

SHOOTING_PAN = 71.00
LOOK_STEP = 0.5

POS_TOLERANCE = 1 # Degrees

class States:
    INIT = -1
    READY = 0
    FIND_TARGET = 1
    OBSERVE_TARGET = 2
    AIM_TARGET = 3
    WAIT_LOWEST_POS = 4
    SHOOT = 5
    FINISH = 6

class Button:
    START = 2
    RESET = 1
    NONE = 0

class TargetInfo:
    alpha = 0.5 # Instantenous
    beta = 0.5 # Memory

    def __init__(self):
        self.ticks = 0 # Amount of ticks the target has been observed
        self.area = 0.0
        self.avg_dx = 0.0 # Variation in X
        self.avg_dy = 0.0 # Variation in Y

        self.lowest_y = 360.0 # Initialized with a number bigger than "possible"
        self.x_for_lowest_y = None

    def observe(self, x, y):
        # First observation
        if self.ticks == 0: 
            # Save positions for next iteration
            self.last_x = x
            self.last_y = y

            self.ticks += 1
            return

        if y < self.lowest_y:
            self.lowest_y = y
            self.x_for_lowest_y = x

        # Calculate deltas
        dx = x - self.last_x
        dy = y - self.last_y

        self.last_x = x
        self.last_y = y

        #print("Dx:", dx)
        #print("Dy:", dy)

        # Calculate average dx and dy with moving average parameters
        self.avg_dx = (self.alpha * dx) + (self.beta * self.avg_dx)
        self.avg_dy = (self.alpha * dy) + (self.beta * self.avg_dy)

        self.ticks += 1

# Load tracker with .json color from command line
tracker = JHT(sys.argv[1])

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
        dm.headMoveByAngle(90, 90)
        look_dir = 1 # This is used to change directions when looking for the target
        
        state = States.READY

    elif state == States.READY:
        print("Ready.")
        # Wait for the start button press

        if btn == Button.START: state = States.FIND_TARGET

    # Look for target
    elif state == States.FIND_TARGET:
        print("Find Target.")
        # Get obj info from tracker
        obj_info = tracker.getObj()

        if obj_info is not None:
            pos, _ = obj_info
            p, t = tracker.centerHeadToPoint(pos)

            dm.headMoveByAngle(p, t)

            ### STATE CHANGE STUFF ###
            target_info = TargetInfo()
            state = States.OBSERVE_TARGET
            ##########################

        else:
            cur_pan = dm.headGetPan()
            cur_tilt = dm.headGetTilt()

            if cur_pan > 120:
                look_dir = 0
            elif cur_pan < 0:
                look_dir = 1

            if look_dir == 1:
                dm.headMoveByAngle(cur_pan + LOOK_STEP, cur_tilt)
            else:
                dm.headMoveByAngle(cur_pan - LOOK_STEP, cur_tilt)

    # Observe target motion to predict its position later
    elif state == States.OBSERVE_TARGET:
        print("Observe Target.")

        # Get obj info from tracker
        obj_info = tracker.getObj()

        if obj_info is not None:
            pos, _ = obj_info
            p, t = tracker.centerHeadToPoint(pos)

            dm.headMoveByAngle(p, t)

            # Convert head angles reading to polar coordinates
            angle = math.atan2(math.radians(t), math.radians(p))
            r = math.sqrt((p ** 2) + (t ** 2))

            polar_x = r * math.cos(angle)
            polar_y = r * math.sin(angle)
            print("Angle:", math.degrees(angle), "r:", r, "X:", polar_x, "Y:", polar_y)

            # Register observation with polar coordinates
            target_info.observe(polar_x, polar_y)

            print("Lowest Y:", target_info.lowest_y)
            print("X for lowest Y:", target_info.x_for_lowest_y)

            print("Avg Dx:", target_info.avg_dx, "Avg Dy:", target_info.avg_dy)

            print(target_info.ticks)
            #if target_info.ticks > 300:
            #    state = States.WAIT_LOWEST_POS

        else:
            state = States.FIND_TARGET

#    elif state == States.AIM_TARGET:
#        print("Aiming at target")
#        # Get obj info from tracker
#
#        pos = (target_info.x_for_lowest_y, target_info.lowest_y)
#        p, t = tracker.centerHeadToPoint(pos)
#        print(p, t)
#
#        dm.headMoveByAngle(p, t)
#
#        # Rotate body until pan angle matches shooting angle
#        dm.walkSetVelocities(-1.5, 0.0, -8.0)
#        dm.walkStart()
#
#        # STATE CHANGE
#        if p > SHOOTING_PAN:
#            dm.walkStop()
#
#            dm.playMotion(72) # Ready bow motion
#
#            dm.motionLoadINI(MOTION_INI)
#
#            state = States.SHOOT

    elif state == States.WAIT_LOWEST_POS:
        print("Wait Lowest Pos")
        # Get obj info from tracker
        obj_info = tracker.getObj()

        if obj_info is not None:
            pos, _ = obj_info
            p, t = tracker.centerHeadToPoint(pos)

            dm.headMoveByAngle(p, t)

            print("Current t:", t, "Lowest:", target_info.lowest_y)
            if (t >= (target_info.lowest_y - POS_TOLERANCE) and t <= (target_info.lowest_y + POS_TOLERANCE)):
                dm.playMotion(72)
            
                dm.motionLoadINI(MOTION_INI)

                state = States.SHOOT

    elif state == States.SHOOT:
        print("Shoot.")
        sleep(1)
        dm.playMotion(73)
        print("Finished.")
        state = States.FINISH

    elif state == States.FINISH:
        #print("Finished.")
        pass # Do nothing
