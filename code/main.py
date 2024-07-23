from pytmx.util_pygame import load_pygame

from debug import debug
from settings import *
from level import Level
from support import *
from data import Data
from ui import UI
from saves import Saves
from overlay import MainMenu

class Game:
    
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.previous_time = 0
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Jackie Boy")
        self.import_assets()
        
        self.ui = UI(self.font, self.ui_frames)
        self.data = Data(self.ui)   # todo, save info in like a plain text file, read and initilize Data. Save into text file only when level has been completed
        self.curr_level = 0
        self.game_active = True

        self.level_maps_test = [
            {"stage_main" :0, "stage_sub": 0, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "menu.tmx")), "completion_reqs": {}},
            {"stage_main" :0, "stage_sub": 0, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "test.tmx")), "completion_reqs": {"kibble": 5, "denta": 1}}
        ]

        self.level_maps = [
            {"stage_main" :0, "stage_sub": 0, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "menu.tmx")), "completion_reqs": {}},
            {"stage_main" :1, "stage_sub": 1, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "1_1.tmx")), "completion_reqs": {}},
            {"stage_main" :1, "stage_sub": 2, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "1_2.tmx")), "completion_reqs": {}},
            {"stage_main" :1, "stage_sub": 3, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "1_3.tmx")), "completion_reqs": {}},
            {"stage_main" :1, "stage_sub": 4, "tmx_map": load_pygame(os.path.join("..", "data", "levels", "1_4.tmx")), "completion_reqs": {}}
        ]

        self.current_overlay = MAIN
        self.current_saves = None
        self.current_save_file = None
        self.main_menu = MainMenu(self.current_overlay, self.font, self.current_saves, self.overlay_frames)
        
        self.run_level = Level(self.level_maps_test[self.curr_level], self.level_frames, self.data)
        #self.run_level = Level(self.level_maps[self.curr_level], self.level_frames, self.data)

    def import_assets(self):
        self.level_frames = {
            'player': import_sub_folders('..', 'graphics', 'player'),
            'items': import_sub_folders('..', 'graphics', 'items'),
            'platform': import_folder('..', 'graphics', 'level', 'platform'),
			'boat': import_folder('..',  'graphics', 'objects', 'boat'),
            'floor_spikes': import_folder('..', 'graphics','enemies', 'floor_spikes'),
            'thorn_bush': import_folder('..', 'graphics','enemies', 'thorn_bush'),
            'bats': import_folder('..', 'graphics','enemies', 'bats'),
            'water_top': import_folder('..', 'graphics', 'level', 'water', 'top'),
			'water_body': import_image('..', 'graphics', 'level', 'water', 'body'),
			'caloud_small': import_folder('..', 'graphics', 'level', 'clouds', 'small'),
			'cldoud_large': import_image('..', 'graphics', 'level', 'clouds', 'large_cloud'),
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
            'water_top': import_folder('..', 'graphics', 'level', 'water', 'top'),
            'water_body': import_image('..', 'graphics', 'level', 'water', 'body'),
            'bg_tiles': import_folder_dict('..', 'graphics', 'level', 'bg', 'tiles'),
            'cloud_small': import_folder('..', 'graphics', 'level', 'clouds', 'small'),
            'cloud_large': import_image('..', 'graphics', 'level', 'clouds', 'large_cloud')
        }

        self.font = pygame.font.Font(join('..', 'graphics', 'ui', 'font', 'runescape_uf.ttf'), 25)
        self.ui_frames = {
            'heart': import_folder('..', 'graphics', 'ui', 'heart'),
            'kibble': import_folder('..', 'graphics', 'ui', 'kibble'),
            'denta': import_folder('..', 'graphics', 'ui', 'denta')
        }
        self.overlay_frames = {
            'heart': import_folder('..', 'graphics', 'ui', 'heart'),
            'kibble': import_folder('..', 'graphics', 'ui', 'kibble'),
            'denta': import_folder('..', 'graphics', 'ui', 'denta')
        }

    def load_save_files(self):
        if (self.current_saves == None):
            # get saves from dir if not loaded. This is set to none when leaving 'saves' menu, so that when returning it will load again
            self.current_saves = Saves()
            print(self.current_saves.get_all_saves())

        print("saves")

    def run(self):
        # moved previous time here due to remove the time it takes during initialization 
        self.previous_time = time.time()
        while (True):

            dt = (time.time() - self.previous_time) * FPS_TARGET
            self.previous_time = time.time()

            event_list = pygame.event.get()
            for event in event_list:
                if (event.type == pygame.QUIT):
                    pygame.quit()
                    sys.exit()

            if (not self.game_active):
                
                # depending on overlay, pause the game

                pass
            else:
                self.run_level.run(dt, event_list)
                self.ui.update(dt, event_list)

                # if main menu level. Also display the main_menu
                if (self.level_maps_test[self.curr_level]['stage_main'] == 0 and self.level_maps_test[self.curr_level]['stage_sub'] == 0):
                    if (not self.current_saves):
                        # only reload current_saves when first time on main menu or returning, not while in main menu
                        self.load_save_files()
                        self.main_menu.save_data = self.current_saves.get_all_saves()

                    offset = self.run_level.current_window_offset
                    self.main_menu.update(offset)
                    
                else:
                    self.current_saves = None

                pygame.display.update()

            self.clock.tick(FPS_MAX)


if __name__ == "__main__":
    game = Game()
    game.run()