from settings import *
from saves import Saves

class MainMenuControl:
    def __init__(self, font_title, font, overlay_frames, func_new_save_file, func_load_save_file, func_quit):

        self.font_title = font_title
        self.font = font
        self.overlay_frames = overlay_frames

        # callback triggers to main
        self.func_new_save_file = func_new_save_file
        self.func_load_save_file = func_load_save_file
        self.func_quit = func_quit

        self.saves = None
        self.reload_saves()

        self.main_menu_list = []
        self.setup_menus()
        self.current_menu = self.find_menu(MAIN)

    def reload_saves(self):
        self.saves = Saves()
        self.saves.load_saves()
    
    def setup_menus(self):

        self.main_menu_list.append({'menu_name': MAIN, 'obj': MainMenuOverlay(self.font_title, self.font, self.overlay_frames, True if (self.saves.get_all_saves) else False, self.goto_save_menu, self.func_new_save_file, self.goto_control_help, self.func_quit)})
        
        self.main_menu_list.append({'menu_name': SAVES, 'obj': SavesOverlay(self.font_title, self.font, self.saves.get_all_saves, self.overlay_frames, self.func_load_save_file, self.go_back)})

        #self.main_menu_list.append({'menu_name': CONTROL_HELP, 'obj': SavesOverlay(self.font_title, self.font, self.overlay_frames, True if (self.saves.get_all_saves) else False, self.goto_save_menu, self.func_new_save_file, self.goto_control_help, self.func_quit, self.go_back)})

    def find_menu(self, name):
        for menu in self.main_menu_list:
            if (menu['menu_name'] == name):
                return menu['obj']
            
        # else
        print("Menu does not exist")

    def goto_save_menu(self):
        self.saves.load_saves()
        self.current_menu = self.find_menu(SAVES)
        self.current_menu.save_data = self.saves.get_all_saves()

    def goto_control_help(self):
        print("how to play")
        #self.current_menu = self.find_menu(CONTROL_HELP)

    def go_back(self):
        dest = MAIN
        if self.current_menu == SAVES:
            dest = MAIN
        elif self.current_menu == CONTROL_HELP:
            dest = MAIN
        else:
            dest = MAIN
        
        self.current_menu = self.find_menu(dest)

    def get_current_menu(self):
        return self.current_menu


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

        self.subtitle_surfaces = []
        self.content_surfaces = []
        self.content_surface_right_1 = []
        self.content_surface_left_1 = []

        self.start_idx = 0
        
        self.container_size = vector(275, 150)
        self.current_total_spacing_y = 0
        self.between_spacing_x, self.between_spacing_y = 25, 25

        self.content_col_x = {
                'left_1': WINDOW_WIDTH/2 - self.container_size.x/2 - self.between_spacing_x - self.container_size.x,
                'center': WINDOW_WIDTH/2 - self.container_size.x/2,
                'right_1': WINDOW_WIDTH/2 + self.container_size.x + self.between_spacing_x
            }

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

    def display_title(self):
        # title 
        self.current_total_spacing_y = self.between_spacing_y
        title_surf = self.font_title.render(GAME_TITLE, False, "white", bgcolor=None, wraplength=0)
        topleft = vector(WINDOW_WIDTH/2 - title_surf.get_width()/2, self.current_total_spacing_y)
        self.outline_surface(title_surf, topleft)
        self.display_surface.blit(title_surf, topleft)
        self.current_total_spacing_y += title_surf.get_height() + self.between_spacing_y

    def display_overlay(self, container_size, current_total_spacing_y, between_spacing_y):
        self.buttons = []
        # title
        x = self.content_col_x['center']
        y = current_total_spacing_y
        if (self.subtitle_surfaces):
            for i in range(len(self.subtitle_surfaces)):
                self.subtitle_surfaces[i].sort(key = lambda s: s['layer'])
                if (y + self.subtitle_surfaces[i][0]['surf'].get_height() + self.subtitle_surfaces[i][0]['offset'].y > WINDOW_HEIGHT):
                    break
                else:
                    y_add = 0
                    for surf in self.subtitle_surfaces[i]:
                        pos_x = x + surf['offset'].x
                        pos_y = y + surf['offset'].y
                        self.display_surface.blit(surf['surf'], (pos_x, pos_y))
                        if (surf['layer'] == 0):
                            y_add = surf['surf'].get_height()

                            # currently only the containers will be the "button". Don't need each surface within a container to be a button obj
                            self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))

                    y += y_add + between_spacing_y


        content_lists = [[self.content_surfaces, self.content_col_x['center'], self.start_idx], [self.content_surface_right_1, self.content_col_x['right_1'], 0], [self.content_surface_left_1, self.content_col_x['left_1'], 0]]
        content_y = y # starting y of the content
        for surf_list, content_x, content_idx in content_lists:
            if (list):
                start_idx = content_idx
                x = content_x
                y = content_y   # reset to top of content section
                for i in range(start_idx, len(surf_list)):
                    surf_list[i].sort(key = lambda s: s['layer'])
                    if (y + surf_list[i][0]['surf'].get_height() + surf_list[i][0]['offset'].y > WINDOW_HEIGHT):
                        break
                    else:
                        y_add = 0
                        for surf in surf_list[i]:
                            pos_x = x + surf['offset'].x
                            pos_y = y + surf['offset'].y
                            self.display_surface.blit(surf['surf'], (pos_x, pos_y))
                            if (surf['layer'] == 0):
                                y_add = surf['surf'].get_height()
                                self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))
                        y += y_add + between_spacing_y

        
        # content
        # center column
        # content_y = y
        # if (self.content_surfaces):
        #     for i in range(self.start_idx, len(self.content_surfaces)):
        #         self.content_surfaces[i].sort(key = lambda s: s['layer'])
        #         if (y + self.content_surfaces[i][0]['surf'].get_height() + self.content_surfaces[i][0]['offset'].y > WINDOW_HEIGHT):
        #             break
        #         else:
        #             y_add = 0
        #             for surf in self.content_surfaces[i]:
        #                 pos_x = x + surf['offset'].x
        #                 pos_y = y + surf['offset'].y
        #                 self.display_surface.blit(surf['surf'], (pos_x, pos_y))
        #                 if (surf['layer'] == 0):
        #                     y_add = surf['surf'].get_height()
        #                     self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))
        #             y += y_add + between_spacing_y

        # right column 1
        # x = self.content_col_x['right_1']
        # y = content_y
        # if (self.content_surface_right_1):
        #     for i in range(len(self.content_surface_right_1)):
        #         self.content_surface_right_1[i].sort(key = lambda s: s['layer'])
        #         if (y + self.content_surface_right_1[i][0]['surf'].get_height() + self.content_surface_right_1[i][0]['offset'].y > WINDOW_HEIGHT):
        #             break
        #         else:
        #             y_add = 0
        #             for surf in self.content_surface_right_1[i]:
        #                 pos_x = x + surf['offset'].x
        #                 pos_y = y + surf['offset'].y
        #                 # print('====')
        #                 # print(pos_x, pos_x, surf['name'])
        #                 self.display_surface.blit(surf['surf'], (pos_x, pos_y))
        #                 if (surf['layer'] == 0):
        #                     y_add = surf['surf'].get_height()
        #                     self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))
        #             y += y_add + between_spacing_y

        # # left column 1
        # x = self.content_col_x['left_1']
        # y = content_y
        # if (self.content_surface_left_1):
        #     for i in range(len(self.content_surface_left_1)):
        #         self.content_surface_left_1[i].sort(key = lambda s: s['layer'])
        #         if (y + self.content_surface_left_1[i][0]['surf'].get_height() + self.content_surface_left_1[i][0]['offset'].y > WINDOW_HEIGHT):
        #             break
        #         else:
        #             y_add = 0
        #             for surf in self.content_surface_left_1[i]:
        #                 pos_x = x + surf['offset'].x
        #                 pos_y = y + surf['offset'].y
        #                 # print('====')
        #                 # print(pos_x, pos_x, surf['name'])
        #                 self.display_surface.blit(surf['surf'], (pos_x, pos_y))
        #                 if (surf['layer'] == 0):
        #                     y_add = surf['surf'].get_height()
        #                     self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))
        #             y += y_add + between_spacing_y

class MainMenuOverlay(Overlay):
    def __init__(self, font_title, font, overlay_frames, have_save_data, func_save_menu, func_new_game, func_control_help, func_quit):
        super().__init__(MAIN, font_title, font, overlay_frames)

        self.have_save_data = have_save_data

        self.func_save_menu = func_save_menu
        self.func_new_game = func_new_game
        self.func_control_help = func_control_help
        self.func_quit = func_quit

        test_text = self.font.render('hello, world!', False, "white", bgcolor=None, wraplength=0)
        self.container_size = vector(275, test_text.get_height() + 20)

        self.content_col_x.update({'center': WINDOW_WIDTH/2 - self.container_size.x/2})
        self.content_col_x.update({'right_1': self.content_col_x['center'] + self.container_size.x + self.between_spacing_x})

        self.populate_content_surfaces()
        #self.populate_content_surface_right_1()

    def create_content_surface(self, text, func):
        container = []
        # container
        container_surf = pygame.Surface((self.container_size.x, self.container_size.y))
        container_surf.set_alpha(55)
        container_surf.fill('#28282B')
        container.append({'name': text, "surf": container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": func, "params": None})  
        # text
        text_surf = self.font.render(text, False, "white", bgcolor=None, wraplength=0)
        container.append({"name": text, "surf": text_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})
        return container

    def populate_content_surfaces(self):
        self.content_surfaces = []

        if (self.have_save_data):
            container = self.create_content_surface('Save files', self.func_save_menu)
            self.content_surfaces.append(container)

        container = self.create_content_surface('New game', self.func_new_game)
        self.content_surfaces.append(container)

        container = self.create_content_surface('How to play', self.func_control_help)
        self.content_surfaces.append(container)

        container = self.create_content_surface('Quit', self.func_quit)
        self.content_surfaces.append(container)

    def populate_content_surface_right_1(self):
        container = self.create_content_surface('hello, world!', None)
        self.content_surface_right_1.append(container)

    def update(self):
        self.display_title()
        self.display_overlay(self.container_size, self.current_total_spacing_y, self.between_spacing_y)

class SavesOverlay(Overlay):
    def __init__(self, font_title, font, save_data, overlay_frames, func_load_save_file, func_go_back):
        
        self._save_data = save_data
        self.func_load_save_file = func_load_save_file
        self.func_go_back = func_go_back

        super().__init__(SAVES, font_title, font, overlay_frames)
        
        self.container_size = vector(275, 150)

        self.content_col_x.update({'center': WINDOW_WIDTH/2 - self.container_size.x/2})
        self.content_col_x.update({'right_1': self.content_col_x['center'] + self.container_size.x + self.between_spacing_x})

        self.populate_subtitle_surfaces()

    @property
    def save_data(self):
        return self._save_data
    
    @save_data.setter
    def save_data(self, save_data):
        self.start_idx = 0
        self._save_data = save_data
        # reload surfaces
        self.populate_content_surfaces()

    def populate_content_surfaces(self):
        self.content_surfaces = []

        if (self.save_data):
            for save in self.save_data:
                self.create_container_save_data(save)

            self.populate_right_col_1()
            self.populate_left_col_1()
        else:
            print("display [No save data]")

    def populate_subtitle_surfaces(self):
        self.subtitle_surfaces = []
        container = []
        # 'Saves' subtitle
        save_title_surf = self.font.render('Saves', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "subtitle_text", "surf": save_title_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})

        save_title_container_surf = pygame.Surface((self.container_size.x, save_title_surf.get_height() + 20))
        save_title_container_surf.set_alpha(55)
        save_title_container_surf.fill('#28282B')
        container.append({"name": "subtitle_container", "surf": save_title_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None})

        self.subtitle_surfaces.append(container)

    def populate_right_col_1(self):
        self.content_surface_right_1 = []
        container = []

        # up
        up_surf = self.font.render('UP', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "UP", "surf": up_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})
        up_surf.set_alpha(0)

        up_container_surf = pygame.Surface((up_surf.get_width() + 20, up_surf.get_height() + 20))
        up_container_surf.set_alpha(0)
        up_container_surf.fill('#28282B')
        clickable = False
        if (self.start_idx > 0):
            clickable = True
            up_surf.set_alpha(255)
            up_container_surf.set_alpha(55)

        container.append({"name": "UP", "surf": up_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": clickable, "func": self.change_start_idx, "params": [-1]})
        self.content_surface_right_1.append(container)
        container = []

        # down
        down_surf = self.font.render('DOWN', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "DOWN", "surf": down_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})
        down_surf.set_alpha(0)

        down_container_surf = pygame.Surface((down_surf.get_width() + 20, down_surf.get_height() + 20))
        down_container_surf.set_alpha(0)
        down_container_surf.fill('#28282B')
        clickable = False
        if (self.start_idx < len(self.content_surfaces) - 1):   # -1 so that at least one save is in the column
            clickable = True
            down_surf.set_alpha(255)
            down_container_surf.set_alpha(55)
        container.append({"name": "DOWN", "surf": down_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.change_start_idx, "params": [1]})
        self.content_surface_right_1.append(container)

    def populate_left_col_1(self):
        self.content_surface_left_1 = []
        container = []
        # back
        back_surf = self.font.render('BACK', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "BACK", "surf": back_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})

        back_container_surf = pygame.Surface((back_surf.get_width() + 20, back_surf.get_height() + 20))
        back_container_surf.fill('#28282B')
        back_container_surf.set_alpha(55)

        container.append({"name": "UP", "surf": back_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.func_go_back, "params": None})
        self.content_surface_left_1.append(container)
        container = []
        
        self.content_col_x.update({'left_1': self.content_col_x['center'] - self.between_spacing_x - back_container_surf.get_width()})

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
        self.display_title()

        self.display_overlay(self.container_size, self.current_total_spacing_y, self.between_spacing_y)
    
        #self.draw_test()