import math
import random
import os.path
import pygame, sys, time
from pygame.math import Vector2 as vector

GAME_TITLE = 'JACKIE BOY'

WINDOW_WIDTH, WINDOW_HEIGHT = 1280, 720
TILE_SIZE = 70
ANIMATION_SPEED = 5
FPS_MAX = 60
FPS_TARGET = 60

# game states
MAIN_MENU = "Main_menu"
LIVE = "Live"
TRANSITION_LEVEL = "Transition level"
GAME_COMPLETE = "Complete complete"
IN_STORE = "In store"

# saves
SAVES_DIR = os.path.join("..", "saves")
SAVE_KEYS = ['secret_levels_unlocked', 'player_health', 'kibble', 'denta', 'stick_level', 'lance_level', 'ball_level', 'highest_stage_level']
SAVE_NEW_TEMPLATE = {
	"secret_levels_unlocked":[1], 
	"player_health":3, 
	"kibble":0,
	"denta":0,
	"stick_level":1,
	"lance_level":1,
	"ball_level":1,
	"highest_stage_level": 1
}

# overlay names
MAIN = "Main"
SAVES = "Saves"
LEVEL_SELECTOR = "Level selector"
CONTROL_HELP = "Control help"
PAUSE_MAIN = "Pause main"
CREDITS = "Credits"
STORE = "Store"

# names of layers and objects from Tiled.
TRIGGERS = "Triggers"
FG = "FG"
WATER_OBJECTS = "Water_objects"
ITEM_OBJECTS = "Item_objects"
ENEMY_OBJECTS = "Enemy_objects"
PLAYER_OBJECTS = "Player_objects"
MOVING_OBJECTS = "Moving_objects"
GENERAL_OBJECTS = "General_objects"
MID_DETAILS = "Mid_details"
PLATFORMS_PARTIAL = "Platforms_partial"
TERRAIN_L_RAMP = "Terrain_l_ramp"   # \
TERRAIN_R_RAMP = "Terrain_r_ramp"   # /
TERRAIN_FLOOR_ONLY = "Terrain_floor_only"
TERRAIN_BASIC = "Terrain_basic"
BG_DETAILS = "BG_details"
BG = "BG"
DATA = "Data"

# Layer order to be draw. Higher number is higher priority
Z_LAYERS = {
    "invis": 0,
    "bg_env": 1,
    "clouds": 2,
    "bg": 3,
    "bg_details": 4, 
    "terrain": 5,
    "mid_details": 6,
    "main": 7,
    "water": 8,
    "fg": 9
}

# Tiled, one scene w, h = 18.2, 10.2

ALIVE = "Alive"
DEAD = "Dead"

# Physics
# Player settings
PLAYER_ACCEL = 0.85
PLAYER_MAX_VEL_X = 15
PLAYER_VEL_Y = 10   # 4 tile jump gap
PLAYER_MAX_VEL_Y = 15
PLAYER_THROW_SPEED = 15

BALL_PROJECTILE = "ball_projectile"

# Environment
# note for 1:1 ramp. gravity displacement (velocity) is 1/1 of horizontal velocity rounded up. Adjusted in player.py
GRAVITY_NORM = 0.33
FRICTION = -0.12    # more negative = less slide
AIR_RESISTANCE = 0

# NPC
HUSKY = "husky"

# Enemies
ENEMY_DOG = "enemy_dog"
ENEMY_BIRD = "enemy_bird"
ENEMY_SQUIRREL = "enemy_squirrel"
ENEMY_ACORN_PROJECTILE = "acorn_projectile"
ENEMY_SIGN = "enemy_sign"

# Dog
DOG_ACCEL = 2
DOG_MAX_VEL_X = 5
DOG_VEL_Y = 6
DOG_MAX_VEL_Y = 7
# Bird
FLIGHT_ATTACK_SPEED = 6
FLIGHT_NORMAL_SPEED = 3
# Squirrel
SQ_PROJECTILE_SPEED = 12   # max x range = (v0^2 sin(2θ0))/g = 390
# SIGN
SIGN_FLIGHT_SPEED = 3
SIGN_ATTACK_FLIGHT_SPEED = 10
SIGN_SPIN_ATTACK_SPEED = 8
SIGN_POLE_PROJECTILE_SPEED = 8
POLE_PROJECTILE = "pole_projectile"

# Weapon types and names
STICK = "stick"
BALL = "ball"
LANCE = "lance"
UMBRELLA = "umbrella"

DAMAGE_COLOUR = {
    STICK: 'red',
    BALL: 'green',
    LANCE: 'blue'
}



# image_orientation offset
IMAGE_RIGHT = 90
IMAGE_UP = 180
IMAGE_LEFT = 270
IMAGE_DOWN = 0
