from math import degrees, radians, atan2, sin, cos
from random import choice

from settings import *
from timerClass import Timer
from movement import Movement

class Player(pygame.sprite.Sprite):

    def __init__(self, pos, groups, data, collision_sprites, semi_collision_sprites, ramp_collision_sprites, enemy_sprites, frames, type = PLAYER_OBJECTS, func_create_ball = None, id = "player_0"):
        # general setup
        super().__init__(groups)
        self.z = Z_LAYERS["main"]
        self.type = type
        self.id = id

        self.data = data

        self.func_create_ball = func_create_ball
        self.has_thrown = False

        self.display_surface = pygame.display.get_surface()
        
        self.frames, self.frame_index = frames, 0
        self.state, self.facing_right = "idle", True
        #self.image = surf
        self.image = self.frames[self.state][self.frame_index]
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_speed = ANIMATION_SPEED

        self.current_window_offset = pygame.math.Vector2(0, 0)

        # rects
        self.player_spawn_point = pos
        # rect to hold entire image
        self.rect = self.image.get_frect(topleft = pos)
        # reduce rect for actual representation of the hit box of the image. -50 means 25 pixels from left and 25 from right
        # Use masking later for more accurate hit box
        self.hitbox_rect = self.rect.inflate(-50, 0)
        # previous rect in previous frame to know which direction this rect came from
        self.old_rect = self.hitbox_rect.copy()

        # collision
        self.collision_sprites = collision_sprites
        self.semi_collision_sprites = semi_collision_sprites
        self.ramp_collision_sprites = ramp_collision_sprites
        self.enemy_sprites = enemy_sprites
        # self.masked_sprites = masked_sprites
        self.on_ramp_wall = False   # flag for same sprite
        self.on_ramp_slope = {"on": False, "ramp_type": None} 
        self.collision_side = {"top": False, "left": False, "bot": False, "right": False, "bot_left": False, "bot_right": False}
        self.list_collide_basic, self.list_collide_ramps, self.list_semi_collide = [], [], []

        # current platform player is standing on
        self.platform = None

        # movement
        self.LEFT_KEY, self.RIGHT_KEY = False, False
        self.is_jumping = False
        self.jump_height = -PLAYER_VEL_Y
        self.gravity, self.friction = GRAVITY_NORM, FRICTION   # incr frict for less slide
        #self.position = pygame.math.Vector2(self.hitbox_rect.bottomleft)
        self.accel_x = PLAYER_ACCEL
        self.vel_max_x = PLAYER_MAX_VEL_X
        self.vel_max_y = PLAYER_MAX_VEL_Y
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        # attacks
        self.is_attacking = False
        self.current_attack = None
        self.attack_pos = pygame.math.Vector2(0, 0)

        self.thrust_offset = [-10, 0, 15]

        self.angle_to_fire = 0

        self.weapon_list = []
        self.current_weapon_index = 0

        self.is_hit = False

        # timer
        self.timers = {
            "wall_jump_move_block": Timer(200), # blocks the use of LEFT and RIGHT right after wall jump
            "unlock_semi_drop_down": Timer(100), # disables the floor collision for semi collision platforms so that the player can drop down through them
            "stick_attack_cooldown": Timer(1000),
            "stick_attack_active": Timer(400),
            "lance_attack_cooldown": Timer(750),
            "lance_attack_active": Timer(400),
            "ball_attack_cooldown": Timer(500),
            "ball_attack_active": Timer(1000),
            "take_damage_cd": Timer(1000)
        }

        # modules
        self.movement = Movement(self)

        #sounds
        self.jump_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_jump", "SFX_Jump_50.mp3"))
        self.jump_sound.set_volume(0.1)

        self.stick_swing1 = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_attacks", "stick_swing.wav"))
        self.stick_swing1.set_volume(0.5)
        self.stick_swing2 = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_attacks", "stick_swing2.wav"))
        self.stick_swing2.set_volume(0.5)

        self.lance_jab = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_attacks", "lance_jab.wav"))
        self.lance_jab.set_volume(0.25)

        self.ball_throw = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_attacks", "ball_throw.wav"))
        self.ball_throw.set_volume(0.5)

        self.hit_sound_1 = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_hit", "pain1.wav"))
        self.hit_sound_1.set_volume(0.5)

        self.hit_sound_2 = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_hit", "pain2.wav"))
        self.hit_sound_2.set_volume(0.5)

        self.hit_sound_3 = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_hit", "pain3.wav"))
        self.hit_sound_3.set_volume(0.5)

        self.hit_sound_4 = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_hit", "pain4.wav"))
        self.hit_sound_4.set_volume(0.5)

        self.hit_sound_5 = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "player_hit", "pain5.wav"))
        self.hit_sound_5.set_volume(0.5)

    def bound(self, val, val_min, val_max):
        return max(min(val, val_max), val_min)

    def move_player_to_spawn(self):
        self.hitbox_rect.topleft = self.player_spawn_point
        self.rect.center = self.hitbox_rect.center
        self.old_rect = self.hitbox_rect.copy()

    def set_current_window_offset(self, current_window_offset):
        self.current_window_offset = pygame.math.Vector2(current_window_offset[0], current_window_offset[1])

    def get_id(self):
        return self.id

    def player_input(self):
        keys = pygame.key.get_pressed()

        # key down
        if (keys[CONTROLS[CNTRL_WEAPON_1][PYGAME_CONST]]):
            new_weapon_index = 0
        elif (keys[CONTROLS[CNTRL_WEAPON_2][PYGAME_CONST]]):
            new_weapon_index = 1
        elif (keys[CONTROLS[CNTRL_WEAPON_3][PYGAME_CONST]]):
            new_weapon_index = 2
        else:
            new_weapon_index = self.current_weapon_index

        self.select_weapon(new_weapon_index)
            
        if (keys[CONTROLS[CNTRL_JUMP][PYGAME_CONST]]):
            self.jump()

        if (not self.timers["wall_jump_move_block"].active):
            # blocks these keys if just jumped off a wall. Prevent infinite climbing with wall jump
            if (keys[CONTROLS[CNTRL_MOVE_LEFT][PYGAME_CONST]]):
                self.LEFT_KEY = True
                self.facing_right = False
            if (keys[CONTROLS[CNTRL_MOVE_RIGHT][PYGAME_CONST]]):
                self.RIGHT_KEY = True
                self.facing_right = True
        
        if (keys[CONTROLS[CNTRL_MOVE_DOWN][PYGAME_CONST]]):
            self.timers["unlock_semi_drop_down"].activate()
        
        # key up
        if (not keys[CONTROLS[CNTRL_JUMP][PYGAME_CONST]]):
            if (self.is_jumping):
                self.velocity.y *= 0.25
                self.is_jumping = False
        if (not keys[CONTROLS[CNTRL_MOVE_LEFT][PYGAME_CONST]]):
            self.LEFT_KEY = False
        if (not keys[CONTROLS[CNTRL_MOVE_RIGHT][PYGAME_CONST]]):
            self.RIGHT_KEY = False

    def select_weapon(self, new_weapon_index):
        new_weapon_index = new_weapon_index % len(self.weapon_list) # circular array
        if (self.current_weapon_index != new_weapon_index):
            # clear prev weapon statues
            self.is_attacking = False
            self.current_attack = None
            self.weapon_list[self.current_weapon_index]["weapon"].set_can_damage(False)
            self.timers[self.weapon_list[self.current_weapon_index]["timer_cooldown"]].deactivate()
            self.timers[self.weapon_list[self.current_weapon_index]["timer_attack"]].deactivate()
            self.current_weapon_index = new_weapon_index

    def get_current_weapon(self):
        if (len(self.weapon_list) > 0 and self.current_weapon_index < len(self.weapon_list)):
            return self.weapon_list[self.current_weapon_index]["weapon"]
        else:
            return None
        
    def adjust_mouse_position(self, mouse_pos):
        mouse_pos = pygame.math.Vector2(mouse_pos)
        mouse_pos = pygame.math.Vector2(mouse_pos.x + self.current_window_offset.x*-1, mouse_pos.y + self.current_window_offset.y*-1)
        player_pos = pygame.math.Vector2(self.hitbox_rect.center)
        return mouse_pos, player_pos

    def weapon_setup(self, weapon_list):
        self.weapon_list = weapon_list
        for weapon in self.weapon_list:
            weapon_attacks = []
            if (weapon["weapon"].type == STICK):
                weapon_attacks.append(self.weapon_slash)
            elif (weapon["weapon"].type == LANCE):
                weapon_attacks.append(self.weapon_thrust)
            elif (weapon["weapon"].type == BALL):
                weapon_attacks.append(self.weapon_throw)

            weapon.update(
                {
                    "original_radius": weapon["weapon"].radius,
                    "timer_cooldown": str(weapon["weapon"].type) + "_attack_cooldown",
                    "timer_attack": str(weapon["weapon"].type) + "_attack_active",
                    "weapon_attacks": weapon_attacks
                }
            )
        #print(self.weapon_list)

    def weapon_management(self):
        if (len(self.weapon_list) > 0 and self.current_weapon_index < len(self.weapon_list)):

            # change active weapon
            for i in range(0, len(self.weapon_list)):
                #self.weapon_list[i].print_weapon_info()
                if (i == self.current_weapon_index):
                    self.weapon_list[i]["weapon"].hide_weapon(False)
                else:
                    self.weapon_list[i]["weapon"].hide_weapon(True)

            if (not self.timers[self.weapon_list[self.current_weapon_index]["timer_attack"]].active):
                self.is_attacking = False

            if (not self.is_attacking):
                # point current weapon to the mouse position if not currently attacking
                mouse_pos, player_pos = self.adjust_mouse_position(pygame.mouse.get_pos())
                self.weapon_list[self.current_weapon_index]["weapon"].point_image(player_pos, pygame.math.Vector2(mouse_pos))
                # here and in method animation if the animation if faster than the timer
                self.weapon_list[self.current_weapon_index]["weapon"].set_can_damage(False)
                self.is_attacking = False
                self.current_attack = None

                if (self.weapon_list[self.current_weapon_index]["weapon"].type == LANCE):
                    self.weapon_list[self.current_weapon_index]["weapon"].set_radius(self.weapon_list[self.current_weapon_index]["original_radius"])
            elif (self.is_attacking):
                if (self.current_attack == "thrust"):
                    # adjust thrust "reach" depending on the current thrust frame animation.
                    self.weapon_thrust()

            # update weapon position to stay with owner
            self.weapon_list[self.current_weapon_index]["weapon"].update_weapon_zone(self.hitbox_rect)

    def weapon_attack(self, mouse_pos):
        mouse_pos, _ = self.adjust_mouse_position(mouse_pos)
        if (len(self.weapon_list) > 0 and self.current_weapon_index < len(self.weapon_list) and self.is_hit == False):
            # only allow attack if valid weapon and is not currently in "hit" state
            if (not self.is_attacking and not self.timers[self.weapon_list[self.current_weapon_index]["timer_cooldown"]].active):
                self.attack_pos = pygame.math.Vector2(mouse_pos) # to fix
                self.is_attacking = True
                self.frame_index = 0
                self.timers[self.weapon_list[self.current_weapon_index]["timer_cooldown"]].activate()
                self.timers[self.weapon_list[self.current_weapon_index]["timer_attack"]].activate()

                # choose an attack
                attack_choice = choice(self.weapon_list[self.current_weapon_index]["weapon_attacks"])
                attack_choice()

    def weapon_slash(self):
        
        self.current_attack = "slash"
        self.frame_index = 0
        player_angle = degrees(atan2(self.attack_pos[1] - self.hitbox_rect.centery, self.attack_pos[0] - self.hitbox_rect.centerx))

        if (self.attack_pos.x >= self.hitbox_rect.x):
            # keep player looking at x direction of attack
            self.facing_right = True
        else:
            self.facing_right = False

        clockwise = self.facing_right
        start_angle = player_angle - 45 if clockwise else player_angle + 45
        end_angle = player_angle + 45 if clockwise else player_angle - 45
        speed = 9
        direction_changes = 1
        self.weapon_list[self.current_weapon_index]["weapon"].swing(start_angle, end_angle, speed, clockwise, direction_changes)
        self.weapon_list[self.current_weapon_index]["weapon"].set_can_damage(True)

        sound = choice([self.stick_swing1, self.stick_swing2])
        sound.play()

    def weapon_thrust(self):
        self.current_attack = "thrust"
        new_radius = 0
        if (self.frame_index < len(self.thrust_offset)):
            if (self.frame_index == 0):
                # need it to play the sound once
                self.lance_jab.play()

            if (int(self.frame_index) == 0):
                self.weapon_list[self.current_weapon_index]["weapon"].set_can_damage(False)
                
            else:
                self.weapon_list[self.current_weapon_index]["weapon"].set_can_damage(True)
            new_radius = self.weapon_list[self.current_weapon_index]["original_radius"] + self.thrust_offset[int(self.frame_index)]
        else:
            self.weapon_list[self.current_weapon_index]["weapon"].set_can_damage(True)
            new_radius = self.weapon_list[self.current_weapon_index]["original_radius"] + self.thrust_offset[len(self.thrust_offset) - 1]

        self.weapon_list[self.current_weapon_index]["weapon"].set_radius(new_radius)



    def weapon_throw(self):
        self.current_attack = "throw"
        #getting angle of attack
        self.angle_to_fire = self.weapon_list[self.current_weapon_index]["weapon"].angle
        # ball then thrown on certain frame in method animation

        self.ball_throw.play()

    def horizontal_movement(self, dt):
        """
        Blending Newton's Laws and Kinematic Equations for x
        """
        self.movement.horizontal_movement(dt)
        # self.acceleration.x = 0
        # if (self.LEFT_KEY):
        #     self.acceleration.x -= self.accel_x
        # if (self.RIGHT_KEY):
        #     self.acceleration.x += self.accel_x
        
        # self.acceleration.x += self.velocity.x * self.friction
        # self.velocity.x += self.acceleration.x * dt
        # self.limit_velocity(self.velocity.x, self.vel_max_x)
        # #self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        # #self.hitbox_rect.x = self.position.x
        # self.hitbox_rect.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)

        #self.collision("horizontal")
        self.movement.collision("horizontal", dt)

    def vertical_movement(self, dt):
        """
        Blending Newton's Laws and Kinematic Equations for y
        """ 
        self.movement.vertical_movement(dt)
        # vel_y_change = 0
        # if (self.on_ramp_slope["on"] and not self.is_jumping):
        #     vel_y_change = math.ceil(abs(self.velocity.x))  # 1:1
        # elif (not self.collision_side["bot"] and any((self.collision_side["left"], self.collision_side["right"])) and not self.is_jumping):
        #     if (self.velocity.y < 0):
        #         # stop it from going any higher since touched wall
        #         self.velocity.y = 0
        #     vel_y_change = (self.acceleration.y / 10) * dt
        # else:
        #     vel_y_change = self.acceleration.y * dt

        # self.velocity.y += vel_y_change

        # if (self.velocity.y > self.vel_max_y):
        #     self.velocity.y = self.vel_max_y 
        
        # #self.position.y += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
        # #self.hitbox_rect.bottom = self.position.y
        # self.hitbox_rect.bottom += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)

        # self.on_ramp_slope["on"] = False

        #self.collision("vertical")
        self.movement.collision("vertical", dt)

    def limit_velocity(self, vel_vec, max_vel):
        """
        Limit for x velocity
        """
        vel_vec = max(-max_vel, min(vel_vec, max_vel))
        if abs(vel_vec) < .01:
            vel_vec = 0 

    def jump(self):
        """
        1. Normal jump. Bottom true, top false, and not currenly is_jumping = Jump and apply normal gravity. is_jumping back to false when space released. This blocks holding jump for more than 1 jump
        2. Normal jump then touches wall. Bottom true, top false, and not currenly is_jumping = Jump. Contact with side wall.
            2.1. If space held, is_jump remains True and apply normal gravity
            2.2. If space released while on wall, is_jump changes to True. Allows wall jump and initial x direction is away from the wall.
        """
        if (self.collision_side["bot"] and not self.collision_side["top"] and not self.is_jumping):
            self.is_jumping = True
            self.velocity.y -= PLAYER_VEL_Y
            #self.collision_side["bot"] = False
            self.jump_sound.play()

        elif (not self.collision_side["bot"] and any((self.collision_side["left"], self.collision_side["right"])) and not self.is_jumping and not self.timers["wall_jump_move_block"].active):
            self.is_jumping = True
            self.velocity.y -= PLAYER_VEL_Y * 0.7
            # force jump away from wall
            self.velocity.x = PLAYER_MAX_VEL_X if self.collision_side["left"] else -PLAYER_MAX_VEL_X
            self.facing_right = True if self.collision_side["left"] else False

            self.timers["wall_jump_move_block"].activate()
            self.LEFT_KEY = False
            self.RIGHT_KEY = False

            self.jump_sound.play()

    # def platform_move(self, dt):
    #     """
    #     Adjust the player while on a moving platform
    #     """
    #     if (self.platform):
    #         # sprite not None and (full collision or (not full collision and bottom has contact))
    #         self.hitbox_rect.topleft += self.platform.direction * self.platform.speed  * dt

    def fill_collide_lists(self, tar_rect):
        # tiles
        self.list_collide_basic = []
        self.list_collide_ramps = []
        self.list_semi_collide = []

        for group in [self.collision_sprites, self.semi_collision_sprites, self.ramp_collision_sprites]:
            for sprite in group:
                if sprite.rect.colliderect(tar_rect):
                    if (group in [self.collision_sprites, self.enemy_sprites]):
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
        #pygame.draw.rect(self.display_surface, "green", top_rect)
        bot_rect = pygame.FRect(self.hitbox_rect.bottomleft, (self.hitbox_rect.width, 1))
        #pygame.draw.rect(self.display_surface, "green", bot_rect)
        left_rect = pygame.FRect(self.hitbox_rect.topleft + vector(-1,self.hitbox_rect.height / 4), (1,self.hitbox_rect.height / 4))
        #pygame.draw.rect(self.display_surface, "green", left_rect)
        right_rect = pygame.FRect(self.hitbox_rect.topright + vector(0,self.hitbox_rect.height / 4),(1,self.hitbox_rect.height / 4))
        #pygame.draw.rect(self.display_surface, "green", right_rect)

        collide_sprites = self.collision_sprites.sprites()
        collide_rects = [sprite.rect for sprite in collide_sprites]
        #semi_collide_rects = [sprite.rect for sprite in self.semi_collision_sprites]
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

        # semi - collisions (floor only)
        semi_collide_sprites = self.semi_collision_sprites.sprites()
        for spr in semi_collide_sprites:
            if (self.velocity.y >= 0 and bot_rect.colliderect(spr.rect) and bot_rect.top <= spr.rect.top):
                # must be "falling", collided, and hit box top is less than or equal than the platform top
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
        
        self.collision_side["top"] = curr_top_collide
        self.collision_side["bot"] = curr_bot_collide
        self.collision_side["left"] = curr_left_collide
        self.collision_side["right"] = curr_right_collide

        # moving platform. Check if player is standing on one
        self.platform = None
        platform_sprites = self.collision_sprites.sprites() + self.semi_collision_sprites.sprites()
        for sprite in [sprite for sprite in platform_sprites if hasattr(sprite, "moving")]:
            if (bot_rect.colliderect(sprite)):
                self.platform = sprite

        #print(self.collision_side)

    # def semi_collisions(self):
    #     if (not self.timers["unlock_semi_drop_down"].active):
    #         # only apply floor collision if player has not expressly keyed down to drop down through the platform
    #         for sprite in self.list_semi_collide:
    #             move_offset = 0
    #             if (sprite.type == MOVING_OBJECTS):
    #                 move_offset = sprite.speed

    #             if (self.hitbox_rect.bottom >= sprite.rect.top and self.old_rect.bottom - move_offset <= sprite.rect.top):
    #                 if (self.velocity.y > 0):
    #                     self.velocity.y = 0
    #                 self.hitbox_rect.bottom = sprite.rect.top

    # def collision_ramp(self, tar_rect, ramp_sprite):
    #     """
    #     check collision of ramp sprites
    #     return (bool, float)
    #     """
    #     #center = tar_rect.width / 2
    #     # player x position relative to the ramp
    #     rel_x = tar_rect.x - ramp_sprite.rect.x

    #     # determine player new height based on the ramp type
    #     # since the ramp is a right isoceles, height can be determined by the overlap in the x axis
    #     if (ramp_sprite.type == TERRAIN_R_RAMP):
    #         # right edge
    #         pos_h = rel_x + self.hitbox_rect.width
    #         # center
    #         #pos_h = rel_x + center
    #     else:
    #         pos_h = TILE_SIZE - rel_x
    #         #pos_h = TILE_SIZE - rel_x - center

    #     # bounds
    #     pos_h = min(pos_h, TILE_SIZE)
    #     pos_h = max(pos_h, 0)

    #     # height that will be in the ramp tile
    #     target_y = ramp_sprite.rect.y + TILE_SIZE - pos_h
    #     #print(tar_rect.bottom, ":", target_y)
    #     if (tar_rect.bottom >= target_y):
    #         # check if the player collided with the actual ramp #and that the player y pos is level or within ramp
    #         # adjust player height
    #         #self.collision_side["bot"] = True
    #         return (True, target_y)
    #     else:
    #         return (False, 0)
        
    def collision(self, axis, dt):
        """
        Loop through all collision_sprites and evaluate collision
        """
        self.movement.collision(axis, dt)
        # # populate collided rects
        # self.fill_collide_lists(self.hitbox_rect)

        # # for semi collision rects
        # self.semi_collisions()

        # # involves both axes and both conditions are external states assgined externally
        # if (self.on_ramp_slope["on"] and self.collision_side["top"]):
        #     # handle on ramp but top is restricted.
        #     self.collision_side["top"] = False

        #     if (self.is_jumping):
        #         # if jumping, stop it and set flag so input key up doesn't apply this again
        #         self.velocity.y *= 0.25
        #         self.is_jumping = False

        #     # move back so to not be in contact with tile above
        #     offset = 15
        #     if (self.on_ramp_slope["ramp_type"] == TERRAIN_R_RAMP):
        #         offset = -offset
        #     temp = self.old_rect.left + offset
        #     self.hitbox_rect.left = self.old_rect.left + offset
        #     self.old_rect.left = temp   

        #     self.velocity.x = 0
             
        # # terrain basic
        # for sprite in self.list_collide_basic:
        #     if (axis == "horizontal"):
        #         move_offset = 0
        #         if (sprite.type == MOVING_OBJECTS):
        #             move_offset = sprite.speed
                
        #         if (self.hitbox_rect.left <= sprite.rect.right and self.old_rect.left + move_offset >= sprite.rect.right):
        #             # left collision and player approach from right
        #             if (not self.on_ramp_slope["on"]):
        #                 # fixed hitching when off ramping onto a basic tile
        #                 pass
        #                 #self.velocity.x = 0

        #             self.hitbox_rect.left = sprite.rect.right
        #         elif (self.hitbox_rect.right >= sprite.rect.left and self.old_rect.right - move_offset <= sprite.rect.left):
        #             # right collision and player approach from left
        #             if (not self.on_ramp_slope["on"]):
        #                 pass
        #                 #self.velocity.x = 0  

        #             self.hitbox_rect.right = sprite.rect.left
        #     else:
        #         moving_offset = 0
        #         if (sprite.type == MOVING_OBJECTS):
        #             moving_offset = sprite.speed
                    
        #         # vertical
        #         if (self.hitbox_rect.bottom >= sprite.rect.top and self.old_rect.bottom - moving_offset <= sprite.rect.top):
        #             # touch ground, player approaching from top
        #             #self.collision_side["bot"] = True
        #             self.velocity.y = 0
        #             self.hitbox_rect.bottom = sprite.rect.top
        #         elif (self.hitbox_rect.top <= sprite.rect.bottom and self.old_rect.top + moving_offset>= sprite.rect.bottom):
        #             # sprite hit top, player approach from below
        #             if (self.is_jumping):
        #                 # if jumping, stop it and set flag so input key up doesn't apply this again
        #                 self.velocity.y *= 0.25
        #                 self.is_jumping = False
        #             self.hitbox_rect.top = sprite.rect.bottom

        # for sprite in self.list_collide_ramps:
        #     # collided with frect of the ramp
        #     if (axis == "horizontal"):
        #         self.on_ramp_wall = False
        #         if (sprite.type == TERRAIN_R_RAMP):
        #             if (self.hitbox_rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right):
        #                 # wall of right ramp, player approach from the right
        #                 if (not self.on_ramp_slope["on"]):
        #                     self.on_ramp_wall = True

        #                 self.velocity.x = 0

        #                 self.hitbox_rect.left = sprite.rect.right
        #             elif (self.hitbox_rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left and self.hitbox_rect.bottom > sprite.rect.bottom):
        #                 # of bottom edge of slope, if below don't hook on
        #                 self.hitbox_rect.right = sprite.rect.left
        #         else:                   
        #             if (self.hitbox_rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left):
        #                 # wall of left ramp, player approach from the left
        #                 if (not self.on_ramp_slope["on"]):
        #                     self.on_ramp_wall = True

        #                 self.velocity.x = 0

        #                 self.hitbox_rect.right = sprite.rect.left
        #             elif (self.hitbox_rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right and self.hitbox_rect.bottom > sprite.rect.bottom):
        #                 self.hitbox_rect.left = sprite.rect.right
        #     else:
        #         if (self.hitbox_rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom):
        #             # bottom of ramp, player approach from bottom
        #             if (self.is_jumping):
        #                 self.velocity.y *= 0.25
        #                 self.is_jumping = False
        #             self.hitbox_rect.top = sprite.rect.bottom
        #         elif (not self.on_ramp_wall): 
        #             res = self.collision_ramp(self.hitbox_rect, sprite)
        #             if (res[0]):
        #                 self.on_ramp_slope["on"] = True
        #                 self.on_ramp_slope["ramp_type"] = sprite.type

        #                 self.velocity.y = 0
        #                 self.hitbox_rect.bottom = res[1]

    def collision_tweak(self):
        # involves both axes and both conditions are external states assgined externally
        if (self.on_ramp_slope["on"] and self.collision_side["top"]):
            # handle on ramp but top is restricted.
            self.collision_side["top"] = False

            if (self.is_jumping):
                # if jumping, stop it and set flag so input key up doesn't apply this again
                self.velocity.y *= 0.25
                self.is_jumping = False

            # move back so to not be in contact with tile above
            offset = vector(0, 0)
            if (self.on_ramp_slope["ramp_type"] == TERRAIN_R_RAMP):
                offset = -offset
            temp = self.old_rect.center + offset
            self.hitbox_rect.center = self.old_rect.center + offset
            self.old_rect.center = temp   

            self.velocity.x = 0

    def evaluate_damage(self, damage, damage_type):
        # later check if match damage type
        if (not self.timers["take_damage_cd"].active):
            self.timers["take_damage_cd"].activate()

            sound = choice([self.hit_sound_1, self.hit_sound_2, self.hit_sound_3, self.hit_sound_4, self.hit_sound_5])
            sound.play()
            self.frame_index = 0

            self.is_hit = True

            if (self.data.player_health - damage <= 0):
                #self.move_player_to_spawn()
                return DEAD
                
            self.data.player_health = self.data.player_health - damage

            # stop current attack
            self.is_attacking = False

            return ALIVE

    def flicker(self):
        if (self.timers["take_damage_cd"].active and sin(pygame.time.get_ticks() / 50) >= 0):
        #if (self.timers["take_damage_cd"].active and int(self.frame_index) % 2 == 0): # if using last 2 frames the same.
            white_mask = pygame.mask.from_surface(self.image)
            white_surface = white_mask.to_surface()
            white_surface.set_colorkey('black')
            self.image = white_surface
    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()
            
    def animate(self, dt):
        self.frame_index += self.animation_speed * dt/FPS_TARGET

        if (self.state == "hit"):
            #when timer is finished then toggle off is_hit
            if (self.timers["take_damage_cd"].active):
                if (self.frame_index >= len(self.frames[self.state])):
                    # first frame is the initial knockback
                    # stay on last frame until timer is finished
                    self.frame_index = len(self.frames[self.state]) - 1
            else:
                self.frame_index = 0
                self.is_hit = False
                self.get_state()
        elif (self.is_attacking):
            if (self.state in ["right_throw", "throw"]):
                if (int(self.frame_index) >= 1 and self.frame_index < len(self.frames[self.state])):
                    # frame that should throw projectile
                    if (not self.has_thrown and self.func_create_ball is not None):
                        self.func_create_ball(self.weapon_list[self.current_weapon_index]["weapon"].rect.center, self.angle_to_fire, self.id)
                        self.has_thrown = True
                    # hide weapon temporarily
                    self.weapon_list[self.current_weapon_index]["weapon"].hide_weapon(True)
                elif(self.frame_index >= len(self.frames[self.state])):
                    self.frame_index = 0
                    self.is_attacking = False
                    self.has_thrown = False
                    self.timers[self.weapon_list[self.current_weapon_index]["timer_attack"]].deactivate()
                    self.weapon_list[self.current_weapon_index]["weapon"].hide_weapon(False)
                    self.get_state()

            elif (self.state in ["slash", "thrust"]):
                if (int(self.frame_index) >= len(self.frames[self.state])):
                    # just hold on last frame
                    self.frame_index = len(self.frames[self.state]) - 1

                #     # last frame is resting place at end. set that it does no damage.
                #     self.weapon_list[self.current_weapon_index]["weapon"].set_can_damage(False)
                # elif (self.frame_index >= len(self.frames[self.state])):
                #     # attack complete
                #     # responsibility of dev to match the duration of the attack rotation to the animation speed
                #     self.frame_index = 0    
                #     self.weapon_list[self.current_weapon_index]["weapon"].set_can_damage(False)
                #     self.is_attacking = False
                #     self.get_state()

        if (self.frame_index >= len(self.frames[self.state])):
            self.frame_index = 0

        self.image = self.frames[self.state][int(self.frame_index)]
        #self.image = self.image if self.facing_right else pygame.transform.flip(self.image, True, False)
        self.mask = pygame.mask.from_surface(self.image)

    def get_state(self):
        self.animation_speed = ANIMATION_SPEED

        if (not self.timers["take_damage_cd"].active):
            self.is_hit = False

        if (self.is_hit):
            self.state = "hit"
        elif (self.is_attacking and self.current_attack is not None and self.timers[self.weapon_list[self.current_weapon_index]["timer_attack"]].active):
            self.state = self.current_attack

            if (self.attack_pos.x >= self.hitbox_rect.x):
                # keep player looking at x direction of attack
                self.facing_right = True
            else:
                self.facing_right = False

            if (self.current_attack == "thrust"):
                self.animation_speed = ANIMATION_SPEED * 2

        elif (self.collision_side["bot"]):
            self.state = "idle" if self.velocity.x == 0 else "run"
        else:
            if (any((self.collision_side["left"], self.collision_side["right"]))):
                self.state = "wall"
            else:
                self.state = "jump" if self.velocity.y < 0 else "fall"

        if self.facing_right:
            self.state = "right_" + self.state
        else:
            self.state = self.state

        #print(self.state)

    def update(self, dt, event_list):

        for event in event_list:
            # for mouse inputs, better to use events because if use mouse.get_pressed it gets the state at the time of call
            if (event.type == pygame.MOUSEBUTTONDOWN):
                if (event.button == 1):
                    self.weapon_attack(event.pos)
                    #print(event.pos)
            if (event.type == pygame.MOUSEWHEEL):
                self.select_weapon(self.current_weapon_index + event.y)

            # later ball attack is a charge attack and only shoots when left button released
            # if (event.type == pygame.MOUSEBUTTONUP):
            #     if (event.button == 1):
            #         self.has_released_attack = True

        self.old_rect = self.hitbox_rect.copy()
        self.update_timers()

        # weapons
        self.weapon_management()

        # player movement
        self.player_input()
        self.horizontal_movement(dt)
        self.vertical_movement(dt)
        # recenter image rect with the hitbox rect for drawing
        self.rect.center = self.hitbox_rect.center
        #self.position = pygame.math.Vector2(self.hitbox_rect.bottomleft)
        self.check_contact()
        self.movement.collision_tweak()
        self.movement.platform_move(dt)
        
        self.get_state()
        self.animate(dt)
        self.flicker()

        #pygame.draw.rect(self.display_surface, "green", self.hitbox_rect)
        
        # reset x vel
        if (self.velocity.x > -0.01 and self.velocity.x < 0.01):
            self.velocity.x = 0

        #print(self.current_window_offset)