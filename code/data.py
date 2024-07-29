class Data:
    def __init__(self, ui):
        self.ui = ui

        self.save_filename = None

        self._player_health = 3
        self._kibble = 0
        self._denta = 0

        self._stick_level_min = 1
        self._stick_level_max = 2
        self._lance_level_min = 1
        self._lance_level_max = 2
        self._ball_level_min = 1
        self._ball_level_max = 2

        self._stick_level = self.stick_level = 1
        self._lance_level = self.lance_level = 1
        self._ball_level = self.ball_level = 1

        self.kibble_for_life = 50

        self.secret_levels_unlocked = []
        self.highest_stage_level = 1

        self.ui.create_hearts(self.player_health)
        self.ui.create_denta_count_surf(self.denta)
        self.ui.create_kibble_count_surf(self.kibble)

    def bound_values(self, value, min_val, max_val):
        return max(min(max_val, value), min_val)

    @property
    def player_health(self):
        return self._player_health
    
    @player_health.setter
    def player_health(self, amount):
        self._player_health = amount
        self.ui.create_hearts(amount)
    
    @property
    def kibble(self):
        return self._kibble
    
    @kibble.setter
    def kibble(self, amount):
        new_amount = amount
        if (amount >= self.kibble_for_life):
            self.player_health += 1
            new_amount -= self.kibble_for_life
        self._kibble = new_amount
        self.ui.create_kibble_count_surf(self.kibble)

    @property
    def denta(self):
        return self._denta
    
    @denta.setter
    def denta(self, amount):
        self._denta = amount
        self.ui.create_denta_count_surf(amount)

    @property
    def stick_level(self):
        return self._stick_level
    
    @stick_level.setter
    def stick_level(self, level):
        self._stick_level = self.bound_values(level, self._stick_level_min, self._stick_level_max)

    @property
    def lance_level(self):
        return self._lance_level
    
    @lance_level.setter
    def lance_level(self, level):
        self._lance_level = self.bound_values(level, self._lance_level_min, self._lance_level_max)

    @property
    def ball_level(self):
        return self._ball_level
    
    @ball_level.setter
    def ball_level(self, level):
        self._ball_level = self.bound_values(level, self._ball_level_min, self._ball_level_max)

    def load_save_data(self, save_data):
        for key, val in save_data.items():
            match key:
                case 'secret_levels_unlocked':
                    self.secret_levels_unlocked = val
                case 'player_health':
                    self.player_health = val
                case 'kibble':
                    self.kibble = val
                case 'denta':
                    self.denta = val
                case 'stick_level':
                    self.stick_level = val
                case 'lance_level':
                    self.lance_level = val
                case 'ball_level':
                    self.ball_level = val
                case 'highest_stage_level':
                    self.highest_stage_level = val
                case _:
                    print(f'unmapped key: {key}')

    def print_data(self):
        print('"""')
        print(f"secret_levels_unlocked: {self.secret_levels_unlocked}")
        print(f"player_health: {self.player_health}")
        print(f"kibble: {self.kibble}")
        print(f"denta: {self.denta}")
        print(f"stick_level: {self.stick_level}")
        print(f"lance_level: {self.lance_level}")
        print(f"ball_level: {self.ball_level}")
        print(f"highest_stage_level: {self.highest_stage_level}")
        print('"""')