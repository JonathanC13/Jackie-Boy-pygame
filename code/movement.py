from settings import *

class Movement():

    def __init__(self, obj):
        self.obj = obj

    def limit_velocity(self, vel_vec, max_vel):
        """
        Limit for x velocity
        """
        vel_vec = max(-max_vel, min(vel_vec, max_vel))
        if abs(vel_vec) < .01: 
            vel_vec = 0 

    def flying_movement(self, dt, velocity):
        self.obj.hitbox_rect.center += velocity * dt

    def horizontal_movement(self, dt):
        self.obj.acceleration.x = 0
        if (self.obj.LEFT_KEY):
            self.obj.acceleration.x -= self.obj.accel_x
        if (self.obj.RIGHT_KEY):
            self.obj.acceleration.x += self.obj.accel_x
        
        self.obj.acceleration.x += self.obj.velocity.x * self.obj.friction
        self.obj.velocity.x += self.obj.acceleration.x * dt
        self.limit_velocity(self.obj.velocity.x, self.obj.vel_max_x)
        #self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        #self.hitbox_rect.x = self.position.x
        self.obj.hitbox_rect.x += self.obj.velocity.x * dt + (self.obj.acceleration.x * 0.5) * (dt * dt)

    def vertical_movement(self, dt):
        vel_y_change = 0
        if (self.obj.on_ramp_slope["on"] and not self.obj.is_jumping):
            if (self.obj.type == ENEMY_DOG):
                vel_y_change = math.ceil(abs(self.obj.velocity.x + 5))
            else:
                vel_y_change = math.ceil(abs(self.obj.velocity.x))  # 1:1 for no bouncing down ramps
        elif (not self.obj.collision_side["bot"] and any((self.obj.collision_side["left"], self.obj.collision_side["right"])) and not self.obj.is_jumping and self.obj.type == PLAYER_OBJECTS):
            if (self.obj.velocity.y < 0):
                # stop it from going any higher since touched wall
                self.obj.velocity.y = 0
            vel_y_change = (self.obj.acceleration.y / 10) * dt
        else:
            vel_y_change = self.obj.acceleration.y * dt

        self.obj.velocity.y += vel_y_change

        self.obj.velocity.y = min(self.obj.velocity.y, self.obj.vel_max_y)
        
        #self.obj.position.y += self.obj.velocity.y * dt + (self.obj.acceleration.y * 0.5) * (dt * dt)
        #self.obj.hitbox_rect.bottom = self.obj.position.y
        self.obj.hitbox_rect.bottom += self.obj.velocity.y * dt + (self.obj.acceleration.y * 0.5) * (dt * dt)

        self.obj.on_ramp_slope["on"] = False

    def platform_move(self, dt):
        """
        Adjust the player while on a moving platform
        """
        if (self.obj.platform):
            # sprite not None and (full collision or (not full collision and bottom has contact))
            self.obj.hitbox_rect.topleft += self.obj.platform.direction * self.obj.platform.speed  * dt

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
            pos_h = rel_x + self.obj.hitbox_rect.width
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
        if (tar_rect.bottom >= target_y):
            # check if the player collided with the actual ramp #and that the player y pos is level or within ramp
            # adjust player height
            #self.obj.collision_side["bot"] = True
            return (True, target_y)
        else:
            return (False, 0)
        
    def semi_collisions(self):
        if (not self.obj.timers["unlock_semi_drop_down"].active):
            # only apply floor collision if player has not expressly keyed down to drop down through the platform
            for sprite in self.obj.list_semi_collide:
                move_offset = 0
                if (sprite.type == MOVING_OBJECTS):
                    move_offset = sprite.speed

                if (self.obj.hitbox_rect.bottom >= sprite.rect.top and self.obj.old_rect.bottom - move_offset <= sprite.rect.top):
                    if (self.obj.velocity.y > 0):
                        self.obj.velocity.y = 0
                    self.obj.hitbox_rect.bottom = sprite.rect.top

    def collision(self, axis, dt):
        """
        Loop through all collision_sprites and evaluate collision
        """

        # populate collided rects
        self.obj.fill_collide_lists(self.obj.hitbox_rect)

        # for semi collision rects
        self.semi_collisions()
             
        # basic collisions (rectangular rects)
        for sprite in self.obj.list_collide_basic:
            if (axis == "horizontal"):    
                move_offset = 0
                if (sprite.type in [MOVING_OBJECTS, ENEMY_BIRD]):
                    move_offset = sprite.rect.width / 4 # abs(self.obj.velocity.x + sprite.speed * dt) # doesn't work
                    #print(move_offset)
                elif (hasattr(sprite, "velocity")):
                    # completely inelastic collision. final v = (ma * ua - mb * ub) / (ma + mb). Let ma = mb.   v = (ua - ub) / 2
                    # but sim elastic when adjust rects
                    u_a = abs(max(self.obj.velocity.x, sprite.velocity.x))
                    u_b = abs(min(self.obj.velocity.x, sprite.velocity.x))

                    final_spd = float((u_a - u_b) / 2)

                    self.obj.velocity.x = final_spd
                    sprite.velocity.x = final_spd

                    move_offset = sprite.rect.width / 4
                
                if (self.obj.hitbox_rect.left <= sprite.rect.right and self.obj.old_rect.left + move_offset >= sprite.rect.right):
                    # left collision and player approach from right
                    if (not self.obj.on_ramp_slope["on"]):
                        # fixed hitching when off ramping onto a basic tile
                        pass
                        #self.obj.velocity.x = 0
                    
                    self.obj.hitbox_rect.left = sprite.rect.right
                elif (self.obj.hitbox_rect.right >= sprite.rect.left and self.obj.old_rect.right - move_offset <= sprite.rect.left):
                    # right collision and player approach from left
                    if (not self.obj.on_ramp_slope["on"]):
                        pass
                        #self.obj.velocity.x = 0  
                    self.obj.hitbox_rect.right = sprite.rect.left
            else:
                moving_offset = 0
                if (sprite.type == MOVING_OBJECTS):
                    moving_offset = sprite.speed
                    
                # vertical
                if (self.obj.hitbox_rect.bottom >= sprite.rect.top and self.obj.old_rect.bottom - moving_offset <= sprite.rect.top):
                    # touch ground, player approaching from top
                    #self.obj.collision_side["bot"] = True
                    self.obj.velocity.y = 0
                    self.obj.hitbox_rect.bottom = sprite.rect.top
                elif (self.obj.hitbox_rect.top <= sprite.rect.bottom and self.obj.old_rect.top + moving_offset>= sprite.rect.bottom):
                    # sprite hit top, player approach from below
                    if (self.obj.is_jumping):
                        # if jumping, stop it
                        self.obj.velocity.y *= 0.25
                    self.obj.hitbox_rect.top = sprite.rect.bottom

        for sprite in self.obj.list_collide_ramps:
            # collided with frect of the ramp
            if (axis == "horizontal"):
                self.obj.on_ramp_wall = False
                if (sprite.type == TERRAIN_R_RAMP):
                    if (self.obj.hitbox_rect.left <= sprite.rect.right and self.obj.old_rect.left >= sprite.rect.right):
                        # wall of right ramp, player approach from the right
                        if (not self.obj.on_ramp_slope["on"]):
                            self.obj.on_ramp_wall = True

                        self.obj.velocity.x = 0

                        self.obj.hitbox_rect.left = sprite.rect.right
                    elif (self.obj.hitbox_rect.right >= sprite.rect.left and self.obj.old_rect.right <= sprite.rect.left and self.obj.hitbox_rect.bottom > sprite.rect.bottom):
                        # of bottom edge of slope, if below don't hook on
                        self.obj.hitbox_rect.right = sprite.rect.left
                else:                   
                    if (self.obj.hitbox_rect.right >= sprite.rect.left and self.obj.old_rect.right <= sprite.rect.left):
                        # wall of left ramp, player approach from the left
                        if (not self.obj.on_ramp_slope["on"]):
                            self.obj.on_ramp_wall = True

                        self.obj.velocity.x = 0

                        self.obj.hitbox_rect.right = sprite.rect.left
                    elif (self.obj.hitbox_rect.left <= sprite.rect.right and self.obj.old_rect.left >= sprite.rect.right and self.obj.hitbox_rect.bottom > sprite.rect.bottom):
                        self.obj.hitbox_rect.left = sprite.rect.right
            else:
                if (self.obj.hitbox_rect.top <= sprite.rect.bottom and self.obj.old_rect.top >= sprite.rect.bottom):
                    # bottom of ramp, player approach from bottom
                    if (self.obj.is_jumping):
                        self.obj.velocity.y *= 0.25
                    self.obj.hitbox_rect.top = sprite.rect.bottom
                elif (not self.obj.on_ramp_wall): 
                    res = self.collision_ramp(self.obj.hitbox_rect, sprite)
                    if (res[0]):
                        self.obj.on_ramp_slope["on"] = True
                        self.obj.on_ramp_slope["ramp_type"] = sprite.type

                        self.obj.velocity.y = 0
                        self.obj.hitbox_rect.bottom = res[1]

    def collision_tweak(self):
        # involves both axes and both conditions are external states assgined externally
        if (self.obj.on_ramp_slope["on"] and self.obj.collision_side["top"]):
            # handle on ramp but top is restricted.
            self.obj.collision_side["top"] = False

            if (self.obj.is_jumping):
                # if jumping, stop it
                self.obj.velocity.y *= 0.25

            # move back so to not be in contact with tile above
            # offset = vector(0, 0)
            # if (self.obj.on_ramp_slope["ramp_type"] == TERRAIN_R_RAMP):
            #     offset = -offset
            temp = self.obj.old_rect.center #+ offset
            self.obj.hitbox_rect.center = self.obj.old_rect.center #+ offset
            self.obj.old_rect.center = temp   

            self.obj.velocity.x = 0
    
    