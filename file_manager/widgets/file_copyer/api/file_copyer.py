import shutil
import os

from rofl_toolbox.file_manager.constants import FC_SETTINGS
from rofl_toolbox.generic_python.python_generic import Generic

# probleme avec le start all
# Qt Error: QThread: Destroyed while thread is still running
# 29911:  (sent by pid 29911)

class FileCopyer:
    def __init__(self):
        self.datas = self.read_json()

    def build_data_files(self, scene, category, group, filename, src, tgt):
        """
        add a file to the database to copy in the futur
        Args:
            scene: scene sid
            category: type of the file
            group: name of the group file
            filename: the name of the file
            src: the source path of the file
            tgt: the target path of the file

        """
        if not self.datas.get(scene):
            self.datas[scene] = {}
        if not self.datas[scene].get(category):
            self.datas[scene][category] = {}
        if not self.datas[scene][category].get(group):
            self.datas[scene][category][group] = {}
        if not self.datas[scene][category][group].get(filename):
            self.datas[scene][category][group][filename] = {}

        self.datas[scene][category][group][filename].update({"src": src, "tgt": tgt, "copied": False})

    def copy_file(self, src, tgt):
        """
        command to copy file
        Args:
            src: source path
            tgt: target path

        """
        shutil.copy(src, tgt)

    def get_all_group_files(self, scene, category, group):
        """
        get all the files of a group
        Args:
            scene: which scene
            category: which category
            group: which group name

        Returns: files dict

        """
        files = self.datas[scene][category][group]
        return files

    def get_all_group_files_copied_number(self, scene, category, group):
        """
        get how many files of a group has already been copied
        Args:
            scene: which scene
            category: which category
            group: which group name

        Returns: number of files copied

        """
        files = self.get_all_group_files(scene=scene, category=category, group=group)
        files = [parm for parm, value in files.items() if value["copied"]]
        return len(files)

    def get_all_group_files_number(self, scene, category, group):
        """
        get the number of the files to copy in a group
        Args:
            scene: which scene
            category: which category
            group: which group name

        Returns: number of files

        """
        files = self.get_all_group_files(scene=scene, category=category, group=group)
        files = list(files.keys())
        return len(files)

    def get_all_scenes(self):
        """
        get all scenes

        Returns: a list of scenes

        """
        return list(self.datas.keys())

    def get_all_scene_categories(self, scene):
        """
        get all categories in a scene
        Args:
            scene: which scene

        Returns: a list of categories

        """
        liste = []
        if not self.datas.get(scene):
            return liste

        liste = sorted(list(self.datas[scene].keys()))
        return liste

    def get_all_scene_category_groups(self, scene, category):
        """
        get all groups in a category
        Args:
            scene: which scene
            category: which category

        Returns: a list of groups

        """
        liste = []
        if not self.datas.get(scene):
            return liste
        if not self.datas[scene].get(category):
            return liste

        liste = sorted(list(self.datas[scene][category].keys()))
        return liste

    def get_all_scene_categories_groups_number(self, scene, category):
        """
        get the number of the groups to copy in a category
        Args:
            scene: which scene
            category: which category

        Returns: number of groups

        """
        childs = self.get_all_scene_category_groups(scene=scene, category=category)
        return len(childs)

    def get_file_src(self, files, file):
        """
        get source path of a file
        Args:
            files: dict of files of a group (to use with get_all_child_files)
            file: the current file

        Returns: the source path

        """
        return files[file]["src"]

    def get_file_status(self, files, file):
        """
        get copy_status of a file
        Args:
            files: dict of files of a group (to use with get_all_child_files)
            file: the current file

        Returns: the copy status

        """
        return files[file]["copied"]

    def get_file_tgt(self, files, file):
        """
        get target path of a file
        Args:
            files: dict of files of a group (to use with get_all_child_files)
            file: the current file

        Returns: the target path

        """
        return files[file]["tgt"]

    def get_source_folder(self, scene, category, group):
        """
        get the folder which contains the files
        Args:
            scene: which scene
            parent: which category
            child: which group name

        Returns: the folder which contains the files

        """
        files = self.datas[scene][category][group]
        first_file = next(iter(files))

        return os.path.dirname(files[first_file]["src"])

    def get_target_folder(self, scene, category, group):
        """
        get the futur folder which contains the files
        Args:
            scene: which scene
            category: which category
            group: which group name

        Returns: the futur folder which contains the files

        """
        files = self.datas[scene][category][group]
        first_file = next(iter(files))

        return os.path.dirname(files[first_file]["tgt"])

    def read_json(self):
        """
        load FileCopyer database
        Returns: the datas

        """
        datas = Generic().read_json(data_file=FC_SETTINGS)
        return datas

    def remove_in_data_files(self, scene, category, group):
        """
        remove file in database
        Args:
            scene: which scene
            category: which category
            group: which group name

        Returns: True if succeed

        """
        del(self.datas[scene][category][group])
        if self.datas[scene][category]:
            self.save_json()
            return True

        del(self.datas[scene][category])
        if self.datas[scene]:
            self.save_json()
            return True

        del(self.datas[scene])
        if self.datas:
            self.save_json()
            return True

        os.remove(FC_SETTINGS)
        self.save_json()
        return True

    def save_json(self):
        """
        save datas in File Copyer database

        """
        Generic().save_json(data_file=FC_SETTINGS, data=self.datas)

    def set_file_status(self, scene, category, group, file):
        """
        turn copy status to True when file is copied
        Args:
            scene: which scene
            category: which category
            name: which group name
            file: which file

        """
        self.datas[scene][category][group][file]["copied"] = True
        self.save_json()