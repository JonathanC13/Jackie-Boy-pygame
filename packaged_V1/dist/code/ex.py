import pygame, sys, time

FPS_TARGET = 60
TILE_SIZE = 50

class tile():
    def __init__(self, pos):
        self.pos = pos

def tile_rect(t):
    return pygame.FRect(t.pos[0] * TILE_SIZE, t.pos[1] * TILE_SIZE, TILE_SIZE, TILE_SIZE)    # topleft x, topleft y, w, h

class Player():
    def __init__(self, pos, collision_rects):
        self.pos = pos
        self.color = (0, 0, 255)
        self.rect = pygame.FRect(pos[0], pos[1], 25, 50)
        self.old_rect = self.rect

        self.collision_rects = collision_rects

        self.speed_x = 5
        self.jump_height = 10
        self.vel_max_y = 15
        self.gravity = 0.33
        self.velocity = pygame.math.Vector2(0, 0)
        self.acceleration = pygame.math.Vector2(0, self.gravity)

        self.jump = False
        self.left, self.right = False, False

    def horizontal_movement(self, dt):
        if (self.left == self.right):
            self.velocity.x = 0
        elif (self.right):
            self.velocity.x = self.speed_x
        else:
            self.velocity.x = -self.speed_x

        self.rect.x += self.velocity.x * dt

        self.collisions("x")

    def vertical_movement(self, dt):
        vel_y_change = self.acceleration.y * dt
        self.velocity.y += vel_y_change

        self.velocity.y = min(self.velocity.y, self.vel_max_y)
        
        self.rect.bottom += self.velocity.y * dt + (self.acceleration.y * 0.5) * (dt * dt)

        self.collisions("y")
    
    def jump_movement(self):
        if (not self.jump):
            self.velocity.y -= self.jump_height
            self.jump = True

    def collisions(self, axis):
        for t_rect in self.collision_rects:
            if (self.rect.colliderect(t_rect)):
                if (axis == "x"):
                    if (self.rect.right >= t_rect.left and self.old_rect.right <= t_rect.left):
                        # right collision, approach from left
                        self.rect.right = t_rect.left
                    elif (self.rect.left <= t_rect.right and self.old_rect.right >= t_rect.left):
                        self.rect.left = t_rect.right
                elif (axis == "y"):
                    if (self.rect.bottom >= t_rect.top and self.old_rect.bottom <= t_rect.top):
                        # bottom collision, approach from top
                        self.rect.bottom = t_rect.top

                        # allow jump only if on floor
                        self.velocity.y = 0
                        self.jump = False
                    elif (self.rect.top <= t_rect.bottom and self.old_rect.top >= t_rect.bottom):
                        self.velocity.y = 0

                        self.rect.top = t_rect.bottom

pygame.init()
screen = pygame.display.set_mode((500, 500))

clock = pygame.time.Clock()
previous_time = time.time()

# tiles
tiles = [tile((3, 6)), tile((1, 8)), tile((5, 8))]
for i in range(10):
    tiles.append(tile([i, 9]))

tiles_rect = []
for tile in tiles:
    tiles_rect.append(tile_rect(tile))

# player
player = Player((50, 200), tiles_rect)

while True:
    screen.fill("black")

    dt = (time.time() - previous_time) * FPS_TARGET
    previous_time = time.time()

    for event in pygame.event.get():
        if (event.type == pygame.QUIT):
            pygame.quit()
            sys.exit()

        if (event.type == pygame.KEYDOWN):
            if (event.key == pygame.K_RIGHT):
                player.right = True
            if (event.key == pygame.K_LEFT):
                player.left = True
            if (event.key == pygame.K_UP):
                player.jump_movement()

        if (event.type == pygame.KEYUP):
            if (event.key == pygame.K_RIGHT):
                player.right = False
            if (event.key == pygame.K_LEFT):
                player.left = False

    # draw background tiles
    for t_rect in tiles_rect:
        pygame.draw.rect(screen, 'red', t_rect)

    player.old_rect = player.rect.copy()        # previous pos
    # update pos
    player.horizontal_movement(dt)
    player.vertical_movement(dt)
    pygame.draw.rect(screen, player.color, player.rect) # draw
    
    pygame.display.update()

    clock.tick(FPS_TARGET)