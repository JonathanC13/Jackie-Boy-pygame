from settings import *
from timerClass import Timer

class Player(pygame.sprite.Sprite):

    def __init__(self, pos, surf = pygame.Surface((TILE_SIZE,TILE_SIZE)), groups = None, collision_sprites = None):
        super().__init__(groups)

        self.display_surface = pygame.display.get_surface()

        self.image = pygame.Surface(surf)
        self.image.fill("red")
        # rects
        self.rect = self.image.get_frect(topleft = pos)
        # previous rect in previous frame to know which direction this rect came from
        self.old_rect = self.rect.copy()

        # collision
        self.collision_sprites = collision_sprites
        self.on_ramp_wall = False   # flag for same sprite
        self.on_ramp_slope = {"on": False, "ramp_type": None} 
        self.collision_side = {"top": False, "left": False, "bot": False, "right": False}
        self.list_collide_basic = []
        self.list_collide_ramps = []

        # movement
        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT = False, False, False
        self.is_jumping = False
        self.gravity, self.friction = GRAVITY_NORM, -0.12   # incr frict for less slide
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        # timer
        self.timers = {
            "wall_jump_move_block": Timer(200)  # blocks the use of LEFT and RIGHT right after wall jump
        }

    def player_input(self):
        keys = pygame.key.get_pressed()

        # key down
        if (keys[pygame.K_SPACE]):
            self.jump()

        if (not self.timers["wall_jump_move_block"].active):
            # blocks these keys if just jumped off a wall. Prevent infinite climbing with wall jump
            if (keys[pygame.K_LEFT]):
                self.LEFT_KEY = True
            if (keys[pygame.K_RIGHT]):
                self.RIGHT_KEY = True
        
        # key up
        if (not keys[pygame.K_SPACE]):
            if (self.is_jumping):
                self.velocity.y *= 0.25
                self.is_jumping = False
        if (not keys[pygame.K_LEFT]):
            self.LEFT_KEY = False
        if (not keys[pygame.K_RIGHT]):
            self.RIGHT_KEY = False

    def horizontal_movement(self, dt):
        """
        Blending Newton's Laws and Kinematic Equations for x
        """
        self.acceleration.x = 0
        if (self.LEFT_KEY):
            self.acceleration.x -= PLAYER_ACCEL
        if (self.RIGHT_KEY):
            self.acceleration.x += PLAYER_ACCEL
        
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        self.limit_velocity(self.velocity.x, PLAYER_MAX_VEL_X)
        self.rect.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)

        self.collision("horizontal")

    def vertical_movement(self, dt):
        """
        Blending Newton's Laws and Kinematic Equations for y
        """ 
        vel_y_change = 0
        if (self.on_ramp_slope["on"] and not self.is_jumping):
            vel_y_change = math.ceil(abs(self.velocity.x))  # 1:1
        elif (not self.collision_side["bot"] and any((self.collision_side["left"], self.collision_side["right"])) and not self.is_jumping):
            if (self.velocity.y < 0):
                # stop it from going any higher since touched wall
                self.velocity.y = 0
            vel_y_change = (self.acceleration.y / 10) * dt
        else:
            vel_y_change = self.acceleration.y * dt

        self.velocity.y += vel_y_change

        if (self.velocity.y > PLAYER_MAX_VEL_Y):
            self.velocity.y = PLAYER_MAX_VEL_Y 
        
        self.rect.bottom += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)

        self.on_ramp_slope["on"] = False
        self.collision("vertical")

    def limit_velocity(self, vel_vec, max_vel):
        """
        Limit for x velocity
        """
        vel_vec = max(-max_vel, min(vel_vec, max_vel))
        if abs(vel_vec) < .01: 
            vel_vec = 0 

    def jump(self):
        """
        1. Normal jump. Bottom true, top false, and not currenly is_jumping = Jump and apply normal gravity. is_jumping back to false when touch ground or space released
        2. Normal jump then touches wall. Bottom true, top false, and not currenly is_jumping = Jump. Contact with side wall.
            2.1. If space held, is_jump remains True and apply normal gravity
            2.2. If space released while on wall, is_jump changes to True. Allows wall jump and initial x direction is away from the wall.
        """
        if (self.collision_side["bot"] and not self.collision_side["top"] and not self.is_jumping):
            self.is_jumping = True
            self.velocity.y -= PLAYER_VEL_Y
            #self.collision_side["bot"] = False
        elif (not self.collision_side["bot"] and any((self.collision_side["left"], self.collision_side["right"])) and not self.is_jumping and not self.timers["wall_jump_move_block"].active):
            self.is_jumping = True
            self.velocity.y -= PLAYER_VEL_Y * 0.7
            # force jump away from wall
            self.velocity.x = PLAYER_MAX_VEL_X if self.collision_side["left"] else -PLAYER_MAX_VEL_X

            self.timers["wall_jump_move_block"].activate()
            self.LEFT_KEY = False
            self.RIGHT_KEY = False

    def fill_collide_lists(self, tar_rect, sprite_group):
        # tiles
        self.list_collide_basic = []
        self.list_collide_ramps = []

        for sprite in sprite_group:
            if sprite.rect.colliderect(tar_rect):
                if (sprite.type in [TERRAIN_BASIC]):
                    self.list_collide_basic.append(sprite)
                               
                elif (sprite.type in [TERRAIN_R_RAMP, TERRAIN_L_RAMP]):
                    self.list_collide_ramps.append(sprite)

    def check_contact(self):
        """
        Get current collisions on the player
        """
        # hit box is 1 pixels jutting out.
        top_rect = pygame.FRect(self.rect.topleft + vector(0, -1), (self.rect.width, 1))
        pygame.draw.rect(self.display_surface, "green", top_rect)
        bot_rect = pygame.FRect(self.rect.bottomleft, (self.rect.width, 1))
        #pygame.draw.rect(self.display_surface, "green", bot_rect)
        left_rect = pygame.FRect(self.rect.topleft + vector(-1,self.rect.height / 4), (1,self.rect.height / 2))
        #pygame.draw.rect(self.display_surface, "green", left_rect)
        right_rect = pygame.FRect(self.rect.topright + vector(0,self.rect.height / 4),(1,self.rect.height / 2))
        #pygame.draw.rect(self.display_surface, "green", right_rect)
        collide_rects = [sprite.rect for sprite in self.collision_sprites if sprite.type == TERRAIN_BASIC]
        collide_ramps = [sprite for sprite in self.collision_sprites if sprite.type in [TERRAIN_R_RAMP, TERRAIN_L_RAMP]]
        
        # check collisions
        # top
        curr_top_collide = True if (top_rect.collidelist(collide_rects) >= 0) else False
        # ground - floor
        curr_bot_collide = True if (bot_rect.collidelist(collide_rects) >= 0) else False
        # left
        curr_left_collide = True if (left_rect.collidelist(collide_rects) >= 0) else False
        # right
        curr_right_collide = True if (right_rect.collidelist(collide_rects) >= 0) else False
        # ramps
        for spr in collide_ramps:
            if (top_rect.colliderect(spr.rect)):
                curr_top_collide = True
            elif (bot_rect.colliderect(spr.rect) and self.collision_ramp(bot_rect, spr)[0]):
                curr_bot_collide = True
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
        #print(self.collision_side)

    def collision(self, axis):
        """
        Loop through all collision_sprites and evaluate collision
        """
        # involves both axes and both conditions are external states assgined externally
        if (self.on_ramp_slope["on"] and self.collision_side["top"]):
            # handle on ramp but top is restricted.
            self.collision_side["top"] = False

            if (self.is_jumping):
                # if jumping, stop it and set flag so input key up doesn't apply this again
                self.velocity.y *= 0.25
                self.is_jumping = False

            self.velocity.x = 0
            # move back to the previous position so not in contact with tile above
            offset = 1
            if (self.on_ramp_slope["ramp_type"] == TERRAIN_R_RAMP):
                offset = -1
            temp = self.old_rect.left + offset
            self.rect.left = self.old_rect.left + offset
            self.old_rect.left = temp   

        # populate collided rects
        self.fill_collide_lists(self.rect, self.collision_sprites)

        # terrain basic first
        for sprite in self.list_collide_basic:
            if (axis == "horizontal"):
                if (self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right):
                    # left collision and approach from right
                    if (not self.on_ramp_slope["on"]):
                        # fixed hitching when off ramping onto a basic tile
                        self.velocity.x = 0

                    self.rect.left = sprite.rect.right
                elif (self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left):
                    # right collision and approach from left
                    if (not self.on_ramp_slope["on"]):
                        self.velocity.x = 0  

                    self.rect.right = sprite.rect.left          
            else:
                # vertical
                if (self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.rect.top):
                    # touch ground, approaching from top
                    #self.collision_side["bot"] = True
                    self.velocity.y = 0
                    self.rect.bottom = sprite.rect.top
                elif (self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom):
                    # sprite hit top, approach from below
                    if (self.is_jumping):
                        # if jumping, stop it and set flag so input key up doesn't apply this again
                        self.velocity.y *= 0.25
                        self.is_jumping = False
                    self.rect.top = sprite.rect.bottom

        for sprite in self.list_collide_ramps:
            # collided with frect of the ramp
            if (axis == "horizontal"):
                self.on_ramp_wall = False
                if (sprite.type == TERRAIN_R_RAMP):
                    if (self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right):
                        # wall of right ramp, approach from the right
                        self.on_ramp_wall = True

                        self.velocity.x = 0

                        self.rect.left = sprite.rect.right
                    elif (self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left and self.rect.bottom > sprite.rect.bottom):
                        # of bottom edge of slope, if below don't hook on
                        self.rect.right = sprite.rect.left
                else:                   
                    if (self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left):
                        # wall of left ramp, approach from the left
                        self.on_ramp_wall = True

                        self.velocity.x = 0

                        self.rect.right = sprite.rect.left
                    elif (self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right and self.rect.bottom > sprite.rect.bottom):
                        self.rect.left = sprite.rect.right
            else:
                if (self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom):
                    # bottom of ramp, approach from bottom
                    if (self.is_jumping):
                        self.velocity.y *= 0.25
                        self.is_jumping = False
                    self.rect.top = sprite.rect.bottom
                elif (not self.on_ramp_wall): 
                    res = self.collision_ramp(self.rect, sprite)
                    if (res[0]):
                        self.on_ramp_slope["on"] = True
                        self.on_ramp_slope["ramp_type"] = sprite.type

                        self.velocity.y = 0
                        self.rect.bottom = res[1]
                    
    def collision_ramp(self, tar_rect, ramp_sprite):
        """
        check collision of ramp sprites
        return (bool, float)
        """
        #center = tar_rect.width / 2
        # player x position relative to the ramp
        rel_x = tar_rect.x - ramp_sprite.rect.x

        # determine player new height based on the ramp type
        # since the ramp is a right isoceles, height can be determined by the overlap in the x axis
        if (ramp_sprite.type == TERRAIN_R_RAMP):
            # right edge
            pos_h = rel_x + self.rect.width
            # center
            #pos_h = rel_x + center
        else:
            pos_h = TILE_SIZE - rel_x
            #pos_h = TILE_SIZE - rel_x - center

        # bounds
        pos_h = min(pos_h, TILE_SIZE)
        pos_h = max(pos_h, 0)

        # height that will be in the ramp tile
        target_y = ramp_sprite.rect.y + TILE_SIZE - pos_h
        #print(tar_rect.bottom, ":", target_y)
        if (tar_rect.bottom >= target_y and tar_rect.bottom - 1 <= ramp_sprite.rect.bottom): 
            # check if the player collided with the actual ramp and that the player y pos is level or within ramp
            # adjust player height
            #self.collision_side["bot"] = True
            return (True, target_y)
        else:
            return (False, 0)
            
    def rot_center(self, image, angle, x, y):
    
        rotated_image = pygame.transform.rotate(image, angle)
        new_rect = rotated_image.get_frect(center = image.get_rect(center = (x, y)).center)

        return rotated_image, new_rect
    
    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

    def update(self, dt):
        self.old_rect = self.rect.copy()

        self.update_timers()

        # player movement
        self.player_input()
        self.horizontal_movement(dt)
        self.vertical_movement(dt)

        self.check_contact()