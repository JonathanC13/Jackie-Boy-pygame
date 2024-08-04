from pytmx.util_pygame import load_pygame

from debug import debug
from settings import *
from level import Level
from support import *
from data import Data
from ui import UI
from saves import Saves
from overlay import MainMenuControl, PauseMainControl, GameCompleteOverlay, SandwichTransition, StoreOverlay

class Game:
    
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.previous_time = 0
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Jackie Boy")
        self.import_assets()
        
        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)
        self.curr_level = 0
        self.game_active = True

        self.level_maps_test = [
            {"stage_main" :1, "stage_sub": 1, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "menu.tmx")), "completion_reqs": {}},
            {"stage_main" :1, "stage_sub": 2, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "test.tmx")), "completion_reqs": {"kibble": 5, "denta": 1}}
        ]

        self.level_maps = [
            {"stage_main" :0, "stage_sub": 0, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "menu.tmx")), "completion_reqs": {}},
            {"stage_main" :1, "stage_sub": 1, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "1_1.tmx")), "completion_reqs": {}},
            {"stage_main" :1, "stage_sub": 2, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "1_2.tmx")), "completion_reqs": {}},
            {"stage_main" :1, "stage_sub": 3, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "1_3.tmx")), "completion_reqs": {}},
            {"stage_main" :1, "stage_sub": 4, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "1_4.tmx")), "completion_reqs": {}}
            #,{"stage_main" :999, "stage_sub": 999, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "test.tmx")), "completion_reqs": {}}
        ]

        self.secret_maps = [
            {"stage_main" :0, "stage_sub": 0, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "S_1.tmx")), "completion_reqs": {}}
        ]

        self.level_names = []
        for i in range(len(self.level_maps)):
            self.level_names.append(str(self.level_maps[i]['stage_main']) + '-' + str(self.level_maps[i]['stage_sub']))

        self.main_menus = MainMenuControl(self.font_title, self.font, self.overlay_frames, self.new_game, self.load_save_file, self.quit_game, self.level_names)
        self.saves = Saves()
        self.pause_menu = PauseMainControl(self.font_title, self.font, self.overlay_frames, self.data, self.func_resume_game, self.to_main_menu, self.load_save_file, self.quit_game, self.level_names)
        self.game_complete_screen = GameCompleteOverlay('Game completed!!!', self.font_title, self.font, self.overlay_frames, self.to_main_menu, self.quit_game)
        self.transition_screen = None
        self.store_screen = None

        self.game_state = MAIN_MENU

        self.ui.game_state = self.game_state
        #self.run_level = Level(self.level_maps_test[self.curr_level], self.level_frames, self.data)
        self.run_level = Level(self.level_maps[self.curr_level], self.level_frames, self.data, self.restart_level, self.level_complete, self.open_store, self.font)

    def import_assets(self):
        self.level_frames = {
            'player': import_sub_folders('..', 'graphics', 'player'),
            'husky': import_folder('..', 'graphics', 'npcs', 'husky'),
            'items': import_sub_folders('..', 'graphics', 'items'),
            'platform': import_folder('..', 'graphics', 'level', 'platform'),
			'boat': import_folder('..',  'graphics', 'objects', 'boat'),
            'floor_spikes': import_folder('..', 'graphics','enemies', 'floor_spikes'),
            'thorn_abush': import_folder('..', 'graphics','enemies', 'thorn_bush'),
            'bats': import_folder('..', 'graphics','enemies', 'bats'),
            'water_top': import_folder('..', 'graphics', 'level', 'water', 'top'),
			'water_body': import_image('..', 'graphics', 'level', 'water', 'body'),
			'cloud_small': import_folder('..', 'graphics', 'level', 'clouds', 'small'),
			'cloud_large': import_image('..', 'graphics', 'level', 'clouds', 'large_cloud'),
            'dog': import_sub_folders('..', 'graphics', 'enemies', 'dog'),
            'bird_brown': import_sub_folders('..', 'graphics', 'enemies', 'bird_brown'),
            'bird_white': import_sub_folders('..', 'graphics', 'enemies', 'bird_white'),
            'squirrel': import_sub_folders('..', 'graphics', 'enemies', 'squirrel'),
            'stick': import_sub_folders('..', 'graphics', 'weapons', 'stick'),
            'umbrella': import_sub_folders('..', 'graphics', 'weapons', 'umbrella'),
            'beak': import_sub_folders('..', 'graphics', 'weapons', 'beak'),
            'acorn': import_sub_folders('..', 'graphics', 'weapons', 'acorn'),
            'acorn_projectile': import_sub_folders('..', 'graphics', 'projectile', 'acorn'),
            'ball': import_sub_folders('..', 'graphics', 'weapons', 'ball'),
            'ball_projectile': import_sub_folders('..', 'graphics', 'projectile', 'ball'),
            'items': import_sub_folders('..', 'graphics', 'items'),
            'effect_particle': import_folder('..', 'graphics', 'effects', 'particle'),
            'flag': import_folder('..', 'graphics', 'level', 'flag'),
            'bg_tiles': import_folder_dict('..', 'graphics', 'level', 'bg', 'tiles'),
            'boss_sign': import_sub_folders('..', 'graphics', 'enemies', 'boss', 'sign'),
            'pole_projectile': import_sub_folders('..', 'graphics', 'projectile', 'pole')
        }

        self.font_title = pygame.font.Font(join('..', 'graphics', 'ui', 'font', 'runescape_uf.ttf'), 45)
        self.font = pygame.font.Font(join('..', 'graphics', 'ui', 'font', 'runescape_uf.ttf'), 25)
        
        self.ui_frames = {
            'heart': import_folder('..', 'graphics', 'ui', 'heart'),
            'kibble': import_folder('..', 'graphics', 'ui', 'kibble'),
            'denta': import_folder('..', 'graphics', 'ui', 'denta'),
            'weapons': import_folder_dict('..', 'graphics', 'ui', 'weapons')
        }
        self.overlay_frames = {
            'heart': import_folder('..', 'graphics', 'ui', 'heart'),
            'kibble': import_folder('..', 'graphics', 'ui', 'kibble'),
            'denta': import_folder('..', 'graphics', 'ui', 'denta'),
            'weapons': import_folder_dict('..', 'graphics', 'ui', 'weapons')
        }

    def get_save_files(self):
        if (self.current_saves == None):
            # get saves from dir if not loaded. This is set to none when leaving 'saves' menu, so that when returning it will load again
            self.current_saves = Saves()
            print(self.current_saves.get_all_saves())

        print("saves")

    def load_save_file(self, filename, level_selected, text = None):
        # load into data.py
        print(f'chosen: {level_selected}')
        data = ''
        if (filename):
            data = self.saves.read_save_file(filename)

            if (data):
                self.data.load_save_data(filename, data)
                #self.data.print_data()

                self.curr_level = level_selected
                self.load_level_transition(text)
                
                if (not self.game_active):
                    self.game_active = True
            else:
                print('Could not read save file.')
        else:
            print('No filename provided.')
            self.curr_level = 0
            self.load_level_transition(text)

    def new_game(self):
        """
        init new save file
        """
        # create file
        filename = self.saves.create_new_save()
        # load into data.py
        self.load_save_file(filename, 1)

    def load_level_transition(self, text = None):
        if (self.game_state != GAME_COMPLETE):
            self.game_state = TRANSITION_LEVEL
        text = text if text is not None else 'Main' if self.curr_level == 0 else self.level_names[self.curr_level]
        self.transition_screen = SandwichTransition(self.font_title, text)

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def to_main_menu(self):
        self.curr_level = 0
        self.game_state = TRANSITION_LEVEL
        self.load_level_transition()

    def func_resume_game(self):
        self.game_active = True

        if (self.game_state == IN_STORE):
            self.game_state = LIVE

    def bound(self, val, val_min, val_max):
        return max(min(val, val_max), val_min)
    
    def save_data(self):
        self.saves.save_data(self.data)

    def restart_level(self):
        # nothing special, just load the save file again to get the original data
        self.load_save_file(self.data.save_filename, self.curr_level, 'Reset')

    def level_complete(self):
        # save player data into save file
        # if final level completed, save the last level index 
        self.curr_level += 1    # next level in self.level_maps
        self.data.highest_stage_level = self.bound(self.curr_level, self.data.highest_stage_level, len(self.level_maps) - 1)    # save to data, but account for the player can complete a previously completed level.

        if self.curr_level >= len(self.level_maps):
            # all levels complete
            self.curr_level = self.bound(self.curr_level, 0, len(self.level_maps) - 1)
            self.game_state = GAME_COMPLETE

        self.save_data()
        self.load_level_transition()

    def open_store(self):
        self.game_state = IN_STORE
        self.store_screen = StoreOverlay(self.font_title, self.font, self.overlay_frames, self.data, self.func_resume_game)

    def draw_bg_tile(self, bg_tile_name):
        for row in range(int(WINDOW_HEIGHT / TILE_SIZE) + 1):
            for col in range(int(WINDOW_WIDTH) + 1):
                x = col * TILE_SIZE
                y = row * TILE_SIZE
                self.display_surface.blit(self.level_frames['bg_tiles'][bg_tile_name], (x, y))

    def run(self):
        # moved previous time here due to remove the time it takes during initialization 
        self.previous_time = time.time()
        while (True):

            dt = (time.time() - self.previous_time) * FPS_TARGET    # reason why I multiply bt FPS_TARGET is so that the speed values do not have to be set very high. I prefer i.e. 5 rather that 500
            self.previous_time = time.time()

            if (self.game_state == IN_STORE):
                self.game_active = False
            elif (self.game_state == TRANSITION_LEVEL):
                self.game_active = False
            elif (self.level_maps[self.curr_level]['stage_main'] == 0 and self.level_maps[self.curr_level]['stage_sub'] == 0):
                self.game_state = MAIN_MENU
                self.game_active = True
            elif (self.game_state == GAME_COMPLETE):
                self.game_active = False
            else:
                self.game_state = LIVE
                # self.game_active may be T or F

            self.ui.game_state = self.game_state

            event_list = pygame.event.get()
            for event in event_list:
                if (event.type == pygame.QUIT):
                    self.quit_game()
                elif event.type == pygame.KEYDOWN:
                    if (event.key == pygame.K_ESCAPE):
                        if (self.game_state == LIVE and self.game_active):
                            self.game_active = False
                            self.pause_menu.goto_pause_main()
                        elif (self.game_state == LIVE and not self.game_active):
                            self.game_active = True
                    
                    if (event.key == pygame.K_f):
                        if (self.run_level.npcs_in_contact):
                            for npc in self.run_level.npcs_in_contact:
                                # for now just interact with first
                                if (npc == HUSKY):
                                    # store
                                    self.open_store()

                if (event.type == pygame.MOUSEBUTTONDOWN):
                    if (event.button == 1):
                        if (self.game_state == MAIN_MENU):
                            self.main_menus.get_current_menu().check_button_clicked(event.pos)
                        elif (self.game_state == LIVE and not self.game_active):
                            self.pause_menu.get_current_menu().check_button_clicked(event.pos)
                        elif (self.game_state == GAME_COMPLETE):
                            self.game_complete_screen.check_button_clicked(event.pos)
                        elif (self.game_state == IN_STORE):
                            self.store_screen.check_button_clicked(event.pos)

            if (not self.game_active):
                # game paused
                if (self.game_state == LIVE):
                    # since the game is "paused", where the background is not updating, need to remove the previous menu's options or else they will still be visible in another menu
                    # my idea to "remove" previous menu options, just blit a surface to override the old before update to draw the new
                    self.draw_bg_tile('Green')
                    self.pause_menu.get_current_menu().update(dt)
                elif (self.game_state == GAME_COMPLETE):
                    self.draw_bg_tile('Brown')
                    self.game_complete_screen.update(dt)
                elif (self.game_state == TRANSITION_LEVEL):
                    if (self.transition_screen is None):
                        self.transition_screen = SandwichTransition(self.font_title, 'Main' if self.curr_level == 0 else self.level_names[self.curr_level])
                    
                    #self.run_level.run(0, event_list) # run level but with 0 dt so that when transition is reversing the background is re drawn

                    if self.transition_screen.reverse and not self.transition_screen.bg_loaded:
                        self.transition_screen.bg_loaded = True
                        # transition requires new level background, load new level
                        self.run_level = Level(self.level_maps[self.curr_level], self.level_frames, self.data, self.restart_level, self.level_complete, self.open_store, self.font)
                    if self.transition_screen.reverse:
                        self.run_level.run(0, event_list) # run level but with 0 dt so that when transition is reversing the background is re drawn

                    if self.transition_screen.update(dt):
                        self.game_state = LIVE
                        self.game_active = True
                elif (self.game_state == IN_STORE):
                    self.run_level.run(0, event_list)   # bg
                    self.ui.update(dt, event_list)
                    self.store_screen.update()

            else:
                self.run_level.run(dt, event_list)
                self.ui.update(dt, event_list)

                # if main menu level. Also display the main_menu
                if (self.game_state == MAIN_MENU):
                    self.main_menus.get_current_menu().update(dt)
                else:
                    # don't need to hold onto the saves while in the levels
                    self.current_saves = None
                    if (self.main_menus.current_menu.overlay != MAIN):
                        # ensure next time returning to main menu, starts at the primary main menu
                        self.main_menus.goto_main_menu()

            pygame.display.update()

            self.clock.tick(FPS_MAX)


if __name__ == "__main__":
    game = Game()
    game.run()