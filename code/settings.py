import os.path
import pygame, sys, time
from pygame.math import Vector2 as vector


WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 70
ANIMATION_SPEED = 6
FPS_MAX = 60
FPS_TARGET = 60

# layers. Highest priority top
TERRAIN_BASIC = "Terrain_basic"
TERRAIN_R_RAMP = "Terrain_r_ramp"
TERRAIN_L_RAMP = "Terrain_l_ramp"


# Tiled. w, h = 18.2, 10.2