from settings import *
from sprites import Orbit

class Weapon():
    def __init__(self, damage, damage_type, level, attack_cooldown, attack_speed, **kwargs):
        self.damage = damage
        self.damage_type = damage_type
        self.level = level
        self.attack_cooldown = attack_cooldown
        self.attack_speed = attack_speed

        super().__init__(**kwargs)

class Stick(Weapon, Orbit):
    def __init__(self, pos, groups, frames, owner, damage, damage_type, level, attack_cooldown, attack_speed):
        # owner sprite
        self.owner = owner
        self.radius = self.owner.rect.width
        self.target_angle = 0 if owner.facing_right else 180
        self.start_angle = self.end_angle = self.target_angle

        super().__init__(damage = damage, damage_type = damage_type, level = level, attack_cooldown = attack_cooldown, attack_speed = attack_speed,
                         pos = pos, frames = frames, radius = self.radius, speed = 1, start_angle = 180, end_angle = -1, groups = groups, type = STICK, z = Z_LAYERS['main'], direction_changes= -1, rotate = True
                         )
        
    def attack(self):
        # Orbit
        # change speed, start_angle, end_angle, direction_changes to initiate the weapon to swing
        pass
