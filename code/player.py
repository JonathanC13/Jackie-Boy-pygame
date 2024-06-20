from settings import *

class Player(pygame.sprite.Sprite):

    def __init__(self, pos, surf = pygame.Surface((TILE_SIZE,TILE_SIZE)), groups = None, collision_sprites = None):
        super().__init__(groups)

        self.image = pygame.Surface(surf)
        self.image.fill("red")
        # rects
        self.rect = self.image.get_frect(topleft = pos)
        # previous rect in previous frame to know which direction this rect came from
        self.old_rect = self.rect.copy()

        # collision
        self.collision_sprites = collision_sprites
        self.touch_ramp_wall = False

        # movement
        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT = False, False, False
        self.is_jumping, self.on_ground = False, False
        self.gravity, self.friction = 0.35, -0.12   # incr frict for less slide
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)

    def player_input(self):
        keys = pygame.key.get_pressed()

        # key down
        if (keys[pygame.K_SPACE]):
            self.jump()
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
        self.limit_velocity(4)
        self.rect.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)

        self.collision("horizontal")

    def vertical_movement(self, dt):
        """
        Blending Newton's Laws and Kinematic Equations for y
        """
        self.velocity.y += self.acceleration.y * dt
        if (self.velocity.y > PLAYER_MAX_VEL_X):
            self.velocity.y = PLAYER_MAX_VEL_X
        
        self.rect.bottom += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)

        self.collision("vertical")

    def limit_velocity(self, max_vel):
        """
        Limit for x velocity
        """
        self.velocity.x = max(-max_vel, min(self.velocity.x, max_vel))
        if abs(self.velocity.x) < .01: 
            self.velocity.x = 0 

    def jump(self):
        if (self.on_ground):
            self.is_jumping = True
            self.velocity.y -= PLAYER_VEL_Y
            self.on_ground = False 

    def collision(self, axis):
        """
        Loop through all collision_sprites and evaluate collision
        """
        for sprite in self.collision_sprites:
            if sprite.rect.colliderect(self.rect):
                if (sprite.type in [TERRAIN_BASIC]):
                    if (axis == "horizontal"):
                        if (self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right):
                            # left collision and approach from right
                            self.velocity.x = 0
                            self.rect.left = sprite.rect.right

                        if (self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left):
                            # right collision and approach from left
                            self.velocity.x = 0
                            self.rect.right = sprite.rect.left

                        # Ignore if player left or right and old_rect is within the sprite.
                        #   This is perfect since when the player is on top, it does not update
                    else:
                        # vertical
                        if (self.rect.bottom >= sprite.rect.top and self.old_rect.bottom <= sprite.rect.top):
                            # touch ground, approaching from top
                            self.on_ground = True
                            self.velocity.y = 0
                            self.rect.bottom = sprite.rect.top

                        
                        # sprite hit top, approach from below
                        if (self.rect.top <= sprite.rect.bottom and self.old_rect.top >= sprite.rect.bottom):
                            if (self.is_jumping):
                                # if jumping, stop it
                                self.velocity.y *= 0.25
                                self.is_jumping = False
                            self.rect.top = sprite.rect.bottom
                            
                elif (sprite.type in [TERRAIN_R_RAMP, TERRAIN_L_RAMP]):
                    # collided with frect of the ramp
                    if (axis == "horizontal"):
                        self.touch_ramp_wall = False
                        if (self.rect.left <= sprite.rect.right and self.old_rect.left >= sprite.rect.right and sprite.type == TERRAIN_R_RAMP):
                            # wall of right ramp, approach from the right
                            self.velocity.x = 0
                            self.rect.left = sprite.rect.right
                            self.touch_ramp_wall = True
                        
                        if (self.rect.right >= sprite.rect.left and self.old_rect.right <= sprite.rect.left and sprite.type == TERRAIN_L_RAMP):
                            # wall of left ramp, approach from the left
                            self.velocity.x = 0
                            self.rect.right = sprite.rect.left
                            self.touch_ramp_wall = True
                    else:
                        if (not self.touch_ramp_wall):
                            # player x position relative to the ramp
                            rel_x = self.rect.x - sprite.rect.x

                            # determine player new height based on the ramp type
                            # since the ramp is a right isoceles, height can be determined by the overlap in the x axis
                            if (sprite.type == TERRAIN_R_RAMP):
                                # right side
                                pos_h = rel_x + self.rect.width
                            else:
                                pos_h = TILE_SIZE - rel_x

                            # bounds
                            pos_h = min(pos_h, TILE_SIZE)
                            pos_h = max(pos_h, 0)

                            # height that will be in the ramp tile
                            target_y = sprite.rect.y + TILE_SIZE - pos_h

                            if (self.rect.bottom >= target_y): 
                                # check if the player collided with the actual ramp
                                # adjust player height
                                self.on_ground = True
                                self.velocity.y = 0
                                self.rect.bottom = target_y


    def update(self, dt):
        self.old_rect = self.rect.copy()
        # player movement
        self.player_input()
        self.horizontal_movement(dt)
        self.vertical_movement(dt)