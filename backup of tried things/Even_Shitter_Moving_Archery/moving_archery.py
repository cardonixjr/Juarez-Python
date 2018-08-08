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

POS_TOLERANCE = 2.0 # Degrees

SHOOT_MOTION_TICKS = 230 # How many ticks the shooting motion takes

class States:
    INIT = -1
    READY = 0
    FIND_TARGET = 1
    OBSERVE_TARGET_1 = 2
    AIM_TARGET = 3
    WAIT_LOWEST_POS = 4
    SHOOT = 5
    FINISH = 6

class Button:
    START = 2
    RESET = 1
    NONE = 0

def checkPosWithinTolerance(pos1, pos2):
    if math.sqrt(((pos2[0] - pos1[0]) ** 2) + (pos2[1] - pos1[1]) ** 2) < POS_TOLERANCE:
        return True
    else:
        return False

def distBetweenPos(pos1, pos2):
    return math.sqrt(((pos2[0] - pos1[0]) ** 2) + (pos2[1] - pos1[1]) ** 2)

class TargetInfo:
    def __init__(self):
        self.ticks = 0 # Amount of ticks the target has been observed
        self.pos_list = [] # Positions the target has been seen
        self.period = None # Amount of ticks in a period
        self.lowest_tick = None
        self.lowest_pos = None
        
    # Observe target movement, returns True once a position repeats (within a tolerance)
    def observe(self, x, y):
        # First observation
        if self.ticks == 0:
            self.pos_list.append((x, y))
            self.ticks += 1

            return False
        
        # Check if current position is the same as the first element of the list,
        # which means the target has completed a period
        print("X, Y - first element of list")
        self.ticks += 1

        # Finished a complete circle
        if checkPosWithinTolerance((x, y), self.pos_list[0]) and self.ticks > 50:
            self._calclowestYPos()
            self.period = self.ticks
            return True
        # Not yet
        else:
            self.pos_list.append((x, y))
            return False

    # Retrieve position and tick number for lowest Y position
    def _calclowestYPos(self):
        lowest_Y = 360.0 # Huge number
        lowest_tick = None
        lowest_pos = None
        for i, p in enumerate(self.pos_list):
            if p[1] < lowest_Y:
                lowest_Y = p[1]
                lowest_tick = i
                lowest_pos = p

        self.lowest_pos = lowest_pos
        self.lowest_tick = lowest_tick

    # Given a position returns the index of the nearest position in pos_list
    def getPositionTick(self, pos):
        nearest_dist = distBetweenPos(self.pos_list[0], pos)
        nearest_i = 0
        i = 1
        for p in self.pos_list[1:]:
            cur_dist = distBetweenPos(p, pos)
            if cur_dist < nearest_dist:
                nearest_dist = cur_dist
                nearest_i = i

            i += 1

        return nearest_i

    def measureTickDistance(self, cur_tick, goal_tick):
        a = goal_tick - cur_tick
        if a > 0:
            return a
        else:
            return self.period + a


# Load tracker with .json color from command line
tracker = JHT(sys.argv[1], mode='single')

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
        dm.headMoveByAngle(70, 90)
        look_dir = 1 # This is used to change directions when looking for the target
        
        state = States.READY

    elif state == States.READY:
        print("Ready.")
        # Wait for the start button press

        if btn == Button.START: 
            find_ticks = 0 # Used in FIND_TARGET STATE
            state = States.FIND_TARGET

    # Look for target
    elif state == States.FIND_TARGET:
        print("Find Target.")
        # Get obj info from tracker
        obj_info = tracker.getObj()

        if obj_info is not None:
            find_ticks += 1
            pos, _ = obj_info
            p, t = tracker.centerHeadToPoint(pos)

            dm.headMoveByAngle(p, t)

            ### STATE CHANGE STUFF ###
            # Count some ticks to center motion on target before next state
            if find_ticks == 100:
                missing_ticks = 0
                target_info = TargetInfo()
                state = States.OBSERVE_TARGET_1
            ##########################

        else:
            # Missed target, find_ticks reset to 0
            find_ticks = 0

            cur_pan = dm.headGetPan()
            cur_tilt = dm.headGetTilt()

            if cur_pan > 100:
                look_dir = 0
            elif cur_pan < 60:
                look_dir = 1

            if look_dir == 1:
                dm.headMoveByAngle(cur_pan + LOOK_STEP, cur_tilt)
            else:
                dm.headMoveByAngle(cur_pan - LOOK_STEP, cur_tilt)

    # Observe target motion to predict its position later
    elif state == States.OBSERVE_TARGET_1:
        print("Observe Target.")

        # Get obj info from tracker
        obj_info = tracker.getObj()

        if obj_info is not None:
            missing_ticks = 0 

            pos, _ = obj_info
            p, t = tracker.centerHeadToPoint(pos)

            dm.headMoveByAngle(p, t)

            finished_period = target_info.observe(p, t)
            if finished_period == True:
                print("Finished a period, ticks:", target_info.period)
                state = States.WAIT_LOWEST_POS

        else:
            print("Missed a frame.")
            missing_ticks += 1

            if missing_ticks == 15:
                state = States.FIND_TARGET

    elif state == States.WAIT_LOWEST_POS:
        print("Wait Lowest Pos")
        # Get obj info from tracker
        obj_info = tracker.getObj()

        if obj_info is not None:
            pos, _ = obj_info
            p, t = tracker.centerHeadToPoint(pos)

            dm.headMoveByAngle(p, t)

            print("Current pos:", (p, t), "Lowest:", target_info.lowest_pos)

            cur_tick = target_info.getPositionTick((p, t))
            print("Current pos tick:", cur_tick, "Lowest pos tick:", target_info.lowest_tick)
            dist = target_info.measureTickDistance(cur_tick, target_info.lowest_tick)

            if dist == 230:
                dm.playMotion(72)
            
                dm.motionLoadINI(MOTION_INI)

                #### STATE CHANGE ####
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
