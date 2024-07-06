from random import choice, randint

from settings import *
from timerClass import Timer
from movement import Movement

# make parent enemy class later

class Dog(pygame.sprite.Sprite):

    def __init__(self, pos, frames, groups, collision_sprites = None, semi_collision_sprites = None, ramp_collision_sprites = None, player_sprites = None, enemy_sprites = None, type = ENEMY_OBJECTS):

        super().__init__(groups)
        self.display_surface = pygame.display.get_surface()
        self.z = Z_LAYERS["main"]
        self.type = type
        # weapon sprite
        self.weapon = None

        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = "idle", True
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
        # Use masking later for more accurate hit box
        self.hitbox_rect = self.rect.inflate(0, 0)
        # previous rect in previous frame to know which direction this rect came from
        self.old_rect = self.hitbox_rect.copy()

        # collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.ramp_collision_sprites = ramp_collision_sprites
        self.player_sprites = player_sprites
        self.enemy_sprites = enemy_sprites
        # self.masked_sprites = masked_sprites
        self.on_ramp_wall = False   # flag for same sprite
        self.on_ramp_slope = {"on": False, "ramp_type": None} 
        self.collision_side = {"top": False, "left": False, "bot": False, "right": False, "bot_left": False, "bot_right": False}
        self.list_collide_basic, self.list_collide_ramps, self.list_semi_collide = [], [], []
        self.platform = None
        self.detection_rect = None
        self.player_sprite = None
        self.player_proximity = {"detected": False, "weapon_in_range": False}
        self.player_location = pygame.math.Vector2(0, 0)
        

        # movement
        self.LEFT_KEY, self.RIGHT_KEY = False, False
        self.is_jumping = False
        self.jump_height = -DOG_VEL_Y
        self.gravity, self.friction = GRAVITY_NORM, -0.12   # incr frict for less slide
        #self.position = pygame.math.Vector2(self.hitbox_rect.bottomleft)
        self.accel_x = DOG_ACCEL
        self.vel_max_x = DOG_MAX_VEL_X
        self.vel_max_y = DOG_MAX_VEL_Y
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)
        self.rand_jump = randint(0, 100)

        # timer
        self.timers = {
            "wall_jump_move_block": Timer(200), # blocks the use of LEFT and RIGHT right after wall jump
            "unlock_semi_drop_down": Timer(100), # disables the floor collision for semi collision platforms so that the player can drop down through them
            "normal_attack_cooldown": Timer(500),
            "movement_duration": Timer(randint(1000, 2000))
        }

        # modules
        self.movement = Movement(self)

        #self.LEFT_KEY = True

    def fill_collide_lists(self, tar_rect):
        # tiles
        self.list_collide_basic = []
        self.list_collide_ramps = []
        self.list_semi_collide = []

        for group in [self.collision_sprites, self.semi_collision_sprites, self.ramp_collision_sprites, self.player_sprites, self.enemy_sprites]:
            for sprite in group:
                if sprite.rect.colliderect(tar_rect):
                    if (group in [self.collision_sprites, self.player_sprites] or (group in self.enemy_sprites and self != sprite)):
                        self.list_collide_basic.append(sprite)
                    elif (group == self.ramp_collision_sprites):               
                        if (sprite.type in [TERRAIN_R_RAMP, TERRAIN_L_RAMP]):
                            self.list_collide_ramps.append(sprite)
                    elif (group == self.semi_collision_sprites):
                        self.list_semi_collide.append(sprite)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt/FPS_TARGET

        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def horizontal_movement(self, dt):        
        self.movement.horizontal_movement(dt)
        self.movement.collision("horizontal", dt)

    def vertical_movement(self, dt):
        self.movement.vertical_movement(dt)
        self.movement.collision("vertical", dt)

    def jump(self):
        if (self.is_jumping):
            if (self.collision_side["bot"]):
                self.is_jumping = True
                self.velocity.y = self.jump_height
                self.hitbox_rect.bottom -= 1
            self.is_jumping = False

    def check_for_player(self):
        # detection zone
        self.detection_rect = self.hitbox_rect.inflate(300, self.weapon.range * 2)
        pygame.draw.rect(self.display_surface, "yellow", self.detection_rect)
        weapon_range_rect = pygame.FRect(self.hitbox_rect.center - pygame.Vector2(self.weapon.range, self.weapon.range), (self.weapon.range * 2, self.weapon.range * 2))
        pygame.draw.rect(pygame.display.get_surface(), "green", weapon_range_rect)
        
        for spr in self.player_sprites:
            pygame.draw.rect(self.display_surface, "yellow", spr.hitbox_rect)
            self.player_proximity["detected"] = self.detection_rect.colliderect(spr.hitbox_rect)
            if (self.player_proximity["detected"]):
                # check if player in weapon range
                self.player_sprite = spr
                self.player_location.x = spr.hitbox_rect.centerx
                self.player_location.y = spr.hitbox_rect.centery

                self.weapon.check_in_range(spr)
                break
        #print(self.player_proximity)

    def check_contact(self):
        """
        Get current collisions on the player
        """
        # hit box is 1 pixels jutting out.
        top_rect = pygame.FRect(self.hitbox_rect.topleft + vector(self.hitbox_rect.width / 4, -1), (self.hitbox_rect.width / 2, 1))
        #pygame.draw.rect(self.display_surface, "red", top_rect)
        bot_rect = pygame.FRect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 1))
        #pygame.draw.rect(self.display_surface, "red", bot_rect)
        left_rect = pygame.FRect(self.hitbox_rect.topleft + vector(-1, 0), (1, self.hitbox_rect.height * 0.8))
        #pygame.draw.rect(self.display_surface, "red", left_rect)
        right_rect = pygame.FRect(self.hitbox_rect.topright + vector(0, 0),(1, self.hitbox_rect.height * 0.8))
        #pygame.draw.rect(self.display_surface, "red", right_rect)
        bot_left_rect = pygame.FRect(self.hitbox_rect.bottomleft + vector(-1, 0), (1, TILE_SIZE + 5))
        #pygame.draw.rect(self.display_surface, "red", bot_left_rect)
        bot_right_rect = pygame.FRect(self.hitbox_rect.bottomright + vector(0, 0), (1, TILE_SIZE + 5))
        #pygame.draw.rect(self.display_surface, "red", bot_right_rect)

        terrain_rects = [sprite.rect for sprite in self.collision_sprites]

        collide_sprites = self.collision_sprites.sprites() + self.player_sprites.sprites() + self.enemy_sprites.sprites()
        collide_rects = [sprite.rect for sprite in collide_sprites if sprite != self] # i.e. specific Dog sprite should not collide with itself.

        semi_collide_rects = [sprite.rect for sprite in self.semi_collision_sprites]
        collide_ramps = [sprite for sprite in self.ramp_collision_sprites]
        
        # check collisions
        # top
        curr_top_collide = True if (top_rect.collidelist(collide_rects) >= 0) else False
        # ground - floor
        # semi-collide bottom only true if also player is falling
        curr_bot_collide = True if (bot_rect.collidelist(collide_rects) >= 0) else False
        # left
        curr_left_collide = True if (left_rect.collidelist(collide_rects) >= 0) else False
        # right
        curr_right_collide = True if (right_rect.collidelist(collide_rects) >= 0) else False
        # for enemy to not fall off.
        # bottom left
        curr_bot_left_collide = True if (bot_left_rect.collidelist(terrain_rects) >= 0 or bot_left_rect.collidelist(semi_collide_rects) >= 0) else False
        # bottom right
        curr_bot_right_collide = True if (bot_right_rect.collidelist(terrain_rects) >= 0 or bot_right_rect.collidelist(semi_collide_rects) >= 0) else False

        # semi - collisions (floor only)
        semi_collide_sprites = self.semi_collision_sprites.sprites()
        for spr in semi_collide_sprites:
            if (self.velocity.y >= 0 and bot_rect.colliderect(spr.rect) and bot_rect.top <= spr.rect.top):
                # must be "falling", collided, and bot_rect top is less than or equal than the platform top
                curr_bot_collide = True
                break

        # ramps
        for spr in collide_ramps:
            ramp_in_relation = self.movement.collision_ramp(bot_rect, spr)

            # if / else since same block
            if (bot_rect.colliderect(spr.rect) and ramp_in_relation[0]):
                curr_bot_collide = True
            elif (top_rect.colliderect(spr.rect)):
                curr_top_collide = True
            else:
                # need to check left and right for the wall side of the ramps
                if (spr.type == TERRAIN_R_RAMP):
                    # right wall of right ramp
                    if (left_rect.colliderect(spr.rect) and left_rect.right >= spr.rect.right):
                        curr_left_collide = True
                else:
                    # left wall of left ramp
                    if (right_rect.colliderect(spr.rect) and right_rect.left <= spr.rect.left):
                        curr_right_collide = True
                # ignore slope bottom edge.

            # for enemy bottom corners
            if (bot_left_rect.colliderect(spr.rect) and self.movement.collision_ramp(bot_left_rect, spr)[0]):
                curr_bot_left_collide = True
            elif (bot_right_rect.colliderect(spr.rect) and self.movement.collision_ramp(bot_right_rect, spr)[0]):
                curr_bot_right_collide = True
        
        self.collision_side["top"] = curr_top_collide
        self.collision_side["bot"] = curr_bot_collide
        self.collision_side["left"] = curr_left_collide
        self.collision_side["right"] = curr_right_collide
        self.collision_side["bot_left"] = curr_bot_left_collide
        self.collision_side["bot_right"] = curr_bot_right_collide

        # moving platform. Check if player is standing on one
        self.platform = None
        platform_sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in platform_sprites if hasattr(sprite, "moving")]:
            if (bot_rect.colliderect(sprite)):
                self.platform = sprite

        #if (self.type == ENEMY_OBJECTS):
        #    print(self.collision_side)

    def enemy_input(self):
        
        # if player in detection, charge toward x
        if (self.player_proximity["detected"]):
            self.facing_right = True if (self.hitbox_rect.x >= self.player_location.x) else False
            pass

            # if player in weapon hit zone, 50/50 rand to attack or back off. cool down for attack, if cooling down, 100 % back off.
        else: 
            # if player not in detection
            if (not self.timers["movement_duration"].active):
                # set new time and pick direction
                self.rand_jump = randint(0, 100)

                self.LEFT_KEY = choice([False, True])
                self.RIGHT_KEY = choice([False, True])
                self.facing_right = self.facing_right if (self.LEFT_KEY != self.RIGHT_KEY) else self.RIGHT_KEY

                self.timers["movement_duration"] = Timer(randint(1000, 2000))
                self.timers["movement_duration"].activate()
        
        if (self.rand_jump >= 90):
            self.is_jumping = True
            self.rand_jump = 0
            self.jump()

        # check if detect ledge that can fall off of
        if (self.collision_side["left"] or not self.collision_side["bot_left"]):
            self.LEFT_KEY = False
            self.RIGHT_KEY = True
            self.facing_right = self.RIGHT_KEY
        elif (self.collision_side["right"] or not self.collision_side["bot_right"]):
            self.LEFT_KEY = True
            self.RIGHT_KEY = False
            self.facing_right = self.RIGHT_KEY



    def update(self, dt, event_list):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()
        
        self.check_for_player()
        self.weapon.point_weapon()
        if (self.player_proximity["detected"]):
            self.facing_right = True if (self.hitbox_rect.x < self.player_location.x) else False

        #self.enemy_input()
        self.horizontal_movement(dt)
        self.vertical_movement(dt)
        # recenter image rect with the hitbox rect
        self.rect.center = self.hitbox_rect.center
        self.check_contact()
        self.movement.collision_tweak()
        self.movement.platform_move(dt)

        self.animate(dt)

        # update weapon sprite center
        self.weapon.center = self.rect.center

        # reset x vel
        if (self.velocity.x > -0.01 and self.velocity.x < 0.01):
            self.velocity.x = 0