import darwin_motions as dm
from time import sleep
import sys
sys.path.append('..')
from head_tracker import JuarezHeadTracker as JHT

SHOOTING_PAN = 70.0

class States:
    READY = 0
    TRACK_TARGET = 1
    AIM_TARGET = 2
    SHOOT = 3

# Load tracker with .json color from command line
tracker = JHT(sys.argv[1])

dm.initMotionManager("/home/juarez/Darwin-Python/Archery/walking_archery.ini")

state = States.READY
while True:
    if state == States.READY:
        dm.playMotion(51) # Walk ready motion
        sleep(5)
        state = States.TRACK_TARGET

    elif state == States.TRACK_TARGET:
        # Get obj info from tracker
        obj_info = tracker.getObj()

        if obj is not None:
            pos, _ = obj
            p, t = tracker.centerHeadToPoint(pos)

            dm.headMoveByAngle(p, t)

            print("Current pan:", p)
