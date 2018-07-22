import darwin_motions as dm
from time import sleep
from head_tracker import JuarezHeadTracker as JHT

MAX_P = 15
MAX_X_SPEED = 15 # Max linear velocity
UPDATE_RATE = 3 # Number of ticks
UPDATE_STEP = 0.5 # Increment in speed each update

tracker = JHT()

dm.initMotionManager()

# Walk ready pose
dm.playMotion(51)

dm.headMoveToHome()
dm.headMoveByAngle(0.0, 105.0)
dm.walkSetPeriodTime(580.0)
initial_xOffset = -8.0
dm.walkSetXOffset(initial_xOffset)

sleep(5)

dm.walkPrintParams()

def updateLinearSpeed(cur_speed):
    if cur_speed >= MAX_X_SPEED:
        return MAX_X_SPEED
    else:
        return cur_speed + UPDATE_STEP

ticks = 0
x_speed = 0.0 # Initial linear walking speed
while True:
    pos = tracker.getObjPosFromBGR()
    
    if pos is not None:
        dab_ticks = 0
        p, t = tracker.centerHeadToPoint(pos)

        dm.headMoveByAngle(p, t)

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

    else:
        dm.walkStop()

    print(ticks)
    print(x_speed)
    ticks += 1
