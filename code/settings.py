import math
import os.path
import pygame, sys, time
from pygame.math import Vector2 as vector



WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 70
ANIMATION_SPEED = 6
FPS_MAX = 60
FPS_TARGET = 60

# layers. Highest priority top
TERRAIN_L_RAMP = "Terrain_l_ramp"   # \
TERRAIN_R_RAMP = "Terrain_r_ramp"   # /
TERRAIN_BASIC = "Terrain_basic"
BG = "BG"

# Tiled. w, h = 18.2, 10.2

# Physics
# Player settings
PLAYER_ACCEL = 0.75
PLAYER_MAX_VEL_X = 15
PLAYER_VEL_Y = 10   # 4 tile jump gap

# Environment
GRAVITY = 0.35