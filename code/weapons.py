from math import radians

from settings import *
from sprites import Orbit


class Weapon(Orbit):
    def __init__(self, owner, range, weapon_range_rect, damage, damage_type, level, weapon_name, damage_colour, **kwargs):
        self.damage = damage
        self.damage_type = damage_type
        self.level = level if level is not None else 1
        self.weapon_name = weapon_name
        self.damage_colour = damage_colour
        self.can_damage = False

        self.owner = owner
        self.range = range
        self.weapon_range_rect = weapon_range_rect

        super().__init__(**kwargs)

        self.target_angle = 0 if owner.facing_right else 180

        self.original_center = self.center
        self.original_radius = self.radius
        
        self.level_pre = "level" + str(level) + "_"

        self.states = {
            "idle": self.level_pre + "idle",
            "attack_active": self.level_pre + "attack_active"
            }
        
    def get_damage(self):
        return self.damage
    
    def get_type(self):
        return self.type

    def kill_weapon(self):
        self.kill()

    def set_can_damage(self, can_damage):
        self.can_damage = can_damage

    def get_can_damage(self):
        return self.can_damage

    # for enemy weapon range in relation to the player or other sprite
    def check_within_rect(self, player_sprite):
        self.owner.player_proximity["weapon_in_range"] = self.weapon_range_rect.colliderect(player_sprite.hitbox_rect)
        #pygame.draw.rect(pygame.display.get_surface(), "green", self.weapon_range_rect)

     # for enemy weapon range in relation to the player or other sprite
    def check_within_circle(self, player_sprite):
        """
        if weapon hit area is circular around owner
        I could have just used: vector(self.hitbox_rect.center).distance_to(vector(spr.hitbox_rect.center)
            I'll keep what I have now
        """
        weapon_range_rect_center = self.weapon_range_rect.center
        #pygame.draw.rect(pygame.display.get_surface(), "green", self.weapon_range_rect)

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
        # update weapon rect in relation to the owner sprite
        self.center = owner_rect.center
        self.weapon_range_rect = pygame.FRect(owner_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2))

    def enemy_point_image(self, player_location, facing_right):
        # point weapon for enemy sprite
        if (self.owner.player_proximity["detected"]):
            # move to angle
            self.point_image(self.owner.hitbox_rect.center, player_location)
        else:
            # reset
            self.start_angle = self.end_angle = self.angle = 0 if facing_right else 180      

    def hide_weapon(self, hide):
        if (hide):
            self.original_center = self.center
            self.original_radius = self.radius

            self.center = (WINDOW_WIDTH + TILE_SIZE*2, WINDOW_HEIGHT + TILE_SIZE*2)
        else:
            self.center = self.original_center
            #self.radius = self.original_radius
    
    def print_weapon_info(self):
        print(self.type)
        print(f'original_center: {self.center}')
        print(f'center: {self.center}')
        print(f'original_radius: {self.original_radius}')
        print(f'radius: {self.radius}')

    def get_state(self):
        if (self.can_damage):
            self.state = self.states["attack_active"]
        else:
            self.state = self.states["idle"]

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt/FPS_TARGET
        
        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]
        self.mask = pygame.mask.from_surface(self.image)

# types of weapons
class Ball(Weapon):
    def __init__(self, pos, groups, frames, owner, level, weapon_name = BALL):
        self.frame_index = 0
        self.state = "level1_idle"

        # owner sprite
        self.owner = owner
        self.owner_ball_offset = self.owner.rect.width / 2

        super().__init__(owner = owner, range = 0, weapon_range_rect = 0, damage = 1, damage_type = BALL, level = level, weapon_name = weapon_name, damage_colour = DAMAGE_COLOUR[BALL],
                         pos = pos, frames = frames[self.state], radius = self.owner_ball_offset, speed = 0, start_angle = 0, end_angle = 0, clockwise = True, groups = groups, type = BALL, z = Z_LAYERS['main'], direction_changes = 0, rotate = True, image_orientation = IMAGE_RIGHT
                         )
        
        self.state = self.states["idle"]

        # self.image_temp = frames[self.state][self.frame_index]
        # self.rect_temp = self.image_temp.get_frect(topleft = pos)
        
        self.range = self.owner_ball_offset + frames[self.state][self.frame_index].get_width()/2 - 5 # -5 to ensure within range (radius)
        self.weapon_range_rect = pygame.FRect(self.owner.hitbox_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2)) # rect for the weapon
        
        # override class AnimatedSprite attr
        self.frames = frames
        #print(self.z)

    def change_level(self, index, level):
        """
        creates new weapon object
        """
        if (self.level != level):
            new_ball = Ball(
                    pos = (self.owner.hitbox_rect.centerx, self.owner.hitbox_rect.centery),
                    groups = self.groups(),
                    frames = self.frames,
                    owner = self.owner,
                    level = level,
                    weapon_name = BALL
                )
            self.owner.weapon_list[index]["weapon"] = new_ball

        # remove current sprite
        self.kill()

    def check_in_range(self, player_sprite):
        # weapon range for enemy sprite
        self.check_within_circle(player_sprite)

    def update(self, dt, event_list):
        self.update_angle(dt)

        self.get_state()
        self.animate(dt)
        self.rotate_image(self.image_orientation)

class Lance(Weapon):
    def __init__(self, pos, groups, frames, owner, level, weapon_name = LANCE):
        self.frame_index = 0
        self.state = "level1_idle"

        # owner sprite
        self.owner = owner
        self.owner_lance_offset = self.owner.rect.width / 1.5

        super().__init__(owner = owner, range = 0, weapon_range_rect = 0, damage = 1, damage_type = LANCE, level = level, weapon_name = weapon_name, damage_colour = DAMAGE_COLOUR[LANCE],
                         pos = pos, frames = frames[self.state], radius = self.owner_lance_offset, speed = 0, start_angle = 0, end_angle = 0, clockwise = True, groups = groups, type = LANCE, z = Z_LAYERS['main'], direction_changes = 0, rotate = True, image_orientation = IMAGE_RIGHT
                         )
        
        self.state = self.states["idle"]

        self.range = self.owner_lance_offset + frames[self.state][self.frame_index].get_width()/2 - 5 # -5 to ensure within range (radius)
        self.weapon_range_rect = pygame.FRect(self.owner.hitbox_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2)) # rect for the weapon
        
        # override class AnimatedSprite attr
        self.frames = frames

        self.original_radius = self.radius

    def change_level(self, index, level):
        """
        creates new weapon object
        """
        if (self.level != level):
            new_lance = Lance(
                    pos = (self.owner.hitbox_rect.centerx, self.owner.hitbox_rect.centery),
                    groups = self.groups(),
                    frames = self.frames,
                    owner = self.owner,
                    level = level,
                    weapon_name = UMBRELLA
                )
            self.owner.weapon_list[index]["weapon"] = new_lance

            # remove current sprite
            self.kill()

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
    def __init__(self, pos, groups, frames, owner, level, weapon_name = STICK):
        self.frame_index = 0
        self.state = "level1_idle"

        # owner sprite
        self.owner = owner
        self.owner_stick_offset = self.owner.rect.width / 1.5

        super().__init__(owner = owner, range = 0, weapon_range_rect = 0, damage = 1, damage_type = STICK, level = level, weapon_name = weapon_name, damage_colour = DAMAGE_COLOUR[STICK],
                         pos = pos, frames = frames[self.state], radius = self.owner_stick_offset, speed = 0, start_angle = 0, end_angle = 0, clockwise = True, groups = groups, type = STICK, z = Z_LAYERS['main'], direction_changes = 0, rotate = True, image_orientation = IMAGE_RIGHT
                         )
        
        self.state = self.states["idle"]

        self.range = self.owner_stick_offset + frames[self.state][self.frame_index].get_width()/2 - 5 # -5 to ensure within range (radius)
        self.weapon_range_rect = pygame.FRect(self.owner.hitbox_rect.center - pygame.Vector2(self.range, self.range), (self.range * 2, self.range * 2)) # rect for the weapon
        
        # override class AnimatedSprite attr
        self.frames = frames
        
    def change_level(self, index, level):
        """
        creates new weapon object
        """
        if (self.level != level):
            new_stick = Stick(
                    pos = (self.owner.hitbox_rect.centerx, self.owner.hitbox_rect.centery),
                    groups = self.groups(),
                    frames = self.frames,
                    owner = self.owner,
                    level = level,
                    weapon_name = STICK
                )
            self.owner.weapon_list[index]["weapon"] = new_stick

            # remove current sprite
            self.kill()

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

class HitboxWeapon(Weapon):
    def __init__(self, pos, groups, frames, owner, level, weapon_name = HITBOX_RECT):
        self.frame_index = 0
        self.state = "level1_idle"
    
        rect = frames[self.state][self.frame_index].get_frect()

        # owner sprite
        self.owner = owner
        self.owner_offset = rect.height/2 + ((self.owner.hitbox_rect.height/2) - rect.height)
        
        self.image_orientation = IMAGE_UP

        super().__init__(owner = owner, range = 0, weapon_range_rect = 0, damage = 1, damage_type = STICK, level = level, weapon_name = weapon_name, damage_colour = DAMAGE_COLOUR[STICK],
                         pos = pos, frames = frames[self.state], radius = self.owner_offset, speed = 0, start_angle = -90, end_angle = -90, clockwise = True, groups = groups, type = STICK, z = Z_LAYERS['fg'], direction_changes = 0, rotate = True, image_orientation = self.image_orientation
                         )
        
        self.state = self.states["idle"]
        
        # override class AnimatedSprite attr
        self.frames = frames

        self.direction = pygame.math.Vector2(0, 0)

    def set_angle_info(self,direction, angle):
        self.direction = pygame.math.Vector2(direction)
        self.angle = angle
        
    def rotate_image(self):
        self.image = pygame.transform.rotozoom(self.image, self.angle, 1).convert_alpha()    # needed to convert_alpha again since it is creating a new image.
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_frect(center = self.center + self.direction * self.radius)

    def damage_active_mask(self):

        if (self.can_damage):
            # damage active image
            surface = self.mask.to_surface()
            surface.set_colorkey('black')

            surf_w, surf_h = surface.get_size()
            for x in range(surf_w):
                for y in range(surf_h):
                    if surface.get_at((x, y))[0] != 0:
                        surface.set_at((x, y), 'red')

            self.image = surface
        # else:
        #     self.image.set_alpha(0)

    def update_weapon_center(self, owner_rect):
        self.center = owner_rect.center

    # update for draw.
    # for test, draw it so I know where it is. For live, do not draw it. maybe on active damage, draw polygon
    def update(self, dt, event_list = None):
        self.get_state()
        self.animate(dt)

        self.rotate_image()

        self.damage_active_mask()

