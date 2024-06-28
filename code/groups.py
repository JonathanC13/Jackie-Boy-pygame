from settings import *

# group to sim camera, override Group class
class AllSprites(pygame.sprite.Group):

    def __init__(self):
        super().__init__()
        self.display_surface = pygame.display.get_surface()
        self.offset = vector(0, 0)

    def draw(self, target_pos, player_width, tmx_map_width):
        self.offset.x = -(target_pos[0] - (WINDOW_WIDTH / 2) + player_width)

        # bounds
        self.offset.x = max(min(self.offset.x, 0), -((tmx_map_width - 2) * TILE_SIZE - WINDOW_WIDTH + player_width))

        for sprite in sorted(self, key = lambda sprite : sprite.z):
            offset_pos = sprite.rect.topleft + self.offset
            # get all sprites in this group
            self.display_surface.blit(sprite.image, offset_pos)