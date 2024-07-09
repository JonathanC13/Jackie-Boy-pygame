from random import uniform

from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite, Orbit
from player import Player
from groups import AllSprites
from enemies import Dog
from weapons import Stick

class Level:

    def __init__(self, level_data, level_frames):

        self.display_surface = pygame.display.get_surface()

        self.stage_main = level_data[0]
        self.stage_sub = level_data[1]
        self.tmx_map = level_data[2]

        self.tmx_map_max_width = self.tmx_map.width

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        #self.all_sprites = AllSprites()
        self.player_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.ramp_collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        # self.masked_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.dog_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()

        self.setup(level_frames)

    def setup(self, level_frames):
        """
        get the layers and objects from the tmx_map and store them in the correct list
        """
        # layers
        for layer in [BG, TERRAIN_BASIC, TERRAIN_R_RAMP, TERRAIN_L_RAMP, TERRAIN_FLOOR_ONLY, PLATFORMS_PARTIAL, FG]:
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
                # elif (layer in [PLATFORMS_PARTIAL]):
                #     z = Z_LAYERS["terrain"]
                #     groups.append(self.masked_sprites)
                elif (layer in [TERRAIN_FLOOR_ONLY]):
                    z = Z_LAYERS["terrain"]
                    groups.append(self.semi_collision_sprites)
                elif (layer in [FG]):
                    z = Z_LAYERS["fg"]

                Sprite(
                    pos = (x * TILE_SIZE, y * TILE_SIZE), 
                    surf = surf, 
                    groups = groups, 
                    type = layer, 
                    z = z)

        # objects
        for obj_layer in [BG_DETAILS, MID_DETAILS]:
            for obj in self.tmx_map.get_layer_by_name(obj_layer):
                z = Z_LAYERS["bg_details"]
                if (obj_layer == BG_DETAILS):
                    z = Z_LAYERS["bg_details"]
                elif (obj_layer == MID_DETAILS):
                    z = Z_LAYERS["mid_details"]

                Sprite(
                    pos = (obj.x, obj.y), 
                    surf = obj.image, 
                    groups = self.all_sprites, 
                    type = obj_layer, 
                    z = z)
                
        # moving objects
        for obj in self.tmx_map.get_layer_by_name(MOVING_OBJECTS):
            if (obj.name == "bats"):
                Orbit(
					pos = (obj.x + obj.width / 2, obj.y + obj.height / 2),
					frames = level_frames["bats"],
					radius = obj.properties["radius"],
					speed = obj.properties["speed"],
					start_angle = obj.properties["angle_start"],
					end_angle = obj.properties["angle_end"],
                    clockwise = obj.properties["clockwise"],
                    groups = (self.all_sprites, self.damage_sprites),
                    type = MOVING_OBJECTS,
                    direction_changes = -1,
                    rotate = False)

            elif (obj.name in ("platform", "boat")):
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

                MovingSprite(
                    frames = level_frames[obj.name], 
                    start_pos = start_pos, 
                    end_pos = end_pos, 
                    path_plane = path_plane, 
                    start_end = start_end, 
                    speed = speed, 
                    full_collision = full_collision, 
                    flip = flip, 
                    groups = groups,
                    type = MOVING_OBJECTS, 
                    z = Z_LAYERS["main"])

        # general objects
        for obj in self.tmx_map.get_layer_by_name(GENERAL_OBJECTS):
            if (obj.name == "invis_wall"):
                image = pygame.Surface([obj.width,obj.height], pygame.SRCALPHA, 32)
                image = image.convert_alpha()
                Sprite(
                    pos = (obj.x, obj.y), 
                    surf = image, 
                    groups = (self.all_sprites, self.collision_sprites), 
                    type = GENERAL_OBJECTS, 
                    z = Z_LAYERS["invis"])
            elif ("ROCK" in str.upper(obj.name)):
                # non-animated
                Sprite(
                    pos = (obj.x, obj.y), 
                    surf = obj.image, 
                    groups = (self.all_sprites, self.collision_sprites), 
                    type = GENERAL_OBJECTS, 
                    z = Z_LAYERS["main"])
            else:
                # animated
                # frames 
                # thorns and floor spikes
                frames = level_frames[obj.name]
                if obj.name == "floor_spikes" and obj.properties["inverted"]:
                    frames = [pygame.transform.flip(frame, False, True) for frame in frames]

                # groups 
                groups = [self.all_sprites]
                if obj.name in ("thorn_bush", "floor_spike"): 
                    groups.append(self.damage_sprites)

                # z index
                z = Z_LAYERS["main"] if not "bg" in obj.name else Z_LAYERS["bg_details"]

                AnimatedSprite(
                    pos = (obj.x, obj.y), 
                    frames = frames, 
                    groups = groups, 
                    type = GENERAL_OBJECTS, 
                    z = z,
                    animation_speed = ANIMATION_SPEED)

        # player objects
        for obj in self.tmx_map.get_layer_by_name(PLAYER_OBJECTS):
            if (obj.name == "player"):
                #self.player = Player((obj.x, obj.y), (obj.width, obj.height), self.all_sprites, self.collision_sprites, self.semi_collision_sprites, self.ramp_collision_sprites, None)
                self.player = Player(
                                pos = (obj.x, obj.y), 
                                surf = obj.image, 
                                groups = (self.all_sprites, self.player_sprites), 
                                collision_sprites = self.collision_sprites, 
                                semi_collision_sprites = self.semi_collision_sprites, 
                                ramp_collision_sprites = self.ramp_collision_sprites,
                                enemy_sprites = self.enemy_sprites,
                                frames = None,
                                type = PLAYER_OBJECTS)
                
        # enemies
        for obj in self.tmx_map.get_layer_by_name(ENEMY_OBJECTS):
            if (obj.name == "dog"):
                dog_obj = Dog(
                    pos = (obj.x, obj.y),
                    frames = level_frames["dog"],
                    groups = (self.all_sprites, self.enemy_sprites, self.dog_sprites),
                    collision_sprites = self.collision_sprites,
                    semi_collision_sprites = self.semi_collision_sprites, 
                    ramp_collision_sprites = self.ramp_collision_sprites,
                    player_sprites = self.player_sprites,
                    enemy_sprites = self.enemy_sprites,
                    type = obj.name
                    )
                
                # each dog gets a stick as a weapon
                dog_obj.weapon = Stick(
                    pos = (obj.x, obj.y),
                    groups = (self.all_sprites, self.damage_sprites),
                    frames = level_frames["stick"],
                    owner = dog_obj,
                    damage = 1,
                    damage_type = STICK,
                    level = 1,
                    attack_cooldown = 500,
                    attack_speed = 1
                )

        # for spr in self.enemy_sprites:
        #     print(spr.weapon.level)
                
        # items
        
        # water

        # triggers

    # handle item, damage, end level collisions here

    def run(self, dt, event_list):
        # game loop here for level. like checking collisions and updating screen
        self.display_surface.fill("black")

        # update sprites
        self.all_sprites.update(dt, event_list)

        # draw all sprites
        self.all_sprites.draw(self.display_surface)
        #self.all_sprites.draw(self.player.hitbox_rect.center, self.player.hitbox_rect.width, self.tmx_map_max_width)
