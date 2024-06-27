from pytmx.util_pygame import load_pygame

from debug import debug
from settings import *
from level import Level
from support import *

class Game:
    
    def __init__(self):
        pygame.init()
        self.clock = pygame.time.Clock()
        self.previous_time = time.time()
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Jackie Boy")
        self.import_assets()
        
        self.curr_level = 1

        self.level_maps = [
            [0, 0, load_pygame(os.path.join("..", "data", "levels", "test_ground.tmx"))],
            [1, 1, load_pygame(os.path.join("..", "data", "levels", "1_1.tmx"))],
            [1, 2, load_pygame(os.path.join("..", "data", "levels", "1_2.tmx"))]
        ]

        self.run_level = Level(self.level_maps[self.curr_level], self.level_frames)

    def import_assets(self):
        self.level_frames = {
            
        }

    def run(self):
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