import pygame
import sys
from pygame.locals import *
import darwin_motions as dm
from time import sleep

pygame.init()
screen = pygame.display.set_mode((300, 300))

CONFIG_INI = "/home/juarez/Darwin-tools/Data/config.ini"

# Sets up all the Action, Walking, Head and Motion Manager
dm.initMotionManager(CONFIG_INI)

# Stand up in a nice motion
dm.playMotion(16)

dm.headMoveToHome()

while True:
    # Get current values of pan and tilt
    cur_pan = dm.headGetPan()
    cur_tilt = dm.headGetTilt()

    for event in pygame.event.get():
        if event.type == QUIT:
            sys.exit(1)

    keys = pygame.key.get_pressed()

    # Amount to increment in each angle
    tilt_i = 0
    pan_i = 0
    mod = 1
    if keys[K_LSHIFT]:
        mod = 0.25
    if keys[K_s]:
        tilt_i += -1 * mod
    if keys[K_w]:
        tilt_i += +1 * mod
    if keys[K_a]:
        pan_i += 1 * mod
    if keys[K_d]:
        pan_i += -1 * mod
    if keys[K_p]:
        print("dab")
        dm.playMotion(50)

    if keys[K_SPACE]:
        print("space")
        dm.headMoveToHome()
    else:
        dm.headMoveByAngle(cur_pan + pan_i, cur_tilt + tilt_i)


    print("Tilt:", dm.headGetTilt(), "Pan:", dm.headGetPan())

    sleep(0.01)
