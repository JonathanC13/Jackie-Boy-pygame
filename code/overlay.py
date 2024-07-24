from settings import *

class Button:
    def __init__(self, name, surface, pos, size, clickable = False, func = None, params = None):
        self.name = name
        self.surface = surface
        self.pos = pos
        self.size = size
        self.clickable = clickable
        self.func = func
        self.params = params

    def click(self):
        if self.clickable and self.func is not None:
            if self.params:
                self.func(*self.params)
            else:
                self.func()

class Overlay:
    def __init__(self, overlay, font_title, font, overlay_frames):
        self._overlay = overlay
        self.font_title = font_title
        self.font = font
        self.overlay_frames = overlay_frames

        self.display_surface = pygame.display.get_surface()

        self.title_surfaces = []
        self.content_surfaces = []
        self.right_col_1_surfaces = []

        self.start_idx = 0

        self.buttons = []

    @property
    def overlay(self):
        return self._overlay
    
    @overlay.setter
    def overlay(self, overlay):
        self._overlay = overlay

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
                    outline_surface.set_at((x, y), '#28282B')

        for dir in direction:
            self.display_surface.blit(outline_surface, (pos[0] + dir[0], pos[1] + dir[1]))

    def check_button_clicked(self, pos):
        if self.buttons:
            for button in self.buttons:
                if (pos[0] >= button.pos[0] and pos[0] <= button.pos[0] + button.size[0] and pos[1] >= button.pos[1] and pos[1] <= button.pos[1] + button.size[1]):
                    #print(f'clicked: {button.name}')
                    button.click()

    def display_overlay(self, container_size, col_x, current_total_spacing_y, between_spacing_y):
        self.buttons = []
        # title
        x = col_x
        y = current_total_spacing_y
        if (self.title_surfaces):
            for i in range(len(self.title_surfaces)):
                self.title_surfaces[i].sort(key = lambda s: s['layer'])
                if (y + self.title_surfaces[i][0]['surf'].get_height() + self.title_surfaces[i][0]['offset'].y > WINDOW_HEIGHT):
                    break
                else:
                    y_add = 0
                    for surf in self.title_surfaces[i]:
                        pos_x = x + surf['offset'].x
                        pos_y = y + surf['offset'].y
                        self.display_surface.blit(surf['surf'], (pos_x, pos_y))
                        if (surf['layer'] == 0):
                            y_add = surf['surf'].get_height()

                            # currently only the containers will be the "button". Don't need each surface within a container to be a button obj
                            self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))

                    y += y_add + between_spacing_y

        # content
        content_y = y
        if (self.content_surfaces):
            for i in range(self.start_idx, len(self.content_surfaces)):
                self.content_surfaces[i].sort(key = lambda s: s['layer'])
                if (y + self.content_surfaces[i][0]['surf'].get_height() + self.content_surfaces[i][0]['offset'].y > WINDOW_HEIGHT):
                    break
                else:
                    y_add = 0
                    for surf in self.content_surfaces[i]:
                        pos_x = x + surf['offset'].x
                        pos_y = y + surf['offset'].y
                        self.display_surface.blit(surf['surf'], (pos_x, pos_y))
                        if (surf['layer'] == 0):
                            y_add = surf['surf'].get_height()
                            self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))
                    y += y_add + between_spacing_y

        y = content_y
        if (self.right_col_1_surfaces):
            for i in range(len(self.right_col_1_surfaces)):
                self.right_col_1_surfaces[i].sort(key = lambda s: s['layer'])
                if (y + self.right_col_1_surfaces[i][0]['surf'].get_height() + self.right_col_1_surfaces[i][0]['offset'].y > WINDOW_HEIGHT):
                    break
                else:
                    y_add = 0
                    for surf in self.right_col_1_surfaces[i]:
                        pos_x = x + surf['offset'].x
                        pos_y = y + surf['offset'].y
                        # print('====')
                        # print(pos_x, pos_x, surf['name'])
                        self.display_surface.blit(surf['surf'], (pos_x, pos_y))
                        if (surf['layer'] == 0):
                            y_add = surf['surf'].get_height()
                            self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))
                    y += y_add + between_spacing_y

class SavesOverlay(Overlay):
    def __init__(self, font_title, font, save_data, overlay_frames, func_load_save_file):
        
        self._save_data = save_data
        self.func_load_save_file = func_load_save_file

        super().__init__(SAVES, font_title, font, overlay_frames)

        self.current_total_spacing_y = 0
        self.between_spacing_x, self.between_spacing_y = 25, 25
        
        self.container_size = vector(275, 150)

        self.populate_title_surfaces()

    @property
    def save_data(self):
        return self._save_data
    
    @save_data.setter
    def save_data(self, save_data):
        self._save_data = save_data
        # reload surfaces
        self.populate_content_surfaces()

    def populate_content_surfaces(self):
        self.content_surfaces = []

        if (self.save_data):
            for save in self.save_data:
                self.create_container_save_data(save)

            self.populate_right_col_1()
        else:
            print("display [No save data]")

    def populate_title_surfaces(self):
        self.title_surfaces = []
        container = []
        # 'Saves' subtitle
        save_title_surf = self.font.render('Saves', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "subtitle_text", "surf": save_title_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})

        save_title_container_surf = pygame.Surface((self.container_size.x, save_title_surf.get_height() + 20))
        save_title_container_surf.set_alpha(55)
        save_title_container_surf.fill('#28282B')
        container.append({"name": "subtitle_container", "surf": save_title_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None})

        self.title_surfaces.append(container)

    def populate_right_col_1(self):
        self.right_col_1_surfaces = []
        container = []

        x = self.container_size.x + self.between_spacing_x

        # up
        up_surf = self.font.render('UP', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "UP", "surf": up_surf, "layer": 1, "offset": vector(x + 10, 10), "clickable": False, "func": None, "params": None})
        up_surf.set_alpha(0)

        up_container_surf = pygame.Surface((up_surf.get_width() + 20, up_surf.get_height() + 20))
        up_container_surf.set_alpha(0)
        up_container_surf.fill('#28282B')
        clickable = False
        if (self.start_idx > 0):
            clickable = True
            up_surf.set_alpha(255)
            up_container_surf.set_alpha(55)

        container.append({"name": "UP", "surf": up_container_surf, "layer": 0, "offset": vector(x, 0), "clickable": clickable, "func": self.change_start_idx, "params": [-1]})
        self.right_col_1_surfaces.append(container)
        container = []

        # down
        down_surf = self.font.render('DOWN', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "DOWN", "surf": down_surf, "layer": 1, "offset": vector(x + 10, 10), "clickable": False, "func": None, "params": None})
        down_surf.set_alpha(0)

        down_container_surf = pygame.Surface((down_surf.get_width() + 20, down_surf.get_height() + 20))
        down_container_surf.set_alpha(0)
        down_container_surf.fill('#28282B')
        clickable = False
        if (self.start_idx < len(self.content_surfaces) - 1):   # -1 so that at least one save is in the column
            clickable = True
            down_surf.set_alpha(255)
            down_container_surf.set_alpha(55)
        container.append({"name": "DOWN", "surf": down_container_surf, "layer": 0, "offset": vector(x, 0), "clickable": True, "func": self.change_start_idx, "params": [1]})
        self.right_col_1_surfaces.append(container)

    def change_start_idx(self, change):
        self.start_idx = max(min(self.start_idx + change, len(self.content_surfaces) - 1), 0)  # -1 so that at least one save is in the column
        self.populate_right_col_1()

    def save_file_chosen(self, name):
        self.func_load_save_file(name)

    def create_container_save_data(self, save):
        container = []
        filename = save['filename'][:14]
        if (len(save['filename']) >= 14):
            filename += '...'
        save_data = save['data']

        # container
        container_surf = pygame.Surface((self.container_size.x, self.container_size.y))
        container_surf.set_alpha(55)
        container_surf.fill('#28282B')
        container.append({"name": str(save['filename']), "surf": container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.save_file_chosen, "params": [str(save['filename'])]})
        
        # file name
        filename_surf = self.font.render('Filename: ' + filename, False, "white", bgcolor=None, wraplength=0)
        container.append({"name": str(save['filename']), "surf": filename_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})

        # items
        x_offset = 10
        x_spacing = 10
        y_spacing = 15
        # hearts
        heart_surf = self.overlay_frames['heart'][0]
        container.append({"name": "heart", "surf": heart_surf, "layer": 1, "offset": vector(x_offset, filename_surf.get_height() + y_spacing), "clickable": False, "func": None, "params": None})
        x_offset += heart_surf.get_width() + x_spacing
        heart_num_surf = self.font.render('x ' + str(save_data['player_health']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "heart", "surf": heart_num_surf, "layer": 1, "offset": vector(x_offset + x_spacing, filename_surf.get_height() + y_spacing), "clickable": False, "func": None, "params": None})
        x_offset += heart_num_surf.get_width() + x_spacing*2

        # denta
        denta_surf = self.overlay_frames['denta'][0]
        container.append({"name": "denta", "surf": denta_surf, "layer": 1, "offset": vector(x_offset, filename_surf.get_height() + y_spacing), "clickable": False, "func": None, "params": None})
        x_offset += denta_surf.get_width() + x_spacing
        denta_num_surf = self.font.render('x ' + str(save_data['denta']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "denta", "surf": denta_num_surf, "layer": 1, "offset": vector(x_offset, filename_surf.get_height() + y_spacing), "clickable": False, "func": None, "params": None})
        x_offset += denta_num_surf.get_width() + x_spacing*2

        # kibble
        kibble_surf = self.overlay_frames['kibble'][0]
        container.append({"name": "kibble", "surf": kibble_surf, "layer": 1, "offset": vector(x_offset, filename_surf.get_height() + y_spacing), "clickable": False, "func": None, "params": None})
        x_offset += kibble_surf.get_width() + x_spacing
        kibble_num_surf = self.font.render('x ' + str(save_data['kibble']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "kibble", "surf": kibble_num_surf, "layer": 1, "offset": vector(x_offset, filename_surf.get_height() + y_spacing), "clickable": False, "func": None, "params": None})

        # weapons
        x_offset = 0

        self.content_surfaces.append(container)

    def draw_test(self):
        for button in self.buttons:
            pygame.draw.rect(self.display_surface, "red", (button.pos, button.size))

    def update(self):
        # title 
        self.current_total_spacing_y = self.between_spacing_y
        title_surf = self.font_title.render(GAME_TITLE, False, "white", bgcolor=None, wraplength=0)
        topleft = vector(WINDOW_WIDTH/2 - title_surf.get_width()/2, self.current_total_spacing_y)
        self.outline_surface(title_surf, topleft)
        self.display_surface.blit(title_surf, topleft)
        self.current_total_spacing_y += title_surf.get_height() + self.between_spacing_y

        self.display_overlay(self.container_size, WINDOW_WIDTH/2 - self.container_size.x/2, self.current_total_spacing_y, self.between_spacing_y)
    
        #self.draw_test()