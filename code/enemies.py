from random import choice, randint
from math import atan2, degrees, radians, sin, cos

from settings import *
from timerClass import Timer
from movement import Movement
from sprites import Orbit

class Enemy(pygame.sprite.Sprite):
    def __init__(self, pos, frames, groups, collision_sprites, semi_collision_sprites, ramp_collision_sprites, player_sprite, enemy_sprites, type = ENEMY_OBJECTS, jump_height = -DOG_VEL_Y, accel_x = DOG_ACCEL, vel_max_x = DOG_MAX_VEL_X, vel_max_y = DOG_MAX_VEL_Y, pathfinder = None, id = id):
        super().__init__(groups)

        self.pos = pos

        self.animation_speed = ANIMATION_SPEED
        self.enemy = True
        self.id = id

        self._health = 1
        self._weakness = choice([STICK, LANCE, BALL])

        self.display_surface = pygame.display.get_surface()

        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = "idle", True
        self.image = self.frames[self.state][self.frame_index]
        self.rect = self.image.get_frect(topleft = pos)
        # Use masking later for more accurate hit box
        self.hitbox_rect = self.rect.inflate(0, 0)
        # previous rect in previous frame to know which direction this rect came from
        self.old_rect = self.hitbox_rect.copy()
        self.mask = pygame.mask.from_surface(self.image)

        # collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.ramp_collision_sprites = ramp_collision_sprites
        self.player_sprite = player_sprite
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

        self.is_hit = False

        # player detection
        self.detection_rect = None
        self.player_sprite_detected = None
        self.player_proximity = {"detected": False, "weapon_in_range": False}
        self.player_location = pygame.math.Vector2(0, 0)
        self.weapon_range_rect = None

        # movement
        self.LEFT_KEY, self.RIGHT_KEY = False, False
        self.is_jumping = False
        self.gravity, self.friction = GRAVITY_NORM, FRICTION   # incr frict for less slide
        self.jump_height = jump_height
        #self.position = pygame.math.Vector2(self.hitbox_rect.bottomleft)
        self.accel_x = accel_x
        self.vel_max_x = vel_max_x
        self.vel_max_y = vel_max_y
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)
        self.rand_jump = randint(0, 100)

        # attack patterns
        self.is_attacking = False
        self.attack_patterns = {
            "idle": [{"timer_name":"idle", "func": self.idle, "can_damage": False}]
        }
        self.attack_seq, self.attack_index, self.attack_seq_len = self.attack_patterns["idle"], 0, 0
        self.current_attack = self.attack_seq[self.attack_index]
        
        # timer
        self.timers = {
            "take_damage_cd": Timer(1000),
            "wall_jump_move_block": Timer(200), # blocks the use of LEFT and RIGHT right after wall jump. // for player
            "unlock_semi_drop_down": Timer(100), # disables the floor collision for semi collision platforms so that the player can drop down through them // for player
            "movement_duration": Timer(randint(1000, 2000)),
            "idle": Timer(1000)
        }

        # modules
        self.movement = Movement(self)
        self.pathfinder = pathfinder

    @property
    def health(self):
        return self._health
    
    @health.setter
    def health(self, health):
        self._health = health

    @property
    def weakness(self):
        return self._weakness
    
    @weakness.setter
    def weakness(self, weakness):
        self._weakness = weakness

    def set_id(self, id):
        self.id = id
    
    def get_id(self):
        return self.id

    def kill_weapon(self):
        self.weapon.kill_weapon()

    def get_rect_center(self):
        return pygame.math.Vector2(self.hitbox_rect.center)
    
    def flicker(self):
        if (self.timers["take_damage_cd"].active and sin(pygame.time.get_ticks() / 50) >= 0):
        #if (self.timers["take_damage_cd"].active and int(self.frame_index) % 2 == 0):
            white_mask = pygame.mask.from_surface(self.image)
            white_surface = white_mask.to_surface()
            white_surface.set_colorkey('black')
            self.image = white_surface

    def animate(self, dt):

        self.frame_index += ANIMATION_SPEED * dt/FPS_TARGET

        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def get_state(self):
        pass

    def fill_collide_lists(self, tar_rect):
        # tiles
        self.list_collide_basic = []
        self.list_collide_ramps = []
        self.list_semi_collide = []

        for group in [self.collision_sprites, self.semi_collision_sprites, self.ramp_collision_sprites, self.player_sprite]:
            if (group is not None):
                for sprite in group:
                    if sprite.rect.colliderect(tar_rect):
                        if (group in [self.collision_sprites, self.player_sprite] or (group in self.enemy_sprites and self != sprite)):
                            self.list_collide_basic.append(sprite)
                        elif (group == self.ramp_collision_sprites):               
                            if (sprite.type in [TERRAIN_R_RAMP, TERRAIN_L_RAMP]):
                                self.list_collide_ramps.append(sprite)
                        elif (group == self.semi_collision_sprites):
                            self.list_semi_collide.append(sprite)

    def check_contact(self, rect, semi_ignore = False, with_player = True):
        """
        Get current collisions on the player
        """
        # hit box is 1 pixels jutting out.
        top_rect = pygame.FRect(rect.topleft + vector(rect.width / 4, -1), (rect.width / 2, 1))
        #pygame.draw.rect(self.display_surface, "red", top_rect)
        bot_rect = pygame.FRect(rect.bottomleft, (rect.width, 1))
        #pygame.draw.rect(self.display_surface, "red", bot_rect)
        left_rect = pygame.FRect(rect.topleft + vector(-1, 0), (1, rect.height * 0.8))
        #pygame.draw.rect(self.display_surface, "red", left_rect)
        right_rect = pygame.FRect(rect.topright + vector(0, 0),(1, rect.height * 0.8))
        #pygame.draw.rect(self.display_surface, "red", right_rect)
        bot_left_rect = pygame.FRect(rect.bottomleft + vector(-1, 0), (1, TILE_SIZE))
        #pygame.draw.rect(self.display_surface, "red", bot_left_rect)
        bot_right_rect = pygame.FRect(rect.bottomright + vector(0, 0), (1, TILE_SIZE))
        #pygame.draw.rect(self.display_surface, "red", bot_right_rect)

        # grouping all basic collidable sprites
        if (with_player):
            collide_sprites = self.collision_sprites.sprites() + [self.player_sprite.sprite]
        else:
            collide_sprites = self.collision_sprites.sprites()
        collide_rects = [sprite.hitbox_rect if sprite.type == PLAYER_OBJECTS else sprite.rect for sprite in collide_sprites if sprite != self] # i.e. specific Dog sprite should not collide with itself.

        # individual terrain tiles
        terrain_rects = [sprite.rect for sprite in self.collision_sprites]
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
        curr_bot_left_collide = True if (bot_left_rect.collidelist(terrain_rects) >= 0 or bot_left_rect.collidelist(semi_collide_rects) >= 0 or bot_left_rect.collidelist(collide_ramps) >= 0) else False
        # bottom right
        curr_bot_right_collide = True if (bot_right_rect.collidelist(terrain_rects) >= 0 or bot_right_rect.collidelist(semi_collide_rects) >= 0 or bot_right_rect.collidelist(collide_ramps) >= 0) else False

        # semi - collisions (floor only)
        if (not semi_ignore):
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

        collision_states = {"top": curr_top_collide, "left": curr_left_collide, "bot": curr_bot_collide, "right": curr_right_collide, "bot_left": curr_bot_left_collide, "bot_right": curr_bot_right_collide}

        # moving platform. Check if player is standing on one
        self.platform = None
        platform_sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in platform_sprites if hasattr(sprite, "moving")]:
            if (bot_rect.colliderect(sprite)):
                self.platform = sprite

        return collision_states

        #if (self.type == ENEMY_OBJECTS):
        #    print(self.collision_side)

    def check_for_player_gen(self, detection_rect):
        #for spr in self.player_sprites:
            #pygame.draw.rect(self.display_surface, "yellow", spr.hitbox_rect)
        self.player_proximity["detected"] = detection_rect.colliderect(self.player_sprite.sprite.hitbox_rect)
        if (self.player_proximity["detected"]):
            # check if player in weapon range
            self.player_sprite_detected = self.player_sprite.sprite
            self.player_location.x = self.player_sprite.sprite.hitbox_rect.centerx
            self.player_location.y = self.player_sprite.sprite.hitbox_rect.centery

            self.weapon.check_in_range(self.player_sprite.sprite)
            #break

    # movement
    def jump(self):
        if (self.is_jumping):
            if (self.collision_side["bot"]):
                self.frame_index = 0
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

    def evaluate_damage(self, damage, damage_type):
        # if not correct damage type, no reaction.
        if (damage_type == self._weakness):
            if (not self.timers["take_damage_cd"].active):
                self.timers["take_damage_cd"].activate()
                self.frame_index = 0
                self.is_hit = True

                self._health -= damage

                if (self._health <= 0):
                    self.kill_weapon()
                    return DEAD
                    
                    # for common enemy, weakness stays the same if has more HP
            
        return ALIVE

    # attacks
    def idle(self):
        pass

    def update(self, dt, event_list):
        pass

# class AcornProjectile(Enemy):
#     def __init__(self, pos, frames, groups, project_tile_speed, angle_fired):

#         super().__init__(pos = pos, frames = frames, groups = groups, collision_sprites = None, semi_collision_sprites = None, ramp_collision_sprites = None, player_sprite = None, enemy_sprites = None, type = "acorn_projectile", jump_height = 0, accel_x = project_tile_speed, vel_max_x = project_tile_speed, vel_max_y = project_tile_speed, pathfinder = None)

#         self.rect = self.image.get_frect(center = pos)
#         self.hitbox_rect = self.rect.inflate(0, 0)
#         self.old_rect = self.hitbox_rect.copy()
#         self.mask = pygame.mask.from_surface(self.image)

#         self.project_tile_speed = project_tile_speed
#         self.friction = AIR_RESISTANCE
#         self.velocity.x = cos(radians(angle_fired)) * project_tile_speed
#         self.velocity.y = sin(radians(angle_fired)) * project_tile_speed

#         # timer
#         self.timers.update(
#             {
#                 "active": Timer(5000)
#             }
#         )

#         self.timers["active"].activate()

#     def manage_state(self):
#         if (not self.timers["active"].active):
#             # remove from group
#             self.kill()
#             #for group in self.groups():
#                 #group.remove(self)

#     def update(self, dt, event_list):
#         self.old_rect = self.hitbox_rect.copy()
#         self.update_timers()   # timer for active
        
#         self.movement.horizontal_movement(dt)
#         self.movement.vertical_movement(dt)
#         # # recenter image rect with the hitbox rect
#         self.rect.center = self.hitbox_rect.center

#         self.manage_state()
#         #self.animate(dt)

class Squirrel(Enemy):
    def __init__(self, pos, frames, groups, collision_sprites, semi_collision_sprites, ramp_collision_sprites, player_sprite, enemy_sprites, type = ENEMY_SQUIRREL, pathfinder = None, func_create_acorn = None, id = "squirrel_0"):
        super().__init__(pos = pos, frames = frames, groups = groups, collision_sprites = collision_sprites, semi_collision_sprites = semi_collision_sprites, ramp_collision_sprites = ramp_collision_sprites, player_sprite = player_sprite, enemy_sprites = enemy_sprites, type = type, jump_height = 0, accel_x = 0, vel_max_x = 0, vel_max_y = DOG_MAX_VEL_Y, pathfinder = pathfinder, id = id)

        self.func_create_acorn = func_create_acorn

        self.throw_max_x = ((SQ_PROJECTILE_SPEED**2) * math.sin(radians(2*45))) / GRAVITY_NORM
    
        self.has_thrown = False
        self.angle_to_fire = 0

        self.hitbox_rect = self.rect.inflate(-15, -25)
        # previous rect in previous frame to know which direction this rect came from
        self.old_rect = self.hitbox_rect.copy()

        # attack patterns
        self.attack_patterns.update(
            {
                "throw": [{"timer_name":"locking_on", "func": self.locking_on, "can_damage": False}, {"timer_name":"locked_on", "func": self.locked_on, "can_damage": False}, {"timer_name":"throw", "func": self.throw, "can_damage": False}, {"timer_name":"idle", "func": self.idle, "can_damage": False}]
            }
        )

        # timer
        self.timers.update(
            {
                "idle": Timer(1500),
                "locking_on": Timer(100),
                "locked_on": Timer(0),
                "throw": Timer(1000)
            }
        )

    def check_for_player(self):
        #pygame.draw.circle(pygame.display.get_surface(), "yellow", self.hitbox_rect.center, self.throw_max_x)
        self.player_proximity["detected"] = self.player_proximity["weapon_in_range"] = False
        #for spr in self.player_sprites:
        if (vector(self.hitbox_rect.center).distance_to(vector(self.player_sprite.sprite.hitbox_rect.center)) <= self.throw_max_x and abs(self.hitbox_rect.centery - self.player_sprite.sprite.hitbox_rect.centery) <= TILE_SIZE):
            # check if player within range and also within a certain y range
            self.player_sprite_detected = self.player_sprite.sprite
            self.player_location.x = self.player_sprite.sprite.hitbox_rect.centerx
            self.player_location.y = self.player_sprite.sprite.hitbox_rect.centery
            self.player_proximity["detected"] = self.player_proximity["weapon_in_range"] = True
            #break

        self.facing_right = True if (self.player_proximity["detected"] and self.player_location.x > self.hitbox_rect.centerx) else False

    # attacks
    def locking_on(self):
        #self.weapon.point_image(self.hitbox_rect.center, self.player_location)
        #getting angle of attack
        self.angle_to_fire = degrees(math.asin((abs(self.player_location.x - self.get_rect_center().x) * GRAVITY_NORM) / (SQ_PROJECTILE_SPEED**2)) / 2)
        
        if (self.player_location.x >= self.get_rect_center().x):
            if (self.angle_to_fire < 1.5):
                self.angle_to_fire = 270 + self.angle_to_fire
            else:
                self.angle_to_fire 
                self.angle_to_fire = 360 - self.angle_to_fire
        else:
            if (self.angle_to_fire < 1.5):
                self.angle_to_fire = 270 - self.angle_to_fire
            else:
                self.angle_to_fire = 180 + self.angle_to_fire

        #pygame.draw.line(pygame.display.get_surface(), "red", self.get_rect_center(), self.weapon.rect.center)
        self.weapon.set_angle(self.angle_to_fire)

    def locked_on(self):
        """
        buffer timer between method locking_on and throw. Gives the player a buffer between when the destination was chosen and firing.
        """
        self.has_thrown = False

    def throw(self):
        # triggered in method animation since want to create the projectile at a certain frame in the animation
        self.func_create_acorn(self.weapon.rect.center, self.angle_to_fire, self.id)

    def perform_attack(self):
        if (self.is_attacking):
            if (self.current_attack["timer_name"] == "locking_on" and self.timers[self.current_attack["timer_name"]].active):
                # specific attack
                self.locking_on()

                if (not self.player_proximity["weapon_in_range"]):
                    self.is_attacking = False

            elif (self.attack_index < self.attack_seq_len):
                # next attack in the sequence
                if (not self.timers[self.current_attack["timer_name"]].active):
                    self.facing_right = True if (self.player_location.x >= self.hitbox_rect.centerx) else False

                    self.timers[self.attack_seq[self.attack_index]["timer_name"]].activate()
                    if (self.attack_seq[self.attack_index]["timer_name"] not in ["throw"]):
                        # not in "throw" because it will be called in method animate so the projectile is created at a certain frame
                        self.attack_seq[self.attack_index]["func"]()
                    self.weapon.set_can_damage(self.attack_seq[self.attack_index]["can_damage"])
                    #print(self.timers[self.attack_seq[self.attack_index]["timer_name"]].start_time)
                    self.current_attack = self.attack_seq[self.attack_index]
                    self.is_attacking = True

                    self.frame_index = 0
                    self.attack_index += 1

            else:
                if (not self.timers[self.current_attack["timer_name"]].active):
                    # disable is_attacking after last timer is finished
                    self.is_attacking = False
                    self.weapon.set_can_damage(False)
                    self.current_attack = None
                    #print(self.timers[self.attack_seq[self.attack_index - 1]["timer_name"]].ended_time)
                    #print('fin')
        else:
            # select moves
            # if the player is generally above the enemy
            self.attack_seq = self.attack_patterns["throw"]

            self.is_home = False
            self.going_home = False
            self.is_attacking = True
            self.attack_index = 0
            self.attack_seq_len = len(self.attack_seq)
            self.current_attack = self.attack_seq[self.attack_index]

    def enemy_input(self):
        if (self.state == "hit"): 
            self.is_attacking = False
        else:
            # if not hit, can perform actions
            if (self.player_proximity["weapon_in_range"] or self.is_attacking):
                self.perform_attack()
            else:
                pass

    def animate(self, dt):
        self.frame_index += ANIMATION_SPEED * dt/FPS_TARGET

        if (self.state == "throw"):
            if (int(self.frame_index) == 2 and not self.has_thrown):
                # frame that should throw projectile
                self.throw()
                self.has_thrown = True
                # hide weapon temporarily
                self.weapon.hide_weapon(True)
            elif(self.frame_index >= len(self.frames[self.state])):
                self.frame_index = 0
                self.timers["throw"].deactivate()

                self.has_thrown = False
                self.weapon.hide_weapon(False)
                self.get_state()
        elif (self.state == "hit"):
            # when timer is finished then toggle off is_hit
            if (self.timers["take_damage_cd"].active):
                if (self.frame_index >= len(self.frames[self.state])):
                    # first frame is the initial knockback
                    self.frame_index = len(self.frames[self.state]) - 1
            else:
                self.frame_index = 0
                self.is_hit = False
                self.get_state()

        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def get_state(self):
        if (self.is_hit):
            self.state = "hit"
        elif (self.current_attack is not None):
            if (self.current_attack["timer_name"] == "throw" and self.timers["throw"].active):
                self.state = self.current_attack["timer_name"]
            else:
                self.state = "idle"
        else:
            self.state = "idle"

    def update(self, dt, event_list):
        self.dt = dt
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()
        
        self.check_for_player()
        #if (not self.is_attacking):
            #self.weapon.enemy_point_image(self.player_location, self.facing_right)
        
        self.enemy_input()
        # apply vertical movement just for initial y pos on ground.
        self.vertical_movement(dt)
        # # recenter image rect with the hitbox rect
        self.rect.center = self.hitbox_rect.center

        self.get_state()
        self.animate(dt)
        self.flicker()

        #pygame.draw.rect(pygame.display.get_surface(), "green", self.hitbox_rect)

class FlyingEnemy(Enemy):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.obstacles = None

        self.flight_src = pygame.math.Vector2(self.pos)
        self.flight_dest =  pygame.math.Vector2(self.pos)

        self.flight_base_speed = FLIGHT_ATTACK_SPEED
        self.flight_speed = self.flight_base_speed 
        self.flight_velocity = pygame.math.Vector2(0, 0)

    def setup_pathfinder(self):
        self.pathfinder.build_matrix(self.obstacles)

    def set_path_points(self, src, dest):
        self.flight_src = src

        # adjust destination if it is a collidable sprite
        valid_dest = dest
        valid_found = False
        while (not valid_found):
            valid_found = True
            dest_rect = pygame.FRect((valid_dest), (1, 1))
            for spr in self.obstacles:
                if (spr.rect.colliderect(dest_rect)):
                    valid_found = False
                    if (src[0] < dest[0]):
                        valid_dest = valid_dest - pygame.math.Vector2(TILE_SIZE, 0)
                    else:
                        valid_dest = valid_dest + pygame.math.Vector2(TILE_SIZE, 0)
                    break

        self.flight_dest = valid_dest

    def determine_path(self):
        # determine path
        self.set_path(self.flight_src, self.flight_dest)
        self.create_path_checkpoints()

    def set_path(self, src, dest):
        _, self.pathfinder.path = self.pathfinder.dijkstra(src, dest) # x, y

    def create_path_checkpoints(self):
        if (len(self.pathfinder.path) > 0):
            self.pathfinder.path_checkpoints = []

            for point in self.pathfinder.path:
                x = point[0] * TILE_SIZE + (TILE_SIZE/2)
                y = point[1] * TILE_SIZE + (TILE_SIZE/2)
                self.pathfinder.path_checkpoints.append(pygame.FRect((x - self.flight_speed * 2, y - self.flight_speed * 2), (self.flight_speed * 4, self.flight_speed * 4)))   # inflated checkpoint to ensure collision of flying sprite

    def assess_path(self):
        # re-evaluate flight_path. Currently giving me trouble
        # self.flight_src = pygame.math.Vector2(self.hitbox_rect.topleft)
        # self.determine_flight_vector(self.flight_src, self.flight_dest)
        self.get_velocity()
        self.check_checkpoint_collision()
        if (self.weapon is not None):
            self.weapon.point_image(self.hitbox_rect.center, self.flight_dest) 
        

    def get_velocity(self):
        if (len(self.pathfinder.path_checkpoints) > 0):
            start = pygame.math.Vector2(self.hitbox_rect.center)
            end = pygame.math.Vector2(self.pathfinder.path_checkpoints[0].center)
            if (end - start) != (0, 0):
                vec = end - start
                if (vec.magnitude() < self.flight_speed):
                    # reduce velocity so the next movemnet step will collide with the checkpoint
                    self.velocity = vec
                else:
                    # fly at speed
                    self.velocity = (end - start).normalize() * self.flight_speed
            else:
                self.velocity = pygame.math.Vector2(0, -3)
        else:
            self.velocity = pygame.math.Vector2(0, 0)
            self.pathfinder.empty_path()

    def check_checkpoint_collision(self):
        if (len(self.pathfinder.path_checkpoints) > 0):
            #for rect in self.pathfinder.path_checkpoints:
            if (self.pathfinder.path_checkpoints[0].collidepoint(self.hitbox_rect.center)):
                del self.pathfinder.path_checkpoints[0]
                self.get_velocity()
        else:
            self.pathfinder.empty_path()

class Sign(FlyingEnemy):
    def __init__(self, pos, frames, groups, collision_sprites, semi_collision_sprites, ramp_collision_sprites, player_sprite, enemy_sprites, type = ENEMY_SIGN, pathfinder = None, id = "sign_0", func_create_pole = None):

        super().__init__(pos = pos, frames = frames, groups = groups, collision_sprites = collision_sprites, semi_collision_sprites = semi_collision_sprites, ramp_collision_sprites = ramp_collision_sprites, player_sprite = player_sprite, enemy_sprites = enemy_sprites, type = type, jump_height = -DOG_VEL_Y, accel_x = DOG_ACCEL, vel_max_x = DOG_MAX_VEL_X, vel_max_y = DOG_MAX_VEL_Y, pathfinder = pathfinder, id = id)

        self.health = 20
        
        self.func_create_pole = func_create_pole

        self.obstacles = []#[spr for spr in self.collision_sprites if (not hasattr(spr, "id") or (hasattr(spr, "id") and spr.get_id() != self.get_id()))]

        self._active = False

        self.flight_base_speed = SIGN_FLIGHT_SPEED
        self.flight_speed = self.flight_base_speed

        # attack patterns
        self.attack_patterns.update(
            {   
                # {"timer_name":"", "func": , "can_damage": }
                "dive": [{"timer_name":"set_home_top", "func": self.set_home_top, "can_damage": False}, {"timer_name":"assess_path", "func": self.assess_path, "can_damage": True}, {"timer_name":"locking_on", "func": self.locking_on, "can_damage": False}, {"timer_name":"locked_on", "func": self.locked_on, "can_damage": False}, {"timer_name":"assess_path", "func": self.assess_path, "can_damage": True}, {"timer_name":"idle", "func": self.idle, "can_damage": False}],

                "parabola": [{"timer_name":"set_home_side", "func": self.set_home_side, "can_damage": False}, {"timer_name":"assess_path", "func": self.assess_path, "can_damage": False}, {"timer_name":"set_spin_attr", "func": self.set_spin_attr, "params": [1, -1],"can_damage": False}, {"timer_name":"start_spinning", "func": self.start_spinning, "can_damage": True}, {"timer_name":"set_parabola", "func": self.set_parabola, "can_damage": True}, {"timer_name":"assess_path", "func": self.assess_path, "can_damage": True}, {"timer_name":"stop_spinning", "func": self.stop_spinning, "can_damage": False}, {"timer_name":"idle", "func": self.idle, "can_damage": False}],

                "fire_poles_cross": [{"timer_name":"set_home_center", "func": self.set_home_center, "can_damage": False}, {"timer_name":"assess_path", "func": self.assess_path, "can_damage": False}, {"timer_name":"locking_on", "func": self.locking_on, "can_damage": False}, {"timer_name":"locked_on", "func": self.locked_on, "can_damage": False}, {"timer_name":"fire_poles_cross", "func": self.fire_poles_cross, "can_damage": False}, {"timer_name":"idle", "func": self.idle, "can_damage": False}],
                
                "spin": [{"timer_name":"set_down_slash", "func": self.set_down_slash, "can_damage": False}, {"timer_name":"spin_for_rotations", "func": self.start_spinning, "can_damage": True}, {"timer_name":"set_up_slash", "func": self.set_up_slash, "can_damage": False}, {"timer_name":"spin_for_rotations", "func": self.start_spinning, "can_damage": True}, {"timer_name":"idle", "func": self.idle, "can_damage": False}]#,

                #"spin_test": [{"timer_name":"set_spin_attr", "func": self.set_spin_attr, "params": [1, -1],"can_damage": False}, {"timer_name":"start_spinning", "func": self.start_spinning, "can_damage": True}]
            }
        )

        self.spin_direction = 1 # 1 is clockwise
        self.spin_num_rotations = -1 # -1 is infinite
        self.curr_rotations = 0
        self.rotation_flag = False

        # timer
        self.timers.update(
            {
                "idle": Timer(600),
                "set_home_top": Timer(50),
                "set_home_side": Timer(50),
                "set_home_center": Timer(50),
                "fire_poles_cross": Timer(100),
                "set_parabola": Timer(50),
                "set_spin_attr": Timer(50),
                "start_spinning": Timer(1000),
                "stop_spinning": Timer(50),
                "set_down_slash": Timer(50),
                "set_up_slash": Timer(50),
                "locking_on": Timer(750),
                "locked_on": Timer(150),
                "assess_path": Timer(1500, None, True),  # repeat on incase bird did not get to destination yet.
                "spin_for_rotations": Timer(2000, None, True),
                "attack_cooldown": Timer(1000)
            }
        )

        self.home_top_pos = vector(4305, 140)   # pos to start some attacks
        self.home_left_pos = vector(3605, 595)
        self.home_right_pos = vector(4865, 595)
        self.home_center_pos = vector(4305, 315)

        self.setup_pathfinder()

        self.start_angle = -90
        self.end_angle = -90
        self.angle = self.start_angle
        self.image_orientation = IMAGE_UP

        self.is_spinning = False

    @property
    def active(self):
        return self._active
    
    @active.setter
    def active(self, bool):
        self._active = bool
    
    def evaluate_damage(self, damage, damage_type):
        # override
        if (damage_type == self._weakness):
            if (not self.timers["take_damage_cd"].active and self._active):
                self.timers["take_damage_cd"].activate()
                self.frame_index = 0
                self.is_hit = True

                self._health -= damage

                if (self._health <= 0):
                    return DEAD
                else:
                    # if has more HP, change weakness type
                    self.weakness = choice([STICK, LANCE, BALL])

        return ALIVE

    def check_for_player_within_melee(self):
        # detection zone
        self.detection_rect = self.hitbox_rect.inflate(150, 150)
        self.player_proximity["detected"] = self.detection_rect.colliderect(self.player_sprite.sprite.hitbox_rect)
        if (self.player_proximity["detected"]):
            self.player_sprite_detected = self.player_sprite.sprite
            self.player_location = self.player_sprite.sprite.hitbox_rect.center

    def point_top(self, player_location, default = True):
        # point weapon for enemy sprite
        if (default):
            self.start_angle = self.end_angle = self.angle = -90
        elif (self.is_attacking):
            # move to angle
            self.point_image(self.hitbox_rect.center, player_location)
            #print(f'{self.rect.center} : {self.player_location}')
        else:
            # reset
            self.start_angle = self.end_angle = self.angle = -90
            #self.point_image(self.hitbox_rect.center, player_location) # for testing

    def point_image(self, source, location):
        source = pygame.math.Vector2(source)
        location = pygame.math.Vector2(location)
        angle = degrees(atan2(location.y - source.y, location.x - source.x))
        self.set_angle(angle)
        #print(f'{angle}')

    def set_angle(self, angle):
        new_end_angle = angle
        self.start_angle = self.end_angle = self.angle = new_end_angle

    def rotate_image(self):


        # vector of the angle
        direction = pygame.math.Vector2(math.cos(radians(self.angle)), math.sin(radians(self.angle))).normalize()

        # angle of rotation based on original image orientation
        angle = degrees(atan2(direction.x, direction.y)) - self.image_orientation		#atan2(y, x). y = x and x = y and then - image_orientation (this also requires user to start the image in the correct position relative to the center of the object orbiting) for correct angle of rotation
        #print(f'{self.angle} : {math.cos(radians(self.angle))} : {math.sin(radians(self.angle))} : {degrees(atan2(direction.x, direction.y))} : {angle}')

        # bug fix where rotating image would fill the newly sized image to hold the rotated image with the colour.
        """
        Unless rotating by 90 degree increments, the image will be padded larger to hold the new size. If the image has pixel alphas, the padded area will be transparent. Otherwise pygame will pick a color that matches the Surface colorkey or the topleft pixel value.

        https://www.reddit.com/r/pygame/comments/24mrx5/rect_filled_with_colour_when_rotating_image/
        """
        self.image = pygame.transform.rotozoom(self.image, angle, 1).convert_alpha()    # needed to convert_alpha again since it is creating a new image.
        self.mask = pygame.mask.from_surface(self.image)
        
        self.rect = self.image.get_frect(center = self.hitbox_rect.center)

        # align weapon hit box
        self.weapon.set_angle_info(direction, angle)

    def set_home_top(self):
        self.point_top(self.player_location, True)
        self.set_destination(pygame.math.Vector2(self.home_top_pos))
        self.flight_speed = SIGN_FLIGHT_SPEED

    def set_home_side(self):
        self.point_top(self.player_location, True)
        self.set_destination(pygame.math.Vector2(choice([self.home_left_pos, self.home_right_pos])))
        self.flight_speed = SIGN_FLIGHT_SPEED

    def set_home_center(self):
        self.point_top(self.player_location, True)
        self.set_destination(pygame.math.Vector2(self.home_center_pos))
        self.flight_speed = SIGN_FLIGHT_SPEED

    def set_destination(self, dest):
        print(f'{self.get_rect_center()}, {dest}')
        self.set_path_points(self.get_rect_center(), dest)
        self.determine_path()

    def locking_on(self):
        self.point_top(self.player_sprite.sprite.hitbox_rect.center, False)

    def locked_on(self):
        """
        save current position
        get player position
        keep image angle to same angle
        """
        self.player_location = self.player_sprite.sprite.hitbox_rect.center
        self.pathfinder.empty_path()
        self.pathfinder.path.append((self.player_location[0] / TILE_SIZE, self.player_location[1] / TILE_SIZE))
        self.create_path_checkpoints()
        self.flight_speed = SIGN_ATTACK_FLIGHT_SPEED

    def fire_poles_cross(self):
        # top
        # pos, angle_fired, owner_id
        self.func_create_pole((self.hitbox_rect.center), self.angle, self.id)

        # left
        self.func_create_pole((self.hitbox_rect.center), self.angle - 90, self.id)

        # right
        self.func_create_pole((self.hitbox_rect.center), self.angle + 90, self.id)

        # bottom
        self.func_create_pole((self.hitbox_rect.center), self.angle + 180, self.id)

    def set_down_slash(self):
        arr = [-1 if self.player_sprite.sprite.hitbox_rect.x > self.get_rect_center().x else 1, 1]
        self.set_spin_attr(arr)

    def set_up_slash(self):
        arr = [1 if self.player_sprite.sprite.hitbox_rect.x > self.get_rect_center().x else -1, 1]
        self.set_spin_attr(arr)

    def set_spin_attr(self, params):
        self.spin_direction = params[0]
        self.spin_num_rotations = params[1]

    def start_spinning(self):
        self.is_spinning = True

    def stop_spinning(self):
        self.is_spinning = False
        self.point_top(self.player_sprite.sprite.hitbox_rect.center, True)
        self.spin_direction = 1
        self.spin_num_rotations = -1
        self.curr_rotations = 0

    def set_parabola(self):
        self.pathfinder.create_parabola_path(pygame.Vector2(self.hitbox_rect.centerx / TILE_SIZE, self.hitbox_rect.centery / TILE_SIZE), pygame.Vector2(self.player_sprite.sprite.hitbox_rect.centerx / TILE_SIZE, self.player_sprite.sprite.hitbox_rect.centery / TILE_SIZE))
        self.create_path_checkpoints()
        self.flight_speed = SIGN_ATTACK_FLIGHT_SPEED

        # print('===')
        # print((self.hitbox_rect.centerx / TILE_SIZE, self.hitbox_rect.centery / TILE_SIZE))
        # print((self.player_sprite.sprite.hitbox_rect.centerx / TILE_SIZE, self.player_sprite.sprite.hitbox_rect.centery / TILE_SIZE))
        # print(self.pathfinder.path)
        # print(self.pathfinder.path_checkpoints)

    def spin(self, dt):
        if (self.is_spinning):
            self.weapon.set_can_damage(True)
            self.angle -= SIGN_SPIN_ATTACK_SPEED * dt * self.spin_direction 
            self.angle = self.angle % 360

            if (self.spin_direction >= 0):
                if (self.rotation_flag and abs(self.angle) <= 270 and abs(self.angle) >= 180):
                    self.curr_rotations += 1
                    self.rotation_flag = False
                elif (abs(self.angle) > 270 and abs(self.angle) < 360):
                    self.rotation_flag = True
            elif (self.spin_direction < 0):
                if (self.rotation_flag and abs(self.angle) >= 270 and abs(self.angle) <= 360):
                    self.curr_rotations += 1
                    self.rotation_flag = False
                elif (abs(self.angle) > 180 and abs(self.angle) < 270):
                    self.rotation_flag = True

            if (self.curr_rotations == self.spin_num_rotations):
                self.weapon.set_can_damage(False)
                self.stop_spinning()

    def perform_attack(self):
        if (self.is_attacking):

            if (self.current_attack["timer_name"] == "spin_for_rotations" and self.timers[self.current_attack["timer_name"]].active):
                # infintie until rotations complete
                if (not self.is_spinning):
                    self.timers[self.current_attack["timer_name"]].kill()
            elif (self.current_attack["timer_name"] == "start_spinning" and self.timers[self.current_attack["timer_name"]].active):
                # usually infinite here, but if ever chosen rotation limit end it if reached within timer
                if (not self.is_spinning):
                    self.timers[self.current_attack["timer_name"]].deactivate()
            elif (self.current_attack["timer_name"] == "assess_path" and self.timers[self.current_attack["timer_name"]].active):
                    # specific attack
                    if (len(self.pathfinder.path_checkpoints) == 0):
                        # end
                        #print('fin_flight')
                        self.pathfinder.empty_path()
                        self.velocity = pygame.math.Vector2(0, 0)
                        self.timers[self.current_attack["timer_name"]].kill()
                    else:
                        self.assess_path()
                    # self.pathfinder.draw_path()
                    # for rect in self.pathfinder.path_checkpoints:
                    #     pygame.draw.rect(pygame.display.get_surface(), "blue", rect)
            elif (self.current_attack["timer_name"] == "locking_on" and self.timers[self.current_attack["timer_name"]].active):
                # specific attack
                self.point_top(self.player_sprite.sprite.hitbox_rect.center, False)

            elif (self.attack_index < self.attack_seq_len):
                # next attack in the sequence
                if (not self.timers[self.current_attack["timer_name"]].active):

                    if (self.attack_seq[self.attack_index]["timer_name"] == "assess_path"):
                        self.timers[self.attack_seq[self.attack_index]["timer_name"]] = Timer(1500, None, True)
                    elif (self.attack_seq[self.attack_index]["timer_name"] == "spin_for_rotations"):
                        self.timers[self.attack_seq[self.attack_index]["timer_name"]] = Timer(2000, None, True)

                    self.timers[self.attack_seq[self.attack_index]["timer_name"]].activate()

                    if (self.attack_seq[self.attack_index]["timer_name"] == "set_spin_attr"):
                        self.attack_seq[self.attack_index]["func"](self.attack_seq[self.attack_index]["params"])
                    else:
                        self.attack_seq[self.attack_index]["func"]()

                    self.weapon.set_can_damage(self.attack_seq[self.attack_index]["can_damage"])
                    #print(self.timers[self.attack_seq[self.attack_index]["timer_name"]].start_time)
                    self.current_attack = self.attack_seq[self.attack_index]
                    self.is_attacking = True

                    self.attack_index += 1

            else:
                if (not self.timers[self.current_attack["timer_name"]].active):
                    # disable is_attacking after last timer is finished
                    self.is_attacking = False
                    self.weapon.set_can_damage(False)
                    self.current_attack = None
                    #print(self.timers[self.attack_seq[self.attack_index - 1]["timer_name"]].ended_time)
                    #print('fin')
                    # start cooldown
                    self.timers['attack_cooldown'] = Timer(randint(1000, 1500))
                    self.timers['attack_cooldown'].activate()
        else:
            # select moves
            moves = ['dive', 'parabola', 'fire_poles_cross']
            #moves = ['spin_test']

            self.check_for_player_within_melee()
            if (self.player_proximity["detected"]):
                # if within melee range, add and increase the odds of close range spin move
                moves = moves + ['spin', 'spin', 'spin']

            self.attack_seq = self.attack_patterns[choice(moves)]

            self.is_attacking = True
            self.attack_index = 0
            self.attack_seq_len = len(self.attack_seq)
            self.current_attack = self.attack_seq[self.attack_index]

    def enemy_input(self):
        # if (self.is_hit):
        #     self.is_attacking = False
        #     self.velocity = pygame.math.Vector2(0, 0)
        # else:
        if (not self.timers['attack_cooldown'].active or self.is_attacking):
            self.flight_speed = SIGN_ATTACK_FLIGHT_SPEED
            self.perform_attack()
        else:
            
            # move toward player
            self.point_top(self.player_location, True)
            self.flight_speed = SIGN_FLIGHT_SPEED
            self.velocity = (self.player_sprite.sprite.hitbox_rect.center - pygame.Vector2(self.hitbox_rect.center)).normalize() * self.flight_speed

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt/FPS_TARGET

        if (self.state == "hit"):
            # when timer is finished then toggle off is_hit
            if (self.timers["take_damage_cd"].active):
                if (self.frame_index >= len(self.frames[self.state])):
                    # first frame is the initial knockback
                    self.frame_index = len(self.frames[self.state]) - 1
            else:
                self.frame_index = 0
                self.is_hit = False
                self.get_state()

        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def get_state(self):
        if (self.is_hit):
            self.state = "hit"
        else:
            self.state = "idle"

    def update(self, dt, event_list = None):
        self.dt = dt
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()
        
        if (self._active):
            
            self.enemy_input()
            self.movement.flying_movement(dt, self.velocity)
            self.spin(dt)
            # recenter image rect with the hitbox rect
            self.rect.center = self.hitbox_rect.center

        self.get_state()    
        self.animate(dt)    # change frame
        self.flicker()      # flicker the frame

        self.rotate_image()
        


class Bird(FlyingEnemy):
    def __init__(self, pos, frames, groups, collision_sprites, semi_collision_sprites, ramp_collision_sprites, player_sprite, enemy_sprites, type = ENEMY_BIRD, pathfinder = None, id = "bird_0"):

        super().__init__(pos = pos, frames = frames, groups = groups, collision_sprites = collision_sprites, semi_collision_sprites = semi_collision_sprites, ramp_collision_sprites = ramp_collision_sprites, player_sprite = player_sprite, enemy_sprites = enemy_sprites, type = type, jump_height = -DOG_VEL_Y, accel_x = DOG_ACCEL, vel_max_x = DOG_MAX_VEL_X, vel_max_y = DOG_MAX_VEL_Y, pathfinder = pathfinder, id = id)

        # for collision_sprites, ignore self object since it would cause the spawn position as an obstacle if not excluded
        self.obstacles = [spr for spr in self.collision_sprites if (not hasattr(spr, "id") or (hasattr(spr, "id") and spr.get_id() != self.get_id()))] + self.semi_collision_sprites.sprites() + self.ramp_collision_sprites.sprites()

        self.hitbox_rect = self.rect.inflate(-10, 0)
        # previous rect in previous frame to know which direction this rect came from
        self.old_rect = self.hitbox_rect.copy()

        self.flight_base_speed = FLIGHT_ATTACK_SPEED
        self.flight_speed = self.flight_base_speed 

        self.spawn_pos = pygame.math.Vector2(self.hitbox_rect.center)
        self.is_home = True
        self.home_rect = None

        self.patrol_left_bound = pygame.math.Vector2(self.spawn_pos[0] - 300, self.spawn_pos[1])
        self.patrol_right_bound = pygame.math.Vector2(self.spawn_pos[0] + 300, self.spawn_pos[1])
        self.patrol_right = False

        self.flight_src = pygame.math.Vector2(pos)
        self.flight_dest =  pygame.math.Vector2(pos)
        self.flight_velocity = pygame.math.Vector2(0, 0)
        self.flight_complete = True # for dive and return. Either this flag or timer
        self.pathing_rect = self.hitbox_rect.copy()
        
        self.dt = 1

        # attack patterns
        self.attack_patterns.update(
            {
                "ram": [{"timer_name":"locking_on", "func": self.locking_on, "can_damage": False}, {"timer_name":"locked_on", "func": self.locked_on, "can_damage": False}, {"timer_name":"assess_path", "func": self.assess_path, "can_damage": True}, {"timer_name":"idle", "func": self.idle, "can_damage": False}]
            }
        )

        # timer
        self.timers.update(
            {
                "idle": Timer(600),
                "locking_on": Timer(500),
                "locked_on": Timer(150),
                "assess_path": Timer(1500, None, True)  # repeat on incase bird did not get to destination yet.
            }
        )

        self.setup_pathfinder()

    def check_for_player(self):
        # detection zone
        #self.detection_rect = self.hitbox_rect.inflate(600, 600)
        #pygame.draw.rect(self.display_surface, "yellow", self.detection_rect)
        #self.check_for_player_gen(self.detection_rect)

        # for bird, entire detection_rect is the attack zone. override weapon_in_range
        #self.player_proximity["weapon_in_range"] = self.player_proximity["detected"]
        #pygame.draw.circle(self.display_surface, "green", self.hitbox_rect.center, 325)
        self.player_proximity["detected"] = self.player_proximity["weapon_in_range"] = False
        #for spr in self.player_sprites:
        if (vector(self.hitbox_rect.center).distance_to(vector(self.player_sprite.sprite.hitbox_rect.center)) <= 300):
            # check if player in weapon range
            self.player_sprite_detected = self.player_sprite.sprite
            self.player_location.x = self.player_sprite.sprite.hitbox_rect.centerx
            self.player_location.y = self.player_sprite.sprite.hitbox_rect.centery

            self.player_proximity["detected"] = self.player_proximity["weapon_in_range"] = True
            #break

    # attacks
    def determine_flight_vector(self, flight_src, flight_dest):
        # determines the velocity vector toward the destination that avoids going toward a collision inbetween
        #print('--')
        try:
            diff_vect = pygame.math.Vector2(flight_dest - flight_src).normalize()   # get direction
        except:
            diff_vect = pygame.math.Vector2(0, 0)
        
        line_velocity = pygame.math.Vector2(diff_vect.x * self.flight_speed, diff_vect.y * self.flight_speed)

        p1 = pygame.FRect((flight_src), (25, 25))
        p2 = pygame.FRect((flight_dest), (5, 5))
        #pygame.draw.rect(pygame.display.get_surface(), "red", p1)
        #pygame.draw.rect(pygame.display.get_surface(), "red", p2)
        #pygame.draw.line(pygame.display.get_surface(), "green", flight_src, flight_dest)
        #print(line_velocity)
        # apply vector to test rect. check for collision and adjust if there is
        store_old_rect = self.old_rect.copy()
        store_hitbox = self.hitbox_rect.copy() # hold original hit_box
        collision_clear_state = 0
        # save old rect and move back
        cycles = 0
        
        ## going around collisions too difficult right now, currently fly through everything
        # while (not self.hitbox_rect.colliderect(p2) 
        #         and 
        #         cycles < 200):
        #     cycles += 1
        #     self.old_rect = self.hitbox_rect.copy()
        #     self.hitbox_rect = self.movement.flying_movement(self.dt, self.hitbox_rect, line_velocity)
        #     self.movement.collision("vertical", self.dt)

        #     upcoming_collison_states = self.check_contact(self.hitbox_rect, True, False)
        #     # depending on destination relative to source, it cares about different collision sides for adjustment
        #     if upcoming_collison_states["bot"]:
        #         line_velocity.y = 0
        #         if (collision_clear_state == 0):
        #             # pick one direction once
        #             if (flight_dest.x >= flight_src.x):
        #                 # move right
        #                 line_velocity.x = self.flight_speed
        #             else:
        #                 line_velocity.x = -self.flight_speed
        #             collision_clear_state = 1
        #     elif (not upcoming_collison_states["bot"] and collision_clear_state == 1):
        #         # cleared the collision
        #         break
            
        # # determine new line_velocity
        # try:
        #     diff_vect = pygame.math.Vector2(self.hitbox_rect.center - flight_src).normalize()   # get direction
        # except:
        #     diff_vect = pygame.math.Vector2(0, 0)
        # print(line_velocity)
        #self.path_checkpoint = pygame.FRect((self.hitbox_rect.center), (5, 5))
        self.flight_velocity = pygame.math.Vector2(diff_vect.x * self.flight_speed, diff_vect.y * self.flight_speed)

        # restore original rects
        self.old_rect = store_old_rect
        self.hitbox_rect = store_hitbox

    def locking_on(self):
        self.weapon.enemy_point_image(self.player_location, self.facing_right)

    def locked_on(self):
        """
        save current position
        get player position
        keep image angle to same angle
        """
        self.set_path_points(self.get_rect_center(), pygame.math.Vector2(self.player_location.x, self.player_location.y))
        self.determine_path()
        self.weapon.enemy_point_image(self.player_location, self.facing_right)
        #self.determine_flight_vector(self.flight_src, self.flight_dest)

    def set_if_home(self):
        if (self.home_rect is not None):
            self.is_home = self.home_rect.collidepoint(self.hitbox_rect.center)
            if (self.is_home):
                self.home_rect = None
                self.weapon.enemy_point_image(self.player_location, self.facing_right)

    # enemy patrol and attack commands
    def perform_attack(self):
        if (self.is_attacking):

            if (self.current_attack["timer_name"] == "assess_path" and self.timers[self.current_attack["timer_name"]].active):
                    # specific attack
                    if (len(self.pathfinder.path_checkpoints) == 0):
                        # end
                        #print('fin_flight')
                        self.pathfinder.empty_path()
                        self.velocity = pygame.math.Vector2(0, 0)
                        self.timers[self.current_attack["timer_name"]].kill()
                    else:
                        self.assess_path()
                    # self.pathfinder.draw_path()
                    # for rect in self.pathfinder.path_checkpoints:
                    #     pygame.draw.rect(pygame.display.get_surface(), "blue", rect)

            elif (self.current_attack["timer_name"] == "locking_on" and self.timers[self.current_attack["timer_name"]].active):
                # specific attack
                self.weapon.enemy_point_image(self.player_location, self.facing_right)

                if (not self.player_proximity["weapon_in_range"]):
                    self.is_attacking = False

            elif (self.attack_index < self.attack_seq_len):
                # next attack in the sequence
                if (not self.timers[self.current_attack["timer_name"]].active):
                    self.facing_right = True if (self.player_location.x >= self.hitbox_rect.centerx) else False

                    if (self.attack_seq[self.attack_index]["timer_name"] == "advance_duration"):
                        self.timers[self.attack_seq[self.attack_index]["timer_name"]] = Timer(randint(250, 500))
                    elif (self.attack_seq[self.attack_index]["timer_name"] == "assess_path"):
                        self.timers[self.attack_seq[self.attack_index]["timer_name"]] = Timer(1500, None, True)

                    self.timers[self.attack_seq[self.attack_index]["timer_name"]].activate()
                    self.attack_seq[self.attack_index]["func"]()
                    self.weapon.set_can_damage(self.attack_seq[self.attack_index]["can_damage"])
                    #print(self.timers[self.attack_seq[self.attack_index]["timer_name"]].start_time)
                    self.current_attack = self.attack_seq[self.attack_index]
                    self.is_attacking = True

                    self.attack_index += 1

            else:
                if (not self.timers[self.current_attack["timer_name"]].active):
                    # disable is_attacking after last timer is finished
                    self.is_attacking = False
                    self.weapon.set_can_damage(False)
                    self.current_attack = None
                    #print(self.timers[self.attack_seq[self.attack_index - 1]["timer_name"]].ended_time)
                    #print('fin')
        else:
            # select moves
            # if the player is generally above the enemy
            self.attack_seq = self.attack_patterns["ram"]

            self.is_home = False
            self.going_home = False
            self.is_attacking = True
            self.attack_index = 0
            self.attack_seq_len = len(self.attack_seq)
            self.current_attack = self.attack_seq[self.attack_index]

    def enemy_input(self):
        if (self.is_hit):
            self.is_attacking = False
            self.velocity = pygame.math.Vector2(0, 0)
        else:
            if (self.player_proximity["weapon_in_range"] or self.is_attacking):
                self.flight_speed = FLIGHT_ATTACK_SPEED
                self.perform_attack()
            else:
                self.flight_speed = FLIGHT_NORMAL_SPEED
                if (len(self.pathfinder.path) == 0):
                    self.patrol_right = not self.patrol_right
                    if (not self.is_home):
                        # check if home, if not return
                        self.set_path_points(self.get_rect_center(), self.spawn_pos)
                        self.determine_path()
                        print(self.flight_src, ": ", self.flight_dest)
                        if (len(self.pathfinder.path_checkpoints) > 0 and self.home_rect is None):
                            self.home_rect = self.pathfinder.path_checkpoints[-1]
                        self.set_if_home()
                    elif (self.is_home):
                        # patrol
                        if (self.patrol_right):
                            self.set_path_points(self.get_rect_center(), self.patrol_right_bound)
                        else:
                            self.set_path_points(self.get_rect_center(), self.patrol_left_bound)
                            
                        self.determine_path()

                self.assess_path()
                if not self.is_home:
                    self.pathfinder.draw_path()
                    for rect in self.pathfinder.path_checkpoints:
                        pygame.draw.rect(pygame.display.get_surface(), "blue", rect)

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt/FPS_TARGET

        if (self.state == "hit"):
            # when timer is finished then toggle off is_hit
            if (self.timers["take_damage_cd"].active):
                if (self.frame_index >= len(self.frames[self.state])):
                    # first frame is the initial knockback
                    self.frame_index = len(self.frames[self.state]) - 1
            else:
                self.frame_index = 0
                self.is_hit = False
                self.get_state()

        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def get_state(self):
        if (self.is_hit):
            self.state = "hit"
        else:
            self.state = "idle"

    def update(self, dt, event_list):
        self.dt = dt
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        self.check_for_player()
        if (not self.is_attacking):
            self.weapon.enemy_point_image(self.player_location, self.facing_right)
        
        self.enemy_input()
        self.movement.flying_movement(dt, self.velocity)
        # # recenter image rect with the hitbox rect
        self.rect.center = self.hitbox_rect.center

        self.facing_right = False if (self.velocity.x < 0) else True

        self.get_state()
        self.animate(dt)
        self.flicker()

        # update weapon position to stay with owner
        self.weapon.update_weapon_zone(self.hitbox_rect)

        
        #pygame.draw.rect(pygame.display.get_surface(), "green", self.hitbox_rect)

class Dog(Enemy):

    def __init__(self, pos, frames, groups, collision_sprites, semi_collision_sprites, ramp_collision_sprites, player_sprite, enemy_sprites, type = ENEMY_DOG, id = "dog_0"):

        super().__init__(pos = pos, frames = frames, groups = groups, collision_sprites = collision_sprites, semi_collision_sprites = semi_collision_sprites, ramp_collision_sprites = ramp_collision_sprites, player_sprite = player_sprite, enemy_sprites = enemy_sprites, type = type, jump_height = -DOG_VEL_Y, accel_x = DOG_ACCEL, vel_max_x = DOG_MAX_VEL_X, vel_max_y = DOG_MAX_VEL_Y, id = id)

        self.hitbox_rect = self.rect.inflate(-50, 0)
        # previous rect in previous frame to know which direction this rect came from
        self.old_rect = self.hitbox_rect.copy()

        # attack patterns
        self.attack_patterns.update(
            {
                "uppercut": [{"timer_name":"ready_uppercut", "func": self.ready_uppercut, "can_damage": False}, {"timer_name":"uppercut", "func": self.attack_uppercut, "can_damage": True}, {"timer_name":"idle", "func": self.idle, "can_damage": False}],
                "advancing_slashes": [{"timer_name":"ready_slash", "func": self.ready_slash, "can_damage": False}, {"timer_name":"advance_duration", "func": self.advance_toward_player, "can_damage": False}, {"timer_name":"slash", "func": self.attack_slash, "can_damage": True}, {"timer_name":"ready_slash", "func": self.ready_slash, "can_damage": False},{"timer_name":"advance_duration", "func": self.advance_toward_player, "can_damage": False}, {"timer_name":"slash", "func": self.attack_slash, "can_damage": True}, {"timer_name":"idle", "func": self.idle, "can_damage": False}],
                "jump_attack": [{"timer_name":"jump", "func": self.jump_for_attack, "can_damage": False}, {"timer_name":"slash", "func": self.attack_slash, "can_damage": True}, {"timer_name":"idle", "func": self.idle, "can_damage": False}]
            }
        )

        # timer
        self.timers.update(
            {
                "idle": Timer(1500),
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
        #pygame.draw.rect(self.display_surface, "yellow", self.detection_rect)

        self.check_for_player_gen(self.detection_rect)

    # attacks
    def ready_uppercut(self):
        self.frame_index = 0
        start_angle = 45 if self.facing_right else 135

        self.weapon.swing(start_angle, start_angle, 0, True, 0)

    def attack_uppercut(self):
        self.frame_index = 0
        clockwise = not self.facing_right
        start_angle = 135 if clockwise else 45
        end_angle = 45 if clockwise else 135

        speed = 9
        direction_changes = 1
        self.weapon.swing(start_angle, end_angle, speed, clockwise, direction_changes)

    def ready_slash(self):
        self.frame_index = 0
        start_angle = 315 if (self.player_location.x >= self.hitbox_rect.centerx) else 225

        self.weapon.swing(start_angle, start_angle, 0, True, 0)

    def attack_slash(self):
        """
        """
        self.frame_index = 0
        player_angle = degrees(atan2(self.player_location.y - self.hitbox_rect.centery, self.player_location.x - self.hitbox_rect.centerx))

        clockwise = self.facing_right
        start_angle = player_angle - 45 if clockwise else player_angle + 45
        end_angle = player_angle + 45 if clockwise else player_angle - 45
        #print('print')
        #print(start_angle)
        #print(end_angle)
        speed = 9
        direction_changes = 1
        self.weapon.swing(start_angle, end_angle, speed, clockwise, direction_changes)

    def jump_for_attack(self):
        self.rand_jump = 1000

    def advance_toward_player(self):
        if (self.player_location.x <= self.hitbox_rect.centerx):
            self.LEFT_KEY = True
            self.RIGHT_KEY = False
        elif (self.player_location.x): 
            self.LEFT_KEY = False
            self.RIGHT_KEY = True

    def perform_attack(self):
        if (self.is_attacking):
            if (self.attack_index < self.attack_seq_len):
                if (not self.timers[self.current_attack["timer_name"]].active):
                    self.facing_right = True if (self.player_location.x >= self.hitbox_rect.centerx) else False

                    if (self.attack_seq[self.attack_index]["timer_name"] == "advance_duration"):
                        self.timers[self.attack_seq[self.attack_index]["timer_name"]] = Timer(randint(250, 500))

                    self.timers[self.attack_seq[self.attack_index]["timer_name"]].activate()
                    self.attack_seq[self.attack_index]["func"]()
                    self.weapon.set_can_damage(self.attack_seq[self.attack_index]["can_damage"])
                    #print(self.timers[self.attack_seq[self.attack_index]["timer_name"]].start_time)
                    self.current_attack = self.attack_seq[self.attack_index]
                    self.is_attacking = True

                    self.frame_index = 0
                    self.attack_index += 1
            else:
                if (not self.timers[self.current_attack["timer_name"]].active):
                    # disable is_attacking after last timer is finished
                    self.is_attacking = False
                    self.weapon.set_can_damage(False)
                    #print(self.timers[self.attack_seq[self.attack_index - 1]["timer_name"]].ended_time)
                    #print('fin')
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
            self.current_attack = self.attack_seq[self.attack_index]

        """
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
        """

    def enemy_input(self):
        #print(self.collision_side)

        if (self.state == "hit"): 
            # flinch
            # stop moving
            self.LEFT_KEY = False
            self.RIGHT_KEY = False
            
            if (self.is_attacking):
                # stop attack
                self.is_attacking = False
                self.weapon.set_can_damage(False)
        else:
            # if not hit, can perform actions
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
                if (self.player_proximity["detected"]):
                    self.LEFT_KEY = False
                    self.RIGHT_KEY = False
                else:
                    self.LEFT_KEY = False
                    self.RIGHT_KEY = True
            elif (self.collision_side["right"] or not self.collision_side["bot_right"]):
                if (self.player_proximity["detected"]):
                    self.LEFT_KEY = False
                    self.RIGHT_KEY = False
                else:
                    self.LEFT_KEY = True
                    self.RIGHT_KEY = False

            self.facing_right = self.RIGHT_KEY

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt/FPS_TARGET

        if (self.state in ["ready_uppercut", "ready_slash"] and self.frame_index >= len(self.frames[self.state])):
            # hold at last frame, until state change (timer runs out)
            self.frame_index = len(self.frames[self.state]) - 1
        elif (self.state in ["uppercut", "slash"] and self.frame_index >= len(self.frames[self.state])):
            # just hold on last frame, until state change (timer runs out)
            self.frame_index = len(self.frames[self.state]) - 1

            # attack complete
            #self.frame_index = 0
            #self.timers[self.state].deactivate()    # responsibility of dev to match the duration of the attack rotation to the animation speed
            #self.weapon.set_can_damage(False)
            #self.get_state()
        elif (self.state == "hit"):
            # when timer is finished then toggle off is_hit
            if (self.timers["take_damage_cd"].active):
                if (self.frame_index >= len(self.frames[self.state])):
                    # first frame is the initial knockback
                    self.frame_index = len(self.frames[self.state]) - 1
            else:
                self.frame_index = 0
                self.is_hit = False
                self.get_state()

        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]
        self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def get_state(self):
        if (self.is_hit):
            self.state = "hit"
        elif (self.current_attack is not None and (self.current_attack["timer_name"] in ["ready_uppercut", "ready_slash", "uppercut", "slash"] and self.timers[self.current_attack["timer_name"]].active)):
            self.state = self.current_attack["timer_name"]
        elif (self.is_jumping):
            self.state = "jump" if self.velocity.y < 0 else "fall" 
        elif (self.LEFT_KEY or self.RIGHT_KEY):
            self.state = "run"
        else:
            self.state = "idle"

    def update(self, dt, event_list):
        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        #self.outline_surface(enemy.image, (enemy.hitbox_rect.topleft + self.current_window_offset), DAMAGE_COLOUR[enemy.weakness])
        

        self.check_for_player()
        if (not self.is_attacking):
            self.weapon.enemy_point_image(self.player_location, self.facing_right)

        self.enemy_input()
        self.horizontal_movement(dt)
        self.vertical_movement(dt)
        # recenter image rect with the hitbox rect
        self.rect.center = self.hitbox_rect.center
        self.collision_side = self.check_contact(self.hitbox_rect, False)
        self.movement.collision_tweak()
        self.movement.platform_move(dt)

        self.get_state()
        self.animate(dt)
        self.flicker()
        # update weapon 
        self.weapon.update_weapon_zone(self.hitbox_rect)

        # reset x vel
        if (self.velocity.x > -0.01 and self.velocity.x < 0.01):
            self.velocity.x = 0
        
        #pygame.draw.rect(pygame.display.get_surface(), "green", self.hitbox_rect)