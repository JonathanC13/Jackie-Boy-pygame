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
        self.terrain_tiles = pygame.sprite.Group()

        self.player_group = pygame.sprite.GroupSingle()
        self.player = Player()
        self.player_group.add(self.player)

        self.setup()

    def setup(self):
        # get the layers and objects from the tmx_map and store them in the correct list

        # tile for terrain
        for layer in [TERRAIN_FLAT, TERRAIN_R_RAMP, TERRAIN_L_RAMP]:
            for x, y, surf in self.tmx_map.get_layer_by_name(layer).tiles():
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, self.terrain_tiles, layer)

    def collision_terrain(self, group_single):
        collide_lst = pygame.sprite.spritecollide(group_single.sprite, self.terrain_tiles, False)

        if (collide_lst):
            collide_flat_lst = [spr for spr in collide_lst if spr.type == TERRAIN_FLAT]
            collide_ramp_lst = [spr for spr in collide_lst if spr.type in (TERRAIN_R_RAMP, TERRAIN_L_RAMP)]
            for spr in collide_flat_lst:
                print(spr.type)
            for spr in collide_ramp_lst:
                print(spr.type)

    def run(self, dt):
        # game loop here for level. like checking collisions and updating screen
        self.display_surface.fill("black")

        # update sprites
        self.player_group.update()

        # check collisions
        self.collision_terrain(self.player_group)

        # draw
        # draw terrain
        self.terrain_tiles.draw(self.display_surface)
        # draw player
        self.player_group.draw(self.display_surface)
        