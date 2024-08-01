from settings import *

class Data:
    def __init__(self, ui):
        self.ui = ui

        self._default_player_health = 3
        self._stick_level_min = 1
        self._stick_level_max = 2
        self._lance_level_min = 1
        self._lance_level_max = 2
        self._ball_level_min = 1
        self._ball_level_max = 2

        self.save_filename = None

        self.data_dict = {
            "secret_levels_unlocked":[1], 
            "player_health": self._default_player_health, 
            "kibble":0,
            "denta":0,
            "stick_level":1,
            "lance_level":1,
            "ball_level":1,
            "highest_stage_level": 1
        }

        self.stick_level = self.data_dict['stick_level']
        self.lance_level = self.data_dict['lance_level']
        self.ball_level = self.data_dict['ball_level']

        self.kibble_for_life = 50

        self.heart_cost = 20
        self.stick_upgrade_cost = 30
        self.lance_upgrade_cost = 30
        self.ball_upgrade_cost = 30

        self._weapon_list = []
        self._current_weapon_index = 0

        self.ui.create_hearts(self.data_dict['player_health'])
        self.ui.create_denta_count_surf(self.data_dict['denta'])
        self.ui.create_kibble_count_surf(self.data_dict['kibble'])

    def bound_values(self, value, min_val, max_val):
        return max(min(max_val, value), min_val)

    @property
    def current_weapon_index(self):
        return self._current_weapon_index
    
    @current_weapon_index.setter
    def current_weapon_index(self, current_weapon_index):
        self._current_weapon_index = current_weapon_index
        self.ui.current_weapon_index = current_weapon_index

    @property
    def weapon_list(self):
        return self._weapon_list
    
    @weapon_list.setter
    def weapon_list(self, weapon_list):
        self._weapon_list = weapon_list
        self.ui.weapon_list = weapon_list

    @property
    def player_health(self):
        return self.data_dict['player_health']
    
    @player_health.setter
    def player_health(self, amount):
        set_amount = amount
        if (set_amount <= 0):
            set_amount = self._default_player_health
        self.data_dict['player_health'] = set_amount
        self.ui.create_hearts(set_amount)
    
    @property
    def kibble(self):
        return self.data_dict['kibble']
    
    @kibble.setter
    def kibble(self, amount):
        new_amount = amount
        if (amount >= self.kibble_for_life):
            self.data_dict['player_health'] += 1
            new_amount -= self.kibble_for_life
        self.data_dict['kibble'] = new_amount
        self.ui.create_kibble_count_surf(self.data_dict['kibble'])

    @property
    def denta(self):
        return self.data_dict['denta']
    
    @denta.setter
    def denta(self, amount):
        self.data_dict['denta'] = amount
        self.ui.create_denta_count_surf(amount)

    @property
    def stick_level(self):
        return self.data_dict['stick_level']
    
    @stick_level.setter
    def stick_level(self, level):
        self.data_dict['stick_level'] = self.bound_values(level, self._stick_level_min, self._stick_level_max)

    @property
    def lance_level(self):
        return self.data_dict['lance_level']
    
    @lance_level.setter
    def lance_level(self, level):
        self.data_dict['lance_level'] = self.bound_values(level, self._lance_level_min, self._lance_level_max)

    @property
    def ball_level(self):
        return self.data_dict['ball_level']
    
    @ball_level.setter
    def ball_level(self, level):
        self.data_dict['ball_level'] = self.bound_values(level, self._ball_level_min, self._ball_level_max)

    @property
    def highest_stage_level(self):
        return self.data_dict['highest_stage_level']
    
    @highest_stage_level.setter
    def highest_stage_level(self, level_index):
        self.data_dict['highest_stage_level'] = level_index

    def check_if_max_level(self, index):
        weapon_name = self.weapon_list[index]['weapon'].weapon_name
        if (weapon_name == STICK):
            if (self.stick_level >= self._stick_level_max):
                return True
        elif (weapon_name == UMBRELLA):
            if (self.lance_level >= self._lance_level_max):
                return True
        elif (weapon_name == BALL):
            if (self.ball_level >= self._ball_level_max):
                return True

        return False

    def buy_heart(self):
        print("heart")
        if (self.denta - self.stick_upgrade_cost >= 0):
            self.denta -= self.heart_cost
            self.player_health += 1
            print("bought heart")
            return True
        
        return False

    def upgrade_weapon(self, index):
        print('upgrade')
        weapon_name = self.weapon_list[index]['weapon'].weapon_name
        if (weapon_name == STICK):
            if (self.denta - self.stick_upgrade_cost >= 0 and not self.check_if_max_level(index)):
                self.denta -= self.stick_upgrade_cost
                self.stick_level += 1
                self.weapon_list[index]['weapon'].change_level(index, self.stick_level)  # in weapon.py will trigger creation of new weapon
                print('upgrade sk')
                return True
        elif (weapon_name == UMBRELLA):
            if (self.denta - self.lance_upgrade_cost >= 0 and not self.check_if_max_level(index)):
                self.denta -= self.lance_upgrade_cost
                self.lance_level += 1
                self.weapon_list[index]['weapon'].change_level(index, self.lance_level)
                print('upgrade ln')
                return True
        elif (weapon_name == BALL):
            if (self.denta - self.ball_upgrade_cost >= 0 and not self.check_if_max_level(index)):
                self.denta -= self.ball_upgrade_cost
                self.ball_level += 1
                self.weapon_list[index]['weapon'].change_level(index, self.ball_level)
                print('upgrade bl')
                return True

        return False

    def load_save_data(self, filename, save_data):
        self.save_filename = filename
        
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
        print(f'filename: {self.save_filename}')
        print(self.data_dict)