from settings import *
from sprites import Orbit

class Weapon(Orbit):
    def __init__(self, owner, range, weapon_range_rect, damage, damage_type, level, **kwargs):
        self.damage = damage
        self.damage_type = damage_type
        self.level = level
        self.can_damage = False

        self.owner = owner
        self.range = range
        self.weapon_range_rect = weapon_range_rect

        super().__init__(**kwargs)

    def set_can_damage(self, can_damage):
        self.can_damage = can_damage

    def check_within_rect(self, player_sprite):
        self.owner.player_proximity["weapon_in_range"] = self.weapon_range_rect.colliderect(player_sprite.hitbox_rect)
        #pygame.draw.rect(pygame.display.get_surface(), "green", self.weapon_range_rect)

    def check_within_circle(self, player_sprite):
        """
        if weapon hit area is circular around owner
        I could have just used: vector(self.hitbox_rect.center).distance_to(vector(spr.hitbox_rect.center)
            I'll keep what I have now
        """
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
                #pygame.draw.rect(pygame.display.get_surface(), "red", weapon_range_slice_rect)
                self.owner.player_proximity["weapon_in_range"] = weapon_range_slice_rect.colliderect(player_sprite.hitbox_rect)
            else:
                self.owner.player_proximity["weapon_in_range"] = False
        else:
            self.owner.player_proximity["weapon_in_range"] = False

    def update_weapon_zone(self, owner_rect):
        self.center = owner_rect.center
        self.weapon_range_rect = pygame.FRect(owner_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2))

    def enemy_point_image(self, player_location, facing_right):
        # point weapon for enemy sprite
        if (self.owner.player_proximity["detected"]):
            # move to angle
            self.point_image(self.owner.hitbox_rect, player_location)
        else:
            # reset
            self.start_angle = self.end_angle = self.angle = 0 if facing_right else 180

    def get_state(self):
        if (self.can_damage):
            self.state = "attack_active"
        else:
            self.state = "idle"

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt/FPS_TARGET
        
        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]

# types of weapons
class Ball(Weapon):
    def __init__(self, pos, groups, frames, owner, damage, damage_type, level):
        self.frame_index = 0
        self.state = "idle"

        # owner sprite
        self.owner = owner
        self.owner_ball_offset = self.owner.rect.width / 2
        self.target_angle = 0 if owner.facing_right else 180

        self.image_temp = frames[self.state][self.frame_index]
        self.rect_temp = self.image_temp.get_frect(topleft = pos)

        self.range = self.owner_ball_offset + frames[self.state][self.frame_index].get_width()/2 - 5 # -5 to ensure within range (radius)
        self.weapon_range_rect = pygame.FRect(self.owner.hitbox_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2)) # rect for the weapon

        super().__init__(owner = owner, range = self.range, weapon_range_rect = self.weapon_range_rect, damage = damage, damage_type = damage_type, level = level,
                         pos = pos, frames = frames[self.state], radius = self.owner_ball_offset, speed = 0, start_angle = 0, end_angle = 0, clockwise = True, groups = groups, type = STICK, z = Z_LAYERS['main'], direction_changes = 0, rotate = True, image_orientation = IMAGE_RIGHT
                         )
        
        # override class AnimatedSprite attr
        self.frames = frames

        self.original_center = self.center
        self.original_radius = self.radius

    def hide_ball(self, hide):
        if (hide):
            self.original_center = self.center
            self.original_radius = self.radius

            self.center = (0, 0)
            self.radius = 0
        else:
            self.center = self.original_center
            self.radius = self.original_radius

    def check_in_range(self, player_sprite):
        # weapon range for enemy sprite
        self.check_within_circle(player_sprite)

    def update(self, dt, event_list):
        self.update_angle(dt)

        self.get_state()
        self.animate(dt)
        self.rotate_image(self.image_orientation)

class Lance(Weapon):
    def __init__(self, pos, groups, frames, owner, damage, damage_type, level):
        self.frame_index = 0
        self.state = "idle"

        # owner sprite
        self.owner = owner
        self.owner_lance_offset = self.owner.rect.width
        self.target_angle = 0 if owner.facing_right else 180

        self.range = self.owner_lance_offset + frames[self.state][self.frame_index].get_width()/2 - 5 # -5 to ensure within range (radius)
        self.weapon_range_rect = pygame.FRect(self.owner.hitbox_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2)) # rect for the weapon

        super().__init__(owner = owner, range = self.range, weapon_range_rect = self.weapon_range_rect, damage = damage, damage_type = damage_type, level = level,
                         pos = pos, frames = frames[self.state], radius = self.owner_lance_offset, speed = 0, start_angle = 0, end_angle = 0, clockwise = True, groups = groups, type = STICK, z = Z_LAYERS['main'], direction_changes = 0, rotate = True, image_orientation = IMAGE_RIGHT
                         )
        
        # override class AnimatedSprite attr
        self.frames = frames

    def check_in_range(self, player_sprite):
        # weapon range for enemy sprite
        self.check_within_circle(player_sprite)

    def update(self, dt, event_list):
        self.update_angle(dt)

        self.get_state()
        self.animate(dt)
        self.rotate_image(self.image_orientation)

# class Stick(Weapon, Orbit):
class Stick(Weapon):
    def __init__(self, pos, groups, frames, owner, damage, damage_type, level):

        self.frame_index = 0
        self.state = "idle"

        # owner sprite
        self.owner = owner
        self.owner_stick_offset = self.owner.rect.width
        self.target_angle = 0 if owner.facing_right else 180
        
        self.range = self.owner_stick_offset + frames[self.state][self.frame_index].get_width()/2 - 5 # -5 to ensure within range (radius)
        self.weapon_range_rect = pygame.FRect(self.owner.hitbox_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2)) # rect for the weapon

        super().__init__(owner = owner, range = self.range, weapon_range_rect = self.weapon_range_rect, damage = damage, damage_type = damage_type, level = level,
                         pos = pos, frames = frames[self.state], radius = self.owner_stick_offset, speed = 0, start_angle = 0, end_angle = 0, clockwise = True, groups = groups, type = STICK, z = Z_LAYERS['main'], direction_changes = 0, rotate = True, image_orientation = IMAGE_RIGHT
                         )
        
        # override class AnimatedSprite attr
        self.frames = frames
        
    def check_in_range(self, player_sprite):
        # weapon range for enemy sprite
        self.check_within_circle(player_sprite)

    def swing(self, start_angle, end_angle, speed, clockwise, direction_changes):
        self.orbit_to_angle(start_angle, end_angle, speed, clockwise, direction_changes)

    def update(self, dt, event_list):
        self.update_angle(dt)

        self.get_state()
        self.animate(dt)
        self.rotate_image(self.image_orientation)
