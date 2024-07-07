from settings import *
from sprites import Orbit
from math import atan2, degrees

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

        self.frame_index = 0
        self.state = "idle"

        # owner sprite
        self.owner = owner
        self.sk_radius = self.owner.rect.width
        self.target_angle = 0 if owner.facing_right else 180
        self.range = self.sk_radius + frames[self.state][self.frame_index].get_width()/2 - 5 # -5 to ensure within range
        self.weapon_range_rect = pygame.FRect(self.owner.hitbox_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2))



        super().__init__(damage = damage, damage_type = damage_type, level = level, attack_cooldown = attack_cooldown, attack_speed = attack_speed,
                         pos = pos, frames = frames[self.state], radius = self.sk_radius, speed = 0, start_angle = 0, end_angle = 0, clockwise = True, groups = groups, type = STICK, z = Z_LAYERS['main'], direction_changes = 0, rotate = True, image_orientation = IMAGE_RIGHT
                         )
        
        # override class AnimatedSprite attr
        self.frames = frames
        
    def check_in_range(self, player_sprite):
        # weapon range for enemy sprite
        self.weapon_range_rect = pygame.FRect(player_sprite.hitbox_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2))
        weapon_range_rect_center = self.weapon_range_rect.center
        pygame.draw.rect(pygame.display.get_surface(), "green", self.weapon_range_rect)

        if (self.weapon_range_rect.colliderect(player_sprite.hitbox_rect)):
            left_offset = 0
            slice_offset = 0
            # circle
            # x pos into the weapon_range_rect and then - self.range to get relative from center
            rel_x = player_sprite.hitbox_rect.x - self.weapon_range_rect.x - self.range
            if (player_sprite.hitbox_rect.centerx < weapon_range_rect_center[0]):
                # from left
                left_offset = player_sprite.hitbox_rect.width
                slice_offset = -1

                rel_x += left_offset

            if (rel_x < self.range):
                rel_y = math.sqrt(self.range**2 - rel_x**2)
                # create rect that slices the y at the x pos
                #weapon_range_slice_rect = pygame.FRect((weapon_range_rect.x + self.range + rel_x - left_offset - slice_offset, weapon_range_rect_center[1] - rel_y), (1, rel_y * 2))
                weapon_range_slice_rect = pygame.FRect((self.weapon_range_rect.x + self.range + rel_x + slice_offset, weapon_range_rect_center[1] - rel_y), (1, rel_y * 2))
                pygame.draw.rect(pygame.display.get_surface(), "red", weapon_range_slice_rect)
                self.owner.player_proximity["weapon_in_range"] = weapon_range_slice_rect.colliderect(player_sprite.hitbox_rect)

    def point_weapon(self, location):
        angle = degrees(atan2(location.y - self.weapon_range_rect.centery, location.x - self.weapon_range_rect.centerx))
        new_end_angle = 360 - abs(angle) if (angle < 0) else angle
        #self.move_to_angle(detected = self.owner.player_proximity["detected"], end_angle = new_end_angle, speed = 5, direction = 0, direction_changes = 1)
        self.start_angle = self.end_angle = self.angle = new_end_angle

    def enemy_point_weapon(self, player_location):
        # point weapon for enemy sprite
        if (self.owner.player_proximity["detected"]):
            # move to angle
            self.point_weapon(player_location)
        else:
            # reset
            self.start_angle = self.end_angle = self.angle = 0 if self.owner.facing_right else 180

    def attack(self):
        # Orbit
        # change speed, start_angle, end_angle, direction_changes to initiate the weapon to swing
        pass

    def get_state(self):
        if (self.owner.is_attacking):
            self.state = "attacking"
        else:
            self.state = "attacking"

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt/FPS_TARGET
        
        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]

    def update(self, dt, event_list):
        self.update_angle(dt)

        self.get_state()
        self.animate(dt)
        self.rotate_image(self.image_orientation)
