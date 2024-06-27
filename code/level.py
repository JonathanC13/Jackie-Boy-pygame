from random import uniform

from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite
from player import Player
from groups import AllSprites

class Level:

    def __init__(self, level_data, level_frames):

        self.display_surface = pygame.display.get_surface()

        self.stage_main = level_data[0]
        self.stage_sub = level_data[1]
        self.tmx_map = level_data[2]

        self.tmx_map_max_width = self.tmx_map.width

        # sprite groups
        self.all_sprites = AllSprites()
        self.collision_sprites = pygame.sprite.Group()
        self.ramp_collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        self.masked_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()

        self.setup(level_frames)

    def setup(self, level_frames):
        """
        get the layers and objects from the tmx_map and store them in the correct list
        """
        # layers
        for layer in [BG, TERRAIN_BASIC, TERRAIN_R_RAMP, TERRAIN_L_RAMP, TERRAIN_FLOOR_ONLY,PLATFORMS_PARTIAL, FG]:
            for x, y, surf in self.tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if (layer == BG):
                    z = Z_LAYERS["bg"]
                elif (layer in [TERRAIN_BASIC]): 
                    z = Z_LAYERS["terrain"]
                    groups.append(self.collision_sprites)
                elif (layer in [TERRAIN_R_RAMP, TERRAIN_L_RAMP]):
                    z = Z_LAYERS["terrain"]
                    groups.append(self.ramp_collision_sprites)
                elif (layer in [PLATFORMS_PARTIAL]):
                    z = Z_LAYERS["terrain"]
                    groups.append(self.masked_sprites)
                elif (layer in [TERRAIN_FLOOR_ONLY]):
                    z = Z_LAYERS["terrain"]
                    groups.append(self.semi_collision_sprites)
                elif (layer in [FG]):
                    z = Z_LAYERS["fg"]
                    
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, layer, z)

        
        for obj in self.tmx_map.get_layer_by_name(BG_DETAILS):
            #bg_details
            pass

        for obj in self.tmx_map.get_layer_by_name(MID_DETAILS):
            Sprite((obj.x, obj.y), obj.image, self.all_sprites, MID_DETAILS, Z_LAYERS["mid_details"])

        # moving objects
        for obj in self.tmx_map.get_layer_by_name(MOVING_OBJECTS):
            pass

        # general objects
        for obj in self.tmx_map.get_layer_by_name(GENERAL_OBJECTS):
            pass


        # player objects
        for obj in self.tmx_map.get_layer_by_name(PLAYER_OBJECTS):
            if (obj.name == "player"):
                #self.player = Player((obj.x, obj.y), (obj.width, obj.height), self.all_sprites, self.collision_sprites, self.semi_collision_sprites, self.ramp_collision_sprites, self.masked_sprites, None)
                self.player = Player((obj.x, obj.y), obj.image, self.all_sprites, self.collision_sprites, self.semi_collision_sprites, self.ramp_collision_sprites, self.masked_sprites, None)

    def run(self, dt, event_list):
        # game loop here for level. like checking collisions and updating screen
        self.display_surface.fill("black")

        # update sprites
        self.all_sprites.update(dt, event_list)

        # draw all sprites
        self.all_sprites.draw(self.player.hitbox_rect.center, self.player.hitbox_rect.width, self.tmx_map_max_width)
