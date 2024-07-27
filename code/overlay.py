from settings import *
from saves import Saves

class MainMenuControl:
    def __init__(self, font_title, font, overlay_frames, func_new_save_file, func_load_save_file, func_quit, level_names):

        self.font_title = font_title
        self.font = font
        self.overlay_frames = overlay_frames
        self.level_names = level_names

        # callback triggers to main
        self.func_new_save_file = func_new_save_file
        self.func_load_save_file = func_load_save_file  # todo, in level selector overlay callback to this
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
        
        self.main_menu_list.append({'menu_name': SAVES, 'obj': SavesOverlay(self.font_title, self.font, self.saves.get_all_saves, self.overlay_frames, self.goto_level_selector, self.go_back)})

        self.main_menu_list.append({'menu_name': LEVEL_SELECTOR, 'obj': LevelSelectorOverlay(self.font_title, self.font, self.overlay_frames, self.level_names, self.func_load_save_file, self.go_back)})

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

    def goto_level_selector(self, filename):
        self.saves.load_saves()
        self.current_menu = self.find_menu(LEVEL_SELECTOR)
        for save in self.saves.get_all_saves():
            if (save['filename'] == filename):
                self.current_menu.set_save_info(filename, save['data']['highest_level_cleared'])
                break

    def goto_control_help(self):
        print("how to play")
        #self.current_menu = self.find_menu(CONTROL_HELP)

    def go_back(self):
        dest = MAIN
        curr_overlay = self.current_menu.overlay
        if curr_overlay == SAVES:
            dest = MAIN
        elif curr_overlay == LEVEL_SELECTOR:
            dest = SAVES
        elif curr_overlay == CONTROL_HELP:
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

        self.container_size = vector(275, 150)
        self.current_total_spacing_y = 0
        self.between_spacing_x, self.between_spacing_y = 25, 25

        self.subtitle_surfaces = []

        self.content_surfaces = {
            "center":
                {
                    "surfaces": [],
                    "content_col_x": WINDOW_WIDTH/2 - self.container_size.x/2,
                    "start_idx": 0
                },
            "right_1":
                {
                    "surfaces": [],
                    "content_col_x": WINDOW_WIDTH/2 + self.container_size.x + self.between_spacing_x,
                    "start_idx": 0
                },
            "left_1":
                {
                    "surfaces": [],
                    "content_col_x": WINDOW_WIDTH/2 - self.container_size.x/2 - self.between_spacing_x - self.container_size.x,
                    "start_idx": 0
                }
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

    def create_content_surface(self, text, func, params):
        container = []
        # container
        container_surf = pygame.Surface((self.container_size.x, self.container_size.y))
        container_surf.set_alpha(85)
        container_surf.fill('#28282B')
        container.append({'name': text, "surf": container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": func, "params": params})  
        # text
        text_surf = self.font.render(text, False, "white", bgcolor=None, wraplength=0)
        container.append({"name": text, "surf": text_surf, "layer": 1, "offset": vector(self.container_size.x/2 - text_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None})
        return container

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
        x = self.content_surfaces['center']['content_col_x']
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

                        if (surf['clickable']):
                            self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))

                    y += y_add + between_spacing_y

        content_y = y # starting y of the content
        for content_elems in self.content_surfaces.values():
            if (list):
                start_idx = content_elems['start_idx']
                x = content_elems['content_col_x']
                y = content_y   # reset to top of content section
                for i in range(start_idx, len(content_elems['surfaces'])):
                    content_elems['surfaces'][i].sort(key = lambda s: s['layer'])
                    if (y + content_elems['surfaces'][i][0]['surf'].get_height() + content_elems['surfaces'][i][0]['offset'].y > WINDOW_HEIGHT):
                        break
                    else:
                        y_add = 0
                        for surf in content_elems['surfaces'][i]:
                            pos_x = x + surf['offset'].x
                            pos_y = y + surf['offset'].y
                            self.display_surface.blit(surf['surf'], (pos_x, pos_y))
                            if (surf['layer'] == 0):
                                y_add = surf['surf'].get_height()
                            if (surf['clickable']):
                                self.buttons.append(Button(surf['name'], surf['surf'], (pos_x, pos_y), surf['surf'].get_size(), surf['clickable'], surf['func'], surf['params']))
                        y += y_add + between_spacing_y

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

        self.content_surfaces['center']['content_col_x'] = WINDOW_WIDTH/2 - self.container_size.x/2
        self.content_surfaces['right_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] + self.container_size.x + self.between_spacing_x

        self.populate_content_surfaces()
        #self.populate_content_surface_right_1()

    def populate_content_surfaces(self):
        self.content_surfaces['center']['surfaces'] = []

        if (self.have_save_data):
            container = self.create_content_surface('Save files', self.func_save_menu, None)
            self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('New game', self.func_new_game, None)
        self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('Player movement', self.func_control_help, None)
        self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('Quit', self.func_quit, None)
        self.content_surfaces['center']['surfaces'].append(container)

    def populate_content_surface_right_1(self):
        self.content_surfaces['right_1']['surfaces'] = []
        container = self.create_content_surface('hello, world!', None, None)
        self.content_surfaces['right_1']['surfaces'].append(container)

    def update(self):
        self.display_title()
        self.display_overlay(self.container_size, self.current_total_spacing_y, self.between_spacing_y)

class ControlHelp(Overlay):
    def __init__(self, font_title, font, overlay_frames, func_go_back):
        super().__init__(SAVES, font_title, font, overlay_frames)

        self.func_go_back = func_go_back

        self.container_size = vector(350, 350)

        self.populate_content_surfaces()

    def populate_content_surfaces(self):
        self.populate_content_surface_center()
        self.populate_content_surface_right_1()
        self.populate_content_surface_left_1()

    def populate_content_surface_center(self):
        self.content_surfaces['center']['surfaces'] = []
        container = []
        container = self.create_content_surface('hello, world!', None, None)
        self.content_surfaces['center']['surfaces'].append(container)

    def populate_content_surface_right_1(self):
        self.content_surfaces['right_1']['surfaces'] = []
        container = []
        container = self.create_content_surface('hello, world!', None, None)
        self.content_surfaces['right_1']['surfaces'].append(container)

    def populate_content_surface_left_1(self):
        self.content_surfaces['left_1']['surfaces'] = []
        containter = []
        container = self.create_content_surface('hello, world!', None, None)
        self.content_surfaces['left_1']['surfaces'].append(container)

    def update(self):
        self.display_title()
        self.display_overlay()

class SavesOverlay(Overlay):
    def __init__(self, font_title, font, save_data, overlay_frames, func_load_save_file, func_go_back):
        
        self._save_data = save_data
        self.func_load_save_file = func_load_save_file
        self.func_go_back = func_go_back

        super().__init__(SAVES, font_title, font, overlay_frames)
        
        self.saves = Saves()

        self.container_size = vector(350, 182)

        self.content_surfaces['center']['content_col_x'] = WINDOW_WIDTH/2 - self.container_size.x/2
        self.content_surfaces['right_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] + self.container_size.x + self.between_spacing_x

        self.populate_subtitle_surfaces()

    @property
    def save_data(self):
        return self._save_data
    
    @save_data.setter
    def save_data(self, save_data):
        self.content_surfaces['center']['start_idx'] = 0
        self._save_data = save_data
        # reload surfaces
        self.populate_content_surfaces()

    def populate_content_surfaces(self):
        self.content_surfaces['center']['surfaces'] = []

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
        container.append({"name": "subtitle_text", "surf": save_title_surf, "layer": 1, "offset": vector(self.container_size.x/2 - save_title_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None})

        save_title_container_surf = pygame.Surface((self.container_size.x, save_title_surf.get_height() + 20))
        save_title_container_surf.set_alpha(85)
        save_title_container_surf.fill('#28282B')
        container.append({"name": "subtitle_container", "surf": save_title_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None})

        self.subtitle_surfaces.append(container)

    def populate_right_col_1(self):
        self.content_surfaces['right_1']['surfaces'] = []
        container = []

        # up
        up_surf = self.font.render('UP', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "UP", "surf": up_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})
        up_surf.set_alpha(0)

        up_container_surf = pygame.Surface((up_surf.get_width() + 20, up_surf.get_height() + 20))
        up_container_surf.set_alpha(0)
        up_container_surf.fill('#28282B')
        clickable = False
        if (self.content_surfaces['center']['start_idx'] > 0):
            clickable = True
            up_surf.set_alpha(255)
            up_container_surf.set_alpha(85)

        container.append({"name": "UP", "surf": up_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": clickable, "func": self.change_start_idx, "params": [-1]})
        self.content_surfaces['right_1']['surfaces'].append(container)
        container = []

        # down
        down_surf = self.font.render('DOWN', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "DOWN", "surf": down_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})
        down_surf.set_alpha(0)

        down_container_surf = pygame.Surface((down_surf.get_width() + 20, down_surf.get_height() + 20))
        down_container_surf.set_alpha(0)
        down_container_surf.fill('#28282B')
        clickable = False
        if (self.content_surfaces['center']['start_idx'] < len(self.content_surfaces['center']['surfaces']) - 1):   # -1 so that at least one save is in the column
            clickable = True
            down_surf.set_alpha(255)
            down_container_surf.set_alpha(85)
        container.append({"name": "DOWN", "surf": down_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.change_start_idx, "params": [1]})
        self.content_surfaces['right_1']['surfaces'].append(container)

    def populate_left_col_1(self):
        self.content_surfaces['left_1']['surfaces'] = []
        container = []
        # back
        back_surf = self.font.render('BACK', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "BACK", "surf": back_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})

        back_container_surf = pygame.Surface((back_surf.get_width() + 20, back_surf.get_height() + 20))
        back_container_surf.fill('#28282B')
        back_container_surf.set_alpha(85)

        container.append({"name": "BACK_container", "surf": back_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.func_go_back, "params": None})
        self.content_surfaces['left_1']['surfaces'].append(container)
        container = []
        
        self.content_surfaces['left_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] - self.between_spacing_x - back_container_surf.get_width()

    def change_start_idx(self, change):
        self.content_surfaces['center']['start_idx'] = max(min(self.content_surfaces['center']['start_idx'] + change, len(self.content_surfaces['center']['surfaces']) - 1), 0)  # -1 so that at least one save is in the column
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
        container_surf.set_alpha(85)
        container_surf.fill('#28282B')
        container.append({"name": str(save['filename']), "surf": container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None})
        
        # file name
        filename_surf = self.font.render('Filename: ' + filename, False, "white", bgcolor=None, wraplength=0)
        container.append({"name": str(save['filename']), "surf": filename_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})

        
        x_offset = 10
        y_offset = filename_surf.get_height()
        row_height = 32
        x_spacing = 10
        y_spacing = 15
        
        # items
        # hearts
        bottom_of_row_y = y_offset + y_spacing + row_height

        heart_surf = self.overlay_frames['heart'][0]
        container.append({"name": "heart", "surf": heart_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - heart_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += heart_surf.get_width() + x_spacing/2
        heart_num_surf = self.font.render('x ' + str(save_data['player_health']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "heart", "surf": heart_num_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - heart_num_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += heart_num_surf.get_width() + x_spacing*3

        # denta
        denta_surf = self.overlay_frames['denta'][0]
        container.append({"name": "denta", "surf": denta_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - denta_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += denta_surf.get_width() + x_spacing/2
        denta_num_surf = self.font.render('x ' + str(save_data['denta']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "denta", "surf": denta_num_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - denta_num_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += denta_num_surf.get_width() + x_spacing*3

        # kibble
        kibble_surf = self.overlay_frames['kibble'][0]
        container.append({"name": "kibble", "surf": kibble_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - kibble_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += kibble_surf.get_width() + x_spacing/2
        kibble_num_surf = self.font.render('x ' + str(save_data['kibble']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "kibble", "surf": kibble_num_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - kibble_num_surf.get_height()), "clickable": False, "func": None, "params": None})

        # weapons
        x_offset = 10

        bottom_of_row_y += y_spacing + row_height
        # stick
        stick_surf = self.overlay_frames['weapons']['stick']
        container.append({"name": "stick_img", "surf": stick_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - stick_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += stick_surf.get_width() + x_spacing/2
        stick_level_surf = self.font.render('lvl ' + str(save_data['stick_level']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "stick_level", "surf": stick_level_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - stick_level_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += stick_level_surf.get_width() + x_spacing*3

        # umbrella
        umbrella_surf = self.overlay_frames['weapons']['umbrella']
        container.append({"name": "umbrella_img", "surf": umbrella_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - umbrella_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += umbrella_surf.get_width() + x_spacing/2
        umbrella_level_surf = self.font.render('lvl ' + str(save_data['lance_level']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "umbrella_level", "surf": umbrella_level_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - umbrella_level_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += umbrella_level_surf.get_width() + x_spacing*3

        # ball
        ball_surf = self.overlay_frames['weapons']['ball']
        container.append({"name": "ball_img", "surf": ball_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - ball_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += ball_surf.get_width() + x_spacing/2
        ball_level_surf = self.font.render('lvl ' + str(save_data['ball_level']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "ball_level", "surf": ball_level_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - ball_level_surf.get_height()), "clickable": False, "func": None, "params": None})
        x_offset += ball_level_surf.get_width() + x_spacing*3

        # save file operations.
        x_offset = 10
        bottom_of_row_y += y_spacing + row_height
        # level select
        level_select_surf = self.font.render('Level select', False, "white", bgcolor=None, wraplength=0)
        level_select_container_surf = pygame.Surface((160, level_select_surf.get_height() + 20))

        container.append({"name": 'level_sel_surf', "surf": level_select_surf, "layer": 2, "offset": vector(level_select_container_surf.get_width()/2 - level_select_surf.get_width()/2, bottom_of_row_y - level_select_surf.get_height()), "clickable": False, "func": None, "params": None})

        level_select_container_surf.set_alpha(85)
        level_select_container_surf.fill('#28282B')
        container.append({"name": 'level_sel_container_surf', "surf": level_select_container_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - level_select_container_surf.get_height() + 10), "clickable": True, "func": self.save_file_chosen, "params": [str(save['filename'])]})
        x_offset += level_select_container_surf.get_width()

        # delete
        delete_surf = self.font.render('Delete', False, "white", bgcolor=None, wraplength=0)
        delete_container_surf = pygame.Surface((160, delete_surf.get_height() + 20))

        container.append({"name": 'delete_surf', "surf": delete_surf, "layer": 2, "offset": vector(x_offset + x_spacing + delete_container_surf.get_width()/2 - delete_surf.get_width()/2, bottom_of_row_y - delete_surf.get_height()), "clickable": False, "func": None, "params": None})
        
        delete_container_surf.set_alpha(85)
        delete_container_surf.fill('#28282B')
        container.append({"name": 'delete_container_surf', "surf": delete_container_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - delete_container_surf.get_height() + 10), "clickable": True, "func": self.delete_save_file, "params": [str(save['filename'])]})


        self.content_surfaces['center']['surfaces'].append(container)

    def delete_save_file(self, filename):
        self.saves.delete_file(filename)

    def draw_test(self):
        for button in self.buttons:
            pygame.draw.rect(self.display_surface, "red", (button.pos, button.size))

    def update(self):
        self.display_title()
        self.display_overlay(self.container_size, self.current_total_spacing_y, self.between_spacing_y)
    
        #self.draw_test()

class LevelSelectorOverlay(Overlay):
    def __init__(self, font_title, font, overlay_frames, level_names, func_load_save_file, func_go_back):
        super().__init__(LEVEL_SELECTOR, font_title, font, overlay_frames)

        self.level_names = level_names
        self.func_load_save_file = func_load_save_file
        self.func_go_back = func_go_back

        self.filename = ''
        self._highest_level_cleared = 0

        test_text = self.font.render('hello, world!', False, "white", bgcolor=None, wraplength=0)
        self.container_size = vector(275, test_text.get_height() + 20)

        self.populate_subtitle_surfaces()
        self.populate_content_surface_center()
        self.populate_left_col_1()

    def populate_subtitle_surfaces(self):
        self.subtitle_surfaces = []
        container = []
        # 'Saves' subtitle
        level_selector_surf = self.font.render('Level selector', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "level_selector_text", "surf": level_selector_surf, "layer": 1, "offset": vector(self.container_size.x/2 - level_selector_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None})

        level_selector_container_surf = pygame.Surface((self.container_size.x, level_selector_surf.get_height() + 20))
        level_selector_container_surf.set_alpha(85)
        level_selector_container_surf.fill('#28282B')
        container.append({"name": "level_selector_container", "surf": level_selector_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None})

        self.subtitle_surfaces.append(container)

    def set_save_info(self, filename, highest_level_cleared):
        self.filename = filename
        self._highest_level_cleared = highest_level_cleared
        self.populate_content_surface_center()

    def populate_content_surface_center(self):
        self.content_surfaces['center']['surfaces'] = []
        for i in range(1, self._highest_level_cleared + 1):
            container = []
            container = self.create_content_surface(self.level_names[i], self.func_load_save_file, [self.filename, i])
            self.content_surfaces['center']['surfaces'].append(container)

    def populate_left_col_1(self):

        self.content_surfaces['left_1']['surfaces'] = []
        container = []
        # back
        back_surf = self.font.render('BACK', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "BACK", "surf": back_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None})

        back_container_surf = pygame.Surface((back_surf.get_width() + 20, back_surf.get_height() + 20))
        back_container_surf.fill('#28282B')
        back_container_surf.set_alpha(85)

        container.append({"name": "BACK_container", "surf": back_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.func_go_back, "params": None})
        self.content_surfaces['left_1']['surfaces'].append(container)
        container = []
        
        self.content_surfaces['left_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] - self.between_spacing_x - back_container_surf.get_width()

    # def populate_content_surface_left_1(self):
    #     self.content_surfaces['left_1']['surfaces'] = []
    #     containter = []
    #     container = self.create_content_surface('hello, world!', None)
    #     self.content_surfaces['left_1']['surfaces'].append(container)

    def update(self):
        self.display_title()
        self.display_overlay(self.container_size, self.current_total_spacing_y, self.between_spacing_y)
