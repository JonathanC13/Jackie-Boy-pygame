import math
import os.path
import pygame, sys, time
from pygame.math import Vector2 as vector



WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 70
ANIMATION_SPEED = 6
FPS_MAX = 60
FPS_TARGET = 60

# names of layers and objects from Tiled.
FG = "FG"
GENERAL_OBJECTS = "General_objects"
PLAYER_OBJECTS = "Player_objects"
MOVING_OBJECTS = "Moving_objects"
PLATFORMS_PARTIAL = "Platforms_partial"
TERRAIN_L_RAMP = "Terrain_l_ramp"   # \
TERRAIN_R_RAMP = "Terrain_r_ramp"   # /
TERRAIN_FLOOR_ONLY = "Terrain_floor_only"
TERRAIN_BASIC = "Terrain_basic"
BG_DETAILS = "BG_details"
BG = "BG"

# Layer order to be draw. Higher number is higher priority
Z_LAYERS = {
    "bg": 0,
    "clouds": 1,
    "bg_tiles": 2,
    "path": 3,
    "bg_details": 4,
    "main": 5,      # game entities that are interactable
    "water": 6,
    "fg": 7
}

# Tiled. w, h = 18.2, 10.2

# Physics
# Player settings
PLAYER_ACCEL = 0.85
PLAYER_MAX_VEL_X = 15
PLAYER_VEL_Y = 10   # 4 tile jump gap
PLAYER_MAX_VEL_Y = 15

# Environment
# note for 1:1 ramp. gravity displacement (velocity) is 1/1 of horizontal velocity rounded up. Adjusted in player.py
GRAVITY_NORM = 0.33