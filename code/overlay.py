from collections import deque

from settings import *
from saves import Saves
from timerClass import Timer

class PauseMainControl:
    def __init__(self, font_title, font, overlay_frames, obj_data, func_resume_game, func_to_main_menu, func_load_save_file, func_quit, level_names):
        self.font_title = font_title
        self.font = font
        self.overlay_frames = overlay_frames
        self.obj_data = obj_data
        self.level_names = level_names

        self.func_resume_game = func_resume_game
        self.func_to_main_menu = func_to_main_menu
        self.func_load_save_file = func_load_save_file
        self.func_quit = func_quit

        self.pause_menu_list = []
        self.setup_menus()
        self.current_menu = self.find_menu(PAUSE_MAIN)

    def setup_menus(self):
        self.pause_menu_list.append({'menu_name': PAUSE_MAIN, 'obj': PauseMainOverlay(self.font_title, self.font, self.overlay_frames, self.obj_data, self.func_resume_game, self.func_to_main_menu, self.goto_level_selector, self.goto_control_help, self.func_quit)})

        self.pause_menu_list.append({'menu_name': LEVEL_SELECTOR, 'obj': LevelSelectorOverlay(self.font_title, self.font, self.overlay_frames, self.level_names, self.func_load_save_file, self.go_back)})

        self.pause_menu_list.append({'menu_name': CONTROL_HELP, 'obj': HowToPlayOverlay('How to play', self.font_title, self.font, self.overlay_frames, self.go_back)})

    def find_menu(self, name):
        for menu in self.pause_menu_list:
            if (menu['menu_name'] == name):
                return menu['obj']
            
        # else
        print("Menu does not exist")

    def goto_pause_main(self):
        # go to pause main
        self.current_menu = self.find_menu(PAUSE_MAIN)

    def goto_level_selector(self):
        self.current_menu = self.find_menu(LEVEL_SELECTOR)
        self.current_menu.set_save_info(self.obj_data.save_filename, self.obj_data.highest_stage_level)

    def goto_control_help(self):
        self.current_menu = self.find_menu(CONTROL_HELP)

    def go_back(self):
        dest = PAUSE_MAIN
        self.current_menu = self.find_menu(dest)

    def get_current_menu(self):
        return self.current_menu

class MainMenuControl:
    def __init__(self, font_title, font, font_creidts, overlay_frames, func_new_save_file, func_load_save_file, func_quit, level_names):

        self.font_title = font_title
        self.font = font
        self.font_credits = font_creidts
        self.overlay_frames = overlay_frames
        self.level_names = level_names

        # callback triggers to main
        self.func_new_save_file = func_new_save_file
        self.func_load_save_file = func_load_save_file  # in level selector overlay callback to this
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

        self.main_menu_list.append({'menu_name': MAIN, 'obj': MainMenuOverlay(self.font_title, self.font, self.overlay_frames, True if (self.saves.get_all_saves) else False, self.goto_save_menu, self.func_new_save_file, self.goto_control_help, self.goto_credits, self.func_quit)})
        
        self.main_menu_list.append({'menu_name': SAVES, 'obj': SavesOverlay(self.font_title, self.font, self.saves.get_all_saves, self.overlay_frames, self.goto_level_selector, self.go_back)})

        self.main_menu_list.append({'menu_name': LEVEL_SELECTOR, 'obj': LevelSelectorOverlay(self.font_title, self.font, self.overlay_frames, self.level_names, self.func_load_save_file, self.go_back)})

        self.main_menu_list.append({'menu_name': CONTROL_HELP, 'obj': HowToPlayOverlay('How to play', self.font_title, self.font, self.overlay_frames, self.go_back)})

        self.main_menu_list.append({'menu_name': CREDITS, 'obj': GameCompleteOverlay('Thank you for playing!', self.font_title, self.font, self.font_credits, self.overlay_frames, self.go_back, self.func_quit)}) #Thank you!!!

    def find_menu(self, name):
        for menu in self.main_menu_list:
            if (menu['menu_name'] == name):
                return menu['obj']
            
        # else
        print("Menu does not exist")

    def goto_main_menu(self):
        self.current_menu = self.find_menu(MAIN)

    def goto_save_menu(self):
        self.saves.load_saves()
        self.current_menu = self.find_menu(SAVES)
        self.current_menu.save_data = self.saves.get_all_saves()

    def goto_level_selector(self, filename):
        self.saves.load_saves()
        self.current_menu = self.find_menu(LEVEL_SELECTOR)
        for save in self.saves.get_all_saves():
            if (save['filename'] == filename):
                self.current_menu.set_save_info(filename, save['data']['highest_stage_level'])
                break

    def goto_control_help(self):
        self.current_menu = self.find_menu(CONTROL_HELP)

    def goto_credits(self):
        self.current_menu = self.find_menu(CREDITS)

    def go_back(self):
        dest = MAIN
        curr_overlay = self.current_menu.overlay
        if curr_overlay == SAVES:
            dest = MAIN
        elif curr_overlay == LEVEL_SELECTOR:
            dest = SAVES
        elif curr_overlay == CONTROL_HELP:
            dest = MAIN
        elif curr_overlay == CREDITS:
            dest = MAIN
        else:
            dest = MAIN
        
        self.current_menu = self.find_menu(dest)

    def get_current_menu(self):
        return self.current_menu


class Button:
    def __init__(self, surf, pos):
        self.name = surf['name']
        self.surface = surf['surf']
        self.pos = pos
        self.size = surf['surf'].get_size()
        self.clickable = surf['clickable']
        self.func = surf['func']
        self.params = surf['params']
        self.click_sound = surf['click_sound']

    def click(self):
        if self.clickable and self.func is not None:
            if self.click_sound is not None:
                self.click_sound.play()

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

        self.content_y = 0

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

    def create_content_surface(self, text, func, params, click_sound = None):
        container = []
        # container
        container_surf = pygame.Surface((self.container_size.x, self.container_size.y))
        container_surf.set_alpha(105)
        container_surf.fill('#28282B')
        container.append({'name': text + str('_container'), "surf": container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": func, "params": params, "click_sound": click_sound})  
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

    def display_overlay(self, current_total_spacing_y, between_spacing_y):
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
                            self.buttons.append(Button(surf, (pos_x, pos_y)))

                    y += y_add + between_spacing_y

        self.content_y = y # starting y of the content
        for content_elems in self.content_surfaces.values():
            if (list):
                start_idx = content_elems['start_idx']
                x = content_elems['content_col_x']
                y = self.content_y   # reset to top of content section
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
                                self.buttons.append(Button(surf, (pos_x, pos_y)))
                        y += y_add + between_spacing_y

class HowToPlayOverlay(Overlay):
    def __init__(self, subtitle_text, font_title, font, overlay_frames, func_go_back):
        super().__init__(HOW_TO_PLAY, font_title, font, overlay_frames)

        self.subtitle_text = subtitle_text

        self.func_go_back = func_go_back

        test_text = self.font.render(subtitle_text, False, "white", bgcolor=None, wraplength=0)
        self.container_size = vector(test_text.get_width() + 20, test_text.get_height() + 20)

        self.content_surfaces['center']['content_col_x'] = WINDOW_WIDTH/2 - self.container_size.x/2

        # sounds
        self.back_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Menu_Navigate_03.wav"))
        self.back_sound.set_volume(0.05) 

        self.display_title() # just to update current_total_spacing_y
        self.y_offset = self.current_total_spacing_y

        #self.populate_subtitle_surfaces()
        self.populate_center_surface()

    def populate_center_surface(self):
        container = self.create_content_surface('Back', self.func_go_back, None, self.back_sound)
        self.content_surfaces['center']['surfaces'].append(container)

    def populate_subtitle_surfaces(self):
        self.subtitle_surfaces = []
        container = []
        # 'Saves' subtitle
        subtitle_surf = self.font.render(self.subtitle_text, False, "white", bgcolor=None, wraplength=0)

        subtitle_container_surf = pygame.Surface((self.container_size.x, subtitle_surf.get_height() + 20))
        subtitle_container_surf.set_alpha(200)
        subtitle_container_surf.fill('#28282B')

        self.y_offset += subtitle_container_surf.get_height()

        container.append({"name": "subtitle_text", "surf": subtitle_surf, "layer": 1, "offset": vector(subtitle_container_surf.get_width()/2 - subtitle_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None, "click_sound": None})
        container.append({"name": "subtitle_container", "surf": subtitle_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, "click_sound": None})

        self.subtitle_surfaces.append(container)

    def display_movement_controls(self):
        local_x_offset = self.between_spacing_x
        local_y_offset = self.y_offset# + self.between_spacing_y

        general_container_x = (WINDOW_WIDTH/2) - local_x_offset*2


        movement_subtitle = self.font.render('Movement', False, "white", bgcolor=None, wraplength=0)
        movement_subtitle_container = pygame.Surface((movement_subtitle.get_width() + 20, movement_subtitle.get_height() + 20))
        movement_subtitle_container.set_alpha(200)

        self.display_surface.blit(movement_subtitle_container, (local_x_offset + general_container_x/2 - movement_subtitle_container.get_width()/2, local_y_offset))
        self.display_surface.blit(movement_subtitle, (local_x_offset + general_container_x/2 - movement_subtitle.get_width()/2,  local_y_offset + movement_subtitle_container.get_height()/2 - movement_subtitle.get_height()/2))

        local_y_offset += movement_subtitle_container.get_height() + self.between_spacing_y

        # left
        move_left = self.font.render(CONTROLS[CNTRL_MOVE_LEFT][DESC] + " : [" + CONTROLS[CNTRL_MOVE_LEFT][KEY] + "]", False, "white", bgcolor=None, wraplength=0)
        move_left_container = pygame.Surface((general_container_x/2 - 10, move_left.get_height() + 20))
        move_left_container.set_alpha(200)
        self.display_surface.blit(move_left_container, (local_x_offset,  local_y_offset))
        self.display_surface.blit(move_left, (local_x_offset + 10,  local_y_offset + move_left_container.get_height()/2 - move_left.get_height()/2))

        # right
        move_right = self.font.render(CONTROLS[CNTRL_MOVE_RIGHT][DESC] + " : [" + CONTROLS[CNTRL_MOVE_RIGHT][KEY] + "]", False, "white", bgcolor=None, wraplength=0)
        move_right_container = pygame.Surface((general_container_x/2 - 10, move_right.get_height() + 20))
        move_right_container.set_alpha(200)
        self.display_surface.blit(move_left_container, (local_x_offset + move_left_container.get_width() + 20,  local_y_offset))
        self.display_surface.blit(move_right, (local_x_offset + move_left_container.get_width() + 20 + 10,  local_y_offset + move_right_container.get_height()/2 - move_right.get_height()/2))

        local_y_offset += move_left_container.get_height() + 5

        # drop down
        move_down = self.font.render(CONTROLS[CNTRL_MOVE_DOWN][DESC] + " : [" + CONTROLS[CNTRL_MOVE_DOWN][KEY] + "] (To drop through half platforms, seen below)", False, "white", bgcolor=None, wraplength=0)
        move_down_container = pygame.Surface((general_container_x, move_right.get_height() + 20))
        move_down_container.set_alpha(200)
        self.display_surface.blit(move_down_container, (local_x_offset,  local_y_offset))
        self.display_surface.blit(move_down, (local_x_offset + 10,  local_y_offset + move_down_container.get_height()/2 - move_down.get_height()/2))

        local_y_offset += move_down_container.get_height() + 5 / 2
        # half platform images
        half_plat_1 = self.overlay_frames['how_to_play']['half_plat_1']
        half_plat_1_container = pygame.Surface((half_plat_1.get_width() + 10, half_plat_1.get_height() + 10))
        self.display_surface.blit(half_plat_1_container, (local_x_offset + general_container_x/2 - 10 - half_plat_1_container.get_width(),  local_y_offset))
        self.display_surface.blit(half_plat_1, (local_x_offset + general_container_x/2 - 10 - half_plat_1_container.get_width()/2 - half_plat_1.get_width()/2,  local_y_offset + half_plat_1_container.get_height()/2 - half_plat_1.get_height()/2))

        half_plat_2 = self.overlay_frames['how_to_play']['half_plat_2']
        half_plat_2_container = pygame.Surface((half_plat_1.get_width() + 10, half_plat_1.get_height() + 10))
        self.display_surface.blit(half_plat_2_container, (local_x_offset + general_container_x/2 + 10,  local_y_offset))
        self.display_surface.blit(half_plat_2, (local_x_offset + general_container_x/2 + 10 + half_plat_2_container.get_width()/2 - half_plat_2.get_width()/2,  local_y_offset + half_plat_2_container.get_height()/2 - half_plat_2.get_height()/2))

        local_y_offset += half_plat_2_container.get_height() + 5

        # jump
        # jumping_subtitle = self.font.render('Jumping', False, "white", bgcolor=None, wraplength=0)
        # jumping_subtitle_container = pygame.Surface((jumping_subtitle.get_width() + 20, jumping_subtitle.get_height() + 20))
        # jumping_subtitle_container.set_alpha(200)

        # self.display_surface.blit(jumping_subtitle_container, (local_x_offset + general_container_x/2 - jumping_subtitle_container.get_width()/2, local_y_offset))
        # self.display_surface.blit(jumping_subtitle, (local_x_offset + general_container_x/2 - jumping_subtitle.get_width()/2,  local_y_offset + jumping_subtitle_container.get_height()/2 - movement_subtitle.get_height()/2))

        local_y_offset += 5 #jumping_subtitle_container.get_height() + 5

        # tap jump
        tap_jump = self.font.render("Tap [" + CONTROLS[CNTRL_JUMP][KEY] + "] for normal jump", False, "white", bgcolor=None, wraplength=0)
        tap_jump_container = pygame.Surface((general_container_x/2 - 10, tap_jump.get_height() + 20))
        tap_jump_container.set_alpha(200)
        self.display_surface.blit(tap_jump_container, (local_x_offset,  local_y_offset))
        self.display_surface.blit(tap_jump, (local_x_offset + 10,  local_y_offset + tap_jump_container.get_height()/2 - tap_jump.get_height()/2))

        # hold jump
        hold_jump_right = self.font.render("Hold [" + CONTROLS[CNTRL_JUMP][KEY] + "] for higher jump", False, "white", bgcolor=None, wraplength=0)
        hold_jump_right_container = pygame.Surface((general_container_x/2 - 10, hold_jump_right.get_height() + 20))
        hold_jump_right_container.set_alpha(200)
        self.display_surface.blit(move_left_container, (local_x_offset + move_left_container.get_width() + 20,  local_y_offset))
        self.display_surface.blit(hold_jump_right, (local_x_offset + move_left_container.get_width() + 20 + 10,  local_y_offset + hold_jump_right_container.get_height()/2 - hold_jump_right.get_height()/2))

        local_y_offset += tap_jump_container.get_height() + 5

        # jump images
        tap_jump = self.overlay_frames['how_to_play']['tap_jump']
        tap_jump_container = pygame.Surface((tap_jump.get_width() + 10, tap_jump.get_height() + 10))
        self.display_surface.blit(tap_jump_container, (local_x_offset + general_container_x/2 - 10 - tap_jump_container.get_width(),  local_y_offset))
        self.display_surface.blit(tap_jump, (local_x_offset + general_container_x/2 - 10 - tap_jump_container.get_width()/2 - tap_jump.get_width()/2,  local_y_offset + tap_jump_container.get_height()/2 - tap_jump.get_height()/2))

        hold_jump = self.overlay_frames['how_to_play']['hold_jump']
        hold_jump_container = pygame.Surface((hold_jump.get_width() + 10, hold_jump.get_height() + 10))
        self.display_surface.blit(hold_jump_container, (local_x_offset + general_container_x/2 + 10,  local_y_offset))
        self.display_surface.blit(hold_jump, (local_x_offset + general_container_x/2 + 10 + hold_jump_container.get_width()/2 - hold_jump.get_width()/2,  local_y_offset + hold_jump_container.get_height()/2 - hold_jump.get_height()/2))

        local_y_offset += hold_jump_container.get_height() + 5

        wall_jump_instr = self.font.render('While touching a wall, jump to wall jump!', False, "white", bgcolor=None, wraplength=0)
        wall_jump_instr_container = pygame.Surface((wall_jump_instr.get_width() + 20, wall_jump_instr.get_height() + 20))
        wall_jump_instr_container.set_alpha(200)

        self.display_surface.blit(wall_jump_instr_container, (local_x_offset + general_container_x/2 - wall_jump_instr_container.get_width()/2, local_y_offset))
        self.display_surface.blit(wall_jump_instr, (local_x_offset + general_container_x/2 - wall_jump_instr.get_width()/2,  local_y_offset + wall_jump_instr_container.get_height()/2 - movement_subtitle.get_height()/2))


    def display_combat_controls(self):
        local_x_offset = WINDOW_WIDTH/2 + self.between_spacing_x
        local_y_offset = self.y_offset# + self.between_spacing_y

        general_container_x = (WINDOW_WIDTH/2) - self.between_spacing_x*2

        attack_subtitle = self.font.render('Attacking', False, "white", bgcolor=None, wraplength=0)
        attack_subtitle_container = pygame.Surface((attack_subtitle.get_width() + 20, attack_subtitle.get_height() + 20))
        attack_subtitle_container.set_alpha(200)

        self.display_surface.blit(attack_subtitle_container, (local_x_offset + general_container_x/2 - attack_subtitle_container.get_width()/2, local_y_offset))
        self.display_surface.blit(attack_subtitle, (local_x_offset + general_container_x/2 - attack_subtitle.get_width()/2,  local_y_offset + attack_subtitle_container.get_height()/2 - attack_subtitle.get_height()/2))

        local_y_offset += attack_subtitle_container.get_height() + self.between_spacing_y

        # selecting weapon
        selecting_weapon = self.font.render("Select a weapon with [" + CONTROLS[CNTRL_WEAPON_1][KEY] + "], ["  + CONTROLS[CNTRL_WEAPON_2][KEY] + "], and ["  + CONTROLS[CNTRL_WEAPON_3][KEY] + "] or the scroll wheel.", False, "white", bgcolor=None, wraplength=0)
        selecting_weapon_container = pygame.Surface((general_container_x, selecting_weapon.get_height() + 20))
        selecting_weapon_container.set_alpha(200)
        self.display_surface.blit(selecting_weapon_container, (local_x_offset,  local_y_offset))
        self.display_surface.blit(selecting_weapon, (local_x_offset + 10,  local_y_offset + selecting_weapon_container.get_height()/2 - selecting_weapon.get_height()/2))

        local_y_offset += selecting_weapon_container.get_height() + 5 / 2

        # weapons inventory image
        weapon_inv = self.overlay_frames['how_to_play']['weapon_inv']
        weapon_inv_container = pygame.Surface((weapon_inv.get_width() + 10, weapon_inv.get_height() + 10))
        self.display_surface.blit(weapon_inv_container, (local_x_offset + general_container_x/2 - weapon_inv_container.get_width()/2,  local_y_offset))
        self.display_surface.blit(weapon_inv, (local_x_offset + general_container_x/2 - weapon_inv.get_width()/2,  local_y_offset + weapon_inv_container.get_height()/2 - weapon_inv.get_height()/2))

        local_y_offset += weapon_inv_container.get_height() + 5

        # how to attack
        attack = self.font.render("To attack, aim with the mouse and then click to attack.", False, "white", bgcolor=None, wraplength=0)
        attack_container = pygame.Surface((general_container_x, attack.get_height() + 20))
        attack_container.set_alpha(200)
        self.display_surface.blit(attack_container, (local_x_offset,  local_y_offset))
        self.display_surface.blit(attack, (local_x_offset + 10,  local_y_offset + attack_container.get_height()/2 - attack.get_height()/2))

        local_y_offset += attack_container.get_height() + 5

        # Enemies
        enemies_mechanic = self.font.render("Enemies will have a coloured outline,", False, "white", bgcolor=None, wraplength=0)
        enemies_mechanic_container = pygame.Surface((general_container_x, enemies_mechanic.get_height() + 20))
        enemies_mechanic_container.set_alpha(200)
        self.display_surface.blit(enemies_mechanic_container, (local_x_offset,  local_y_offset))
        self.display_surface.blit(enemies_mechanic, (local_x_offset + 10,  local_y_offset + enemies_mechanic_container.get_height()/2 - enemies_mechanic.get_height()/2))

        local_y_offset += enemies_mechanic_container.get_height()

        enemies_mechanic_2 = self.font.render("hit them with the same colour weapon to inflict damage!", False, "white", bgcolor=None, wraplength=0)
        enemies_mechanic_2_container = pygame.Surface((general_container_x, enemies_mechanic_2.get_height() + 20))
        enemies_mechanic_2_container.set_alpha(200)
        self.display_surface.blit(enemies_mechanic_container, (local_x_offset,  local_y_offset))
        self.display_surface.blit(enemies_mechanic_2, (local_x_offset + 10,  local_y_offset + enemies_mechanic_2_container.get_height()/2 - enemies_mechanic_2.get_height()/2))
        
        local_y_offset += enemies_mechanic_2_container.get_height() + 5 / 2

        # lance
        lance_type = self.overlay_frames['how_to_play']['lance_type']
        lance_type_container = pygame.Surface((lance_type.get_width() + 10, lance_type.get_height() + 10))
        self.display_surface.blit(lance_type_container, (local_x_offset + general_container_x/2 - lance_type_container.get_width()/2,  local_y_offset))
        self.display_surface.blit(lance_type, (local_x_offset + general_container_x/2 - lance_type.get_width()/2,  local_y_offset + lance_type_container.get_height()/2 - lance_type.get_height()/2))

        # stick
        stick_type = self.overlay_frames['how_to_play']['stick_type']
        stick_type_container = pygame.Surface((lance_type.get_width() + 10, lance_type.get_height() + 10))
        self.display_surface.blit(stick_type_container, (local_x_offset + general_container_x/2 - lance_type_container.get_width()/2 - 10 - stick_type_container.get_width(),  local_y_offset))
        self.display_surface.blit(stick_type, (local_x_offset + general_container_x/2 - lance_type_container.get_width()/2 - 10 - stick_type_container.get_width()/2 - stick_type.get_width()/2,  local_y_offset + stick_type_container.get_height()/2 - stick_type.get_height()/2))
        
        # ball
        ball_type = self.overlay_frames['how_to_play']['ball_type']
        ball_type_container = pygame.Surface((ball_type.get_width() + 10, ball_type.get_height() + 10))
        self.display_surface.blit(ball_type_container, (local_x_offset + general_container_x/2 + lance_type_container.get_width()/2 + 10,  local_y_offset))
        self.display_surface.blit(ball_type, (local_x_offset + general_container_x/2 + lance_type_container.get_width()/2 + 10 + ball_type_container.get_width()/2 - ball_type.get_width()/2,  local_y_offset + ball_type_container.get_height()/2 - ball_type.get_height()/2))



    def update(self, dt):
        self.display_title()
        self.display_overlay(self.current_total_spacing_y, self.between_spacing_y)
        self.display_movement_controls()
        self.display_combat_controls()

class GameCompleteOverlay(Overlay):
    def __init__(self, subtitle_text, font_title, font, font_credits, overlay_frames, func_to_main_menu, func_quit):
        super().__init__(CREDITS, font_title, font, overlay_frames)

        self.subtitle_text = subtitle_text

        self.font_credits = font_credits

        self.func_to_main_menu = func_to_main_menu
        self.func_quit = func_quit

        test_text = self.font.render(subtitle_text, False, "white", bgcolor=None, wraplength=0)
        self.container_size = vector(test_text.get_width() + 20, test_text.get_height() + 20)

        self.container_size_credits = vector(550, 450)

        self.subtitle_container_surf = None

        self.content_surfaces['center']['content_col_x'] = WINDOW_WIDTH/2 - 25
        self.content_surfaces['right_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] + 50 + self.between_spacing_x

        self.credits_text = ['','','','','','',''] # empty so that credits start lower than the top
        self.credits_path = os.path.join("..", "credits", "credits.txt")
        #self.credits = []
        self.credit_roll_speed = -0.5
        self.credits_q = deque()

        # sounds
        self.select_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Pickup_00.wav"))
        self.select_sound.set_volume(0.05)

        self.back_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Menu_Navigate_03.wav"))
        self.back_sound.set_volume(0.05) 

        self.load_credits_from_file()
        self.populate_subtitle_surfaces()
        self.populate_content_surfaces()
        self.populate_credits()

    def load_credits_from_file(self):
        try:
            f = open(self.credits_path, 'r')
        except OSError:
            print("Could not open/read file:", self.credits_path)
            return None
        else:
            with f:
                for line in f:
                    #print(f'{line.strip()}')
                    self.credits_text.append(line.strip())
    
    def populate_subtitle_surfaces(self):
        self.subtitle_surfaces = []
        container = []
        # 'Saves' subtitle
        save_title_surf = self.font.render(self.subtitle_text, False, "white", bgcolor=None, wraplength=0)

        save_title_container_surf = pygame.Surface((self.container_size.x, save_title_surf.get_height() + 20))
        save_title_container_surf.set_alpha(200)
        save_title_container_surf.fill('#28282B')

        container.append({"name": "subtitle_text", "surf": save_title_surf, "layer": 1, "offset": vector(25 - save_title_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None, "click_sound": None})
        container.append({"name": "subtitle_container", "surf": save_title_container_surf, "layer": 0, "offset": vector(25 - save_title_container_surf.get_width()/2, 0), "clickable": False, "func": None, "params": None, "click_sound": None})

        self.subtitle_surfaces.append(container)

    def populate_left_col_1(self):
        self.content_surfaces['left_1']['surfaces'] = []
        container = []
        # credit subtitle
        subtitle_surf = self.font.render('Credits', False, "white", bgcolor=None, wraplength=0)
        
        self.subtitle_container_surf = pygame.Surface((self.container_size_credits.x, subtitle_surf.get_height() + 20))
        self.subtitle_container_surf.fill('#28282B')
        self.subtitle_container_surf.set_alpha(200)

        container.append({"name": "Credits_sub", "surf": subtitle_surf, "layer": 1, "offset": vector(self.subtitle_container_surf.get_width()/2 - subtitle_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None, "click_sound": None})
        container.append({"name": "Credits_sub_container", "surf": self.subtitle_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, "click_sound": None})
        self.content_surfaces['left_1']['surfaces'].append(container)
        container = []

        # credits
        credits_surf = self.font.render('Credits', False, "white", bgcolor=None, wraplength=0)

        credits_container_surf = pygame.Surface(self.container_size_credits)

        container.append({"name": "Credits", "surf": credits_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, "click_sound": None})
        container.append({"name": "Credits_container", "surf": credits_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, "click_sound": None})
        self.content_surfaces['left_1']['surfaces'].append(container)
        
        # offset
        self.content_surfaces['left_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] - self.between_spacing_x - self.subtitle_container_surf.get_width()



    def populate_credits(self):
        y_spacing = 10
        for credit in self.credits_text:
            surf = self.font_credits.render(credit, False, "white", bgcolor=None, wraplength=0)
            #self.credits.append({"surf": surf, "offset": vector(10, y_spacing)})
            self.credits_q.append({"surf": surf, "offset": vector(10, y_spacing)})
            y_spacing += surf.get_height() + 10

    def populate_content_surfaces(self):
        self.content_surfaces['center']['surfaces'] = []

        # left col 1
        self.populate_left_col_1()

        # right 1
        container = self.create_content_surface('Main menu', self.func_to_main_menu, None, self.back_sound)
        self.content_surfaces['right_1']['surfaces'].append(container)

        container = self.create_content_surface('Quit game', self.func_quit, None, None)
        self.content_surfaces['right_1']['surfaces'].append(container)

    def roll_credits(self, dt):

        start_y = self.content_y + self.subtitle_container_surf.get_height() + self.between_spacing_y
        y_max = start_y + self.container_size_credits.y

        # self.credits.sort(key = lambda credit: credit['offset'].y)
        # print('---')
        # print(self.credits)
        # print(self.credits[-1::])
        len_q = len(self.credits_q)
        # since there can only be one credit exiting the container at one time, indicate to pop the first element and add back to the end of the q to maintain the natural order of the credit roll
        to_pop = False

        for credit in self.credits_q:
            
            y_blit = start_y + credit['offset'].y

            if (y_blit + credit['surf'].get_height() < y_max):
                self.display_surface.blit(credit['surf'], (self.content_surfaces['left_1']['content_col_x'] + credit['offset'].x + self.container_size_credits.x/2 - credit['surf'].get_width()/2, y_blit))
            # do not break, need to update offset of the remaining credits

            credit['offset'].y += self.credit_roll_speed * dt
            y = start_y + credit['offset'].y
            # roll over
            # offset is top left
            if (y < start_y):
                if (self.credits_q[len_q - 1]['offset'].y < self.container_size_credits.y):
                    # if the last credit is within the container, just stick the rollover credit at the bottom of the container
                    credit['offset'].y = self.container_size_credits.y - credit['surf'].get_height()
                else:
                    # must stick the rollover credit to the end of the line of credits.
                    credit['offset'].y = self.credits_q[len_q - 1]['offset'].y + self.credits_q[len_q - 1]['surf'].get_height() + 10 + self.credit_roll_speed * dt    # add speed again since the offset this credit is based on will also be subject to the speed in this loop
                    to_pop = True

        if (to_pop):
            self.credits_q.append(self.credits_q.popleft())

    def update(self, dt):
        self.display_title()
        self.display_overlay(self.current_total_spacing_y, self.between_spacing_y)

        self.roll_credits(dt)

class PauseMainOverlay(Overlay):
    def __init__(self, font_title, font, overlay_frames, obj_data, func_resume_game, func_to_main_menu, goto_level_selector, func_goto_control_help, func_quit):
        super().__init__(MAIN, font_title, font, overlay_frames)

        self.save_data = obj_data

        self.func_resume_game = func_resume_game
        self.func_to_main_menu = func_to_main_menu
        self.goto_level_selector = goto_level_selector
        self.func_goto_control_help = func_goto_control_help
        self.func_quit = func_quit

        test_text = self.font.render('hello, world!', False, "white", bgcolor=None, wraplength=0)
        self.container_size = vector(275, test_text.get_height() + 20)

        self.content_surfaces['center']['content_col_x'] = WINDOW_WIDTH/2 - self.container_size.x/2
        self.content_surfaces['right_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] + self.container_size.x + self.between_spacing_x
        
        # sounds
        self.select_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Pickup_00.wav"))
        self.select_sound.set_volume(0.05)

        self.back_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Menu_Navigate_03.wav"))
        self.back_sound.set_volume(0.05) 

        self.populate_subtitle_surfaces()
        self.populate_content_surfaces()

    def populate_subtitle_surfaces(self):
        self.subtitle_surfaces = []
        container = []
        # 'Saves' subtitle
        save_title_surf = self.font.render('Paused', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "subtitle_text", "surf": save_title_surf, "layer": 1, "offset": vector(self.container_size.x/2 - save_title_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None, "click_sound": None})

        save_title_container_surf = pygame.Surface((self.container_size.x, save_title_surf.get_height() + 20))
        save_title_container_surf.set_alpha(200)
        save_title_container_surf.fill('#28282B')
        container.append({"name": "subtitle_container", "surf": save_title_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, 'click_sound': None})

        self.subtitle_surfaces.append(container)

    def populate_content_surfaces(self):
        self.content_surfaces['center']['surfaces'] = []

        container = self.create_content_surface('Resume game', self.func_resume_game, None, self.select_sound)
        self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('Main menu', self.func_to_main_menu, None, self.select_sound)
        self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('Level select', self.goto_level_selector, None, self.select_sound)
        self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('How to play', self.func_goto_control_help, None, self.select_sound)
        self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('Quit game', self.func_quit, None, None)
        self.content_surfaces['center']['surfaces'].append(container)

    def update(self, dt):
        self.display_title()
        self.display_overlay(self.current_total_spacing_y, self.between_spacing_y)

class MainMenuOverlay(Overlay):
    def __init__(self, font_title, font, overlay_frames, have_save_data, func_goto_save_menu, func_new_game, func_to_control_help, func_goto_credits, func_quit):
        super().__init__(MAIN, font_title, font, overlay_frames)

        self.have_save_data = have_save_data

        self.func_goto_save_menu = func_goto_save_menu
        self.func_new_game = func_new_game
        self.func_to_control_help = func_to_control_help
        self.func_goto_credits = func_goto_credits
        self.func_quit = func_quit

        test_text = self.font.render('hello, world!', False, "white", bgcolor=None, wraplength=0)
        self.container_size = vector(275, test_text.get_height() + 20)

        self.content_surfaces['center']['content_col_x'] = WINDOW_WIDTH/2 - self.container_size.x/2
        self.content_surfaces['right_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] + self.container_size.x + self.between_spacing_x

        # sounds
        self.select_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Pickup_00.wav"))
        self.select_sound.set_volume(0.05)

        self.back_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Menu_Navigate_03.wav"))
        self.back_sound.set_volume(0.05) 

        self.populate_content_surfaces()
        #self.populate_content_surface_right_1()

    def populate_content_surfaces(self):
        self.content_surfaces['center']['surfaces'] = []

        if (self.have_save_data):
            container = self.create_content_surface('Save files', self.func_goto_save_menu, None, self.select_sound)
            self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('New game', self.func_new_game, None, self.select_sound)
        self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('How to play', self.func_to_control_help, None, self.select_sound)
        self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('Credits', self.func_goto_credits, None, self.select_sound)
        self.content_surfaces['center']['surfaces'].append(container)

        container = self.create_content_surface('Quit game', self.func_quit, None, None)
        self.content_surfaces['center']['surfaces'].append(container)

    def populate_content_surface_right_1(self):
        self.content_surfaces['right_1']['surfaces'] = []
        container = self.create_content_surface('hello, world!', None, None)
        self.content_surfaces['right_1']['surfaces'].append(container)

    def update(self, dt):
        self.display_title()
        self.display_overlay(self.current_total_spacing_y, self.between_spacing_y)

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
        container = self.create_content_surface('hello, world!', None, None, None)
        self.content_surfaces['center']['surfaces'].append(container)

    def populate_content_surface_right_1(self):
        self.content_surfaces['right_1']['surfaces'] = []
        container = []
        container = self.create_content_surface('hello, world!', None, None, None)
        self.content_surfaces['right_1']['surfaces'].append(container)

    def populate_content_surface_left_1(self):
        self.content_surfaces['left_1']['surfaces'] = []
        containter = []
        container = self.create_content_surface('hello, world!', None, None, None)
        self.content_surfaces['left_1']['surfaces'].append(container)

    def update(self, dt):
        self.display_title()
        self.display_overlay()

class SavesOverlay(Overlay):
    def __init__(self, font_title, font, save_data, overlay_frames, func_goto_level_selector, func_go_back):
        
        self._save_data = save_data
        self.func_goto_level_selector = func_goto_level_selector
        self.func_go_back = func_go_back

        super().__init__(SAVES, font_title, font, overlay_frames)
        
        self.saves = Saves()

        self.container_size = vector(375, 182)

        self.content_surfaces['center']['content_col_x'] = WINDOW_WIDTH/2 - self.container_size.x/2
        self.content_surfaces['right_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] + self.container_size.x + self.between_spacing_x

        # sounds
        self.select_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Pickup_00.wav"))
        self.select_sound.set_volume(0.05)

        self.back_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Menu_Navigate_03.wav"))
        self.back_sound.set_volume(0.05) 

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
        #else:
            #print("display [No save data]")

        self.populate_left_col_1()

    def populate_subtitle_surfaces(self):
        self.subtitle_surfaces = []
        container = []
        # 'Saves' subtitle
        save_title_surf = self.font.render('Saves', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "subtitle_text", "surf": save_title_surf, "layer": 1, "offset": vector(self.container_size.x/2 - save_title_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None, "click_sound": None})

        save_title_container_surf = pygame.Surface((self.container_size.x, save_title_surf.get_height() + 20))
        save_title_container_surf.set_alpha(200)
        save_title_container_surf.fill('#28282B')
        container.append({"name": "subtitle_container", "surf": save_title_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, "click_sound": None})

        self.subtitle_surfaces.append(container)

    def populate_right_col_1(self):
        self.content_surfaces['right_1']['surfaces'] = []
        container = []

        # up
        up_surf = self.font.render('UP', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "UP", "surf": up_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None, "click_sound": None})
        up_surf.set_alpha(0)

        up_container_surf = pygame.Surface((up_surf.get_width() + 20, up_surf.get_height() + 20))
        up_container_surf.set_alpha(0)
        up_container_surf.fill('#28282B')
        clickable = False
        if (self.content_surfaces['center']['start_idx'] > 0):
            clickable = True
            up_surf.set_alpha(255)
            up_container_surf.set_alpha(105)

        container.append({"name": "UP", "surf": up_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": clickable, "func": self.change_start_idx, "params": [-1], "click_sound": self.select_sound})
        self.content_surfaces['right_1']['surfaces'].append(container)
        container = []

        # down
        down_surf = self.font.render('DOWN', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "DOWN", "surf": down_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None, 'click_sound': None})
        down_surf.set_alpha(0)

        down_container_surf = pygame.Surface((down_surf.get_width() + 20, down_surf.get_height() + 20))
        down_container_surf.set_alpha(0)
        down_container_surf.fill('#28282B')
        clickable = False
        if (self.content_surfaces['center']['start_idx'] < len(self.content_surfaces['center']['surfaces']) - 1):   # -1 so that at least one save is in the column
            clickable = True
            down_surf.set_alpha(255)
            down_container_surf.set_alpha(105)
        container.append({"name": "DOWN", "surf": down_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.change_start_idx, "params": [1], 'click_sound': self.select_sound})
        self.content_surfaces['right_1']['surfaces'].append(container)

    def populate_left_col_1(self):
        self.content_surfaces['left_1']['surfaces'] = []
        container = []
        # back
        back_surf = self.font.render('BACK', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "BACK", "surf": back_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None, 'click_sound': None})

        back_container_surf = pygame.Surface((back_surf.get_width() + 20, back_surf.get_height() + 20))
        back_container_surf.fill('#28282B')
        back_container_surf.set_alpha(105)

        container.append({"name": "BACK_container", "surf": back_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.func_go_back, "params": None, 'click_sound': self.back_sound})
        self.content_surfaces['left_1']['surfaces'].append(container)
        container = []
        
        self.content_surfaces['left_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] - self.between_spacing_x - back_container_surf.get_width()

    def change_start_idx(self, change):
        self.content_surfaces['center']['start_idx'] = max(min(self.content_surfaces['center']['start_idx'] + change, len(self.content_surfaces['center']['surfaces']) - 1), 0)  # -1 so that at least one save is in the column
        self.populate_right_col_1()

    def create_container_save_data(self, save):
        container = []
        stem = save['stem'][:16]
        if (len(save['stem']) >= 16):
            stem += '...'
        save_data = save['data']

        # container
        container_surf = pygame.Surface((self.container_size.x, self.container_size.y))
        container_surf.set_alpha(105)
        container_surf.fill('#28282B')
        container.append({"name": str(save['stem']), "surf": container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, 'click_sound': None})
        
        # file name
        stem_surf = self.font.render('Name: ' + stem, False, "white", bgcolor=None, wraplength=0)
        container.append({"name": str(save['stem']) + "_container", "surf": stem_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None, "click_sound": None})

        
        x_offset = 10
        y_offset = stem_surf.get_height()
        row_height = 32
        x_spacing = 10
        y_spacing = 15
        
        # items
        # hearts
        bottom_of_row_y = y_offset + y_spacing + row_height

        heart_surf = self.overlay_frames['heart'][0]
        container.append({"name": "heart", "surf": heart_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - heart_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += heart_surf.get_width() + x_spacing/2
        heart_num_surf = self.font.render('x ' + str(save_data['player_health']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "heart", "surf": heart_num_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - heart_num_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += heart_num_surf.get_width() + x_spacing*3

        # denta
        denta_surf = self.overlay_frames['denta'][0]
        container.append({"name": "denta", "surf": denta_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - denta_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += denta_surf.get_width() + x_spacing/2
        denta_num_surf = self.font.render('x ' + str(save_data['denta']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "denta", "surf": denta_num_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - denta_num_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += denta_num_surf.get_width() + x_spacing*3

        # kibble
        kibble_surf = self.overlay_frames['kibble'][0]
        container.append({"name": "kibble", "surf": kibble_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - kibble_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += kibble_surf.get_width() + x_spacing/2
        kibble_num_surf = self.font.render('x ' + str(save_data['kibble']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "kibble", "surf": kibble_num_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - kibble_num_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})

        # weapons
        x_offset = 10

        bottom_of_row_y += y_spacing + row_height
        # stick
        stick_surf = self.overlay_frames['weapons']['stick']
        container.append({"name": "stick_img", "surf": stick_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - stick_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += stick_surf.get_width() + x_spacing/2
        stick_level_surf = self.font.render('lvl ' + str(save_data['stick_level']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "stick_level", "surf": stick_level_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - stick_level_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += stick_level_surf.get_width() + x_spacing*3

        # umbrella
        umbrella_surf = self.overlay_frames['weapons']['umbrella']
        container.append({"name": "umbrella_img", "surf": umbrella_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - umbrella_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += umbrella_surf.get_width() + x_spacing/2
        umbrella_level_surf = self.font.render('lvl ' + str(save_data['lance_level']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "umbrella_level", "surf": umbrella_level_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - umbrella_level_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += umbrella_level_surf.get_width() + x_spacing*3

        # ball
        ball_surf = self.overlay_frames['weapons']['ball']
        container.append({"name": "ball_img", "surf": ball_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - ball_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += ball_surf.get_width() + x_spacing/2
        ball_level_surf = self.font.render('lvl ' + str(save_data['ball_level']), False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "ball_level", "surf": ball_level_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - ball_level_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        x_offset += ball_level_surf.get_width() + x_spacing*3

        # save file operations.
        x_offset = 10
        bottom_of_row_y += y_spacing + row_height
        # level select
        level_select_surf = self.font.render('Level select', False, "white", bgcolor=None, wraplength=0)
        level_select_container_surf = pygame.Surface((172.5, level_select_surf.get_height() + 20))

        container.append({"name": 'level_sel_surf', "surf": level_select_surf, "layer": 2, "offset": vector(level_select_container_surf.get_width()/2 - level_select_surf.get_width()/2, bottom_of_row_y - level_select_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})

        level_select_container_surf.set_alpha(105)
        level_select_container_surf.fill('#28282B')
        container.append({"name": 'level_sel_container_surf', "surf": level_select_container_surf, "layer": 1, "offset": vector(x_offset, bottom_of_row_y - level_select_container_surf.get_height() + 10), "clickable": True, "func": self.func_goto_level_selector, "params": [str(save['filename'])], "click_sound": self.select_sound})
        x_offset += level_select_container_surf.get_width()

        # delete
        delete_surf = self.font.render('Delete', False, "white", bgcolor=None, wraplength=0)
        delete_container_surf = pygame.Surface((172.5, delete_surf.get_height() + 20))

        container.append({"name": 'delete_surf', "surf": delete_surf, "layer": 2, "offset": vector(x_offset + x_spacing + delete_container_surf.get_width()/2 - delete_surf.get_width()/2, bottom_of_row_y - delete_surf.get_height()), "clickable": False, "func": None, "params": None, "click_sound": None})
        
        delete_container_surf.set_alpha(105)
        delete_container_surf.fill('#28282B')
        container.append({"name": 'delete_container_surf', "surf": delete_container_surf, "layer": 1, "offset": vector(x_offset + x_spacing, bottom_of_row_y - delete_container_surf.get_height() + 10), "clickable": True, "func": self.delete_save_file, "params": [str(save['filename'])], "click_sound": self.select_sound})


        self.content_surfaces['center']['surfaces'].append(container)

    def delete_save_file(self, filename):
        self.saves.delete_file(filename)
        self.reload_saves()

    def reload_saves(self):
        self.saves.load_saves()
        self.save_data = self.saves.get_all_saves()

    def draw_test(self):
        for button in self.buttons:
            pygame.draw.rect(self.display_surface, "red", (button.pos, button.size))

    def update(self, dt):
        self.display_title()
        self.display_overlay(self.current_total_spacing_y, self.between_spacing_y)
    
        #self.draw_test()

class LevelSelectorOverlay(Overlay):
    def __init__(self, font_title, font, overlay_frames, level_names, func_load_save_file, func_go_back):
        super().__init__(LEVEL_SELECTOR, font_title, font, overlay_frames)

        self.level_names = level_names
        self.func_load_save_file = func_load_save_file
        self.func_go_back = func_go_back

        self.filename = ''
        self._highest_stage_level = 0

        test_text = self.font.render('hello, world!', False, "white", bgcolor=None, wraplength=0)
        self.container_size = vector(275, test_text.get_height() + 20)

        self.content_surfaces['center']['content_col_x'] = WINDOW_WIDTH/2 - self.container_size.x/2

        # sounds
        self.select_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Pickup_00.wav"))
        self.select_sound.set_volume(0.05)

        self.back_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "menu_select", "Menu_Navigate_03.wav"))
        self.back_sound.set_volume(0.05) 

        self.populate_subtitle_surfaces()
        self.populate_content_surface_center()
        self.populate_left_col_1()

    def populate_subtitle_surfaces(self):
        self.subtitle_surfaces = []
        container = []
        # 'Saves' subtitle
        level_selector_surf = self.font.render('Level selector', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "level_selector_text", "surf": level_selector_surf, "layer": 1, "offset": vector(self.container_size.x/2 - level_selector_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None, "click_sound": None})

        level_selector_container_surf = pygame.Surface((self.container_size.x, level_selector_surf.get_height() + 20))
        level_selector_container_surf.set_alpha(200)
        level_selector_container_surf.fill('#28282B')
        container.append({"name": "level_selector_container", "surf": level_selector_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, "click_sound": None})

        self.subtitle_surfaces.append(container)

    def set_save_info(self, filename, highest_stage_level):
        self.filename = filename
        self._highest_stage_level = highest_stage_level
        self.populate_content_surface_center()

    def populate_content_surface_center(self):
        len_level_names = len(self.level_names)
        self.content_surfaces['center']['surfaces'] = []
        for i in range(1, self._highest_stage_level + 1):
            if (i >= len_level_names):
                break
            container = []
            container = self.create_content_surface(self.level_names[i], self.func_load_save_file, [self.filename, i], self.select_sound)
            self.content_surfaces['center']['surfaces'].append(container)

    def populate_left_col_1(self):

        self.content_surfaces['left_1']['surfaces'] = []
        container = []
        # back
        back_surf = self.font.render('BACK', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "BACK", "surf": back_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None, "click_sound": None})

        back_container_surf = pygame.Surface((back_surf.get_width() + 20, back_surf.get_height() + 20))
        back_container_surf.fill('#28282B')
        back_container_surf.set_alpha(105)

        container.append({"name": "BACK_container", "surf": back_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.func_go_back, "params": None, "click_sound": self.back_sound})
        self.content_surfaces['left_1']['surfaces'].append(container)
        container = []
        
        self.content_surfaces['left_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] - self.between_spacing_x - back_container_surf.get_width()

    # def populate_content_surface_left_1(self):
    #     self.content_surfaces['left_1']['surfaces'] = []
    #     containter = []
    #     container = self.create_content_surface('hello, world!', None, None)
    #     self.content_surfaces['left_1']['surfaces'].append(container)

    def update(self, dt):
        self.display_title()
        self.display_overlay(self.current_total_spacing_y, self.between_spacing_y)

class StoreOverlay(Overlay):
    def __init__(self, font_title, font, overlay_frames, data, func_resume_game):
        super().__init__(STORE, font_title, font, overlay_frames)

        self._data = data
        self.func_resume_game = func_resume_game

        self.shop_text = self.font.render('Shop', False, "white", bgcolor=None, wraplength=0)
        self.container_size = vector(300, self.shop_text.get_width())

        self.content_surfaces['center']['content_col_x'] = WINDOW_WIDTH/2 - self.container_size.x/2

        # sounds
        self.buy_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "shop", "buy_coin.wav"))
        self.buy_sound.set_volume(0.05)

        self.sell_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "shop", "sell_coin3.wav"))
        self.sell_sound.set_volume(0.05)

        self.back_sound = pygame.mixer.Sound(os.path.join("..", "audio", "sound_effects", "shop", "open_shop_cloth-heavy.wav"))
        self.back_sound.set_volume(0.5)

        self.populate_subtitle_surfaces()
        self.populate_content_surface_center()
        self.populate_left_col_1()

    @property
    def data(self):
        return self._data
    
    @data.setter
    def data(self, data):
        self._data = data
        # repop surfaces
        self.populate_content_surface_center()

    def populate_subtitle_surfaces(self):
        self.subtitle_surfaces = []
        container = []
        # 'Saves' subtitle
        level_selector_surf = self.shop_text
        container.append({"name": "Shop_text", "surf": level_selector_surf, "layer": 1, "offset": vector(self.container_size.x/2 - level_selector_surf.get_width()/2, 10), "clickable": False, "func": None, "params": None, 'click_sound':None})

        level_selector_container_surf = pygame.Surface((self.container_size.x, level_selector_surf.get_height() + 20))
        level_selector_container_surf.set_alpha(200)
        level_selector_container_surf.fill('#28282B')
        container.append({"name": "Shop_container", "surf": level_selector_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, 'click_sound': None})

        self.subtitle_surfaces.append(container)
    
    def populate_content_surface_center(self):
        self.content_surfaces['center']['surfaces'] = []
        container = []
        
        # hearts
        # container
        heart_container_surf = pygame.Surface((self.container_size.x, self.container_size.y * 2))
        heart_container_surf.set_alpha(105)
        heart_container_surf.fill('#28282B')
        container.append({"name": "heart_container_surf", "surf": heart_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, 'click_sound': None})
        # desc
        heart_surf = self.overlay_frames['heart'][0]
        heart_buy_surf = self.font.render(f' Price: {self.data.shop_prices["heart"]} treats', False, "white", bgcolor=None, wraplength=0)
        total_len = heart_surf.get_width() + heart_buy_surf.get_width()
        container.append({"name": "heart_surf", "surf": heart_surf, "layer": 1, "offset": vector(self.container_size.x/2 - total_len/2, 10), "clickable": False, "func": None, "params": None, 'click_sound': None})
        container.append({"name": "heart_buy_surf", "surf": heart_buy_surf, "layer": 1, "offset": vector(self.container_size.x/2 + heart_surf.get_width() - total_len/2, 10), "clickable": False, "func": None, "params": None, 'click_sound': None})
        # options
        y_offset = max(heart_surf.get_height(), heart_buy_surf.get_height())
        
        if (self.data.denta >= self.data.shop_prices["heart"]):
            heart_buy = self.font.render('Buy', False, "white", bgcolor=None, wraplength=0)
            heart_buy_container = pygame.Surface((self.container_size.x/2 - 20, heart_buy.get_height() + 20))
            heart_buy_container.set_alpha(105)
            container.append({"name": "heart_buy_container", "surf": heart_buy_container, "layer": 1, "offset": vector(10, y_offset + 10), "clickable": True, "func": self.data.buy_heart, "params": None, 'click_sound': self.buy_sound})
            container.append({"name": "heart_buy", "surf": heart_buy, "layer": 2, "offset": vector(10 + heart_buy_container.get_width()/2 - heart_buy.get_width()/2, y_offset + 10 + heart_buy_container.get_height()/2 - heart_buy.get_height()/2), "clickable": False, "func": None, "params": None, 'click_sound': None})

        if (self.data.player_health > 1):
            heart_sell = self.font.render('Sell', False, "white", bgcolor=None, wraplength=0)
            heart_sell_container = pygame.Surface((self.container_size.x/2 - 20, heart_sell.get_height() + 20))
            heart_sell_container.set_alpha(105)
            container.append({"name": "heart_sell_container", "surf": heart_sell_container, "layer": 1, "offset": vector(heart_container_surf.get_width()/2 + 10, y_offset + 10), "clickable": True, "func": self.data.sell_heart, "params": None, 'click_sound': self.sell_sound})
            container.append({"name": "heart_sell", "surf": heart_sell, "layer": 2, "offset": vector(heart_container_surf.get_width()/2 + 10 + heart_sell_container.get_width()/2 - heart_sell.get_width()/2, y_offset + 10 + heart_sell_container.get_height()/2 - heart_sell.get_height()/2), "clickable": False, "func": None, "params": None, 'click_sound': None})
        
        self.content_surfaces['center']['surfaces'].append(container)
        container = []

        # weapons
        for i in range(len(self.data.weapon_list)):
            weapon_name = str(self.data.weapon_list[i]['weapon'].weapon_name)

            container_surf = pygame.Surface((self.container_size.x, self.container_size.y * 2 + 10))
            container_surf.fill('#28282B')

            surf = self.overlay_frames['weapons'][weapon_name]

            

            if (self.data.check_if_max_level(i)):
                container_surf.set_alpha(200)
                container.append({"name": weapon_name + "_container_surf", "surf": container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, 'click_sound':None})
                text_surf = self.font.render(' At max level', False, "white", bgcolor=None, wraplength=0)
            else:
                container_surf.set_alpha(105)
                container.append({"name": weapon_name + "_container_surf", "surf": container_surf, "layer": 0, "offset": vector(0, 0), "clickable": False, "func": None, "params": None, 'click_sound':None})
                text_surf = self.font.render(f' Upgrade with {self.data.shop_prices[weapon_name]} treats', False, "white", bgcolor=None, wraplength=0)

            total_len = surf.get_width() + text_surf.get_width()

            container.append({"name": "stick_surf", "surf": surf, "layer": 1, "offset": vector(self.container_size.x/2 - total_len/2, 10), "clickable": False, "func": None, "params": None, 'click_sound':None})
            container.append({"name": "stick_text_surf", "surf": text_surf, "layer": 1, "offset": vector(self.container_size.x/2 + surf.get_width() - total_len/2, 10), "clickable": False, "func": None, "params": None, 'click_sound':None})

            # options
            buy = True
            sell = True

            if (self.data.check_if_min_level(i)):
                buy = True
                sell = False
            elif (self.data.check_if_max_level(i)):
                buy = False
                sell = True
            # options
            y_offset = max(surf.get_height(), text_surf.get_height())
            if (buy):
                buy_surf = self.font.render('Buy', False, "white", bgcolor=None, wraplength=0)
                buy_container = pygame.Surface((self.container_size.x/2 - 20, buy_surf.get_height() + 20))
                buy_container.set_alpha(105)
                container.append({"name": "buy_container", "surf": buy_container, "layer": 1, "offset": vector(10, y_offset + 10), "clickable": True, "func": self.data.upgrade_weapon, "params": [i], 'click_sound': self.buy_sound})
                container.append({"name": "buy_surf", "surf": buy_surf, "layer": 2, "offset": vector(10 + buy_container.get_width()/2 - buy_surf.get_width()/2, y_offset + 10 + buy_container.get_height()/2 - buy_surf.get_height()/2), "clickable": False, "func": None, "params": None, 'click_sound': None})

            if (sell):
                sell_surf = self.font.render('Sell', False, "white", bgcolor=None, wraplength=0)
                sell_container = pygame.Surface((self.container_size.x/2 - 20, sell_surf.get_height() + 20))
                sell_container.set_alpha(105)
                container.append({"name": "sell_container", "surf": sell_container, "layer": 1, "offset": vector(container_surf.get_width()/2 + 10, y_offset + 10), "clickable": True, "func": self.data.degrade_weapon, "params": [i], 'click_sound': self.sell_sound})
                container.append({"name": "sell_surf", "surf": sell_surf, "layer": 2, "offset": vector(container_surf.get_width()/2 + 10 + sell_container.get_width()/2 - sell_surf.get_width()/2, y_offset + 10 + sell_container.get_height()/2 - sell_surf.get_height()/2), "clickable": False, "func": None, "params": None, 'click_sound': None})

            self.content_surfaces['center']['surfaces'].append(container)
            container = []

    def populate_left_col_1(self):
        self.content_surfaces['left_1']['surfaces'] = []
        container = []
        # Resume
        back_surf = self.font.render('Exit', False, "white", bgcolor=None, wraplength=0)
        container.append({"name": "Exit", "surf": back_surf, "layer": 1, "offset": vector(10, 10), "clickable": False, "func": None, "params": None, 'click_sound':None})

        back_container_surf = pygame.Surface((back_surf.get_width() + 20, back_surf.get_height() + 20))
        back_container_surf.fill('#28282B')
        back_container_surf.set_alpha(105)

        container.append({"name": "Exit_container", "surf": back_container_surf, "layer": 0, "offset": vector(0, 0), "clickable": True, "func": self.func_resume_game, "params": None, 'click_sound':self.back_sound})
        self.content_surfaces['left_1']['surfaces'].append(container)
        container = []
        
        self.content_surfaces['left_1']['content_col_x'] = self.content_surfaces['center']['content_col_x'] - self.between_spacing_x - back_container_surf.get_width()

    def update(self):
        self.display_title()
        self.populate_content_surface_center()
        self.display_overlay(self.current_total_spacing_y, self.between_spacing_y)

class Transitions:
    def __init__(self):

        self.display_surface = pygame.display.get_surface()
        self.complete = False
        self.speed = 5

        self.timers = {
            'hold': Timer(1000)
        }

    def update_timers(self):
        for timer in self.timers.values():
            timer.update()

class SandwichTransition(Transitions):
    def __init__(self, font, center_text):
        super().__init__()

        self.contacted = False
        self.reverse = False
        self.bg_loaded = False

        self.timers.update(
            {
                'hold': Timer(1000)
            }
        )

        self.top_cover_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.top_cover_rect = self.top_cover_surf.get_frect(topleft = (0, -WINDOW_HEIGHT))

        self.bot_cover_surf = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        self.bot_cover_rect = self.bot_cover_surf.get_frect(topleft = (0, WINDOW_HEIGHT))

        self.text_surf = font.render(center_text, False, "white", bgcolor=None, wraplength=0)

    def update(self, dt):
        self.update_timers()

        if (not self.contacted or self.reverse):
            if (not self.reverse and self.top_cover_rect.bottom >= self.bot_cover_rect.top):
                self.contacted = True
                self.timers['hold'].activate()
            elif (self.reverse and self.top_cover_rect.bottom <= 0 and self.bot_cover_rect.top >= WINDOW_HEIGHT):
                self.complete = True
            else:
                # move rects toward each other
                self.top_cover_rect.centery += self.speed * dt * (-1 if self.reverse else 1)
                pygame.draw.rect(self.display_surface, 'black', self.top_cover_rect)

                self.bot_cover_rect.centery -= self.speed * dt * (-1 if self.reverse else 1)
                pygame.draw.rect(self.display_surface, 'black', self.bot_cover_rect)

        elif (self.contacted):
            if (not self.timers['hold'].active and not self.reverse):
                self.reverse = True

            else:
                pygame.draw.rect(self.display_surface, 'black', self.top_cover_rect)
                pygame.draw.rect(self.display_surface, 'black', self.bot_cover_rect)
                self.display_surface.blit(self.text_surf, (WINDOW_WIDTH/2 - self.text_surf.get_width()/2, WINDOW_HEIGHT/2 - self.text_surf.get_height()/2))
            
        return self.complete