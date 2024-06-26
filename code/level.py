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
        # tiles for terrain
        for layer in [BG, TERRAIN_BASIC, TERRAIN_R_RAMP, TERRAIN_L_RAMP, TERRAIN_FLOOR_ONLY,PLATFORMS_PARTIAL, FG]:
            for x, y, surf in self.tmx_map.get_layer_by_name(layer).tiles():
                groups = [self.all_sprites]
                if (layer == BG):
                    z = Z_LAYERS["bg"]
                elif (layer in [TERRAIN_BASIC]): 
                    z = Z_LAYERS["main"]
                    groups.append(self.collision_sprites)
                elif (layer in [TERRAIN_R_RAMP, TERRAIN_L_RAMP]):
                    z = Z_LAYERS["main"]
                    groups.append(self.ramp_collision_sprites)
                elif (layer in [PLATFORMS_PARTIAL]):
                    z = Z_LAYERS["main"]
                    groups.append(self.masked_sprites)
                elif (layer in [TERRAIN_FLOOR_ONLY]):
                    z = Z_LAYERS["main"]
                    groups.append(self.semi_collision_sprites)
                elif (layer in [FG]):
                    z = Z_LAYERS["fg"]
                    
                Sprite((x * TILE_SIZE, y * TILE_SIZE), surf, groups, layer, z)

        
        for obj in self.tmx_map.get_layer_by_name(BG_DETAILS):
            pass

        # moving objects
        for obj in self.tmx_map.get_layer_by_name(MOVING_OBJECTS):
            if (obj.name == "platform"):
                if (obj.width > obj.height):
                    # horizontal path
                    path_plane = "x"
                    start_pos = (obj.x, obj.y + (obj.height / 2))
                    end_pos = (obj.x + obj.width, obj.y + (obj.height / 2))
                else:
                    # vertical path
                    path_plane = "y"
                    start_pos = (obj.x + (obj.width / 2), obj.y)
                    end_pos = (obj.x + (obj.width / 2), obj.y + obj.height)
                flip = obj.properties["flip"]
                full_collision = obj.properties["full_collision"]
                speed = obj.properties["speed"]
                start_end = obj.properties["start_end"]

                groups = [self.all_sprites]
                if (full_collision):
                    groups.append(self.collision_sprites)
                else:
                    groups.append(self.semi_collision_sprites)
                groups = tuple(groups)

                MovingSprite(start_pos, end_pos, path_plane, start_end, speed, full_collision, groups, False, MOVING_OBJECTS)

        # general objects
        for obj in self.tmx_map.get_layer_by_name(GENERAL_OBJECTS):
            if (obj.name in ("crate", "barrel")):
                # non-animated
                Sprite((obj.x, obj.y), obj.image, (self.all_sprites, self.collision_sprites), GENERAL_OBJECTS, Z_LAYERS["main"])
            else:
                # animated
                # frames 
                frames = level_frames[obj.name] if not 'palm' in obj.name else level_frames['palms'][obj.name]
                if obj.name == 'floor_spike' and obj.properties['inverted']:
                    frames = [pygame.transform.flip(frame, False, True) for frame in frames]

                # groups 
                groups = [self.all_sprites]
                if obj.name in('palm_small', 'palm_large'): 
                    groups.append(self.semi_collision_sprites)
                elif obj.name in ('saw', 'floor_spike'): 
                    groups.append(self.damage_sprites)

                # z index
                z = Z_LAYERS['main'] if not 'bg' in obj.name else Z_LAYERS['bg_details']

                # animation speed
                animation_speed = ANIMATION_SPEED if not 'palm' in obj.name else ANIMATION_SPEED + uniform(-1,1)

                AnimatedSprite((obj.x, obj.y), frames, groups, GENERAL_OBJECTS, z, animation_speed)

        # player objects
        for obj in self.tmx_map.get_layer_by_name(PLAYER_OBJECTS):
            if (obj.name == "testPlayer"):
                #self.player = Player((obj.x, obj.y), (obj.width, obj.height), self.all_sprites, self.collision_sprites)
                self.player = Player((obj.x, obj.y), (obj.width, obj.height), self.all_sprites, self.collision_sprites, self.semi_collision_sprites, self.ramp_collision_sprites, self.masked_sprites, level_frames["player"])

    def run(self, dt, event_list):
        # game loop here for level. like checking collisions and updating screen
        self.display_surface.fill("black")

        # update sprites
        self.all_sprites.update(dt, event_list)

        # draw all sprites
        self.all_sprites.draw(self.player.hitbox_rect.center, self.player.hitbox_rect.width, self.tmx_map_max_width)
