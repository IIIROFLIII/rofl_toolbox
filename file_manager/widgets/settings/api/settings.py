import os

from rofl_toolbox.generic_python.python_generic import Generic
from rofl_toolbox.file_manager.constants import USER_HOME

SETTINGS_FOLDER = os.path.expanduser("~")

class Settings:
    def __init__(self):
        self.default_bdd_dir = USER_HOME
        self.default_files_folder = "Scene Folder"
        self.default_fps = 25

        self._data = {"bdd_dir": self.default_bdd_dir,
                      "files_folder": self.default_files_folder,
                      "sequence_player_fps": self.default_fps}
        self.load()

    @property
    def data(self):
        return self._data

    @property
    def path(self):
        return os.path.join(SETTINGS_FOLDER, "ROFL_settings.json")

    def get_bdd_dir(self):
        self.load()
        return self.data["bdd_dir"]

    def get_files_folder(self):
        self.load()
        return self.data["files_folder"]

    def get_fps(self):
        self.load()
        return self.data["sequence_player_fps"]

    def load(self):
        if not os.path.exists(self.path):
            self.save()

        self._data = Generic().read_json(self.path)

    def modify_data_path(self, new_path):
        self.load()
        self.data["bdd_dir"] = new_path
        self.save()

    def modify_files_path(self, new_path):
        self.load()
        self.data["files_folder"] = new_path
        self.save()

    def modify_fps(self, value):
        self.load()
        self.data["sequence_player_fps"] = value
        self.save()

    def save(self):
        if not os.path.exists(SETTINGS_FOLDER):
            os.makedirs(SETTINGS_FOLDER)

        self._data = Generic().save_json(self.path, self.data)

if __name__ == '__main__':
    set = Settings()
    print(set.data)