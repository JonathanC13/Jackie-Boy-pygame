from settings import *
from sprites import Sprite
from player import Player

class Level:

    def __init__(self, level_data):

        self.display_surface = pygame.display.get_surface()

        self.stage_main = level_data[0]
        self.stage_sub = level_data[1]
        self.tmx_map = level_data[2]

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()

        self.setup()

    def setup(self):
        """
        get the layers and objects from the tmx_map and store them in the correct list
        """

        # tiles for terrain
        for layer in [BG, TERRAIN_BASIC, TERRAIN_R_RAMP, TERRAIN_L_RAMP]:
            for x, y, surf in self.tmx_map.get_layer_by_name(layer).tiles():
                if (layer == BG):
                    Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.all_sprites, layer)
                else:
                    Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, (self.all_sprites, self.collision_sprites), layer)

        # object for player
        for obj in self.tmx_map.get_layer_by_name("Objects"):
            if (obj.name == "testPlayer"):
                self.player = Player((obj.x, obj.y), (obj.width, obj.height), self.all_sprites, self.collision_sprites)

    def run(self, dt):
        # game loop here for level. like checking collisions and updating screen
        self.display_surface.fill("black")

        # update sprites
        self.all_sprites.update(dt)

        # draw all sprites
        self.all_sprites.draw(self.display_surface)

        
        