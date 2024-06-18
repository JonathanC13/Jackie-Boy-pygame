from pytmx.util_pygame import load_pygame

import debug
from settings import *
import level

class Game:
    
    def __init__(self):
        pygame.init()
        self.previous_time = 0
        self.display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Jackie The Dog")

        self.curr_level = 0

        self.levels = [
            [1, 1, load_pygame(os.path.join("../", "data/levels", "testGround.tmx"))]
        ]

        self.run_level = level.Level(self.levels[self.curr_level])

    def run(self):
        while (True):

            dt = (time.time() - self.previous_time) * (FPS_TARGET/2)
            self.previous_time = time.time()

            for event in pygame.event.get():
                if (event.type == pygame.QUIT):
                    pygame.quit()
                    sys.exit()

            self.run_level.run(dt)
            pygame.display.update()


if __name__ == "__main__":
    game = Game()
    game.run()