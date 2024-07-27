import json

from settings import *

class Saves:
    def __init__(self):
        self.saves_dir = SAVES_DIR
        self.all_saves = []

    def get_all_saves(self):
        return self.all_saves

    def load_saves(self):
        #print(self.saves_dir)
        self.all_saves = []
        with os.scandir(self.saves_dir) as it:
            for entry in it:
                if entry.is_file() and os.path.splitext(entry)[1] == '.json':
                    path = os.path.join(self.saves_dir, entry.name)
                    try:
                        f = open(path)
                    except OSError:
                        print("Could not open/read file:", path)
                        continue

                    with f:
                        try:
                            reader = json.load(f)
                        except json.JSONDecodeError:
                            print("Not valid JSON file:", path)
                            #f.close()
                            continue
                        
                        self.validate_json_keys(os.path.splitext(entry.name)[0], reader)
                        #f.close()

    def validate_json_keys(self, filename, data):
        valid_save_file = True
        for key in SAVE_KEYS:
            if (key not in data):
                valid_save_file = False
                break

        if valid_save_file:
            self.all_saves.append({"filename": str(filename), "data": data})

    def delete_file(self, filename):
        print('delete: ', filename)