from settings import *
from sprites import AnimatedSprite
from groups import AllSprites
from random import randint

class UI:
    def __init__(self, font, frames):
        self.display_surface = pygame.display.get_surface()
        self.heart_sprites = pygame.sprite.Group()
        self.static_sprites = pygame.sprite.Group()
        self.font = font
        self.frames = frames

        self.inventory_x = 20

        # health
        self.heart_frames = frames["heart"]
        self.heart_surface_height = self.heart_frames[0].height
        self.heart_surface_width = self.heart_frames[0].width
        self.heart_padding = 10
        self.heart_y = 20
        self.heart_amount_surf = None
        self.max_shown = 3

        # denta
        self.denta_frames = frames["denta"]
        self.denta_surface_height = self.denta_frames[0].height
        self.denta_y = self.heart_y + self.heart_surface_height + 20
        self.denta_amount_surf = None

        # kibble
        self.kibble_frames = frames["kibble"]
        self.kibble_surface_height = self.kibble_frames[0].height
        self.kibble_y = self.denta_y + self.denta_surface_height + 20
        self.kibble_amount_surf = None

        # weapons.
        self._weapon_list = []
        self.weapon_bg_size = (60, 60)
        self._current_weapon_index = 0

        self._game_state = MAIN_MENU

        self.create_static_sprites()

    @property
    def current_weapon_index(self):
        return self._current_weapon_index
    
    @current_weapon_index.setter
    def current_weapon_index(self, current_weapon_index):
        self._current_weapon_index = current_weapon_index

    @property
    def game_state(self):
        return self._game_state
    
    @game_state.setter
    def game_state(self, _game_state):
        self._game_state = _game_state

    @property
    def weapon_list(self):
        return self._weapon_list
    
    @weapon_list.setter
    def weapon_list(self, weapon_list):
        self._weapon_list = weapon_list

    def display_weapons(self):
        # get weapon info and get total width for all weapons in ui
        weapon_ui = [{'weapon_name': '', 'damage_colour': 'grey', 'pos': vector(WINDOW_WIDTH/2, 20)} for _ in range(len(self.weapon_list))]
        all_weapon_width = 0
        for i in range(len(self.weapon_list)):
            weapon_name = self.weapon_list[i]['weapon'].weapon_name
            damage_colour = self.weapon_list[i]['weapon'].damage_colour
            #weapon_surf_width = self.frames['weapons'][weapon_name].get_width()
            weapon_surf_width = self.weapon_bg_size[0]

            weapon_ui[i]['weapon_name'] = weapon_name
            weapon_ui[i]['damage_colour'] = damage_colour

            weapon_ui[i]['pos'].x += all_weapon_width
            all_weapon_width += weapon_surf_width
        
        # adjust to center the weapon ui while bliting
        offset_to_center = all_weapon_width / 2
        for i in range(len(weapon_ui)):
            weapon_surf = self.frames['weapons'][weapon_ui[i]['weapon_name']]
            # bg
            weapon_bg = pygame.Surface(self.weapon_bg_size)
            weapon_bg.fill(weapon_ui[i]['damage_colour'])
            if (i == self._current_weapon_index):
                weapon_bg.set_alpha(255)
            else:
                weapon_bg.set_alpha(50)
            self.display_surface.blit(weapon_bg, (weapon_ui[i]['pos'].x - offset_to_center, weapon_ui[i]['pos'].y))

            # weapon image. center within container
            self.display_surface.blit(weapon_surf, (weapon_ui[i]['pos'].x - offset_to_center + self.weapon_bg_size[0]/2 - weapon_surf.get_width()/2, weapon_ui[i]['pos'].y + self.weapon_bg_size[1]/2 - weapon_surf.get_height()/2))

            # weapon key
            key_num_surf = self.font.render(str(i + 1), False, "white", bgcolor=None, wraplength=0)
            self.display_surface.blit(key_num_surf, (weapon_ui[i]['pos'].x - offset_to_center, weapon_ui[i]['pos'].y))


    def create_hearts(self, amount):
        hearts = 0
        if (amount <= self.max_shown):
            self.heart_amount_surf = None
            hearts = amount
        else:
            self.heart_amount_surf = self.font.render('+ ' + str(amount - self.max_shown), False, "white", bgcolor=None, wraplength=0)
            hearts = self.max_shown

        for sprite in self.heart_sprites:
            sprite.kill()
        for heart in range(hearts):
            x = self.inventory_x + (heart * (self.heart_surface_width + self.heart_padding))
            y = self.heart_y
            Heart((x, y), self.heart_frames, self.heart_sprites) 

    def create_static_sprites(self):
        AnimatedSprite((self.inventory_x, self.denta_y), self.denta_frames, self.static_sprites, "denta")
        AnimatedSprite((self.inventory_x, self.kibble_y), self.kibble_frames, self.static_sprites, "kibble")

    def outline_surface(self, surface, pos):
        """
        
        """
        offset = 1
        direction = [[0,  -offset], [offset,  -offset], [offset,  0], [offset,  offset], [0,  offset], [-offset,  offset], [-offset,  0], [-offset,  -offset]]

        text_mask = pygame.mask.from_surface(surface)
        outline_surface = text_mask.to_surface()
        outline_surface.set_colorkey('black')

        surf_w, surf_h = outline_surface.get_size()
        for x in range(surf_w):
            for y in range(surf_h):
                if outline_surface.get_at((x, y))[0] != 0:
                    outline_surface.set_at((x, y), 'grey')

        for dir in direction:
            self.display_surface.blit(outline_surface, (pos[0] + dir[0], pos[1] + dir[1]))

    def create_denta_count_surf(self, amount):
        self.denta_amount_surf = self.font.render('x ' + str(amount), False, "white", bgcolor=None, wraplength=0)

    def create_kibble_count_surf(self, amount):
        self.kibble_amount_surf = self.font.render('x ' + str(amount), False, "white", bgcolor=None, wraplength=0)

    def update(self, dt, event_list = None):
        if (self.game_state != MAIN_MENU):
            self.heart_sprites.update(dt, event_list)
            self.static_sprites.update(dt, event_list)
            
            self.heart_sprites.draw(self.display_surface)
            self.static_sprites.draw(self.display_surface)

            if (self.heart_amount_surf is not None):
                x = 100
                y = self.heart_y + self.heart_surface_height - self.heart_amount_surf.get_size()[1]
                self.outline_surface(self.heart_amount_surf, (x, y))
                self.display_surface.blit(self.heart_amount_surf, (x, y))

            x = self.inventory_x + 35
            if (self.denta_amount_surf is not None):
                y = self.denta_y + self.denta_surface_height - self.denta_amount_surf.get_size()[1]
                self.outline_surface(self.denta_amount_surf, (x, y))
                self.display_surface.blit(self.denta_amount_surf, (x, y))
                #re = self.denta_amount_surf.get_frect(topleft = (x, y))
                #pygame.draw.rect(self.display_surface, "green", re)
            if (self.kibble_amount_surf is not None):
                y = self.kibble_y + self.kibble_surface_height - self.kibble_amount_surf.get_size()[1]
                self.outline_surface(self.kibble_amount_surf, (x, y))
                self.display_surface.blit(self.kibble_amount_surf, (x, y))

            if (self.weapon_list):
                self.display_weapons()

class Heart(AnimatedSprite):
    def __init__(self, pos, frames, groups):
        super().__init__(pos, frames, groups)
        self.active = False

    def animate(self, dt):
        self.frame_index += self.animation_speed * dt/FPS_TARGET
        if (self.frame_index >= self.len_frames):
            self.frame_index = 0
            self.active = False
        self.image = self.frames[int(self.frame_index)]
    
    def update(self, dt, event_list = None):
        if self.active:
            self.animate(dt)
        else:
            if (randint(0, 100) == 1):
                self.active = True