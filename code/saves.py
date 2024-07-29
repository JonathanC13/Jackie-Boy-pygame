import json
import datetime

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
                        f = open(path, 'r')
                    except OSError:
                        print("Could not open/read file:", path)
                        continue
                    else:
                        with f:
                            try:
                                reader = json.load(f)
                            except json.JSONDecodeError:
                                print("Not valid JSON file:", path)
                                #f.close()
                                continue
                            else:
                                valid_save_file = self.validate_json_keys(reader)

                                if valid_save_file:
                                    self.all_saves.append({"stem": str(os.path.splitext(entry.name)[0]), "filename": str(entry.name), "data": reader})
                                #f.close()

    def validate_json_keys(self, data):
        valid_save_file = True
        for key in SAVE_KEYS:
            if (key not in data):
                valid_save_file = False
                break

        return valid_save_file

    def read_save_file(self, filename):
        path = os.path.join(self.saves_dir, filename)
        try:
            f = open(path, 'r')
        except OSError:
            print("Could not open/read file:", path)
            return None
        else:
            with f:
                try:
                    reader = json.load(f)
                except json.JSONDecodeError:
                    print("Not valid JSON file:", path)
                    #f.close()
                    return None
                else:
                    valid_save_file = self.validate_json_keys(reader)
                    if (valid_save_file):
                        return reader
                    
        return None

    def create_new_save(self):
        now = datetime.datetime.now()
        new_stem = now.strftime("%Y%m%d_%H%M%S.json")

        path = os.path.join(self.saves_dir, new_stem)

        # Serializing json
        json_object = '{}'
        try:
            json_object = json.dumps(SAVE_NEW_TEMPLATE, indent=4)
        except:
            print("Could not serialize json for save file.")
            return None
        else:
            try:
                f = open(path, 'w')
            except OSError:
                print("Could not open file:", path)
                return None
            else:
                with f:
                    f.write(json_object)

                return new_stem
        return None

    def delete_file(self, filename):
        path = os.path.join(self.saves_dir, filename)
        if os.path.exists(path):
            try:
                os.remove(path)
            except:
                print("OS remove error")
        else:
            print("The file does not exist") 