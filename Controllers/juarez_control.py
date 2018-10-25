import pygame
import sys
from pygame.locals import *
import darwin_motions as dm
from time import sleep

DELTA_VEL = 0.5

pygame.init()
screen = pygame.display.set_mode((300, 300))

CONFIG_INI = "/home/juarez/Darwin-tools/Data/config.ini"

# Sets up all the Action, Walking, Head and Motion Manager
dm.initMotionManager(CONFIG_INI)

# Stand up in a nice motion
dm.playMotion(51)

dm.headMoveToHome()
dm.walkPrintParams()

X_AMPLITUDE = 0.0
Y_AMPLITUDE = 0.0
A_AMPLITUDE = 0.0
while True:
    # Get current values of pan and tilt
    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(1)
        elif event.type == KEYDOWN:
            if event.key == K_SPACE:
                if dm.walkIsRunning():
                    dm.walkStop()
                else:
                    dm.walkStart()
            elif event.key == K_w:
                X_AMPLITUDE += DELTA_VEL
            elif event.key == K_s:
                X_AMPLITUDE -= DELTA_VEL
            elif event.key == K_a:
                Y_AMPLITUDE += DELTA_VEL
            elif event.key == K_d:
                Y_AMPLITUDE -= DELTA_VEL
            elif event.key == K_q:
                A_AMPLITUDE += DELTA_VEL
            elif event.key == K_e:
                A_AMPLITUDE -= DELTA_VEL
            elif event.key == K_z:
                X_AMPLITUDE = 0.0
                Y_AMPLITUDE = 0.0
                A_AMPLITUDE = 0.0

            elif event.key == K_t:
                dm.playMotion(111)

    keys = pygame.key.get_pressed()

    cur_pan = dm.headGetPan()
    cur_tilt = dm.headGetTilt()
    
    # Amount to increment in each angle
    tilt_i = 0
    pan_i = 0
    mod = 1
    if keys[K_LSHIFT]:
        mod = 0.25
    if keys[K_j]:
        tilt_i += -1 * mod
    if keys[K_u]:
        tilt_i += +1 * mod
    if keys[K_h]:
        pan_i += 1 * mod
    if keys[K_k]:
        pan_i += -1 * mod

    if keys[K_o]:
        dm.headMoveToHome()
    else:
        dm.headMoveByAngle(cur_pan +pan_i, cur_tilt + tilt_i)

    dm.walkSetVelocities(X_AMPLITUDE, Y_AMPLITUDE, A_AMPLITUDE)
    print("X: {}, Y: {}, A: {}".format(X_AMPLITUDE, Y_AMPLITUDE, A_AMPLITUDE))

    sleep(0.01)
