from random import randint, uniform, choice

from settings import *
from sprites import Sprite, Cloud
from timerClass import Timer

# group to sim camera, override Group class
class AllSprites(pygame.sprite.Group):

    def __init__(self, tmx_map_width, tmx_map_height, clouds, horizon_info, bg_tile = None, top_limit = 0):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector(0, 0)

        self.camera_bounds = {
            "left": 0,
            "right": -((tmx_map_width * TILE_SIZE - (0 * TILE_SIZE)) - WINDOW_WIDTH),
            "top": -top_limit,
            "bottom": -((tmx_map_height * TILE_SIZE) - WINDOW_HEIGHT)
        }

        self.tmx_map_width = tmx_map_width
        self.tmx_map_height = tmx_map_height
        self.top_limit = -top_limit
        self.bg_tile = bg_tile
        self.sky = not bg_tile

        self.horizon_line = horizon_info['horizon_line']
        self.horizon_line_colour = horizon_info['horizon_line_colour']
        self.horizon_colour = horizon_info['horizon_colour']

        # cloud frames
        self.large_cloud = clouds['large']
        self.small_cloud = clouds['small']

        self.cloud_direction = -1

        # large clouds
        self.large_cloud_speed = 0.25
        self.large_cloud_x = 0
        self.large_cloud_tiles = int((self.tmx_map_width * TILE_SIZE) / self.large_cloud.get_width()) + 2
        self.large_cloud_width, self.large_cloud_height = self.large_cloud.get_size()

        # smaller clouds
        # timer -> cloud every 2.5 seconds
        # lots of clouds on init
        self.small_cloud_init_num = 0#21        # if fps worsening, lessen init clouds and increase cloud spawn timer
        self.small_cloud_speed_min = 0.25
        self.small_cloud_speed_max = 0.5
        self.init_small_clouds()
        
        self.draw_bg()

    def init_small_clouds(self):
        self.small_cloud_timer = Timer(5000, self.create_small_cloud, True) # 2500
        self.small_cloud_timer.activate()

        for cloud in range(self.small_cloud_init_num):
            surface = choice(self.small_cloud)
            x = randint(0, self.tmx_map_width * TILE_SIZE)
            y = randint(self.camera_bounds["top"], self.horizon_line)
            speed = uniform(self.small_cloud_speed_min, self.small_cloud_speed_max)
            Cloud((x, y), surface, self, type = 'cloud', z = Z_LAYERS["clouds"], speed = speed)

    def create_small_cloud(self):
        surface = choice(self.small_cloud)
        x = randint(self.tmx_map_width * TILE_SIZE + 100, self.tmx_map_width * TILE_SIZE + 200)
        y = randint(self.camera_bounds["top"], self.horizon_line)
        speed = uniform(self.small_cloud_speed_min, self.small_cloud_speed_max)
        Cloud((x, y), surface, self, type = 'cloud', z = Z_LAYERS["clouds"])

    def get_offset(self):
        return self.offset
    
    def draw_bg(self):
        # int(self.top_limit / TILE_SIZE) - 1. If top_limit is ever positive, fill the background
        
        # background if set in Tiled
        if (self.bg_tile):
            for row in range(int(-self.top_limit / TILE_SIZE) - 1, self.tmx_map_height):
                for col in range(self.tmx_map_width):
                    x = col * TILE_SIZE
                    y = row * TILE_SIZE
                    Sprite((x, y), self.bg_tile, self, DATA, Z_LAYERS["bg_env"])

    def draw_sky(self):
        self.display_surface.fill("#84bee5")

        horizon_y = self.horizon_line + self.offset.y

        sea_rect = pygame.FRect(0, horizon_y, WINDOW_WIDTH, WINDOW_HEIGHT - horizon_y)
        pygame.draw.rect(self.display_surface, self.horizon_colour, sea_rect)

        pygame.draw.line(self.display_surface, self.horizon_line_colour, (0, horizon_y), (WINDOW_WIDTH, horizon_y), 2)

    def draw_large_cloud(self, dt):
        self.large_cloud_x += self.cloud_direction * self.large_cloud_speed * dt
        if (self.large_cloud_x <= -self.large_cloud_width):
            # reset
            self.large_cloud_x = 0
        for cloud in range(self.large_cloud_tiles):
            left = self.large_cloud_x + (self.large_cloud_width * cloud) + self.offset.x
            top = self.horizon_line - self.large_cloud_height + self.offset.y
            self.display_surface.blit(self.large_cloud, (left, top))

    def draw(self, target_pos, dt):
        
        # moving away from origin, increasingly negative
        self.offset.x = -(target_pos[0] - (WINDOW_WIDTH / 2))
        self.offset.y = -(target_pos[1] - (WINDOW_HEIGHT / 2))

        # bounds
        self.offset.x = max(min(self.offset.x, 0), self.camera_bounds["right"])    # - WINDOW_WIDTH to keep the last window at the upper limit one game screen wide
        self.offset.y = max(min(self.offset.y, self.camera_bounds["top"]), self.camera_bounds["bottom"])

        if self.sky:
            self.small_cloud_timer.update()
            self.draw_sky()
            self.draw_large_cloud(dt)

        for sprite in sorted(self, key = lambda sprite : sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            # get all sprites in this group
            self.display_surface.blit(sprite.image, offset_pos)