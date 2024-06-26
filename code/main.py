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
        
        self.curr_level = 0

        self.level_maps = [
            [1, 1, load_pygame(os.path.join("..", "data", "levels", "testGround.tmx"))]
        ]

        self.run_level = Level(self.level_maps[self.curr_level], self.level_frames)

    def import_assets(self):
        self.level_frames = {
            "flag": import_folder("..", "graphics", "level", "flag")
        }

    def run(self):
        while (True):

            dt = (time.time() - self.previous_time) * FPS_TARGET
            self.previous_time = time.time()

            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    pygame.quit()
                    sys.exit()

            self.run_level.run(dt)
            pygame.display.update()

            self.clock.tick(FPS_MAX)


if __name__ == "__main__":
    game = Game()
    game.run()