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
HOW_TO_PLAY = "How to play"

# music keys
MUSIC_MAIN = "main"
MUSIC_GAME = "game"
MUSIC_CRED = "credits"
MUSIC_BOSS = "boss"
MUSIC_TRANS = "trans"

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

HITBOX_RECT = "hitbox_rect"



# image_orientation offset
IMAGE_RIGHT = 90
IMAGE_UP = 180
IMAGE_LEFT = 270
IMAGE_DOWN = 0

# Controls
CNTRL_WEAPON_1 = "weapon 1"
CNTRL_WEAPON_2 = "weapon 2"
CNTRL_WEAPON_3 = "weapon 3"
CNTRL_JUMP = "jump"
CNTRL_MOVE_LEFT = "left"
CNTRL_MOVE_RIGHT = "right"
CNTRL_MOVE_DOWN = "drop down"
CNTRL_ESC = "escape"
CNTRL_INTERACT = "interact"

PYGAME_CONST = "pygame_const"
KEY = "key"
DESC = "desc"

CONTROLS = {
    CNTRL_WEAPON_1: {
        PYGAME_CONST: pygame.K_1,
        KEY: "1",
        DESC: "Switch to weapon 1"
    },
    CNTRL_WEAPON_2: {
        PYGAME_CONST: pygame.K_2,
        KEY: "2",
        DESC: "Switch to weapon 2"
    },
    CNTRL_WEAPON_3: {
        PYGAME_CONST: pygame.K_3,
        KEY: "3",
        DESC: "Switch to weapon 3"
    },
    CNTRL_JUMP: {
        PYGAME_CONST: pygame.K_SPACE,
        KEY: "Space",
        DESC: "Jump"
    },
    CNTRL_MOVE_LEFT: {
        PYGAME_CONST: pygame.K_a,
        KEY: "A",
        DESC: "Move left"
    },
    CNTRL_MOVE_RIGHT: {
        PYGAME_CONST: pygame.K_d,
        KEY: "D",
        DESC: "Move right"
    },
    CNTRL_MOVE_DOWN: {
        PYGAME_CONST: pygame.K_s,
        KEY: "S",
        DESC: "Drop down"
    },
    CNTRL_ESC: {
        PYGAME_CONST: pygame.K_ESCAPE,
        KEY: "Esc",
        DESC: "Exit pause menu"
    },
    CNTRL_INTERACT: {
        PYGAME_CONST: pygame.K_f,
        KEY: "F",
        DESC: "Interact"
    }
}


