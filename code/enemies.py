from random import choice, randint
from math import atan2, degrees

from settings import *
from timerClass import Timer
from movement import Movement

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites = None, semi_collision_sprites = None, ramp_collision_sprites = None, player_sprites = None, enemy_sprites = None, type = ENEMY_OBJECTS, jump_height = -DOG_VEL_Y, accel_x = DOG_ACCEL, vel_max_x = DOG_MAX_VEL_X, vel_max_y = DOG_MAX_VEL_Y):
        super().__init__(groups)

        self.display_surface = pygame.display.get_surface()

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

        self.z = Z_LAYERS["main"]
        self.type = type
        # weapon sprite
        self.weapon = None

        # collision flags
        # self.masked_sprites = masked_sprites
        self.on_ramp_wall = False   # flag for same sprite
        self.on_ramp_slope = {"on": False, "ramp_type": None} 
        self.collision_side = {"top": False, "left": False, "bot": False, "right": False, "bot_left": False, "bot_right": False}
        self.list_collide_basic, self.list_collide_ramps, self.list_semi_collide = [], [], []
        self.platform = None

        # player detection
        self.detection_rect = None
        self.player_sprite_detected = None
        self.player_proximity = {"detected": False, "weapon_in_range": False}
        self.player_location = pygame.math.Vector2(0, 0)
        self.weapon_range_rect = None

        # movement
        self.LEFT_KEY, self.RIGHT_KEY = False, False
        self.is_jumping = False
        self.gravity, self.friction = GRAVITY_NORM, -0.12   # incr frict for less slide
        self.jump_height = -DOG_VEL_Y
        #self.position = pygame.math.Vector2(self.hitbox_rect.bottomleft)
        self.accel_x = DOG_ACCEL
        self.vel_max_x = DOG_MAX_VEL_X
        self.vel_max_y = DOG_MAX_VEL_Y
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)
        self.rand_jump = randint(0, 100)

        # attack patterns
        self.is_attacking = False
        self.attack_patterns = {
            "attack_delay": [{"timer_name":"attack_delay", "func": self.attack_delay}]
        }
        self.attack_seq, self.attack_seq_len, self.attack_index = self.attack_patterns["attack_delay"], 0, 0
        self.current_attack = None
        
        # timer
        self.timers = {
            "wall_jump_move_block": Timer(200), # blocks the use of LEFT and RIGHT right after wall jump. // for player
            "unlock_semi_drop_down": Timer(100), # disables the floor collision for semi collision platforms so that the player can drop down through them // for player
            "movement_duration": Timer(randint(1000, 2000)),
            "attack_delay": Timer(1000)
        }

        # modules
        self.movement = Movement(self)

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt/FPS_TARGET

        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def get_state(self):
        if (self.current_attack is not None):
            self.state = self.current_attack
        elif (self.LEFT_KEY or self.RIGHT_KEY):
            self.state = "run"
        else:
            self.state = "idle"

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

        # basic terrain tiles
        terrain_rects = [sprite.rect for sprite in self.collision_sprites]

        # grouping all basic collidable sprites
        collide_sprites = self.collision_sprites.sprites() + self.player_sprites.sprites() + self.enemy_sprites.sprites()
        collide_rects = [sprite.hitbox_rect if sprite.type == PLAYER_OBJECTS else sprite.rect for sprite in collide_sprites if sprite != self] # i.e. specific Dog sprite should not collide with itself.

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

    def check_for_player_gen(self, detection_rect):
        for spr in self.player_sprites:
            pygame.draw.rect(self.display_surface, "yellow", spr.hitbox_rect)
            self.player_proximity["detected"] = detection_rect.colliderect(spr.hitbox_rect)
            if (self.player_proximity["detected"]):
                # check if player in weapon range
                self.player_sprite_detected = spr
                self.player_location.x = spr.hitbox_rect.centerx
                self.player_location.y = spr.hitbox_rect.centery

                self.weapon.check_in_range(spr)
                break

    # movement
    def jump(self):
        if (self.is_jumping):
            if (self.collision_side["bot"]):
                self.is_jumping = True
                self.velocity.y = self.jump_height
                self.hitbox_rect.bottom -= 1
            self.is_jumping = False

    def horizontal_movement(self, dt):        
        self.movement.horizontal_movement(dt)
        self.movement.collision("horizontal", dt)

    def vertical_movement(self, dt):
        self.movement.vertical_movement(dt)
        self.movement.collision("vertical", dt)

    # attacks
    def attack_delay(self):
        pass

    def update(self, dt, event_list):
        pass

class Bird(Enemy):
    def __init__(self, pos, frames, groups, collision_sprites = None, semi_collision_sprites = None, ramp_collision_sprites = None, player_sprites = None, enemy_sprites = None, type = ENEMY_OBJECTS):
        super().__init__(pos = pos, frames = frames, groups = groups, collision_sprites = collision_sprites, semi_collision_sprites = semi_collision_sprites, ramp_collision_sprites = ramp_collision_sprites, player_sprites = player_sprites, enemy_sprites = enemy_sprites, type = type, jump_height = -DOG_VEL_Y, accel_x = DOG_ACCEL, vel_max_x = DOG_MAX_VEL_X, vel_max_y = DOG_MAX_VEL_Y)

        self.dive_src = pygame.math.Vector2(pos)
        self.dive_dest =  pygame.math.Vector2(pos)
        self.dive_complete = True # for dive and return. Either this flag or timer

        # attack patterns
        self.attack_patterns.update(
            {
                "divebomb": [{"timer_name":"attack_delay", "func": self.attack_delay, "can_damage": False}, {"timer_name":"lock_on", "func": self.lock_on, "can_damage": False}, {"timer_name":"dive", "func": self.attack_delay, "can_damage": True}, {"timer_name":"return_to_dive_src", "func": self.return_to_dive_src, "can_damage": False}]
            }
        )

        # timer
        self.timers.update(
            {
                "attack_delay": Timer(1500),
                "lock_on": Timer(1000)
            }
        )

        self.LEFT_KEY = True

    # TODO override vertical method since flying

    def check_for_player(self):
        # detection zone
        self.detection_rect = self.hitbox_rect.inflate(400, 400)
        pygame.draw.rect(self.display_surface, "yellow", self.detection_rect)

        self.check_for_player_gen(self.detection_rect)

        # for bird, entire detection_rect is the attack zone. override weapon_in_range
        self.player_proximity["weapon_in_range"] = self.player_proximity["detected"]

    # attacks
    def lock_on(self):
        """
        save current position
        get player position
        keep image angle to same angle
        """
        self.dive_src = pygame.math.Vector2(self.hitbox_rect.center)
        self.dive_dest = pygame.math.Vector2(self.player_location)
        self.weapon.enemy_point_image(self.player_location, self.facing_right)

    def linear_path_vector(self, src, dest):
        pass

    def dive_bomb(self):
        """
        idea for moving point to point
        get x and y diff.
        divide by dive speed * dt (pix per frame) to get intervals of x and y per frame. let's ignore gravity for now
        set dive_complete = False

        in enemy_input()
        index < len
            if previous attack is dive or return_to_dive_src    # index -1
                if (dive_complete == True or Timer done)     
                    move to next move
                
                else
                    update dive_complete by checking collision of bird hitbox with destination rect # just so if the x y calc path is not perfect the flag triggers
                    True if collide
            elif (((self.attack_index == 0) or (self.attack_index > 0 and not self.timers[self.attack_seq[self.attack_index - 1]["timer_name"]].active))
                        and not self.timers[self.attack_seq[self.attack_index]["timer_name"]].active):
        """
        pass

    def return_to_dive_src(self):
        pass

    # TODO enemy patrol and attack commands
    
    def update(self, dt, event_list):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        self.check_for_player()
        if (not self.is_attacking):
            self.weapon.enemy_point_image(self.player_location, self.facing_right)
        print(self.dive_src)
        # self.enemy_input()
        # self.horizontal_movement(dt)
        # self.vertical_movement(dt)
        # # recenter image rect with the hitbox rect
        # self.rect.center = self.hitbox_rect.center
        # self.check_contact()
        # self.movement.collision_tweak()
        # self.movement.platform_move(dt)

        self.get_state()
        #self.animate(dt)

        # update weapon 
        self.weapon.update_weapon_zone(self.hitbox_rect)

        # reset x vel
        if (self.velocity.x > -0.01 and self.velocity.x < 0.01):
            self.velocity.x = 0

class Dog(Enemy):

    def __init__(self, pos, frames, groups, collision_sprites = None, semi_collision_sprites = None, ramp_collision_sprites = None, player_sprites = None, enemy_sprites = None, type = ENEMY_OBJECTS):

        super().__init__(pos = pos, frames = frames, groups = groups, collision_sprites = collision_sprites, semi_collision_sprites = semi_collision_sprites, ramp_collision_sprites = ramp_collision_sprites, player_sprites = player_sprites, enemy_sprites = enemy_sprites, type = type, jump_height = -DOG_VEL_Y, accel_x = DOG_ACCEL, vel_max_x = DOG_MAX_VEL_X, vel_max_y = DOG_MAX_VEL_Y)
        
        # attack patterns
        self.attack_patterns.update(
            {
                "uppercut": [{"timer_name":"ready_uppercut", "func": self.ready_uppercut, "can_damage": False}, {"timer_name":"uppercut", "func": self.attack_uppercut, "can_damage": True}, {"timer_name":"attack_delay", "func": self.attack_delay, "can_damage": False}],
                "advancing_slashes": [{"timer_name":"ready_slash", "func": self.ready_slash, "can_damage": False}, {"timer_name":"advance_duration", "func": self.advance_toward_player, "can_damage": False}, {"timer_name":"slash", "func": self.attack_slash, "can_damage": True}, {"timer_name":"ready_slash", "func": self.ready_slash, "can_damage": False},{"timer_name":"advance_duration", "func": self.advance_toward_player, "can_damage": False}, {"timer_name":"slash", "func": self.attack_slash, "can_damage": True}, {"timer_name":"attack_delay", "func": self.attack_delay, "can_damage": False}],
                "jump_attack": [{"timer_name":"jump", "func": self.jump_for_attack, "can_damage": False}, {"timer_name":"slash", "func": self.attack_slash, "can_damage": True}, {"timer_name":"attack_delay", "func": self.attack_delay, "can_damage": False}]
            }
        )

        # timer
        self.timers.update(
            {
                "attack_delay": Timer(1500),
                "ready_uppercut": Timer(250),
                "uppercut": Timer(600),
                "ready_slash": Timer(10),
                "advance_duration": Timer(randint(250, 500)),
                "slash": Timer(400),
                "jump": Timer(250)  # for attack
            }
        )

        self.LEFT_KEY = True

    def check_for_player(self):
        # detection zone
        self.detection_rect = self.hitbox_rect.inflate(300, self.weapon.range * 2)
        pygame.draw.rect(self.display_surface, "yellow", self.detection_rect)

        self.check_for_player_gen(self.detection_rect)

    # attacks
    def ready_uppercut(self):
        start_angle = 45 if self.facing_right else 135

        self.weapon.swing(start_angle, start_angle, 0, True, 0)

    def attack_uppercut(self):
        clockwise = not self.facing_right
        start_angle = 135 if clockwise else 45
        end_angle = 45 if clockwise else 135

        speed = 9
        direction_changes = 1
        self.weapon.swing(start_angle, end_angle, speed, clockwise, direction_changes)

    def ready_slash(self):
        start_angle = 315 if (self.player_location.x >= self.hitbox_rect.centerx) else 225

        self.weapon.swing(start_angle, start_angle, 0, True, 0)

    def attack_slash(self):
        """
        """
        player_angle = degrees(atan2(self.player_location.y - self.hitbox_rect.centery, self.player_location.x - self.hitbox_rect.centerx))

        clockwise = self.facing_right
        start_angle = player_angle - 45 if clockwise else player_angle + 45
        end_angle = player_angle + 45 if clockwise else player_angle - 45
        print('print')
        print(start_angle)
        print(end_angle)
        speed = 9
        direction_changes = 1
        self.weapon.swing(start_angle, end_angle, speed, clockwise, direction_changes)

    def jump_for_attack(self):
        self.rand_jump = 1000

    def advance_toward_player(self):
        if (self.player_location.x <= self.hitbox_rect.centerx):
            self.LEFT_KEY = True
            self.RIGHT_KEY = False
        else: 
            self.LEFT_KEY = False
            self.RIGHT_KEY = True

    def perform_attack(self):
        if (self.is_attacking):
            if (self.attack_index < self.attack_seq_len):
                if (((self.attack_index == 0) or (self.attack_index > 0 and not self.timers[self.attack_seq[self.attack_index - 1]["timer_name"]].active))
                        and not self.timers[self.attack_seq[self.attack_index]["timer_name"]].active):
                    # Either:   1. if first move in list and timer has not started yet = start
                    #           2. if other moves, check if previous move timer is complete before starting.
                    self.facing_right = True if (self.player_location.x >= self.hitbox_rect.centerx) else False

                    if (self.attack_seq[self.attack_index]["timer_name"] == "advance_duration"):
                        self.timers[self.attack_seq[self.attack_index]["timer_name"]] = Timer(randint(250, 500))

                    self.timers[self.attack_seq[self.attack_index]["timer_name"]].activate()
                    self.attack_seq[self.attack_index]["func"]()
                    self.weapon.set_can_damage(self.attack_seq[self.attack_index]["can_damage"])
                    #print(self.timers[self.attack_seq[self.attack_index]["timer_name"]].start_time)
                    self.current_attack = self.attack_seq[self.attack_index]["timer_name"]
                    self.is_attacking = True

                    self.attack_index += 1
            else:
                if (not self.timers[self.attack_seq[self.attack_index - 1]["timer_name"]].active):
                    # disable is_attacking after last timer is finished
                    self.is_attacking = False
                    self.current_attack = None
                    self.weapon.set_can_damage(False)
                    #print(self.timers[self.attack_seq[self.attack_index - 1]["timer_name"]].ended_time)
                    print('fin')

        else:
            # select moves
            if (self.player_location.y < self.hitbox_rect.top):
                # if the player is generally above the enemy
                self.attack_seq = self.attack_patterns["uppercut"]
            else:
                attack_choice = choice(["advancing_slashes", "jump_attack"])
                self.attack_seq = self.attack_patterns[attack_choice]

            self.is_attacking = True
            self.attack_index = 0
            self.attack_seq_len = len(self.attack_seq)

    def enemy_input(self):   
        # if player in detection, charge toward x
        if (self.player_proximity["detected"] or self.is_attacking):
            if (self.player_proximity["weapon_in_range"] or self.is_attacking):
                self.perform_attack()
            else:
                # move toward player
                self.advance_toward_player()
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
        elif (self.collision_side["right"] or not self.collision_side["bot_right"]):
            self.LEFT_KEY = True
            self.RIGHT_KEY = False

        self.facing_right = self.RIGHT_KEY

    def update(self, dt, event_list):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        self.check_for_player()
        if (not self.is_attacking):
            self.weapon.enemy_point_image(self.player_location, self.facing_right)

        self.enemy_input()
        self.horizontal_movement(dt)
        self.vertical_movement(dt)
        # recenter image rect with the hitbox rect
        self.rect.center = self.hitbox_rect.center
        self.check_contact()
        self.movement.collision_tweak()
        self.movement.platform_move(dt)

        self.get_state()
        #self.animate(dt)

        # update weapon 
        self.weapon.update_weapon_zone(self.hitbox_rect)

        # reset x vel
        if (self.velocity.x > -0.01 and self.velocity.x < 0.01):
            self.velocity.x = 0