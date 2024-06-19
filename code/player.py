from settings import *

class Player(pygame.sprite.Sprite):

    def __init__(self, pos, group, collision_sprites):
        super().__init__(group)

        self.group = group

        self.image = pygame.Surface((50, 50))
        self.image.fill("red")
        self.rect = self.image.get_rect(bottomleft = (pos[0], pos[1]))

        self.collision_sprites = collision_sprites

        # movement
        self.LEFT_KEY, self.RIGHT_KEY, self.FACING_LEFT = False, False, False
        self.is_jumping, self.on_ground = False, False
        self.gravity, self.friction = 0.35, -0.12   # incr frict for less slide
        self.position, self.velocity = pygame.math.Vector2(pos[0], pos[1]), pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)

    def player_input(self):
        keys = pygame.key.get_pressed()

        # key down
        if (keys[pygame.K_SPACE]):
            self.jump()
        
        if (keys[pygame.K_LEFT] and keys[pygame.K_RIGHT]):
            self.LEFT_KEY = False
            self.RIGHT_KEY = False   
        elif (keys[pygame.K_LEFT]):
            self.LEFT_KEY = True
        elif (keys[pygame.K_RIGHT]):
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
            self.acceleration.x -= 0.3
        elif (self.RIGHT_KEY):
            self.acceleration.x += 0.3
        
        self.acceleration.x += self.velocity.x * self.friction
        self.velocity.x += self.acceleration.x * dt
        self.limit_velocity(4)
        self.position.x += self.velocity.x * dt + (self.acceleration.x * 0.5) * (dt * dt)
        self.rect.x = self.position.x

    def vertical_movement(self, dt):
        """
        Blending Newton's Laws and Kinematic Equations for y
        """
        self.velocity.y += self.acceleration.y * dt
        if (self.velocity.y > 7):
            self.velocity.y = 7
        
        self.position.y += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)
        
        self.rect.bottom = self.position.y

    def limit_velocity(self, max_vel):
        self.velocity.x = max(-max_vel, min(self.velocity.x, max_vel))
        if abs(self.velocity.x) < .01: 
            self.velocity.x = 0 

    def jump(self):
        if (self.on_ground):
            self.is_jumping = True
            self.velocity.y -= 8
            self.on_ground = False 

    def terrain_collision(self):
        collide_lst = pygame.sprite.spritecollide(self.group.sprite, self.collision_sprites, False)

        if (collide_lst):
            for spr in collide_lst:
                self.on_ground = True
                self.velocity.y = 0
                self.group.sprite.rect.bottom = spr.rect.top

    def update(self, dt):
        # player movement
        self.player_input()
        self.horizontal_movement(dt)
        self.vertical_movement(dt)

        # check collisions
        self.terrain_collision()
        