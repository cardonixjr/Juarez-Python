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

    keys = pygame.key.get_pressed()

    dm.walkSetVelocities(X_AMPLITUDE, Y_AMPLITUDE, A_AMPLITUDE)
    print("X: {}, Y: {}, A: {}".format(X_AMPLITUDE, Y_AMPLITUDE, A_AMPLITUDE))

    sleep(0.01)
