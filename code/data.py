class Data:
    def __init__(self, ui):
        self.ui = ui

        self._player_health = 5
        self._kibble = 0
        self._denta = 0

        self.ui.create_hearts(self._player_health)
        self.ui.create_denta_count_surf(self._denta)
        self.ui.create_kibble_count_surf(self._kibble)

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
        self._kibble = amount
        self.ui.create_kibble_count_surf(self._kibble)

    @property
    def denta(self):
        return self._denta
    
    @denta.setter
    def denta(self, amount):
        self._denta = amount
        self.ui.create_denta_count_surf(amount)

    def print_data(self):
        print(f"player_health: {self._player_health}")
        print(f"kibble: {self._kibble}")
        print(f"denta: {self._denta}")