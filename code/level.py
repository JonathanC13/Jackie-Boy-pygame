from settings import *
from sprites import Sprite, AnimatedSprite, MovingSprite, Orbit, Item, ParticleEffectSprite
from player import Player
from groups import AllSprites
from enemies import Dog, Bird, Squirrel
from weapons import Stick, Lance, Ball
from projectiles import AcornProjectile, BallProjectile
from pathfinder import Pathfinder

class Level:

    def __init__(self, level_data, level_frames):

        self.display_surface = pygame.display.get_surface()

        self.stage_main = level_data[0]
        self.stage_sub = level_data[1]
        self.tmx_map = level_data[2]
        self.tmx_map_max_width = self.tmx_map.width

        self.acorn_frames = level_frames["acorn_projectile"]
        self.particle_frames = level_frames["effect_particle"]
        self.ball_frames = level_frames["ball_projectile"]

        # sprite groups
        self.all_sprites = pygame.sprite.Group()
        #self.all_sprites = AllSprites()
        self.player_sprite = pygame.sprite.GroupSingle()
        self.player_weapon_sprites = pygame.sprite.Group()
        self.ball_sprites = pygame.sprite.Group()
        self.collision_sprites = pygame.sprite.Group()
        self.ramp_collision_sprites = pygame.sprite.Group()
        self.semi_collision_sprites = pygame.sprite.Group()
        # self.masked_sprites = pygame.sprite.Group()
        self.enemy_sprites = pygame.sprite.Group()
        self.dog_sprites = pygame.sprite.Group()
        self.bird_sprites = pygame.sprite.Group()
        self.squirrel_sprites = pygame.sprite.Group()
        self.acorn_sprites = pygame.sprite.Group()
        self.damage_sprites = pygame.sprite.Group()
        self.item_sprites = pygame.sprite.Group()

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
                                groups = (self.all_sprites, self.player_sprite), 
                                collision_sprites = self.collision_sprites, 
                                semi_collision_sprites = self.semi_collision_sprites, 
                                ramp_collision_sprites = self.ramp_collision_sprites,
                                enemy_sprites = self.enemy_sprites,
                                frames = level_frames["player"],
                                type = PLAYER_OBJECTS,
                                func_create_ball = self.create_ball,
                                id = "player_0")
                
                stick_weapon = Stick(
                    pos = (self.player.hitbox_rect.centerx, self.player.hitbox_rect.centery),
                    groups = (self.all_sprites, self.player_weapon_sprites),
                    frames = level_frames["stick"],
                    owner = self.player,
                    level = 1
                )

                lance_weapon = Lance(
                    pos = (self.player.hitbox_rect.centerx, self.player.hitbox_rect.centery),
                    groups = (self.all_sprites, self.player_weapon_sprites),
                    frames = level_frames["beak"],
                    owner = self.player,
                    level = 1
                )

                ball_weapon = Ball(
                    pos = (self.player.hitbox_rect.centerx, self.player.hitbox_rect.centery),
                    groups = (self.all_sprites),
                    frames = level_frames["ball"],
                    owner = self.player,
                    level = 1
                )

                weapon_list = [{"weapon": stick_weapon}, {"weapon": lance_weapon}, {"weapon": ball_weapon}]
                self.player.weapon_setup(weapon_list)
       
        dog_idx = 0
        bird_idx = 0
        squirrel_idx = 0
        # enemies
        for obj in self.tmx_map.get_layer_by_name(ENEMY_OBJECTS):
            if (obj.name == "dog"):
                dog_obj = Dog(
                    pos = (obj.x, obj.y),
                    frames = level_frames["dog"],
                    groups = (self.all_sprites, self.enemy_sprites, self.dog_sprites, self.collision_sprites),
                    collision_sprites = self.collision_sprites,
                    semi_collision_sprites = self.semi_collision_sprites, 
                    ramp_collision_sprites = self.ramp_collision_sprites,
                    player_sprite = self.player_sprite,
                    enemy_sprites = self.enemy_sprites,
                    type = ENEMY_DOG,
                    id = "dog_" + str(dog_idx)
                    )
                
                # each dog gets a stick as a weapon
                dog_obj.weapon = Stick(
                    pos = (dog_obj.hitbox_rect.centerx, dog_obj.hitbox_rect.centery),
                    groups = (self.all_sprites, self.damage_sprites),
                    frames = level_frames["stick"],
                    owner = dog_obj,
                    level = 1
                )
                dog_idx += 1
            elif (obj.name == "bird"):
                bird_obj = Bird(
                    pos = (obj.x, obj.y),
                    frames = level_frames["bird"],
                    groups = (self.all_sprites, self.enemy_sprites, self.bird_sprites, self.collision_sprites),
                    collision_sprites = self.collision_sprites,
                    semi_collision_sprites = self.semi_collision_sprites,
                    ramp_collision_sprites = self.ramp_collision_sprites,
                    player_sprite = self.player_sprite,
                    enemy_sprites = self.enemy_sprites,
                    type = ENEMY_BIRD,
                    pathfinder = Pathfinder(self.tmx_map.width, self.tmx_map.height),
                    id = "bird_" + str(bird_idx)
                    )
                
                bird_obj.weapon = Lance(
                    pos = (bird_obj.hitbox_rect.centerx, bird_obj.hitbox_rect.centery),
                    groups = (self.all_sprites, self.damage_sprites),
                    frames = level_frames["beak"],
                    owner = bird_obj,
                    level = 1
                )
                bird_idx += 1
            elif (obj.name == "squirrel"):
                squirrel_obj = Squirrel(
                    pos = (obj.x, obj.y),
                    frames = level_frames["squirrel"],
                    groups = (self.all_sprites, self.enemy_sprites, self.squirrel_sprites, self.collision_sprites),
                    collision_sprites = self.collision_sprites,
                    semi_collision_sprites = self.semi_collision_sprites,
                    ramp_collision_sprites = self.ramp_collision_sprites,
                    player_sprite = self.player_sprite,
                    enemy_sprites = self.enemy_sprites,
                    type = ENEMY_SQUIRREL,
                    pathfinder = Pathfinder(self.tmx_map.width, self.tmx_map.height),
                    func_create_acorn = self.create_acorn,
                    id = "squirrel_" + str(squirrel_idx)
                    )
                squirrel_obj.weapon = Ball(
                    pos = (squirrel_obj.hitbox_rect.centerx, squirrel_obj.hitbox_rect.centery),
                    groups = (self.all_sprites),
                    frames = level_frames["acorn"],
                    owner = squirrel_obj,
                    level = 1
                )
                squirrel_idx += 1

        # for spr in self.enemy_sprites:
        #     print(spr.weapon.level)
                
        # items
        for obj in self.tmx_map.get_layer_by_name(ITEM_OBJECTS):
            Item(
                item_type = obj.name, 
                 pos = (obj.x + TILE_SIZE/2, obj.y + TILE_SIZE/2), 
                 frames = level_frames["items"][obj.name], 
                 groups = (self.all_sprites, self.item_sprites)
            )
        
        # water

        # triggers

    def create_ball(self, pos, angle_fired, owner_id):
        BallProjectile(pos, self.ball_frames, (self.all_sprites, self.ball_sprites), PLAYER_THROW_SPEED, angle_fired, owner_id, self.particle_frames, self.all_sprites)

    def create_acorn(self, pos, angle_fired, owner_id):
        AcornProjectile(pos, self.acorn_frames, (self.all_sprites, self.damage_sprites, self.acorn_sprites), SQ_PROJECTILE_SPEED, angle_fired, owner_id, self.particle_frames, self.all_sprites)

    def check_projectile_owner(self, sprite, group_sprite):
        """
        Ignore the collision between the projectile and the owner to resolve the case when the collision happens right after creation since the initial position is within collision detection rect.
        With attr "id" the projectile can still collide with other sprites of the same class object.
        Also check if the 'sprite' and 'group_sprite' is not the same sprite since I am checking sprites with sprites in its own group
        """
        if sprite.rect.colliderect(group_sprite):
            # true = collided and can be included in list
            if (hasattr(sprite, "id") and hasattr(group_sprite, "owner_id")):
                if (sprite.get_id() == group_sprite.get_owner_id()):
                    # projectile hit its owner
                    #print(getattr(sprite, "id"))
                    #print(getattr(group_sprite, "owner_id"))
                    return False
            elif (sprite == group_sprite):
                # projectile collided with itself.
                return False
            return True
        else: 
            return False

    # handle item, damage, end level collisions here
    def projectile_collision(self):
        """
        collision should remove the projectile from game, excluding collision with the owner of the projectile
        projectiles hitting eachother should also remove from game
        """
        projectile_sprite_groups = [self.acorn_sprites, self.ball_sprites]
        sprites = self.collision_sprites.sprites() + self.ramp_collision_sprites.sprites() + self.acorn_sprites.sprites() + self.ball_sprites.sprites()
        for sprite in sprites:
            #pygame.sprite.spritecollide(sprite, self.acorn_sprites, True, pygame.sprite.collide_mask)  # need to use mask if image surface is larger than the actual image
            for projectile_grp in projectile_sprite_groups:
                collided_list = pygame.sprite.spritecollide(sprite, projectile_grp, True, collided=self.check_projectile_owner) 
                if (collided_list):
                    for collided_sprite in collided_list:
                        ParticleEffectSprite(
                            pos = collided_sprite.rect.center, 
                            frames = self.particle_frames, 
                            groups = self.all_sprites
                        )

                        if (hasattr(collided_sprite, "owner_id") and hasattr(sprite, "enemy")):
                            if (collided_sprite.get_owner_id() == self.player.get_id()):
                                # if the owner of the projectile is the player, then it can damage the enemy
                                sprite.evaluate_damage(collided_sprite.get_damage(), collided_sprite.get_type())

    # def acorn_collision(self):
    #     # collision with terrain should remove the acorn from game
    #     sprites = [spr for spr in self.collision_sprites.sprites() if spr.type != "squirrel"] + self.ramp_collision_sprites.sprites()
    #     for sprite in sprites:
    #         sprite_list = pygame.sprite.spritecollide(sprite, self.acorn_sprites, True, pygame.sprite.collide_mask)
    #         if (sprite):
    #             for collided_sprite in sprite_list:
    #                 ParticleEffectSprite(
    #                     pos = collided_sprite.rect.center, 
    #                     frames = self.particle_frames, 
    #                     groups = self.all_sprites
    #                 )

    def hit_collision(self):
        """
        If player collides with sprites that will do damage to the player
        """
        # better performance to check rect first and then mask, rather than always checking the mask
        if (pygame.sprite.spritecollide(self.player_sprite.sprite, self.damage_sprites, False)):
            #print('collide with rect')
            hit_sprites = pygame.sprite.spritecollide(self.player_sprite.sprite, self.damage_sprites, False, pygame.sprite.collide_mask)

            if(hit_sprites):
                for sprite in hit_sprites:
                    # later will need to check if enemy weapon is also active to inflict damage
                    #print('hit with mask')
                    if (sprite.type == ENEMY_ACORN_PROJECTILE):
                        sprite.kill()
                        ParticleEffectSprite(
                            pos = sprite.rect.center, 
                            frames = self.particle_frames, 
                            groups = self.all_sprites
                        )
                    
                        if (hasattr(sprite, "owner_id")):
                            if (sprite.get_owner_id() != self.player.get_id()):
                                # if the owner of the projectile is NOT the player, then damage
                                # todo
                                pass
                    else:
                        # other damage sprite
                        pass
                            
                    

                    

        # if performance is not impacted negatively enough to notice, then it would be less verbose
        """
        if (pygame.sprite.spritecollide(self.player_sprite, self.damage_sprites, True, pygame.sprite.collide_mask)):
            do something
        """

    def item_collision(self):
        """
        player collide with items
        """
        if (self.item_sprites):
            if (pygame.sprite.spritecollide(self.player_sprite.sprite, self.item_sprites, False)):
                items_collected = pygame.sprite.spritecollide(self.player_sprite.sprite, self.item_sprites, True, pygame.sprite.collide_mask)
                if (items_collected):
                    print(items_collected)
                    for sprite in items_collected:
                        print(sprite.item_type)
                        ParticleEffectSprite(
                            pos = sprite.rect.center, 
                            frames = self.particle_frames, 
                            groups = self.all_sprites
                        )

    def attack_collision(self):
        """
        player attack interaction with enemy entities
        """
        target_sprite_grps = [self.acorn_sprites, self.enemy_sprites]
        player_current_weapon = self.player.get_current_weapon()
        if (target_sprite_grps and player_current_weapon.get_can_damage()):
            for grp in target_sprite_grps:
                if (pygame.sprite.spritecollide(player_current_weapon, grp, False)):
                    targets_hit = pygame.sprite.spritecollide(player_current_weapon, grp, False, pygame.sprite.collide_mask)
                    if (targets_hit):
                        for hit in targets_hit:
                            if (hit.type in [ENEMY_DOG, ENEMY_BIRD, ENEMY_SQUIRREL]):
                                # damage to enemey
                                # since there can be multiple collisions within one attack, within enemy sprites have internal timer for cooldown to receive damage so only one instance of damage
                                hit.evaluate_damage(player_current_weapon.get_damage(), player_current_weapon.type)
                            elif (hit.type in [ENEMY_ACORN_PROJECTILE]):
                                # reflect projectile
                                hit.reverse(PLAYER_THROW_SPEED, player_current_weapon.angle)
                                # change owner
                                hit.set_owner_id(self.player.get_id())
                            else:
                                print(f"User error, missing type in attack_collision: {hit.type}")

    def run(self, dt, event_list):
        # game loop here for level. like checking collisions and updating screen
        self.display_surface.fill("black")

        # update sprites
        self.all_sprites.update(dt, event_list)
        self.projectile_collision()
        self.hit_collision()
        self.item_collision()
        self.attack_collision()
        
        # draw all sprites
        self.all_sprites.draw(self.display_surface)
        #self.all_sprites.draw(self.player.hitbox_rect.center, self.player.hitbox_rect.width, self.tmx_map_max_width)