from math import radians, sin, cos, atan2, degrees

from settings import *
from sprites import AnimatedSprite, ParticleEffectSprite
from movement import Movement
from timerClass import Timer

class Projectiles(AnimatedSprite):

    def __init__(self, pos, frames, groups, type = BALL, projectile_speed = 0, angle_fired = 0, owner_id = None, particle_frames = None, particle_group = None, damage = 1, level = 1):

        self.owner_id = owner_id

        self.damage = damage
        self.level = level
        
        self.particle_frames = particle_frames
        self.particle_group = particle_group

        self.frames, self.frame_index = frames, 0
        self.facing_right = True
        self.level = level if level is not None else 1
        self.level_pre = "level" + str(level) + "_"

        self.states = {
            "attack_active": self.level_pre + "attack_active"
            }
        
        self.state = self.states["attack_active"]

        super().__init__(pos, frames = frames[self.state], groups = groups, type = type, z = Z_LAYERS["main"])

        # override to center
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
        self.gravity = GRAVITY_NORM
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
                "active": Timer(5000),
                "reverse": Timer(1000)
            }
        
        # modules
        self.movement = Movement(self)

    def get_damage(self):
        return self.damage

    def get_type(self):
        return self.type

    def set_owner_id(self, owner_id):
        self.owner_id = owner_id

    def get_owner_id(self):
        return self.owner_id

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def manage_state(self):
        if (not self.timers["active"].active):
            # remove from group
            self.kill()
            #for group in self.groups():
                #group.remove(self)
            if self.particle_frames is not None and self.particle_group is not None:
                ParticleEffectSprite(self.rect.center, self.particle_frames, self.particle_group)

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
    def __init__(self, pos, frames, groups, projectile_speed, angle_fired, owner_id, particle_frames, particle_group, damage = 1, level = 1):

        super().__init__(pos = pos, frames = frames, groups = groups, type = BALL_PROJECTILE, projectile_speed = projectile_speed, angle_fired = angle_fired, owner_id = owner_id, particle_frames = particle_frames, particle_group = particle_group, damage = damage, level = level)

        # timer
        self.timers.update(
            {
                "active": Timer(6000)
            }
        )
        
        self.timers["active"].activate()

class AcornProjectile(Projectiles):
    def __init__(self, pos, frames, groups, projectile_speed, angle_fired, owner_id, particle_frames, particle_group, damage = 1, level = 1):

        super().__init__(pos = pos, frames = frames, groups = groups, type = ENEMY_ACORN_PROJECTILE, projectile_speed = projectile_speed, angle_fired = angle_fired, owner_id = owner_id, particle_frames = particle_frames, particle_group = particle_group, damage = damage, level = level)

        # timer
        self.timers.update(
            {
                "active": Timer(5000)
            }
        )

        self.timers["active"].activate()

    def reverse(self, speed, angle):
        if not self.timers["reverse"].active:
            self.projectile_speed = speed
            self.velocity.x = cos(radians(angle)) * speed
            self.velocity.y = sin(radians(angle)) * speed

            self.timers["reverse"].activate()

class PoleProjectile(Projectiles):
    def __init__(self, pos, frames, groups, projectile_speed, angle_fired, owner_id, particle_frames, particle_group, damage = 1, level = 1, image_orientation = IMAGE_RIGHT):

        super().__init__(pos = pos, frames = frames, groups = groups, type = POLE_PROJECTILE, projectile_speed = projectile_speed, angle_fired = angle_fired, owner_id = owner_id, particle_frames = particle_frames, particle_group = particle_group, damage = damage, level = level)

        self.angle = angle_fired
        self.image_orientation = image_orientation

        # timer
        self.timers.update(
            {
                "active": Timer(6000)
            }
        )
        
        self.timers["active"].activate()

        self.rotate_image()

    def rotate_image(self):
        direction = pygame.math.Vector2(math.cos(radians(self.angle)), math.sin(radians(self.angle))).normalize()
        
        angle = degrees(atan2(direction.x, direction.y))# - self.image_orientation
        self.image = pygame.transform.rotozoom(self.image, angle, 1)
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_frect(center = self.hitbox_rect.center)

    def update(self, dt, event_list):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()   # timer for active
        
        self.movement.flying_movement(dt, self.velocity)
        # recenter image rect with the hitbox rect
        self.rect.center = self.hitbox_rect.center

        self.manage_state()
        #self.animate(dt)