import darwin_motions as dm
from time import sleep
import sys
sys.path.append('..')
from head_tracker import JuarezHeadTracker as JHT

MAX_P = 15
MAX_X_SPEED = 15 # Max linear velocity
UPDATE_RATE = 3 # Number of ticks
UPDATE_STEP = 0.5 # Increment in speed each update
CROSSED_LINE_OBJ_SIZE = 129000

class States:
    RUNNING_FORWARD = 0
    RUNNING_BACKWARDS = 1
    BACKWARDS_RECENTER = 2

tracker = JHT(sys.argv[1])

dm.initMotionManager()

# Walk ready pose
dm.playMotion(51)

dm.headMoveToHome()
dm.headMoveByAngle(0.0, 105.0)
dm.walkSetPeriodTime(580.0)

dm.walkPrintParams()

sleep(5)

def updateLinearSpeed(cur_speed):
    if cur_speed >= MAX_X_SPEED:
        return MAX_X_SPEED
    else:
        return cur_speed + UPDATE_STEP

current_state = States.RUNNING_FORWARD
ticks = 0
x_speed = 0.0 # Initial linear walking speed
while True:
    obj = tracker.getObj()

    if obj is not None:
        pos, area = obj
        p, t = tracker.centerHeadToPoint(pos)

        dm.headMoveByAngle(p, t)

    else:
        dm.walkStop()
        print("Object not detected this iteration.")
        continue # Skip this loop

    if current_state == States.RUNNING_FORWARD:
        print("walk forward")
        if ticks % UPDATE_RATE == 0:
            x_speed = updateLinearSpeed(x_speed)

        if p > MAX_P:
            p = MAX_P
            dm.walkSetVelocities(6.0, 0.0, p)
        elif p < -MAX_P:
            p = -MAX_P
            dm.walkSetVelocities(6.0, 0.0, p)
        else:
            dm.walkSetVelocities(x_speed, 0.0, p)

        dm.walkStart()

        if area > CROSSED_LINE_OBJ_SIZE:
            # Changing State
            current_state = States.RUNNING_BACKWARDS
            #dm.walkSetZOffset(40.0)
            #dm.walkSetPeriodTime(550.0)
            dm.walkStop()
            sleep(0.2)

    elif current_state == States.RUNNING_BACKWARDS:
        print("walk backwards")
        dm.walkSetVelocities(-8.0, -1.0, -7.5)
        if p > 15.0 or p < -12.0:
            current_state = States.BACKWARDS_RECENTER

        dm.walkStart()

    elif current_state == States.BACKWARDS_RECENTER:
        print("backwards recenter")
        if p > 5.0:
            dm.walkSetVelocities(-1.0, 0.0, 7.0)
        elif p < -1.0:
            print(p)
            dm.walkSetVelocities(-1.0, 0.0, -15.0)
        else:
            current_state = States.RUNNING_BACKWARDS


    print(ticks)
    print(x_speed)
    ticks += 1
