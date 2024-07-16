from pytmx.util_pygame import load_pygame

from debug import debug
from settings import *
from level import Level
from support import *

class Game:
    
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.previous_time = 0
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Jackie Boy")
        self.import_assets()
        
        self.curr_level = 1

        self.level_maps = [
            [0, 0, load_pygame(os.path.join("..", "data", "levels", "test_ground.tmx"))],
            [0, 0, load_pygame(os.path.join("..", "data", "levels", "test.tmx"))],
            [1, 1, load_pygame(os.path.join("..", "data", "levels", "1_1.tmx"))],
            [1, 2, load_pygame(os.path.join("..", "data", "levels", "1_2.tmx"))],
            [1, 3, load_pygame(os.path.join("..", "data", "levels", "1_3.tmx"))],
            [1, 4, load_pygame(os.path.join("..", "data", "levels", "1_4.tmx"))]
        ]

        self.run_level = Level(self.level_maps[self.curr_level], self.level_frames)

    def import_assets(self):
        self.level_frames = {
            'items': import_sub_folders('..', 'graphics', 'item s'),
            'platform': import_folder('..', 'graphics', 'level', 'platform'),
			'boat': import_folder('..',  'graphics', 'objects', 'boat'),
            'floor_spikes': import_folder('..', 'graphics','enemies', 'floor_spikes'),
            'thorn_bush': import_folder('..', 'graphics','enemies', 'thorn_bush'),
            'bats': import_folder('..', 'graphics','enemies', 'bats'),
            'water_top': import_folder('..', 'graphics', 'level', 'water', 'top'),
			'water_body': import_image('..', 'graphics', 'level', 'water', 'body'),
			'cloud_small': import_folder('..', 'graphics','level', 'clouds', 'small'),
			'cloud_large': import_image('..', 'graphics','level', 'clouds', 'large_cloud'),
            'dog': import_sub_folders('..', 'graphics','enemies', 'dog'),
            'bird': import_sub_folders('..', 'graphics','enemies', 'bird'),
            'squirrel': import_sub_folders('..', 'graphics','enemies', 'squirrel'),
            'stick': import_sub_folders('..', 'graphics','weapons', 'stick'),
            'beak': import_sub_folders('..', 'graphics','weapons', 'beak'),
            'acorn': import_sub_folders('..', 'graphics','weapons', 'acorn'),
            'acorn_projectile': import_sub_folders('..', 'graphics','enemies', 'acorn')
        }

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

            self.run_level.run(dt, event_list)
            pygame.display.update()

            self.clock.tick(FPS_MAX)


if __name__ == "__main__":
    game = Game()
    game.run()