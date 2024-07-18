from math import radians, sin, cos

from settings import *
from sprites import AnimatedSprite
from movement import Movement
from timerClass import Timer

class Projectiles(AnimatedSprite):

    def __init__(self, pos, frames, groups, type = "projectile", projectile_speed = 0, angle_fired = 0, owner_id = None):

        self.owner_id = owner_id

        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = "idle", True
        self.image = self.frames[self.state][self.frame_index]

        super().__init__(pos, frames = frames[self.state], groups = groups, type = type, z = Z_LAYERS["main"])

        self.rect = self.image.get_frect(center = pos)
        self.hitbox_rect = self.rect.inflate(0, 0)
        self.old_rect = self.hitbox_rect.copy()
        self.mask = pygame.mask.from_surface(self.image)

        self.z = Z_LAYERS["main"]
        self.type = type

        # collision flags
        # self.masked_sprites = masked_sprites
        self.on_ramp_wall = False   # flag for same sprite
        self.on_ramp_slope = {"on": False, "ramp_type": None} 
        self.collision_side = {"top": False, "left": False, "bot": False, "right": False, "bot_left": False, "bot_right": False}

        # movement
        self.LEFT_KEY, self.RIGHT_KEY = False, False
        self.is_jumping = False
        self.gravity, self.friction = GRAVITY_NORM, FRICTION   # incr frict for less slide
        #self.position = pygame.math.Vector2(self.hitbox_rect.bottomleft)
        self.accel_x = projectile_speed
        self.vel_max_x = projectile_speed
        self.vel_max_y = projectile_speed
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        self.projectile_speed = projectile_speed
        self.friction = AIR_RESISTANCE
        self.velocity.x = cos(radians(angle_fired)) * projectile_speed
        self.velocity.y = sin(radians(angle_fired)) * projectile_speed

        # timer
        self.timers = {
                "active": Timer(5000)
            }
        
        # modules
        self.movement = Movement(self)

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def manage_state(self):
        if (not self.timers["active"].active):
            # remove from group
            self.kill()
            #for group in self.groups():
                #group.remove(self)

    def update(self, dt, event_list):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()   # timer for active
        
        self.movement.horizontal_movement(dt)
        self.movement.vertical_movement(dt)
        # recenter image rect with the hitbox rect
        self.rect.center = self.hitbox_rect.center

        self.manage_state()
        #self.animate(dt)

class BallProjectile(Projectiles):
    def __init__(self, pos, frames, groups, projectile_speed, angle_fired, owner_id):

        super().__init__(pos = pos, frames = frames, groups = groups, type = "ball_projectile", projectile_speed = projectile_speed, angle_fired = angle_fired, owner_id = owner_id)

        # timer
        self.timers = {
                "active": Timer(6000)
            }
        
        self.timers["active"].activate()

class AcornProjectile(Projectiles):
    def __init__(self, pos, frames, groups, projectile_speed, angle_fired, owner_id):

        super().__init__(pos = pos, frames = frames, groups = groups, type = "acorn_projectile", projectile_speed = projectile_speed, angle_fired = angle_fired, owner_id = owner_id)

        # timer
        self.timers.update(
            {
                "active": Timer(5000)
            }
        )

        self.timers["active"].activate()