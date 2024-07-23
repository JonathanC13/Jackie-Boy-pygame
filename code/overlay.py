from settings import *

class Overlay:
    def __init__(self, overlay, font, save_data, overlay_frames):
        self._overlay = overlay
        self.font = font
        self.save_data = save_data
        self.overlay_frames = overlay_frames

        self.display_surface = pygame.display.get_surface()

        self.surfaces_to_blit = []
        self.start_idx = 0

    @property
    def overlay(self):
        return self._overlay
    
    @overlay.setter
    def overlay(self, overlay):
        self._overlay = overlay

    def set_start_idx(self, index):
        self.start_idx = index

    def display_overlay(self, camera_offset):
        if (self.surfaces_to_blit):
            for i in range(self.start_idx, len(self.surfaces_to_blit)):
                self.surfaces_to_blit[i].sort(key = lambda s: s['layer'])
                if (self.surfaces_to_blit[i][0]['surf'].get_height() + self.surfaces_to_blit[i][0]['topleft'].y > WINDOW_HEIGHT):
                    continue
                else:
                    for surf in self.surfaces_to_blit[i]:
                        self.display_surface.blit(surf['surf'], surf['topleft'])

class MainMenu(Overlay):
    def __init__(self, overlay, font, save_data, overlay_frames):
        
        super().__init__(overlay, font, save_data, overlay_frames)

        self.current_total_spacing_y = 150
        self.between_spacing_y = 25
        
        self.container_size = vector(275, 150)

    def overlay_save_data(self):
        if (self.save_data):
            for save in self.save_data:
                self.create_container_save_data(save)
        else:
            print("display [No save data]")

    def create_container_save_data(self, save):
        container = []
        filename = save['filename'][:14]
        if (len(save['filename']) >= 14):
            filename += '...'
        save_data = save['data']
        # container
        container_surf = pygame.Surface((self.container_size.x, self.container_size.y))
        container_surf.set_alpha(100)
        container.append({"surf": container_surf, "layer": 0, "topleft": vector((WINDOW_WIDTH/2) - (self.container_size.x/2), self.current_total_spacing_y)})
        
        # file name
        filename_surf = self.font.render('Filename: ' + filename, False, "white", bgcolor=None, wraplength=0)
        container.append({"surf": filename_surf, "layer": 1, "topleft": vector((WINDOW_WIDTH/2) - self.container_size.x/2 + 10, self.current_total_spacing_y + 10)})

        # items
        x_offset = (WINDOW_WIDTH/2) - self.container_size.x/2
        x_spacing = 10
        y_spacing = 15
        # hearts
        x_offset += x_spacing
        heart_surf = self.overlay_frames['heart'][0]
        container.append({"surf": heart_surf, "layer": 1, "topleft": vector(x_offset, self.current_total_spacing_y + filename_surf.get_height() + y_spacing)})
        x_offset += heart_surf.get_width() + x_spacing
        heart_num_surf = self.font.render('x ' + str(save_data['player_health']), False, "white", bgcolor=None, wraplength=0)
        container.append({"surf": heart_num_surf, "layer": 1, "topleft": vector(x_offset, self.current_total_spacing_y + filename_surf.get_height() + y_spacing)})
        x_offset += heart_num_surf.get_width() + x_spacing*2

        # denta
        denta_surf = self.overlay_frames['denta'][0]
        container.append({"surf": denta_surf, "layer": 1, "topleft": vector(x_offset, self.current_total_spacing_y + filename_surf.get_height() + y_spacing)})
        x_offset += denta_surf.get_width() + x_spacing
        denta_num_surf = self.font.render('x ' + str(save_data['denta']), False, "white", bgcolor=None, wraplength=0)
        container.append({"surf": denta_num_surf, "layer": 1, "topleft": vector(x_offset, self.current_total_spacing_y + filename_surf.get_height() + y_spacing)})
        x_offset += denta_num_surf.get_width() + x_spacing*2

        # kibble
        kibble_surf = self.overlay_frames['kibble'][0]
        container.append({"surf": kibble_surf, "layer": 1, "topleft": vector(x_offset, self.current_total_spacing_y + filename_surf.get_height() + y_spacing)})
        x_offset += kibble_surf.get_width() + x_spacing
        kibble_num_surf = self.font.render('x ' + str(save_data['kibble']), False, "white", bgcolor=None, wraplength=0)
        container.append({"surf": kibble_num_surf, "layer": 1, "topleft": vector(x_offset, self.current_total_spacing_y + filename_surf.get_height() + y_spacing)})

        # weapons
        x_offset = 0

        self.surfaces_to_blit.append(container)

        self.current_total_spacing_y += self.container_size.y + self.between_spacing_y

    def update(self, camera_offset):
        if (self.overlay == SAVES):
            self.overlay_save_data()
            self.display_overlay(camera_offset)
        else:
            self.overlay = SAVES
    