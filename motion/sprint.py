import darwin_motions as dm
from time import sleep
import sys
sys.path.append('..')
from head_tracker import JuarezHeadTracker as JHT

MAX_P = 15
MAX_X_SPEED = 15 # Max linear velocity
UPDATE_RATE = 3 # Number of ticks
UPDATE_STEP = 0.5 # Increment in speed each update
CROSSED_LINE_OBJ_SIZE = 30000

CONFIG_INI = "/home/juarez/Darwin-Python/Sprint2/sprint.ini"

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

tracker = JHT(sys.argv[1], mode="sprint")

dm.initMotionManager(CONFIG_INI)

def updateLinearSpeed(cur_speed):
    if cur_speed >= MAX_X_SPEED:
        return MAX_X_SPEED
    else:
        return cur_speed + UPDATE_STEP

state = States.INIT
while True:
    btn = dm.getButton()
    if btn == Button.START: state = States.INIT
